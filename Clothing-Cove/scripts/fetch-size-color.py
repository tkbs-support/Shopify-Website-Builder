"""Read-only bulk fetch of size/color filter-readiness signals.
Pulls options + the taxonomy metafields that actually drive Shopify filters,
so the analysis can score the dual standard (variant option AND metafield).
Writes data/size-color.jsonl. Makes no changes.
"""
import json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()
STORE = os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL = f"https://{STORE}/admin/api/2024-10/graphql.json"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "size-color.jsonl")

def gql(q, v=None):
    payload = json.dumps({"query": q, "variables": v or {}}).encode()
    req = urllib.request.Request(GQL, data=payload, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    for a in range(6):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.loads(r.read())
                if out.get("errors"): raise RuntimeError(json.dumps(out["errors"])[:600])
                return out["data"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<5: time.sleep(6); continue
            raise

BULK = """
{
  products(query: "status:active published_status:published") {
    edges { node {
      id handle title status productType totalInventory
      options { name values }
      sizeStd:    metafield(namespace:"shopify", key:"size")            { value }
      shoeSize:   metafield(namespace:"shopify", key:"shoe-size")       { value }
      ringSize:   metafield(namespace:"shopify", key:"ring-size")       { value }
      accSize:    metafield(namespace:"shopify", key:"accessory-size")  { value }
      colorPat:   metafield(namespace:"shopify", key:"color-pattern")   { value }
      fabric:     metafield(namespace:"shopify", key:"fabric")          { value }
      dressOcc:   metafield(namespace:"shopify", key:"dress-occasion")  { value }
      fit:        metafield(namespace:"shopify", key:"fit")             { value }
      topLen:     metafield(namespace:"shopify", key:"top-length-type") { value }
      skirtLen:   metafield(namespace:"shopify", key:"skirt-dress-length-type") { value }
    } }
  }
}
"""

def run_bulk():
    mut = """mutation($q:String!){ bulkOperationRunQuery(query:$q){
        bulkOperation{ id status } userErrors{ field message } } }"""
    d = gql(mut, {"q": BULK})
    errs = d["bulkOperationRunQuery"]["userErrors"]
    if errs: raise SystemExit("bulk userErrors: " + json.dumps(errs))
    print("bulk started:", d["bulkOperationRunQuery"]["bulkOperation"]["id"])
    poll = "{ currentBulkOperation { id status errorCode objectCount fileSize url } }"
    while True:
        op = gql(poll)["currentBulkOperation"]
        print(f"  status={op['status']} objects={op.get('objectCount')} size={op.get('fileSize')}")
        if op["status"] in ("COMPLETED","FAILED","CANCELED"):
            break
        time.sleep(8)
    if op["status"] != "COMPLETED":
        raise SystemExit("bulk did not complete: " + json.dumps(op))
    url = op["url"]
    if not url:
        open(OUT, "w").close(); print("no rows"); return
    print("downloading", op["fileSize"], "bytes...")
    urllib.request.urlretrieve(url, OUT)
    n = sum(1 for _ in open(OUT, encoding="utf-8"))
    print("wrote", OUT, "rows:", n)

if __name__ == "__main__":
    run_bulk()
