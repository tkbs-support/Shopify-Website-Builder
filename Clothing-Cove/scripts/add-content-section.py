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

new_section_id = "tkbs-seo-product-attributes"

data["sections"][new_section_id] = {
    "type": "text-with-image",
    "settings": {
        "subheading": "Your Destination for Women's Fashion",
        "title": "Women's Clothing & Accessories in Milford, MI",
        "image_position": "right",
        "content": "<p>The Clothing Cove carries over 2,000 designer dresses — from casual day dresses to mother-of-the-bride gowns and evening wear in sizes petite through plus. Our curated selection includes perfect-fit pants by Renuar and Sympli, premium denim from Liverpool and Judy Blue, and layering pieces in fabrics like bamboo, cotton, and wrinkle-free blends.</p><p>Complete your look with Brighton jewelry, handcrafted Rachel Marie Designs pieces, and accessories ranging from leather handbags to scarves and sunglasses. Locally owned since 1987, we're proud to feature US-made and fair trade brands alongside our designer collections.</p>",
        "link_text": "Shop All Collections",
        "link_url": "/collections"
    }
}

order = data["order"]
collection_list_idx = order.index("collection-list")
order.insert(collection_list_idx + 1, new_section_id)

print(f"\nInserted '{new_section_id}' after 'collection-list'")
print(f"New section order: {order}")

print("\nPushing templates/index.json...")
put_asset("templates/index.json", json.dumps(data, indent=2))
print("\nDone!")
