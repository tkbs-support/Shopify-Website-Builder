"""Analyze fresh audit data from data/ and write data/analysis.json.

Read-only over local files. All numbers computed fresh — nothing taken from old reports.
"""
import json
import os
import re
import sys
import difflib
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from type_expectations import expectation

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass
# Admin domain for permanent product-editor links (never 404, unlike storefront previews)
STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN", "the-clothing-cove-store.myshopify.com")

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def strip_html(html):
    if not html:
        return ""
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ---------- load products ----------
products = {}
with open(os.path.join(DATA, "products.jsonl"), encoding="utf-8") as f:
    for line in f:
        node = json.loads(line)
        nid = node.get("id", "")
        pid = node.get("__parentId")
        if pid is None and "/Product/" in nid:
            node["_variants"] = []
            node["_images"] = []
            products[nid] = node
        elif pid and "/ProductVariant/" in nid:
            products[pid]["_variants"].append(node)
        elif pid and ("/ProductImage/" in nid or "/Image" in nid or "altText" in node):
            products[pid]["_images"].append(node)

all_products = list(products.values())
active = [p for p in all_products if p["status"] == "ACTIVE"]


def in_stock(p):
    ti = p.get("totalInventory")
    if ti is not None:
        return ti > 0
    return any((v.get("inventoryQuantity") or 0) > 0 for v in p["_variants"])


stock = [p for p in active if in_stock(p)]

CANON = {"color": "Color", "size": "Size", "style": "Style", "scent": "Scent",
         "shoe size": "Shoe size", "ring size": "Ring size", "print": "Print",
         "strength": "Strength", "colors": "Color", "title": "Title"}


def canon_opt(name):
    return (name or "").strip().lower()


def has_opt(p, key):
    return any(canon_opt(o["name"]) == key or
               (key == "color" and canon_opt(o["name"]) == "colors")
               for o in p.get("options") or [])


def is_default_title(p):
    opts = p.get("options") or []
    return len(opts) == 1 and canon_opt(opts[0]["name"]) == "title"


def seo_metrics(pool):
    m = {}
    n = len(pool)
    m["count"] = n
    m["missing_body"] = sum(1 for p in pool if len(strip_html(p.get("descriptionHtml"))) == 0)
    m["short_body"] = sum(1 for p in pool if 0 < len(strip_html(p.get("descriptionHtml"))) < 100)
    m["missing_images"] = sum(1 for p in pool if not p["_images"])
    m["images_total"] = sum(len(p["_images"]) for p in pool)
    m["images_no_alt"] = sum(1 for p in pool for i in p["_images"] if not (i.get("altText") or "").strip())
    m["products_zero_alt"] = sum(1 for p in pool if p["_images"] and all(not (i.get("altText") or "").strip() for i in p["_images"]))
    m["missing_tags"] = sum(1 for p in pool if not p.get("tags"))
    m["missing_seo_title"] = sum(1 for p in pool if not ((p.get("seo") or {}).get("title") or "").strip())
    m["missing_seo_desc"] = sum(1 for p in pool if not ((p.get("seo") or {}).get("description") or "").strip())
    m["missing_type"] = sum(1 for p in pool if not (p.get("productType") or "").strip())
    m["missing_vendor"] = sum(1 for p in pool if not (p.get("vendor") or "").strip())
    titles = Counter((p["title"] or "").strip().lower() for p in pool)
    dup = {t: c for t, c in titles.items() if c > 1}
    m["dup_title_products"] = sum(dup.values())
    m["dup_title_groups"] = len(dup)
    m["missing_color"] = sum(1 for p in pool if not has_opt(p, "color"))
    m["missing_size"] = sum(1 for p in pool if not has_opt(p, "size"))
    m["default_title"] = sum(1 for p in pool if is_default_title(p))
    m["has_color_pattern_mf"] = sum(1 for p in pool if p.get("colorPattern"))
    return m


result = {
    "totals": {
        "all_statuses": len(all_products),
        "active": len(active),
        "draft": sum(1 for p in all_products if p["status"] == "DRAFT"),
        "archived": sum(1 for p in all_products if p["status"] == "ARCHIVED"),
        "in_stock": len(stock),
        "out_of_stock": len(active) - len(stock),
    },
    "seo_active": seo_metrics(active),
    "seo_stock": seo_metrics(stock),
}

# ---------- option name inventory ----------
opt_products = defaultdict(set)      # canonical -> product ids
opt_stock = defaultdict(set)
opt_variants = defaultdict(Counter)  # canonical -> raw name -> product count
opt_values = defaultdict(set)
stock_ids = {p["id"] for p in stock}
for p in active:
    for o in p.get("options") or []:
        raw = o["name"]
        c = canon_opt(raw)
        if c == "title":
            continue
        opt_products[c].add(p["id"])
        if p["id"] in stock_ids:
            opt_stock[c].add(p["id"])
        opt_variants[c][raw] += 1
        for v in o.get("values") or []:
            opt_values[c].add(v.strip().upper())

result["option_types"] = [
    {
        "canonical": c,
        "products": len(ids),
        "in_stock": len(opt_stock[c]),
        "unique_values": len(opt_values[c]),
        "raw_names": dict(opt_variants[c].most_common()),
    }
    for c, ids in sorted(opt_products.items(), key=lambda kv: -len(kv[1]))
]

# ---------- known option values (for non-standard-option verdicts) ----------
def _opt_values(key):
    s = set()
    for p in active:
        for o in p.get("options") or []:
            if canon_opt(o["name"]) in (key, key + "s"):
                for v in o.get("values") or []:
                    s.add(v.strip().lower())
    return s
known_color_vals = _opt_values("color")
known_size_vals = _opt_values("size")


def nonstandard_verdict(raw):
    c = raw.strip().lower()
    if c in known_color_vals or c in known_size_vals:
        return "Value used as option name"
    if difflib.SequenceMatcher(None, c, "color").ratio() > 0.6:
        return "Typo — should be Color"
    if difflib.SequenceMatcher(None, c, "size").ratio() > 0.6:
        return "Typo — should be Size"
    if len(c) > 18 or any(ch in raw for ch in "!?") or " our " in (" " + c + " "):
        return "Invalid — not a usable option"
    return "Non-standard — review"


# ---------- data quality ----------
issues = []
for c, raws in opt_variants.items():
    target = CANON.get(c)
    for raw, count in raws.items():
        if target and raw != target:
            if raw.strip() != raw:
                kind = "Trailing/leading space"
            elif raw.strip().lower() == c and raw.strip() != target:
                kind = "Inconsistent casing"
            else:
                kind = "Merge/rename"
            issues.append({"issue": kind, "canonical": target, "raw": raw, "products": count})
    if target is None:
        for raw, count in raws.items():
            issues.append({"issue": nonstandard_verdict(raw), "canonical": "", "raw": raw,
                           "products": count, "nonstandard": True})
result["data_quality"] = sorted(issues, key=lambda x: -x["products"])

# ---------- color & size values ----------
def value_ranking(key):
    cnt = Counter()
    for p in active:
        seen = set()
        for o in p.get("options") or []:
            if canon_opt(o["name"]) in (key, key + "s"):
                for v in o.get("values") or []:
                    seen.add(v.strip().upper())
        for v in seen:
            cnt[v] += 1
    return cnt

color_counts = value_ranking("color")
size_counts = value_ranking("size")
result["color_values"] = color_counts.most_common(60)
result["color_values_unique"] = len(color_counts)
result["size_values"] = size_counts.most_common(60)
result["size_values_unique"] = len(size_counts)

# ---------- by product type ----------
by_type = defaultdict(lambda: {"total": 0, "in_stock": 0, "color": 0, "stock_color": 0,
                               "size": 0, "stock_size": 0, "stock_no_body": 0, "stock_no_img": 0})
for p in active:
    t = (p.get("productType") or "(none)").strip() or "(none)"
    row = by_type[t]
    row["total"] += 1
    s = p["id"] in stock_ids
    c = has_opt(p, "color")
    z = has_opt(p, "size")
    if s:
        row["in_stock"] += 1
        if c:
            row["stock_color"] += 1
        if z:
            row["stock_size"] += 1
        if len(strip_html(p.get("descriptionHtml"))) == 0:
            row["stock_no_body"] += 1
        if not p["_images"]:
            row["stock_no_img"] += 1
    if c:
        row["color"] += 1
    if z:
        row["size"] += 1
result["by_type"] = sorted(({"type": k, **v} for k, v in by_type.items()), key=lambda r: -r["total"])

# ---------- filter readiness: type-aware Color/Size expectation + per-SKU worklist ----------
# Missing an option is only a PROBLEM when the product type should have it.
type_exp = {}
for row in result["by_type"]:
    ins = row["in_stock"]
    cc = row["stock_color"] / ins if ins else 0.0
    sc = row["stock_size"] / ins if ins else 0.0
    label, cat, ec, es, basis, review = expectation(row["type"], cc, sc)
    row["label"], row["category"] = label, cat
    row["expects_color"], row["expects_size"] = ec, es
    row["basis"], row["review"] = basis, review
    row["color_problems"] = (ins - row["stock_color"]) if ec else 0
    row["size_problems"] = (ins - row["stock_size"]) if es else 0
    type_exp[row["type"]] = row

result["color_problems"] = sum(r["color_problems"] for r in result["by_type"])
result["size_problems"] = sum(r["size_problems"] for r in result["by_type"])
result["types_expecting_color"] = sum(1 for r in result["by_type"] if r["expects_color"])
result["types_expecting_size"] = sum(1 for r in result["by_type"] if r["expects_size"])
# raw (type-blind) counts kept for the "false positives removed" story
result["missing_color_alltypes"] = result["seo_stock"]["missing_color"]
result["missing_size_alltypes"] = result["seo_stock"]["missing_size"]

ACC_CATS = {"Bag", "Scarf", "Hat", "HairAcc", "Eyewear", "Wallet", "Accessory", "Belt", "Readers"}
worklist = []
for p in stock:
    code = (p.get("productType") or "(none)").strip() or "(none)"
    te = type_exp.get(code)
    if not te:
        continue
    miss_c = te["expects_color"] and not has_opt(p, "color")
    miss_s = te["expects_size"] and not has_opt(p, "size")
    if not (miss_c or miss_s):
        continue
    cat = te["category"]
    if miss_s and cat in ("Apparel", "Footwear"):
        pr = 1
    elif miss_c and cat in ("Apparel", "Footwear"):
        pr = 2
    elif miss_c and cat in ACC_CATS:
        pr = 3
    else:
        pr = 4
    worklist.append({
        "priority": pr,
        "title": (p.get("title") or "").strip()[:70],
        "type": te["label"],
        "vendor": (p.get("vendor") or "").strip(),
        "missing_color": "Yes" if miss_c else "",
        "missing_size": "Yes" if miss_s else "",
        # permanent admin product-editor link — always valid for an existing active product
        "admin_url": f"https://{STORE_DOMAIN}/admin/products/{p['id'].split('/')[-1]}",
    })
worklist.sort(key=lambda w: (w["priority"], w["type"], w["title"]))
result["problem_worklist"] = worklist

# ---------- brand / vendor facet ----------
vend = Counter((p.get("vendor") or "").strip() for p in stock)
result["brand"] = {
    "missing": vend.get("", 0),
    "distinct": len([v for v in vend if v]),
    "top": vend.most_common(12),
}

# ---------- material / fabric facet (data currently trapped in description prose) ----------
FAB = ["cotton", "polyester", "rayon", "bamboo", "linen", "silk", "wool", "nylon",
       "spandex", "denim", "leather", "cashmere", "viscose", "modal", "acrylic", "velvet"]
fabcnt = Counter()
mat_products = 0
for p in stock:
    text = strip_html(p.get("descriptionHtml")).lower()
    found = [f for f in FAB if re.search(r"\b" + f + r"\b", text)]
    if found:
        mat_products += 1
    for f in found:
        fabcnt[f] += 1
result["material"] = {
    "in_desc": mat_products,
    "structured_option": sum(1 for p in stock for o in (p.get("options") or [])
                             if "material" in canon_opt(o["name"]) or "fabric" in canon_opt(o["name"])),
    "top_fabrics": fabcnt.most_common(12),
}

# ---------- duplicate titles detail ----------
titles = defaultdict(list)
for p in stock:
    titles[(p["title"] or "").strip().lower()].append(p)
dups = [{"title": ps[0]["title"], "products": len(ps), "vendors": len({p.get('vendor') for p in ps})}
        for t, ps in titles.items() if len(ps) > 1]
result["dup_titles_stock"] = sorted(dups, key=lambda d: -d["products"])[:40]

# ---------- aging: how old is the out-of-stock tail ----------
from datetime import datetime, timezone
def yr(p):
    try:
        return int(p["createdAt"][:4])
    except Exception:
        return 0
created_active = Counter(yr(p) for p in active)
created_stock = Counter(yr(p) for p in stock)
result["created_by_year_active"] = dict(sorted(created_active.items()))
result["created_by_year_stock"] = dict(sorted(created_stock.items()))
oos = [p for p in active if p["id"] not in stock_ids]
upd_oos = Counter(int(p["updatedAt"][:4]) for p in oos)
result["oos_updated_by_year"] = dict(sorted(upd_oos.items()))

# ---------- price ranges (in-stock) ----------
prices = []
for p in stock:
    for v in p["_variants"]:
        try:
            prices.append(float(v.get("price") or 0))
        except Exception:
            pass
prices = [x for x in prices if x > 0]
prices.sort()
if prices:
    result["price_stats"] = {
        "min": prices[0], "max": prices[-1],
        "median": prices[len(prices) // 2],
        "p25": prices[len(prices) // 4],
        "p75": prices[3 * len(prices) // 4],
    }

# ---------- collections ----------
collections = []
with open(os.path.join(DATA, "collections.jsonl"), encoding="utf-8") as f:
    for line in f:
        n = json.loads(line)
        if "/Collection/" in n.get("id", ""):
            txt = strip_html(n.get("descriptionHtml"))
            collections.append({
                "title": n["title"], "handle": n["handle"],
                "desc_len": len(txt), "desc_preview": txt[:140],
                "seo_title": ((n.get("seo") or {}).get("title") or "").strip(),
                "seo_desc": ((n.get("seo") or {}).get("description") or "").strip(),
                "products": (n.get("productsCount") or {}).get("count", 0),
                "has_image": bool(n.get("image")),
                "smart": bool(n.get("ruleSet")),
            })
col_total = len(collections)
result["collections"] = {
    "total": col_total,
    "missing_desc": sum(1 for c in collections if c["desc_len"] == 0),
    "short_desc": sum(1 for c in collections if 0 < c["desc_len"] < 100),
    "good_desc": sum(1 for c in collections if c["desc_len"] >= 100),
    "missing_seo_title": sum(1 for c in collections if not c["seo_title"]),
    "missing_seo_desc": sum(1 for c in collections if not c["seo_desc"]),
    "no_image": sum(1 for c in collections if not c["has_image"]),
    "empty": sum(1 for c in collections if c["products"] == 0),
    "smart": sum(1 for c in collections if c["smart"]),
}
result["collections_list"] = sorted(collections, key=lambda c: -c["products"])

# ---------- navigable collections (parsed from live homepage nav) ----------
nav = {}
home_nav = os.path.join(DATA, "live", "home.html")
if os.path.exists(home_nav):
    html = open(home_nav, encoding="utf-8", errors="replace").read()
    handles = sorted(set(re.findall(r'href="/collections/([^"?#/]+)"', html)))
    hset = set(handles)
    for h in handles:
        if h.startswith("brands-") or h.startswith("brand-"):
            cat = "Brand"
        elif any(h != o and h.startswith(o + "-") for o in hset):
            cat = "Subcategory"
        else:
            cat = "Top-Level"
        nav[h] = {"category": cat}
result["navigable"] = nav

# ---------- pages & blog ----------
pages = json.load(open(os.path.join(DATA, "pages.json"), encoding="utf-8"))
result["pages"] = [{
    "title": p["title"], "handle": p["handle"],
    "published": bool(p.get("published_at")),
    "content_len": len(strip_html(p.get("body_html"))),
} for p in pages]

blogdata = json.load(open(os.path.join(DATA, "blogs.json"), encoding="utf-8"))
arts = blogdata["articles"]
art_years = Counter((a.get("published_at") or a.get("created_at") or "?")[:4] for a in arts)
result["blog"] = {
    "blogs": len(blogdata["blogs"]),
    "articles": len(arts),
    "published": sum(1 for a in arts if a.get("published_at")),
    "by_year": dict(sorted(art_years.items())),
    "latest": max((a.get("published_at") or "" for a in arts), default=""),
}

# ---------- theme checks ----------
theme_dir = os.path.join(DATA, "theme")
checks = {}
tl_path = os.path.join(theme_dir, "layout__theme.liquid")
if os.path.exists(tl_path):
    tl = open(tl_path, encoding="utf-8").read()
    checks["og_tags"] = 'property="og:' in tl or "property='og:" in tl
    checks["twitter_tags"] = 'name="twitter:' in tl
    checks["json_ld_theme"] = "application/ld+json" in tl
    checks["canonical"] = "canonical_url" in tl
    checks["viewport"] = "viewport" in tl
    checks["preconnect"] = "preconnect" in tl
    checks["custom_title_logic"] = "template.name == 'index'" in tl or 'template.name == "index"' in tl
snip = os.path.join(theme_dir, "snippets__microdata-schema.liquid")
checks["microdata_snippet"] = os.path.exists(snip)
sd_path = os.path.join(theme_dir, "config__settings_data.json")
if os.path.exists(sd_path):
    sd = open(sd_path, encoding="utf-8").read()
    checks["color_swatch_config"] = '"color_swatch_config"' in sd
    m = re.search(r'"color_swatch_config"\s*:\s*"((?:[^"\\]|\\.)*)"', sd)
    checks["color_swatch_config_len"] = len(m.group(1)) if m else 0
themes_meta = json.load(open(os.path.join(theme_dir, "themes.json"), encoding="utf-8"))
checks["live_theme"] = next((f"{t['name']} (id {t['id']})" for t in themes_meta if t["role"] == "main"), "?")
checks["theme_count"] = len(themes_meta)
asset_list = json.load(open(os.path.join(theme_dir, "asset_list.json"), encoding="utf-8"))
checks["jsonld_snippets"] = [a["key"] for a in asset_list if "json-ld" in a["key"].lower() or "jsonld" in a["key"].lower() or "schema" in a["key"].lower()]
result["theme"] = checks

# ---------- live homepage ----------
live = {}
home_path = os.path.join(DATA, "live", "home.html")
if os.path.exists(home_path):
    html = open(home_path, encoding="utf-8", errors="replace").read()
    t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
    live["title"] = re.sub(r"\s+", " ", t.group(1)).strip() if t else ""
    d = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    live["meta_description"] = d.group(1) if d else ""
    live["og_tags"] = len(re.findall(r'property="og:', html))
    live["twitter_tags"] = len(re.findall(r'name="twitter:', html))
    live["json_ld_blocks"] = len(re.findall(r"application/ld\+json", html))
    h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    live["h1_count"] = len(h1s)
    live["h1_texts"] = [re.sub(r"<[^>]+>|\s+", " ", h).strip()[:80] for h in h1s[:5]]
    ld_blocks = re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S)
    types = []
    for b in ld_blocks:
        for m in re.finditer(r'"@type"\s*:\s*"([^"]+)"', b):
            types.append(m.group(1))
    live["json_ld_types"] = sorted(set(types))
result["live_home"] = live

counts = json.load(open(os.path.join(DATA, "counts.json"), encoding="utf-8"))
result["counts"] = counts

out = os.path.join(DATA, "analysis.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=1, default=str)
print("wrote", out)

# quick console summary
t = result["totals"]
print(f"products: {t['all_statuses']} total | {t['active']} active | {t['in_stock']} in stock")
print(f"collections: {result['collections']['total']} | missing desc: {result['collections']['missing_desc']}")
print(f"pages: {len(result['pages'])} | articles: {result['blog']['articles']}")
print(f"theme: {checks.get('live_theme')}")
print(f"live home: ld+json={live.get('json_ld_blocks')} og={live.get('og_tags')}")
