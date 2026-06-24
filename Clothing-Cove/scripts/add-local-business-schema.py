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

LOCAL_BUSINESS_BLOCK = """
{%- if request.page_type == 'index' -%}
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "ClothingStore",
    "name": "The Clothing Cove",
    "description": "Women's clothing store in Milford, MI featuring 2000+ designer dresses, Brighton jewelry, and curated fashion accessories. Locally owned since 1987.",
    "url": "https://theclothingcove.com",
    "telephone": "+1-248-685-2500",
    "email": "service@theclothingcove.com",
    "image": "https://theclothingcove.com/cdn/shop/files/Untitled_design_-_2025-11-07T121430.139_96x.png",
    "logo": "https://theclothingcove.com/cdn/shop/files/Untitled_design_-_2025-11-07T121430.139_96x.png",
    "foundingDate": "1987",
    "founder": {
      "@type": "Person",
      "name": "Eric Horsley"
    },
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "414 North Main Street",
      "addressLocality": "Milford",
      "addressRegion": "MI",
      "postalCode": "48381",
      "addressCountry": "US"
    },
    "geo": {
      "@type": "GeoCoordinates",
      "latitude": 42.5910504,
      "longitude": -83.5998731
    },
    "openingHoursSpecification": [
      {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "opens": "10:00",
        "closes": "18:00"
      },
      {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": "Saturday",
        "opens": "09:30",
        "closes": "18:00"
      }
    ],
    "priceRange": "$$",
    "paymentAccepted": "Cash, Credit Card",
    "currenciesAccepted": "USD, CAD",
    "hasMap": "https://maps.google.com/?q=414+North+Main+Street+Milford+MI+48381",
    "sameAs": []
  }
  </script>
{%- endif -%}"""

print("Fetching snippets/microdata-schema.liquid...")
content = get_asset("snippets/microdata-schema.liquid")

content = content.rstrip() + "\n" + LOCAL_BUSINESS_BLOCK + "\n"

print("Pushing snippets/microdata-schema.liquid...")
put_asset("snippets/microdata-schema.liquid", content)
print("\nDone! LocalBusiness schema added to homepage.")
