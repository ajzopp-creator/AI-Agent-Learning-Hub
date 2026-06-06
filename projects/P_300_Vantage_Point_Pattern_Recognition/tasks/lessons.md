# P_300 Lessons Log

**File:** `tasks/lessons.md`
**Status:** Live working document
**Last Updated:** 2026-06-03 SEALED (Phase 3 Ledger Calibration System COMPLETE. M-040 through M-044 added. Five critical errors documented and fixed. Ledger verified: COHR + DE signals captured. Next: 20-day wait, then ledger-fill.)
**Maintained By:** Anthony Zoppi + Claude (architect)

---

## Purpose & Relationship to Other Files

This file is the **live working lessons doc** for P_300. It stages lessons before they are structurally embedded.

| File | Role |
| :---- | :---- |
| `docs/P_300_System_Architecture_v2.7.md` §6 (EC Log) | Permanent archive of *structurally embedded* lessons (encoded in schema, SKILL, or code) |
| `tasks/lessons.md` (this file) | Live working lessons -- staging area; methodology rules; recent corrections not yet promoted |
| `.claude/skills/p300-project-context/SKILL.md` | Concise auto-loaded protection rules; populated from promoted lessons |

**Promotion path:** New correction -> `tasks/lessons.md` -> applied immediately for current chat -> when generalizes, promoted to EC log + encoded structurally in SKILL/code/schema.

This file is loaded at session start by the SIP per the INIT protocol.

---

## Section 1 -- Session Methodology Rules (Active)

### M-001 -- "You write, I review" pattern
**Rule:** For all file deliveries (Python, docs, configs), the AI writes the file directly to its target Windows path via `windows-mcp:FileSystem`. The operator reviews. The AI never asks the operator to copy-paste code from chat. (Confirmed 2026-05-13.)

### M-002 -- One file per turn
**Rule:** When multiple files are queued, deliver one per response. Operator reviews. AI writes the next. No multi-file blasts.

### M-003 -- Plan before write
**Rule:** Any task involving 3+ files or architectural decisions requires a written file plan with line-count estimates *before* any code is written. Wait for explicit operator approval.

### M-004 -- Dual delivery for documents
**Rule:** Standalone reference documents (architecture, lessons, SIP, SKILL) require BOTH disk write AND in-chat artifact. Disk for permanence, artifact for review. (Identified 2026-05-13.)

### M-005 -- Match operator message length
**Rule:** Short user message -> short AI response. Substantive decisions warrant substantive answers; trivial pings get trivial replies. Never lecture. Never restate the operator's question.

### M-006 -- Honest accountability over defensive recovery
**Rule:** When the AI misses something, acknowledge it directly. No padding, no apology spirals. State what was missed, what's being corrected, and move on.

### M-007 -- Direct file writes when filesystem MCP is available
**Rule:** At session start run `tool_search` for `filesystem:write_file` or `windows-mcp:FileSystem`. When available, write all project files directly. Never use the sandbox-download-and-move pattern. (Confirmed 2026-05-13.)

### M-008 -- Check bash_tool for wall-clock time before falling back
**Rule:** When displaying the session header time, run `bash_tool` with `TZ='America/New_York' date '+%A, %B %d, %Y -- %H:%M ET'`. The "time not available" fallback applies ONLY when no shell tool is reachable. (Identified 2026-05-13.)

### M-009 -- Architecture doc contains only canonical statements
**Rule:** The P_300 architecture doc states facts, not suggestions. Hedge phrases are forbidden unless explicitly marked illustrative. (Identified 2026-05-13.)

### M-010 -- Catch vestigial planning artifacts at architecture transitions
**Rule:** When project strategy shifts, audit prior plan artifacts for items that no longer fit. Plan revisions must update downstream artifacts in the same pass. (Identified 2026-05-13.)

**Instances caught so far:**
- (1) Preservation CSV concept survived Path A->B fresh-start decision (Stage 2->3, 2026-05-13)
- (2) `ONEDRIVE_ROOT` constant survived D3 converter scope trim (Stage 4, 2026-05-15)
- (3) `History Grid (*).csv` live-format reference survived Stage 4 XLSX standardization (Stage 6 pre-work, 2026-05-16)

### M-011 -- Route Python logging to stdout in scripts called from PowerShell
**Rule:** All Python scripts from PowerShell must configure `logging.basicConfig()` with `stream=sys.stdout`. PowerShell flags any stderr output as red NativeCommandError even when exit code is 0. (Identified 2026-05-13.)

**Extension (Stage 6, 2026-05-17):** ANY stderr output renders red, including SyntaxWarning, DeprecationWarning, `sys.stderr.write()`, and third-party library warnings. Defenses: forward slashes in path literals; `warnings.filterwarnings("ignore", ...)`; `2>&1` redirection as last resort.

### M-012 -- Set PRAGMA foreign_keys = ON immediately after every sqlite3.connect()
**Rule:** SQLite's `foreign_keys` pragma defaults to OFF per-connection. Every connection must execute `conn.execute("PRAGMA foreign_keys = ON;")` immediately after `sqlite3.connect()`. All connections go through `python/utilities/db_connect.py`. (Identified 2026-05-14.)

### M-013 -- Cross-field invariants in Pydantic v2 go in `@model_validator(mode="after")`
**Rule:** Pydantic v2 field validators run in declaration order and see only earlier fields. Cross-field invariants belong in `@model_validator(mode="after")`. (Identified 2026-05-14.)

### M-014 -- Validate config artifacts against a real source-data sample before commit
**Rule:** For any config claiming alignment with vendor data, run a verification pass against an actual example file BEFORE writing to the final location. (Identified 2026-05-14.)

### M-015 -- Live filesystem MCP reads override project attachments for `tasks/*.md`
**Rule:** When INIT loads `tasks/lessons.md` and `tasks/todo.md`, ALWAYS read via filesystem MCP (`filesystem:read_text_file`), NEVER trust project-attached versions. Attachments lag disk. (Identified 2026-05-15.)

### M-016 -- Verify python interpreter resolution at session start
**Rule:** Before suggesting any `python` invocation in a fresh PowerShell session, run `(Get-Command python).Source` and confirm it returns `C:\Users\Trader\.conda\envs\p140\python.exe`. Never paper over with `$py` aliases.

**Workstation facts:** Active host is PowerShell ISE. ISE profile: `D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShellISE_profile.ps1`. Documents is OneDrive-redirected to D:\. Four python.exe installs in PATH -- without profile prepend, Python 3.14 wins.

**Mandatory diagnostic:** `$PROFILE` / `(Get-Command python).Source` / `($env:Path -split ';')[0..2]`

**STRUCTURALLY EMBEDDED 2026-05-16:** SKILL v2.4 Critical Paths + Workstation Resolution subsection.

### M-017 -- INIT must reconcile live catalog state against tracking docs (catalog is ground truth)
**Rule:** During INIT, query the live catalog DB for ground truth. If catalog state diverges from tracking docs, catalog wins. Surface divergence BEFORE proposing any work.

**STRUCTURALLY EMBEDDED 2026-05-16:** SIP v2.4 Step 5b + SKILL v2.4 Critical Paths + Must/Must-Not rules #13.

### M-018 -- Domain/infrastructure module names must not collide with Python stdlib
**Rule:** Module files in `domain/`, `infrastructure/`, and `application/` must NOT share a name with any Python stdlib module. Use descriptive suffixes. (Identified 2026-05-18.)

**STRUCTURALLY EMBEDDED 2026-05-18:** SKILL v2.5 Anti-Patterns list #11.

### M-019 -- Windows PowerShell stdout default encoding is cp1252; use ASCII-only
**Rule:** Use ASCII-only in any string flowing through `print()`, `sys.stdout.write()`, or `logger.info()`. File writes are SAFE when explicit `encoding="utf-8"` is passed. (Identified 2026-05-18.)

**Extension (2026-05-20):** PowerShell `>` redirection encodes as UTF-16 LE. Use `Out-File -Encoding utf8` or write directly from Python with `encoding="utf-8"`.

**STRUCTURALLY EMBEDDED 2026-05-18:** SKILL v2.5 Anti-Patterns list #12.

### M-020 -- Schema field `return_pct` stores decimal fractions, not percentages
**Rule:** `forward_labels.return_pct` stores decimal fractions (0.0672 = 6.72%). Multiply by 100 at the display boundary only. (Identified 2026-05-18.)

**STRUCTURALLY EMBEDDED 2026-05-18:** SKILL v2.5 Anti-Patterns list #13.

### M-021 -- Pydantic v2 `model_copy(update=...)` skips re-validation
**Rule:** `model_copy(update=...)` does NOT run validators. Use full re-construction in validator negative tests. (Identified 2026-05-17.)

### M-022 -- Target = anchor workflow for VP pattern capture
**Rule:** The operator-chosen target date IS the launch/anchor. Pattern setup = 20 bars BACK; forward labels = 5/7/10/15/20 trading days FORWARD. Filename: `Pattern_<TARGET_YYYYMMDD>_<CAPTURE_YYYYMMDD>_<SYMBOL>.xlsx`. (Identified 2026-05-18.)

### M-023 -- VP license/access constraints and thesis-flexible symbol substitution
**Rule:** Operator's VP subscription doesn't include all sector browses. When a recommended symbol is unavailable, operator names alternatives; Claude substitutes preserving thesis. (Identified 2026-05-18.)

### M-024 -- Pipeline A filename date format is strict YYYYMMDD; no capture-date sanity check
**Rule:** Pipeline A does NOT check that capture date is not in the future or that target precedes capture. Double-check capture date before running `add-pattern`. (Identified 2026-05-18.)

### M-025 -- CWD discipline for `python cli.py`; folder convention drift on Pattern XLSX saves
**Rule (CWD):** Always invoke `python python\cli.py` from project root.
**Rule (folder):** Pattern XLSX files belong in `data\historical_patterns\`, NOT `data\historical\`. (Identified 2026-05-18.)

### M-026 -- Date-validity pre-checks for date-driven pick lists
**Rule:** Validate every proposed date against weekends and US market holidays before publishing any date-driven pick list. Use `pandas.tseries.holiday.USFederalHolidayCalendar` + `weekday() < 5` check. (Identified 2026-05-18.)

### M-027 -- Cost-estimate discipline: measure or admit unknown, never extrapolate from feel
**Rule:** When asked for cost, token, time, or performance estimates, either (a) measure the actual value, or (b) state "unknown" with the specific reason. Never extrapolate from intuition. (Identified 2026-05-19.)

### M-028 -- Parameter sweeps on sparse catalogs must bracket the firing region
**Rule:** At N ~25 patterns, production-default thresholds may produce zero firing events. Bracket the signal-firing region first; then sweep outward. Re-run at N >= 50. RETIRED 2026-05-28 -- N=116 sweep completed; see M-034. (Identified 2026-05-19.)

### M-029 -- Don't interpret domain data without confirming domain semantics
**Rule:** State what the measurement says (numeric, value-neutral). Only label features as "signal"/"noise" when domain meaning is confirmed. (Identified 2026-05-19.)

### M-030 -- `windows-mcp:PowerShell` + `python -c` with embedded code hangs reliably
**Rule:** Do not invoke `python -c "<embedded code>"` via `windows-mcp:PowerShell`. Hangs ~75-100% of attempts. Use `python script.py` instead. (Identified 2026-05-20.)

### M-031 -- File-size accretion crossing §8.4.2 is a signal to split, not a license to slim docstrings
**Rule:** When a file grows past 300 lines through legitimate accretion, split at a natural boundary. Don't compress docstrings. Current breaches: `schemas_pipeline_b.py` 408, `daily_evaluate_pipeline.py` 417, `report_writer.py` 373. (Identified 2026-05-20.)

### M-032 -- Windows CMD batch: `SETLOCAL ENABLEDELAYEDEXPANSION` + `!VAR!` breaks parser on this system
**Rule:** Do not use `SETLOCAL ENABLEDELAYEDEXPANSION` combined with `!VAR!` in Windows batch files on this workstation. Produces `: was unexpected at this time.` even on syntactically correct files. Use `%date%` string slicing for date; `goto` label pattern to break for loops. (Identified 2026-05-21.)

### M-033 -- Catalog composition: 70:30 uptrend-to-pullback target; 3:1 ongoing maintenance ratio
**Rule:** Maintain catalog at ~70% uptrend / 30% pullback to hold baseline WR in 0.65-0.72 range where BUY/WATCH gates are meaningfully discriminating. For every 3 uptrend patterns added, add 1 pullback before the next uptrend batch.

**Pullback pattern criteria:** 15-25% decline across the pre-anchor 20-bar window, 3-5 bars of tight sideways consolidation. Anchor = first day of consolidation. Expected forward-label profitability: 30-40% at h=5.

(Captured 2026-05-21)

### M-034 -- Feature ablation at N=116: volume_zscore is noise; z_score not discriminating at this catalog size
**Rule:** Before treating default similarity features and classification thresholds as production-ready, run feature ablation and threshold sweep at meaningful catalog size (N>=50 per M-028). Two findings from 2026-05-28 at N=116:

**Finding 1 -- volume_zscore removed from SIMILARITY_FEATURES (config.py v1.4):**
Removing it raised BUY precision from 54.0% to 70.5% (+16.5 pp) with +42 BUY count -- the largest single-feature delta by a wide margin. Volume is noisy cross-symbol and cross-time; matching on volume regime pulls similarity toward volume profile instead of price structure. All other 9 features within +-1.3 pp of baseline. close_pct_from_anchor retained (-4.0 pp if removed -- contributing signal).

**Finding 2 -- BUY_MIN_Z_SCORE lowered from 1.0 to 0.0 (config.py v1.5):**
At N=116 with 58% baseline WR, z_score is not a discriminating BUY gate. Every combo at wr=0.70 produced identical results across z=-0.5, 0.0, and 0.5 (buy_count=49, precision=79.6%). z>1.0 was suppressing valid BUY signals without improving precision. z=0.0 preserves the semantic intent (cluster must be above baseline) without blocking signals the wr gate already validated.

**Current production thresholds (post 2026-05-28):**
- BUY: n>=5, wr>=0.70, z>0.0 -- precision 79.6%, mean return +6.4% at h=5 (N=116 LOO)
- WATCH: n>=3, wr>=0.60, z>0.0 (unchanged from Stage 6 Decision F)

**Re-evaluation trigger:** Re-run ablation and sweep at N=300+. Re-tighten BUY_MIN_Z_SCORE toward 1.0 when z becomes a meaningful separator.

(Captured 2026-05-28)

### M-035 -- AI must verify python interpreter BEFORE issuing any python invocation to the operator
**Rule:** M-016 is not only a diagnostic the operator runs when something breaks. The AI must proactively run `(Get-Command python).Source` via `windows-mcp:PowerShell` and confirm it returns `C:\Users\Trader\.conda\envs\p140\python.exe` BEFORE telling the operator to run any `python` command. If the check fails, fix the interpreter first. Never issue a `python` command to the operator on an unverified interpreter.

**Failure mode captured 2026-05-29:** AI instructed operator to run `python integrations\lm_studio\examples\p300_status_check.py` without checking interpreter. Python 3.14 (system) was active; ImportError on `idna` followed. M-016 was in the SKILL but AI treated it as operator-only guidance rather than a pre-flight gate on every AI-issued python invocation.

(Captured 2026-05-29)

### M-036 -- Hub root bootstrap in `python/application/` requires 5 x `.parent`, not 4
**Rule:** Any file located at `python/application/<file>.py` is 5 levels below the Hub root. The correct bootstrap is:

```python
_HUB_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
```

Count: `<file>.py` -> `application/` -> `python/` -> `<project_root>/` -> `projects/` -> `Hub root`.

Using 4 x `.parent` resolves to `projects/` instead of Hub root, causing all Hub-relative path lookups to fail silently or with confusing FileNotFoundError.

**Failure mode captured 2026-05-29:** `daily_evaluate_pipeline.py` v1.8 used 4 x `.parent`. `_HUB_ROOT` resolved to `projects/` instead of `C:\Users\Trader\AI-Agent-Learning-Hub\`. All P_000 and P_010 config reads failed with FileNotFoundError. Fixed in v1.9.

**Applies to:** All files in `python/application/`. Files in `python/domain/`, `python/infrastructure/`, and `python/utilities/` are one level shallower -- they require 4 x `.parent` to reach Hub root.

(Captured 2026-05-29)

### M-038 -- Always verify the Hub interface before proposing any cross-project call
**Rule:** Before writing or proposing any code that calls from one project into another, read the actual source file of the calling module to confirm how it currently imports the target. Then check `shared_resources/python_utils/` for a published Hub interface. If one exists, use it -- never reach into another project's internals via a hardcoded `sys.path` injection.

**The Hub interface for Obsidian writes is:**
```python
from shared_resources.python_utils.vault_interface import write_to_vault
```
located at `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils\vault_interface.py`.

**Failure mode captured 2026-05-31:** AI proposed a backfill script that would have called `handle_write()` from P_800's internal `obsidian_writers.application.write_handler` directly, bypassing the published Hub interface `write_to_vault()` in `shared_resources/python_utils/vault_interface.py`. The existing `write_signal_to_obsidian.py` was already violating this boundary via `sys.path` injection. Both corrected to use the Hub interface.

**Check sequence before any cross-project import:**
1. Read the calling module's current import block
2. Check `shared_resources/python_utils/` for an existing interface
3. Read the interface README if present
4. Use the published interface -- never bypass it

(Captured 2026-05-31)

### M-039 -- Pipe multi-line script output to UTF-8 file; read it back directly
**Rule:** When a Python script will produce more than one screen of output, always pipe to a UTF-8 file and read it back via `windows-mcp:FileSystem`. Never ask the operator to paste it and never use bare `>` redirection -- PowerShell default `>` writes UTF-16 LE which produces garbled text and is unreadable by Claude.

**Correct pattern for any long-output script:**
```powershell
python python\script.py 2>&1 | Out-File -Encoding utf8 output.txt
```
Claude then reads `output.txt` directly via `windows-mcp:FileSystem` without operator involvement.

**Applies to:** catalog-summary, feature ablation, threshold sweep, backfill, LOO replay, and any other script with unbounded output.

**Failure mode captured 2026-05-31:** Backfill script produced 750 lines. AI told operator to run and paste output. Operator uploaded a file written with bare `>` which produced UTF-16 LE. Claude had to decode around the encoding artifact rather than reading clean UTF-8 directly.

(Captured 2026-05-31)

### M-040 -- Test execution paths, not just imports; end-to-end before marking complete
**Rule:** Module-level imports and parser registration pass tests; handler execution is different. When adding new CLI subcommands, ledger hooks, or any stateful feature, test ACTUAL EXECUTION: call the handler, invoke the workflow, verify output. Don't just test that imports work or that the parser builds. 

**Procedure before marking any feature "production-ready":**
1. Write test that imports the handler function AND calls it (not just `build_parser()`)
2. Run the actual user workflow end-to-end 
3. For multi-step processes (capture → wait → fill → report), test at least one minimal cycle
4. Verify the output is correct
5. **CRITICAL:** Verify that non-blocking error paths actually succeed, not just that errors are logged

**Failure mode captured 2026-06-03:** Phase 3 ledger system (calibration, ledger-fill, ledger-calibration subcommands) passed a test suite that only verified `build_parser()` succeeded and subcommands were registered. The test never called `_cmd_daily_evaluate()` which triggers lazy imports. Result: `ledger_record.py` had a broken import (`infrastructure.catalog_db` doesn't exist) that passed all tests but failed on first real execution when Tony ran `P_300_DailyEval_v2.bat COHR`. Root cause: incomplete test coverage of execution paths.

**Second failure (same session, 2026-06-03):** After fixing the import error, the ledger_record hook runs non-blocking (good design), but `get_latest_catalog()` call returns wrong path → queries wrong DB → `sqlite3.OperationalError: no such table: patterns`. Hook fails silently; signal still fires. Good error handling masks the real bug: catalog path resolution is broken. Lesson: test non-blocking error paths to verify they actually SUCCEED, not just that they're handled.

**Applies to:** Any new CLI handler, ledger hook, pipeline stage, or cross-module orchestration. Especially important for non-blocking error handlers — verify the happy path works, not just that errors are caught.

(Captured 2026-06-03)

### M-044 -- Read skill documentation FIRST; don't experiment after asking "what should I be using?"
**Rule:** When uncertainty arises about the right tool or approach, **read the applicable skill doc immediately** before proposing workarounds or experiments. Asking "what should I be using" and then fumbling instead of reading the answer wastes time and erodes trust.

**Failure mode captured 2026-06-03:** After multiple PowerShell timeouts on Python commands, Tony pointed out the answer was already documented in the python-project-architecture skill. Instead of reading it, I continued experimenting with different MCP approaches. Lost time and credibility. The skill document had the answer all along.

**Fix:** Whenever you encounter "I believe it's in [skill name]", **immediately fetch and read that skill** before responding. Don't hypothesize; read the source.

(Captured 2026-06-03)

### M-043 -- Non-blocking errors must be logged at WARNING level so operators notice them
**Rule:** When an error is intentionally non-blocking (doesn't stop the flow), log it at WARNING level, NOT INFO or just ERROR. Non-blocking errors that are only logged at ERROR level get lost in the stream and the operator thinks the feature succeeded.

**Failure mode captured 2026-06-03:** Ledger_record hook failed silently (threw exception, caught it, logged at ERROR). The batch file saw exit code 0 and continued. COHR and DE were both archived even though their signals were never recorded to the ledger. Operator only noticed by checking logs after the fact.

**Fix:** (1) Log non-blocking failures at WARNING level so they stand out. (2) Consider adding a summary line at the end: "Ledger: OK" or "Ledger: FAILED (see logs)".

(Captured 2026-06-03)

### M-044 -- Read skill documentation FIRST; don't experiment after asking "what should I be using?"
**Rule:** When uncertainty arises about the right tool or approach, **read the applicable skill doc immediately** before proposing workarounds or experiments. Asking "what should I be using" and then fumbling instead of reading the answer wastes time and erodes trust.

**Failure mode captured 2026-06-03:** After multiple PowerShell timeouts on Python commands, Tony pointed out the answer was already documented in the python-project-architecture skill. Instead of reading it, I continued experimenting with different MCP approaches. Lost time and credibility. The skill document had the answer all along.

**Fix:** Whenever you encounter "I believe it's in [skill name]", **immediately fetch and read that skill** before responding. Don't hypothesize; read the source.

(Captured 2026-06-03)

### M-042 -- Non-blocking hooks can hide silent failures; add explicit success logging
**Rule:** When a feature is designed to fail non-blocking (errors logged but don't stop the flow), add EXPLICIT success logging so absence of a success message indicates the hook never ran or failed silently. Without positive confirmation, debugging becomes guesswork.

**Failure mode captured 2026-06-03:** Ledger_record hook was called but produced no output (no error, no success). Ledger DB remained empty. Without explicit "ledger record success → ledger_id=NNN" logging, operator couldn't tell if the hook ran at all, failed silently, or the insert succeeded but didn't write.

**Fix:** Add explicit logger.info() on success path so every firing produces a log line.

(Captured 2026-06-03)

### M-041 -- Verify utility function signatures before using them in integration points
**Rule:** When adding a new feature that calls an existing utility function (especially from `utilities/`), verify the function exists, understand what it returns, and test it in isolation FIRST. Don't assume a function with a suggestive name does what you expect. Broken utility calls in integration points can hide under non-blocking error handlers.

**Failure mode captured 2026-06-03:** After fixing the import error in ledger_record.py, the code called `get_latest_catalog()` from `utilities/db_utils.py` — a function that either doesn't exist or returns the wrong type/path. The failure was silent due to non-blocking error handling; the ledger hook failed but the daily eval continued and the signal fired. No indication to operator that the ledger record failed until examining logs. 

**Fix:** Use explicit path construction (glob + mtime sort) instead of relying on a utility function that wasn't verified. After fix confirmed working (COHR eval 2026-06-03 12:11:26).

**Applies to:** Any new cross-module call, especially to utilities or infrastructure layers. Always verify by reading the source before use.

(Captured 2026-06-03)

---

## Section 2 -- Operational Lessons Specific to P_300 (Not Yet in EC Log)

### O-001 -- Pattern file bar overage
**Lesson:** VP exported files may contain 1-2 extra bars beyond nominal pattern length. This is a VP export artifact, not corruption. `pattern_instances.window_length` = actual bar count. Never truncate.

### O-002 -- Active symbol inventory (Stage 5 re-ingest scope)
**Lesson:** Distinct symbols for Stage 5 re-ingest: SPY, QQQ, MSFT, NVDA, AAPL, CTRA, ATGE, VOD, CME, TR, LYV, FSLY, NFLX, APPN, BRK_A, ITA, MSA, PG + singletons (HL, IPI, ICE, OII, POET, TXRH, DELL, DNN, ASTS, ESVIF). Singletons require fresh VP captures.

### O-004 -- Empty DB is not a clean baseline for current schema
**Lesson:** `empty__catalog.db` uses the original Perplexity 7-table schema. Archival only -- not a restore point.

### O-005 -- Skill scatter across 5+ locations is a known issue
**Lesson:** P_300 SKILL at `.claude/skills/p300-project-context/SKILL.md`. Consolidation is future work.

### O-006 -- VP History Grid XLSX uses merged top-row headers
**Lesson:** openpyxl returns the merge value only at the first cell of each group; continuation cells return `None`. Sub-header row has two format variants (abbreviated vs full Triple Cross names). Existing parser handles both. (Captured 2026-05-14.)

### O-007 -- Volatility-divergence flag first production validation (2026-05-20)
**Lesson:** First live multi-candidate eval: PLAY 2.79x and WDAY 2.14x both STRONG fires, both PASS class. Flag surfaced correctly without gating. MILD band may be too narrow -- re-evaluate at 50+ candidates.

### O-008 -- VantagePoint .ptf portfolio file is XML; symbol list parseable programmatically (2026-05-21)
**Lesson:** `.ptf` files are XML. Symbol list accessible via `xml.etree.ElementTree`. P_300_WatchList_May2026.ptf yielded 5 symbols in under 1 second. Future: read .ptf -> extract symbols -> drive Pipeline B eval runs. Candidate for P_800 integration.

---

## Section 3 -- Anti-Patterns Reminder (Quick Reference)

- **Never** `df.tail(N)` or `df.head(N)` truncation in converter or ingest layer
- **Never** write TEXT into an INTEGER FK column
- **Never** raw dollar values in cross-symbol similarity matching (use normalized columns)
- **Never** mock data dictionaries in production decision engines
- **Never** hardcoded paths outside `config.py`
- **Never** mix layers (domain doing I/O, infrastructure making business decisions)
- **Never** merge Pipeline A and Pipeline B into a single script
- **Never** put LLM-generated output in the BUY/WATCH/PASS decision path
- **Never** write directly to the master DB -- Lock + Temp-DB + Atomic Move only
- **Never** name a module after a Python stdlib module (M-018)
- **Never** emit Unicode through stdout when invoking from PowerShell -- ASCII only (M-019)
- **Never** treat `forward_labels.return_pct` as a percentage; decimal fraction, x100 at display boundary (M-020)
- **Never** use `SETLOCAL ENABLEDELAYEDEXPANSION` + `!VAR!` in Windows batch files on this system (M-032)
- **Never** issue a `python` command to the operator without first verifying interpreter via `(Get-Command python).Source` (M-035)
- **Never** use 4 x `.parent` from a file in `python/application/` to reach Hub root -- requires 5 x `.parent` (M-036)
- **Never** reach into another project's internals via `sys.path` injection -- always use the Hub interface in `shared_resources/python_utils/` (M-038)
- **Never** use bare `>` redirection for script output -- use `| Out-File -Encoding utf8`; read the file back directly (M-039)

---

## Section 4 -- Open Items / Recent Corrections Not Yet Promoted

*(No active open items as of 2026-05-13. All identified failures from the rebuild session were promoted to EC-060 through EC-067 in the architecture doc.)*

*(2026-05-18 status: M-016, M-017, M-018, M-019 STRUCTURALLY EMBEDDED in SKILL v2.5.)*

*(2026-05-19 status -- Stage 7/8/9 SEAL: M-022 through M-029 added at lesson-level. M-028 retires at N>=50.)*

*(2026-05-20 status -- Stage 9-followup: M-030, M-031, M-019 extension added.)*

*(2026-05-21 status -- Pipeline A tooling: M-032 added; O-008 added to Section 2. M-033 added -- permanent operational rule.)*

*(2026-05-28 status -- Feature ablation + threshold sweep: M-034 added. volume_zscore removed from SIMILARITY_FEATURES; BUY_MIN_Z_SCORE lowered to 0.0. Both changes in config.py v1.4 and v1.5. M-028 formally retired -- N=116 sweep completed. Re-evaluation trigger set at N=300+.)*

*(2026-05-29 status -- M-035 added: AI must verify python interpreter before issuing any python invocation to operator.)*

*(2026-05-29 status -- M-036 added: Hub root bootstrap in python/application/ requires 5 x .parent. Fixed in daily_evaluate_pipeline.py v1.9. cli.py --clean flag routed through main() instead of run_daily_evaluate(). SIP v2.9 updated. NVDA PASS @ h=20 validated.)*

*(2026-05-30 status -- M-037 formalized. Dead code cleanup complete. Evals: ARLP BUY, COTY WATCH, DOX BUY, DD WATCH, EQX WATCH.)*

*(2026-05-31 status -- Catalog reconciled N=139 / 053026catalog.db. M-038 added (Hub interface). M-039 added (UTF-8 output). Gap 6 fixed in write_signal_to_obsidian.py v1.1/v1.2. Backfill complete: 89 notes corrected. P_800 Obsidian Note Standard v1.1 drafted. Pending: standard implementation (6 files), P_800 doc disk write.)*

*(2026-06-03 status -- Phase 3 Ledger Calibration System COMPLETE & VERIFIED. Fired signals captured: COHR (BUY h=15 wr=70% n=20) + DE (BUY h=5 wr=95% n=20). Five critical errors fixed and documented as lessons M-040 through M-044. All import, schema, query, and logging issues resolved. Ledger DB ready for backfill and calibration workflows.)*

---

## Section 5 -- Stage Methodology Notes

### S-001 -- Decision before draft
Each new stage opens with a planning conversation, not a draft. Architecture decisions get locked first.

### S-002 -- Fork-in-the-road questions get a recommendation, not a menu
When the AI surfaces a choice, it always recommends one with rationale. The operator may override but never has to choose blind.

### S-003 -- Stage transition requires document update
At the end of each stage, the architecture doc Change Log gets a new entry. The Stage roadmap in §7 gets updated. The SKILL gets reviewed. New lessons get promoted from this file to the EC log where structurally embedded.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** Any new methodology rule, operational lesson, or correction during a session
- **Promotion review:** End of each stage, lessons in Sections 1, 2, 4 reviewed for promotion to EC log

---

**End of P_300 Lessons Log**
