"""Direct verification: TKBS theme record timestamp + ported values in templates/index.json."""
import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()
STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API = "2024-10"
TKBS_ID = "145504469107"


def get(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


theme = get(f"https://{STORE}/admin/api/{API}/themes/{TKBS_ID}.json")["theme"]
print(f"Theme: {theme['name']}")
print(f"  theme.updated_at: {theme['updated_at']}")

asset = get(f"https://{STORE}/admin/api/{API}/themes/{TKBS_ID}/assets.json"
            f"?asset%5Bkey%5D=templates%2Findex.json")["asset"]
print(f"\ntemplates/index.json on TKBS theme:")
print(f"  asset.updated_at: {asset['updated_at']}")

data = json.loads(asset["value"])
s = data["sections"]
slide1 = s["slideshow"]["blocks"]["dadcc779-7579-43d6-a268-44c0452b20bf"]["settings"]
print(f"\nPorted values as stored on Shopify right now:")
print(f"  1. Slide 1 image:        {slide1['image']}")
print(f"     Slide 1 mobile image: {slide1['mobile_image']}")
print(f"  2. Sale slide disabled:  {s['slideshow']['blocks']['image_cKMgkd'].get('disabled')}")
hours = s["76c53ab3-0098-4632-b1f9-cf9edc63ec77"]["settings"]["hours"]
print(f"  3. Hours mentions Thursday 10am-8pm: {'Thursday 10am - 8pm' in hours}")
nd = s["collection-list"]["blocks"]["collection_NdFW6Q"]["settings"]
print(f"  4. Tile: collection={nd['collection']!r}, title={nd['title']!r}")
