# Shopify SEO + Filter & Search Readiness — Audit Learnings & Traps

Distilled from the Clothing Cove engagement (June 2026). This is the reference behind the
`shopify-store-audit` skill. **The core lesson:** audit the **live, rendered, published** state —
not a stored field or the theme file. Almost every overstated metric came from violating that.

---

## THE ONE RULE
> A metric is only real if it's true on the **published storefront** and in the **rendered HTML**.
> Stored-field-empty ≠ missing. Theme-file-empty ≠ missing. In-stock ≠ published.

Before quoting ANY number to a client, ask: (1) Is this scoped to **published** products? (2) Does the
**live page** actually lack it, or is there a **fallback/app** filling it? A client will open their store
and check — if your number collapses under inspection, you lose the room.

---

## TRAP CATALOG (the ones that bit us)

### 1. "Missing SEO title" — Shopify pre-fills the default
- `seo.title` empty ≠ no title. Shopify renders the **product name** as the `<title>` fallback, AND the
  admin "Search engine listing → Page title" box is **pre-filled** with the product name + a character
  count, so it *looks* set.
- **Tell:** the title is the raw product name, SKU and all (e.g. `…10095`). No human writes that.
- **Verdict:** real count, but it's **hygiene** ("no custom-written title; runs on the product-name
  default"), NOT a missing-content emergency. Never say "the box is empty" — it isn't.

### 2. "Missing meta description" — theme falls back to the body
- `seo.description` empty ≠ no meta description. The theme renders `<meta name="description">` from the
  **body text**. Live pages have a description even when the custom field is blank.
- **Check:** `curl` the live PDP and read the rendered `<meta name="description">`.
- **Verdict:** hygiene/quality (auto-derived, un-optimized, often >160 chars), not a void. The only true
  void is when the **body is also empty** (tiny on a published store).

### 3. App metafields can mask OR mirror — check both, label correctly
- SEO apps (SEOMetaManager etc.) store title/desc in `global.title_tag` / `global.description_tag`.
  Always count **native `seo.*` OR the app metafield**. Here they were exact **mirrors** (same products),
  so the app does NOT independently fill blanks — do not tell the client "the app covers it."

### 4. "Missing images / body" — the UNPUBLISHED backlog
- The audit scoped to `status:ACTIVE + in-stock`, but **~34% of those were not published** to the
  storefront (received into inventory, never photographed/published). They **dominate** the
  missing-image/body counts. Live store: ~0%.
- Clothing Cove: "3,838 missing images" → **24** on the published store. "3,522 missing body" → ~1%.
- **Always re-scope SEO metrics to `published_status:published`.** The unpublished set is a separate
  **merchandising/backlog** story (publish + photograph), not a live-SEO problem.

### 5. "Missing schema / Open Graph" — theme-only check is wrong
- `theme.liquid` having no JSON-LD ≠ no schema live. An **app injects** rich structured data on the live
  site. Clothing Cove homepage + PDPs had `ClothingStore`, `Product`+`Offer`+availability+brand+sku,
  `Organization`, `BreadcrumbList`, `OpeningHoursSpecification`, full OG tags — **a strength, not a gap.**
- **Check:** `curl -sL -A "Mozilla/5.0" <live url>` and grep for `application/ld+json`, `"@type"`,
  `og:`. (Retry on HTTP 000 — transient failures read a stale temp file.)

### 6. "Missing size/color" filters — option vs metafield vs neither vs one-size
- "Missing size" defined as "no variant option literally named `Size`" conflates four states:
  (a) has the option under another name (`Shoe size`, `Ring size`) → false negative;
  (b) has it in a **metafield** only; (c) genuinely absent; (d) legitimately **one-size** (ponchos).
- **Dual standard** (the right bar): a product is filter-ready only with **both** the variant **option**
  (PDP selection) **and** the **taxonomy metafield** (clean, normalized, swatch/text filter).
- Shopify taxonomy metafields (`shopify.size`, `shopify.color-pattern`, `shoe-size`, `ring-size`) are
  `list.metaobject_reference` → values are **metaobject GIDs**, not text.

### 7. Collection descriptions — the ONE genuine content gap (no fallback)
- Unlike products, a collection **body description** has **no Shopify fallback**. Empty = the category
  page is a headline + a product grid and nothing else. ~78% of collections (and ~86% of the *navigable*
  ones — the number that matters) were empty. This is the **real, high-value** gap (category/brand pages
  drive rankings + give AI something to read). Collection **meta titles** DO fall back to the collection
  name → same hygiene caveat as products.

### 8. Scope drift & denominators
- Active vs in-stock vs published; separate export pulls differ slightly (36,047 vs 35,931 active;
  11,693 vs 11,742 in-stock). **Pick one scope per chart, label it, prefer published for SEO.** Don't let
  one row use 11,693 and the next 11,742.

### 9. Re-scope EVERY "in-stock" metric to published before claiming it
- Duplicate titles 909 → **36** live. "99% tags" → ~95%. The image error is not unique; assume every
  count is inflated by the unpublished set until re-scoped.

---

## BLIND SPOTS (nearly missed — found by adversarial review agents)
- **No GSC/GA4 baseline** behind the projection = unfalsifiable. Add **Phase 0**: connect Search Console +
  GA4, pull 16-month baseline + ranking/competitor snapshot. For a *declining* store, diagnose *why* first.
- **Indexation bloat:** non-navigable/event/empty/duplicate collections, giant "catalog" collections
  (Products: 36,959) as crawl sinks, `-copy` duplicate products (~1,160 handles), cryptic abbreviated
  handles (~4,110), mega-menu dumping 400+ links on the homepage. → "indexation hygiene / pruning" workstream.
- **Reviews + FAQ rich results blocked:** 0 products had review data, no review app installed, FAQ page
  had no `FAQPage` schema. Highest-CTR rich results for a boutique, currently $0-effort-blocked.
- **Value fragmentation:** ~3,620 raw color strings, ~348 sizes. Raw values can't power filters →
  normalization (map raw → taxonomy, confident-auto + review-tail) is a **prerequisite**, not an afterthought.
- **Agentic-commerce surface:** Shopify's newer robots/UCP/`agents.md`/`sitemap_agentic_discovery` — an
  AEO frontier worth assessing.

---

## CORRECT METHODOLOGY (the checklist)
1. Fetch **published + in-stock** for all SEO claims (`query:"status:active published_status:published"`).
2. For titles/meta/schema/OG: **curl the live rendered HTML**; distinguish stored field vs rendered
   fallback vs app metafield.
3. For filters: dual standard (option AND metafield); learn raw→taxonomy mappings **from products staff
   already tagged** (no fabrication); route ambiguous values to human review.
4. Collections: measure **body** description emptiness (real gap) separately from meta-title (hygiene).
5. **Spawn 3 adversarial review agents** before finalizing — data-recompute, proposal-QA, blind-spots.
   This caught the duplicate-title scope error, the templated-title bug, the visible "Progress" columns,
   and the indexation/reviews omissions.
6. Re-scope and re-verify every headline number against the **live** store — a client will.

---

## DATA / API GOTCHAS
- **Bulk export JSONL:** lines **without a `handle`** key are sub-objects (variants/images, joined by
  `__parentId`) — filter to product lines.
- **Metafields in bulk** come as `{"value": "..."}` — access `['value']`, then `json.loads` for list types.
- **Token scopes:** `read_metaobjects` / `read_metaobject_definitions` are often **denied** — you can't
  resolve taxonomy display names; use the GIDs (the import only needs GIDs). Setting a metaobject-reference
  metafield needs `write_products`, NOT `write_metaobjects` (referencing existing metaobjects).
- **Matrixify** metaobject-reference imports take the **GID** (newline-separated for list metafields).
- `vendor` = cryptic wholesale supplier codes (LEEGIN LEATHER = Brighton); `productType` = 3-letter codes
  (`J E W`, `D R C`) — **unusable** for auto-writing copy. Ground copy in the collection/brand identity.
- Network in the sandbox is flaky: retry on DNS `getaddrinfo`/HTTP 000; remove temp files before re-grep
  so you don't read stale output.

---

## PROPOSAL FRAMING (client-facing doctrine)
- **Value-anchor pricing:** show conventional **hands-on hours** (the agency anchor) + an **in-house**
  comparison (months + staff wages); TKBS column = faster **and** cheaper. Price on value, not delivery speed.
- **Never reveal automation/tooling** in client docs — strip "scripted", "bulk-generate", "automatable",
  "Script". The efficiency is the margin to absorb, not disclose. (Watch for leftover "Progress/✓ Done"
  columns that reveal the work is fast/cheap.)
- **Lead with the real gaps** (collection content, filters, AEO content depth, Phase 0 baseline). Frame
  titles/meta as **hygiene**. Don't claim strengths (schema, OG, live images) as gaps.
- **3 clean files:** SEO+AEO Plan, Filter & Search Readiness Plan, Projected Impact (lead/cover).
  Dollar price appears **only on the cover**. No version words in filenames.
- **The integrity play wins skeptical clients:** not overselling (titles=hygiene, schema=already good,
  "3,838 images" → 24) is exactly what earns trust with a been-burned-before owner.
