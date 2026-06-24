"""Type-aware Color/Size gap analysis for The Clothing Cove.

Distinguishes "missing an option" from "missing an option that this product type
should have." A vase missing Color or a soup mix missing Size is NOT a problem;
a dress missing Size IS. Expectation is curated per decoded product-type category,
with an empirical fallback (>=50% of in-stock items in the type already carry the
option) for unmapped long-tail types.
"""
import json
import collections

# code -> (human label, category, expects_color, expects_size)
# Curated from decoded productType codes + sample titles. Debatable calls marked REVIEW.
TYPE_MAP = {
    "J E W": ("Jewelry", "Jewelry", True, False),
    "H O A": ("Home & Decor", "Home", False, False),
    "A C C": ("Accessories (general)", "Accessory", True, False),
    "B A G": ("Bags & Handbags", "Bag", True, False),
    "T O C": ("Tops", "Apparel", True, True),
    "S O M": ("Special-Occasion Dresses", "Apparel", True, True),
    "C H A": ("Charms (Brighton)", "Charm", False, False),
    "B A B": ("Baby & Gifts", "Baby", False, False),
    "J A K": ("Jackets & Cardigans", "Apparel", True, True),
    "S H O": ("Shoes", "Footwear", True, True),
    "S O C": ("Occasion Dresses", "Apparel", True, True),
    "C H H": ("Christmas / Home", "Home", False, False),
    "P A M": ("Pants", "Apparel", True, True),
    "S O X": ("Novelty / Misc", "Accessory", True, False),   # REVIEW (empirical-ish)
    "D R C": ("Dresses", "Apparel", True, True),
    "A C S": ("Scarves & Wraps", "Scarf", True, False),
    "A C H": ("Hair Accessories", "HairAcc", True, False),
    "R D R": ("Reading Glasses", "Readers", True, True),      # size = magnification
    "S U N": ("Sunglasses", "Eyewear", True, False),
    "T O B": ("Blouses", "Apparel", True, True),
    "K N W": ("Knitwear", "Apparel", True, True),
    "W A L": ("Wallets & SLG", "Wallet", True, False),
    "P A J": ("Jeans", "Apparel", True, True),
    "H A T": ("Hats & Headbands", "Hat", True, False),
    "S L P": ("Sleep & Lounge", "Apparel", True, True),
    "D R E": ("Dresses", "Apparel", True, True),
    "T A N": ("Tanks", "Apparel", True, True),
    "F O D": ("Food & Pantry", "Food", False, False),
    "T O P": ("Tops", "Apparel", True, True),
    "K N C": ("Knit Cardigans", "Apparel", True, True),
    "W A T": ("Watches", "Watch", False, False),             # REVIEW (color optional)
    "P A P": ("Pants (Petite)", "Apparel", True, True),
    "S K S": ("Skirts & Skorts", "Apparel", True, True),
    "M E N": ("Men's (belts)", "Belt", True, False),         # REVIEW (size?)
    "T O L": ("Tops", "Apparel", True, True),
    "P A C": ("Capris", "Apparel", True, True),
    "P R M": ("RMD / Premium Charms", "Charm", False, False),  # REVIEW
    "L E G": ("Leggings", "Apparel", True, True),
    "A C B": ("Belts", "Belt", True, True),                  # REVIEW (size 36%)
    "V E S": ("Vests", "Apparel", True, True),
    "P E T": ("Pet", "Pet", False, False),
    "B R A": ("Bras & Intimates", "Apparel", True, True),
}

EMPIRICAL_THRESHOLD = 0.50  # unmapped type expects an option if >=50% in-stock have it


def has_opt(p, key):
    for o in p.get("options", []):
        n = o["name"].strip().lower()
        if key == "color" and ("color" in n or "colour" in n):
            return True
        if key == "size" and "size" in n:
            return True
    return False


# gather in-stock products by type
by_type = collections.defaultdict(list)
for line in open("data/products.jsonl", encoding="utf-8"):
    d = json.loads(line)
    if (d.get("totalInventory") or 0) <= 0:
        continue
    pt = (d.get("productType") or "(none)").strip() or "(none)"
    by_type[pt].append(d)

total_instock = sum(len(v) for v in by_type.values())

# empirical coverage per type
def coverage(prods, key):
    return sum(has_opt(p, key) for p in prods) / max(len(prods), 1)

old_missing_color = old_missing_size = 0
new_color_problems = new_size_problems = 0
rows = []
review_flags = {"S O X", "W A T", "M E N", "P R M", "A C B"}

for pt, prods in sorted(by_type.items(), key=lambda x: -len(x[1])):
    n = len(prods)
    cc, sc = coverage(prods, "color"), coverage(prods, "size")
    if pt in TYPE_MAP:
        label, cat, exp_c, exp_s = TYPE_MAP[pt]
    else:
        label, cat = pt, "(unmapped)"
        exp_c, exp_s = cc >= EMPIRICAL_THRESHOLD, sc >= EMPIRICAL_THRESHOLD
    miss_c = sum(not has_opt(p, "color") for p in prods)
    miss_s = sum(not has_opt(p, "size") for p in prods)
    old_missing_color += miss_c
    old_missing_size += miss_s
    prob_c = miss_c if exp_c else 0
    prob_s = miss_s if exp_s else 0
    new_color_problems += prob_c
    new_size_problems += prob_s
    if n >= 10:
        rows.append((n, label, pt, int(cc*100), int(sc*100), exp_c, exp_s,
                     prob_c, prob_s, pt in review_flags))

print(f"In-stock products analyzed: {total_instock:,}\n")
print("=== HEADLINE IMPACT ===")
print(f"  Missing COLOR  — old (all types): {old_missing_color:,}   "
      f"-> real problems (type-aware): {new_color_problems:,}   "
      f"(removed {old_missing_color-new_color_problems:,} false positives)")
print(f"  Missing SIZE   — old (all types): {old_missing_size:,}   "
      f"-> real problems (type-aware): {new_size_problems:,}   "
      f"(removed {old_missing_size-new_size_problems:,} false positives)")
print()
print("=== PER-TYPE (in-stock >=10) ===")
print(f"  {'n':>5} | {'col%':>4} {'siz%':>4} | {'expC':>4} {'expS':>4} | "
      f"{'C-prob':>6} {'S-prob':>6} | type")
for n, label, pt, cc, sc, ec, es, pc, ps, rev in rows:
    mark = " *REVIEW" if rev else ""
    print(f"  {n:5d} | {cc:3d}% {sc:3d}% | {str(ec):>4} {str(es):>4} | "
          f"{pc:6d} {ps:6d} | {label}{mark}")
