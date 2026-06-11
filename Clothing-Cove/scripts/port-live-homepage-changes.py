"""Port the client's live-theme homepage changes into the TKBS theme.

Applies the 4 client changes identified by threeway-index-diff.py to
templates/index.json on the TKBS theme (145504469107), then re-fetches and
verifies that the only remaining differences vs live are Josh's SEO edits.
"""
import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"
TKBS_ID = "145504469107"
BASE_URL = f"https://{STORE}/admin/api/{API_VERSION}/themes/{TKBS_ID}/assets.json"

KEY = "templates/index.json"
MAP_SECTION = "76c53ab3-0098-4632-b1f9-cf9edc63ec77"


def put_asset(key, value):
    data = json.dumps({"asset": {"key": key, "value": value}}).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="PUT", headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_asset(key):
    url = f"{BASE_URL}?asset%5Bkey%5D={key.replace('/', '%2F')}"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["asset"]["value"]


live = json.load(open("data/themes/live/files/templates/index.json", encoding="utf-8"))
tkbs = json.load(open("data/themes/tkbs/files/templates/index.json", encoding="utf-8"))
s = tkbs["sections"]
ls = live["sections"]

# 1. Slideshow slide 1: new banner images
slide = s["slideshow"]["blocks"]["dadcc779-7579-43d6-a268-44c0452b20bf"]["settings"]
slide["image"] = "shopify://shop_images/Website_Banners_DESKTOP_25.jpg"
slide["mobile_image"] = "shopify://shop_images/Mobile_banners_14.jpg"

# 2. Client disabled the "Women's Clothing Sale" slide
s["slideshow"]["blocks"]["image_cKMgkd"]["disabled"] = True

# 3. Updated store hours (take live value verbatim)
s[MAP_SECTION]["settings"]["hours"] = ls[MAP_SECTION]["settings"]["hours"]

# 4. New Arrivals tile retargeted to clothing collection
#    (client titled it "New apparel"; Josh approved the SEO-stronger variant)
nd = s["collection-list"]["blocks"]["collection_NdFW6Q"]["settings"]
nd["button_link"] = "shopify://collections/clothing"
nd["collection"] = "clothing"
nd["title"] = "New Apparel & Accessories"

print("Pushing merged templates/index.json to TKBS theme...")
result = put_asset(KEY, json.dumps(tkbs, indent=2))
print(f"  Updated: {result['asset']['key']} at {result['asset']['updated_at']}")

# Save merged copy locally and verify
with open("data/themes/tkbs/files/templates/index.json", "w", encoding="utf-8", newline="") as f:
    f.write(json.dumps(tkbs, indent=2))

print("\nRe-fetching from TKBS theme to verify...")
remote = json.loads(get_asset(KEY))


def leaves(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(leaves(v, f"{prefix}.{k}" if prefix else k))
    else:
        out[prefix] = obj
    return out


r, l = leaves(remote), leaves(live)
MISSING = object()
diffs = [p for p in sorted(set(r) | set(l)) if r.get(p, MISSING) != l.get(p, MISSING)]
print(f"\nRemaining differences vs live ({len(diffs)}) — should ALL be Josh's SEO edits:")
for p in diffs:
    print(f"  {p}")
