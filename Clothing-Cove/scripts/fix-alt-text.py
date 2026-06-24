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

def fix_slideshow():
    print("Fixing sections/slideshow.liquid...")
    content = get_asset("sections/slideshow.liquid")

    # Desktop images
    old_desktop = 'alt="{{ block.settings.image.alt | escape }}">'
    new_desktop = 'alt="{{ block.settings.image.alt | default: block.settings.title | default: block.settings.button_1_text | default: \'The Clothing Cove promotional banner\' | escape }}">'

    # Mobile images
    old_mobile = 'alt="{{ mobile_image.alt | escape }}">'
    new_mobile = 'alt="{{ mobile_image.alt | default: block.settings.title | default: block.settings.button_1_text | default: \'The Clothing Cove promotional banner\' | escape }}">'

    count = 0
    if old_desktop in content:
        content = content.replace(old_desktop, new_desktop)
        count += content.count(new_desktop)
        print(f"  Desktop img alt: added fallback chain")
    if old_mobile in content:
        content = content.replace(old_mobile, new_mobile)
        print(f"  Mobile img alt: added fallback chain")

    put_asset("sections/slideshow.liquid", content)

def fix_shop_the_look():
    print("Fixing sections/shop-the-look.liquid...")
    content = get_asset("sections/shop-the-look.liquid")

    old_alt = 'alt="{{ block.settings.image.alt | escape }}">'
    new_alt = 'alt="{{ block.settings.image.alt | default: section.settings.title | default: \'Shop the look at The Clothing Cove\' | escape }}">'

    if old_alt in content:
        content = content.replace(old_alt, new_alt)
        print(f"  img alt: added fallback chain")

    put_asset("sections/shop-the-look.liquid", content)

if __name__ == "__main__":
    print("=== Alt Text Fixes ===\n")
    fix_slideshow()
    print()
    fix_shop_the_look()
    print("\nDone!")
