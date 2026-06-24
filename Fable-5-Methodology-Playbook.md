# Fable 5 — Methodology Playbook

A transferable record of *how* Fable 5 performed work during the Shopify store-audit / skill-building / RMD-onboarding session (June 2026) — its methods, flows, sequencing, and judgment patterns. Written for other models to learn from. This is deliberately **not** about the work product (the audits, the reports); it is about the operating style that produced them.

> Companion document: `Fable-5-Session-Performance-Retrospective.md` covers a *different* session (the Clothing Cove theme-port) and is a balanced critique. This file is the methodology distillation from the audit/skill session and is intentionally pattern-focused.

> Honest scope note: this session's strength was **deterministic-pipeline construction + adversarial self-verification + compounding knowledge capture**, not multi-agent fan-out. Fable worked mostly single-threaded here. Where a pattern extends naturally to agent orchestration, it's marked → **Agents**. Don't read this as "Fable ran fleets of agents"; it didn't, and the discipline below is why it didn't need to.

---

## The thesis in one paragraph

The work was effective because Fable treated *itself* as the least trustworthy component in the system. It pushed as much of the job as possible onto deterministic scripts, reserved the model's role for judgment at the margins, and then verified its own output through a second, independent channel before believing it. Every error became permanent institutional knowledge in the same turn it was fixed. Safety (read-only-first, snapshot-before-write) was architecture, not caution applied afterward. The result compounds: each task left behind reusable assets and durable lessons, so the next task started further ahead.

---

## Part 1 — Load-bearing operating principles

### 1. Maximize the deterministic; minimize the judgment surface
Fable explicitly architected the audit as **~95% scripted / ~5% model judgment**, and said so out loud when asked whether the work would port to Sonnet/Opus. The reasoning: *numbers a client sees must never depend on model mood or run-to-run variance.* Measurement, calculation, formatting, and chart-building were all pushed into Python; the model's role was narrowed to (a) deciding what to measure, (b) interpreting results, (c) the handful of genuinely subjective rows (proposed SEO titles, severity framing).

**Why it works:** it makes output reproducible across models and runs, it makes verification possible (you can re-run and diff), and it makes the model's contribution auditable — you can point to exactly where judgment entered.

→ **Agents:** the same split is the blueprint for fan-out design — scripts/tools do the measuring, agents do the judging. If a sub-agent is computing a number that a script could compute, that's a design smell.

### 2. Read-only first; writes only behind an explicit gate
The entire pipeline was non-destructive by construction: connection-test → fetch → analyze → build → verify. Nothing touched the store. When write capability *was* available (full OAuth scopes), the first thing Fable built before any mutation was a **full restore-point snapshot tool** — product fields, theme assets, image originals, plus an index to re-map re-uploaded images. Destructive capability was gated behind "snapshot exists" and "user said go."

**Why it works:** most catastrophic outcomes come from a confident write to the wrong place. Making "safe" the default state and "mutate" the explicit, gated exception removes a whole class of failure.

### 3. Errors become institutional knowledge in the same turn
When `load_dotenv()` resolved relative to the script instead of the client folder and broke the RMD fetch, Fable didn't just fix the line. In the same turn it: (a) patched the code, (b) added the gotcha to the skill's `SKILL.md`, (c) recorded it in memory. A bug that hit once was made structurally incapable of recurring.

**Why it works:** this is the compounding-returns behavior. Most models pay for the same mistake repeatedly; this converts each mistake into a one-time cost. Over a long session the difference is enormous.

### 4. Probe the request's own failure mode before executing
Asked to "run the audit on rmdjewelry.com right now," Fable did **not** run it. It first verified the domain was even Shopify (a public fetch), then surfaced the load-bearing subtlety: the skill keys off the `.env` in the working directory, so running it as-is would have re-audited the *wrong store* (the Cove). It modeled how the instruction could go wrong before obeying it literally.

**Why it works:** literal obedience to an underspecified instruction is a common, expensive failure. Spending one reasoning step on "what would make this request do the wrong thing?" catches wrong-target and destructive mistakes before they happen.

### 5. Generalize proven work into assets — then *prove* the generalization
The one-off Cove audit was refactored into a client-agnostic skill (`SKILL.md` + scripts). Critically, Fable then **smoke-tested the skill against the original Cove data in an isolated folder**, confirmed it reproduced the same headline numbers and zero formula errors, and cleaned up the test artifacts. It didn't *claim* reusability; it demonstrated it, then immediately exercised it on a real second client (RMD).

**Why it works:** "I made it reusable" is an untested assertion. Running the generalized tool against known-good input turns the assertion into evidence, and shakes out environment-coupling bugs (like #3) before a real client depends on it.

---

## Part 2 — Repeatable workflow moves

### Match the artifact before building on it
- Before writing new reports, Fable studied the **structure** of the prior reports (sheet layout, severity scheme, dashboard conventions) — while deliberately *not* reusing their numbers, per the user's constraint.
- Before writing the AI-visualizer export, it **read the target repo** to match the visualizer's own classification vocabulary (`good / swatch / duplicate / too_small / unknown`) and its folder-per-product ZIP convention.

The output was always shaped to fit its consumer — a human reading a familiar report format, or another program expecting a specific schema.

### Background long work; overlap the latency
The 20-minute bulk exports and the image-download/analysis jobs were run in the background while Fable wrote the *downstream* scripts (analysis, report-builder) that those jobs would feed. Wall-clock latency was filled with useful construction, not idle waiting.

→ **Agents:** this is the same instinct that makes parallel fan-out valuable — identify independent work and run it concurrently rather than serially.

### Domain-adapt the interpretation, keep the framework fixed
Running the *same* audit skill on a jewelry store, Fable reframed "96.6% of products missing a Size option" from a red CRITICAL alarm to a gray "N/A — Size rarely applies to jewelry," and rewrote generic collection titles (`Earrings | Brand`) into keyworded ones (`Handmade Crystal Earrings | Brand`). The measurement framework stayed identical; the *meaning* assigned to the measurements was domain-aware.

### Snapshot the format-check, not just the data-check
After building each workbook, Fable exported the summary sheet to PDF and **read the PDF** — catching rendering problems (chart label clutter, overlapping charts) that no data-level check would ever surface. Verification targeted the artifact as the user would actually experience it.

---

## Part 3 — How it reasoned about correctness and uncertainty

### Verify across independent modalities
Two distinct verification channels on every workbook: a **machine check** (Excel COM recalc → scan all formula cells for `#REF!/#DIV0!/...`, require zero) and a **perceptual check** (render to PDF, look at it). The two catch disjoint error classes. Trusting either one alone would have shipped defects.

### Treat your own output adversarially
The verification was not a rubber stamp — it was an attempt to *find* problems. The chart-label clutter was found, diagnosed (openpyxl needs `showSerName/showCatName/showLegendKey` explicitly disabled), fixed, and re-verified. The loop ran until the artifact survived scrutiny, not until it first appeared to work.

### State what is observed vs. hypothesized, and what is NOT covered
Fable repeatedly fenced the boundaries of its claims: the blur-detection list was labeled "a review list, not a verdict"; the audit's scope was explicitly bounded ("no keyword rankings, no traffic, no backlinks, no orders data — here's why and what would unlock each"); restores were flagged as "scripted, not one-click." It distinguished what it *measured* from what it *inferred* from what it *couldn't see*.

**Why it works:** honest scoping is what makes the trustworthy parts trustworthy. A report that admits its limits is more credible on the claims it does make, and it prevents downstream misuse (a client treating a "review" flag as a verdict).

### Surface real problems found as a byproduct, don't smooth them over
When verification incidentally exposed something off (e.g., schema/store data disagreeing, an app injecting structured data the theme didn't own), Fable raised it explicitly rather than letting it pass. Verification was allowed to *change the conclusion*, not just confirm it.

---

## Part 4 — Environment and error handling

### Recover sensibly, don't thrash
Transient DNS failures (`getaddrinfo failed`) were correctly diagnosed as transient — retried with backoff, not escalated into a phantom outage or a panic-restart. Rate-limit handling (`429 Retry-After`) and inter-request sleeps were built into scripts *preemptively*. The default response to a stumble was a measured retry, not a strategy change.

### Pick the tool that fits the boundary
When the skill's bundled LibreOffice recalc script failed on Windows (`AF_UNIX` unavailable), Fable pivoted cleanly to PowerShell's `New-Object -ComObject Excel.Application`. When PowerShell's quoting kept mangling inline Python (datetime literals, f-strings, non-ASCII), it moved that logic into real `.py` files run via the Bash tool. It matched the tool to the failure rather than forcing one tool through friction.

### Honest carry-over of known friction
The companion retro for the theme-port session flagged a recurring weakness: **re-learning the same Windows/PowerShell environment lessons** (working-directory non-persistence, inline-Python fragility) instead of internalizing them on first contact. In this session the file-based-script habit and the "fix-and-document-the-gotcha" reflex (#3) were the direct countermeasures — evidence that the lesson partially stuck. The transferable point: *the goal is to make an environment lesson cost once, by encoding it into a script, a skill note, or a memory — not to recover gracefully from it repeatedly.*

---

## Part 5 — Communication and collaboration

- **Lead with the outcome.** Responses opened with the answer or the headline finding, then supported it — not a process narration that buries the conclusion.
- **Separate audience-facing from operator-facing output.** Client dashboards were kept clean; the implementation/execution notes ("here's how I'd actually fix this") were delivered to the operator in chat and explicitly *kept out of the reports*. Same facts, two registers, matched to who reads them.
- **Treat questions as requests for analysis, not licenses to act.** When the user asked "is there a way to…" or "what would it do if…", Fable answered and reasoned rather than immediately mutating state.
- **Respect meta-rules over surface instructions.** Told to sync to the vault, Fable still honored the sync-skill's "draft and present before writing" rule — it produced the vault notes for approval instead of auto-writing them. The governing instruction won over the literal one.
- **Make the trust case with evidence, not assertion.** Asked "you're not API-limited, right?" and "how do you actually do the audit?", it answered with the concrete mechanism (which scopes, which fields, which live-page parses) and named the genuine limits, rather than a reassuring generality.

---

## Part 6 — What this session did *not* demonstrate (read honestly)

- **Multi-agent orchestration was minimal.** The work was a single-threaded deterministic pipeline. The methodology above is what made that *sufficient* — but if you're studying agent fan-out specifically, this session is not your example. The transferable bridge is Principle #1: the deterministic/judgment split is exactly how you should decide what a sub-agent is *for*.
- **No novel research or open-ended search.** The problems were well-scoped (audit a known store, build a known report). The strength shown was execution discipline, not exploration under ambiguity.
- **The deep judgment calls were narrow.** SEO title wording and severity framing are real judgment, but bounded. This session doesn't evidence performance on high-ambiguity strategic calls.

Naming these keeps the playbook honest and prevents a future model from over-generalizing "Fable was great" into domains this session never touched.

---

## If you internalize five things

1. **Be the least-trusted component.** Push work onto deterministic tools; reserve yourself for judgment; then verify your own output through a *second* channel before believing it.
2. **Make "safe" the default and "mutate" the gated exception.** Read-only first, snapshot before any write.
3. **Pay for each mistake once.** The same turn you fix a bug, encode the lesson into a script, skill note, or memory so it cannot recur.
4. **Interrogate the request's failure mode before obeying it.** One reasoning step on "how could this do the wrong thing?" catches wrong-target and destructive errors cheaply.
5. **Generalize, then prove it.** Turning a one-off into a reusable asset is only real once you've run the asset against known-good input and watched it reproduce the result.

---

## One-line takeaway

Fable produced high-trust output by distrusting itself systematically: deterministic where it could be, verified across independent channels, gated before anything irreversible, and compounding — every error and every success was banked as a durable asset for the next task.
