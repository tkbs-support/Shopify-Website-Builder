"""Download and analyze in-stock product images: resolution, blur/graininess,
duplicate detection (reused stock crystal photos), variant-image linkage.

Writes data/image-analysis.json. Run from the RMD folder after fetch-image-data.py.
"""
import io
import json
import os
import re
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image as PImage

DATA = "data"
CACHE = os.path.join(DATA, "imgcache")
os.makedirs(CACHE, exist_ok=True)

# ---------- load bulk export ----------
products = {}
with open(os.path.join(DATA, "images.jsonl"), encoding="utf-8") as f:
    for line in f:
        n = json.loads(line)
        nid = n.get("id", "")
        pid = n.get("__parentId")
        if pid is None and "/Product/" in nid:
            n["_images"] = []
            n["_variants"] = []
            products[nid] = n
        elif pid and "/ProductVariant/" in nid:
            products[pid]["_variants"].append(n)
        elif pid:
            products[pid]["_images"].append(n)

stock = [p for p in products.values() if (p.get("totalInventory") or 0) > 0]
print(f"{len(products)} active products, {len(stock)} in stock")

# color vocabulary from the main audit (for swatch-name detection)
color_tokens = set()
try:
    a = json.load(open(os.path.join(DATA, "analysis.json"), encoding="utf-8"))
    for val, _ in a.get("color_values", []):
        for tok in re.split(r"[^A-Z0-9]+", val.upper()):
            if len(tok) >= 4:
                color_tokens.add(tok)
except Exception:
    pass
print(f"{len(color_tokens)} color tokens loaded")


def cdn_resize(url, width=800):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}width={width}"


def img_num_id(gid):
    return gid.rsplit("/", 1)[-1]


def download(img):
    path = os.path.join(CACHE, img_num_id(img["id"]) + ".img")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    for attempt in range(5):
        try:
            req = urllib.request.Request(cdn_resize(img["url"]),
                                         headers={"User-Agent": "Mozilla/5.0 TKBS-ImageAudit"})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
            with open(path, "wb") as f:
                f.write(body)
            return path
        except Exception:
            time.sleep(1 + attempt)
    return None


def dhash(gray_img, size=8):
    small = gray_img.resize((size + 1, size), PImage.LANCZOS)
    px = np.asarray(small, dtype=np.float32)
    bits = px[:, 1:] > px[:, :-1]
    return "".join("1" if b else "0" for b in bits.flatten())


def blur_score(gray_arr):
    g = gray_arr.astype(np.float32)
    lap = (4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:])
    return float(lap.var())


# ---------- download + per-image metrics ----------
all_imgs = []
for p in stock:
    for img in p["_images"]:
        all_imgs.append((p, img))
print(f"{len(all_imgs)} in-stock images to analyze")

results = {}

def process(item):
    p, img = item
    iid = img["id"]
    rec = {"product_id": p["id"], "url": img["url"],
           "width": img.get("width") or 0, "height": img.get("height") or 0,
           "alt": (img.get("altText") or "").strip()}
    path = download(img)
    if path:
        try:
            with PImage.open(path) as im:
                gray = im.convert("L")
                rec["dhash"] = dhash(gray)
                arr = np.asarray(gray)
                rec["blur"] = round(blur_score(arr), 1)
                rec["mean_lum"] = round(float(arr.mean()), 1)
        except Exception as e:
            rec["error"] = str(e)[:100]
    else:
        rec["error"] = "download failed"
    results[iid] = rec
    return iid

t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    done = 0
    for _ in ex.map(process, all_imgs):
        done += 1
        if done % 150 == 0:
            print(f"  {done}/{len(all_imgs)} ({time.time()-t0:.0f}s)")
print(f"downloaded+hashed {len(results)} images in {time.time()-t0:.0f}s")

# ---------- duplicate clusters (cross product) ----------
by_hash = defaultdict(list)
for iid, rec in results.items():
    if rec.get("dhash"):
        by_hash[rec["dhash"]].append(iid)
clusters = {h: ids for h, ids in by_hash.items() if len(ids) > 1}
prod_title = {p["id"]: p["title"] for p in products.values()}
cluster_info = []
for h, ids in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
    prods = sorted({prod_title[results[i]["product_id"]] for i in ids})
    cluster_info.append({"hash": h, "images": len(ids), "products": len(prods),
                         "product_titles": prods[:12],
                         "sample_url": results[ids[0]]["url"]})

# blur threshold: bottom 12th percentile of valid scores, capped
blurs = sorted(r["blur"] for r in results.values() if "blur" in r)
blur_cut = min(np.percentile(blurs, 12), 120.0) if blurs else 0
print(f"blur cutoff: {blur_cut:.0f} (median {np.median(blurs):.0f})")


def filename_of(url):
    return url.split("/")[-1].split("?")[0]


def looks_like_swatch_name(img_rec):
    name = re.sub(r"\.[a-z]+$", "", filename_of(img_rec["url"]).upper())
    toks = set(re.split(r"[^A-Z0-9]+", name))
    return len(toks & color_tokens) > 0


# ---------- per-product assessment ----------
product_rows = []
image_rows = []
variant_rows = []
totals = defaultdict(int)

for p in stock:
    pid = p["id"]
    imgs = p["_images"]
    variants = p["_variants"]
    real_variants = [v for v in variants if (v.get("title") or "") != "Default Title"]
    color_opt = next((o for o in p.get("options") or [] if (o["name"] or "").strip().lower() in ("color", "colors")), None)
    issues = []

    if not imgs:
        issues.append("NO_IMAGES")
        totals["products_no_images"] += 1

    unlinked = [v for v in real_variants if not v.get("image")]
    if imgs and unlinked:
        issues.append("VARIANTS_UNLINKED")
        totals["products_variants_unlinked"] += 1
        for v in unlinked:
            opt = "; ".join(f"{o['value']}" for o in v.get("selectedOptions") or [])
            variant_rows.append({"product": p["title"], "handle": p["handle"],
                                 "variant": opt or v.get("title"),
                                 "in_stock": (v.get("inventoryQuantity") or 0) > 0,
                                 "issue": "Variant not linked to any image"})

    # variant color count vs image count: many colors, one image = stock photo suspicion
    if color_opt and imgs:
        n_colors = len(color_opt.get("values") or [])
        if n_colors >= 3 and len(imgs) == 1:
            issues.append("ONE_IMAGE_MANY_COLORS")
            totals["products_one_image_many_colors"] += 1

    low_res = blurry = dup = swatchy = 0
    for img in imgs:
        rec = results.get(img["id"], {})
        img_issues = []
        w, h = rec.get("width", 0), rec.get("height", 0)
        if w and min(w, h) < 800:
            img_issues.append("LOW_RES")
            low_res += 1
        if rec.get("blur", 1e9) < blur_cut:
            img_issues.append("BLURRY_REVIEW")
            blurry += 1
        if rec.get("dhash") in clusters:
            n_prods = len({results[i]["product_id"] for i in clusters[rec["dhash"]]})
            if n_prods > 1:
                img_issues.append("DUPLICATE_ACROSS_PRODUCTS")
                dup += 1
        if looks_like_swatch_name(rec) if rec.get("url") else False:
            img_issues.append("STOCK_SWATCH_NAME")
            swatchy += 1
        if img_issues:
            image_rows.append({"product": p["title"], "handle": p["handle"],
                               "image_url": rec.get("url", ""), "width": w, "height": h,
                               "blur": rec.get("blur"), "issues": img_issues})
    if low_res:
        issues.append("LOW_RES")
        totals["products_low_res"] += 1
    if blurry:
        issues.append("BLURRY_REVIEW")
        totals["products_blurry"] += 1
    if dup:
        issues.append("STOCK_DUPLICATE")
        totals["products_stock_dup"] += 1
    if swatchy:
        issues.append("STOCK_SWATCH_NAME")
        totals["products_swatch_name"] += 1

    totals["images_low_res"] += low_res
    totals["images_blurry"] += blurry
    totals["images_dup"] += dup
    totals["images_swatch_name"] += swatchy
    if issues:
        totals["products_with_any_issue"] += 1

    product_rows.append({
        "product": p["title"], "handle": p["handle"], "type": p.get("productType") or "",
        "preview": p.get("onlineStorePreviewUrl") or "",
        "images": len(imgs), "variants": len(real_variants) or 1,
        "colors": len((color_opt or {}).get("values") or []),
        "unlinked_variants": len(unlinked) if imgs else len(real_variants),
        "issues": issues,
    })

out = {
    "scope": {"in_stock_products": len(stock), "images_analyzed": len(results),
              "blur_cutoff": round(float(blur_cut), 1)},
    "totals": dict(totals),
    "clusters": cluster_info,
    "products": sorted(product_rows, key=lambda r: -len(r["issues"])),
    "image_rows": image_rows,
    "variant_rows": variant_rows,
}
with open(os.path.join(DATA, "image-analysis.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
print("wrote data/image-analysis.json")
print(json.dumps(dict(totals), indent=1))
print(f"duplicate clusters spanning multiple products: {sum(1 for c in cluster_info if c['products'] > 1)}")
