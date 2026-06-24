import json
import urllib.request
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"

with open(r"a:\TKBS Marketing - Git\Shopify-Website-Builder\collection-analysis.json") as f:
    existing = json.load(f)

found_handles = set(r["handle"] for r in existing)

missing_handles = [
    "brands-brighton-meridian","brands-usa-brands-rachel-marie-designs","brands-usa-brands-vocal",
    "brands-vocal","brands-worlds-softest-socks","brighton","brighton-accessories",
    "brighton-accessories-badge-clips","brighton-accessories-belts","brighton-accessories-keyfobs",
    "brighton-accessories-mens","brighton-accessories-travel","brighton-charms",
    "brighton-charms-amulets","brighton-charms-beads","brighton-charms-charms",
    "brighton-charms-seasonal","brighton-charms-spacers","brighton-charms-stoppers",
    "brighton-eyewear","brighton-eyewear-holders","brighton-eyewear-readers",
    "brighton-eyewear-sunglasses","brighton-handbags","brighton-handbags-backpacks",
    "brighton-handbags-crossbodies","brighton-handbags-hobos","brighton-handbags-organizers",
    "brighton-handbags-straw","brighton-handbags-totes","brighton-handbags-wallets",
    "brighton-jewelry","brighton-jewelry-bracelets","brighton-jewelry-earrings",
    "brighton-jewelry-lockets","brighton-jewelry-necklaces","brighton-jewelry-rings",
    "brighton-jewelry-watches","clothing","clothing-bottoms","clothing-bottoms-best-sellers",
    "clothing-bottoms-capris","clothing-bottoms-cruise-wear","clothing-bottoms-jeans",
    "clothing-bottoms-leggings","clothing-bottoms-perfect-fit-pants","clothing-bottoms-petite",
    "clothing-bottoms-plus","clothing-bottoms-popular","clothing-bottoms-sale",
    "clothing-bottoms-shorts","clothing-bottoms-skirts","clothing-denim","clothing-denim-bell",
    "clothing-denim-capris","clothing-denim-jackets","clothing-denim-jeans",
    "clothing-denim-jeggings","clothing-denim-skinny","clothing-denim-straight-leg",
    "clothing-jumpsuits","clothing-tops","clothing-tops-casual","clothing-tops-dressy",
    "clothing-tops-fashion-cardigans","clothing-tops-jackets","clothing-tops-layering",
    "clothing-tops-plus","clothing-tops-ponchos-and-capes","clothing-tops-sweaters",
    "clothing-tops-tank-tops","clothing-tops-tunics","dresses","dresses-casual",
    "dresses-evening","dresses-mother-of-bride","dresses-pant-sets","dresses-petite",
    "dresses-plus","sale","sale-accessories","sale-bottoms","sale-dresses","sale-tops",
    "shop-with-purpose","shop-with-purpose-accessories","shop-with-purpose-accessories-footwear",
    "shop-with-purpose-accessories-handbags","shop-with-purpose-accessories-hats-and-gloves",
    "shop-with-purpose-accessories-jewelry","shop-with-purpose-accessories-scarves",
    "shop-with-purpose-baby","shop-with-purpose-clothing","shop-with-purpose-clothing-bottoms",
    "shop-with-purpose-clothing-dresses","shop-with-purpose-clothing-tops",
    "shop-with-purpose-home","shop-with-purpose-pet","shop-with-purpose-usa-made",
    "sympli","sympli-best-sellers","sympli-bottoms","sympli-dresses","sympli-layering",
    "sympli-sale","sympli-tops",
]

def fetch_json(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def analyze_body(body_html):
    if not body_html or not body_html.strip():
        return {"has_text": False, "has_image": False, "text_preview": ""}
    has_image = bool(re.search(r"<img\s", body_html, re.IGNORECASE))
    text = re.sub(r"<[^>]+>", " ", body_html)
    text = re.sub(r"\s+", " ", text).strip()
    has_text = len(text) > 10
    return {"has_text": has_text, "has_image": has_image, "text_preview": text[:150] if has_text else ""}

print(f"Fetching {len(missing_handles)} missing collections by handle...")
new_results = []
for i, handle in enumerate(missing_handles):
    url = f"https://{STORE}/admin/api/{API_VERSION}/custom_collections.json?handle={handle}"
    data = fetch_json(url)
    cols = data.get("custom_collections", [])
    if cols:
        c = cols[0]
        body = c.get("body_html") or ""
        analysis = analyze_body(body)
        new_results.append({
            "id": c["id"],
            "handle": c["handle"],
            "title": c["title"],
            "has_text": analysis["has_text"],
            "has_image": analysis["has_image"],
            "text_preview": analysis["text_preview"],
            "body_html_len": len(body),
        })
    else:
        new_results.append({
            "id": 0,
            "handle": handle,
            "title": handle.replace("-", " ").title(),
            "has_text": False,
            "has_image": False,
            "text_preview": "",
            "body_html_len": 0,
        })
    if (i + 1) % 20 == 0:
        print(f"  {i+1}/{len(missing_handles)}...")
        time.sleep(0.5)

all_results = existing + new_results
seen = set()
deduped = []
for r in all_results:
    if r["handle"] not in seen:
        seen.add(r["handle"])
        deduped.append(r)

deduped.sort(key=lambda x: x["handle"])

with open(r"a:\TKBS Marketing - Git\Shopify-Website-Builder\collection-analysis.json", "w", encoding="utf-8") as f:
    json.dump(deduped, f, indent=2)

with_text = sum(1 for r in deduped if r["has_text"])
with_image = sum(1 for r in deduped if r["has_image"])
image_only = sum(1 for r in deduped if r["has_image"] and not r["has_text"])
nothing = sum(1 for r in deduped if not r["has_text"] and not r["has_image"])

print(f"\nTotal navigable collections: {len(deduped)}")
print(f"  With text: {with_text}")
print(f"  With image: {with_image}")
print(f"  Image only (no text): {image_only}")
print(f"  Nothing at all: {nothing}")
