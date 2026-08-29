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
(full text preserved, nothing deleted), and verbose retained entries get
a compression pass (prose tightened, no rule/path/number removed --
same standard as the SIP's own compression passes). First pass:
2026-07-22, 37 entries archived. Second pass: 2026-07-26, 28 more
entries archived + a compression pass on the ~10 heaviest retained
entries -- file dropped 138.4KB/1,392 lines -> ~63KB. See
tasks/lessons_archive.md for the removed entries and WO-P000-E8.001 for
the retention standard.

---
## Section 1 -- Session Methodology Rules (Active)

### M-111 -- A WO's Status header is a claim about its own body, not a substitute for reading it
**Rule:** A work order's `**Status:**` line can go stale independently of the body beneath it -- the body can accumulate real, verified evidence (PEH steps, real production runs, closed follow-ups) while the header line is simply never touched. Reading only the header and reporting it as current status is a distinct failure from M-054 (a *closure note in tasks/*.md* is a claim, not evidence) -- this is the WO document's own internal header/body contradiction, and it can make Claude confidently report an ACTIVE WO as unverified when it's actually done, not just report a DONE WO as active. Caught 2026-08-12: WO-P300-E4.006's header read "BUILT, NOT YET PEH-VERIFIED" while its own body documented four PASSED PEH steps, a real production migration, and a closed byte-identity regression, all dated 2026-07-19/21 -- three weeks of drift, propagated into an INIT summary and a downstream WO's (E5.008) false blocker before Tony's own pushback triggered a full re-read. **Prevention: for any WO whose Status is being reported, quoted, or relied on for a downstream decision (blocking another WO, an INIT summary, a work-order-governance display), read the full body -- not just the header -- before stating status as fact. A header/body mismatch is itself worth surfacing, not silently resolved toward whichever one seems more current.**

### M-089 -- `db_utils.get_latest_catalog()` returns a plain `str`, not a `Path`
**Rule:** Other callers rely on the plain-`str` return for direct
`sqlite3.connect(f"file:{path}...")` use -- wrap in `Path()` before calling
any `Path`-only method (`.stat()`, `.name`) on it. Caught 2026-07-13 in a
diagnostic script; script-local bug, not a `db_utils.py` defect.

### M-001 -- "You write, I review" pattern
**Rule:** For all file deliveries (Python, docs, configs), the AI writes the file directly to its target Windows path via `windows-mcp:FileSystem`. The operator reviews. The AI never asks the operator to copy-paste code from chat. (Confirmed 2026-05-13.)

### M-003 -- Plan before write
**Rule:** Any task involving 3+ files or architectural decisions requires a written file plan with line-count estimates *before* any code is written. Wait for explicit operator approval.

### M-005 -- Match operator message length
**Rule:** Short user message -> short AI response. Substantive decisions warrant substantive answers; trivial pings get trivial replies. Never lecture. Never restate the operator's question.

### M-006 -- Honest accountability over defensive recovery
**Rule:** When the AI misses something, acknowledge it directly. No padding, no apology spirals. State what was missed, what's being corrected, and move on.

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

**Rule:** Do not use `SETLOCAL ENABLEDELAYEDEXPANSION` combined with `!VAR!` in Windows batch files on this workstation -- produces `: was unexpected at this time.` even on syntactically correct files. Use `%date%` string slicing for dates; `goto` label pattern to break for loops. Generalized: don't set-and-use a `%VAR%` inside the same `(...)` block, period -- plain percent-expansion is parse-time-bound within a block regardless of delayed expansion.

**Recurrence (2026-07-07):** `P_300_AddPattern.bat`'s day-rollover backup copy silently no-op'd since the 2026-06-23 rebuild -- `NEWCATALOG` was set and referenced inside the same parenthesized `if/else (...)` block, so `%NEWCATALOG%` evaluated empty; `copy /y "...\%LATEST%" "...\"` (empty destination) silently failed with no errorlevel check. No data damage (ingest still wrote to the existing catalog correctly via `get_latest_catalog()`), but the daily-snapshot naming convention never fired for at least 2 weeks. Fixed via the goto-label pattern M-032 already prescribes -- `NEWCATALOG` set at top-level, not inside a block.

(Identified 2026-05-21; recurrence 2026-07-07)
### M-034 -- Feature ablation at N=116: volume_zscore is noise; z_score not discriminating at this catalog size

**Rule:** Run feature ablation and threshold sweep at meaningful catalog size (N>=50) before treating default similarity features/thresholds as production-ready.

**Finding 1 (2026-05-28, N=116):** Removing `volume_zscore` from SIMILARITY_FEATURES raised BUY precision 54.0% -> 70.5% (+16.5pp) with +42 BUY count -- volume is noisy cross-symbol/cross-time. All other 9 features within +-1.3pp. Shipped config.py v1.4.

**Finding 2 (same date):** `BUY_MIN_Z_SCORE` lowered 1.0 -> 0.0 (config.py v1.5) -- at N=116/58% baseline WR, z_score wasn't discriminating (z=-0.5/0.0/0.5 all produced identical buy_count=49, precision=79.6%). Production thresholds post-2026-05-28: BUY n>=5/wr>=0.70/z>0.0 (79.6% precision, +6.4% mean h=5), WATCH n>=3/wr>=0.60/z>0.0.

**Addendum (2026-06-28, re-eval trigger fired at N=331):** Walk-forward eval (strictly-earlier-anchor corpus, not LOO) on the full 331-pattern catalog: z>0.0 gave BUY=155 (60.0% accuracy); z>1.0 gave BUY=97 (62.9% accuracy). WATCH absorbed exactly the 58-pattern difference; PASS bit-for-bit identical across both -- confirms the override touches only the BUY boundary. The 58 demoted patterns ran 55.2% WR (below the 60% BUY-pool average) -- a real, modest edge cut. Decision: re-tightened `BUY_MIN_Z_SCORE` 0.0 -> 1.0 (config.py v1.8). Trigger closed.

(Captured 2026-05-28 / 2026-06-28)
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

**Rule:** Any console line claiming `[OK]`, `SUCCESS`, `DONE`, `written`, etc. MUST be produced from the actual function call's return value, not hardcoded before/instead of the call. A hardcoded success string is a falsified functional test. Placeholder output strings are permitted ONLY during active UI scaffolding within a single session -- before the session ends, every placeholder must be replaced with a real call or tracked as an open todo.md item. No placeholder survives a session boundary.

**Trigger (2026-06-12):** `report_writer.py print_signal_report_clean()` printed `[OK] {ticker} written to vault` and `ARCHIVE OK` as hardcoded strings -- no vault write and no archive call existed anywhere in the function. Scaffolded 2026-05-27, never replaced. The correctly-wired `signal_emitter.emit_signal_packet()` path masked the fact that this function's writes were fake.

**Addendum (2026-06-17) -- the original fix never landed:** todo.md/lessons.md both logged this closed 2026-06-12. It wasn't -- `report_writer.py` was still v1.7 with both strings verbatim, running live in production for 5+ days undetected. Real fix landed v1.8 -- see M-054.

**Pairs with:** M-040, M-047, M-054.

(Captured 2026-06-12)
## Section 2 -- Operational Lessons Specific to P_300 (Not Yet in EC Log)

### O-001 -- Pattern file bar overage
**Lesson:** VP exported files may contain 1-2 extra bars beyond nominal pattern length. This is a VP export artifact, not corruption. `pattern_instances.window_length` = actual bar count. Never truncate.

### O-004 -- Empty DB is not a clean baseline for current schema
**Lesson:** `empty__catalog.db` uses the original Perplexity 7-table schema. Archival only -- not a restore point.

### O-005 -- Skill scatter across 5+ locations is a known issue
**Lesson:** P_300 SKILL at `.claude/skills/p300-project-context/SKILL.md`. Consolidation is future work.

### O-006 -- VP History Grid XLSX uses merged top-row headers
**Lesson:** openpyxl returns the merge value only at the first cell of each group; continuation cells return `None`. Sub-header row has two format variants (abbreviated vs full Triple Cross names). Existing parser handles both. (Captured 2026-05-14.)

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

### M-075 -- A function that accepts scratch-path overrides for SOME of its I/O but not all of it is a test-isolation trap; every persistent side-effect needs its own override parameter

**Rule:** Before treating any function as safely testable via path overrides, enumerate EVERY persistent side effect it has (every file write, DB write, checkpoint, append) and confirm each has its own override parameter -- not just the ones already exposed. A function is only as test-isolated as its least-overridable side effect.

**Trigger (2026-07-08):** `run_bulk_extraction()` accepted `master_db`/`temp_db` overrides but had NO parameter for the checkpoint file path -- always read/wrote the real `BULK_CHECKPOINT_FILE`. A test run (itself triggering the real M-074 bug) wrote a real file into the LIVE checkpoint as "completed" with 0 detections. Every subsequent test run -- including after the M-074 fix -- silently skipped the file, looking exactly like "the sweep found nothing" rather than the real bug.

**Fix:** Added `checkpoint_path: Path = BULK_CHECKPOINT_FILE` as a fourth parameter, threaded through the load/save helpers (both changed from optional-default to required-positional internally). Docstring now states explicitly: overriding master_db/temp_db without also overriding checkpoint_path risks live-checkpoint pollution.

**Pairs with:** M-017, M-054, M-080 (same root cause recurred, different WO: reports_dir there, checkpoint_path here).

(Captured 2026-07-08)
### M-079 -- A mechanically-detected pattern is not a curated pattern; corpus composition is a calibrated input, not just data volume

**Date:** 2026-07-10
**Trigger:** WO-P300-E2.003 staging merge of 495 STRICT bulk patterns into the 508-pattern live analog pool dropped walk-forward BUY win rate 68.8% -> 63.6% while nearly doubling BUY volume (157 -> 316). Promotion correctly withheld -- the staging-eval-before-promote gate (decision 2) did exactly its job. CIEN head-to-head then explained WHY: manual and STRICT detection have EQUAL precision (80%/80% into >=15% risers on real data) but catch DIFFERENT phases -- the detector fires at crossover ignition (condition 1), Tony's picks are mid-trend continuation entries (condition 1 failed on all 5 of his picks, including all 4 winners). Merging them into one analog pool mixes two different setup populations under thresholds (M-034) calibrated for only one of them.

**Generalized rules:**
1. Never merge a mechanically-detected corpus into a human-curated analog pool without a staging-copy eval comparison first -- and treat the comparison as the decision, not a formality. Detection-rule conformance is a proxy for setup quality, not the thing itself.
2. When two signal sources have equal precision but different coverage, the right integration is usually a FUNNEL (breadth source feeds the precision gate) not a UNION (both dumped into one pool). Scanner -> eyeball -> catalog preserves both edges; merge destroys the curation edge.
3. A validation gate that fires (blocks a promotion) is a success, not a failure -- log the numbers that fired it, don't work around it.

**Pairs with:** M-034 (threshold calibration is corpus-specific), WO-P300-E2.001's original merge deferral (the isolation that made this test possible), WO-P300-E2.003 closure state (bridge built, verified, parked).

(Captured 2026-07-10)


### M-085 -- A resolution heuristic's negative result ("couldn't find a match") gets silently trusted as ground truth unless exhaustively checked against a wider search

**Rule:** A heuristic that returns "no match" reads the same whether the answer is genuinely absent or just outside its search radius -- only a materially wider search (or manual check) can tell the two apart. When a "no match found" bucket is large enough to meaningfully change a headline number if wrong, spot-check it against a wider search before trusting it as ground truth.

**Trigger (2026-07-13):** WO-P300-E3.002 ground-truth validation. `resolve_pick()` tried 4 combinations per pick (direction x {nearest bar, idx-1, idx+1}); non-matches got filed OUTCOME-INVALID across multiple validation rounds as settled. A session-close spot-check widened to both directions across idx-2..idx+2 (10 checks) on a 17-symbol sample: only 3 (AME/PCAR/SHW) held up as genuinely invalid -- 14/17 qualify somewhere the narrower search never looked. Additional finding: several of the 14 (AMZN, GOOGL, CIEN, SPY) qualify under a DIFFERENT class than their recorded inferred direction -- mtdiff-sign direction inference at the exact pick bar may be noisy/transitional. Not root-caused.

**Status:** Open -- next session: widen `resolve_pick` to the full exhaustive search and re-run the 84-anchor validation. If the 14/17 ratio holds across the full 24-pick bucket, true HITS is likely ~78-80/84 (93%+), not 60/84 (71.4%).

**Pairs with:** M-084.

(Captured 2026-07-13)
## M-094 -- atomic_move's own backup is single-level, overwrites every promote (no built-in deep history)

**Status:** Noted, not yet resolved -- Tony's call pending on scope.

**What happened (2026-07-14):** Before the first real WO-P300-E3.002 production batch (5,584 mined candidates), Tony asked for a catalog backup, framing it as "should be built in." `atomic_move()`'s docstring confirms it renames the current master to `<master>.bak`, explicitly "overwriting any previous backup" -- confirmed via `models/` listing, every dated catalog has exactly one `.bak`, never a rolling history. A second promote after a large batch would overwrite the only recovery point before any issue surfaces.

**Interim fix:** explicit manual backup to `models/archive/databases/pre_mine_batch_071026catalog_20260714.db` (verified byte-identical via `mode=info`), using the pre-existing archive-snapshot convention.

**Open question, Tony's call:** should a pre-promote snapshot to `models/archive/databases/` become automatic inside `promote_staging_to_live()` (size-threshold or unconditional)? Not decided.

(Captured 2026-07-14)
## M-103 -- PowerShell here-string quoting silently corrupts markdown backticks and drops trailing newlines

**Trigger:** Wrote a todo.md log entry containing markdown code-ticks (e.g. `` `run_incremental_post_batch` ``) via a PowerShell double-quoted here-string (`@"..."@`). PowerShell interpreted backtick+letter as an escape sequence (`` `r `` = carriage return, `` `n `` = newline) instead of literal backtick + text, splitting `` `run_incremental_post_batch` `` into a stray CR mid-word and silently eating the identifier's leading characters. No error, no warning -- the write succeeded and reported a byte count, but the content was wrong. Caught by re-reading the file back, not by the write itself.

**Second bug, same fix attempt:** Switched to a single-quoted here-string (`@'...'@`, which treats backtick literally) and the identifiers came out correct, but the line immediately before the closing `'@` lost its trailing newline -- PowerShell here-string syntax excludes the final line break before the terminator. This merged a `---` separator directly into the next entry's `**>>>` header with no line break.

**Fix:** For any file write containing literal backticks, use a single-quoted here-string (`@'...'@`), never double-quoted. Always leave a deliberate blank line (empty line) before the closing `'@` when the content must end in a newline, since the line directly preceding the terminator gets its own trailing newline stripped. Always re-read the written region back before trusting the write (ties to M-051 -- no `[OK]` without a real verifying read).

**Applies to:** Any windows-mcp:PowerShell write of markdown/code content containing backticks -- todo.md, lessons.md, WO files, or any Python/config file edited via inline PowerShell rather than `windows-mcp:FileSystem` mode=write with `content` passed as a parameter (which does not go through PowerShell string-escape parsing at all and is the safer default for content with backticks).

(Captured 2026-07-18)

---

## M-105 -- A WO's claimed permanent test file is a claim, not evidence -- two instances found missing from disk in one session, both caught only by independent re-verification

**Rule:** A WO/lessons.md entry stating a permanent test file was built (with a line count and "N/N PASS") describes what the writing session believed, not a guarantee the file landed on disk -- M-054's rule applied to test-file existence specifically. When reviewing a prior WO's claimed deliverables, run (or at minimum filename-search) the actual file before treating its coverage as real. A `__pycache__` listing is a cheap secondary signal -- a `.pyc` for every sibling test file but none for the claimed one is a strong tell.

**Trigger (2026-07-20/21):** Two instances, same session, both caught by an independent-review chat: (1) WO-P300-E4.005 claimed `tests/test_similarity.py` (113 lines, 7/7 PASS) -- zero matches anywhere, no `__pycache__` trace. (2) M-095's own entry claimed `tests/test_get_latest_catalog_path_safety.py` -- same result, absent. Both rebuilt from scratch same night, both real and verified passing (7/7 and matching checks, real PEH via Claude Code Desktop). The underlying correctness claims (JIT byte-identity, the dedup fix) were independently true and separately evidenced -- only the permanent-test-file ARTIFACT was missing, twice.

**Applies to:** Any independent-review session evaluating a prior WO's stated deliverables -- test files, migrations, reports.

(Captured 2026-07-20/21, filed after Tony's explicit "yes make entry.")
## M-106 -- Bulk pattern-mining exports land in data\bulk\mine\, not data\historical_patterns\

**Rule:** `data\historical_patterns\` is the single-pattern AddPattern drop folder (Pipeline A, `add_pattern_pipeline.py`). The bulk pattern-mining path (mine-patterns -> ingest-mined, used for pre-export-checked multi-symbol batches) reads from `DATA_BULK_MINE` (`config.py`, = `data\bulk\mine\`). These are two different pipelines with two different drop folders -- VP pattern exports for a bulk batch go in `data\bulk\mine\`, never `data\historical_patterns\`.

**Trigger:** Tony corrected a session instruction that told him to drop the 16-symbol pre-export-checked batch's pattern files in `data\historical_patterns\` -- wrong folder for this pipeline. Confirmed against the real `config.py` constant (`DATA_BULK_MINE: Path = DATA_BULK / "mine"`, `DATA_BULK = DATA_DIR / "bulk"`) and the real directory (`data\bulk\mine\` exists on disk; `data\historical_patterns\` is Pipeline A's folder, unrelated to this batch).

**Fix:** Before naming a drop folder for a pattern-export batch, check which pipeline the batch is going through (single-pattern AddPattern vs. bulk mine-patterns) and grep `config.py` for the actual constant rather than assuming from a prior single-pattern-flow habit.

**Applies to:** Any session directing Tony to export/drop VP pattern files for a bulk (multi-symbol, pre-checked) batch.

(Captured 2026-07-21, Tony's direct correction.)


---

## M-109 -- A file's absence from memory/context is not evidence it doesn't exist on disk -- check before writing to any path claimed as "new"

**Rule:** Before writing to any file path as if creating it fresh, run `windows-mcp:FileSystem mode=info` first. Absence from Claude's own context (memory, this session's reads, a WO's file plan) is not evidence the file doesn't exist on the real machine -- it only proves Claude hasn't seen it yet (M-015's principle applies with equal force to "no attachment mentioned it").

**Trigger (2026-07-22):** WO-P000-E8.001 pilot -- wrote a fresh `CLAUDE.md` for P_300 root, reasoning from an earlier audit that checked other projects but never P_300 itself. Wrote via `mode=write, overwrite=true` without a prior `mode=info` check. A follow-up `mode=info` (routine mtime confirmation) showed `Created: 2026-06-18` -- a real, actively-maintained file had been silently overwritten. `overwrite=true` succeeds identically whether creating or clobbering.

**Recovery:** No `.bak`, no VS Code local history. Hub root is a git repo -- `git log --oneline -- <path>` (run by Tony directly, since `git log` hangs through the MCP relay, same family as M-030/M-076) found one commit; `git show <commit>:<path>` recovered the content. First copy-paste round mixed in unrelated scrollback (M-056's family); redirecting straight to a file and reading it back avoided a second lossy paste. Recovered content also carried pipe encoding corruption (M-019's family) -- restored using the project's ASCII convention.

**Fix:** `mode=info` before any `mode=write` to a path not already confirmed present-and-current this session -- not just for edits (M-015 covers those), but for any write framed as "creating" something.

**Pairs with:** M-015, M-054, M-056, M-019.

(Captured 2026-07-22, Claude's own mistake, self-caught via the mtime-verification habit M-054 already established.)
## M-110 -- Multi-segment PowerShell array assembly: verify the FULL result before Set-Content, every time, not just the pieces you remember editing

**Rule:** When building a file edit out of multiple array segments (`$before + $new + $after`), the failure mode is never in the individual pieces -- it's in the ASSEMBLY. After any multi-segment assembly and `Set-Content`, do a full re-read of the affected region (not just boundary lines): `ast.parse()` (catches truncation/syntax breaks), then an actual import (catches undefined names), then a real execution for logic changes (catches structurally-valid-but-wrong code, which nothing short of running it reliably catches).

**Trigger (2026-07-23):** Three real, distinct mistakes in one PowerShell session on `ingest_mined_pipeline.py`: (1) `$result` written before all segments were appended, silently truncating everything after the last-appended piece; (2) an array element modified in place (`$lines[51] = ...`) then `$before`/`$after` built from ranges excluding that index, silently dropping the edit; (3) two new pieces (a function def and a call meant for a different function) assembled in the wrong relative order -- syntactically valid but structurally wrong (a call nested inside its own function's body instead of `main()`; `main()` lost its `return 0`).

None of the three were caught by boundary-line verification prints -- all confirmed the edges of referenced segments, not completeness or order. `ast.parse()` didn't catch #3 either (nested-wrong code is still syntactically valid).

**Pairs with:** M-109 (check before write), M-054 (a claim -- "the boundaries look right" -- is not evidence the whole thing is right).

(Captured 2026-07-23, three of Claude's own mistakes in one session, all self-caught.)

## M-111 -- M-097's "persists indefinitely" theory was wrong; headless Claude Code OAuth tokens do not reliably refresh

**Rule:** `claude -p` (headless/non-interactive) does NOT share the same reliable auto-refresh behavior as an interactive session. Per Anthropic's own Claude Code CLI issue tracker (multiple confirmed reports: anthropics/claude-code #28827, #50743, #79685, #80091), the OAuth access token has a short TTL (~8 hours) and is not reliably refreshed when the CLI is invoked headlessly, while a concurrent interactive session on the same machine keeps working. A script that calls `claude -p ... --chrome` roughly once a day should be expected to hit a 401 on a routine basis, not treated as rare. M-097's "a login persists indefinitely under normal use, so this was a one-time bootstrap gap" was reasoned from Anthropic's docs on LOGIN expiry (the multi-day/long-lived kind, code.claude.com/docs/en/authentication's 3-day warning) -- a separate, longer-lived mechanism from the short-lived ACCESS TOKEN refresh problem specific to headless mode. Two different expiry mechanisms were conflated.

**Trigger:** Real recurrences on 2026-08-12 and 2026-08-19 (a third, 2026-08-18, per Tony directly -- undocumented in todo.md, matching the exact recording-gap risk M-097 itself warns about). Three occurrences in five weeks, the last two on consecutive days, directly contradicts "very likely a one-time gap."

**Fix:** Not built this session. Two real candidate directions surfaced, neither yet tested: (1) route the Chaikin batch through Tony's already-running interactive Claude Code session (`--continue`/`--resume`) instead of an independent `-p` spawn, since interactive sessions don't hit this bug; (2) `claude setup-token` issues a long-lived (1-year) credential, but per code.claude.com/docs/en/authentication it "can only make model requests, so it can't establish Remote Control sessions" -- unconfirmed whether `--chrome` browsing counts as a Remote Control session, which would rule this option out for this specific use case. This entry corrects M-097's root-cause claim only; M-097's actual fix (the `claude auth status --text` pre-flight guard, loud-not-silent) remains valid and unaffected.

**Pairs with:** M-097 (corrects its stated root cause, not its shipped fix), WO-P300-E4.009 (loud-detection WO this failure mode keeps exercising).

(Captured 2026-08-19, Claude's own correction of a prior session's theory, prompted by Tony asking for root cause on a recurrence.)








## M-112 -- A WO's "WHAT WAS BUILT" section can go stale even when the WO itself is never touched -- a LATER, unrelated WO can quietly retire the code it describes

**Rule:** M-111 documents drift in a WO's own Status header. This is a different failure: WO-P300-E4.009's Status header was never wrong, but its "WHAT WAS BUILT" section (Tee-Object capture + failure-phrase match + red banner + $LOG line, built into P_300_RunAllDailyEvals.ps1's inline Chaikin chain) stopped describing real production code on 2026-08-12, when WO-P800-E4.001's schema-driven migration replaced that inline chain with a call to Hub-root RunChaikinBatch.ps1 -- a script with no output capture, no phrase matching, no banner, and no log file at all. Nobody cross-checked E4.009 against the code WO-P800-E4.001 was replacing, because E4.009 wasn't the WO being worked. A WO can be 100% internally consistent (header matches body) and still be entirely wrong about what code currently exists, if a later WO in a different project changes the ground under it.

**Trigger:** 2026-08-21, first real Chaikin batch failure since the migration (0/8 notes updated, WebFetch-403 fallback instead of a login wall). Went looking for the promised red banner and $LOG entry to confirm E4.009's detection fired -- neither exists in the current code. The failure WAS caught, just by a different, undocumented mechanism (P_300_RunAllDailyEvals.ps1's post-run vault-note check, added by WO-P800-E4.001 for an unrelated reason -- verifying enrichment succeeded, not originally framed as E4.009's replacement).

**Prevention:** When a WO changes a shared call path (a script another WO's "WHAT WAS BUILT" section describes calling into), grep the ledger for other WOs referencing that same script/mechanism before closing -- not just the WOs in Affects:. WO_COMPLETION_GATE.md's Caller Propagation check (ref WO-P115-E2.001) covers callers of a changed function; it doesn't currently cover WOs whose own acceptance criteria describe the code being replaced. Candidate fix, not yet proposed to Tony: extend Caller Propagation's checklist item to include "other WOs describing this code path" as a category to search, not just active call sites.

**Pairs with:** M-111 (header/body drift within one WO), M-054 (live artifact over any document), WO-P300-E4.009, WO-P800-E4.001.

(Captured 2026-08-21, Claude's own finding, prompted by Tony providing real failure-run console output and flagging "not clean.")


## M-113 -- Claude in Chrome "Your approved sites" is a persistent, browser-level grant, not per-conversation -- but two known Anthropic-side bugs can make it misbehave

**Rule:** Once a site shows under the extension's Permissions -> "Your approved sites" with a Revoke button, that's an "always allow" grant that persists across separate sessions/tab groups/conversations until manually revoked -- confirmed live 2026-08-21: Tony approved members.chaikinanalytics.com in his own side panel, and a completely separate MCP tab-group session (this chat) navigated to the same domain immediately after with zero prompt. Not scoped to the approving conversation.

**Known failure modes (Anthropic-side, not ours), if the prompt ever recurs unexpectedly:**
1. anthropics/claude-code#74715 -- "Always allow" sometimes persists as `duration:"once"` instead of `duration:"always"` in the extension's storage; the site never actually lands in the approved list despite the user clicking Always Allow, so the prompt keeps firing every action.
2. anthropics/claude-code#58464 / #57219 -- domain shows correctly under "Your approved sites" (recent Last Used timestamp and all) but `navigate` calls still return "permission_required" / "Navigation to this domain is not allowed" anyway -- a sync gap between the approval store and the navigate permission check.

Neither hit us on 2026-08-21 -- the approval stuck cleanly and navigate worked immediately, no retry needed. Listed here so a future recurrence isn't mistaken for something P_300 broke.

**Accepted workaround (Tony's call, 2026-08-21):** if Chaikin (or any approved site) unexpectedly re-prompts, Tony manually re-approves once -- acceptable as a one-off. Becomes worth real investigation only if it recurs repeatedly (pattern, not a single blip) -- same one-off-vs-repeatable threshold this Hub already applies to the Chaikin OAuth 401 recurrences (M-111).

**Pairs with:** M-111 (headless auth reliability, same "one-off is fine, pattern needs investigation" threshold), WO-P300-E4.009 (this permission model is the foundation of the MCP-driven Chaikin pull that replaced `claude -p --chrome` for today's real batch).

(Captured 2026-08-21, Tony's own policy call after Claude found and explained the two known upstream bugs.)



## M-114 -- "No usable cache, full O(N^2) rescore required" was declared from the JSON fingerprint alone; the eval already existed on disk, and the machinery to rebuild it in minutes had been built a month earlier

**Rule:** Before declaring that a long recompute is required, check ALL THREE places a walk-forward result can live, not just one: (1) `outputs\reports\eval\walkforward_*.txt` -- every promote writes a post-batch report for the full catalog, named after the STAGING db (`walkforward_staging_ingest_mined_*`), which is byte-identical to the live catalog it was promoted to; (2) `topk_cache` on the live catalog -- maintained on every promote via `update_for_new_batch` (new pids scored + all displaced existing pids rechecked, including backfilled anchor dates); (3) only then the JSON cache (`models\eval_cache\`), whose fingerprint is keyed to the PRE-batch catalog and will miss after every promote by design. If (1) is missing, `application\reconstruct_pre_batch.py` (WO-P300-E5.004 Part A, 130s at N=14,812, 25/25 exact vs. real DTW) rebuilds the batch from (2). `run_eval_loop.py` is the cold-path tool for a catalog with no `topk_cache` -- it must never be pointed at the live catalog.

**Trigger:** 2026-08-27/28 session concluded WO-P300-E5.006 step 3 was BLOCKED on a ~214.5h uncached run, built `P_300_RunEvalLoop_KeepAwake.bat`, and planned a checkpoint/resume layer -- all because `read_cached_walk_forward` returned None on the 42,955-fingerprint JSON. Verified 2026-08-29: `walkforward_staging_ingest_mined_default_20260826_130212.txt` already holds all 44,399 patterns x 5 horizons (221,996 lines, last row VYX 2026-07-28 corpus_size 44,396), written by the 08-26 promote (`BulkAddPattern_20260826_111500.log`: "topk_cache populated on staging: 1444 new pids, 42341 existing pids rechecked"). The backfill concern (1,438 of 1,444 new pids with historical anchor dates) is exactly what the recheck loop handles.

**Prevention:** Any "must rescore" conclusion in this project cites the report-folder listing and the live `topk_cache` row count in the same message. The KeepAwake eval wrapper stays on disk but is not run; the checkpoint plan is dropped. A blocker entry in a WO gets the same evidence bar as an acceptance criterion (M-100) -- "no cache" was asserted from one lookup, not three.

**Pairs with:** M-082 (re-deriving instead of re-running proven logic -- E5.004 solved this exact shape), M-100 (premises need evidence), M-054 (live artifact over session memory), WO-P300-E5.004, WO-P300-E5.006.

(Captured 2026-08-29, Claude's own finding after Tony challenged the 214.5h estimate: "we definitely did not build this environment correctly that any process would take this long on 44,000 records.")
