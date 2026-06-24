import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
STORE=os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN=os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL=f"https://{STORE}/admin/api/2024-10/graphql.json"
OUT=os.path.join(os.path.dirname(__file__),"..","data","seo-meta.jsonl")
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
  seo { title description }
  tt: metafield(namespace:"global", key:"title_tag"){ value }
  dt: metafield(namespace:"global", key:"description_tag"){ value }
} } } }"""
d=gql("""mutation($q:String!){ bulkOperationRunQuery(query:$q){ bulkOperation{id} userErrors{message} } }""",{"q":BULK})
if d["bulkOperationRunQuery"]["userErrors"]: raise SystemExit(d["bulkOperationRunQuery"]["userErrors"])
while True:
    op=gql("{ currentBulkOperation { status objectCount url } }")["currentBulkOperation"]
    if op["status"] in ("COMPLETED","FAILED","CANCELED"): break
    time.sleep(8)
print("status:", op["status"], "objects:", op.get("objectCount"))
urllib.request.urlretrieve(op["url"], OUT)
def s(x): return (x or "").strip()
n=0; tnat=ttag=tany=0; dnat=dtag=dany=0
for line in open(OUT,encoding="utf-8"):
    p=json.loads(line)
    if p.get("status")!="ACTIVE" or (p.get("totalInventory") or 0)<=0: continue
    n+=1
    seo=p.get("seo") or {}
    tn=s(seo.get("title")); tg=s((p.get("tt") or {}).get("value") if p.get("tt") else "")
    dn=s(seo.get("description")); dg=s((p.get("dt") or {}).get("value") if p.get("dt") else "")
    if tn: tnat+=1
    if tg: ttag+=1
    if tn or tg: tany+=1
    if dn: dnat+=1
    if dg: dtag+=1
    if dn or dg: dany+=1
print(f"\nIN-STOCK active: {n}")
print(f"TITLE       native set: {tnat} ({100*tnat//n}%) | app tag set: {ttag} ({100*ttag//n}%) | has either: {tany} ({100*tany//n}%)")
print(f"DESCRIPTION native set: {dnat} ({100*dnat//n}%) | app tag set: {dtag} ({100*dtag//n}%) | has either: {dany} ({100*dany//n}%)")
