# Fable 5 — Session Performance Retrospective

A meta-analysis of *how* the Fable 5 model performed the work during the Clothing Cove theme-port session (June 11–14, 2026) — its working style, failure modes, and recovery patterns. This is about process and execution quality, not the subject matter of the task.

Evidence is drawn directly from the session transcript (actual error messages, tool sequences, and decisions).

---

## Summary judgment

Strong engineering judgment and verification discipline; let down repeatedly by a small set of avoidable environment-friction errors that it failed to internalize after first contact. The *quality* of the output was high and well-verified; the *efficiency* of getting there leaked tool calls to the same recurring mistakes.

---

## What it did well

### 1. Round-trip verification of every mutation
It never trusted a write. After every `PUT` to the Shopify Asset API it re-fetched the asset and compared against what it intended to write (`port-live-homepage-changes.py`, `push-schema-hours-fix.py` both end with a re-download + diff/marker check, including `round-trip identical: True`). When the user later challenged whether changes had actually ported, the evidence already existed and it could produce authoritative proof (theme `updated_at`, asset values, and a rendered preview-HTML fetch) instead of re-asserting.

### 2. Defensive sequencing around irreversible actions
- Committed a git snapshot of both themes **before** the merge as an explicit rollback point (`c47d557`), and referenced commits by hash when describing rollback options.
- Used a true **3-way merge** (ancestor snapshot + both sides) to attribute every change to either the client or prior TKBS work, rather than a naive two-way diff that would have risked clobbering. Result: zero misattributed conflicts.
- Never published the theme itself — correctly left that gate to the user — and never pushed anything client-facing without sign-off.

### 3. Calibrated honesty / no overclaiming
- In the report annotations it distinguished "done" (green ✓) from "partial" (amber ◐) and explicitly refused to mark items done it couldn't verify (e.g. left og:/twitter app-dependency as partial rather than claiming the theme covered it).
- When asked to confirm the SEO Manager fix, it checked and said **"Not yet"** rather than confirming prematurely — then confirmed only once both schema blocks actually agreed.
- Surfaced a **real bug as a byproduct of verification**: caught that the theme schema said Thursday closes 6pm while the store's own homepage said 8pm. It flagged this rather than glossing over it, and it turned into a genuine correctness fix.

### 4. Self-correcting under user challenge
The "why does it still say Last saved: May 15?" question was handled well: instead of defending, it fetched the theme record, the asset timestamp, and the rendered preview, then correctly diagnosed the *real* cause (the admin UI only updates that label on theme-editor saves, not API writes) and offered the screenshot-level verification path.

### 5. Record hygiene
Kept memory files and the Obsidian project note in sync with reality as facts changed across the session (publish-ready → published; hours unverified → verified → app-fixed), and updated the spreadsheet status notes to match. Records didn't drift from truth.

---

## Recurring friction (the avoidable stuff)

### 1. Working-directory amnesia — the standout weakness
PowerShell shell state does **not** persist between tool calls, so a `Set-Location Clothing-Cove` in one call is gone by the next. After the mid-session repo reorg moved files into `Clothing-Cove/`, the model hit "can't open file '...\scripts\verify-port.py'" / "No such file or directory" **at least three separate times** (`verify-port.py`, `verify-live-schema.py`, the first `annotate-progress.py` attempt, the openpyxl load).

Each time it recovered by re-running with `Set-Location ...; <command>` chained in one call — but it kept *re-learning* the same lesson instead of adopting "always prefix the cd in the same call" as a durable habit after the first failure. This is the clearest efficiency leak in the session.

### 2. Windows/PowerShell inline-Python fragility
Inlining logic via `python -c "..."` repeatedly broke on the Windows/PowerShell boundary:
- `SyntaxError: leading zeros in decimal integer literals` — an ISO datetime literal got de-quoted by PowerShell before Python saw it.
- `f-string expression part cannot include a backslash`.
- `UnicodeEncodeError: 'charmap' codec can't encode character '→'` (and repeatedly for –, é) because Windows stdout defaults to cp1252.

It *eventually* converged on the right pattern — write a real `.py` file and add `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` — but oscillated between inline and file-based scripting longer than it should have given how early the first encoding error appeared.

### 3. Tooling existence assumptions
Assumed `win32com` was importable for Excel COM (`ModuleNotFoundError: No module named 'win32com'`), then pivoted cleanly to PowerShell's `New-Object -ComObject Excel.Application`. Good recovery, but the assumption cost a round-trip; the memory note about "Excel COM on Windows" existed and could have pre-empted it.

### 4. External-state collisions handled, but reactively
Hit the Excel file lock twice (`PermissionError: [Errno 13]`, plus a `~$....xlsx` lock-file detection). It handled these gracefully — detected the lock, told the user to close the file, retried — but only after colliding, rather than checking for the lock file first when it knew the user had the workbook open.

---

## Adaptive behaviors (recovery quality was high)

Where it stumbled, it generally recovered sensibly rather than thrashing:
- **Transient DNS** (`getaddrinfo failed`): correctly diagnosed as transient rather than a real outage, retried, and baked retry-with-backoff loops into the scripts (`capture-theme-delta.py`, the preview fetches). Did not over-engineer or panic-restart anything.
- **Rate limiting**: pre-emptively built `429 Retry-After` handling and inter-request sleeps into the capture script before hitting a limit.
- **Checksum false-positives**: recognized that Shopify asset-list MD5s can differ on byte-identical binaries, and added a byte-compare before trusting any binary diff — then recorded this as a reusable gotcha.

The recovery instinct is good. The gap is that several of these stumbles were *predictable* from the environment context and could have been prevented rather than recovered from.

---

## Process / workflow patterns

- **File-based scripts as durable artifacts**: leaned toward writing named scripts in `scripts/` (`capture-theme-delta.py`, `threeway-index-diff.py`, `port-live-homepage-changes.py`, `verify-live-schema.py`, etc.) rather than throwaway inline commands. Upside: reproducible, auditable, re-runnable before publish. Downside: `scripts/` accumulated several one-shot diagnostic files that won't be reused — mild clutter.
- **TodoWrite cadence**: used it to track multi-step phases and kept it roughly current, though it occasionally lagged behind actual state.
- **Communication**: consistently led with the outcome/TLDR, used tables for enumerable facts, and correctly treated user *questions* ("is there a reason…", "what still needs to be done…") as requests for analysis rather than license to start changing things.
- **Gate discipline**: respected the explicit "present the plan before doing any work" instruction and stopped for sign-off before the first mutation.

---

## Recommendations for future sessions on this stack

1. **Adopt the cd-prefix habit immediately and permanently**: every PowerShell call that runs a project script should chain `Set-Location <dir>; <cmd>` in the same invocation, because shell state never persists. Don't re-learn this per session.
2. **Default to file-based Python over `python -c`** on Windows for anything with quotes, datetimes, f-strings, or non-ASCII — and put `sys.stdout.reconfigure(encoding='utf-8', errors='replace')` at the top of every script as boilerplate.
3. **Read the environment/memory context for landmines before acting**, not after colliding: the win32com gap and the Excel-lock pattern were both foreseeable.
4. **Check for `~$*.xlsx` lock files before attempting openpyxl saves** when the user is known to have the workbook open.
5. **Keep the verification discipline** — it was the best thing about the session and directly caught a real correctness bug. Don't trade it away for brevity.
6. **Prune one-shot diagnostic scripts** (or mark them clearly) so `scripts/` stays signal-rich.

---

## One-line takeaway

High-trust output through relentless verification and defensive sequencing, dragged down by a handful of Windows/PowerShell environment frictions it kept rediscovering instead of internalizing. Fix the environment-habit leaks and the same judgment would run materially faster.
