import json, os, sys, time, urllib.request, re
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
STORE=os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN=os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL=f"https://{STORE}/admin/api/2024-10/graphql.json"; OUT=os.path.join(os.path.dirname(__file__),"..","data","pub-content.jsonl")
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
BULK="""{ products(query:"status:active published_status:published"){ edges { node {
  totalInventory title tags descriptionHtml
  seo{ title description }
  tt: metafield(namespace:"global", key:"title_tag"){ value }
  dt: metafield(namespace:"global", key:"description_tag"){ value }
} } } }"""
d=gql("""mutation($q:String!){ bulkOperationRunQuery(query:$q){ bulkOperation{id} userErrors{message} } }""",{"q":BULK})
if d["bulkOperationRunQuery"]["userErrors"]: raise SystemExit(d["bulkOperationRunQuery"]["userErrors"])
while True:
    op=gql("{ currentBulkOperation { status objectCount url } }")["currentBulkOperation"]
    if op["status"] in ("COMPLETED","FAILED","CANCELED"): break
    time.sleep(8)
urllib.request.urlretrieve(op["url"], OUT)
TAG=re.compile(r'<[^>]+>')
def s(x): return (x or "").strip()
n=mt=md=mtag=mb=sb=0; titles=Counter()
for line in open(OUT,encoding="utf-8"):
    p=json.loads(line)
    if (p.get("totalInventory") or 0)<=0: continue
    n+=1
    if not (s((p.get("seo") or {}).get("title")) or (s(p["tt"]["value"]) if p.get("tt") else "")): mt+=1
    if not (s((p.get("seo") or {}).get("description")) or (s(p["dt"]["value"]) if p.get("dt") else "")): md+=1
    if not (p.get("tags") or []): mtag+=1
    bl=len(TAG.sub('', p.get("descriptionHtml") or "").strip())
    if bl==0: mb+=1
    elif bl<100: sb+=1
    titles[s(p.get("title")).lower()]+=1
dup=sum(c for c in titles.values() if c>1)
print(f"PUBLISHED in-stock: {n}")
print(f"no_title={mt} no_meta={md} no_tags={mtag} no_body={mb} short_body={sb} dup_titles={dup}")
json.dump({"count":n,"no_title":mt,"no_meta":md,"no_tags":mtag,"no_body":mb,"short_body":sb,"dup_titles":dup},
          open(os.path.join(os.path.dirname(__file__),"..","data","pub-content-summary.json"),"w"))
