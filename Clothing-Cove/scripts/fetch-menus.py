import json
import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()
url = f"https://{os.getenv('SHOPIFY_STORE_DOMAIN')}/admin/api/2024-10/graphql.json"
q = """{ menus(first: 25) { edges { node { handle title items {
  title type url items { title type url items { title type url } } } } } } }"""
req = urllib.request.Request(
    url, data=json.dumps({"query": q}).encode(), method="POST",
    headers={"X-Shopify-Access-Token": os.getenv("SHOPIFY_ACCESS_TOKEN"),
             "Content-Type": "application/json"})
import time
for attempt in range(8):
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read())
        break
    except Exception as e:
        print("retry", attempt, e)
        time.sleep(3)
if out.get("errors"):
    print("ERR", json.dumps(out["errors"])[:500])
else:
    with open("data/menus.json", "w", encoding="utf-8") as f:
        json.dump(out["data"], f, indent=1)
    print("menus saved:", [e["node"]["handle"] for e in out["data"]["menus"]["edges"]])
