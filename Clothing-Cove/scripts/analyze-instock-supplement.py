"""Supplemental in-stock-focused metrics -> data/analysis2.json"""
import json
import os
import re
from collections import Counter

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

products = {}
with open(os.path.join(DATA, "products.jsonl"), encoding="utf-8") as f:
    for line in f:
        n = json.loads(line)
        if "/Product/" in n.get("id", "") and n.get("__parentId") is None:
            products[n["id"]] = n

active = [p for p in products.values() if p["status"] == "ACTIVE"]
stock = [p for p in active if (p.get("totalInventory") or 0) > 0]

def canon(name):
    return (name or "").strip().lower()

def rank_values(pool, key):
    cnt = Counter()
    for p in pool:
        seen = set()
        for o in p.get("options") or []:
            if canon(o["name"]) in (key, key + "s"):
                for v in o.get("values") or []:
                    seen.add(v.strip().upper())
        for v in seen:
            cnt[v] += 1
    return cnt

color_stock = rank_values(stock, "color")
size_stock = rank_values(stock, "size")

refs_all, refs_stock = set(), set()
for p in active:
    mf = p.get("colorPattern")
    if mf and mf.get("value"):
        ids = re.findall(r"gid://shopify/Metaobject/\d+", mf["value"])
        refs_all.update(ids)
        if (p.get("totalInventory") or 0) > 0:
            refs_stock.update(ids)

out = {
    "color_values_stock": color_stock.most_common(60),
    "color_values_stock_unique": len(color_stock),
    "size_values_stock": size_stock.most_common(60),
    "size_values_stock_unique": len(size_stock),
    "metaobject_refs_unique_active": len(refs_all),
    "metaobject_refs_unique_stock": len(refs_stock),
}
with open(os.path.join(DATA, "analysis2.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print(json.dumps({k: (v if isinstance(v, int) else v[:5]) for k, v in out.items()}, default=str))
