# P_300 Lessons Log

**File:** `tasks/lessons.md`
**Status:** Live working document
**Last Updated:** 2026-07-12 (WO-P300-E3.001 Scanner Loop built + PEH-verified 7/7 -- 5 files: archive_scanner_file.py NEW, scanner_report_writer.py NEW, scanner_loop.py NEW, cli.py v1.11 +scanner-loop, config.py v1.12 +SCANNER LOOP section. Data-source decision resolved same-day: reuses IntelliScan's native crossover screen + existing bulk_grid_reader.py/bulk_pattern_detector.py unchanged, point-in-time only, STRICT-only, report-only (no catalog write). M-080 added: missing reports_dir override forced test monkeypatching, same family as M-075 -- fixed at the source, not just in the test. data/bulk/nightly_scan/ folder created; real nightly-export run is next, separate step.) | 2026-07-08 (WO-P300-E2.001 Bulk Extraction: spec reviewed, scan decoded from .isc, Phase 0 verified on SPY/AAPL/DE exports (VP backfills predictions only 5 yr, boundary 2021-07-14), config.py v1.9 shipped + PEH-verified 11/11. M-070 added: PEH is a two-file contract -- run_this.py + run_this_context.txt written together, always. PowerShell MCP wedged mid-session per M-030; recovery = Claude Desktop restart.) | 2026-06-29 (ledger-fill produced its first real output ever: 4 stacked bugs found and fixed in one session -- M-060 date format, M-061 yfinance MultiIndex columns, M-062 query_unfilled checked the wrong column, M-064 persist-only-on-full-fill discarded every partial outcome. M-063 widened the fetch window. Result: h5=115/h7=97/h10=58/h15=2/h20=0 fully real, verified via before/after counts. See M-060 through M-064.) | 2026-06-29 (Ledger dedup: 175->142 rows, 33 duplicates removed across 26 groups -- COHR fired 6x, an entire 06-12 batch re-fired wholesale on 06-13/06-15. M-059 added: insert_fired_signal() has no uniqueness guard; code fix still OWED. Backup saved before delete; live-recount safety check matched dry-run exactly.) | 2026-06-28 (AddPattern batch: 31/32 ingested clean, 1 rejected as true duplicate (DOCU, source_file_id=277) -- catalog 331->362 patterns / 245 symbols. DailyEval batch: 22/22 clean, 9 BUY/12 WATCH/1 PASS, first live run under config v1.8 z>1.0. M-058 added: failed ingests leave the source file in historical_patterns\, blocking re-runs until the operator removes it. Pairs with O-009.) | 2026-06-17 (M-051 REAL fix landed: report_writer.py v1.8 -- print_signal_report_clean() no longer hardcodes [OK] written to vault / ARCHIVE OK; gated on LEDGER_LOG_CLASSES, fabricated archive block removed. Paired daily_evaluate_pipeline.py v1.20 M-043 fix -- _obsidian_write() False return now logged. M-054 added: the 2026-06-12 todo.md/lessons.md closure note for this exact bug was never verified against the file -- bug ran live in production 2026-06-12 through 2026-06-17 undetected. Caught via operator-uploaded live DailyEval console log.) | 2026-06-16 (WO-P300-E1.001 IntelliScan stop integration SHIPPED. intelliscan_reader.py v1.0 NEW; signal_schemas.py v2.1 (3 new SignalV2 fields); signal_emitter.py v2.1; daily_evaluate_pipeline.py v1.18. Smoke test PASS: 12 symbols, both support levels correct. M-052 added. WO-P115-E2.001 OPEN -- same pattern needed for P_115.) | 2026-06-12 (M-051 added -- hardcoded success string anti-pattern; falsified functional test captured in report_writer.py print_signal_report_clean().) | 2026-06-11 (M-019 instance: ledger_record.py Unicode arrow fixed; NFR-1 + report_writer smoke PASS; Enhancement 2 gate-on 3/4 done.) | 2026-06-09 (Enhancement 2 shipped -- Certainty-Equivalent BUY gate. CARA exponential utility (Kochenderfer Ch. 6) computes a risk-adjusted CE return per horizon; gates BUY when CE_GATE_ENABLED=True. Shipped OFF (observe-only). config v1.7 + schemas_pipeline_b v1.3 + domain/utility.py v1.0 NEW + aggregator v1.1 + signal_classifier v1.1 + report_writer v1.7. M-046 + M-047 added. utility.py smoke PASS verified.) | 2026-06-08 (Enhancement 1 shipped -- P_300 -> P_400 SIGNAL_V2 signal packet via the P_800 Hub interface. signal_emitter v2.0 + daily_evaluate_pipeline v1.15. M-045 added. COHR live BUY validated -> packet written to TradeOrderManagement/signals/. Architecture v2.7 Enhancement Log + Change Log updated.) | 2026-06-03 SEALED (Phase 3 Ledger Calibration System COMPLETE. M-040 through M-044 added. Ledger verified: COHR + DE signals captured. Next: 20-day wait, then ledger-fill.)
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

## Working-State Doc Retention (WO-P000-E8.001)

This file is capped at ~40 live entries / ~70KB. When it crosses that,
the oldest / most-settled entries move to tasks/lessons_archive.md
(full text preserved, nothing deleted). First pass: 2026-07-22, 37
entries archived (12 already promoted into a SKILL.md, 3 self-superseded
by their own later entry, 8 promoted into CLAUDE.md as Locked
Decisions, 14 resolved code fixes with no later lesson citing them back).
See tasks/lessons_archive.md for the removed entries and
WO-P000-E8.001 for the retention standard.

---

## Section 1 -- Session Methodology Rules (Active)

### M-089 -- `db_utils.get_latest_catalog()` returns a plain `str`, not a `Path`
**Rule:** Other callers rely on the plain-`str` return for direct
`sqlite3.connect(f"file:{path}...")` use -- wrap in `Path()` before calling
any `Path`-only method (`.stat()`, `.name`) on it. Caught 2026-07-13 in a
diagnostic script; script-local bug, not a `db_utils.py` defect.

### M-090 -- Live catalog `symbols` table column is `ticker`, NOT `symbol`; the architecture doc's schema section is stale
**Rule:** `P300_System_Architecture_V1.1.md` Section 9.1's schema listing
(`symbols(symbol_id, symbol)`) does NOT match the real schema -- confirmed
2026-07-13 via a read-only `PRAGMA table_info` against the live
`071026catalog.db`, which shows `ticker`. That architecture doc is v1.1
dated 2026-04-20; the SIP pairs with a v2.7 that isn't the uploaded copy.
Never trust the architecture doc's schema section without a live
`PRAGMA table_info` check first -- same discipline as M-054, applied to
schema instead of task-closure claims.

(Captured 2026-07-13)

### M-001 -- "You write, I review" pattern
**Rule:** For all file deliveries (Python, docs, configs), the AI writes the file directly to its target Windows path via `windows-mcp:FileSystem`. The operator reviews. The AI never asks the operator to copy-paste code from chat. (Confirmed 2026-05-13.)

### M-003 -- Plan before write
**Rule:** Any task involving 3+ files or architectural decisions requires a written file plan with line-count estimates *before* any code is written. Wait for explicit operator approval.

### M-005 -- Match operator message length
**Rule:** Short user message -> short AI response. Substantive decisions warrant substantive answers; trivial pings get trivial replies. Never lecture. Never restate the operator's question.

### M-006 -- Honest accountability over defensive recovery
**Rule:** When the AI misses something, acknowledge it directly. No padding, no apology spirals. State what was missed, what's being corrected, and move on.

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

### M-013 -- Cross-field invariants in Pydantic v2 go in `@model_validator(mode="after")`
**Rule:** Pydantic v2 field validators run in declaration order and see only earlier fields. Cross-field invariants belong in `@model_validator(mode="after")`. (Identified 2026-05-14.)

### M-014 -- Validate config artifacts against a real source-data sample before commit
**Rule:** For any config claiming alignment with vendor data, run a verification pass against an actual example file BEFORE writing to the final location. (Identified 2026-05-14.)

### M-015 -- Live filesystem MCP reads override project attachments for `tasks/*.md`
**Rule:** When INIT loads `tasks/lessons.md` and `tasks/todo.md`, ALWAYS read via filesystem MCP (`filesystem:read_text_file`), NEVER trust project-attached versions. Attachments lag disk. (Identified 2026-05-15.)

### M-021 -- Pydantic v2 `model_copy(update=...)` skips re-validation
**Rule:** `model_copy(update=...)` does NOT run validators. Use full re-construction in validator negative tests. (Identified 2026-05-17.)

### M-024 -- Pipeline A filename date format is strict YYYYMMDD; no capture-date sanity check
**Rule:** Pipeline A does NOT check that capture date is not in the future or that target precedes capture. Double-check capture date before running `add-pattern`. (Identified 2026-05-18.)

### M-026 -- Date-validity pre-checks for date-driven pick lists
**Rule:** Validate every proposed date against weekends and US market holidays before publishing any date-driven pick list. Use `pandas.tseries.holiday.USFederalHolidayCalendar` + `weekday() < 5` check. (Identified 2026-05-18.)

### M-027 -- Cost-estimate discipline: measure or admit unknown, never extrapolate from feel
**Rule:** When asked for cost, token, time, or performance estimates, either (a) measure the actual value, or (b) state "unknown" with the specific reason. Never extrapolate from intuition. (Identified 2026-05-19.)

### M-029 -- Don't interpret domain data without confirming domain semantics
**Rule:** State what the measurement says (numeric, value-neutral). Only label features as "signal"/"noise" when domain meaning is confirmed. (Identified 2026-05-19.)

### M-030 -- `windows-mcp:PowerShell` + `python -c` with embedded code hangs reliably
**Rule:** Do not invoke `python -c "<embedded code>"` via `windows-mcp:PowerShell`. Hangs ~75-100% of attempts. Use `python script.py` instead. (Identified 2026-05-20.)

### M-031 -- File-size accretion crossing §8.4.2 is a signal to split, not a license to slim docstrings
**Rule:** When a file grows past 300 lines through legitimate accretion, split at a natural boundary. Don't compress docstrings. Current breaches: `schemas_pipeline_b.py` 408, `daily_evaluate_pipeline.py` 417, `report_writer.py` 373. (Identified 2026-05-20.)

### M-032 -- Windows CMD batch: `SETLOCAL ENABLEDELAYEDEXPANSION` + `!VAR!` breaks parser on this system
**Rule:** Do not use `SETLOCAL ENABLEDELAYEDEXPANSION` combined with `!VAR!` in Windows batch files on this workstation. Produces `: was unexpected at this time.` even on syntactically correct files. Use `%date%` string slicing for date; `goto` label pattern to break for loops. (Identified 2026-05-21.)

**Recurrence 2026-07-07 -- P_300_AddPattern.bat day-rollover copy silently no-op'd, undetected since the 2026-06-23 rebuild:** The 2026-06-23 rebuild of this file (after Tony accidentally overwrote it) claimed to implement the day-rollover catalog-backup copy "avoiding M-032's delayed-expansion trap," but the shipped version set `NEWCATALOG` and referenced `%NEWCATALOG%` inside the SAME parenthesized `if/else (...)` block without delayed expansion -- classic percent-expansion-at-parse-time bug, a different failure shape than M-032's original (that one was about `!VAR!` breaking the parser outright; this one is about `%VAR%` silently evaluating empty when set-and-used in the same block). `%NEWCATALOG%` evaluated to empty string on every new-day run since 2026-06-23 -- the "[BACKUP] New catalog day -- copying to" line printed with nothing after it, and `copy /y "...\%LATEST%" "...\"` (empty destination filename) silently failed with no errorlevel check. No data damage (ingest still correctly wrote to the single existing `062326catalog.db` via `db_utils.get_latest_catalog()`), but the intended daily-snapshot naming convention (`<mmddyy>catalog.db` per session) never fired across at least two 2026-07-07 AddPattern runs (and likely every session since 06-23 that crossed a day boundary). Caught when Tony asked why the catalog was still named `062326catalog.db` on 2026-07-07. Fixed by restructuring to the goto-label pattern M-032 already prescribes -- `NEWCATALOG` is now set in a top-level statement, not inside a parenthesized block, so `%NEWCATALOG%` re-expands correctly on each subsequent line without needing delayed expansion at all. **Generalized rule:** M-032 isn't just "don't use `!VAR!`" -- it's "don't set-and-use a `%VAR%` inside the same `(...)` block, period," since plain percent-expansion is parse-time-bound within a block regardless of whether delayed expansion is enabled. Any future `.bat` touching this project should be checked for this shape specifically.

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
- **Never** assume a downstream parser still matches a report/console format after that format changes -- a fixed-column regex fails silently (None, no exception) rather than throwing when a column is added (M-067)
- **Never** trust a --clean batch's silence as proof every emit succeeded (or failed) -- logging.disable(logging.WARNING) spans the whole run and swallows any function reporting only via the logging module; if it doesn't also print(), it's invisible either way (M-068)
- **Never** pass a decimal-fraction stat (mean_return_pct, or anything in M-020's decimal-space convention) into a %-formatted string without the *100 scaling applied at that call site -- each consumer scales independently, there's no single place it happens automatically (M-068)

---

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

### M-063 -- ledger_fill.py's fetch window (+25 calendar days) could never reach the h20 horizon regardless of elapsed time

**Rule:** Calendar days and trading days are not interchangeable at the comment-author's assumed ratio. 25 calendar days yields ~17-18 trading days (5/7 ratio), but h20 needs `history[20]`, i.e. at least 21 trading days of data. The window was structurally incapable of ever reaching h20 -- not a timing issue, a math error in the original implementation. Fixed to +35 calendar days (~25 trading days, comfortable margin past 21 even with US holidays in the window). When computing a fetch/lookback window from a trading-day target, multiply by ~7/5 and add a holiday buffer -- never assume calendar days ≈ trading days.

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

### M-070 -- PEH handoff staged with only half the pair: run_this.py overwritten but run_this_context.txt left stale from a prior project's session

**Date:** 2026-07-08
**Trigger:** Operator ran the staged config.py v1.9 verification (11/11 PASS) but flagged that `verify\run_this_context.txt` still described a long-closed P_920/SHEL vault-write test with its own DO-NOT list -- context and script disagreed. Nothing wrong executed (the script was the intended one), but the operator had no reliable way to know which task the folder represented, and a stale DO-NOT list could steer a future session incorrectly.

**Root cause:** The PEH pattern is a two-file contract -- `run_this.py` + `run_this_context.txt` written together, always. This session wrote only the script.

**Rule going forward:** Every PEH staging writes BOTH files in the same pass, and the context file states: task, project, WO reference, what the script does, any DO-NOTs, and status. When reading a verify folder at session start, treat script/context disagreement as stale-state and reconcile before running anything.

**Status:** Applied 2026-07-08 (context file rewritten to match the config check; rule active for all future PEH handoffs).


### M-071 -- PEH verification script's own sys.path setup assumed a flat python/ layout that doesn't match the project

**Date:** 2026-07-08
**Trigger:** WO-P300-E2.001 session widened schemas.py's ColumnMapEntry.type (v2.2 -> v2.3, shared live-Pipeline-A file) and staged a PEH verification script to confirm the change didn't break live ingest before building further bulk-pipeline files on top of it. First run failed at `import vp_xlsx_reader` -- the script's sys.path.insert only added `python/`, but `vp_xlsx_reader.py` lives under `python/infrastructure/`. Not a bug in the code under test; a bug in the verification script itself.

**Root cause:** Assumed a flat `python/` layout (matching where `config.py` and `schemas.py` sit) without checking where the specific module being verified actually lives. `python-project-architecture`'s layer folders (`domain/`, `infrastructure/`, `application/`) mean any PEH script that imports a layered module needs each relevant subfolder on sys.path, not just the project's `python/` root.

**Fix:** Added `python/infrastructure` to sys.path alongside `python/` -- only the sys.path insert lines were touched, no change to the checks, assertions, or data being verified (per the handoff rule: fix the harness, never the thing it's testing, without flagging it as a separate change).

**Generalized rule:** Before staging any PEH script that imports a layered module (anything under `domain/`, `infrastructure/`, or `application/`), check that module's actual folder first rather than assuming `python/` covers it. A verification script's own import setup is itself something to get right before trusting its PASS/FAIL output -- a failure at the import stage says nothing about the thing being verified.

**Status:** Applied 2026-07-08 (schemas.py v2.3 ColumnMapEntry.type widening confirmed safe against live Pipeline A -- 5/5 PEH checks PASS after the sys.path fix).


### M-072 -- VP ROC% field can render as literal infinity ('∞'), not corrupted data

**Date:** 2026-07-08
**Trigger:** WO-P300-E2.001 bulk_grid_reader.py, first real-data test run against 10_Pattern_SPY.xlsx (2,512 bars), failed at row 56: `Cannot coerce '∞' to float`. Investigated rather than assumed-corrupt -- confirmed via direct cell read that VP itself writes the unicode infinity symbol into the ROC% column when the underlying rate-of-change calculation divides by a value near zero. Real VP output, not a bad export.

**Root cause:** `_coerce_cell`'s float branch called bare `float(value)`, which does not parse the unicode `'∞'` character (or `'-∞'`) -- Python's float() only accepts ASCII `'inf'`/`'infinity'` spellings.

**Fix:** Added an explicit string-match branch before the generic `float()` call: `'∞'`/`'inf'`/`'Infinity'` -> `float('inf')`, negative forms -> `float('-inf')`. `roc_pct` is not read by any of the 9 detection conditions, so an infinite value there is harmless downstream -- confirmed before treating this as low-risk to fix this way rather than rejecting the row.

**Generalized rule:** Any VP field derived from a ratio/percent-change calculation (ROC%, and potentially others not yet hit) can legitimately render as infinity when its denominator approaches zero. Float-coercion code touching such fields should handle the unicode infinity symbol explicitly rather than assuming a parse failure means bad data -- verify against the real cell value before writing a rejection path.

**Status:** Applied 2026-07-08 (bulk_grid_reader.py v1.1). Full 2,512-bar SPY file parses clean end-to-end after the fix; verified via direct test run, not just unit-level coercion checks.


### M-075 -- A function that accepts scratch-path overrides for SOME of its I/O but not all of it is a test-isolation trap; every persistent side-effect needs its own override parameter

**Date:** 2026-07-08
**Trigger:** `run_bulk_extraction()` v1.0/v1.1 accepted `master_db` and `temp_db` as overridable parameters (used correctly by a PEH test script to point at scratch DBs) but had NO parameter for the checkpoint file path -- it always read/wrote the real `BULK_CHECKPOINT_FILE` from `config.py` regardless of what DB paths were passed. A test run (itself triggering the real M-074 bug, causing every hit to be rejected) wrote `5_Pattern_SPY.xlsx` into the LIVE checkpoint as "completed" with 0 detections. Every subsequent test run -- including after the M-074 fix landed and would have worked -- silently skipped the file because the live checkpoint said it was already done. This produced zero per-hit log output and looked exactly like "the sweep found nothing," a materially different and more confusing symptom than the real bug.

**Root cause:** Partial overridability is worse than none: a caller who successfully overrides `master_db`/`temp_db` reasonably assumes ALL persistent state for that run is isolated, and has no signal that a third side-channel (the checkpoint) is still writing to the real filesystem location. The function's own signature was the misleading claim here -- it looked test-safe and wasn't.

**Fix:** Added `checkpoint_path: Path = BULK_CHECKPOINT_FILE` as a fourth parameter, threaded through `_load_or_init_checkpoint`/`_save_checkpoint` (both changed from optional-default to required-positional internally, so a future internal call site can't silently fall back to the live path by omission). Docstring now states explicitly: a caller overriding master_db/temp_db MUST also override checkpoint_path or risk live-checkpoint pollution.

**Generalized rule:** Before treating any function as safely testable via path overrides, enumerate EVERY persistent side effect it has (every file write, every DB write, every append), not just the ones already exposed as parameters. A function is only as test-isolated as its least-overridable side effect. This applies especially to checkpoint/resume files, which are easy to overlook because they're metadata about the run rather than the run's primary output.

**Recovery note:** No live-checkpoint cleanup was needed in this instance -- confirmed via direct file check that `bulk_extract_checkpoint.json` does not exist on disk, meaning no real bulk-extraction run has ever happened yet (cli.py's `+bulk-extract` subcommand and `P_300_BulkExtract.bat` are both still unbuilt per the WO's own todo.md sequencing). Had a real run already occurred, this bug would have required manually editing the live checkpoint to remove the false completion entry before the fix could be trusted.

**Pairs with:** M-017 (this hub's general instinct that ground truth must be reconcilable -- a checkpoint that silently disagrees with reality is the same failure shape as a stale tracking doc), M-054 (verify claims against the actual file, which is exactly how this was traced -- confirmed the live checkpoint's absence directly rather than assuming the "safe, no cleanup needed" claim was correct).

(Captured 2026-07-08)

### M-073 Recurrence -- 2026-07-10 (WO-P300-E2.001, 7-file IntelliScan run verification)

Same failure as M-073 above, but the real cause was worse than "create_file silently no-ops on an existing path": Claude's `create_file`/`str_replace` tools in this app are sandbox-local -- they do not write to the real Windows machine at all, regardless of what Windows path string is passed. Claude staged `run_this.py` + `run_this_context.txt` for a bulk-extract verification using `create_file` with real `C:\Users\Trader\...` paths; both calls "succeeded" but wrote to Claude's own ephemeral container, never touching `Agentic-Hub-Governance\verify\` on the actual machine. Tony/Claude Code then ran against the real (stale, 2026-07-09) `run_this_context.txt` still sitting there from the prior run, correctly flagged it as internally inconsistent with the actual console output, and substituted its own ad hoc diagnostic script rather than trusting the stale one. Underlying DB numbers were still independently verified correct (bars=instances*20, labels=instances*5, per-symbol sum matched total-minus-baseline exactly) -- no data-integrity harm -- but the audit-trail file was wrong until corrected after the fact via `windows-mcp:FileSystem` write+overwrite=true, confirmed via `mode=info` mtime change.

**Rule:** For any file under `C:\Users\Trader\AI-Agent-Learning-Hub\...` (i.e. the real project, not scratch text shown only in chat), Claude must use `windows-mcp:FileSystem` (mode=write, overwrite=true for existing paths) -- never `create_file` or `str_replace`, which are sandbox-only regardless of the path string given to them. Always follow with `mode=info` to confirm mtime changed before treating a PEH file as staged. This is a stricter, corrected version of the original M-073 fix, not just a repeat of it.


### M-059 -- CODE FIX SHIPPED, 2026-07-10 (closes the "still OWED" item)

**Fix:** `ledger_db.py` -- `_init_schema()` adds `CREATE UNIQUE INDEX IF NOT
EXISTS idx_fired_signals_unique ON fired_signals(ticker, signal_date,
signal_class, chosen_horizon)`. `insert_fired_signal()` changed from a bare
`INSERT` to `INSERT ... ON CONFLICT(...) DO NOTHING`; on conflict (rowcount
0), logs at INFO and returns the existing row's `ledger_id` via a lookup
`SELECT` instead of inserting a duplicate. Added `import logging` (file had
none before). File grew 187 -> 241 lines, still under the 300 limit;
`insert_fired_signal()` itself stays under 50 lines.

**Pre-flight (2026-07-10, before writing the fix):** confirmed live
`buy_ledger.db` had 0 duplicate groups across all 230 rows (last data-level
dedup was 2026-06-29, 175->142; ledger had grown 88 rows since with no
re-check until now) -- safe to add the UNIQUE index with no migration step.

**Functional verification (2026-07-10):** 4-case smoke test against an
isolated `tempfile.mkdtemp()` throwaway DB (confirmed via
`LedgerDB(db_path=tmp_db)`, never opened `BUY_LEDGER_DB`) -- exact-duplicate
insert absorbed into the same `ledger_id` with row count staying flat;
inserts differing only in `chosen_horizon` or only in `signal_class`
correctly got new rows. PASS on first run, no fix cycle needed.

**Result:** M-059 is closed at the code level now, not just the one-time
2026-06-29 data cleanup. Any future re-run of a batch/symbol that already
fired will silently return the existing `ledger_id` instead of duplicating.
Pairs with M-046 -- the ledger lambda-tuning depends on stays clean by
construction going forward, no more periodic dedup passes needed.

(Captured 2026-07-10)


### M-079 -- A mechanically-detected pattern is not a curated pattern; corpus composition is a calibrated input, not just data volume

**Date:** 2026-07-10
**Trigger:** WO-P300-E2.003 staging merge of 495 STRICT bulk patterns into the 508-pattern live analog pool dropped walk-forward BUY win rate 68.8% -> 63.6% while nearly doubling BUY volume (157 -> 316). Promotion correctly withheld -- the staging-eval-before-promote gate (decision 2) did exactly its job. CIEN head-to-head then explained WHY: manual and STRICT detection have EQUAL precision (80%/80% into >=15% risers on real data) but catch DIFFERENT phases -- the detector fires at crossover ignition (condition 1), Tony's picks are mid-trend continuation entries (condition 1 failed on all 5 of his picks, including all 4 winners). Merging them into one analog pool mixes two different setup populations under thresholds (M-034) calibrated for only one of them.

**Generalized rules:**
1. Never merge a mechanically-detected corpus into a human-curated analog pool without a staging-copy eval comparison first -- and treat the comparison as the decision, not a formality. Detection-rule conformance is a proxy for setup quality, not the thing itself.
2. When two signal sources have equal precision but different coverage, the right integration is usually a FUNNEL (breadth source feeds the precision gate) not a UNION (both dumped into one pool). Scanner -> eyeball -> catalog preserves both edges; merge destroys the curation edge.
3. A validation gate that fires (blocks a promotion) is a success, not a failure -- log the numbers that fired it, don't work around it.

**Pairs with:** M-034 (threshold calibration is corpus-specific), WO-P300-E2.001's original merge deferral (the isolation that made this test possible), WO-P300-E2.003 closure state (bridge built, verified, parked).

(Captured 2026-07-10)


### M-080 -- A function safely testable via ONE path override still needs an override for EVERY persistent write it makes; a missing one forces the test to monkeypatch module constants instead

**Date:** 2026-07-12
**Trigger:** WO-P300-E3.001 Scanner Loop, first build. `run_scanner_loop()` v1.0 accepted `input_dir` as an override but hardcoded its report write via `write_scanner_report(hits)` -- no `target_dir` passed, so it always wrote to production `SCANNER_REPORTS_DIR`. The first PEH run (Claude Code) caught this before it happened: the test needed a scratch report location and, finding no parameter for it, had to monkeypatch `scanner_report_writer.SCANNER_REPORTS_DIR` at the module level to avoid writing a real file into `outputs/reports/scanner/` during a scratch-data test.

**Root cause:** Same shape as M-075 (bulk_extract_pipeline.py's missing checkpoint_path override) -- a function partially overridable looks fully test-safe to a caller who only checks the one parameter they need, until a second persistent side effect turns out to have no override at all. Here it was the report write; in M-075 it was the checkpoint write.

**Fix:** Added `reports_dir: Path | None = None` to `run_scanner_loop()`, threaded to `write_scanner_report(hits, target_dir=reports_dir)`, plus a matching `--reports-dir` CLI flag on the `scanner-loop` subcommand. PEH test updated to pass the real parameter instead of monkeypatching the module constant -- monkeypatching was a symptom of the gap, not a valid permanent test pattern once the real fix exists.

**Generalized rule:** Before treating any orchestration function as test-safe because it accepts a path override, enumerate every persistent write it makes (DB writes, checkpoint files, report files, archive writes) and confirm each has its own override parameter -- not just the one the current test happens to need. A function is only as test-isolated as its least-overridable side effect (restating M-075's rule, now confirmed as a recurring pattern across two different WOs, not a one-off).

**Companion catch, same PEH pass (cosmetic):** `config.py`'s new SCANNER LOOP docstring changelog entry contained `E:\ -- confirmed existing` -- an unescaped backslash-space is not a valid Python escape sequence, producing a `SyntaxWarning` on every import. Fixed by escaping to `E:\\`. Harmless (warning only, not an error) but worth catching before it accumulates -- any Windows path segment written inside a docstring or string literal needs the same escaping discipline as one written inside code.

**Pairs with:** M-075 (identical root cause, different WO -- checkpoint_path there, reports_dir here; this entry exists specifically to mark the pattern as recurring, not novel), M-054 (a PEH pass that comes back PASS without this kind of scrutiny is not the same as one that actually verified test isolation).

(Captured 2026-07-12)


### M-081 -- Don't pre-exclude a population based on an unproven schema assumption when the project already has an empirical gate to measure it

**Date:** 2026-07-12
**Trigger:** WO-P300-E3.002 pattern_miner.py v1.1 capped screening at the
catalog's existing 20-trading-day horizon (max of FORWARD_HORIZONS),
reasoning that a pattern selected for a move taking longer than that
would be "mismatched" with its own stored forward_labels (which only
cover h5-h20). Real validation data showed 16 of Tony's own historical
picks -- several of his cleanest winners (LMT +15.4% in 87 trading
days, SPY +15.3% in 89, GOOGL +24.4% in 94) -- would have been
permanently excluded by that cap. Tony challenged it directly: "why
would we do that unless h20 is proven not a reliable measure."

**Root cause:** The objection sounded structural ("the schema only
stores h5-h20") but wasn't actually about data integrity --
forward_labels are ALWAYS computed honestly for whatever anchor gets
selected, regardless of why it was selected; nothing would have been
fabricated or mismatched. The real concern (does including
later-outcome patterns dilute short-horizon win-rate stats) is an
EMPIRICAL question, and this project already has a purpose-built
mechanism for exactly that class of question: the M-079 staging eval
gate (build a staging copy, run walk-forward comparison, promote only
if it holds up). Capping the miner's screening window pre-decided the
empirical question in code instead of routing it to the gate designed
for it -- the same category of error M-079 itself was created to
prevent, just occurring one step earlier in the pipeline (at the
screening/inclusion stage instead of the promotion stage).

**Fix:** pattern_miner.py v1.2 -- screening extended to
MINE_MAX_SCREEN_DAYS=180 (~Tony's original "6-9 month" framing).
Stored forward_labels remain h5-h20 only, computed exactly as before,
no schema change. MinedCandidate gained `standard_horizon: bool` so
extended finds stay visibly distinguishable in every downstream report
and CSV -- transparency instead of exclusion. The actual precision
question (does this population help or hurt) is left to the M-079
gate this WO's Phase 2 already requires, unchanged.

**Generalized rule:** When a proposed exclusion is justified by "the
downstream schema/consumer only handles X" rather than by "this would
produce incorrect or fabricated data," check whether the project
already has an empirical gate designed to answer exactly that
precision/composition question (M-079's staging-eval pattern). If it
does, route the question there instead of encoding an assumption in
code -- an untested assumption dressed as a structural constraint is
still just an assumption, and this project's whole governance model
(E2.003's rejection was MEASURED, not presumed) exists specifically to
catch that distinction.

**Pairs with:** M-079 (the staging-eval gate this correction routes
the real question to), M-054 (an unverified claim -- here, "h20 is a
sufficient/reliable measure" -- is not evidence just because it sounds
plausible or matches the existing schema).

(Captured 2026-07-12)


### M-083 -- A per-item screen + post-hoc dedup cannot correctly identify "the launch bar" inside a persistent trend; only a sequential consume-the-window scan can, and no dedup-window value fixes it

**Date:** 2026-07-12
**Trigger:** WO-P300-E3.002 pattern_miner.py v1.0-v1.3 all shared the
same architecture: screen every bar independently ("does this bar see
a 15%+ move somewhere in its own forward window?"), then collapse
overlapping qualifying bars into one "launch" via a dedup window.
M-082's fix (cap the dedup window at 20 trading days) reduced but did
not solve the problem -- re-validation still landed at 18/84 (21.4%),
not the ~29-45 range multiple fix iterations had targeted. Tracing
LMT 2025-09-02 (Claude Code, before reporting the number) found the
real cause: during LMT's unbroken ~2.5-month uptrend (2025-07-07
through 2025-09-09), essentially EVERY bar independently qualifies --
each one genuinely sees a real 15%+ move somewhere in its own forward
window, because they're all riding the same underlying move. Dedup
can only ever land on whichever bar the suppression-window arithmetic
happens to leave unswallowed -- a mechanically arbitrary choice among
many equally-valid bars, not a measure of which one is "the" launch.
Tony's actual pick (2025-09-02, a bigger and faster move than the bar
dedup happened to keep) got swallowed by an earlier bar's suppression
window purely by arithmetic coincidence.

**Root cause:** The screening question itself ("will price eventually
move 15%+ from here") has no way to distinguish a true launch bar from
any other bar riding the same trend -- both are equally, genuinely
true. No dedup-window formula operating AFTER an unbounded per-bar
screen can recover that distinction, because the information needed
to make it was never computed -- dedup is post-hoc cleanup on an
already-lossy signal, not a fix for the signal itself. This is a
different class of problem from M-082 (a parameter's range change
breaking a downstream formula) -- M-082 was a real coupling bug with a
parameter fix; this is the per-bar-screen architecture being wrong at
the design level, which no parameter within that architecture can
correct.

**Fix (Tony's design, proposed directly, 2026-07-12):** Replaced the
screen-everything + dedup architecture with a sequential cursor scan
per class. Walk a cursor forward through eligible bars; at each
position, check for a qualifying move (standard horizons, then
extended search); on a match, record it and JUMP the cursor to
`match_idx + horizon_days + 1` -- consuming the ENTIRE window that
proved the move before ever screening a bar inside it as a candidate.
Run independently per class so an unrelated breakdown can still
overlap in time with an uptrend elsewhere. This makes non-overlap
STRUCTURAL (a cursor physically cannot revisit consumed bars) instead
of an approximation applied after the fact -- and it naturally
produces MULTIPLE anchors through a long trend, matching how Tony's
own ground-truth picks actually cluster (several symbols show 3-6
distinct manual picks within a few months of each other), rather than
collapsing an entire trend into one over- or under-suppressed anchor.
pattern_miner.py v1.4.

**Honest limitation, stated in the code, not hidden:** even the
corrected algorithm cannot guarantee landing on the EXACT bar Tony's
eye picked within an unbroken qualifying stretch -- outcome-only data
genuinely cannot distinguish a technically-real launch from an
adjacent, also-technically-real one a few bars over. Fully resolving
that would need a technical/setup signal (e.g. the existing
9-condition crossover detector from WO-P300-E2.001) layered on top of
the outcome screen, not a purely outcome-based fix. Flagged for
future validation results rather than papered over.

**Generalized rule:** When a per-item screen followed by a dedup/
cleanup step keeps producing wrong results across multiple parameter
fixes (M-075's checkpoint override, M-080's report path, M-082's dedup
cap were all real, correct, narrow fixes -- and the underlying number
still didn't move enough), stop tuning the cleanup step and ask
whether the screen itself is the wrong shape for the problem. A
symptom that survives several genuinely-correct narrow fixes is a
signal to escalate to a design question, not a signal to fix harder
in the same place. In this case, the operator (who understands the
actual real-world process being automated) proposed the correct
redesign directly -- a reminder that when Claude's own iterated fixes
aren't converging, the person who does the task manually may already
know the right algorithm shape.

**Pairs with:** M-082 (the immediately preceding fix in the same file
-- correct but insufficient, which is what surfaced this deeper
issue), M-079 (mechanically-detected "qualifying" is not the same as
a curated, meaningful pick -- same family of lesson, here applying to
a single symbol's bar-by-bar screen rather than corpus composition).

(Captured 2026-07-12)


### M-084 -- An aggregate correlation (density vs. a plausible variable) can't discriminate a real phenomenon from a bug that mimics it; check the distribution, not just the average

**Date:** 2026-07-12
**Trigger:** WO-P300-E3.002 pattern_miner.py v1.6 (same-class re-arm)
raised ground-truth hit rate 45.5% -> 86.4% but also produced 16,146
extra candidates across 30 symbols. Claude Code's per-symbol
candidates/100-bars table showed density correlating cleanly with
independently-known stock volatility (ASTS/BOIL/MSTR/ARDX -- volatile
names with short 3-yr grids -- at the top; PCAR/ITW/AME/ICE/LMT/SHW --
boring industrials -- at the bottom) and argued this supports "the
miner is finding real moves, not over-generating." The correlation is
real, but it does not settle the question: "genuinely volatile stocks
have more real 15%+ moves" and "same-class re-arm has reintroduced
per-bar re-triggering on the names most likely to have some qualifying
move within reach of almost every bar" BOTH predict the exact same
density-correlates-with-volatility pattern. An aggregate statistic
that's consistent with two different hypotheses can't be used to pick
between them.

**Root cause:** A plausible-sounding aggregate explanation ("the
volatile stocks are on top, the boring ones are on bottom, that's
exactly what you'd expect") reads as confirmation the same way a clean
exit code or a passing test suite does -- but neither actually checked
the mechanism. The discriminating number was one level down:
average bar-gap between same-class candidates
(`eligible_bars / candidate_count`). ASTS uptrend ~1.11 bars and BOIL
breakdown ~1.15 bars mean a new "launch" on essentially every
consecutive trading day -- no real stock produces that as distinct,
human-recognizable events, regardless of how volatile it genuinely is.
PCAR (~33.7 bars) and LMT (~60.8 bars) look like real, weeks-apart
launches by the same measure. Both symbol groups fit the "density
correlates with volatility" story; only the gap distribution separates
a real result from a reintroduced bug.

**Generalized rule:** When validating an algorithm's output density or
count against real-world plausibility, don't stop at an aggregate
statistic (a total, a per-symbol average, or a correlation with some
plausible explanatory variable) even when it produces a clean,
satisfying story. Ask explicitly: does this correlation actually rule
out the alternative hypothesis, or is it equally consistent with both?
If equally consistent, compute or request the underlying distribution
-- for any sequential/scanning algorithm specifically, the gap between
consecutive same-class outputs is usually the number that discriminates,
since a reintroduced per-item-qualification bug and a genuine
high-frequency real phenomenon can produce IDENTICAL aggregate density
while differing completely at the distribution level (back-to-back
vs. genuinely spread out).

**Status:** RESOLVED, 2026-07-13 -- matched-window confound check confirms
REAL, ISOLATED DENSITY, not an artifact. A corpus-wide diagnostic (all 40
files, full audit-agent self-check on every run -- 80 total audit passes,
all clean) did exactly what this lesson called for: checked the underlying
distribution instead of trusting the aggregate correlation. Two findings,
in order:

1. Full-corpus density table (40 symbols, real bar counts): BOIL 2.44,
   ASTS 2.53, MSTR 2.92, ARDX 3.59, CRK 3.77 -- a clean break from
   everything else (9.07-51.27). But those 5 are also the only 753-bar
   (~3yr) files in the corpus vs. ~2513-bar (~10yr) for the rest -- a
   real confound (shorter total bars mechanically compresses avg_gap =
   total_bars/candidate_count even at an identical candidate rate),
   flagged explicitly rather than glossed over.
2. Matched-window re-check: all 35 long files truncated to the same
   753-bar window (most recent, ascending-order bars[-753:]) and
   re-run through mine_bars() + a full self-audit. Verdict: the crowded
   five still rank 1-5 of 40 on the matched window -- their positions
   didn't move. The gap to the nearest competitor (INTC, 5.02) WIDENED
   relative to the original ranking, not narrowed. Zero truncated long
   symbols matched or beat the crowded five's own worst density (3.77).

**Conclusion:** BOIL/ASTS/MSTR/ARDX/CRK are genuinely, structurally denser
than every other symbol in the corpus, independent of window length --
not a bar-count artifact, not this same lesson's own re-triggering-bug
hypothesis. A density-based pre-filter for Phase 2 is justified by this
diagnostic's own stated success criteria. Design of that pre-filter
(threshold, flag-vs-exclude) is a separate, not-yet-made decision -- this
resolution closes the empirical question only, not the design question.

Original open status (superseded, kept for record): Open, not yet resolved
-- this lesson exists to prevent accepting the volatility-correlation
explanation on its own strength before the raw candidate-date-list /
gap-histogram check (staged as next session's PEH task) comes back. See
todo.md 2026-07-12 entry for full validation history (v1.5/v1.6, Round
1/Round 2 hit rates) and the specific next step.

**Pairs with:** M-083 (same file, same underlying per-bar-qualification
failure mode -- this lesson flags that the same-class re-arm fix built
to reduce it may have reintroduced a scoped-down version on the most
volatile names), M-064 (a clean/plausible-looking result is not
evidence of correctness without checking the actual mechanism -- same
principle, here applied to an aggregate statistic instead of an exit
code).

(Captured 2026-07-12)


---

### M-087 -- v2.0's crossover-gated eligibility model cannot catch a qualifying move that completes BEFORE its own crossover confirms

**Found:** 2026-07-13, WO-P300-E3.002, part 16 diagnostic (eligibility + outcome trace at the real crossover bar for BLK/NVDA/TECK, the 3 anchors part 15's M-086 date-attribution check left unexplained).

**BLK 2026-02-23 (traced case):** the qualifying breakdown move (-15.71% over 7 bars) is anchored at the bar immediately BEFORE the breakdown crossover -- that bar is still in UPTREND regime (`bars_since_crossover=7`, direction=uptrend), so `_is_eligible(breakdown)` is correctly `False` there (eligibility hasn't opened yet). By the crossover bar itself (`bars_since_crossover=0`, eligible=True), the move has already substantially played out and no longer clears 15% from any eligible bar onward. This is not a bug in `_is_eligible` or `_qualifies_for_class` -- both are working exactly as designed. It is a genuine scope boundary of the v2.0 architecture: outcome is always measured STRICTLY FORWARD from an eligible (already-crossed-over) bar, so a move that leads its own confirming crossover by more than a bar or two is structurally unreachable, by construction, regardless of search radius or resolve_pick logic.

**NVDA 2026-05-05 and TECK 2026-05-20 (traced, different shape):** no qualifying move in EITHER direction, at any standard or extended horizon, anywhere in a window around their real crossover bar. Nearest actual `mine_bars()` candidates belong to unrelated, earlier crossover cycles -- not near-misses. These two do not show BLK's "move precedes eligibility" pattern; they simply have no traceable >=15% hi/lo-range move near the ground-truth date under any interpretation checked. Closer in kind to the AME/PCAR/SHW OUTCOME-INVALID bucket (consistent every round this session) than to a `pattern_miner.py` defect -- the apparent earlier "match" for these two was itself an artifact of the same M-086 mechanism (an outcome-only search finding SOME qualifying move nearby without requiring that direction's own crossover to be active), just without a clean later crossover to reattribute to.

**Rule:** a crossover-gated eligibility model (measure outcome only from a confirmed trend-state bar) has an inherent one-directional blind spot -- it can miss real moves that precede their own confirming signal. Whether to widen eligibility to allow a bounded look-back before the crossover (catching BLK-shaped cases) is a real architecture decision, not a bug fix -- explicitly not made in this session, Tony's call if pursued.

**Session-final ground-truth accounting, all 84 anchors individually resolved, zero unexplained:** 77 HITS (91.7%) + 3 confirmed OUTCOME-INVALID (AME/PCAR/SHW) + 1 BLK (M-087 boundary case) + 2 NVDA/TECK (M-087, OUTCOME-INVALID-shaped) + 1 BAC (marginal/hairline, separately flagged, undiagnosed further) = 84.

---

### M-086 -- An outcome-only fallback that ignores WHEN a direction's own crossover occurred will misattribute a later, unrelated crossover's outcome to an earlier bar

**Found:** 2026-07-13, WO-P300-E3.002, part 14 diagnostic (bar-by-bar mtdiff trace on 12 of part 13's 13 real misses).

**What happened:** `resolve_pick_widened`'s tier-2 fallback (part 13) accepted ANY direction's qualifying 15% move within +/-2 bars of a pick's target date, without requiring that direction's own MT crossover to have occurred AT OR BEFORE the probed bar. Checked bar-by-bar for all 12 direction-mismatched real misses: every single one anchors on a bar still in the OPPOSITE mtdiff regime, with the resolved direction's actual crossover occurring 2-9 trading days LATER (BLK +5, CRK +3, DE +7, DVN +9, HAL +8, NVDA x2 +3, TDC x2 +4/+6, TECK x2 +2/+3). Tier-2 was structurally guaranteed to do this: any probe where the searched class != that probe's own inferred direction (`xdir_p`) is, by definition, a bar where that class's crossover has not (yet) happened there.

**Root cause, generalized:** an outcome-only search ("does a qualifying move exist nearby, in either direction") that doesn't also require the resolved direction's own trend-state to actually be active at the resolution point will silently borrow a DIFFERENT, later trend's outcome and misattribute it backward. This is not a `pattern_miner.py` bug -- v2.1's crossover-gated `mine_bars()` never made this mistake, because eligibility (Section `_is_eligible`) already enforces direction-matches-current-crossover as a hard gate. The bug was specific to the VALIDATION script's tier-2 fallback, which had no equivalent gate.

**Rule:** any resolution/matching heuristic that accepts a qualifying outcome for a class must also verify that class's own state-defining condition (here: crossover) held at or before the anchor point -- an outcome check alone is not sufficient, regardless of how tight the search radius is. Widening search radius (parts 11-13) cannot fix this class of bug; only adding the temporal gate can.

**Not yet resolved:** whether these 12 anchors are simply mis-dated relative to `pattern_miner.py`'s own crossover convention (Tony's manual entry a few days ahead of formal MT confirmation -- in which case `mine_bars()` likely already found each one at its real, later crossover date, and the true reachable-hit rate is higher than 68/84) is a pending confirming check, not yet run as of this entry.

---

### M-085 -- A resolution heuristic's negative result ("couldn't find a match") gets silently trusted as ground truth unless exhaustively checked against a wider search

**Date:** 2026-07-13
**Trigger:** WO-P300-E3.002 ground-truth validation. `resolve_pick()`
(used across parts 5/8/9 of this session's PEH rounds) tries exactly 4
combinations per pick: original inferred direction at the nearest bar,
opposite direction at that same bar, original direction at idx-1,
original direction at idx+1. When none of the 4 qualify, the pick gets
filed as OUTCOME-INVALID -- "never clears 15%, genuine ground-truth
noise, not a code bug." That label was carried across multiple
validation rounds (66-anchor, then 84-anchor, then the v2.1 re-run) as
settled. A session-close spot-check (Tony's explicit ask, not
something already planned) widened the search to both directions
across idx-2..idx+2 (10 checks instead of 4) on a 17-symbol sample:
only 3 (AME/PCAR/SHW) held up as genuinely invalid. 14/17 qualify
somewhere the narrower search never looked.

**Root cause:** `resolve_pick`'s 4-combination search was built to fix
a real, narrower problem (M-084-adjacent: the original single-bar/
single-direction check was too rigid) and was treated as "the fix"
once it visibly improved the numbers (OUTCOME-INVALID dropped 30->24
across earlier rounds). But 4 combinations is itself an arbitrary,
untested boundary -- nothing distinguished "this is now exhaustive
enough" from "this happens to be wider than before." A heuristic that
returns None reads the same whether the answer is genuinely absent or
just outside the heuristic's search radius; only widening the search
further (or checking by hand) can tell the two apart. Same shape as
M-084 (an aggregate/heuristic result treated as settled without
checking what a wider or more granular look would show), but at the
level of a matching function's search radius rather than a density
statistic.

**Additional finding, not just search radius:** several of the 14
(AMZN, GOOGL, CIEN, SPY) qualify under a DIFFERENT class than the one
recorded as their inferred direction (e.g. AMZN logged dir=breakdown,
qualifies repeatedly as uptrend). This suggests mtdiff-sign direction
inference AT THE EXACT PICK BAR can be noisy/transitional for some
picks -- a neighboring bar's mtdiff may better reflect the real trend
direction Tony was actually trading. Not yet root-caused; flagged for
next session, not guessed at here.

**Generalized rule:** When a resolution/matching heuristic is widened
to fix a specific known gap (a bar-snapping issue, a direction-
inference issue, etc.), its remaining "no match found" results should
get at least one exhaustive spot-check against a materially wider
search before being trusted as ground truth for downstream validation
-- especially if that "no match" bucket is large enough to meaningfully
change a headline number if wrong (24/84 = ~29% of this session's
ground truth). A heuristic's negative result is not evidence of
absence; it's only evidence the heuristic's specific search didn't
find one.

**Status:** Open -- next session: widen `resolve_pick` (or replace it
with the full exhaustive idx-2..idx+2, both-directions search this
spot-check used) and re-run the full 84-anchor validation. If the
14/17 ratio holds across the complete 24-pick bucket, true HITS is
likely ~78-80/84 (93%+), not 60/84 (71.4%). Also investigate the
direction-mismatch pattern (AMZN/GOOGL/CIEN/SPY qualifying under the
opposite class from their recorded inferred direction) as a possibly
separate, real issue in how direction gets inferred for a pick, not
just a search-radius gap.

**Pairs with:** M-084 (aggregate/heuristic result trusted without
checking the underlying distribution -- same principle, applied here
to a matching function's search radius instead of a density statistic).

(Captured 2026-07-13)

---

## M-091 — Session-header timestamp fabricated instead of pulled from system (SIP Step 1 violation)

**Status:** Resolved same session (caught by Tony immediately).

**What happened:** INIT Step 1 requires displaying the session header
with time "via `windows-mcp:PowerShell` or local system fallback."
Claude wrote `Tuesday, July 14, 2026 -- 14:22 ET` in the header without
calling any tool for it -- a plausible-looking guess, not a real read.
Tony caught it immediately ("where did you get the time?? Bad mistake").
Real time via `Get-Date`: `09:57 ET` -- off by 4+ hours.

**Root cause:** Same family as M-051 (fabricated status strings without
a real call behind them) -- this is the identical failure mode applied
to a timestamp instead of a vault-write confirmation. The INIT template
lists a time field; Claude filled it from pattern-completion instead of
treating "via PowerShell" as a hard requirement to actually invoke the
tool.

**Generalized rule:** Every field in the Step 6 session-header template
that names its own source ("via PowerShell", "via FileSystem read", "via
config.py grep") must be traceable to an actual tool call made THIS
session, not inferred, estimated, or pattern-completed -- no exceptions
for fields that seem low-stakes (a timestamp) vs. high-stakes (catalog
health). If the tool wasn't called, the field must say "unavailable,"
never a plausible-looking value.

**Prevention:** Before displaying the Step 6 summary, verify each
templated field has a corresponding tool-call result in this session's
own transcript -- not memory, not the previous session's value with the
date bumped forward.

(Captured 2026-07-14)

---

## M-092 — mine_audit.py's float epsilon didn't account for the CSV round-trip it sits downstream of

**Status:** Resolved same session.

**What happened:** During PEH of `application/ingest_mined_pipeline.py`
(file #6, WO-P300-E3.002), every one of 3 real approved ADBE rows failed
`mine_audit.py`'s audit gate on a `move_pct mismatch` -- claimed and
recomputed values printed identical at 6 decimals but differed by
~1e-7, past `_MOVE_PCT_EPSILON = 1e-9`.

**Root cause:** `mine_report_writer.py`'s candidates CSV writes
`move_pct` at `:.6f` precision (deliberate -- operator-readable). That
round-trip can move a real, genuinely-unchanged value by up to ~5e-7.
`mine_audit.py`'s epsilon (1e-9) was sized only for float-arithmetic
noise in the recompute itself and never accounted for the CSV
precision boundary sitting between "approved" and "re-audited" -- a
gap between two files (#3 and #5) each individually correct, that only
showed up when file #6 actually chained them together for the first
time.

**Fix:** `_MOVE_PCT_EPSILON` widened 1e-9 -> 1e-6 in `mine_audit.py`
v1.1. CSV precision deliberately left unchanged (6 decimals on a 15%+
move is intentional operator-facing precision, not the bug).
`tests/test_mine_audit.py` NEW (file's first real bug fix, per
Regression Test Governance) -- 2 tests: a CSV-rounded real value
passes audit, a genuinely different value (+0.01) still fails it.

**Generalized rule:** A float-tolerance constant sized against one
producer of the value (arithmetic noise) can silently fail against a
DIFFERENT producer of the same value (a serialization round-trip) once
a later file actually chains the two together. When two independently-
correct files are combined for the first time by a third, re-verify
tolerance/precision assumptions at that seam specifically -- don't
assume "both passed their own PEH" implies the combination is safe.

**Pairs with:** M-082/M-084 family (a value correct in isolation, silently
wrong once a later change puts it in a new context).

(Captured 2026-07-14)

---

## M-093 — MINE_MIN_ANCHOR_DATE gates the anchor, not the window behind it -- a window can still reach into backfilled 0.0 placeholder bars

**Status:** Resolved same session.

**What happened:** Second PEH pass on `application/ingest_mined_pipeline.py`
(file #6, WO-P300-E3.002), after the M-092 fix, hit a new failure on the
same real ADBE run: `merge_one_pattern` raised a Pydantic `ValidationError`
-- `pred_high`/`pred_low` both `0.0`, failing `PatternBarRecord`'s
`gt=0` constraint. The mined anchor (2021-08-04) was itself legitimately
past `MINE_MIN_ANCHOR_DATE` (2021-07-14), but its `BULK_WINDOW_LENGTH`
(20-bar) window reached back to 2021-07-08 -- six days into the
pre-backfill period, where VantagePoint's predictive fields are 0.0
placeholders.

**Root cause:** `MINE_MIN_ANCHOR_DATE` was only ever enforced as an
anchor-eligibility gate (`pattern_miner.py`'s `_is_eligible()`). Nothing
checked that the WINDOW BEHIND an eligible anchor also stays clear of
the boundary -- `_build_window_and_labels()` only guarded against
`window_start < 0` (not enough bars at all), not against the window's
earliest bar predating the backfill cutoff.

**Fix:** `_build_window_and_labels()` (ingest_mined_pipeline.py v1.1) now
raises `ValueError` when `window_bars[0].bar_date < MINE_MIN_ANCHOR_DATE`,
treated the same as insufficient-history -- an audit-adjacent skip, never
an insert or a crash. `run_this.py` (the PEH script itself) was also
fixed: it was blindly taking the first 3 chronological mined candidates,
which is exactly the failure mode most likely to hit an early,
boundary-adjacent anchor -- it now filters for candidates whose window
clears the boundary before taking 3. New regression test
`tests/test_ingest_mined_pipeline.py` (2 tests: window-before-boundary
rejected, window-clear-of-boundary accepted), per Regression Test
Governance.

**Separately found (test-only, no production bug):** the same PEH run's
dedup step (`run_this.py` re-ingesting the same 3 approved rows into the
already-populated staging connection) expected duplicates to be caught
via `catalog_merge_io`'s `_pattern_already_exists` check, but they're
actually always caught earlier, via `mine_audit.py`'s "catalog collision"
reason -- `_existing_keys_for_symbol` reads the connection fresh at the
top of `_ingest_symbol` every call, so an already-committed anchor is
guaranteed to already be in `existing_keys` before `merge_one_pattern`
ever runs for it. `merge_one_pattern`'s own check is the real backstop
only for a same-batch duplicate not yet committed (existing_keys read
once, before that batch's loop) -- a different scenario than "re-run
against an already-populated connection." Fixed the assertion to check
the actual guarantee (0 new inserts, all 3 recognized as already
present) rather than assuming which specific mechanism intercepts.

**Generalized rule:** A boundary constant (`MINE_MIN_ANCHOR_DATE`) that
gates one point in time (the anchor) doesn't automatically gate a
WINDOW of bars measured backward from that point -- check the whole
window against the boundary, not just its endpoint. Also: when a
PEH script picks "the first N" of anything real-data-driven to keep a
test deterministic, that selection is itself a place bugs hide -- prefer
filtering for the property the test actually needs over taking an
arbitrary prefix.

**Pairs with:** M-092 (same file #6 PEH session, same root pattern -- a
value/constant correct for the purpose it was originally built for,
silently insufficient once a later file combines it with a wider-reaching
computation).

(Captured 2026-07-14)

---

## M-094 — atomic_move's own backup is single-level, overwrites every promote (no built-in deep history)

**Status:** Noted, not yet resolved -- Tony's call pending on scope.

**What happened:** Before the first real WO-P300-E3.002 production batch
(5,584 mined candidates, keep=YES on all per the document-only density
decision), Tony asked for a catalog backup first, framing it as
something that "should be built in." Checked `infrastructure/
verify_ingestion.py`'s `atomic_move()` docstring directly rather than
assuming: it renames the current master to `<master>.bak`, but
explicitly "overwriting any previous backup." Confirmed via
`models/` directory listing -- every dated catalog file has exactly one
`.bak` sibling, never more; there's no rolling or dated history at all,
just the immediately-prior state.

**Why this matters now specifically:** every promote to date has been a
handful of patterns (one AddPattern run, a few bulk-extract files). A
5,584-candidate batch is a different order of magnitude -- if something
looks wrong only after a SECOND promote happens (e.g. the next day's
routine AddPattern run), the single-level `.bak` will have already been
overwritten and the pre-mine-batch state is unrecoverable through the
built-in mechanism alone.

**Interim fix (2026-07-14, this session):** explicit manual backup taken
BEFORE the batch, to a distinct, non-overwritable filename:
`models/archive/databases/pre_mine_batch_071026catalog_20260714.db`
(verified byte-identical via `windows-mcp:FileSystem mode=info` --
3,346,432 bytes, matching mtime). This is the established
`models/archive/databases/` convention (pre-existing dir, already used
for retired snapshots), not a new pattern invented for this session.

**Open question, Tony's call:** should a pre-promote snapshot to
`models/archive/databases/` become an automatic step inside
`promote_staging_to_live()` (or `ingest-mined`'s CLI wrapper
specifically) for any batch over some size threshold, or for every
promote regardless of size? Not decided or built this session -- flagged
so it doesn't get lost, scope intentionally left to Tony rather than
guessed.

**Pairs with:** the project's Lock+Temp-DB+Atomic Move protocol generally
-- this doesn't change that protocol's correctness (it's still atomic,
still verified pre/post), it's specifically about backup DEPTH for
large/high-stakes batches.

(Captured 2026-07-14)

---

## M-095 — get_latest_catalog()'s str-vs-Path convention (M-089) recurred at 3 more call sites, one crashed a real promote

**Status:** Resolved same session (3 call sites fixed). Systemic fix (typed sibling function) filed as WO-P300-E4.002, PENDING.

**What happened:** First real WO-P300-E3.002 production `--promote` crashed:
`'str' object has no attribute 'exists'`. Real live `catalog.db` confirmed
untouched (mtime unchanged) -- crash happened before any write, the
Lock+Temp-DB+Atomic-Move protocol's own pre-write ordering protected the
data even while the code itself was broken.

**Root cause:** `get_latest_catalog()` deliberately returns `str` (by
design, not a bug in itself). M-089 already established the convention
that every caller must wrap it in `Path()`. Grepping every call site in
the codebase tonight found the convention had been silently violated 3
more times since M-089: `catalog_merge_pipeline.py`'s
`build_staging_merge()` AND `promote_staging_to_live()` (both), and
`ingest_mined_pipeline.py`'s `run_ingest_mined()` (this session's own
file #6). The `promote_staging_to_live()` site is what actually crashed
(`atomic_move()` calls `.exists()` on it). The other two never crashed
-- `shutil.copy2()` and `load_full_catalog()` both happen to tolerate a
raw `str` -- meaning they were silently WRONG, not silently safe, and
would have crashed the instant either function's implementation ever
changed to expect a real `Path`.

**Fix:** All 3 call sites wrapped: `Path(get_latest_catalog())`.
`catalog_merge_pipeline.py` -> v1.1, `ingest_mined_pipeline.py` -> v1.2.
New regression test `tests/test_get_latest_catalog_path_safety.py`
(static source-scan, not runtime -- greps both files for the unwrapped
pattern, fails if it reappears).

**Tony's architectural question, answered directly:** does
`db_connect.py` already shield this? Partially -- it's explicitly
"the single choke point for all catalog access" (its own docstring),
but only for `sqlite3.Connection` objects. `sqlite3.connect()` accepts
a raw string fine, so `db_connect.py` itself calls
`get_latest_catalog()` unwrapped (line 59) and never breaks. The 3
sites that broke tonight all needed the raw filesystem PATH itself
(`shutil.copy2`, `atomic_move`'s `.exists()` check, a typed dataclass
field) -- a genuinely different need `db_connect.py`'s shield was never
built to cover.

**Systemic fix, not built tonight (mid-incident, correctly deferred):**
WO-P300-E4.002 filed -- a typed sibling `get_latest_catalog_path() ->
Path` in `db_utils.py`, so future callers needing the path get it
correctly-typed automatically instead of relying on a
remember-every-time convention that has now failed 4 times total
(M-089 + this session's 3). PENDING, will surface at every future INIT
until closed -- Tony's explicit choice, so it stays visible rather than
living only as a lessons.md paragraph.

**Generalized rule:** when a static-typing convention (must wrap X in
Y) has to be manually remembered at every call site with no
enforcement, one violation is a bug; a second violation in the same
session at a different site is a systemic-fix signal -- stop patching
individual call sites once the pattern repeats within the same
incident and file the real fix as its own item, even under real
production time pressure. Don't let "just fix this one" absorb what's
actually a "fix the interface" finding.

**Pairs with:** M-089 (original instance of the same convention gap).

(Captured 2026-07-14, live production incident during WO-P300-E3.002's
first real --promote)

### M-096 -- Uncapped-runtime gate steps are bugs, not performance backlog items
**Rule:** Any process step that sits inside a promotion/decision gate the operator has to wait on -- with no cap, no timeout, no sampling bound -- and whose cost scales with catalog/dataset size (so it only gets slower over time) is a reliability defect. File and treat it as a bug (fix required before the gate is trusted for routine operator use), never as an optional performance-improvement backlog item, regardless of whether the underlying computation is otherwise correct.
**Trigger:** WO-P300-E4.003 (2026-07-15) was first filed as a performance-improvement WO after the M-079 walk-forward eval ran 40+ minutes against the full 6039-pattern catalog and looked hung to the operator. Tony corrected same session: a gate step with unbounded, size-scaling runtime and no cap is a bug. WO-P300-E4.003 reclassified accordingly.
**Applies to:** P_300 (M-079 walk-forward eval today; any future gate step with no runtime bound), and any future project where a decision gate's own cost is allowed to grow unchecked with data volume.


### M-099 -- A cache keyed on file identity (mtime/filename) breaks under any operation that legitimately renames or copies the file without changing its content
**Rule:** When a cache's invalidation key includes filesystem metadata (mtime, filename) rather than actual content, any routine file operation that touches that metadata -- a backup copy, a dated rollover, an atomic-move-then-rename -- silently defeats the cache even though nothing the cache cares about changed. Key caches on content identity (row count + max PK + file size, or a real hash for smaller files) when the underlying operation legitimately copies/renames without mutating content.
**Trigger:** E4.003's pre-batch walk-forward cache (infrastructure/eval_io.py) was keyed on `<catalog_stem>_<mtime_ns>_<tag>`. `P_300_RunBulkAddPattern.ps1`'s daily dated-rollover step (`071526catalog.db` -> `071726catalog.db`, a plain file copy, same content) gives the copy both a new filename AND a new mtime -- guaranteed cache miss on literally the first run of every single day, the one run where the cache matters most. Caught live during a real BulkAddPattern run on 2026-07-17: the "pre" pass, expected to hit the E4.003 cache instantly, instead paid the full ~31-minute re-score because the morning's rollover had already run before ingest-mined started.
**Fix:** `infrastructure/eval_io.py` v1.5 -- `_cache_key()` now fingerprints catalog CONTENT (`pattern_instances` row count + `MAX(pattern_instance_id)` + file size) instead of mtime; `_stable_stem()` also strips the `<mmddyy>` rollover prefix so the cache filename itself doesn't churn daily. A real promote (insert/delete) changes the fingerprint correctly; a same-content rollover copy now hits. `tests/test_eval_scoring.py` v1.1 -- cache fixture rebuilt as a real minimal SQLite db (fingerprint needs a real query, not a text-file mtime); added `_test_rollover_copy_still_hits()` proving the exact case this fix targets. Both suites (E4.003's + E4.004's) re-run clean, 8/8 checks, PEH-confirmed 2026-07-17.
**Applies to:** Any project with a file-keyed cache sitting in front of an expensive computation; any workflow with a rename/copy/backup step that isn't also a content change (dated rollovers, `.bak` files, archive copies) -- the identity-vs-content distinction matters most exactly where it's easiest to miss (the cache "worked" in every test that didn't happen to rename the file first).

(Captured 2026-07-17)

### M-100 -- A WO's WHY premise needs the same evidence bar as its acceptance criteria, especially when it's plausible-sounding
**Rule:** "On a normal daily run, new items are dated today" is the kind of premise that sounds obviously true and goes unchallenged during planning -- but if the actual data-generating process doesn't work that way, the whole optimization is dead code from the moment it ships, no matter how correct the implementation is. Before building an optimization that depends on a claimed property of the data, check the property against real data from the actual pipeline, not against an intuition about how the pipeline "should" work.
**Trigger:** WO-P300-E4.004's WHY section stated "every one of that day's approved picks has today's anchor_date" as the premise justifying incremental post-batch scoring. First real BulkAddPattern run (2026-07-17) hit the guardrail on pattern #1: `mine-patterns` scans full multi-year history and finds candidates at their REAL historical chart dates (earliest this run: 2021-08-18), not the run date. Manual Pipeline A (AddPattern.bat) likely shares this property -- Tony dates a pattern to when the chart setup occurred, not to when he enters it. Neither of P_300's two real ingestion paths appears to produce same-day-anchored inserts, so the premise was never true in practice, not just true-until-an-edge-case.
**Fix:** The guardrail (added specifically because "don't fully trust this premise" was already the right instinct during design) caught it safely -- zero wrong data, correct fallback to a full re-score. But the WO's stated acceptance criterion (real speedup on a representative batch) is unmet and will stay unmet for this pipeline as currently used. Flagged in WO-P300-E4.004's REAL-WORLD FINDING section rather than silently left OWNER_DONE with an unmet criterion; Tony's call next session on whether to leave it as an inert safety net, revert it, or redesign around what the data actually does.
**Applies to:** Any future WO whose optimization depends on a claimed pattern in how/when data arrives (same-day, monotonic, deduplicated, etc.) -- verify the claim against a real sample from the real pipeline before or immediately after build, not just at first real-world use weeks later. The guardrail pattern itself (assert the assumption, fall back safely on violation, never trust silently) is worth reusing whenever a WO's premise can't be fully verified before deciding to build.

(Captured 2026-07-17)

### M-101 -- Reconstructing a result from partial/merged computations must replicate the ORIGINAL's exact ordering logic, not just its sort key
**Rule:** When a result set is normally built by sorting one homogeneous collection (e.g. `sorted(all_metadata.keys(), key=...)`), and a variant instead assembles the same result set from two SEPARATELY-SOURCED sub-collections (reused + freshly-computed) and sorts the concatenation, ties on the sort key can resolve differently -- Python's sort is stable, so tie-breaking depends on INSERTION order, and concatenating two lists built by different processes rarely preserves the original's insertion order. Byte-identity requires replicating the exact ordering computation (same iterable, same key, same stability), not just "sorted by the same key."
**Trigger:** WO-P300-E4.004 v1.1's `assemble_incremental_post_batch()` built `reused_results + rescored_results` then sorted the concatenation by anchor_date. `run_walk_forward()`'s reference ordering is `sorted(all_metadata.keys(), key=anchor_date)` over the FULL metadata dict. On a same-date tie between an existing (reused) pid and a new (rescored) pid, the two orderings disagreed -- reused_results always listed new pids before existing rescore pids (construction order), while the reference iterates all_metadata's natural key order (existing-inserted-first, since `_merge()` builds `{**existing, **new}`). Caught by the mixed-dates regression test's byte-identity assertion during PEH (2026-07-17) -- the existing test already encoded the invariant, no new test needed for the fix itself.
**Fix:** Build a `results_by_pid` lookup dict from both sub-collections, then order the final list via the SAME `sorted(all_metadata.keys(), key=anchor_date)` computation the reference function uses -- not a sort over the assembled results. Guarantees identical tie-break behavior because it's literally the same operation on the same dict, not a parallel implementation that happens to use the same key.
**Applies to:** Any "skip redundant work, reuse partial results" optimization that must byte-match a from-scratch computation -- caching, incremental updates, partial re-scoring. When ties are possible on the ordering key, order via the reference's own iteration/sort logic over the full population, never by sorting a differently-constructed concatenation and hoping tie-breaking lines up.

(Captured 2026-07-17)

## M-102 -- MINE_MIN_ANCHOR_DATE as a frozen literal goes stale the moment VP's rolling 5-year backfill window moves past it

**Rule:** VP's predictive-column backfill boundary is a ROLLING 5-year window measured from each export's date, not a fixed calendar date. A constant calibrated once against "today" (e.g. `date(2021,7,14)` set 2026-07-12) is correct only until the rolling window moves past it -- which happens continuously, not on some future one-time event. By 2026-07-17, five days after calibration, the frozen literal was already stale.

**Trigger:** `MINE_MIN_ANCHOR_DATE` was set as a frozen literal `date(2021, 7, 14)` on 2026-07-12. The CNK mined-pattern batch crashed on 2026-07-17 hitting a backfilled zero-prediction bar the (by-then-stale) literal no longer excluded correctly.

**Fix:** Replaced the frozen literal with a computed first-safe date (calendar today minus 5 years, plus a 2-day buffer), recomputed at run time instead of calibrated once and left to drift. First formula draft (`today - (5*365+2)` days, ignoring leap years) landed exactly ON the last zero-prediction bar and still crashed the same batch -- corrected to a true calendar 5-year-plus-2-days offset, which matches the original 2021-07-14 calibration and real observed data (first non-zero bar = 2021-07-19 as of 2026-07-17). config.py v1.18.

**Applies to:** Any constant derived from "today" at calibration time that represents a boundary which itself moves with the calendar (backfill windows, rolling-window cutoffs, N-years-back references). Compute at call time from the current date, never freeze as a literal -- a literal is correct on the day it's written and increasingly wrong every day after.

(Captured 2026-07-17 -- filed retroactively 2026-07-18 during independent review of an unrelated WO; config.py v1.18's changelog referenced this as M-102 and described the fix in full, but no lessons.md entry actually existed until this filing. Ties to M-054 -- a changelog claim is not the same as an evidenced lessons.md entry.)

## M-104 -- A pip dependency-conflict warning reflects a declared pin, not real usage -- grep the codebase before reacting to one

**Trigger:** WO-P300-E4.005 Phase 2a required bumping numba 0.61.2 -> 0.64.0 in the shared p140 env (0.61.2 didn't support the env's numpy; 0.64.0 does). pip's installer completed the upgrade but printed a resolver conflict: `pandas-ta 0.4.71b0 requires numba==0.61.2, but you have numba 0.64.0 which is incompatible.` pandas-ta is not declared in any project's requirements.txt AND is not imported anywhere in the Hub's Python code (verified: recursive grep across `projects\` for both the requirements-file pin and the `import pandas_ta` statement, zero hits either way) -- a phantom risk, not a real one, in this instance.

**Fix:** Before treating a pip conflict warning as a blocker (or as safe to ignore), grep the actual Hub codebase for real imports of the conflicting package -- not just its requirements.txt declarations, since an unused package can still be installed and still carry a stale pin. pip's resolver only knows about declared metadata; it can't tell you whether anything actually calls the code. A hard-pinned-but-unused package is noise; a hard-pinned-and-imported one is a real cross-project blast-radius question that needs the owning project identified before the shared env changes.

---

## M-103 -- PowerShell here-string quoting silently corrupts markdown backticks and drops trailing newlines

**Trigger:** Wrote a todo.md log entry containing markdown code-ticks (e.g. `` `run_incremental_post_batch` ``) via a PowerShell double-quoted here-string (`@"..."@`). PowerShell interpreted backtick+letter as an escape sequence (`` `r `` = carriage return, `` `n `` = newline) instead of literal backtick + text, splitting `` `run_incremental_post_batch` `` into a stray CR mid-word and silently eating the identifier's leading characters. No error, no warning -- the write succeeded and reported a byte count, but the content was wrong. Caught by re-reading the file back, not by the write itself.

**Second bug, same fix attempt:** Switched to a single-quoted here-string (`@'...'@`, which treats backtick literally) and the identifiers came out correct, but the line immediately before the closing `'@` lost its trailing newline -- PowerShell here-string syntax excludes the final line break before the terminator. This merged a `---` separator directly into the next entry's `**>>>` header with no line break.

**Fix:** For any file write containing literal backticks, use a single-quoted here-string (`@'...'@`), never double-quoted. Always leave a deliberate blank line (empty line) before the closing `'@` when the content must end in a newline, since the line directly preceding the terminator gets its own trailing newline stripped. Always re-read the written region back before trusting the write (ties to M-051 -- no `[OK]` without a real verifying read).

**Applies to:** Any windows-mcp:PowerShell write of markdown/code content containing backticks -- todo.md, lessons.md, WO files, or any Python/config file edited via inline PowerShell rather than `windows-mcp:FileSystem` mode=write with `content` passed as a parameter (which does not go through PowerShell string-escape parsing at all and is the safer default for content with backticks).

(Captured 2026-07-18)

---

## M-105 -- A WO's claimed permanent test file is a claim, not evidence -- two instances found missing from disk in one session, both caught only by independent re-verification

**Rule:** A WO or lessons.md entry stating a permanent regression test file was built, with a specific line count and a "N/N PASS" result, describes what the writing session BELIEVED happened -- not a guarantee the file actually landed on disk. This is M-054's own rule ("a closure note is a claim, not evidence") applied specifically to test-file existence, which needs the same discipline as any other closure claim: verify the artifact directly, don't infer it from prose describing it.

**Trigger:** Two separate instances, same session, both caught only by an independent-review chat that hadn't written the original code:
1. WO-P300-E4.005's own Phase 2a text claimed `tests/test_similarity.py` as "NEW, 113 lines, permanent... 7/7 PASS." A project-wide filename search found zero matches; `tests/__pycache__/` held compiled artifacts for two sibling test files but none for this one -- no trace it had ever run there.
2. M-095's lessons.md entry (2026-07-14) claimed `tests/test_get_latest_catalog_path_safety.py` as a built static-scan regression test. Same result: absent from disk, no `__pycache__` trace.

Both were rebuilt from scratch the same night (2026-07-20), both real and verified passing afterward (7/7 and matching checks respectively, real PEH execution via Claude Code Desktop). The underlying correctness claims each WO made (JIT byte-identity, the dedup fix) were independently true and separately evidenced (a different PEH regression script, a real production incident) -- it was specifically the PERMANENT TEST FILE artifact that was missing, twice, not the underlying work.

**Fix:** When a WO's own text claims a test file exists, don't take that as settled during independent review -- run (or at minimum `Test-Path`/filename-search) the actual file before treating its coverage as real. A `__pycache__` directory listing is a cheap secondary signal: a `.pyc` for every sibling test file but none for the claimed one is a strong tell the file never ran from that location, even before checking the source file itself.

**Applies to:** Any independent-review session evaluating a prior WO's stated deliverables -- test files, migration scripts, generated reports, anything described as "built" in prose. Two independent occurrences of the identical failure mode in one session is a pattern worth naming, not two unrelated coincidences to shrug off.

(Captured 2026-07-20/21, filed after Tony's explicit "yes make entry" -- flagged during the session, not filed unilaterally.)


---

## M-106 -- Bulk pattern-mining exports land in data\bulk\mine\, not data\historical_patterns\

**Rule:** `data\historical_patterns\` is the single-pattern AddPattern drop folder (Pipeline A, `add_pattern_pipeline.py`). The bulk pattern-mining path (mine-patterns -> ingest-mined, used for pre-export-checked multi-symbol batches) reads from `DATA_BULK_MINE` (`config.py`, = `data\bulk\mine\`). These are two different pipelines with two different drop folders -- VP pattern exports for a bulk batch go in `data\bulk\mine\`, never `data\historical_patterns\`.

**Trigger:** Tony corrected a session instruction that told him to drop the 16-symbol pre-export-checked batch's pattern files in `data\historical_patterns\` -- wrong folder for this pipeline. Confirmed against the real `config.py` constant (`DATA_BULK_MINE: Path = DATA_BULK / "mine"`, `DATA_BULK = DATA_DIR / "bulk"`) and the real directory (`data\bulk\mine\` exists on disk; `data\historical_patterns\` is Pipeline A's folder, unrelated to this batch).

**Fix:** Before naming a drop folder for a pattern-export batch, check which pipeline the batch is going through (single-pattern AddPattern vs. bulk mine-patterns) and grep `config.py` for the actual constant rather than assuming from a prior single-pattern-flow habit.

**Applies to:** Any session directing Tony to export/drop VP pattern files for a bulk (multi-symbol, pre-checked) batch.

(Captured 2026-07-21, Tony's direct correction.)


---

## M-107 -- `ingest-mined` and `merge-research-catalog` share one file (`cli_commands/bulk_promote.py`) but are two different WOs -- verify the actual CLI source before attributing a real production event

**Rule:** Console output naming a CLI subcommand ("ingest-mined --promote") is not enough on its own to identify which WO owns it when two similarly-shaped promote commands live in the same file. `merge-research-catalog` = WO-P300-E2.003 (staging db `staging_merge_catalog.db`, PARKED since 2026-07-10). `ingest-mined` = WO-P300-E3.002 Phase 2 (staging db `staging_ingest_mined.db`). Same promote mechanics underneath (`catalog_merge_pipeline.promote_staging_to_live`, deliberately shared/unchanged per E3.002's own design), different owning WOs.

**Trigger:** Tony pasted a real `ingest-mined --promote` console log (+4,055 patterns / +13 symbols, real live promotion). First-pass attribution guessed WO-P300-E2.003 from session-context pattern-matching ("mined-batch promotion") without opening the actual command source; Tony said "confirmed" (trusting the read, not independently re-checking). Caught before logging, by opening `cli_commands/bulk_promote.py` directly -- the docstrings name the owning WO per command in plain text.

**Fix:** Before logging a real production event (WO status change, todo.md/lessons.md entry) against a specific WO, grep the actual CLI source (`register()` / `_cmd_*` docstrings) for the command that was run, not just the shape of the console output or a prior session's verbal framing. A "confirmed" from Tony on a terse exchange is not independent verification of the attribution -- same principle as M-054 applied to WO identity, not just claimed status.

**Applies to:** Any session logging a real catalog-write event where more than one WO's staging/promote pipeline could plausibly match the command shape.

(Captured 2026-07-22, Claude's own misattribution, self-caught before logging.)

---

## M-108 -- WO-P300-E3.002's Acceptance Criteria drafted a manual M-079 eval-review step Tony doesn't actually perform in practice

**Rule:** The WO's written Acceptance Criteria says: "Phase 2 first real batch: audit gate pass + M-079 staging eval comparison reviewed before promote." Tony's actual standing practice: audit gate clean (built into `ingest-mined`'s build step, runs automatically) -> promote directly, no separate manual walk-forward eval review. These are different gates -- the audit gate checks row-level validity (threshold clears, anchor is the real launch, eligibility, no collision); the M-079 eval checks population-level precision impact on BUY/WATCH/PASS (the mechanism that caught E2.003's 68.8%->63.6% dilution). Tony's call is that audit-gate-clean is sufficient for his own ingest-mined batches; the population-level risk that motivated M-079 in E2.003 was a different pipeline (unfiltered bulk-scan, not outcome-first mined + audit-gated).

**Trigger:** Real first production `ingest-mined --promote` run (2026-07-22, +4,055 patterns). Flagged the written-criteria-vs-practice gap once, Tony's answer: "I do not eval manually at all if there are no issues go to promote."

**Fix:** WO-P300-E3.002's Acceptance Criteria line should be corrected to match actual practice (audit gate pass is the real, sufficient gate for promote) rather than staying written as a step nobody performs -- a criterion nobody follows is worse than no criterion, it invites a false "not fully met" read on every future batch. Not re-litigating this after Tony's explicit answer.

**Applies to:** WO-P300-E3.002 and any future WO reusing its ingest-mined promote path.

(Captured 2026-07-22, Tony's direct standing-practice clarification.)


---

## M-109 -- A file's absence from memory/context is not evidence it doesn't exist on disk -- check before writing to any path claimed as "new"

**Rule:** Before writing to any file path as if creating it fresh -- even one that "should" be new per a plan, a WO, or an absence from lessons.md/todo.md/memory -- run `windows-mcp:FileSystem mode=info` (or `mode=read`) on that exact path first. Absence from Claude's own context (memory, this session's reads, a WO's file plan) is not evidence the file doesn't exist on the real machine; it only proves Claude hasn't seen it yet, which are not the same thing (M-015's principle -- live filesystem overrides project attachments -- applies with equal force to "no attachment mentioned it," not just to "the attachment's stale copy disagrees").

**Trigger:** WO-P000-E8.001 pilot (2026-07-22) -- planned and wrote a fresh `CLAUDE.md` for P_300 project root, reasoning from an earlier same-session audit that checked P_010/P_800/P_020/P_400/P_805 for a CLAUDE.md but never checked P_300 itself. Wrote via `windows-mcp:FileSystem mode=write, overwrite=true` directly, without a prior `mode=info`/`mode=read` check. The write succeeded and reported a normal result -- no error, no warning -- but a follow-up `mode=info` call (routine mtime confirmation, Protocol F1+F2) showed `Created: 2026-06-18`, over a month before this session: a real, actively-maintained project CLAUDE.md already existed at that exact path and was silently overwritten. No tool-level signal distinguished "created a new file" from "clobbered an existing one" -- `overwrite=true` succeeds identically either way.

**Recovery:** No `.bak` existed. VS Code local history had no entry (file wasn't edited through VS Code, so never captured there). Hub root is a git repo; `git log --oneline -- <path>` (run by Tony directly, since `git log` hung reliably through the MCP relay -- same failure family as M-030/M-076 but for git instead of python) found one commit. `git show <commit>:<path>` recovered the content, but the first copy-paste round mixed in unrelated terminal scrollback (M-056's family) and cut off mid-file; redirecting straight to a file (`| Out-File -Encoding utf8 <path>`) and reading that back directly avoided a second lossy paste. Recovered content also carried encoding corruption from the pipe (mis-decoded em-dashes and box-drawing characters, M-019's family) -- restored using this project's own ASCII convention (`--`, `->`, `+--`) rather than reintroducing the Unicode that caused it.

**Fix going forward:** `mode=info` (cheap, fast) before any `mode=write` to a path not already confirmed present-and-current in this session -- not just for edits (M-015 already covers those), but for any write framed as "creating" something, since "framed as new" is a claim about Claude's own knowledge state, not a fact about the filesystem.

**Applies to:** Any file write anywhere in the Hub, but especially WO-P000-E8.001's own remaining rollout (P_115/P_400/P_020/P_805/P_010/P_800 audits) -- the exact mistake this lesson describes (assuming "no CLAUDE.md" from an incomplete audit) is a live risk for every project still on that WO's list.

**Pairs with:** M-015 (live filesystem overrides attachments/memory), M-054 (a claim -- here, "this file doesn't exist" -- is not evidence until checked directly), M-056 (a copy-paste can silently mix in unrelated content), M-019 (Windows/PowerShell encoding corruption family).

(Captured 2026-07-22, Claude's own real mistake, self-caught via the mtime-verification habit M-054 already established -- not caught by Tony first this time.)


---

## M-110 -- Multi-segment PowerShell array assembly: verify the FULL result before Set-Content, every time, not just the pieces you remember editing

**Rule:** When building a file edit out of multiple array segments (`$before + $newPiece + $after` style, the standard safe-edit pattern this whole session), the failure mode is never in the individual pieces -- it's in the ASSEMBLY. Three real, distinct mistakes happened this way in one session: (1) writing `$result` before all segments were appended (`ingest_mined_pipeline.py` truncated right after the last-appended piece, silently dropping everything after it); (2) modifying an array element in place (`$lines[51] = ...`) then building `$before`/`$after` from ranges that excluded that modified index, silently dropping the edit entirely; (3) two new pieces (a function definition and a call meant for a different function) assembled in the wrong relative order, producing code that was syntactically valid but structurally wrong -- a new function's call ended up nested inside its own body instead of inside `main()`, and `main()` lost its `return 0`.

None of these three were caught by the immediate small-range verification prints used throughout this session (`Write-Output "before last: [...]"` / `"after first: [...]"`) -- all three passed those checks, because the checks only confirmed the BOUNDARIES of segments the assembly code referenced, not that the assembly was complete or correctly ordered. `ast.parse()` also didn't catch #3 -- nested-wrong code is still syntactically valid Python.

**Fix:** After any multi-segment assembly and `Set-Content`, do a full re-read of the affected region (not just boundary lines) before considering the edit done. For anything beyond a trivial single-line change, that means: `ast.parse()` (catches truncation and syntax breaks), then an actual import (catches undefined names), then -- for logic changes, not just structural ones -- a real execution (catches structurally-valid-but-wrong code like #3, which nothing short of running it will reliably catch). The PEH round-trip cost of doing this is real but small next to re-discovering a broken production file after the fact, which is what happened here on a file (`ingest_mined_pipeline.py`) that runs the actual ingest path.

**Applies to:** Any edit built via `$before + $new + $after` (or equivalent) array-segment assembly, especially in one PowerShell session touching multiple files back to back, where fatigue/pattern-momentum from three prior successful edits (config.py, eval_scoring.py, bulk_promote.py) likely contributed to the fourth and fifth being rushed.

**Pairs with:** M-109 (check before write), M-054 (a claim -- here, "the boundaries look right" -- is not evidence the whole thing is right).

(Captured 2026-07-23, three of Claude's own real mistakes in one session, all self-caught -- two via a full careful re-read, one via real execution after the re-read alone wasn't trusted.)
