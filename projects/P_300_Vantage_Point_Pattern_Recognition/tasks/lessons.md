# P_300 Lessons Log

**File:** `tasks/lessons.md`
**Status:** Live working document
**Last Updated:** 2026-06-29 (ledger-fill produced its first real output ever: 4 stacked bugs found and fixed in one session -- M-060 date format, M-061 yfinance MultiIndex columns, M-062 query_unfilled checked the wrong column, M-064 persist-only-on-full-fill discarded every partial outcome. M-063 widened the fetch window. Result: h5=115/h7=97/h10=58/h15=2/h20=0 fully real, verified via before/after counts. See M-060 through M-064.) | 2026-06-29 (Ledger dedup: 175->142 rows, 33 duplicates removed across 26 groups -- COHR fired 6x, an entire 06-12 batch re-fired wholesale on 06-13/06-15. M-059 added: insert_fired_signal() has no uniqueness guard; code fix still OWED. Backup saved before delete; live-recount safety check matched dry-run exactly.) | 2026-06-28 (AddPattern batch: 31/32 ingested clean, 1 rejected as true duplicate (DOCU, source_file_id=277) -- catalog 331->362 patterns / 245 symbols. DailyEval batch: 22/22 clean, 9 BUY/12 WATCH/1 PASS, first live run under config v1.8 z>1.0. M-058 added: failed ingests leave the source file in historical_patterns\, blocking re-runs until the operator removes it. Pairs with O-009.) | 2026-06-17 (M-051 REAL fix landed: report_writer.py v1.8 -- print_signal_report_clean() no longer hardcodes [OK] written to vault / ARCHIVE OK; gated on LEDGER_LOG_CLASSES, fabricated archive block removed. Paired daily_evaluate_pipeline.py v1.20 M-043 fix -- _obsidian_write() False return now logged. M-054 added: the 2026-06-12 todo.md/lessons.md closure note for this exact bug was never verified against the file -- bug ran live in production 2026-06-12 through 2026-06-17 undetected. Caught via operator-uploaded live DailyEval console log.) | 2026-06-16 (WO-P300-E1.001 IntelliScan stop integration SHIPPED. intelliscan_reader.py v1.0 NEW; signal_schemas.py v2.1 (3 new SignalV2 fields); signal_emitter.py v2.1; daily_evaluate_pipeline.py v1.18. Smoke test PASS: 12 symbols, both support levels correct. M-052 added. WO-P115-E2.001 OPEN -- same pattern needed for P_115.) | 2026-06-12 (M-051 added -- hardcoded success string anti-pattern; falsified functional test captured in report_writer.py print_signal_report_clean().) | 2026-06-11 (M-019 instance: ledger_record.py Unicode arrow fixed; NFR-1 + report_writer smoke PASS; Enhancement 2 gate-on 3/4 done.) | 2026-06-09 (Enhancement 2 shipped -- Certainty-Equivalent BUY gate. CARA exponential utility (Kochenderfer Ch. 6) computes a risk-adjusted CE return per horizon; gates BUY when CE_GATE_ENABLED=True. Shipped OFF (observe-only). config v1.7 + schemas_pipeline_b v1.3 + domain/utility.py v1.0 NEW + aggregator v1.1 + signal_classifier v1.1 + report_writer v1.7. M-046 + M-047 added. utility.py smoke PASS verified.) | 2026-06-08 (Enhancement 1 shipped -- P_300 -> P_400 SIGNAL_V2 signal packet via the P_800 Hub interface. signal_emitter v2.0 + daily_evaluate_pipeline v1.15. M-045 added. COHR live BUY validated -> packet written to TradeOrderManagement/signals/. Architecture v2.7 Enhancement Log + Change Log updated.) | 2026-06-03 SEALED (Phase 3 Ledger Calibration System COMPLETE. M-040 through M-044 added. Ledger verified: COHR + DE signals captured. Next: 20-day wait, then ledger-fill.)
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

**Addendum 2026-06-28 -- re-evaluation trigger fired at N=331; BUY_MIN_Z_SCORE re-tightened to 1.0 (config.py v1.8):**
A walk-forward eval (`domain/eval_scoring.py` -- corpus restricted to strictly-earlier `anchor_date` per pattern, NOT leave-one-out) ran the full 331-pattern catalog (`062326catalog.db`) at both z>0.0 (then-current prod) and z>1.0 (Stage 6 original), via an overridable gate copy parity-verified against the live `signal_classifier` before the comparison was trusted. Results:
- z>0.0: BUY=155 (93 correct / 62 false_positive, 60.0% accuracy)
- z>1.0: BUY=97 (61 correct / 36 false_positive, 62.9% accuracy)
- WATCH absorbs exactly the 58-pattern difference (70->128); PASS is bit-for-bit identical (106 patterns, 44 correct / 62 missed) across both runs -- confirms the override touches only the BUY boundary, nothing else.
- The 58 demoted patterns ran 55.2% win rate (32W/26L) -- below the original BUY pool's 60% average, so the cut trades away a real, if modest, edge rather than noise.

Decision: re-tightened `BUY_MIN_Z_SCORE` 0.0 -> 1.0 in `config.py` v1.8. Closes this re-evaluation trigger.

(Captured 2026-06-28)

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
3. For multi-step processes (capture -> wait -> fill -> report), test at least one minimal cycle
4. Verify the output is correct
5. **CRITICAL:** Verify that non-blocking error paths actually succeed, not just that errors are logged

**Failure mode captured 2026-06-03:** Phase 3 ledger system (calibration, ledger-fill, ledger-calibration subcommands) passed a test suite that only verified `build_parser()` succeeded and subcommands were registered. The test never called `_cmd_daily_evaluate()` which triggers lazy imports. Result: `ledger_record.py` had a broken import (`infrastructure.catalog_db` doesn't exist) that passed all tests but failed on first real execution when Tony ran `P_300_DailyEval_v2.bat COHR`. Root cause: incomplete test coverage of execution paths.

**Second failure (same session, 2026-06-03):** After fixing the import error, the ledger_record hook runs non-blocking (good design), but `get_latest_catalog()` call returns wrong path -> queries wrong DB -> `sqlite3.OperationalError: no such table: patterns`. Hook fails silently; signal still fires. Good error handling masks the real bug: catalog path resolution is broken. Lesson: test non-blocking error paths to verify they actually SUCCEED, not just that they're handled.

**Applies to:** Any new CLI handler, ledger hook, pipeline stage, or cross-module orchestration. Especially important for non-blocking error handlers -- verify the happy path works, not just that errors are caught.

(Captured 2026-06-03)

### M-041 -- Verify utility function signatures before using them in integration points
**Rule:** When adding a new feature that calls an existing utility function (especially from `utilities/`), verify the function exists, understand what it returns, and test it in isolation FIRST. Don't assume a function with a suggestive name does what you expect. Broken utility calls in integration points can hide under non-blocking error handlers.

**Failure mode captured 2026-06-03:** After fixing the import error in ledger_record.py, the code called `get_latest_catalog()` from `utilities/db_utils.py` -- a function that either doesn't exist or returns the wrong type/path. The failure was silent due to non-blocking error handling; the ledger hook failed but the daily eval continued and the signal fired. No indication to operator that the ledger record failed until examining logs.

**Fix:** Use explicit path construction (glob + mtime sort) instead of relying on a utility function that wasn't verified. After fix confirmed working (COHR eval 2026-06-03 12:11:26).

**Applies to:** Any new cross-module call, especially to utilities or infrastructure layers. Always verify by reading the source before use.

(Captured 2026-06-03)

### M-042 -- Non-blocking hooks can hide silent failures; add explicit success logging
**Rule:** When a feature is designed to fail non-blocking (errors logged but don't stop the flow), add EXPLICIT success logging so absence of a success message indicates the hook never ran or failed silently. Without positive confirmation, debugging becomes guesswork.

**Failure mode captured 2026-06-03:** Ledger_record hook was called but produced no output (no error, no success). Ledger DB remained empty. Without explicit "ledger record success -> ledger_id=NNN" logging, operator couldn't tell if the hook ran at all, failed silently, or the insert succeeded but didn't write.

**Fix:** Add explicit logger.info() on success path so every firing produces a log line.

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

### M-045 -- Verify the full cross-project write path before relying on a Hub-interface schema key
**Rule:** A published Consumer Guide is the caller contract, but before trusting a new Hub-interface schema key (e.g. `write_to_vault("SIGNAL_V2", ...)`), confirm the dispatch chain is wired end-to-end in the owning project: (1) the schema registry maps the key to a model, (2) the output-format map routes it (md vs json), (3) the filename builder handles it, (4) the writer exists. A key documented in a guide can still be unwired in code. Confirm on disk, then trust.

**Why it matters (2026-06-08):** Before the COHR live test of Enhancement 1, P_800's `write_handler.py` docstring named only the legacy `P400SIG` json path -- never `SIGNAL_V2`. Because the emit is non-blocking by design, an unwired key would have silently logged a WARNING and produced a false "pass." Verifying the chain across `obsidian_writers/config.py` (OUTPUT_FORMAT / VAULT_FOLDER_MAP / JSON_FILENAME_SUFFIX), `validator.py` -> `schemas.py` (SCHEMA_REGISTRY["SIGNAL_V2"] = SignalV2), and `filename_builder.py` confirmed all four links wired (P_800 work dated 2026-06-07/08); the handler docstring was merely stale. Verifying first turned a potential false-pass into a real end-to-end validation.

**Pairs with:** M-040 (test execution paths, not just imports), M-041 (verify utility signatures before use), M-038 (use the Hub interface for cross-project writes).

(Captured 2026-06-08)

### M-046 -- Risk-aversion lambda is signal provenance; log every change as calibration-affecting
**Rule:** RISK_AVERSION_LAMBDA (config v1.7, Certainty-Equivalent BUY gate) is applied to DECIMAL-FRACTION returns (0.06 = 6%), NOT percentages. At decimal magnitudes lambda must be large to bite -- the meaningful band is ~10-40; default is 20.0. A BUY made at lambda=20 is NOT comparable to a BUY made at lambda=5. Therefore:
1. Any change to RISK_AVERSION_LAMBDA is a calibration-affecting event -- log the change + rationale here in lessons.md.
2. Fired signals are only comparable across runs at the SAME lambda.
3. Lambda is stamped into the report header (report_writer v1.7 `Risk model:` line) and is to be stamped into the ledger record when the gate goes live, so every fired signal records the lambda it was judged under.
4. NEVER calibrate lambda as if returns were in percent (6.0) -- that collapses every CE toward the worst-case analog and nukes every BUY.

**Design (NARRATOR_ENABLED precedent):** CE_GATE_ENABLED defaults False. While off, the CE is computed and displayed but does NOT alter any signal -- determinism regression stays byte-identical. The gate goes live only after lambda is tuned against the ledger. Verified 2026-06-09: utility.py smoke PASS; dispersed cluster [-0.10, 0.02, 0.06, 0.20] mean +4.5% -> CE -3.7% at lambda=20 (8.2 pt penalty), confirming the fat-tail penalty fires as intended.

**Open before gate-on (M-040):** signal_classifier smoke harness covers only CE_GATE_ENABLED=False; the gate-ON path (CE below threshold blocks a BUY) has NO test yet. Add two harness cases proving block-on and no-op-off BEFORE flipping the flag in production. Also owed: end-to-end daily-evaluate determinism replay vs a pre-change run (NFR-1 proof that observe-mode changed nothing).

(Captured 2026-06-09)

### M-047 -- Smoke harnesses must not emit production warning strings they did not earn
**Rule:** A test harness that prints a real production warning on demand trains the operator to half-trust the output. Any harness block that forces a warning/error condition by hand (rather than detecting it) must label its output as a demonstration -- e.g. a `[SMOKE DEMO]` banner stating the state is simulated, not measured -- so the string can never be mistaken for a live detection.

**Failure mode captured 2026-06-09:** report_writer.py smoke harness called print_signal_report_clean(narration=None, narrator_warning=True), which printed `[WARNING] LM Studio unavailable -- narration skipped` even though LM Studio was never contacted. Operator correctly flagged this as misleading regardless of it being a test. Fixed by banner-labeling the demo block (report_writer v1.7). The production string itself is left verbatim -- the demo's job is to show it -- but the banner now announces the state as staged.

**Underlying design note (out of scope, backlog):** In production the warning is driven by a caller-passed boolean (narrator_warning), so print_signal_report_clean renders whatever it is told -- the display can disagree with actual LM Studio state. The real fix is to derive the warning from a recorded narrator outcome (not-attempted / succeeded / attempted-and-failed) in daily_evaluate_pipeline.py, so no boolean can be set wrong. Requires reading the current narrator-detection block first; scoped as its own change.

(Captured 2026-06-09)

### M-048 -- filesystem:edit_file batches are atomic; verify after every multi-edit batch
**Rule:** `filesystem:edit_file` applies its `edits` array as a single transaction. If any one edit's `oldText` fails to match exactly, the ENTIRE batch rolls back -- including edits in the same array that would have matched. A clean partial application never happens. Therefore: after any multi-edit batch, re-read or grep the file to confirm every intended change landed; never assume "the diff showed N edits so N applied." When a batch errors, re-issue ALL edits from that batch, not just the one that failed.

**Failure mode captured 2026-06-09:** SKILL.md decision-flag edit issued as a 3-edit batch (checklist line, Aligned-with pointer, changelog entry). The changelog edit's `oldText` assumed `## Changelog` was immediately followed by the 2026-05-29 entry, but a 2026-05-30 entry sat between them (disk SKILL was newer than the project-attached copy). The mismatch rolled back all three; a verification grep showed the checklist line and Aligned-with pointer were both still stale despite the tool reporting the batch. Re-issued the two reverted edits separately; confirmed by grep. Root contributing cause: trusted the project-attached snapshot's changelog structure instead of the just-read disk content.

(Captured 2026-06-09)

### M-049 -- ATR is a shared Wilder util computed at eval time, never re-fetched downstream
**Rule:** ATR (and any shared eval-time price computation) lives as a pure-domain utility in `shared_resources/python_utils/` and is computed by each evaluating project at evaluation time, on the OHLC bars already in memory -- never re-fetched by a downstream project. Import via the editable install (`from shared_resources.python_utils.atr import compute_atr_wilder`); no per-project copy, no sys.path side-channel. ATR uses full True Range (max of high-low, |high - prev_close|, |low - prev_close|) + Wilder RMA smoothing -- never a high-low-only or simple-average proxy. The function takes plain (high, low, close) tuples so it stays decoupled from any project's bar schema.

**Why (2026-06-10):** P_300's `_compute_atr_from_bars` was a high-low-only simple average -- it understated volatility on gappy names and produced tighter-than-true stops. Moving ATR to P_400 (the target authority) was considered and rejected: P_400 would have to re-read the bars at entry, but the eval project already holds them, so the computation belongs where the data is. Shipped as `shared_resources/python_utils/atr.py` v1.0 (+ test_atr.py 9/9, incl hand-computed Wilder 86/27); P_300 `daily_evaluate_pipeline` v1.16 consumes it.

(Captured 2026-06-10)

### M-050 -- Target ownership: eval projects emit a baseline; P_400 resolves the final target
**Rule:** Every evaluating project (P_300, P_115, future) emits the SAME baseline shape only -- guideline entry/target/stop + setup context (plus a candidate target if useful). P_400 is the single authority that resolves the broker-facing final target: it validates reward-to-risk, applies sizing/stop/council rules, and publishes the order-ready target. Eval projects feed P_400, never compete with it, and must not present their levels as execution-final. The `guideline_*` field names + the `position_size=0` sentinel encode this -- they only make sense if P_400 resolves.

**Why (2026-06-10):** Decided while upgrading ATR. P_300's ATR-derived stop/target are a candidate baseline, not the execution target. Enforcement is still OWED in P_400's build-out -- today P_400's only domain logic is `packet_classifier.classify(filename)`; no target resolver / RR / sizing exists yet, so P_300's guideline_target is the only target by default until P_400 builds it. signal_emitter docstring now marks its levels "candidate/baseline; P_400 resolves final."

(Captured 2026-06-10)

### M-051 -- Never hardcode a success string; output only follows a real call result
**Rule:** Any console line claiming `[OK]`, `SUCCESS`, `DONE`, `written`, or equivalent MUST be produced from the actual function call return value, not hardcoded before or instead of the call. A hardcoded success string is a falsified functional test -- it trains the operator to trust output that has no evidentiary basis and masks real failures indefinitely.

**Correct pattern:**
```python
result = write_to_vault(...)               # real call
print(f"[OK] {ticker} written to vault")   # only after call returns without exception
```

**Forbidden pattern:**
```python
print(f"[OK] {ticker} written to vault")   # hardcoded -- NO CALL WAS MADE
```

**Failure mode captured 2026-06-12:** `report_writer.py` `print_signal_report_clean()` printed `[OK] {ticker} written to vault` and `ARCHIVE OK` as hardcoded strings. No vault write call and no archive call existed anywhere in the function. The strings were scaffolded during clean-output design (v1.4, 2026-05-27) as layout placeholders and never replaced. Because the output looked correct, the missing wiring went undetected across multiple production runs. The 2026-06-11 Obsidian notes that do exist were written by `signal_emitter.emit_signal_packet()` via the P_800 Hub interface -- a separate, correctly wired path. The hardcoded strings in `print_signal_report_clean()` masked the fact that no direct P_300 Obsidian write was ever called from that function.

**Extension -- scaffolding discipline:** Placeholder output strings are permitted ONLY during active UI scaffolding in a single session. Before the session ends, every placeholder must be either (a) replaced with a real call, or (b) removed and tracked as an open todo.md item. No placeholder survives a session boundary.

**Addendum 2026-06-17 -- the original fix never landed:** tasks/todo.md and the system-doc-initializer SKILL both logged this as closed 2026-06-12 ("M-051 closure"). It wasn't. report_writer.py was still v1.7 (2026-06-09) with both hardcoded strings verbatim, plus the archive block also claimed a literal `data/processed/2026-05.zip` path that was never real. The bug ran live in production for 5+ days. Real fix landed 2026-06-17 in report_writer.py v1.8 -- see M-054.

**Pairs with:** M-040 (test execution paths not just imports), M-047 (smoke harnesses must not emit unearned production strings).

(Captured 2026-06-12)

### M-052 -- Stop architecture: emit both VP support levels; let P_400 decide which clears risk
**Rule:** P_300 (and all signal-producing projects) emit three stop fields in every SIGNAL_V2 packet when the IntelliScan eval-parameters grid is present at eval time:
- `intelliscan_support_1`: nearer VP structural support level (primary stop anchor)
- `intelliscan_support_2`: wider VP structural support level
- `atr_adjusted_stop`: `max(intelliscan_support_1, entry - 1x ATR)` -- P_400's primary Quant-gate input

P_300 does NOT decide which level P_400 uses. P_400 receives both and applies its three-gate risk logic to determine if support_1 clears parameters; if not, it may use support_2. P_300 emitting only the tighter level would force P_400 to reject valid setups it could accept with the wider level.

When the IntelliScan grid is absent at eval time, all three fields are `None` (not zero, not omitted). The pipeline is non-blocking -- `load_intelliscan()` logs a WARNING and returns `{}` if the file is missing; `get_support_levels()` returns `(None, None)` for symbols not in the grid.

**File location (operator drops before daily eval bat):**
`<project_root>/data/live/P_300_HistoryGrid_IntelliscanEvalParameters.xlsx`

**Stop method hierarchy (per P_115 pattern, confirmed by Tony 2026-06-16):**
1. Chart structure (support, consolidation base, pattern invalidation -- e.g. bottom of Eddie Z handle) -- PRIMARY
2. IntelliScan VP support level -- PREFERRED when structural level not identifiable from pattern alone
3. ATR-based (2x ATR below entry) -- FALLBACK when no clean structural level exists

**Why this matters (2026-06-16):** P_300 was placing stops at tight pattern technical levels (correct for chart analysis). P_400's Quant gate requires stop >= 1x ATR. Systematic STOP_TOO_TIGHT blocks were occurring on valid setups -- the IntelliScan grid's multi-day verified support levels are naturally wider and structurally grounded, resolving the conflict without synthetic floor inflation.

**Applies to:** P_300, P_115 (WO-P115-E2.001 OPEN), and all future signal-producing projects.

(Captured 2026-06-16)

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

### O-009 -- Symbol case in pattern filenames must be strictly uppercase
**Lesson:** The filename validator in `vp_xlsx_reader.py` enforces `Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx` with uppercase SYMBOL. A single lowercase character (e.g. `RCl` instead of `RCL`) causes an immediate ValueError, catalog unchanged, file not deleted -- it stays in `data\historical_patterns\` requiring a manual rename before re-run. Caught twice (2026-06-16 RCl). Before running AddPattern.bat, visually confirm every filename has an uppercase symbol. Windows Explorer does not flag case mismatches.

**Fix when it happens:** `Rename-Item "...\Pattern_YYYYMMDD_YYYYMMDD_RCl.xlsx" "Pattern_YYYYMMDD_YYYYMMDD_RCL.xlsx"` then re-run the bat.

(Captured 2026-06-16)

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
- **Never** hardcode a success string (`[OK]`, `DONE`, `written`, etc.) -- output only after the real call returns without exception (M-051)
- **Never** assume a rejected AddPattern file is self-clearing -- failed ingests leave the source XLSX in `data\historical_patterns\`; it will block every future batch with the same error until deleted or renamed (M-058)
- **Never** assume daily-evaluate fired signals are duplicate-free -- `insert_fired_signal()` has no uniqueness guard; a re-run on an already-fired signal_date stacks a new row every time (M-059)
- **Never** assume a date string's format without checking its actual source column -- this hub mixes YYYYMMDD (filenames) and YYYY-MM-DD (catalog/ledger) conventions; M-060 was a 26-day, 100%-failure-rate silent bug from this exact assumption
- **Never** assume yfinance returns single-level columns for a single ticker -- flatten MultiIndex columns immediately after download (M-061)
- **Never** write an "unfilled" query against the FIRST field a multi-stage fill populates -- check the LAST field, or partial rows get permanently skipped (M-062)
- **Never** trust a clean exit / "0 errors" log as proof of correctness when the actual counter ("Filled 0/142") still reads zero -- a quiet run can hide a silent persist bug just as easily as a crash hides a parse bug (M-064)

---

## Section 1.5 -- M-053

### M-053 -- Case-normalization must operate on the captured group, not the whole literal string
**Rule:** When a regex match has both literal case-sensitive segments and a variable-case segment (e.g. `Pattern_` / `.xlsx` literals vs. a `SYMBOL` group), normalize case AFTER the match -- on the captured group only. Never call `.upper()`/`.lower()` on the full input before matching against a pattern containing case-sensitive literals; it silently breaks the literals.

**Instance:** `vp_xlsx_reader.py` v1.3 (2026-06-16, O-009 fix) called `filename.upper()` on the whole filename before matching `_FILENAME_PATTERN`, which requires literal `Pattern_`/`.xlsx`. This caused **100% AddPattern ingest failure** from the moment v1.3 shipped -- caught 2026-06-17 09:25 (18/18 files failed in one run). Not caught at the time because the v1.3 fix was never smoke-tested against a normal correctly-cased filename, only against the RCl repro case (which also failed for the same reason, just attributed to a different cause).

**Fix (v1.4, 2026-06-17):** `_FILENAME_PATTERN` compiled with `re.IGNORECASE`; `_parse_filename()` no longer uppercases the input. Only `m.group("symbol").upper()` is normalized when building `PatternFileMetadata`. A PEH smoke-test script was staged at `04-Shared-Resources/verify/run_this.py` (5 cases incl. 2 of the real failed files) but no PASS/FAIL result was reported back -- verification instead came from the production re-run: 13/18 succeeded (vs 0/18 pre-fix); remaining 5 failures were genuine data issues (insufficient bar history / sheet-name mismatch), unrelated to this bug.

**STRUCTURALLY EMBEDDED 2026-06-17:** vp_xlsx_reader.py v1.4.

---

## Section 1.6 -- M-054

### M-054 -- A "DONE"/closure note in tasks/*.md is a claim, not evidence; verify the file before trusting it
**Rule:** tasks/todo.md and tasks/lessons.md entries claiming a fix landed (e.g. "M-051 closure") describe what a prior session believed it did, not what the file on disk actually contains. Before relying on such a closure note -- especially before building new work on top of it, or telling the operator a known bug is fixed -- verify directly: read the file's version header/changelog, or grep for the specific pattern the bug involved. A closure note with no verification is not closure.

**Failure mode captured 2026-06-17:** tasks/todo.md and tasks/lessons.md both stated `print_signal_report_clean()`'s hardcoded `[OK] written to vault` / `ARCHIVE OK` strings (M-051) were fixed and confirmed 2026-06-12 via Claude Code. `report_writer.py` was still v1.7 (2026-06-09) with the exact bug verbatim -- no version bump, no changelog entry for any fix. The bug ran live in production for at least 5 days (2026-06-12 through 2026-06-17) undetected, because the tracking doc said it was already handled -- including a literal stale `data/processed/2026-05.zip` path in the fabricated archive line, and a false `[OK] {ticker} written to vault` claim for PASS-classified signals (CRML, NNE) that never get a real vault write at all. Caught only because the operator uploaded a live DailyEval console log and it was read line-by-line against the actual pipeline code, rather than trusted on the strength of the prior closure note.

**Pairs with:** M-040 (test execution paths, not just imports -- the same discipline applies one level up: verify a CLAIMED fix, not just a NEW one).

(Captured 2026-06-17)

### M-055 -- INIT must never call python via windows-mcp:PowerShell; read a pre-generated status file instead
**Rule:** Any INIT step that previously needed live Python output (catalog-summary, LM Studio check) must be redesigned as: (1) an operator-run `.bat` writes a status JSON outside the chat session, (2) INIT reads that JSON via `windows-mcp:FileSystem`. INIT itself never invokes `python` via `windows-mcp:PowerShell` for these steps -- not even via `python script.py`. M-030 already banned `python -c`; this extends the same prohibition to script invocation specifically on the INIT path, where the ~4-min subprocess ceiling has now been confirmed twice in this file alone as a recurring failure (2026-06-10/11 entries), not an edge case.

**Why now (2026-06-18):** SIP Steps 5b/5c had quietly encoded an assumption -- that a live subprocess call during INIT was acceptable -- that the rest of this Hub already knew was false (M-030, peh-handoff SKILL, the 2026-06-10/11 "count unverified due to PowerShell MCP timeout" entries in todo.md). The fix (WO-P000-E4.001) generalizes beyond P_300: any project's INIT step needing Python output should use the same operator-run-bat-plus-status-file pattern, not a live call.

**Pairs with:** M-030 (`python -c` hangs reliably), M-039 (pipe multi-line output to a file, read it back -- same instinct, different mechanism: a status file replaces the live call entirely rather than just fixing the encoding of its output).

(Captured 2026-06-18)

### M-056 -- A clipboard paste can silently overwrite a production launcher; verify file integrity, don't trust a stray error block

**Rule:** Operator-facing `.bat`/`.ps1` launchers are vulnerable to an editor-window mixup: copying console text intending to paste it elsewhere (e.g. into chat) but the target window is actually the launcher file open in an editor, overwriting the real script with a fragment of console text. When the operator reports a script "acted weird" or produced unexpected console messages and says they ignored them, do not assume the script is intact -- check the file's size/mtime/content directly before re-running or debugging the logic. A script behaving strangely is a cheaper signal to check file integrity than to debug application logic.

**Failure mode captured 2026-06-23:** `P_300_AddPattern.bat` (real script, last legitimate edit 2026-05-21) was reduced to 101 bytes containing a single stray line of PowerShell console text (`XLSX    : PS C:\Users\Trader\...`). Caused by Tony copying a filename/path intending to paste it into chat, with the `.bat` file actually focused in an editor at the time -- the paste (and save) landed there instead. Tony noticed the resulting console messages looked wrong and closed/ignored them rather than investigating, then flagged the file size next session. No on-disk backup or VS Code local history existed to recover the literal original; the file had to be reconstructed from `cli.py`'s real subcommands plus a console transcript of a prior run, then verified end-to-end on a real ingest (TSLA, pattern_instance_id=320) before being trusted as a faithful rebuild.

**Operator-side habit to flag when relevant:** if a launcher prints something unrecognized or malformed immediately on open, stop and check the file before closing the window -- closing/ignoring an error is what let this go undetected until the next session.

**Pairs with:** M-054 (a closure note is a claim, not evidence -- same root instinct: verify the actual file/state rather than trusting that things are as expected).

(Captured 2026-06-23)

### M-057 -- windows-mcp Python calls have a hard ~4-min ceiling; a near-the-line job still completes server-side after the client gives up -- check outputs before assuming failure

**Rule:** `windows-mcp:PowerShell` enforces a system-level ~4-minute ceiling on any single call, independent of any script-internal timeout param passed. This is NOT the same failure mode as M-030 (`python -c` hangs, never completes) -- a job that runs slightly past ~4 min (e.g. 4:30-4:40) DOES finish successfully server-side; the client just cancels a few seconds before completion. Before assuming a timed-out python call failed or needs a re-run, check whether its expected output actually landed.

**Failure mode captured 2026-06-28:** Two `run_eval_loop.py` invocations (331 patterns x 5 horizons, ~4:30-4:40 actual runtime) via `windows-mcp:PowerShell` both timed out client-side at ~4 min. Checking `outputs\reports\eval\` afterward showed BOTH had written complete, valid reports 37-40 seconds after the client gave up. No re-run needed -- the existing output was read and used directly.

**Correct response to a windows-mcp Python timeout:**
1. Do not assume the job failed or is wedged.
2. Check the expected output location via `windows-mcp:FileSystem` first.
3. Fall back to PEH handoff only if the output genuinely isn't there, or pre-emptively for any job expected to run near/past ~4 min (known in advance from catalog size).
4. Never retry the same call directly -- it won't run faster the second time.

**Distinction from M-030/M-055:** those describe calls that may never finish. This describes a clean, correctly-working script that simply outruns an external ceiling unrelated to its own logic -- a different root cause, same "don't call python directly via windows-mcp:PowerShell for anything non-trivial" conclusion.

(Captured 2026-06-28)

### M-058 -- A failed AddPattern ingest leaves the source file in place; same filename will block every subsequent run until the operator removes it

**Rule:** When `add-pattern` rejects a file as already-ingested (`source_file_id` collision) or for any other validation failure, the catalog is untouched by design (M-024/M-025 family) -- but the source XLSX is also left untouched in `data\historical_patterns\`, since only successful ingests get archived/deleted (Step 2 never runs on failure). A duplicate filename will throw the identical error on every future AddPattern batch until an operator explicitly deletes or renames the file. Before re-running a batch that previously had a rejection, confirm the rejected file is gone or corrected -- don't assume the failure was self-clearing.

**Failure mode captured 2026-06-28:** `Pattern_20260109_20260203_DOCU.xlsx` rejected mid-batch (`source_file_id=277` already existed -- a true duplicate, distinct from the M-053 case where DOCU needed re-capture with more history). 31/32 other files in the same batch ingested clean; catalog reconciled at 362 patterns / 245 symbols, 0 hollow, HEALTHY. File confirmed still present in `data\historical_patterns\` post-run; operator verified it was a genuine duplicate and deleted it (folder confirmed empty after).

**Pairs with:** O-009 (same failed-ingest-leaves-file-in-place mechanic, different root cause -- case mismatch there, true duplicate here).

(Captured 2026-06-28)

### M-059 -- insert_fired_signal() has no uniqueness guard; re-running daily-evaluate on an already-fired signal_date stacks a duplicate ledger row every time

**Rule:** `ledger_db.insert_fired_signal()` is a bare INSERT with no check against `(ticker, signal_date, signal_class, chosen_horizon)` already existing. Any daily-evaluate re-run that covers a signal_date already fired (re-running a batch, re-evaluating a symbol, a retry after a partial-batch failure) inserts a fresh duplicate row rather than skipping or updating. Duplicates compound risk-skew calibration (M-046) by overweighting whichever signals happened to get re-fired most.

**Failure mode captured 2026-06-29:** Ledger fill-status check (PEH, read-only) on 175 fired_signals rows found 26 duplicate groups / 33 duplicate rows -- COHR (2026-06-02 BUY h=15) alone fired 6x across 4 separate sessions (06-03 through 06-08) with byte-identical predicted stats. A second cluster (COF/CRK/DX/EMBJ/CMCSA/BEKE/MFA/NDAQ/OTIS/SGML/SYNA/UI/XYL/HCKT/NCTY/BOWFF, all signal_date 2026-06-12) re-fired wholesale on 06-13 and again on 06-15 -- an entire batch re-run, not isolated symbols. Two groups (CGBD 2026-06-10, BOWFF 2026-06-11) had DIFFERING stats across duplicate rows because the catalog had grown between fires -- those are not pure no-op re-runs, they're the same signal_date re-evaluated against a larger catalog.

**Fix applied 2026-06-29 (data-level only, code fix still OWED):** Dry-run script (read-only) grouped by `(ticker, signal_date, signal_class, chosen_horizon)`, flagged every group >1 row, kept the LATEST `fired_at` per group (not earliest -- the latest snapshot reflects the largest/most-representative catalog at fire time, which matters for the stats-differ cases). Tony reviewed the full group-by-group listing before authorizing. Execute script re-derived the grouping live (not from a cached id list, to avoid drift if new signals fired between dry-run and execute), backed up `buy_ledger.db` to a timestamped `.bak_dedup_<stamp>.db` first, verified the live duplicate count matched the dry-run count (33) before deleting -- would have aborted with zero changes on a mismatch. Result: 175 -> 142 rows, verified via before/after count reconciliation in the same script run. PASS.

**Still OWED:** A real uniqueness constraint or upsert-on-conflict in `insert_fired_signal()` (or a pre-insert existence check in `daily_evaluate_pipeline.py`'s ledger-record hook) so this can't recur. Until that lands, any operator re-run of a batch/symbol that already fired will re-duplicate.

**Pairs with:** M-046 (lambda tuning needs a clean, non-duplicated ledger -- this was caught specifically while checking ledger fill-status ahead of the ~2026-07-01 lambda-tuning window).

(Captured 2026-06-29)

### M-060 -- ledger_fill.py parsed signal_date as YYYYMMDD when it's stored as YYYY-MM-DD; every single fill attempt failed since the ledger was built

**Rule:** Two date conventions coexist in this hub: AddPattern filenames/fetch-window strings use YYYYMMDD, but the catalog and `fired_signals.signal_date` use ISO YYYY-MM-DD. A function touching a date string must check which convention its actual source column uses, not assume consistency hub-wide. `_try_fill_outcome()` was built assuming YYYYMMDD (the filename convention) but `signal_date` arrives as YYYY-MM-DD -- `datetime.strptime(signal_date, "%Y%m%d")` threw on every row, 100% failure rate, since 2026-06-03 (26 days, completely silent -- no one had looked at ledger-fill output until this session).

**Fix:** normalize once at function entry (`signal_date_norm = signal_date.replace("-", "")`) and use the normalized value for every downstream YYYYMMDD-expecting call in the function (fetch_price_history, the anchor_date comparison).

### M-061 -- yfinance returns MultiIndex columns even for a single-ticker download; row["Close"] silently returns a Series, not a scalar

**Rule:** Don't assume `yf.download(ticker, ...)` returns single-level columns just because only one ticker was requested -- the installed yfinance version returns `('Close', TICKER)`-style MultiIndex columns regardless. `row["Close"]` against a MultiIndex returns a sub-Series, which blows up downstream with "truth value of a Series is ambiguous" the moment it hits a scalar comparison (`anchor_close <= 0`). Flatten immediately after download: `if data.columns.nlevels > 1: data.columns = data.columns.get_level_values(0)`. Cost nothing when already single-level (no-op).

### M-062 -- query_unfilled() checked h5_return_pct, not h20_return_pct; a partial fill permanently removed a row from future fill attempts

**Rule:** When a row can be filled incrementally (h5 today, h7/h10/h15/h20 later as more trading days elapse), the "still needs work" query must check the LAST field to complete, not the first. Checking h5_return_pct IS NULL meant any row that got even a single horizon filled dropped out of `query_unfilled()` forever -- h7/h10/h15/h20 would never be revisited. Fix: check `h20_return_pct IS NULL` instead.

### M-063 -- ledger_fill.py's fetch window (+25 calendar days) could never reach the h20 horizon regardless of elapsed time

**Rule:** Calendar days and trading days are not interchangeable at the comment-author's assumed ratio. 25 calendar days yields ~17-18 trading days (5/7 ratio), but h20 needs `history[20]`, i.e. at least 21 trading days of data. The window was structurally incapable of ever reaching h20 -- not a timing issue, a math error in the original implementation. Fixed to +35 calendar days (~25 trading days, comfortable margin past 21 even with US holidays in the window). When computing a fetch/lookback window from a trading-day target, multiply by ~7/5 and add a holiday buffer -- never assume calendar days ≈ trading days.

### M-064 -- update_realized_outcome() was only ever called when ALL 5 horizons were filled; every partial outcome was computed correctly then silently discarded

**Rule:** `fill_ledger()`'s persist call lived inside the `if outcome.is_filled():` branch only. A partial outcome (e.g. h5/h7/h10/h15 ready, h20 still pending -- which, given the project's age, was the realistic case for every row) was computed in memory and then thrown away on every run, with no error, no log line at INFO level, nothing. Combined with the original blanket UPDATE in `update_realized_outcome()` (would have overwritten a partial fill with NULLs on any later run that didn't recompute every field), this needed two coordinated fixes: (1) persist on ANY new horizon data, not just a complete set; (2) use `SET col = COALESCE(?, col)` in the UPDATE so a None in the new outcome never clobbers an already-saved value from an earlier partial run.

**Discovery sequence (all in one 2026-06-29 session, found stacked on top of each other):** M-060 threw on every row -> fixed -> M-061 then threw on every row (different exception) -> fixed -> ran clean with "Filled 0/142", looked successful but wasn't -> traced through the code (not the log, since the bug produced no visible symptom) -> found M-062 and M-063 -> fixed both -> still "Filled 0/142" with real per-row INFO lines showing computed values -> found M-064, the real blocker -> fixed -> first real fills landed: h5=115, h7=97, h10=58, h15=2, h20=0 (h20 expected at 0 -- oldest signals hit their 20th trading day on the day of this fix, before market close). Four bugs were compounding; a clean run with no errors and a plausible-sounding "0 filled" log line was NOT evidence of correctness (pairs with M-054 -- a closure claim, or in this case a clean exit code, is not evidence).

**Pairs with:** M-046 (this is the ledger the lambda-tuning gate depends on -- it had never actually filled a single row before this session, despite "Phase 1-3 COMPLETE" being recorded in todo.md on 2026-06-03).

(Captured 2026-06-29)

### M-065 -- Typing a `.ps1` filename at a `cmd` prompt opens it in the associated editor instead of executing it; no execution occurs, no error is thrown

**Rule:** PowerShell scripts are not directly executable by typing their filename at a `cmd.exe` prompt the way a `.bat` is -- Windows resolves the file association instead (typically an editor, e.g. VS Code) and opens it for viewing/editing. No error appears in the console; the prompt simply returns, making it look like nothing happened rather than signaling a launch failure. The correct invocation from `cmd` (or as a launcher target) is explicit: `powershell -ExecutionPolicy Bypass -File "<path>\script.ps1"`. From a PowerShell prompt itself, `.\script.ps1` (or full path) executes directly -- the ambiguity is specific to invoking a `.ps1` from `cmd.exe` or via a bare filename.

**Failure mode captured 2026-06-30:** Tony ran `P_300_RunAllPatterns.ps1` from a `cmd` prompt by typing the filename. VS Code opened (visible in the pasted output via its startup log) instead of the script running -- no AddPattern activity, no log file written, no error message. Looked like a silent no-op rather than a launch-method mistake. Re-run with the explicit `powershell -ExecutionPolicy Bypass -File` form executed correctly.

**Distinguishing signal:** if a `.ps1` invocation produces editor/IDE startup log lines (extension host, storage service init, etc.) instead of script output, the file was opened, not run.

(Captured 2026-06-30)

### M-066 -- "N trading days have elapsed" claims must be computed against the actual calendar (holidays included), not estimated; a held-as-fact note can be wrong the same way a closure note can

**Rule:** A statement that a signal "hit its Nth trading day" on a specific date is a calculation, not an observation -- it must be derived by counting actual trading days (weekdays minus US market holidays) from the real signal_date, not estimated by eye. The same discipline M-054 requires for closure notes (verify, don't trust) applies to date-math claims embedded in lesson/todo entries.

**Failure mode captured 2026-06-30:** The 2026-06-29 M-064 capture stated DE/COHR (signal_date 2026-06-02) "hit their 20th trading day on 06-29." Recount: Jun 2 -> Jun 30 spans 21 weekdays, but Juneteenth (Jun 19, 2026, a Friday) is a federal market holiday -- 20 actual trading days through Jun 30, and Jun 30 itself hadn't closed at the time ledger-fill was run (15:53 ET). Real count: 19 completed sessions past the anchor close, h20 needs 20 sessions past anchor (21 total data points, index 0-20) -- short by ~2 sessions. `cli.py ledger-fill` run 2026-06-30 correctly returned `Filled 0 / 154` -- the code (M-060/061/063/064 fixes) is NOT broken; the prior day-count claim was. Expected real availability: after 2026-07-01 close, assuming no further holidays.

**Pairs with:** M-063 (calendar days != trading days, same confusion previously caught in code; this is the same error recurring in a human/session note instead).

(Captured 2026-06-30)

---

## Section 4 -- Open Items / Recent Corrections Not Yet Promoted

*(2026-06-16 status -- WO-P300-E1.001 IntelliScan stop integration SHIPPED. 4 files: intelliscan_reader.py v1.0 NEW (reads P_300_HistoryGrid_IntelliscanEvalParameters.xlsx from data/live/; returns support_1/support_2 per symbol; non-blocking when absent); signal_schemas.py v2.1 (atr_adjusted_stop, intelliscan_support_1, intelliscan_support_2 added to SignalV2 as Optional[float] = None; validator added); signal_emitter.py v2.1 (3 new optional params wired through _build_signal_v2_packet and emit_signal_packet); daily_evaluate_pipeline.py v1.18 (load_intelliscan() once at pipeline start; get_support_levels() per symbol; atr_adjusted_stop computed as max(is1, close - 1xATR) or ATR floor when is1 absent; all 3 fields passed to emit_signal_packet). Smoke test PASS: 12 symbols loaded, both support levels correct. M-052 added. WO-P115-E2.001 OPEN: same integration needed for P_115 -- separate session.)*

*(2026-06-12 status -- M-051 added: hardcoded success string anti-pattern captured in report_writer.py print_signal_report_clean(). The [OK] written to vault and ARCHIVE OK strings were scaffolded placeholders never replaced with real calls. print_signal_report_clean() needs its hardcoded status strings replaced with actual call results -- tracked as open work. WO-P300-E1.001 BACKLOG created: resistance lookup to replace VP predicted high as target formula.)*

*(2026-06-11 status -- Enhancement 2 gate-on prerequisites: report_writer smoke PASS (all 3 scenarios incl None-CE render); NFR-1 determinism replay PASS (CGBD BUY h=5, all 5 horizons identical across 2 runs, certainty_equivalent included). M-019 instance found and fixed in ledger_record.py: Unicode arrow U+2192 in logger.info f-string was triggering cp1252 UnicodeEncodeError on every BUY/WATCH ledger write; replaced with ASCII -> and converted to % formatting. Junk replay ledger entries (ids 41-42) deleted via cleanup script; fired_signals back to 40. One prerequisite remaining: lambda tuning against ledger (~2026-07-01).)*

*(2026-06-09 status -- Enhancement 2 (Certainty-Equivalent BUY gate) shipped observe-only; see todo.md. M-046 + M-047 added. Decision-flag surfacing added to INIT: SIP v3.0 -> v3.1 (Step 5 config.py grep + Step 6 Decision flags line + fail-fast row) and SKILL aligned (checklist line, SIP ref v3.1). M-048 added (filesystem:edit_file batches are atomic -- verify after every multi-edit batch). Catalog reconciled to live ground truth N=186 / 155 symbols / 060826catalog.db -- see todo.md reconciliation entry; corrects the stale N=156 closure, the never-real N=175 note, and the false "AVXL/CRK/HP FAILED" entry.)*

*(2026-06-08 status -- Enhancement 1 (P_300 -> P_400 SIGNAL_V2 signal packet) shipped. signal_emitter.py v1.1 -> v2.0 (routes via P_800 Hub interface write_to_vault SIGNAL_V2; no path construction, M-038). daily_evaluate_pipeline.py v1.14 -> v1.15 (Stage 5a gate BUY-only -> LEDGER_LOG_CLASSES (BUY, WATCH); fixed the v1.14 vault_root TypeError crash on every BUY). schemas_signal_packet.py now vestigial -- flagged for removal. M-045 added. COHR live BUY @ h=15 validated -> 2026-06-08_COHR_v2.0.json written. Architecture v2.7 Enhancement Log + Change Log updated. position_size=0 / asset_class=stock sentinel validated against P_800 SignalV2.)*

*(2026-06-03 status -- Phase 3 Ledger Calibration System COMPLETE & VERIFIED. Fired signals captured: COHR (BUY h=15 wr=70% n=20) + DE (BUY h=5 wr=95% n=20). Five critical errors fixed and documented as lessons M-040 through M-044. All import, schema, query, and logging issues resolved. Ledger DB ready for backfill and calibration workflows.)*

*(2026-05-31 status -- Catalog reconciled N=139 / 053026catalog.db. M-038 added (Hub interface). M-039 added (UTF-8 output). Gap 6 fixed in write_signal_to_obsidian.py v1.1/v1.2. Backfill complete: 89 notes corrected. P_800 Obsidian Note Standard v1.1 drafted. Pending: standard implementation (6 files), P_800 doc disk write.)*

*(2026-05-30 status -- M-037 formalized. Dead code cleanup complete. Evals: ARLP BUY, COTY WATCH, DOX BUY, DD WATCH, EQX WATCH.)*

*(2026-05-29 status -- M-036 added: Hub root bootstrap in python/application/ requires 5 x .parent. Fixed in daily_evaluate_pipeline.py v1.9. cli.py --clean flag routed through main() instead of run_daily_evaluate(). SIP v2.9 updated. NVDA PASS @ h=20 validated.)*

*(2026-05-29 status -- M-035 added: AI must verify python interpreter before issuing any python invocation to operator.)*

*(2026-05-28 status -- Feature ablation + threshold sweep: M-034 added. volume_zscore removed from SIMILARITY_FEATURES; BUY_MIN_Z_SCORE lowered to 0.0. Both changes in config.py v1.4 and v1.5. M-028 formally retired -- N=116 sweep completed. Re-evaluation trigger set at N=300+.)*

*(2026-05-21 status -- Pipeline A tooling: M-032 added; O-008 added to Section 2. M-033 added -- permanent operational rule.)*

*(2026-05-20 status -- Stage 9-followup: M-030, M-031, M-019 extension added.)*

*(2026-05-19 status -- Stage 7/8/9 SEAL: M-022 through M-029 added at lesson-level. M-028 retires at N>=50.)*

*(2026-05-18 status: M-016, M-017, M-018, M-019 STRUCTURALLY EMBEDDED in SKILL v2.5.)*

*(2026-05-13 status: All identified failures from the rebuild session were promoted to EC-060 through EC-067 in the architecture doc.)*

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
