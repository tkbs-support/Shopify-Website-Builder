const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, LevelFormat,
  HeadingLevel, BorderStyle, Header, Footer, PageNumber,
} = require("docx");

// --- palette ---
const NAVY = "1F3A5F";
const ACCENT = "2E75B6";
const GREY = "5A5A5A";
const LIGHT = "888888";

const checkBox = "☐"; // ☐ empty checkbox

function section(title) {
  return new Paragraph({
    spacing: { before: 260, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 2 } },
    children: [new TextRun({ text: title, bold: true, size: 24, color: NAVY })],
  });
}

function phase(label) {
  return new Paragraph({
    spacing: { before: 140, after: 60 },
    children: [new TextRun({ text: label, bold: true, size: 19, color: ACCENT })],
  });
}

function item(boldPart, rest) {
  return new Paragraph({
    numbering: { reference: "checks", level: 0 },
    spacing: { after: 70 },
    children: [
      new TextRun({ text: boldPart, bold: true, size: 19 }),
      ...(rest ? [new TextRun({ text: rest, size: 19 })] : []),
    ],
  });
}

function note(text) {
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, italics: true, size: 16, color: GREY })],
  });
}

const doc = new Document({
  styles: { default: { document: { run: { font: "Calibri", size: 19, color: "222222" } } } },
  numbering: {
    config: [
      {
        reference: "checks",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: checkBox,
            alignment: AlignmentType.LEFT,
            style: { run: { color: ACCENT }, paragraph: { indent: { left: 360, hanging: 260 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1080, right: 1080, bottom: 900, left: 1080 },
        },
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER,
              children: [
                new TextRun({ text: "TKBS Marketing", bold: true, size: 15, color: NAVY }),
                new TextRun({ text: "   ·   Project Kickoff Checklist   ·   Page ", size: 15, color: LIGHT }),
                new TextRun({ children: [PageNumber.CURRENT], size: 15, color: LIGHT }),
              ],
            }),
          ],
        }),
      },
      children: [
        // --- Title block ---
        new Paragraph({
          spacing: { after: 20 },
          children: [new TextRun({ text: "The Clothing Cove", bold: true, size: 40, color: NAVY })],
        }),
        new Paragraph({
          spacing: { after: 60 },
          children: [new TextRun({ text: "Project Kickoff Checklist", size: 26, color: ACCENT })],
        }),
        new Paragraph({
          spacing: { after: 40 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 4 } },
          children: [
            new TextRun({
              text: "What needs to be in place to begin the SEO & AEO and Filter & Search Readiness work — and the sequence once we start.",
              italics: true, size: 18, color: GREY,
            }),
          ],
        }),

        // --- Part 1 ---
        section("Part 1 — What we need from you (access & approvals)"),
        note("These unlock the work and let us measure results against a real baseline."),
        item("Google Search Console", " — grant TKBS access (or verify the property and add us as a user). This is how we diagnose the multi-year traffic decline and prove the lift."),
        item("Google Analytics (GA4)", " — grant access. If GA4 isn’t fully set up, we’ll confirm and finish the configuration."),
        item("Shopify admin access", " — a staff account so we can enable filters, publish content, and manage the theme. (Backend catalog data already pulled — this is for making the changes.)"),
        item("Google Business Profile", " — manager access, so we can verify name, address, phone, hours and categories match the website exactly."),
        item("Scope sign-off", " — confirm the Foundation scope (all six core filters + SEO base) so we can schedule the 4-week window."),
        item("Single point of contact", " — one person on your side to confirm brand/product judgment calls and approve the short review lists."),

        // --- Part 2 ---
        section("Part 2 — What happens once access is in place"),

        phase("Phase 0 — Measurement baseline (Week 1)"),
        item("Connect Search Console + GA4", " and pull the 16-month traffic baseline."),
        item("Capture current rankings", " plus a competitor snapshot, so the projected lift is measured — not promised."),

        phase("Foundation — Filters & Search (Weeks 1–4)"),
        item("Enable the ready-to-go filters", " (Brand, Garment type — data is already complete)."),
        item("Normalize and backfill Size and Color data", " so filters display clean, word-based values."),
        item("Switch the four core filters live", " (Size, Color, Brand, Garment type — Price & Availability already on)."),

        phase("Foundation — SEO & AEO (Weeks 1–4)"),
        item("Confirm theme & homepage SEO is live", " (title, meta, H1, schema — already published June 11)."),
        item("Write descriptions + SEO titles", " for the 251 navigable category & brand pages (the real content gap)."),
        item("Indexation hygiene", " — prune / noindex thin, empty and duplicate collections."),

        phase("Ongoing — Tracking"),
        item("Monthly reporting", " that shows traffic and revenue lift against the Phase 0 baseline."),

        new Paragraph({
          spacing: { before: 200 },
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 4 } },
          children: [
            new TextRun({
              text: "Full-catalog product enrichment (titles, descriptions, tags, alt-text), fabric & occasion filters, a reviews app, and the unpublished product backlog are scoped separately, per batch.",
              italics: true, size: 16, color: GREY,
            }),
          ],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  const out = "Delivery Files/The Clothing Cove - Project Kickoff Checklist.docx";
  fs.writeFileSync(out, buffer);
  console.log("Wrote", out);
});
