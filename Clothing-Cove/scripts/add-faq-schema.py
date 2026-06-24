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

# Dynamic FAQ schema that reads Q&A from the page content at render time
FAQ_SCHEMA_BLOCK = """
{%- if page.handle == 'faqs' -%}
  {%- assign faq_content = page.content -%}
  {%- assign faq_parts = faq_content | split: 'Question:' -%}
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
      {%- for part in faq_parts -%}
        {%- if part contains 'Answer:' -%}
          {%- assign qa = part | split: 'Answer:' -%}
          {%- assign question = qa[0] | strip_html | strip | remove: '?' -%}
          {%- assign answer = qa[1] | split: 'Question:' | first | strip_html | strip -%}
          {%- if question != blank and answer != blank -%}
            {
              "@type": "Question",
              "name": {{ question | append: '?' | json }},
              "acceptedAnswer": {
                "@type": "Answer",
                "text": {{ answer | json }}
              }
            }{%- unless forloop.last -%},{%- endunless -%}
          {%- endif -%}
        {%- endif -%}
      {%- endfor -%}
    ]
  }
  </script>
{%- endif -%}"""

print("Fetching snippets/microdata-schema.liquid...")
content = get_asset("snippets/microdata-schema.liquid")

content = content.rstrip() + "\n" + FAQ_SCHEMA_BLOCK + "\n"

print("Pushing snippets/microdata-schema.liquid...")
put_asset("snippets/microdata-schema.liquid", content)
print("\nDone! FAQPage schema added for /pages/faqs")
