import json
import urllib.request
import os
import time
from dotenv import load_dotenv

load_dotenv()

STORE = os.getenv("SHOPIFY_STORE_DOMAIN")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-10"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token": TOKEN})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < 4:
                wait = 3 + attempt * 2
                print(f"  Retry {attempt+1} ({e}) - waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def run():
    base = f"https://{STORE}/admin/api/{API_VERSION}/products.json"
    since_id = 0
    page = 0

    opt_names = {}
    opt_casings = {}
    opt_values = {}
    opt_stock = {}
    opt_by_type = {}
    default_title = 0
    opt_counts = {}
    total = 0

    while True:
        url = f"{base}?limit=250&status=active&since_id={since_id}&fields=id,options,variants,product_type"
        data = fetch_json(url)
        products = data.get("products", [])
        if not products:
            break

        for p in products:
            total += 1
            pt = p.get("product_type", "") or "(empty)"

            has_stock = any(
                v.get("inventory_management") is None or v.get("inventory_quantity", 0) > 0
                for v in p["variants"]
            )

            is_default = (
                len(p["options"]) == 1
                and p["options"][0]["name"] == "Title"
                and len(p["variants"]) == 1
                and p["variants"][0].get("title") == "Default Title"
            )

            if is_default:
                default_title += 1
                continue

            n_opts = len(p["options"])
            opt_counts[n_opts] = opt_counts.get(n_opts, 0) + 1

            for opt in p["options"]:
                if opt["name"] == "Title":
                    continue
                key = opt["name"].lower()

                opt_names[key] = opt_names.get(key, 0) + 1
                opt_casings.setdefault(key, {})
                opt_casings[key][opt["name"]] = opt_casings[key].get(opt["name"], 0) + 1
                opt_stock.setdefault(key, {"total": 0, "in_stock": 0})
                opt_stock[key]["total"] += 1
                if has_stock:
                    opt_stock[key]["in_stock"] += 1
                opt_values.setdefault(key, {})
                opt_by_type.setdefault(key, {})
                opt_by_type[key][pt] = opt_by_type[key].get(pt, 0) + 1

                # Collect unique values from variants
                opt_idx = next(
                    (i for i, o in enumerate(p["options"]) if o["name"] == opt["name"]),
                    None,
                )
                if opt_idx is not None:
                    field = f"option{opt_idx + 1}"
                    seen = set()
                    for v in p["variants"]:
                        val = v.get(field, "")
                        if val and val not in seen:
                            seen.add(val)
                            opt_values[key][val] = opt_values[key].get(val, 0) + 1

        since_id = products[-1]["id"]
        page += 1
        if page % 10 == 0:
            print(f"  Page {page} — {total} products...")
        time.sleep(0.5)

    # Save data
    output = {
        "total_scanned": total,
        "default_title": default_title,
        "option_name_counts": opt_names,
        "option_name_casings": opt_casings,
        "option_values": opt_values,
        "option_stock": opt_stock,
        "option_by_product_type": opt_by_type,
        "products_by_option_count": opt_counts,
    }
    out_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "option-audit-results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Print report
    print()
    print("=" * 70)
    print(f"COMPREHENSIVE PRODUCT OPTION AUDIT ({total:,} products)")
    print("=" * 70)
    print(f"Default Title (no options): {default_title:,}")
    print(f"With real options: {total - default_title:,}")

    print("\nBy option count:")
    for c in sorted(opt_counts):
        print(f"  {c} option(s): {opt_counts[c]:,}")

    print(f"\n{'Option':<16} {'Products':>9} {'In Stock':>9} {'Unique':>8}  Casings")
    print("-" * 70)
    for name, count in sorted(opt_names.items(), key=lambda x: -x[1]):
        s = opt_stock[name]
        uv = len(opt_values[name])
        casings = ", ".join(f"{k}:{v}" for k, v in sorted(opt_casings[name].items(), key=lambda x: -x[1]))
        print(f"  {name:<14} {count:>9,} {s['in_stock']:>9,} {uv:>8,}  {casings}")

    for name, _ in sorted(opt_names.items(), key=lambda x: -x[1])[:10]:
        vals = sorted(opt_values[name].items(), key=lambda x: -x[1])
        print(f"\n--- \"{name}\" top values ({len(vals):,} unique) ---")
        for v, c in vals[:25]:
            print(f"  {v}: {c}")
        if len(vals) > 25:
            print(f"  ... +{len(vals) - 25} more")
        print("  Top product types:")
        for pt, c in sorted(opt_by_type[name].items(), key=lambda x: -x[1])[:8]:
            print(f"    {pt}: {c}")

    print(f"\nFull data saved to {out_path}")


if __name__ == "__main__":
    print("=== Comprehensive Option Audit (READ-ONLY) ===")
    print(f"Store: {STORE}\n")
    run()
