"""Read-only: list the taxonomy metaobjects that shopify.color-pattern / shopify.size
reference (GID + name + handle), so we can map raw option values to them.
Also dumps the raw color/size option vocabulary from the catalog (offline).
"""
import json, os, sys, urllib.request, urllib.error, time
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()
STORE=os.getenv("SHOPIFY_STORE_DOMAIN"); TOKEN=os.getenv("SHOPIFY_ACCESS_TOKEN")
GQL=f"https://{STORE}/admin/api/2024-10/graphql.json"
DATA=os.path.join(os.path.dirname(__file__),"..","data")

def gql(q,v=None):
    payload=json.dumps({"query":q,"variables":v or {}}).encode()
    req=urllib.request.Request(GQL,data=payload,method="POST",
        headers={"X-Shopify-Access-Token":TOKEN,"Content-Type":"application/json"})
    for a in range(6):
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                out=json.loads(r.read())
                if out.get("errors"): raise RuntimeError(json.dumps(out["errors"])[:500])
                return out["data"]
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and a<5: time.sleep(6); continue
            raise

# 1. find the metaobject definition referenced by each metafield definition
DEF_Q="""{ metafieldDefinitions(first:100, ownerType:PRODUCT){ nodes{
  namespace key validations{ name value } } } }"""
defs=gql(DEF_Q)["metafieldDefinitions"]["nodes"]
ref={}
for d in defs:
    if d["namespace"]=="shopify" and d["key"] in ("color-pattern","size","shoe-size","ring-size"):
        for v in d["validations"]:
            if "metaobject" in v["name"].lower():
                ref[d["key"]]=v["value"]
print("metaobject definition ids referenced:", ref)

# 2. list entries for each referenced metaobject definition
ENTRIES="""query($id:ID!,$cur:String){ metaobjectDefinition(id:$id){ type name
  metaobjects(first:250, after:$cur){ pageInfo{hasNextPage endCursor}
    nodes{ id handle displayName } } } }"""
taxonomy={}
for key,defid in ref.items():
    entries=[]; cur=None
    while True:
        d=gql(ENTRIES,{"id":defid,"cur":cur})["metaobjectDefinition"]
        mo=d["metaobjects"]
        for n in mo["nodes"]: entries.append({"gid":n["id"],"handle":n["handle"],"name":n["displayName"]})
        if mo["pageInfo"]["hasNextPage"]: cur=mo["pageInfo"]["endCursor"]
        else: break
    taxonomy[key]={"type":d["type"],"name":d["name"],"entries":entries}
    print(f"\n=== {key}  ({d['type']}, {len(entries)} entries) ===")
    print("   ", ", ".join(e["name"] for e in entries[:60]))
json.dump(taxonomy, open(os.path.join(DATA,"taxonomy.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nwrote data/taxonomy.json")

# 3. raw option vocabulary (offline) among in-stock option-only products
rows=[json.loads(l) for l in open(os.path.join(DATA,"size-color.jsonl"),encoding="utf-8")]
def norm(n): return (n or "").strip().lower()
colors=Counter(); sizes=Counter()
for p in rows:
    if p.get("status")!="ACTIVE" or (p.get("totalInventory") or 0)<=0: continue
    for o in p.get("options") or []:
        nm=norm(o["name"])
        if nm in ("color","colors"):
            for v in o["values"]: colors[v.strip()]+=1
        if nm in ("size","shoe size","ring size"):
            for v in o["values"]: sizes[v.strip()]+=1
json.dump({"colors":colors.most_common(),"sizes":sizes.most_common()},
          open(os.path.join(DATA,"raw-vocab.json"),"w",encoding="utf-8"), ensure_ascii=False)
print(f"\nraw COLOR values: {len(colors)} distinct. top:", colors.most_common(25))
print(f"\nraw SIZE values: {len(sizes)} distinct. top:", sizes.most_common(40))
