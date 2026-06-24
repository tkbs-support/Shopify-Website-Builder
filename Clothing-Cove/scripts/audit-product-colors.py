import json
import urllib.request
import os
import time
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"

COLOR_NAMES = {"color", "colour", "couleur", "colore", "farbe"}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def audit_all_products():
    base = f"https://{STORE}/admin/api/{API_VERSION}/products.json"
    since_id = 0
    page = 0

    stats = {
        "total_active": 0,
        "in_stock": 0,
        "out_of_stock": 0,
        "with_color_option": 0,
        "without_color_option": 0,
        "in_stock_with_color": 0,
        "in_stock_without_color": 0,
        "default_title_only": 0,
        "color_option_name_variants": {},
        "product_types": {},
        "color_values": {},
        "products_with_color": [],
        "product_type_color_breakdown": {},
    }

    while True:
        url = f"{base}?limit=250&status=active&since_id={since_id}&fields=id,title,options,variants,product_type"
        data = fetch_json(url)
        products = data.get("products", [])
        if not products:
            break

        for p in products:
            stats["total_active"] += 1
            pt = p.get("product_type", "") or "(empty)"

            has_in_stock = any(
                v.get("inventory_management") is None or (v.get("inventory_quantity", 0) > 0)
                for v in p["variants"]
            )

            color_opt = None
            for o in p["options"]:
                if o["name"].lower() in COLOR_NAMES:
                    color_opt = o
                    break

            is_default = len(p["options"]) == 1 and p["options"][0]["name"] == "Title"
            if is_default:
                stats["default_title_only"] += 1

            if has_in_stock:
                stats["in_stock"] += 1
            else:
                stats["out_of_stock"] += 1

            stats["product_types"][pt] = stats["product_types"].get(pt, 0) + 1

            if pt not in stats["product_type_color_breakdown"]:
                stats["product_type_color_breakdown"][pt] = {
                    "total": 0, "with_color": 0, "in_stock": 0, "in_stock_with_color": 0
                }
            stats["product_type_color_breakdown"][pt]["total"] += 1
            if has_in_stock:
                stats["product_type_color_breakdown"][pt]["in_stock"] += 1

            if color_opt:
                stats["with_color_option"] += 1
                name = color_opt["name"]
                stats["color_option_name_variants"][name] = stats["color_option_name_variants"].get(name, 0) + 1
                stats["product_type_color_breakdown"][pt]["with_color"] += 1

                if has_in_stock:
                    stats["in_stock_with_color"] += 1
                    stats["product_type_color_breakdown"][pt]["in_stock_with_color"] += 1

                colors = set()
                for v in p["variants"]:
                    val = v.get("option1", "")
                    if color_opt == p["options"][0] and val:
                        colors.add(val)
                    elif len(p["options"]) > 1 and color_opt == p["options"][1]:
                        val = v.get("option2", "")
                        if val:
                            colors.add(val)
                    elif len(p["options"]) > 2 and color_opt == p["options"][2]:
                        val = v.get("option3", "")
                        if val:
                            colors.add(val)

                for c in colors:
                    stats["color_values"][c] = stats["color_values"].get(c, 0) + 1

                stats["products_with_color"].append({
                    "id": p["id"],
                    "title": p["title"],
                    "product_type": pt,
                    "color_option_name": name,
                    "color_values": sorted(colors),
                    "in_stock": has_in_stock,
                })
            else:
                stats["without_color_option"] += 1
                if has_in_stock:
                    stats["in_stock_without_color"] += 1

        since_id = products[-1]["id"]
        page += 1
        if page % 10 == 0:
            print(f"  Page {page} — {stats['total_active']} products scanned...")
        time.sleep(0.5)

    return stats


def print_summary(stats):
    print("\n" + "=" * 60)
    print("PRODUCT COLOR AUDIT — THE CLOTHING COVE")
    print("=" * 60)

    print(f"\nTotal active products:        {stats['total_active']:,}")
    print(f"  In stock:                   {stats['in_stock']:,}")
    print(f"  Out of stock:               {stats['out_of_stock']:,}")
    print(f"  Default Title (no options): {stats['default_title_only']:,}")

    print(f"\n--- Color Option Status ---")
    print(f"Products WITH Color option:   {stats['with_color_option']:,}")
    print(f"Products WITHOUT Color option:{stats['without_color_option']:,}")
    pct = (stats['with_color_option'] / stats['total_active'] * 100) if stats['total_active'] else 0
    print(f"Color coverage:               {pct:.1f}%")

    print(f"\n--- In-Stock Breakdown ---")
    print(f"In stock WITH color:          {stats['in_stock_with_color']:,}")
    print(f"In stock WITHOUT color:       {stats['in_stock_without_color']:,}")
    pct_stock = (stats['in_stock_with_color'] / stats['in_stock'] * 100) if stats['in_stock'] else 0
    print(f"In-stock color coverage:      {pct_stock:.1f}%")

    print(f"\n--- Color Option Name Variants ---")
    for name, count in sorted(stats["color_option_name_variants"].items(), key=lambda x: -x[1]):
        print(f"  '{name}': {count:,} products")

    print(f"\n--- Unique Color Values ({len(stats['color_values'])} total) ---")
    for color, count in sorted(stats["color_values"].items(), key=lambda x: -x[1])[:50]:
        print(f"  {color}: {count} products")
    if len(stats["color_values"]) > 50:
        print(f"  ... and {len(stats['color_values']) - 50} more")

    print(f"\n--- Product Types (by color coverage) ---")
    print(f"  {'Type':<12} {'Total':>7} {'In Stock':>9} {'Has Color':>10} {'In Stock+Color':>15}")
    print(f"  {'-'*12} {'-'*7} {'-'*9} {'-'*10} {'-'*15}")
    for pt, info in sorted(stats["product_type_color_breakdown"].items(), key=lambda x: -x[1]["total"]):
        print(f"  {pt:<12} {info['total']:>7,} {info['in_stock']:>9,} {info['with_color']:>10,} {info['in_stock_with_color']:>15,}")


if __name__ == "__main__":
    print("=== Product Color Audit (READ-ONLY) ===")
    print(f"Store: {STORE}\n")
    print("Scanning all active products...")

    stats = audit_all_products()

    print_summary(stats)

    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "color-audit-results.json")
    serializable = {k: v for k, v in stats.items()}
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)

    print(f"\nFull data saved to: {output_file}")
    print("Done!")
