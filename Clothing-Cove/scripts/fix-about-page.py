import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"
PAGE_ID = "14777352307"
THEME_ID = "145504469107"

def api_request(url, data=None, method=None):
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
    })
    if data:
        req.data = json.dumps(data).encode()
    if method:
        req.method = method
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# 1. Update page SEO title, meta description, and body HTML
print("=== Fixing About Us Page ===\n")

new_body = """<h2>Our Story</h2>
<p>It all began in 1987 when my husband, Eric, and I opened an exercise business, California Toning of Milford, where we also sold fashionable workout gear. By 1990, we had expanded our offerings and knew that we loved the business of selling great sportswear, special occasion clothing, jewelry and accessories to the women of Milford, Michigan and the surrounding area. We dropped the exercise portion, and, with a change of the name and business model, The Clothing Cove was born.</p>

<p>We have been living the dream, working side by side, ever since. In 2025, we celebrate over 38 years in the ladies clothing retail business with many of those who have supported us throughout the decades. We love what we do, God who guides us, and all those who work alongside us! The entire staff of The Clothing Cove, from the office, support staff, and web personnel, to the sales professionals on the sales floor, feel privileged to serve our community. They help to create a fun and welcoming environment in which women can shop with exceptional customer service. We strive to honor Christ, and serve our local community with honesty and integrity.</p>

<h2>Tenacity Boutique — Shopping With Purpose</h2>
<p>Blessed beyond measure by the God that we serve, we felt led to help a cause that touched our hearts. We wanted to build awareness of the plight of women caught in the throes of sex trafficking and do our part to help put an end to this local epidemic. In August of 2017, we opened Tenacity Boutique, right next to The Clothing Cove. The more "casual sister" of the Cove, Tenacity means "with a firm grip or purpose." A portion of our Tenacity proceeds helps support Hope Against Trafficking in Pontiac, Michigan. This non-profit helps survivors rescued from trafficking in Michigan.</p>

<h2>US-Made, Fair Trade & Ethically Sourced Fashion</h2>
<p>We strive to purchase US and North American made products with a special emphasis on merchandise that is domestically or locally made. Fair Trade, eco-friendly and ethically made items are also searched out. You can feel good about your purchase because many of our lines are philanthropic in some way — many themselves also support those caught in sex trafficking and drug addiction.</p>

<p>Our hope is that you enjoy the vast array of carefully selected fashion and curated items found in both stores and visit us often to help us do good in our neighborhood and beyond.</p>"""

page_url = f"https://{STORE}/admin/api/{API_VERSION}/pages/{PAGE_ID}.json"
result = api_request(page_url, data={
    "page": {
        "id": int(PAGE_ID),
        "body_html": new_body,
        "metafields_global_title_tag": "About The Clothing Cove | Women's Clothing Store in Milford, MI Since 1987",
        "metafields_global_description_tag": "Family-owned since 1987, The Clothing Cove offers 2000+ designer dresses, Brighton jewelry & women's fashion in downtown Milford, MI. Meet our team and story.",
    }
}, method="PUT")
print(f"  Page updated: {result['page']['title']}")
print(f"  SEO title: About The Clothing Cove | Women's Clothing Store in Milford, MI Since 1987")
print(f"  Meta desc: 158 chars")
print(f"  Body: restructured with H2 headings")


# 2. Extend LocalBusiness schema to About page
print("\nExtending LocalBusiness schema to About page...")

theme_url = f"https://{STORE}/admin/api/{API_VERSION}/themes/{THEME_ID}/assets.json"

def get_asset(key):
    url = f"{theme_url}?asset%5Bkey%5D={key.replace('/', '%2F')}"
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["asset"]["value"]

def put_asset(key, value):
    data = json.dumps({"asset": {"key": key, "value": value}}).encode()
    req = urllib.request.Request(theme_url, data=data, method="PUT", headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"  Updated: {result['asset']['key']}")

content = get_asset("snippets/microdata-schema.liquid")

old_condition = "{%- if request.page_type == 'index' -%}"
new_condition = "{%- if request.page_type == 'index' or page.handle == 'about-us' -%}"

# Only replace the one inside the LocalBusiness block
if old_condition in content:
    # Find the last occurrence (which is our LocalBusiness block, added at the end)
    last_idx = content.rfind(old_condition)
    content = content[:last_idx] + content[last_idx:].replace(old_condition, new_condition, 1)
    put_asset("snippets/microdata-schema.liquid", content)
    print("  LocalBusiness schema now appears on homepage AND About page")
else:
    print("  WARNING: Could not find condition to update")

print("\nDone!")
