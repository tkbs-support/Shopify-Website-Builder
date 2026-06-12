"""Push corrected microdata-schema.liquid (Thu 10-20 hours + full sameAs) to the TKBS theme."""
import json
import os
import sys
import urllib.request
from dotenv import load_dotenv

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
BASE = f"https://{STORE}/admin/api/2024-10/themes/145504469107/assets.json"
KEY = "snippets/microdata-schema.liquid"

content = open("data/themes/tkbs/files/snippets/microdata-schema.liquid", encoding="utf-8").read()
data = json.dumps({"asset": {"key": KEY, "value": content}}).encode()
req = urllib.request.Request(BASE, data=data, method="PUT", headers={
    "X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    r = json.loads(resp.read())["asset"]
print(f"Updated {r['key']} at {r['updated_at']}")

url = f"{BASE}?asset%5Bkey%5D={KEY.replace('/', '%2F')}"
req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
with urllib.request.urlopen(req) as resp:
    remote = json.loads(resp.read())["asset"]["value"]

checks = [
    ('Thursday 10-20 block', '"dayOfWeek": "Thursday",\n        "opens": "10:00",\n        "closes": "20:00"'),
    ('Mon/Tue/Wed/Fri 10-18', '["Monday", "Tuesday", "Wednesday", "Friday"]'),
    ("Twitter sameAs", "https://twitter.com/TheClothingCove"),
    ("Pinterest sameAs", "https://www.pinterest.com/covegirle/"),
    ("YouTube sameAs", "https://www.youtube.com/c/TheClothingCoveBoutique"),
]
for label, marker in checks:
    print(f"  {label}: {marker in remote}")
print(f"  round-trip identical: {remote == content}")
