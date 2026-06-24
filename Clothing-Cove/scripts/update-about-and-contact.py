import json
import urllib.request
import os
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"

def api_put(url, data):
    req = urllib.request.Request(url, method="PUT", headers={
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json",
    })
    req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


# === 1. About Us - Add Visit Us & Hours section ===
print("=== Updating About Us ===")

about_body = """<h2>Our Story</h2>
<p>It all began in 1987 when my husband, Eric, and I opened an exercise business, California Toning of Milford, where we also sold fashionable workout gear. By 1990, we had expanded our offerings and knew that we loved the business of selling great sportswear, special occasion clothing, jewelry and accessories to the women of Milford, Michigan and the surrounding area. We dropped the exercise portion, and, with a change of the name and business model, The Clothing Cove was born.</p>

<p>We have been living the dream, working side by side, ever since. In 2025, we celebrate over 38 years in the ladies clothing retail business with many of those who have supported us throughout the decades. We love what we do, God who guides us, and all those who work alongside us! The entire staff of The Clothing Cove, from the office, support staff, and web personnel, to the sales professionals on the sales floor, feel privileged to serve our community. They help to create a fun and welcoming environment in which women can shop with exceptional customer service. We strive to honor Christ, and serve our local community with honesty and integrity.</p>

<h2>Tenacity Boutique - Shopping With Purpose</h2>
<p>Blessed beyond measure by the God that we serve, we felt led to help a cause that touched our hearts. We wanted to build awareness of the plight of women caught in the throes of sex trafficking and do our part to help put an end to this local epidemic. In August of 2017, we opened Tenacity Boutique, right next to The Clothing Cove. The more "casual sister" of the Cove, Tenacity means "with a firm grip or purpose." A portion of our Tenacity proceeds helps support Hope Against Trafficking in Pontiac, Michigan. This non-profit helps survivors rescued from trafficking in Michigan.</p>

<h2>US-Made, Fair Trade &amp; Ethically Sourced Fashion</h2>
<p>We strive to purchase US and North American made products with a special emphasis on merchandise that is domestically or locally made. Fair Trade, eco-friendly and ethically made items are also searched out. You can feel good about your purchase because many of our lines are philanthropic in some way - many themselves also support those caught in sex trafficking and drug addiction.</p>

<p>Our hope is that you enjoy the vast array of carefully selected fashion and curated items found in both stores and visit us often to help us do good in our neighborhood and beyond.</p>

<h2>Visit Us</h2>
<p><strong>The Clothing Cove</strong><br>414 North Main Street<br>Milford, MI 48381<br>248-685-2500<br><a href="mailto:service@theclothingcove.com">service@theclothingcove.com</a></p>

<p><strong>Store Hours</strong><br>Monday - Friday: 10:00 AM - 6:00 PM<br>Saturday: 9:30 AM - 6:00 PM<br>Sunday: Closed</p>"""

result = api_put(
    f"https://{STORE}/admin/api/{API_VERSION}/pages/14777352307.json",
    {"page": {"id": 14777352307, "body_html": about_body}}
)
print(f"  Updated: {result['page']['title']}")


# === 2. Contact Us - Restructure with headings + SEO ===
print("\n=== Updating Contact Us ===")

contact_body = """<h2>Get In Touch</h2>
<p>We'd love to hear from you! Whether you have a question about a product, need help with sizing, or want to check availability, our team is here to help.</p>

<p><strong>Email:</strong> <a href="mailto:service@theclothingcove.com">service@theclothingcove.com</a><br><strong>Phone:</strong> <a href="tel:+12486852500">248-685-2500</a></p>

<h2>Store Hours</h2>
<p>Monday - Friday: 10:00 AM - 6:00 PM<br>Saturday: 9:30 AM - 6:00 PM<br>Sunday: Closed</p>

<h2>Our Location</h2>
<p><strong>The Clothing Cove</strong><br>414 North Main Street<br>Milford, MI 48381</p>

<p>We're located in the heart of downtown Milford on Main Street. Come on in - we are here to serve you for all your special occasions, sportswear, accessories, and everyday fashion needs.</p>

<p>WE LOOK FORWARD TO SEEING YOU!</p>"""

result = api_put(
    f"https://{STORE}/admin/api/{API_VERSION}/pages/13783629939.json",
    {"page": {
        "id": 13783629939,
        "body_html": contact_body,
        "metafields_global_title_tag": "Contact Us & Store Hours | The Clothing Cove - Milford, MI",
        "metafields_global_description_tag": "Visit The Clothing Cove at 414 N Main St, Milford, MI. Open Mon-Fri 10-6, Sat 9:30-6. Call 248-685-2500 or email service@theclothingcove.com.",
    }}
)
print(f"  Updated: {result['page']['title']}")
print(f"  SEO title: Contact Us & Store Hours | The Clothing Cove - Milford, MI")
print(f"  Meta desc: 140 chars")

print("\nDone! Both pages updated live.")
