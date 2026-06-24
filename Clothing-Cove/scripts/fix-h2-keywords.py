import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
THEME_ID = "145504469107"
API_VERSION = "2024-10"
BASE_URL = f"https://{STORE}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"

def get_asset(key):
    url = f"{BASE_URL}?asset%5Bkey%5D={key.replace('/', '%2F')}"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["asset"]["value"]

def put_asset(key, value):
    data = json.dumps({"asset": {"key": key, "value": value}}).encode()
    req = urllib.request.Request(BASE_URL, data=data, method="PUT", headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"  Updated: {result['asset']['key']}")

print("Fetching templates/index.json...")
content = get_asset("templates/index.json")
data = json.loads(content)

sections = data["sections"]

# Fix slideshow titles ("SHOP NOW" -> more descriptive)
slideshow_blocks = sections["slideshow"]["blocks"]
changes = []

for block_id, block in slideshow_blocks.items():
    s = block["settings"]
    old_title = s.get("title", "")
    link = s.get("button_1_link", "")

    if old_title == "SHOP NOW" and "customer-apprecation" in link:
        s["title"] = "Customer Appreciation Sale"
        changes.append(f"  Slideshow ({block_id[:8]}): 'SHOP NOW' -> 'Customer Appreciation Sale'")
    elif old_title == "SHOP NOW" and "sale" in link:
        s["title"] = "Women's Clothing Sale"
        changes.append(f"  Slideshow ({block_id[:8]}): 'SHOP NOW' -> 'Women's Clothing Sale'")

# Fix collection list titles
collection_blocks = sections["collection-list"]["blocks"]

for block_id, block in collection_blocks.items():
    s = block["settings"]
    old_title = s.get("title", "")

    if old_title == "For Special Occasions":
        s["title"] = "Dresses for Special Occasions"
        changes.append(f"  Collection ({block_id[:8]}): 'For Special Occasions' -> 'Dresses for Special Occasions'")
    elif old_title == "" and s.get("subheading") == "Brighton Accessories":
        s["title"] = "Brighton Jewelry & Accessories"
        changes.append(f"  Collection ({block_id[:8]}): '' -> 'Brighton Jewelry & Accessories'")
    elif old_title == "freshen up your home":
        s["title"] = "Home Décor & Gifts"
        changes.append(f"  Collection ({block_id[:8]}): 'freshen up your home' -> 'Home Décor & Gifts'")

# Fix shop-the-look title
stl = sections["shop-the-look"]["settings"]
old_stl = stl.get("title", "")
if old_stl == "Shop The Look":
    stl["title"] = "Shop The Look — Jewelry & Accessories"
    changes.append(f"  Shop the Look: 'Shop The Look' -> 'Shop The Look — Jewelry & Accessories'")

if changes:
    print(f"\nChanges ({len(changes)}):")
    for c in changes:
        print(c)
    print("\nPushing templates/index.json...")
    put_asset("templates/index.json", json.dumps(data, indent=2))
else:
    print("No matching H2s found to update.")

print("\nDone!")
