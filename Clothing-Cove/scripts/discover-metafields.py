"""Read-only discovery: where do size/color actually live?
Lists product/variant metafield DEFINITIONS, then dumps options + ALL metafields
for specific products the audit flagged as 'missing size'. Makes no changes.
"""
import json, os, sys, urllib.request, urllib.error, time
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()
STORE = os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL = f"https://{STORE}/admin/api/2024-10/graphql.json"

def gql(q, v=None):
    payload = json.dumps({"query": q, "variables": v or {}}).encode()
    req = urllib.request.Request(GQL, data=payload, method="POST",
        headers={"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
    for a in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read())
                if out.get("errors"): raise RuntimeError(json.dumps(out["errors"])[:600])
                return out["data"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<4: time.sleep(5); continue
            raise

DEF_Q = """
query($owner: MetafieldOwnerType!) {
  metafieldDefinitions(first: 100, ownerType: $owner) {
    nodes { name namespace key type { name }
      capabilities { adminFilterable { enabled } } }
  }
}"""
print("STORE:", STORE)
for owner in ["PRODUCT", "PRODUCTVARIANT"]:
    d = gql(DEF_Q, {"owner": owner})
    nodes = d["metafieldDefinitions"]["nodes"]
    print(f"\n===== {owner} metafield definitions ({len(nodes)}) =====")
    for n in nodes:
        af = n["capabilities"]["adminFilterable"]["enabled"]
        print(f"  {n['namespace']}.{n['key']:30} type={n['type']['name']:20} name={n['name']!r} adminFilterable={af}")

# specific flagged products
HANDLES = ["fringed-poncho","cachet-57756-cap-slv-embellished-long-dress","cheetah-print-dress",
           "spring-step-migula-2-tone-cross-strap-sandals","sqn-crcht-poncho"]
PROD_Q = """
query($q: String!) {
  products(first: 5, query: $q) {
    nodes {
      title handle productType
      options { name values }
      metafields(first: 40) { nodes { namespace key type value } }
      variants(first: 3) { nodes { title selectedOptions { name value } } }
    }
  }
}"""
print("\n\n========== FLAGGED PRODUCTS — options vs metafields ==========")
for h in HANDLES:
    d = gql(PROD_Q, {"q": f"handle:{h}"})
    for p in d["products"]["nodes"]:
        print(f"\n--- {p['handle']}  (type {p['productType']})  {p['title'][:50]}")
        print("  OPTIONS:", [(o['name'], o['values'][:6]) for o in p['options']])
        mfs = p['metafields']['nodes']
        sizey = [m for m in mfs if any(w in (m['namespace']+m['key']).lower() for w in ('size','dimension','fit','measure'))]
        print(f"  METAFIELDS ({len(mfs)} total). size/fit-related:")
        for m in sizey: print(f"     {m['namespace']}.{m['key']} ({m['type']}) = {str(m['value'])[:80]}")
        if not sizey:
            for m in mfs[:12]: print(f"     {m['namespace']}.{m['key']} ({m['type']}) = {str(m['value'])[:60]}")
