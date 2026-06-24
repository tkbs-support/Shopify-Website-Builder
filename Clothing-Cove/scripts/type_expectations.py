"""Product-type -> Color/Size expectation map for The Clothing Cove.

Single source of truth for "does this product type even need a Color / Size
option?" A vase or a soup mix missing Size is not a problem; a dress is.

Expectation is curated per decoded productType code (the store uses cryptic
3-letter codes like 'J E W' = Jewelry). Codes not in the map fall back to an
empirical rule: the type "expects" an option if >= EMPIRICAL_THRESHOLD of its
in-stock products already carry it. Color and Size are judged independently.

Decoded + curated from the June 2026 catalog (productType codes + sample titles
+ observed option coverage). REVIEW = debatable / low-volume; adjust freely.
"""

EMPIRICAL_THRESHOLD = 0.50

# code -> (human label, category group, expects_color, expects_size)
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
    "S O X": ("Novelty / Misc", "Accessory", True, False),   # REVIEW
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
    "W A T": ("Watches", "Watch", False, False),             # REVIEW
    "P A P": ("Pants (Petite)", "Apparel", True, True),
    "S K S": ("Skirts & Skorts", "Apparel", True, True),
    "M E N": ("Men's (belts)", "Belt", True, False),         # REVIEW
    "T O L": ("Tops", "Apparel", True, True),
    "P A C": ("Capris", "Apparel", True, True),
    "P R M": ("RMD / Premium Charms", "Charm", False, False),  # REVIEW
    "L E G": ("Leggings", "Apparel", True, True),
    "A C B": ("Belts", "Belt", True, True),                  # REVIEW
    "V E S": ("Vests", "Apparel", True, True),
    "P E T": ("Pet", "Pet", False, False),
    "B R A": ("Bras & Intimates", "Apparel", True, True),
}

# Low-volume / debatable curated calls, surfaced in the report for review.
REVIEW_CODES = {"S O X", "W A T", "M E N", "P R M", "A C B"}


def expectation(code, color_cov, size_cov):
    """Return (label, category, expects_color, expects_size, basis, review).

    color_cov / size_cov: fraction (0..1) of in-stock products of this type that
    already carry a Color / Size option. Used for the empirical fallback.
    """
    if code in TYPE_MAP:
        label, cat, ec, es = TYPE_MAP[code]
        return label, cat, ec, es, "curated", code in REVIEW_CODES
    return (code, "(unmapped)",
            color_cov >= EMPIRICAL_THRESHOLD,
            size_cov >= EMPIRICAL_THRESHOLD,
            "empirical", False)
