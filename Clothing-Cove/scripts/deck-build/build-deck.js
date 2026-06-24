// The Clothing Cove — Growth Plan deck (TKBS branded)
// Brand constants + helpers adapted from tkbs-initial-analysis slide-template.js
const PptxGenJS = require("pptxgenjs");

// ── Brand Constants ──────────────────────────────────────────────────────────
const CHARCOAL = "1B2838";
const MINT = "00D4AA";
const WHITE = "FFFFFF";
const COOL_GRAY = "64748B";
const CONTENT_BG = "F7F8FA";
const CARD_BG = "FFFFFF";
const SECTION_BORDER = "E2E6EB";
const DARK_ACCENT = "2A3A4E";
const MUTED = "94A3B8";
const AMBER = "F59E0B";

const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.12 });
const makeCardShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.10 });

// ── Logo mark (native shapes — circle + bars, mint) ──────────────────────────
function addLogoMark(slide, x, y, scale = 1) {
  const u = 0.5 * scale;            // base unit
  slide.addShape("ellipse", { x, y: y + 0.05 * scale, w: u, h: u, fill: { type: "none" }, line: { color: MINT, width: 2.5 * scale } });
  slide.addShape("rect", { x: x + u * 0.78, y: y + 0.20 * scale, w: u * 0.95, h: u * 0.22, fill: { color: MINT } });
  slide.addShape("rect", { x: x + u * 1.30, y: y + 0.42 * scale, w: u * 0.30, h: u * 0.40, fill: { color: MINT } });
  slide.addShape("rect", { x: x + u * 1.62, y: y + 0.42 * scale, w: u * 0.26, h: u * 0.26, fill: { color: MINT } });
}

function addWordmark(slide, x, y, size, onDark = true) {
  const color = onDark ? WHITE : CHARCOAL;
  slide.addText([
    { text: "TURN", options: { fontSize: size, fontFace: "Arial Black", color, bold: true, charSpacing: 2 } },
    { text: "KEY", options: { fontSize: size, fontFace: "Arial Black", color: MINT, bold: true, charSpacing: 2 } }
  ], { x, y, w: 5, h: size / 50, margin: 0, align: "left" });
}

function addFooter(slide, slideNum, totalSlides) {
  slide.addShape("rect", { x: 0, y: 5.15, w: 10, h: 0.475, fill: { color: CHARCOAL } });
  slide.addText([
    { text: "TURN", options: { fontSize: 8, fontFace: "Arial", color: WHITE, bold: true } },
    { text: "KEY", options: { fontSize: 8, fontFace: "Arial", color: MINT, bold: true } },
    { text: " BUSINESS SOLUTIONS", options: { fontSize: 7, fontFace: "Arial", color: MUTED } }
  ], { x: 0.4, y: 5.2, w: 4, h: 0.35, margin: 0 });
  slide.addText("The Clothing Cove — Growth Plan", { x: 3.4, y: 5.2, w: 3.2, h: 0.35, fontSize: 7, fontFace: "Arial", color: MUTED, align: "center", margin: 0 });
  slide.addText(`${slideNum} / ${totalSlides}`, { x: 7, y: 5.2, w: 2.6, h: 0.35, fontSize: 7, fontFace: "Arial", color: MUTED, align: "right", margin: 0 });
}

function addRefSlide(pres, opts) {
  const slide = pres.addSlide();
  slide.background = { color: CONTENT_BG };
  slide.addShape("rect", { x: 0, y: 0, w: 10, h: 0.08, fill: { color: MINT } });
  slide.addText(opts.kicker || "THE CLOTHING COVE", { x: 0.5, y: 0.22, w: 9, h: 0.22, fontSize: 9, fontFace: "Arial Black", color: MINT, charSpacing: 3, margin: 0 });
  slide.addText(opts.title, { x: 0.5, y: 0.44, w: 9, h: 0.45, fontSize: 22, fontFace: "Arial Black", color: CHARCOAL, margin: 0 });
  slide.addText(opts.subtitle, { x: 0.5, y: 0.92, w: 9, h: 0.34, fontSize: 11, fontFace: "Arial", color: COOL_GRAY, margin: 0, valign: "top" });
  slide.addShape("rect", { x: 0.5, y: 1.3, w: 9, h: 0.015, fill: { color: SECTION_BORDER } });
  return slide;
}

function addCard(slide, x, y, w, h, title, items, accentColor) {
  slide.addShape("rect", { x, y, w, h, fill: { color: CARD_BG }, shadow: makeCardShadow(), line: { color: SECTION_BORDER, width: 0.5 } });
  slide.addShape("rect", { x, y, w: 0.06, h, fill: { color: accentColor || MINT } });
  slide.addText(title, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.3, fontSize: 12, fontFace: "Arial", color: CHARCOAL, bold: true, margin: 0 });
  const itemTexts = items.map((item, i) => ({
    text: item,
    options: { bullet: { code: "2022" }, breakLine: i < items.length - 1, fontSize: 9.5, fontFace: "Arial", color: COOL_GRAY, paraSpaceAfter: 5 }
  }));
  slide.addText(itemTexts, { x: x + 0.2, y: y + 0.5, w: w - 0.4, h: h - 0.62, margin: 0, valign: "top" });
}

function addStat(slide, x, y, number, label, w = 1.6) {
  slide.addShape("rect", { x, y, w, h: 0.95, fill: { color: CARD_BG }, shadow: makeCardShadow(), line: { color: SECTION_BORDER, width: 0.5 } });
  slide.addText(number, { x, y: y + 0.08, w, h: 0.45, fontSize: 23, fontFace: "Arial Black", color: MINT, align: "center", margin: 0 });
  slide.addText(label, { x: x + 0.05, y: y + 0.52, w: w - 0.1, h: 0.38, fontSize: 7.5, fontFace: "Arial", color: COOL_GRAY, align: "center", margin: 0, valign: "top" });
}

// ══════════════════════════════════════════════════════════════════════════════
const pres = new PptxGenJS();
pres.defineLayout({ name: "TKBS", width: 10, height: 5.625 });
pres.layout = "TKBS";
pres.author = "Turnkey Business Solutions";
pres.company = "TKBS";
pres.title = "The Clothing Cove — Growth Plan";

let n = 0;
const TOTAL = 9;
const num = () => ++n;

// ── Slide 1: Title (dark) ─────────────────────────────────────────────────────
(() => {
  const s = pres.addSlide();
  s.background = { color: CHARCOAL };
  addLogoMark(s, 0.5, 0.5, 1.05);
  addWordmark(s, 0.5, 1.35, 26);
  s.addShape("rect", { x: 0.5, y: 1.95, w: 2.5, h: 0.04, fill: { color: MINT } });
  s.addText("The Clothing Cove", { x: 0.5, y: 2.25, w: 6, h: 0.6, fontSize: 34, fontFace: "Arial Black", color: WHITE, margin: 0 });
  s.addText("Growth Plan — SEO & AEO · Filter & Search Readiness · Projected Impact", { x: 0.5, y: 2.95, w: 6.2, h: 0.6, fontSize: 13, fontFace: "Arial", color: MINT, margin: 0, valign: "top" });
  s.addText("Prepared June 2026  ·  Milford, MI", { x: 0.5, y: 3.6, w: 6, h: 0.3, fontSize: 11, fontFace: "Arial", color: MUTED, margin: 0 });

  // right sidebar — at a glance
  s.addShape("rect", { x: 6.5, y: 0, w: 3.5, h: 5.625, fill: { color: DARK_ACCENT } });
  s.addText("AT A GLANCE", { x: 6.8, y: 0.5, w: 3, h: 0.3, fontSize: 10, fontFace: "Arial Black", color: MINT, charSpacing: 3, margin: 0 });
  s.addShape("rect", { x: 6.8, y: 0.86, w: 2.4, h: 0.02, fill: { color: MINT } });
  const facts = [
    { l: "Organic traffic", v: "~3,000 visits / mo" },
    { l: "Navigable collections w/o desc.", v: "218 of 254 (86%)" },
    { l: "Core filters live", v: "2 of 6" },
    { l: "Modeled 12-mo revenue lift", v: "≈ +21% (expected)" },
    { l: "Foundation delivery", v: "4 weeks" },
  ];
  facts.forEach((f, i) => {
    const y = 1.15 + i * 0.72;
    s.addText(f.l, { x: 6.8, y, w: 3, h: 0.22, fontSize: 8.5, fontFace: "Arial", color: MUTED, margin: 0 });
    s.addText(f.v, { x: 6.8, y: y + 0.2, w: 3, h: 0.3, fontSize: 14, fontFace: "Arial", color: WHITE, bold: true, margin: 0 });
  });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 2: Navbar fix ───────────────────────────────────────────────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "LIVE SITE FIX",
    title: "Navigation Bar Flash — Why It Happens",
    subtitle: "The menu occasionally collapses to the left on load, then corrects on refresh. We traced the cause on the live theme.",
  });
  addCard(s, 0.5, 1.5, 4.4, 2.05, "ROOT CAUSE", [
    "The menu is built by a third-party app (Globo Mega Menu), not the theme.",
    "On every load it replaces the theme's native menu with its own markup via JavaScript.",
    "Its styling loads separately from Globo's CDN — when that CSS loses the race against the JS, the menu renders as an unstyled list crunched to the left.",
  ], AMBER);
  addCard(s, 5.1, 1.5, 4.4, 2.05, "WHY IT'S INTERMITTENT", [
    "It's a load-order race, decided by network and cache timing.",
    "On refresh the CSS is already cached, so it applies instantly and the menu looks correct.",
    "Cold loads and slow connections are when the flash appears — hence 'sometimes.'",
  ], COOL_GRAY);

  // fix bar
  s.addShape("rect", { x: 0.5, y: 3.75, w: 9, h: 1.2, fill: { color: CHARCOAL }, shadow: makeShadow() });
  s.addShape("rect", { x: 0.5, y: 3.75, w: 0.06, h: 1.2, fill: { color: MINT } });
  s.addText("THE FIX", { x: 0.72, y: 3.85, w: 8.5, h: 0.25, fontSize: 10, fontFace: "Arial Black", color: MINT, charSpacing: 2, margin: 0 });
  s.addText([
    { text: "A scoped CSS rule keyed to Globo's own loading flag: reserve the nav's height and keep the unstyled menu hidden until Globo finishes building it — turning the visible crunch into invisible space that fills in cleanly. ", options: { fontSize: 10, fontFace: "Arial", color: WHITE } },
    { text: "Delivered safely via a duplicated theme → preview → publish, so nothing changes live until it's confirmed.", options: { fontSize: 10, fontFace: "Arial", color: MINT, bold: true } },
  ], { x: 0.72, y: 4.12, w: 8.6, h: 0.78, margin: 0, valign: "top" });
  s.addText("Status: diagnosed on the live theme — feasible and ready to implement.", { x: 0.5, y: 4.98, w: 9, h: 0.15, fontSize: 8, fontFace: "Arial", color: COOL_GRAY, italic: true, margin: 0 });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 3: Filter & Search — readiness by filter ────────────────────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "FILTER & SEARCH READINESS",
    title: "Only 2 of 6 Expected Filters Are Live",
    subtitle: "Scope: 7,709 published live products. A filter is 'fully ready' only with both the shopper-facing option and the normalized metafield that powers a clean facet.",
  });

  const rows = [
    ["Availability", "100%", "Live", MINT],
    ["Price", "100%", "Live", MINT],
    ["Brand", "100%", "Data ready — enable (Phase 1)", MINT],
    ["Garment type", "99%", "Data ready — enable (Phase 1)", MINT],
    ["Size", "32%", "Partial — backfill metafield (Phase 1)", AMBER],
    ["Color", "16%", "Partial — backfill + gaps (Phase 1)", AMBER],
    ["Fabric / Material", "13%", "Greenfield — proposal ready (Phase 2)", COOL_GRAY],
    ["Dress occasion", "2%", "Greenfield — via collections (Phase 2)", COOL_GRAY],
  ];
  const tableRows = [[
    { text: "Filter", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, align: "left", valign: "middle" } },
    { text: "% Ready", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, align: "center", valign: "middle" } },
    { text: "Status", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, align: "left", valign: "middle" } },
  ]];
  rows.forEach((r, i) => {
    const bg = i % 2 === 0 ? CARD_BG : CONTENT_BG;
    tableRows.push([
      { text: r[0], options: { fontFace: "Arial", color: CHARCOAL, bold: true, fill: { color: bg }, fontSize: 9.5, align: "left", valign: "middle" } },
      { text: r[1], options: { fontFace: "Arial Black", color: r[3], fill: { color: bg }, fontSize: 10, align: "center", valign: "middle" } },
      { text: r[2], options: { fontFace: "Arial", color: COOL_GRAY, fill: { color: bg }, fontSize: 9, align: "left", valign: "middle" } },
    ]);
  });
  s.addTable(tableRows, { x: 0.5, y: 1.5, w: 5.9, colW: [1.7, 0.9, 3.3], rowH: 0.30, border: { type: "solid", color: SECTION_BORDER, pt: 0.5 }, valign: "middle" });

  // right insight panel
  s.addShape("rect", { x: 6.6, y: 1.5, w: 2.9, h: 3.45, fill: { color: CHARCOAL }, shadow: makeShadow() });
  s.addShape("rect", { x: 6.6, y: 1.5, w: 2.9, h: 0.06, fill: { color: MINT } });
  s.addText("THE HEADLINE", { x: 6.8, y: 1.68, w: 2.5, h: 0.25, fontSize: 10, fontFace: "Arial Black", color: MINT, charSpacing: 2, margin: 0 });
  s.addText([
    { text: "Size and Color are the conversion-critical filters.", options: { fontSize: 11, fontFace: "Arial", color: WHITE, bold: true, breakLine: true, paraSpaceAfter: 8 } },
    { text: "Most products already let shoppers select size and color — the gap is the normalized metafield that powers a clean filter.", options: { fontSize: 10, fontFace: "Arial", color: MUTED, breakLine: true, paraSpaceAfter: 8 } },
    { text: "That's a structured-data task done in batches, not a per-product rebuild.", options: { fontSize: 10, fontFace: "Arial", color: MINT } },
  ], { x: 6.8, y: 2.0, w: 2.55, h: 2.85, margin: 0, valign: "top" });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 4: Filter & Search — phased roadmap ─────────────────────────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "FILTER & SEARCH READINESS",
    title: "Phased Roadmap — Value Ships Early",
    subtitle: "Sequenced so shoppers get working filters in week 1, with the conversion-critical backfills following close behind.",
  });

  const phases = [
    { tag: "PHASE 1", color: MINT, title: "Quick wins + backfill", items: [
      "Enable Brand + Garment-type filters — data is complete (1–2 hrs, week 1)",
      "Size backfill — 1,480 items → clean Size filter (37–62 hrs, wks 1–3)",
      "Color backfill — 2,734 items, clean text display (68–114 hrs, wks 1–4)",
    ] },
    { tag: "PHASE 2", color: AMBER, title: "Depth filters", items: [
      "Fabric / Material — 964 items, parsed & reviewed (40–56 hrs, wks 4–5)",
      "Dress occasion — mapped from sub-collections (4–8 hrs, wk 5)",
    ] },
    { tag: "PHASE 3", color: COOL_GRAY, title: "Optional full coverage", items: [
      "Length, Fit, and store-led data for items with no size/color in any form",
      "Captured at intake going forward (142–218 hrs, ongoing)",
    ] },
  ];
  let y = 1.5;
  phases.forEach((p) => {
    const h = 0.42 + p.items.length * 0.26;
    s.addShape("rect", { x: 0.5, y, w: 9, h, fill: { color: CARD_BG }, shadow: makeCardShadow(), line: { color: SECTION_BORDER, width: 0.5 } });
    s.addShape("rect", { x: 0.5, y, w: 1.4, h, fill: { color: p.color } });
    s.addText(p.tag, { x: 0.5, y: y + 0.12, w: 1.4, h: 0.25, fontSize: 11, fontFace: "Arial Black", color: p.color === AMBER ? CHARCOAL : WHITE, align: "center", margin: 0 });
    s.addText(p.title, { x: 0.5, y: y + 0.38, w: 1.4, h: 0.3, fontSize: 8, fontFace: "Arial", color: p.color === AMBER ? CHARCOAL : WHITE, align: "center", margin: 0, valign: "top" });
    const items = p.items.map((it, i) => ({ text: it, options: { bullet: { code: "2022" }, breakLine: i < p.items.length - 1, fontSize: 9.5, fontFace: "Arial", color: COOL_GRAY, paraSpaceAfter: 4 } }));
    s.addText(items, { x: 2.05, y: y + 0.12, w: 7.3, h: h - 0.2, margin: 0, valign: "middle" });
    y += h + 0.12;
  });
  s.addText([
    { text: "Recommended foundation (Phase 1–2): 150–242 hrs — all six core filters working.   ", options: { fontSize: 9.5, fontFace: "Arial", color: CHARCOAL, bold: true } },
    { text: "Full coverage (Phase 3): +142–218 hrs, optional.", options: { fontSize: 9.5, fontFace: "Arial", color: COOL_GRAY } },
  ], { x: 0.5, y: y + 0.02, w: 9, h: 0.3, margin: 0 });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 5: Projected Impact — headline ──────────────────────────────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "PROJECTED IMPACT",
    title: "Two Levers That Multiply",
    subtitle: "Modeled conservatively from a 3,000 organic-sessions/mo baseline. Illustrative scenario shapes — with no GSC/GA4 baseline yet, Phase 0 sets and re-calibrates the real targets.",
  });

  addStat(s, 0.5, 1.5, "+12%", "Organic traffic\n(Track A — SEO/AEO)", 2.1);
  addStat(s, 2.75, 1.5, "+8%", "Revenue per session\n(Track B — Filters)", 2.1);
  addStat(s, 5.0, 1.5, "≈ +21%", "Combined revenue\n(expected, M12)", 2.1);
  addStat(s, 7.25, 1.5, "+8→51%", "Range across\nscenarios", 2.25);

  addCard(s, 0.5, 2.75, 4.4, 1.55, "TRACK A — SEO / AEO drives TRAFFIC", [
    "Optimized collection + product content, schema, and AI-answer readiness pull more organic sessions.",
    "Modeled as a cumulative lift on the 3,000/mo baseline.",
  ], MINT);
  addCard(s, 5.1, 2.75, 4.4, 1.55, "TRACK B — FILTERS drive CONVERSION", [
    "Color/size/material filters + on-site search help the people already arriving find and buy.",
    "Modeled as revenue-per-session uplift — the more controllable of the two levers.",
  ], MINT);

  s.addShape("rect", { x: 0.5, y: 4.45, w: 9, h: 0.5, fill: { color: CHARCOAL } });
  s.addText([
    { text: "Revenue is shown as an index (base 100) — ", options: { fontSize: 9.5, fontFace: "Arial", color: MUTED } },
    { text: "the Orders API was not granted at audit, so no baseline AOV. ", options: { fontSize: 9.5, fontFace: "Arial", color: MUTED } },
    { text: "Multiply the index by (current monthly revenue ÷ 100) to dollarize.", options: { fontSize: 9.5, fontFace: "Arial", color: MINT, bold: true } },
  ], { x: 0.7, y: 4.45, w: 8.6, h: 0.5, margin: 0, valign: "middle" });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 6: Projected Impact — projection chart + delivery paths ──────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "PROJECTED IMPACT",
    title: "12-Month Revenue Index & Delivery Paths",
    subtitle: "Combined revenue index (base 100) by scenario, and the three ways to deliver the same foundation scope.",
  });

  const labels = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "M10", "M11", "M12"];
  const data = [
    { name: "Conservative", labels, values: [100, 100, 102, 102, 104, 104, 105.1, 106.1, 107.1, 107.1, 107.1, 108.2, 108.2] },
    { name: "Expected", labels, values: [100, 101, 103, 105.1, 108.2, 111.3, 113.4, 115.6, 116.6, 118.8, 119.9, 119.9, 121] },
    { name: "Strong", labels, values: [100, 102, 106.1, 110.2, 116.6, 123.2, 129.9, 134.5, 139.1, 143.8, 147.3, 149.6, 150.8] },
  ];
  s.addChart(pres.ChartType.line, data, {
    x: 0.5, y: 1.5, w: 5.7, h: 3.4,
    chartColors: [COOL_GRAY, MINT, CHARCOAL],
    lineSize: 2.5, lineSmooth: true,
    showLegend: true, legendPos: "b", legendFontSize: 9, legendFontFace: "Arial",
    showTitle: false,
    valAxisMinVal: 95, valAxisMaxVal: 155, valAxisMajorUnit: 10,
    catAxisLabelFontSize: 8, valAxisLabelFontSize: 8,
    catAxisLabelFontFace: "Arial", valAxisLabelFontFace: "Arial",
    valGridLine: { style: "solid", color: SECTION_BORDER, size: 0.5 },
    catGridLine: { style: "none" },
  });

  // delivery paths
  s.addText("WHAT IT TAKES — SAME OUTCOME, THREE PATHS", { x: 6.5, y: 1.5, w: 3.1, h: 0.3, fontSize: 9.5, fontFace: "Arial Black", color: CHARCOAL, margin: 0 });
  const paths = [
    { t: "In-house (your team)", time: "~13–22 months", cost: "$10,120–16,808 wages", note: "Pulls staff off the floor; historically stalls.", c: COOL_GRAY, dark: false },
    { t: "Outside agency", time: "~2–4 months", cost: "$23,750–39,000", note: "Specialist rates, same hands-on work.", c: AMBER, dark: false },
    { t: "TKBS (us)", time: "4 weeks", cost: "$12,000", note: "Faster than in-house, a fraction of agency — your team stays selling.", c: MINT, dark: true },
  ];
  let py = 1.85;
  paths.forEach((p) => {
    const h = 0.95;
    s.addShape("rect", { x: 6.5, y: py, w: 3.0, h, fill: { color: p.dark ? CHARCOAL : CARD_BG }, shadow: makeCardShadow(), line: { color: SECTION_BORDER, width: 0.5 } });
    s.addShape("rect", { x: 6.5, y: py, w: 0.06, h, fill: { color: p.c } });
    s.addText(p.t, { x: 6.65, y: py + 0.07, w: 2.8, h: 0.22, fontSize: 10, fontFace: "Arial", bold: true, color: p.dark ? WHITE : CHARCOAL, margin: 0 });
    s.addText([
      { text: p.time + "  ·  ", options: { fontSize: 9, fontFace: "Arial", color: p.dark ? MINT : CHARCOAL, bold: true } },
      { text: p.cost, options: { fontSize: 9, fontFace: "Arial", color: p.dark ? MINT : p.c, bold: true } },
    ], { x: 6.65, y: py + 0.30, w: 2.8, h: 0.22, margin: 0 });
    s.addText(p.note, { x: 6.65, y: py + 0.52, w: 2.8, h: 0.4, fontSize: 8, fontFace: "Arial", color: p.dark ? MUTED : COOL_GRAY, margin: 0, valign: "top" });
    py += h + 0.1;
  });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 7: SEO & AEO — the gap ──────────────────────────────────────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "SEO & AEO PLAN",
    title: "The Content Gap Holding Back Rankings",
    subtitle: "The catalog is strong; discoverability hasn't kept up. The category and brand pages that should rank have no text for Google — or AI — to read.",
  });
  addStat(s, 0.5, 1.5, "86%", "Navigable collections w/o\ndescription (218 of 254)", 2.1);
  addStat(s, 2.75, 1.5, "59%", "In-stock products on\ndefault SEO title (4,579)", 2.1);
  addStat(s, 5.0, 1.5, "96%", "In-stock products\nuntagged (7,365)", 2.1);
  addStat(s, 7.25, 1.5, "Apr '23", "Last blog post —\nnothing fresh to cite", 2.25);

  addCard(s, 0.5, 2.75, 4.4, 2.1, "CRITICAL — WHY IT MATTERS", [
    "Category pages are what Google & AI read to learn what the store sells — 218 of 254 navigable collections have no description (the real content gap).",
    "143 live products have no description at all — invisible to search and AI.",
    "Only 2 of 6 filters live (no Color/Size/Brand facets).",
  ], AMBER);
  addCard(s, 5.1, 2.75, 4.4, 2.1, "ALREADY FIXED (LIVE, JUNE 11)", [
    "Theme SEO work published live (was sitting on an unpublished theme).",
    "Homepage title, H1 & meta now keyworded + location-aware.",
    "ClothingStore + FAQ JSON-LD added; store hours verified & consistent.",
  ], MINT);
  addFooter(s, num(), TOTAL);
})();

// ── Slide 8: SEO & AEO — fix roadmap ──────────────────────────────────────────
(() => {
  const s = addRefSlide(pres, {
    kicker: "SEO & AEO PLAN",
    title: "Fix Roadmap — Highest-Value First",
    subtitle: "Publish what exists, then the category content that drives rankings, then catalog-wide depth. AEO readiness is built in throughout.",
  });

  const rows = [
    ["P1 ✓", "Publish/port theme SEO work to live theme", "Theme only", "Done — live June 11", MINT],
    ["P1 ✓", "Homepage title, meta & H1 (keyword + location)", "2 elements", "Done — live June 11", MINT],
    ["P2", "Write descriptions for navigable category & brand pages", "251 collections", "The real content gap — start here", AMBER],
    ["P2", "SEO titles + meta descriptions for live products", "4,579 / 2,797", "Catalog hygiene at scale", COOL_GRAY],
    ["P3", "Tag live products (filtering + AI taxonomy)", "7,365 products", "Feeds filters & AI category signals", COOL_GRAY],
    ["P3", "Product descriptions (missing + thin) + alt text", "143 + 541 / 842 img", "Indexable + AI-recommendable", COOL_GRAY],
  ];
  const tableRows = [[
    { text: "Pri", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, align: "center", valign: "middle" } },
    { text: "Action", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, valign: "middle" } },
    { text: "Scope", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, valign: "middle" } },
    { text: "Note", options: { fontFace: "Arial", bold: true, color: WHITE, fill: { color: CHARCOAL }, fontSize: 9, valign: "middle" } },
  ]];
  rows.forEach((r, i) => {
    const bg = i % 2 === 0 ? CARD_BG : CONTENT_BG;
    tableRows.push([
      { text: r[0], options: { fontFace: "Arial Black", color: r[4], fill: { color: bg }, fontSize: 9, align: "center", valign: "middle" } },
      { text: r[1], options: { fontFace: "Arial", color: CHARCOAL, bold: true, fill: { color: bg }, fontSize: 9, valign: "middle" } },
      { text: r[2], options: { fontFace: "Arial", color: COOL_GRAY, fill: { color: bg }, fontSize: 8.5, valign: "middle" } },
      { text: r[3], options: { fontFace: "Arial", color: COOL_GRAY, fill: { color: bg }, fontSize: 8.5, valign: "middle" } },
    ]);
  });
  s.addTable(tableRows, { x: 0.5, y: 1.5, w: 9, colW: [0.7, 3.5, 1.7, 3.1], rowH: 0.42, border: { type: "solid", color: SECTION_BORDER, pt: 0.5 }, valign: "middle" });
  s.addText("AEO readiness rides along: collection descriptions + schema + a revived blog are what make the store legible and citable to ChatGPT, Perplexity & Google AI Overviews.", { x: 0.5, y: 4.62, w: 9, h: 0.35, fontSize: 9, fontFace: "Arial", color: COOL_GRAY, italic: true, margin: 0 });
  addFooter(s, num(), TOTAL);
})();

// ── Slide 9: Next steps (dark) ────────────────────────────────────────────────
(() => {
  const s = pres.addSlide();
  s.background = { color: CHARCOAL };
  addLogoMark(s, 4.35, 0.4, 0.95);
  s.addText("Recommended Next Step", { x: 0, y: 1.5, w: 10, h: 0.5, fontSize: 26, fontFace: "Arial Black", color: WHITE, align: "center", margin: 0 });
  s.addText("Start with the $12,000 foundation — diagnostics, high-value category content, and all six core filters in ~4 weeks, with tracking that proves the lift before any full-catalog enrichment.", { x: 1.5, y: 2.05, w: 7, h: 0.7, fontSize: 12, fontFace: "Arial", color: MINT, align: "center", margin: 0, valign: "top" });

  const steps = [
    "Connect Search Console + GA4 and capture the 16-month baseline",
    "Ship the navbar fix and enable the ready filters (Brand, Garment type)",
    "Write the category & brand page content, then backfill Size & Color",
  ];
  steps.forEach((step, i) => {
    const y = 2.95 + i * 0.6;
    s.addShape("ellipse", { x: 1.7, y, w: 0.38, h: 0.38, fill: { color: MINT } });
    s.addText(String(i + 1), { x: 1.7, y, w: 0.38, h: 0.38, fontSize: 15, fontFace: "Arial Black", color: CHARCOAL, align: "center", valign: "middle", margin: 0 });
    s.addText(step, { x: 2.25, y: y - 0.02, w: 6.2, h: 0.42, fontSize: 12, fontFace: "Arial", color: WHITE, valign: "middle", margin: 0 });
  });

  s.addShape("rect", { x: 0.5, y: 4.85, w: 9, h: 0.5, fill: { color: DARK_ACCENT } });
  s.addText("Josh Horsley  ·  info@tkbsmarketing.com  ·  248-891-7144  ·  tkbsmarketing.com", { x: 0.5, y: 4.85, w: 9, h: 0.5, fontSize: 10, fontFace: "Arial", color: MUTED, align: "center", valign: "middle", margin: 0 });
  addFooter(s, num(), TOTAL);
})();

const out = "../../Delivery Files/The Clothing Cove - Growth Plan (TKBS).pptx";
pres.writeFile({ fileName: out }).then((f) => console.log("Saved:", f)).catch((e) => { console.error(e); process.exit(1); });
