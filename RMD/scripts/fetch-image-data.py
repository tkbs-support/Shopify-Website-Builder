"""Fetch image-level detail for active products: URLs, dimensions, variant-image links.
Read-only. Writes data/images.jsonl. Run from the RMD folder.
"""
import json
import os
import time
import urllib.request

from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), ".env"))
STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL_URL = f"https://{STORE}/admin/api/2024-10/graphql.json"


def gql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(GQL_URL, data=payload, method="POST",
                                 headers={"X-Shopify-Access-Token": TOKEN,
                                          "Content-Type": "application/json"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                out = json.loads(resp.read())
                if out.get("errors"):
                    raise RuntimeError(json.dumps(out["errors"])[:500])
                return out["data"]
        except RuntimeError:
            raise
        except Exception:
            if attempt < 7:
                time.sleep(3)
                continue
            raise


BULK = """
{
  products(query: "status:active") {
    edges {
      node {
        id title handle productType totalInventory onlineStorePreviewUrl
        featuredImage { id }
        options { name values }
        images {
          edges { node { id url width height altText } }
        }
        variants {
          edges { node {
            id title inventoryQuantity
            selectedOptions { name value }
            image { id }
          } }
        }
      }
    }
  }
}
"""

mutation = """
mutation($q: String!) {
  bulkOperationRunQuery(query: $q) {
    bulkOperation { id status }
    userErrors { field message }
  }
}"""
data = gql(mutation, {"q": BULK})
errs = data["bulkOperationRunQuery"]["userErrors"]
if errs:
    raise SystemExit(f"bulk start failed: {errs}")
print("bulk started")
while True:
    time.sleep(5)
    op = gql("{ currentBulkOperation { status errorCode objectCount fileSize url } }")["currentBulkOperation"]
    print(" ", op["status"], op.get("objectCount"))
    if op["status"] == "COMPLETED":
        break
    if op["status"] in ("FAILED", "CANCELED"):
        raise SystemExit(f"bulk {op['status']}: {op.get('errorCode')}")
urllib.request.urlretrieve(op["url"], "data/images.jsonl")
print("saved data/images.jsonl,", op["objectCount"], "objects")
