import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
STORE=os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN=os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL=f"https://{STORE}/admin/api/2024-10/graphql.json"
OUT=os.path.join(os.path.dirname(__file__),"..","data","seo-titles.jsonl")
def gql(q,v=None):
    p=json.dumps({"query":q,"variables":v or {}}).encode()
    r=urllib.request.Request(GQL,data=p,method="POST",headers={"X-Shopify-Access-Token":TOKEN,"Content-Type":"application/json"})
    for a in range(6):
        try:
            with urllib.request.urlopen(r,timeout=120) as resp:
                o=json.loads(resp.read())
                if o.get("errors"): raise RuntimeError(json.dumps(o["errors"])[:300])
                return o["data"]
        except Exception:
            if a<5: time.sleep(6); continue
            raise
BULK="""{ products { edges { node {
  status totalInventory
  seo { title }
  tt: metafield(namespace:"global", key:"title_tag"){ value }
} } } }"""
m="""mutation($q:String!){ bulkOperationRunQuery(query:$q){ bulkOperation{id status} userErrors{message} } }"""
d=gql(m,{"q":BULK})
if d["bulkOperationRunQuery"]["userErrors"]: raise SystemExit(d["bulkOperationRunQuery"]["userErrors"])
while True:
    op=gql("{ currentBulkOperation { status objectCount url } }")["currentBulkOperation"]
    if op["status"] in ("COMPLETED","FAILED","CANCELED"): break
    time.sleep(8)
print("status:", op["status"], "objects:", op.get("objectCount"))
urllib.request.urlretrieve(op["url"], OUT)
# analyze
n=es=es_app=truly=0
for line in open(OUT,encoding="utf-8"):
    p=json.loads(line)
    if p.get("status")!="ACTIVE" or (p.get("totalInventory") or 0)<=0: continue
    n+=1
    seot=((p.get("seo") or {}).get("title") or "").strip()
    app=((p.get("tt") or {}) or {}).get("value")
    app=(app or "").strip() if app else ""
    if not seot:
        es+=1
        if app: es_app+=1
        else: truly+=1
print(f"\nIN-STOCK active: {n}")
print(f"empty native seo.title: {es} ({100*es//n}%)   <- the '8,459' metric")
print(f"  of those, app title_tag set: {es_app}")
print(f"  truly no title anywhere:    {truly} ({100*truly//n}%)")
