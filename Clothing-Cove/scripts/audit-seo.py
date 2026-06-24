import json
import urllib.request
import os
import time
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"
THEME_ID = "145504469107"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < 4:
                time.sleep(3 + attempt * 2)
            else:
                raise


def get_asset(key):
    url = f"https://{STORE}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json?asset%5Bkey%5D={key.replace('/', '%2F')}"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["asset"]["value"]


def audit_products():
    """Scan all products for SEO data completeness."""
    print("=== PRODUCT SEO AUDIT ===\n")
    base = f"https://{STORE}/admin/api/{API_VERSION}"
    since_id = 0
    page = 0

    stats = {
        "total": 0,
        "in_stock": 0,
        "missing_title_tag": 0,
        "missing_desc_tag": 0,
        "missing_body_html": 0,
        "short_body_html": 0,  # < 100 chars
        "missing_images": 0,
        "seo_hidden": 0,
        "missing_product_type": 0,
        "missing_vendor": 0,
        "missing_tags": 0,
        "duplicate_titles": {},
        "title_lengths": {"too_short": 0, "good": 0, "too_long": 0},
        "desc_lengths": {"missing": 0, "too_short": 0, "good": 0, "too_long": 0},
        "images_without_alt": 0,
        "images_total": 0,
        "products_with_no_alt_images": 0,
        "sample_missing_desc": [],
        "sample_missing_body": [],
        "sample_seo_hidden": [],
        "sample_no_images": [],
        "by_type_seo": {},
    }

    while True:
        url = f"{base}/products.json?limit=250&status=active&since_id={since_id}&fields=id,title,body_html,product_type,vendor,tags,images,handle"
        data = fetch_json(url)
        products = data.get("products", [])
        if not products:
            break

        for p in products:
            stats["total"] += 1
            pt = p.get("product_type", "") or "(empty)"
            has_stock = True  # simplified — we already know stock from prior audit

            if pt not in stats["by_type_seo"]:
                stats["by_type_seo"][pt] = {"total": 0, "no_body": 0, "short_body": 0, "no_images": 0}
            stats["by_type_seo"][pt]["total"] += 1

            # Body HTML
            body = p.get("body_html", "") or ""
            clean_body = body.replace("<br>", "").replace("<p>", "").replace("</p>", "").strip()
            if not clean_body:
                stats["missing_body_html"] += 1
                stats["by_type_seo"][pt]["no_body"] += 1
                if len(stats["sample_missing_body"]) < 10:
                    stats["sample_missing_body"].append({"title": p["title"], "handle": p["handle"], "type": pt})
            elif len(clean_body) < 100:
                stats["short_body_html"] += 1
                stats["by_type_seo"][pt]["short_body"] += 1

            # Images
            images = p.get("images", [])
            if not images:
                stats["missing_images"] += 1
                stats["by_type_seo"][pt]["no_images"] += 1
                if len(stats["sample_no_images"]) < 10:
                    stats["sample_no_images"].append({"title": p["title"], "handle": p["handle"]})
            else:
                no_alt = sum(1 for img in images if not img.get("alt"))
                stats["images_total"] += len(images)
                stats["images_without_alt"] += no_alt
                if no_alt == len(images):
                    stats["products_with_no_alt_images"] += 1

            # Product type / vendor / tags
            if not p.get("product_type"):
                stats["missing_product_type"] += 1
            if not p.get("vendor") or p["vendor"] == "The Clothing Cove":
                stats["missing_vendor"] += 1
            if not p.get("tags"):
                stats["missing_tags"] += 1

            # Track duplicate titles
            title = p["title"].strip().upper()
            stats["duplicate_titles"][title] = stats["duplicate_titles"].get(title, 0) + 1

        since_id = products[-1]["id"]
        page += 1
        if page % 10 == 0:
            print(f"  Page {page} — {stats['total']} products...")
        time.sleep(0.5)

    # Now scan metafields for SEO data (title_tag, description_tag, seo.hidden)
    print("\nScanning product metafields for SEO tags...")
    since_id = 0
    mf_page = 0
    mf_stats = {"has_title": 0, "has_desc": 0, "seo_hidden": 0, "checked": 0}

    while True:
        url = f"{base}/products.json?limit=250&status=active&since_id={since_id}&fields=id,title,handle"
        data = fetch_json(url)
        products = data.get("products", [])
        if not products:
            break

        for p in products:
            mf_stats["checked"] += 1
            mf_url = f"{base}/products/{p['id']}/metafields.json"

            try:
                mf_data = fetch_json(mf_url)
                metafields = mf_data.get("metafields", [])
            except Exception:
                continue

            has_title = False
            has_desc = False
            is_hidden = False

            for mf in metafields:
                if mf["namespace"] == "global" and mf["key"] == "title_tag":
                    has_title = True
                elif mf["namespace"] == "global" and mf["key"] == "description_tag":
                    has_desc = True
                elif mf["namespace"] == "seo" and mf["key"] == "hidden":
                    if str(mf["value"]) == "1":
                        is_hidden = True
                        if len(stats["sample_seo_hidden"]) < 10:
                            stats["sample_seo_hidden"].append({"title": p["title"], "handle": p["handle"]})

            if has_title:
                mf_stats["has_title"] += 1
            if has_desc:
                mf_stats["has_desc"] += 1
            if is_hidden:
                mf_stats["seo_hidden"] += 1

            time.sleep(0.5)

        since_id = products[-1]["id"]
        mf_page += 1
        if mf_page % 2 == 0:
            print(f"  Metafield page {mf_page} — {mf_stats['checked']} products...")

        # Only scan first 500 products for metafields (rate limit friendly), extrapolate
        if mf_stats["checked"] >= 500:
            print(f"  Sampled {mf_stats['checked']} products for metafields, extrapolating...")
            break

    # Extrapolate metafield stats
    scale = stats["total"] / mf_stats["checked"] if mf_stats["checked"] > 0 else 1
    stats["est_with_title_tag"] = round(mf_stats["has_title"] * scale)
    stats["est_without_title_tag"] = stats["total"] - stats["est_with_title_tag"]
    stats["est_with_desc_tag"] = round(mf_stats["has_desc"] * scale)
    stats["est_without_desc_tag"] = stats["total"] - stats["est_with_desc_tag"]
    stats["est_seo_hidden"] = round(mf_stats["seo_hidden"] * scale)
    stats["mf_sample_size"] = mf_stats["checked"]
    stats["mf_raw"] = mf_stats

    # Count duplicates
    dup_count = sum(1 for t, c in stats["duplicate_titles"].items() if c > 1)
    dup_products = sum(c for t, c in stats["duplicate_titles"].items() if c > 1)
    stats["duplicate_title_count"] = dup_count
    stats["duplicate_title_products"] = dup_products

    return stats


def audit_theme_templates():
    """Check theme templates for SEO elements."""
    print("\n=== THEME TEMPLATE SEO AUDIT ===\n")

    findings = []

    # Check theme.liquid for key SEO elements
    print("Checking layout/theme.liquid...")
    theme_liquid = get_asset("layout/theme.liquid")

    checks = {
        "canonical_tag": "canonical" in theme_liquid.lower(),
        "og_tags": 'property="og:' in theme_liquid,
        "twitter_cards": 'name="twitter:' in theme_liquid,
        "structured_data_json_ld": "application/ld+json" in theme_liquid,
        "viewport_meta": "viewport" in theme_liquid,
        "charset_meta": "charset" in theme_liquid,
        "hreflang": "hreflang" in theme_liquid,
        "preconnect": "preconnect" in theme_liquid,
        "custom_homepage_title": "template.name == 'index'" in theme_liquid,
        "custom_homepage_meta": "template.name == 'index'" in theme_liquid and "meta name=\"description\"" in theme_liquid,
    }

    for check, found in checks.items():
        findings.append({"template": "layout/theme.liquid", "check": check, "present": found})
        status = "YES" if found else "NO "
        print(f"  {status} {check}")

    time.sleep(0.5)

    # Check product template
    print("\nChecking product template...")
    try:
        product_json = get_asset("templates/product.json")
        findings.append({"template": "templates/product.json", "check": "product_template_exists", "present": True})
        print("  YES product.json template exists")

        pj = json.loads(product_json)
        sections = list(pj.get("sections", {}).keys())
        print(f"  Sections: {', '.join(sections[:10])}")
    except Exception:
        findings.append({"template": "templates/product.json", "check": "product_template_exists", "present": False})
        print("  NO product.json template not found")

    time.sleep(0.5)

    # Check collection template
    print("\nChecking collection template...")
    try:
        coll_json = get_asset("templates/collection.json")
        findings.append({"template": "templates/collection.json", "check": "collection_template_exists", "present": True})
        print("  YES collection.json template exists")
    except Exception:
        findings.append({"template": "templates/collection.json", "check": "collection_template_exists", "present": False})

    time.sleep(0.5)

    # Check for robots.txt.liquid
    print("\nChecking robots.txt...")
    try:
        robots = get_asset("templates/robots.txt.liquid")
        findings.append({"template": "robots.txt.liquid", "check": "custom_robots", "present": True})
        print("  YES Custom robots.txt.liquid exists")
        print(f"  Content preview: {robots[:200]}")
    except Exception:
        findings.append({"template": "robots.txt.liquid", "check": "custom_robots", "present": False})
        print("  NO No custom robots.txt (using Shopify default)")

    time.sleep(0.5)

    # Check for structured data snippets
    print("\nChecking for schema/structured data snippets...")
    try:
        asset_list = fetch_json(f"https://{STORE}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json")
        all_assets = [a["key"] for a in asset_list["assets"]]

        schema_snippets = [a for a in all_assets if "schema" in a.lower() or "json-ld" in a.lower() or "structured" in a.lower()]
        print(f"  Schema-related assets: {schema_snippets if schema_snippets else 'None found'}")

        seo_snippets = [a for a in all_assets if "seo" in a.lower()]
        print(f"  SEO-related assets: {seo_snippets if seo_snippets else 'None found'}")

        findings.append({"template": "assets", "check": "schema_snippets", "present": bool(schema_snippets), "details": schema_snippets})
        findings.append({"template": "assets", "check": "seo_snippets", "present": bool(seo_snippets), "details": seo_snippets})
    except Exception as e:
        print(f"  Error listing assets: {e}")

    return findings


def audit_collections():
    """Check collection pages for SEO data."""
    print("\n=== COLLECTION SEO AUDIT ===\n")

    collections = []
    url = f"https://{STORE}/admin/api/{API_VERSION}/custom_collections.json?limit=250"
    data = fetch_json(url)
    for c in data.get("custom_collections", []):
        collections.append({
            "id": c["id"],
            "title": c["title"],
            "handle": c["handle"],
            "body_html": c.get("body_html", ""),
            "sort_order": c.get("sort_order", ""),
            "type": "custom",
        })

    time.sleep(0.5)

    url = f"https://{STORE}/admin/api/{API_VERSION}/smart_collections.json?limit=250"
    data = fetch_json(url)
    for c in data.get("smart_collections", []):
        collections.append({
            "id": c["id"],
            "title": c["title"],
            "handle": c["handle"],
            "body_html": c.get("body_html", ""),
            "sort_order": c.get("sort_order", ""),
            "type": "smart",
        })

    stats = {
        "total": len(collections),
        "missing_body": 0,
        "short_body": 0,
        "has_body": 0,
        "collections": collections,
    }

    for c in collections:
        body = (c["body_html"] or "").replace("<br>", "").replace("<p>", "").replace("</p>", "").strip()
        if not body:
            stats["missing_body"] += 1
        elif len(body) < 100:
            stats["short_body"] += 1
        else:
            stats["has_body"] += 1

    print(f"Total collections: {stats['total']}")
    print(f"  With description: {stats['has_body']}")
    print(f"  Short description (<100 chars): {stats['short_body']}")
    print(f"  Missing description: {stats['missing_body']}")

    return stats


def audit_pages():
    """Check static pages for SEO data."""
    print("\n=== PAGES SEO AUDIT ===\n")

    url = f"https://{STORE}/admin/api/{API_VERSION}/pages.json?limit=250"
    data = fetch_json(url)
    pages = data.get("pages", [])

    stats = {
        "total": len(pages),
        "published": 0,
        "missing_body": 0,
        "short_body": 0,
        "pages": [],
    }

    for p in pages:
        body = (p.get("body_html", "") or "").strip()
        is_published = p.get("published_at") is not None
        if is_published:
            stats["published"] += 1

        page_info = {
            "title": p["title"],
            "handle": p["handle"],
            "published": is_published,
            "body_length": len(body),
            "has_body": bool(body),
        }
        stats["pages"].append(page_info)

        if not body:
            stats["missing_body"] += 1
        elif len(body) < 200:
            stats["short_body"] += 1

    print(f"Total pages: {stats['total']}")
    print(f"  Published: {stats['published']}")
    print(f"  Missing body: {stats['missing_body']}")
    print(f"  Short body (<200 chars): {stats['short_body']}")
    for p in stats["pages"]:
        status = "published" if p["published"] else "draft"
        print(f"  - {p['title']} ({p['handle']}) [{status}] — {p['body_length']} chars")

    return stats


def audit_blog():
    """Check blog posts."""
    print("\n=== BLOG SEO AUDIT ===\n")

    url = f"https://{STORE}/admin/api/{API_VERSION}/blogs.json"
    data = fetch_json(url)
    blogs = data.get("blogs", [])

    stats = {"blogs": [], "total_articles": 0}

    for blog in blogs:
        time.sleep(0.5)
        art_url = f"https://{STORE}/admin/api/{API_VERSION}/blogs/{blog['id']}/articles/count.json"
        art_count = fetch_json(art_url).get("count", 0)
        stats["blogs"].append({"title": blog["title"], "handle": blog["handle"], "article_count": art_count})
        stats["total_articles"] += art_count
        print(f"  Blog: {blog['title']} — {art_count} articles")

    if not blogs:
        print("  No blogs found")

    return stats


if __name__ == "__main__":
    print("=" * 60)
    print("FULL SEO/AEO AUDIT — THE CLOTHING COVE")
    print("=" * 60)
    print(f"Store: {STORE}\n")

    results = {}

    results["products"] = audit_products()
    results["theme"] = audit_theme_templates()
    results["collections"] = audit_collections()
    results["pages"] = audit_pages()
    results["blog"] = audit_blog()

    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seo-audit-results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    # Print summary
    p = results["products"]
    print("\n" + "=" * 60)
    print("SEO AUDIT SUMMARY")
    print("=" * 60)

    print(f"\nPRODUCT SEO ({p['total']:,} products scanned):")
    print(f"  Missing body/description:     {p['missing_body_html']:,}")
    print(f"  Short body (<100 chars):      {p['short_body_html']:,}")
    print(f"  Missing images:               {p['missing_images']:,}")
    print(f"  Images without alt text:      {p['images_without_alt']:,} / {p['images_total']:,}")
    print(f"  Products with NO alt text:    {p['products_with_no_alt_images']:,}")
    print(f"  Missing product type:         {p['missing_product_type']:,}")
    print(f"  Missing vendor:               {p['missing_vendor']:,}")
    print(f"  Missing tags:                 {p['missing_tags']:,}")
    print(f"  Duplicate titles:             {p['duplicate_title_count']:,} titles across {p['duplicate_title_products']:,} products")
    print(f"  Est. missing SEO title tag:   {p['est_without_title_tag']:,}")
    print(f"  Est. missing SEO description: {p['est_without_desc_tag']:,}")
    print(f"  Est. SEO hidden:              {p['est_seo_hidden']:,}")

    c = results["collections"]
    print(f"\nCOLLECTION SEO ({c['total']} collections):")
    print(f"  Missing description:          {c['missing_body']}")
    print(f"  Short description:            {c['short_body']}")
    print(f"  Has description:              {c['has_body']}")

    pg = results["pages"]
    print(f"\nPAGES ({pg['total']} pages):")
    print(f"  Published:                    {pg['published']}")
    print(f"  Missing body:                 {pg['missing_body']}")

    b = results["blog"]
    print(f"\nBLOG:")
    print(f"  Blogs: {len(b['blogs'])}, Total articles: {b['total_articles']}")

    print(f"\nFull data saved to {out_path}")
    print("Done!")
