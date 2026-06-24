# The Clothing Cove — Color Filtering & Swatch Roadmap

**Prepared by:** TKBS Marketing  
**Date:** May 18, 2026  
**Status:** Proposal — No store changes have been made

---

## Executive Summary

Color filtering on theclothingcove.com is not working effectively. An audit of all 35,721 active products reveals two root causes: (1) only 47% of products have color metadata attached, and (2) the theme's color swatch display is not configured — so even products that have color data show plain text instead of visual color chips. This roadmap proposes a phased fix starting with quick wins that require no product changes.

---

## Current State (Audit Results)

### Overall Catalog

| Metric | Count | % of Total |
|--------|------:|-----------|
| Total active products | 35,721 | 100% |
| In stock | 11,747 | 32.9% |
| Out of stock | 23,974 | 67.1% |

### Color Metadata Coverage

| Metric | Count | % |
|--------|------:|---|
| Products WITH a Color option | 16,783 | 47.0% of all active |
| Products WITHOUT a Color option | 18,938 | 53.0% of all active |
| **In-stock products WITH color** | **5,420** | **46.1% of in-stock** |
| **In-stock products WITHOUT color** | **6,327** | **53.9% of in-stock** |
| Products with no options at all ("Default Title") | 17,245 | 48.3% of all active |
| Products with `shopify.color-pattern` metafield | 1,374 | 3.8% of all active |
| Products with ANY Shopify standard metafield | 1,514 | 4.2% of all active |

### Color Option Naming Inconsistency

The Color option name varies across products:

| Option Name | Products |
|-------------|------:|
| "Color" | 12,747 |
| "COLOR" | 4,019 |
| "color" | 17 |

This inconsistency can cause Search & Discovery to treat them as separate filters.

### Unique Color Values

There are **6,052 unique color values** across all products. The top 30:

| Color | Products | | Color | Products |
|-------|------:|---|-------|------:|
| BLACK | 3,289 | | BEIGE | 427 |
| SILVER | 1,112 | | GREEN | 389 |
| WHITE | 1,107 | | BROWN | 382 |
| NAVY | 1,067 | | IVORY | 340 |
| BLUE | 810 | | PURPLE | 313 |
| PINK | 782 | | MULTI | 296 |
| GREY | 768 | | DENIM | 232 |
| GOLD | 767 | | TEAL | 220 |
| RED | 704 | | OLIVE | 216 |
| CLEAR | 629 | | TAUPE | 203 |
| TURQUOISE | 184 | | CHAMPAGNE | 142 |
| YELLOW | 177 | | BURGUNDY | 142 |
| TAN | 170 | | CREAM | 140 |
| AQUA | 161 | | CORAL | 131 |
| CHARCOAL | 160 | | PEWTER | 128 |

The long tail of 6,000+ values includes compound colors ("BLACK/WHITE", "GOLD/NAVY"), pattern names ("AURORA BOREALIS", "SILVER NIGHT"), brand-specific names, and vendor codes.

### Color Coverage by Product Type (Top Categories)

| Type | Total | In Stock | Has Color | In Stock + Color |
|------|------:|--------:|----------:|-----------------:|
| J E W (Jewelry) | 12,798 | 3,991 | 3,551 | 1,056 |
| H O A (Home/Art) | 3,880 | 1,599 | 649 | 298 |
| B A G (Bags) | 2,247 | 628 | 1,479 | 465 |
| T O C (Tops/Clothing) | 2,019 | 488 | 1,798 | 448 |
| A C C (Accessories) | 1,911 | 739 | 827 | 311 |
| J A K (Jackets) | 1,270 | 251 | 1,079 | 232 |
| S O M (Something?) | 905 | 408 | 893 | 403 |
| C H A (?) | 891 | 382 | 127 | 61 |
| B A B (Baby) | 778 | 273 | 208 | 54 |
| C H H (Children) | 707 | 205 | 99 | 40 |
| D R C (Dresses Casual?) | 616 | 163 | 533 | 152 |
| S O X (Socks) | 507 | 169 | 200 | 62 |
| P A M (?) | 485 | 175 | 474 | 174 |
| S H O (Shoes) | 456 | 219 | 415 | 185 |
| S O C (?) | 456 | 208 | 446 | 202 |

**Key insight:** Jewelry (J E W) is the largest category with 12,798 products but only 28% have color data. Clothing categories (T O C, J A K, D R C) have much better coverage at 70-90%.

---

## Why Filters Don't Work

### Problem 1: No Visual Swatches Configured

The Prestige theme has built-in color swatch support — colored squares that appear in collection filters and on product cards. However, the **color swatch configuration is completely empty**. This means:

- Collection page filters show color names as plain text links instead of colored chips
- Product cards don't show color dots for variant selection
- The filtering experience feels unpolished and hard to browse

**Fix:** Populate the theme's `color_swatch_config` setting with a mapping of color names to hex codes (e.g., "BLACK: #000000", "NAVY: #001F3F"). No product data changes needed.

### Problem 2: Inconsistent Option Naming

4,036 products use "COLOR" or "color" instead of "Color". Search & Discovery may treat these as separate filter groups, splitting what should be one unified Color filter.

**Fix:** Standardize all option names to "Color" via the Shopify Admin API.

### Problem 3: Missing Color Data

53.9% of in-stock products have no color option at all. Many of these are "Default Title" single-variant products (likely from POS or bulk imports). Some product types where color is relevant (like Jewelry with 74% missing) could benefit from having color added.

**Fix:** This is the largest effort — requires either manual data entry, bulk CSV updates, or API scripting per product type.

### Problem 4: Structured Metafields Barely Started

Only 1,374 products (3.8%) have the `shopify.color-pattern` metafield — the structured metadata that Search & Discovery uses for smart filtering. These reference 405 unique color metaobjects. The data is heavily concentrated in the **newest products**, suggesting someone started tagging recently but coverage is still very low. Other Shopify standard metafields (size, fabric, gender, age group) are similarly sparse (~1-3% coverage).

**Note:** The API token currently lacks `read_metaobjects` scope, so we cannot inspect what color values those 405 metaobjects contain. Adding this scope would let us audit and build on the existing work.

**Fix:** Continue the tagging initiative and extend it across more of the catalog. Alternatively, the variant Color option values can power filtering without metafields — metafields just give richer structure.

---

## Proposed Fix Phases

### Phase 1 — Activate Color Swatches (Quick Win)

**What:** Populate the theme's empty color swatch configuration with hex codes for all existing color values.

**Impact:** Immediately makes color filters visual (colored chips instead of text) for the 5,420 in-stock products that already have color data. No product data is changed.

| Detail | |
|--------|---|
| Effort | ~2-3 hours |
| Risk | None — theme display setting only, easily reversible |
| Products affected | 0 (no product changes) |
| Visible improvement | Color filters show as colored squares; product cards show color dots |

### Phase 2 — Standardize Color Option Names

**What:** Rename "COLOR" and "color" to "Color" on all 4,036 affected products so Search & Discovery treats them as one unified filter.

| Detail | |
|--------|---|
| Effort | ~1-2 hours (automated script) |
| Risk | Low — cosmetic change to option label only, does not affect inventory or variants |
| Products affected | 4,036 |
| Visible improvement | Single unified "Color" filter in Search & Discovery |

### Phase 3 — Improve Swatch Appearance (Optional)

**What:** Evaluate the default Prestige theme swatch styling and make CSS adjustments if needed (shape, size, hover effects, mobile tap targets).

| Detail | |
|--------|---|
| Effort | ~1-2 hours |
| Risk | None — cosmetic CSS changes on development theme, tested before publishing |
| Products affected | 0 |
| Visible improvement | More polished filter and swatch appearance |

### Phase 4 — Add Color Data to Products (Larger Effort)

**What:** Add Color options to product types that should have them but don't. Priority candidates based on the audit:

| Product Type | In Stock, No Color | Action |
|---|---:|---|
| J E W (Jewelry) | 2,935 | Likely needs color for many items |
| H O A (Home/Art) | 1,301 | May not need color (home goods) |
| A C C (Accessories) | 428 | Some items would benefit |
| C H A | 321 | Evaluate based on product type meaning |
| B A B (Baby) | 219 | Clothing items need color |

| Detail | |
|--------|---|
| Effort | Significant — depends on scope. Days to weeks for thousands of products. |
| Risk | Medium — modifies product data. Would use dry-run testing first. |
| Approach options | Shopify bulk editor, CSV export/import, or automated API scripts |

### Phase 5 — Search & Discovery Optimization

**What:** Verify and configure the Color filter in the Search & Discovery app. Ensure proper sort order and display.

| Detail | |
|--------|---|
| Effort | ~30 minutes |
| Risk | None |

### Phase 6 — Publish to Live

**What:** Apply all changes from the development theme to the live production theme.

| Detail | |
|--------|---|
| Effort | ~30 minutes |
| Risk | Low — changes tested on development theme first |

---

## Recommended Approach

1. **Start with Phases 1 + 2** — these are quick wins (3-5 hours total) that make the existing color data functional and visually appealing. No product data risk.

2. **Evaluate Phase 3** after seeing Phases 1-2 live — the built-in styling may be sufficient.

3. **Scope Phase 4 based on priorities** — adding color to all 6,327 in-stock products without it is a large project. Consider starting with specific clothing categories (T O C, J A K, D R C) where color is most relevant to shoppers, and exclude categories like H O A (home goods) and F O D (food) where color filtering adds less value.

4. **Phase 4 can be done incrementally** — one product type at a time, with review between batches.

---

## Timeline Estimate

| Phase | Time | Prerequisite |
|-------|------|-------------|
| Phase 1 (Swatches) | 2-3 hours | None |
| Phase 2 (Standardize names) | 1-2 hours | None |
| Phase 3 (CSS polish) | 1-2 hours | Phase 1 |
| Phase 4 (Add color data) | 1-4 weeks | Phases 1-2, scope decision |
| Phase 5 (Search & Discovery) | 30 min | Phases 1-2 |
| Phase 6 (Go live) | 30 min | All prior phases |

**Phases 1-3 + 5-6 can be completed in approximately 1 day.**  
**Phase 4 timeline depends on how many product types are prioritized.**

---

## Appendix: Full Audit Data

Complete audit data including all 6,052 unique color values, per-product breakdowns, and product type analysis is available in `color-audit-results.json`.
