"""Fetch fresh audit data from Shopify: products, collections, pages, blogs, theme.

Writes raw data to data/ for downstream analysis. Read-only — makes no changes.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"
GQL_URL = f"https://{STORE}/admin/api/{API_VERSION}/graphql.json"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)


def rest_get(path, raw=False):
    url = f"https://{STORE}/admin/api/{API_VERSION}/{path}"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read()
                return body if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(float(e.headers.get("Retry-After", 2)))
                continue
            raise
        except Exception:
            if attempt < 4:
                time.sleep(3)
                continue
            raise


def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        GQL_URL, data=payload, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"},
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                out = json.loads(resp.read())
                if out.get("errors"):
                    raise RuntimeError(json.dumps(out["errors"])[:500])
                return out["data"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503) and attempt < 4:
                time.sleep(5)
                continue
            raise
        except RuntimeError:
            raise
        except Exception:
            if attempt < 4:
                time.sleep(3)
                continue
            raise


def run_bulk(query, out_file):
    """Run a bulk operation and download the JSONL result."""
    mutation = """
    mutation($q: String!) {
      bulkOperationRunQuery(query: $q) {
        bulkOperation { id status }
        userErrors { field message }
      }
    }"""
    data = gql(mutation, {"q": query})
    errs = data["bulkOperationRunQuery"]["userErrors"]
    if errs:
        raise RuntimeError(f"bulk start failed: {errs}")
    print(f"  bulk op started: {data['bulkOperationRunQuery']['bulkOperation']['id']}")

    poll = """
    { currentBulkOperation { id status errorCode objectCount fileSize url } }"""
    while True:
        time.sleep(10)
        op = gql(poll)["currentBulkOperation"]
        status = op["status"]
        print(f"  status={status} objects={op.get('objectCount')}")
        if status == "COMPLETED":
            break
        if status in ("FAILED", "CANCELED"):
            raise RuntimeError(f"bulk op {status}: {op.get('errorCode')}")

    if not op["url"]:
        open(out_file, "w").close()
        return 0
    print(f"  downloading {op['fileSize']} bytes...")
    urllib.request.urlretrieve(op["url"], out_file)
    return int(op["objectCount"])


def fetch_counts():
    counts = {}
    for status in ("active", "draft", "archived"):
        counts[f"products_{status}"] = rest_get(f"products/count.json?status={status}")["count"]
    counts["custom_collections"] = rest_get("custom_collections/count.json")["count"]
    counts["smart_collections"] = rest_get("smart_collections/count.json")["count"]
    counts["pages"] = rest_get("pages/count.json")["count"]
    try:
        counts["orders_all_time"] = rest_get("orders/count.json?status=any")["count"]
        counts["orders_access"] = True
    except urllib.error.HTTPError as e:
        counts["orders_access"] = False
        counts["orders_error"] = e.code
    with open(os.path.join(DATA_DIR, "counts.json"), "w") as f:
        json.dump(counts, f, indent=2)
    print("counts:", json.dumps(counts))
    return counts


PRODUCTS_BULK = """
{
  products {
    edges {
      node {
        id
        title
        handle
        status
        vendor
        productType
        tags
        createdAt
        updatedAt
        publishedAt
        templateSuffix
        totalInventory
        tracksInventory
        descriptionHtml
        onlineStorePreviewUrl
        seo { title description }
        featuredImage { id }
        options { name values }
        colorPattern: metafield(namespace: "shopify", key: "color-pattern") { value }
        variants {
          edges {
            node {
              id
              title
              sku
              price
              compareAtPrice
              inventoryQuantity
              selectedOptions { name value }
            }
          }
        }
        images {
          edges {
            node { id altText }
          }
        }
      }
    }
  }
}
"""

COLLECTIONS_BULK = """
{
  collections {
    edges {
      node {
        id
        title
        handle
        descriptionHtml
        updatedAt
        sortOrder
        templateSuffix
        seo { title description }
        productsCount { count }
        image { altText }
        ruleSet { appliedDisjunctively rules { column condition relation } }
      }
    }
  }
}
"""


def fetch_pages_blogs():
    pages = []
    since = 0
    while True:
        batch = rest_get(f"pages.json?limit=250&since_id={since}")["pages"]
        if not batch:
            break
        pages.extend(batch)
        since = batch[-1]["id"]
    with open(os.path.join(DATA_DIR, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages, f)
    print(f"pages: {len(pages)}")

    blogs = rest_get("blogs.json?limit=250")["blogs"]
    articles = []
    for b in blogs:
        since = 0
        while True:
            batch = rest_get(f"blogs/{b['id']}/articles.json?limit=250&since_id={since}")["articles"]
            if not batch:
                break
            for a in batch:
                a["_blog_title"] = b["title"]
            articles.extend(batch)
            since = batch[-1]["id"]
    with open(os.path.join(DATA_DIR, "blogs.json"), "w", encoding="utf-8") as f:
        json.dump({"blogs": blogs, "articles": articles}, f)
    print(f"blogs: {len(blogs)}, articles: {len(articles)}")


def fetch_theme():
    themes = rest_get("themes.json")["themes"]
    main = next(t for t in themes if t["role"] == "main")
    theme_dir = os.path.join(DATA_DIR, "theme")
    os.makedirs(theme_dir, exist_ok=True)
    with open(os.path.join(theme_dir, "themes.json"), "w") as f:
        json.dump(themes, f, indent=2)
    assets = rest_get(f"themes/{main['id']}/assets.json")["assets"]
    with open(os.path.join(theme_dir, "asset_list.json"), "w") as f:
        json.dump(assets, f, indent=2)
    wanted = [
        "layout/theme.liquid",
        "config/settings_data.json",
        "config/settings_schema.json",
        "snippets/microdata-schema.liquid",
        "templates/index.json",
        "templates/collection.json",
        "templates/product.json",
        "sections/main-collection-product-grid.liquid",
        "sections/main-collection.liquid",
    ]
    available = {a["key"] for a in assets}
    for key in wanted:
        if key not in available:
            continue
        try:
            a = rest_get(f"themes/{main['id']}/assets.json?asset%5Bkey%5D=" + key.replace("/", "%2F"))["asset"]
            fn = key.replace("/", "__")
            with open(os.path.join(theme_dir, fn), "w", encoding="utf-8") as f:
                f.write(a.get("value") or "")
            print(f"  saved {key}")
        except Exception as e:
            print(f"  skip {key}: {e}")
    print(f"theme: {main['name']} (id {main['id']}), {len(assets)} assets")


def fetch_live_pages():
    """Fetch live public pages for on-page verification."""
    import gzip
    live_dir = os.path.join(DATA_DIR, "live")
    os.makedirs(live_dir, exist_ok=True)
    urls = {
        "home": "https://theclothingcove.com/",
        "robots": "https://theclothingcove.com/robots.txt",
        "sitemap": "https://theclothingcove.com/sitemap.xml",
    }
    for name, url in urls.items():
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TKBS-Audit",
                "Accept-Encoding": "gzip",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
            with open(os.path.join(live_dir, f"{name}.html"), "wb") as f:
                f.write(body)
            print(f"  live {name}: {len(body)} bytes")
        except Exception as e:
            print(f"  live {name} failed: {e}")


def fetch_menus():
    try:
        data = gql("""
        { menus(first: 25) { edges { node { handle title items {
            title type url items { title type url items { title type url } } } } } } }""")
        with open(os.path.join(DATA_DIR, "menus.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"menus: {len(data['menus']['edges'])}")
    except Exception as e:
        print(f"menus failed (non-fatal): {e}")


if __name__ == "__main__":
    t0 = time.time()
    print("=== counts ===")
    fetch_counts()
    print("=== pages & blogs ===")
    fetch_pages_blogs()
    print("=== theme ===")
    fetch_theme()
    print("=== live pages ===")
    fetch_live_pages()
    print("=== menus ===")
    fetch_menus()
    print("=== products bulk ===")
    n = run_bulk(PRODUCTS_BULK, os.path.join(DATA_DIR, "products.jsonl"))
    print(f"products bulk objects: {n}")
    print("=== collections bulk ===")
    n = run_bulk(COLLECTIONS_BULK, os.path.join(DATA_DIR, "collections.jsonl"))
    print(f"collections bulk objects: {n}")
    print(f"DONE in {time.time() - t0:.0f}s")
