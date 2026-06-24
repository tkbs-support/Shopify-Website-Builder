import json
import urllib.request
import os
import re
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"

NAV_COLLECTIONS = set("""a-rare-bird accessories accessories-accessories accessories-accessories-belts-1 accessories-accessories-candles accessories-accessories-fragrance accessories-accessories-hats accessories-accessories-hats-and-gloves accessories-accessories-lip-balm accessories-accessories-lotion accessories-accessories-scarves accessories-accessories-small-accessories accessories-accessories-soap accessories-accessories-sunglasses accessories-footwear accessories-footwear-casual accessories-footwear-dressy accessories-footwear-shoe-accessories accessories-footwear-slippers accessories-footwear-socks accessories-handbags accessories-handbags-casual accessories-handbags-evening accessories-handbags-recycled-canvas-bags accessories-handbags-travel accessories-handbags-wallets accessories-jewelry accessories-jewelry-bracelets accessories-jewelry-brooches accessories-jewelry-designer accessories-jewelry-earrings accessories-jewelry-fashion-jewelry accessories-jewelry-necklaces accessories-jewelry-rachel-marie-designs accessories-jewelry-usa-made brand-origami brands brands-adrianna-papell brands-alex-evenings brands-anju-jewelry brands-baggallini brands-bali brands-braza-bra brands-brighton-jewelry-and-accessories brands-brighton-meridian brands-by-jj brands-charlie-b brands-cj-bella brands-coco-carmen brands-damee brands-democracy brands-easel brands-ethyl brands-fca brands-foot-petals brands-forever-new brands-frank-lyman brands-greenleaf brands-habitat brands-inis-fragrance brands-insight-ny brands-jacqueline-kent brands-jade-dresses brands-jag-jeans brands-jess-jane brands-joseph-ribkoff brands-jostar brands-keren-hart brands-liv-by-habitat brands-liverpool-jeans brands-made-in-italy brands-mgny brands-michael-tyler brands-modgy brands-montage brands-multiples-clothing-company brands-my-fun-colors brands-naked-bee brands-north-american-designers brands-north-american-designers-bali brands-north-american-designers-michael-tyler brands-parsley-sage brands-pol brands-pure-essence brands-rachel-marie-designs brands-renuar brands-slim-sation brands-spring-step-shoes brands-sympli brands-tagua-jewelry brands-tenacity-bella-tunno brands-tenacity-democracy brands-tenacity-e-cloth brands-tenacity-insect-shield brands-tenacity-rachel-marie-designs brands-tenacity-vocal brands-tenacity-warmies brands-tribal brands-usa-brands-forever-new brands-usa-brands-naked-bee brands-usa-brands-rachel-marie-designs brands-usa-brands-vocal brands-vocal brands-worlds-softest-socks brighton brighton-accessories brighton-accessories-badge-clips brighton-accessories-belts brighton-accessories-hair brighton-accessories-home brighton-accessories-keyfobs brighton-accessories-mens brighton-accessories-travel brighton-brighton-holiday-gifts-christmas-jewelry brighton-charms brighton-charms-amulets brighton-charms-beads brighton-charms-charms brighton-charms-seasonal brighton-charms-spacers brighton-charms-stoppers brighton-collections brighton-collections-barbados brighton-collections-christo brighton-collections-coastal brighton-collections-contempo brighton-collections-ferrara brighton-collections-halo brighton-collections-interlok brighton-collections-mingle brighton-eyewear brighton-eyewear-holders brighton-eyewear-readers brighton-eyewear-sunglasses brighton-handbags brighton-handbags-backpacks brighton-handbags-barbados-1 brighton-handbags-bucket-bags brighton-handbags-card-cases brighton-handbags-crossbodies brighton-handbags-hobos brighton-handbags-organizers brighton-handbags-shoulder-bags brighton-handbags-straw brighton-handbags-totes brighton-handbags-wallets brighton-jewelry brighton-jewelry-anklets brighton-jewelry-apple-watch-bands brighton-jewelry-bracelets brighton-jewelry-earrings brighton-jewelry-lockets brighton-jewelry-necklaces brighton-jewelry-rings brighton-jewelry-watches clothing clothing-bottoms clothing-bottoms-best-sellers clothing-bottoms-capris clothing-bottoms-cruise-wear clothing-bottoms-jeans clothing-bottoms-leggings clothing-bottoms-perfect-fit-pants clothing-bottoms-petite clothing-bottoms-plus clothing-bottoms-popular clothing-bottoms-sale clothing-bottoms-shorts clothing-bottoms-skirts clothing-denim clothing-denim-bell clothing-denim-capris clothing-denim-jackets clothing-denim-jeans clothing-denim-jeggings clothing-denim-skinny clothing-denim-straight-leg clothing-jumpsuits clothing-tops clothing-tops-casual clothing-tops-dressy clothing-tops-fashion-cardigans clothing-tops-jackets clothing-tops-layering clothing-tops-petite clothing-tops-plus clothing-tops-ponchos-and-capes clothing-tops-sweaters clothing-tops-tank-tops clothing-tops-tunics clothing-tops-vests customer-apprecation dresses dresses-casual dresses-evening dresses-mother-of-bride dresses-pant-sets dresses-petite dresses-plus erin-gray-jewelry gift-cards-on-line-e-gift-cards home-pillows home-tea-towels judy-blue new-arrivals radzoli readers sale sale-accessories sale-bottoms sale-cove-insiders sale-dresses sale-handbags sale-tops shop-with-purpose shop-with-purpose-accessories shop-with-purpose-accessories-footwear shop-with-purpose-accessories-handbags shop-with-purpose-accessories-hats-and-gloves shop-with-purpose-accessories-jewelry shop-with-purpose-accessories-scarves shop-with-purpose-baby shop-with-purpose-brands shop-with-purpose-brands-bella-tunno shop-with-purpose-brands-democracy shop-with-purpose-brands-finchberry shop-with-purpose-brands-manual-woodworkers-weavers shop-with-purpose-brands-mona-b shop-with-purpose-brands-neon-buddha shop-with-purpose-brands-rachel-marie-designs shop-with-purpose-brands-second-nature-by-hand shop-with-purpose-brands-vocal-apparel shop-with-purpose-clothing shop-with-purpose-clothing-bottoms shop-with-purpose-clothing-dresses shop-with-purpose-clothing-tops shop-with-purpose-home shop-with-purpose-home-journaling shop-with-purpose-home-mugs-tumblers shop-with-purpose-home-puzzles shop-with-purpose-pet shop-with-purpose-unique-gifts shop-with-purpose-unique-gifts-baby shop-with-purpose-unique-gifts-home shop-with-purpose-unique-gifts-pet shop-with-purpose-usa-made spa sympli sympli-best-sellers sympli-bottoms sympli-dresses sympli-layering sympli-sale sympli-tops trust-your-journey""".split())

def fetch_json(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def analyze_body(body_html):
    if not body_html or not body_html.strip():
        return {"has_text": False, "has_image": False, "text_preview": ""}

    has_image = bool(re.search(r'<img\s', body_html, re.IGNORECASE))
    text = re.sub(r'<[^>]+>', ' ', body_html)
    text = re.sub(r'\s+', ' ', text).strip()
    has_text = len(text) > 10

    return {
        "has_text": has_text,
        "has_image": has_image,
        "text_preview": text[:150] if has_text else "",
    }

print("Fetching all collections...")

all_collections = []

# Custom collections (paginated)
since_id = 0
while True:
    url = f"https://{STORE}/admin/api/{API_VERSION}/custom_collections.json?limit=250"
    if since_id:
        url += f"&since_id={since_id}"
    data = fetch_json(url)
    batch = data.get("custom_collections", [])
    if not batch:
        break
    all_collections.extend(batch)
    since_id = batch[-1]["id"]
    print(f"  Fetched {len(all_collections)} custom collections...")

# Smart collections
data = fetch_json(f"https://{STORE}/admin/api/{API_VERSION}/smart_collections.json?limit=250")
smart = data.get("smart_collections", [])
all_collections.extend(smart)
print(f"  + {len(smart)} smart collections = {len(all_collections)} total")

# Filter to navigable only and analyze
results = []
for c in all_collections:
    if c["handle"] not in NAV_COLLECTIONS:
        continue

    body = c.get("body_html") or ""
    analysis = analyze_body(body)

    results.append({
        "id": c["id"],
        "handle": c["handle"],
        "title": c["title"],
        "has_text": analysis["has_text"],
        "has_image": analysis["has_image"],
        "text_preview": analysis["text_preview"],
        "body_html_len": len(body),
    })

# Deduplicate by handle (keep first)
seen = set()
deduped = []
for r in results:
    if r["handle"] not in seen:
        seen.add(r["handle"])
        deduped.append(r)

results = sorted(deduped, key=lambda x: x["handle"])

out_path = r"a:\TKBS Marketing - Git\Shopify-Website-Builder\collection-analysis.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

with_text = sum(1 for r in results if r["has_text"])
with_image = sum(1 for r in results if r["has_image"])
image_only = sum(1 for r in results if r["has_image"] and not r["has_text"])

print(f"\nNavigable collections analyzed: {len(results)}")
print(f"  With text description: {with_text}")
print(f"  With image: {with_image}")
print(f"  Image ONLY (no text): {image_only}")
print(f"  No description at all: {sum(1 for r in results if not r['has_text'] and not r['has_image'])}")
print(f"\nSaved to: {out_path}")
