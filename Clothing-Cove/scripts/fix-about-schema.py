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

print("Extending LocalBusiness schema to About page (duplicate theme only)...")

content = get_asset("snippets/microdata-schema.liquid")

old_condition = "{%- if request.page_type == 'index' -%}"
new_condition = "{%- if request.page_type == 'index' or page.handle == 'about-us' -%}"

last_idx = content.rfind(old_condition)
if last_idx >= 0:
    content = content[:last_idx] + content[last_idx:].replace(old_condition, new_condition, 1)
    put_asset("snippets/microdata-schema.liquid", content)
    print("  LocalBusiness schema now appears on homepage AND About page")
else:
    print("  WARNING: Could not find condition to update")

print("\nDone!")
