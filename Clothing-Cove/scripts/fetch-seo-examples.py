import json, os, sys, urllib.request, time
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
STORE=os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN=os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL=f"https://{STORE}/admin/api/2024-10/graphql.json"
def gql(q,v=None):
    p=json.dumps({"query":q,"variables":v or {}}).encode()
    r=urllib.request.Request(GQL,data=p,method="POST",headers={"X-Shopify-Access-Token":TOKEN,"Content-Type":"application/json"})
    for a in range(6):
        try:
            with urllib.request.urlopen(r,timeout=60) as resp:
                o=json.loads(resp.read())
                if o.get("errors"): raise RuntimeError(json.dumps(o["errors"])[:300])
                return o["data"]
        except Exception:
            if a<5: time.sleep(5); continue
            raise
Q="""query($c:String){ products(first:100, sortKey:TITLE, query:"status:active inventory_total:>0 published_status:published", after:$c){
  pageInfo{hasNextPage endCursor}
  nodes{ handle title seo{title description}
    tt:metafield(namespace:"global",key:"title_tag"){value}
    dt:metafield(namespace:"global",key:"description_tag"){value} } } }"""
def s(x): return (x or "").strip()
def clean(t): t=t.lower(); return not any(w in t for w in ["test","delete","do not","sample","copy"])
title_only=[]; desc_only=[]; both=[]; cur=None; pages=0
while pages<16 and (len(title_only)<10 or len(desc_only)<10 or len(both)<20):
    d=gql(Q,{"c":cur})["products"]; pages+=1
    for p in d["nodes"]:
        t=s(p.get("title"))
        if not t or not clean(t): continue
        has_t = bool(s((p.get("seo") or {}).get("title")) or (s((p.get("tt") or {}).get("value")) if p.get("tt") else ""))
        has_d = bool(s((p.get("seo") or {}).get("description")) or (s((p.get("dt") or {}).get("value")) if p.get("dt") else ""))
        rec=(t, f"https://theclothingcove.com/products/{p.get('handle')}")
        if not has_t and not has_d and len(both)<20: both.append(rec)
        elif not has_t and has_d and len(title_only)<10: title_only.append(rec)
        elif has_t and not has_d and len(desc_only)<10: desc_only.append(rec)
    if not d["pageInfo"]["hasNextPage"]: break
    cur=d["pageInfo"]["endCursor"]
missing_desc = desc_only + both[:10-len(desc_only)]   # 10 missing description (distinct from 'both' list below)
missing_both = both[10-len(desc_only):][:10]
def show(name, lst):
    print(f"\n=== {name} ({len(lst)}) ===")
    for t,u in lst: print(f"  • {t[:50]:50}  {u}")
print(f"[counts] title_only={len(title_only)} desc_only={len(desc_only)} both>={len(both)}")
show("MISSING SEO TITLE", title_only)
show("MISSING META DESCRIPTION", missing_desc)
show("MISSING BOTH", missing_both)
