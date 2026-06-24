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
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": TOKEN,
    })
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
        return result

def fix_theme_liquid():
    print("Fetching layout/theme.liquid...")
    content = get_asset("layout/theme.liquid")

    old_title = """<title>
      {{ page_title }}{% if current_tags %}{% assign meta_tags = current_tags | join: ', ' %} &ndash; {{ 'general.meta.tags' | t: tags: meta_tags }}{% endif %}{% if current_page != 1 %} &ndash; {{ 'general.meta.page' | t: page: current_page }}{% endif %}{% unless page_title contains shop.name %} &ndash; {{ shop.name }}{% endunless %}
    </title>"""

    new_title = """<title>
      {%- if template.name == 'index' -%}
        The Clothing Cove | Women's Clothing, Dresses & Brighton Jewelry | Milford, MI
      {%- else -%}
        {{ page_title }}{% if current_tags %}{% assign meta_tags = current_tags | join: ', ' %} &ndash; {{ 'general.meta.tags' | t: tags: meta_tags }}{% endif %}{% if current_page != 1 %} &ndash; {{ 'general.meta.page' | t: page: current_page }}{% endif %}{% unless page_title contains shop.name %} &ndash; {{ shop.name }}{% endunless %}
      {%- endif -%}
    </title>"""

    old_meta = """    {%- if page_description -%}
      <meta name="description" content="{{ page_description | escape }}">
    {%- endif -%}"""

    new_meta = """    {%- if template.name == 'index' -%}
      <meta name="description" content="The Clothing Cove is Milford, MI's premier dress store — shop 2000+ designer dresses, women's clothing, Brighton jewelry &amp; accessories. Visit us at 414 N Main St.">
    {%- elsif page_description -%}
      <meta name="description" content="{{ page_description | escape }}">
    {%- endif -%}"""

    old_content_for_layout = "{{ content_for_layout }}"

    new_content_for_layout = """{%- if template.name == 'index' -%}
      <h1 class="visually-hidden">The Clothing Cove — Women's Clothing, Dresses & Brighton Jewelry in Milford, MI</h1>
    {%- endif -%}
    {{ content_for_layout }}"""

    if old_title not in content:
        print("  WARNING: Could not find title block to replace. Skipping title fix.")
    else:
        content = content.replace(old_title, new_title)
        print("  Title tag: updated with homepage conditional")

    if old_meta not in content:
        print("  WARNING: Could not find meta description block to replace. Skipping meta fix.")
    else:
        content = content.replace(old_meta, new_meta)
        print("  Meta description: updated with homepage conditional")

    if old_content_for_layout not in content:
        print("  WARNING: Could not find content_for_layout. Skipping H1 fix.")
    else:
        content = content.replace(old_content_for_layout, new_content_for_layout, 1)
        print("  H1: added visually-hidden homepage H1")

    print("Pushing layout/theme.liquid...")
    put_asset("layout/theme.liquid", content)

if __name__ == "__main__":
    print("=== SEO Fixes for The Clothing Cove ===\n")
    fix_theme_liquid()
    print("\nDone! Preview the theme to verify changes.")
