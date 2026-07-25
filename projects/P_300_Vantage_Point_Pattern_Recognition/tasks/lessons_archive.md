# P_300 Lessons Archive

**File:** `tasks/lessons_archive.md`
**Companion to:** `tasks/lessons.md` (live file)
**Retention standard:** WO-P000-E8.001
**First archive pass:** 2026-07-22

This file holds lessons removed from the live `tasks/lessons.md` to keep
it under its ~40-entry/~70KB cap. Nothing here is deleted -- full text
preserved exactly as it appeared in the live file. Entries are grouped
by why they were archived, in the order they were removed from the live
file (which is itself close to, but not strictly, numeric M-order, since
the live file mixes chronological append order with a couple of
sub-numbered sections).

## Why these 37 were archived (2026-07-22 pass)

- **12 lessons** already cited by number inside an active SKILL.md
  (`p300-project-context` or `python-project-architecture`) -- the rule
  is enforced where Claude actually reads it every session; this copy
  was redundant. M-002, M-004, M-007, M-016, M-017, M-018, M-019, M-020,
  M-022, M-036, M-082, M-097.
- **3 lessons** self-superseded by their own later entry, still in the
  live file under a different heading. M-028 (explicitly marked
  RETIRED, see M-034), the original long M-059 (superseded by "M-059 --
  CODE FIX SHIPPED, 2026-07-10," which stays live), the original M-073
  (superseded by "M-073 Recurrence," which stays live with the
  corrected diagnosis).
- **8 lessons** promoted into `CLAUDE.md` as Locked Decisions --
  standing architecture/decision facts, not active bug watches. M-012,
  M-023, M-025, M-033, M-049, M-050, M-052, M-078.
- **14 lessons** resolved code fixes with no later lesson in the file
  ever citing them back (checked via every "Pairs with:" cross-
  reference in the file -- a real, later dependency is the signal kept
  a lesson live; these had none). M-053, M-060, M-061, M-062, M-064,
  M-065, M-067, M-068, M-069, M-074, M-076, M-077, M-088, M-098.

Everything else in the live file at time of this pass either had a real
later citation, was too recent to judge, or was left for a slower,
more careful second pass rather than a rushed call -- see WO-P000-E8.001
and the 2026-07-22 `tasks/todo.md` session entry for the full triage.

---
### M-002 -- One file per turn
**Rule:** When multiple files are queued, deliver one per response. Operator reviews. AI writes the next. No multi-file blasts.

### M-004 -- Dual delivery for documents
**Rule:** Standalone reference documents (architecture, lessons, SIP, SKILL) require BOTH disk write AND in-chat artifact. Disk for permanence, artifact for review. (Identified 2026-05-13.)

### M-007 -- Direct file writes when filesystem MCP is available
**Rule:** At session start run `tool_search` for `filesystem:write_file` or `windows-mcp:FileSystem`. When available, write all project files directly. Never use the sandbox-download-and-move pattern. (Confirmed 2026-05-13.)

### M-012 -- Set PRAGMA foreign_keys = ON immediately after every sqlite3.connect()
**Rule:** SQLite's `foreign_keys` pragma defaults to OFF per-connection. Every connection must execute `conn.execute("PRAGMA foreign_keys = ON;")` immediately after `sqlite3.connect()`. All connections go through `python/utilities/db_connect.py`. (Identified 2026-05-14.)

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

### M-022 -- Target = anchor workflow for VP pattern capture
**Rule:** The operator-chosen target date IS the launch/anchor. Pattern setup = 20 bars BACK; forward labels = 5/7/10/15/20 trading days FORWARD. Filename: `Pattern_<TARGET_YYYYMMDD>_<CAPTURE_YYYYMMDD>_<SYMBOL>.xlsx`. (Identified 2026-05-18.)

### M-023 -- VP license/access constraints and thesis-flexible symbol substitution
**Rule:** Operator's VP subscription doesn't include all sector browses. When a recommended symbol is unavailable, operator names alternatives; Claude substitutes preserving thesis. (Identified 2026-05-18.)

### M-025 -- CWD discipline for `python cli.py`; folder convention drift on Pattern XLSX saves
**Rule (CWD):** Always invoke `python python\cli.py` from project root.
**Rule (folder):** Pattern XLSX files belong in `data\historical_patterns\`, NOT `data\historical\`. (Identified 2026-05-18.)

### M-028 -- Parameter sweeps on sparse catalogs must bracket the firing region
**Rule:** At N ~25 patterns, production-default thresholds may produce zero firing events. Bracket the signal-firing region first; then sweep outward. Re-run at N >= 50. RETIRED 2026-05-28 -- N=116 sweep completed; see M-034. (Identified 2026-05-19.)

### M-033 -- Catalog composition: 70:30 uptrend-to-pullback target; 3:1 ongoing maintenance ratio
**Rule:** Maintain catalog at ~70% uptrend / 30% pullback to hold baseline WR in 0.65-0.72 range where BUY/WATCH gates are meaningfully discriminating. For every 3 uptrend patterns added, add 1 pullback before the next uptrend batch.

**Pullback pattern criteria:** 15-25% decline across the pre-anchor 20-bar window, 3-5 bars of tight sideways consolidation. Anchor = first day of consolidation. Expected forward-label profitability: 30-40% at h=5.

(Captured 2026-05-21)

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

### M-049 -- ATR is a shared Wilder util computed at eval time, never re-fetched downstream
**Rule:** ATR (and any shared eval-time price computation) lives as a pure-domain utility in `shared_resources/python_utils/` and is computed by each evaluating project at evaluation time, on the OHLC bars already in memory -- never re-fetched by a downstream project. Import via the editable install (`from shared_resources.python_utils.atr import compute_atr_wilder`); no per-project copy, no sys.path side-channel. ATR uses full True Range (max of high-low, |high - prev_close|, |low - prev_close|) + Wilder RMA smoothing -- never a high-low-only or simple-average proxy. The function takes plain (high, low, close) tuples so it stays decoupled from any project's bar schema.

**Why (2026-06-10):** P_300's `_compute_atr_from_bars` was a high-low-only simple average -- it understated volatility on gappy names and produced tighter-than-true stops. Moving ATR to P_400 (the target authority) was considered and rejected: P_400 would have to re-read the bars at entry, but the eval project already holds them, so the computation belongs where the data is. Shipped as `shared_resources/python_utils/atr.py` v1.0 (+ test_atr.py 9/9, incl hand-computed Wilder 86/27); P_300 `daily_evaluate_pipeline` v1.16 consumes it.

(Captured 2026-06-10)

### M-050 -- Target ownership: eval projects emit a baseline; P_400 resolves the final target
**Rule:** Every evaluating project (P_300, P_115, future) emits the SAME baseline shape only -- guideline entry/target/stop + setup context (plus a candidate target if useful). P_400 is the single authority that resolves the broker-facing final target: it validates reward-to-risk, applies sizing/stop/council rules, and publishes the order-ready target. Eval projects feed P_400, never compete with it, and must not present their levels as execution-final. The `guideline_*` field names + the `position_size=0` sentinel encode this -- they only make sense if P_400 resolves.

**Why (2026-06-10):** Decided while upgrading ATR. P_300's ATR-derived stop/target are a candidate baseline, not the execution target. Enforcement is still OWED in P_400's build-out -- today P_400's only domain logic is `packet_classifier.classify(filename)`; no target resolver / RR / sizing exists yet, so P_300's guideline_target is the only target by default until P_400 builds it. signal_emitter docstring now marks its levels "candidate/baseline; P_400 resolves final."

(Captured 2026-06-10)

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

## Section 1.5 -- M-053

### M-053 -- Case-normalization must operate on the captured group, not the whole literal string
**Rule:** When a regex match has both literal case-sensitive segments and a variable-case segment (e.g. `Pattern_` / `.xlsx` literals vs. a `SYMBOL` group), normalize case AFTER the match -- on the captured group only. Never call `.upper()`/`.lower()` on the full input before matching against a pattern containing case-sensitive literals; it silently breaks the literals.

**Instance:** `vp_xlsx_reader.py` v1.3 (2026-06-16, O-009 fix) called `filename.upper()` on the whole filename before matching `_FILENAME_PATTERN`, which requires literal `Pattern_`/`.xlsx`. This caused **100% AddPattern ingest failure** from the moment v1.3 shipped -- caught 2026-06-17 09:25 (18/18 files failed in one run). Not caught at the time because the v1.3 fix was never smoke-tested against a normal correctly-cased filename, only against the RCl repro case (which also failed for the same reason, just attributed to a different cause).

**Fix (v1.4, 2026-06-17):** `_FILENAME_PATTERN` compiled with `re.IGNORECASE`; `_parse_filename()` no longer uppercases the input. Only `m.group("symbol").upper()` is normalized when building `PatternFileMetadata`. A PEH smoke-test script was staged at `04-Shared-Resources/verify/run_this.py` (5 cases incl. 2 of the real failed files) but no PASS/FAIL result was reported back -- verification instead came from the production re-run: 13/18 succeeded (vs 0/18 pre-fix); remaining 5 failures were genuine data issues (insufficient bar history / sheet-name mismatch), unrelated to this bug.

**STRUCTURALLY EMBEDDED 2026-06-17:** vp_xlsx_reader.py v1.4.

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

### M-067 -- A report-format column change silently broke a downstream regex parser for 3+ weeks with no error and no visible symptom

**Rule:** When a fixed-width or fixed-column console/report format changes (a column added, removed, or reordered), every downstream parser keyed to that format's exact column count must be updated in the same change, or grepped for and flagged. A regex anchored with `^...$` and a fixed number of capture groups doesn't throw when a line grows an extra column -- it just stops matching, silently, and the caller sees `None` with no exception. That failure mode is functionally identical to M-054/M-064's "clean exit is not evidence of correctness": nothing in the console output signals the loss.

**Failure mode captured 2026-07-03:** Enhancement 2 (2026-06-09, CE gate) added a `ce` (certainty-equivalent) column to `report_writer.py`'s per-horizon stats table, changing it from 7 columns to 8. `write_signal_to_obsidian.py`'s `stats_pattern` regex was never updated to match -- it has not matched a single stats-table row since 2026-06-09. Every P300 Obsidian note written since then shipped with `h5_win_rate`/`h5_mean_ret`/`z_score` silently `None`, stripped before the vault write (the write itself succeeded, so `[OK] written to vault` printed correctly every time -- the note existed, just with empty frontmatter behind a populated narrative). Caught only because the operator asked why frontmatter fields read `null` despite the narrative text having real numbers, prompting a direct read of the vault note rather than trusting the write confirmation.

**Fix:** Re-run against the 16 notes already in vault from the 2026-07-01 batch (via direct `parse_report_and_write` call per symbol, not a full pipeline re-run) -- verified via direct read of EPAM's note post-fix: all 5 horizons populated, values match the source report exactly, `note_version` incremented to 2 with `verdict_history` correctly recording the prior (empty) write.

**Pairs with:** M-051/M-054 (a successful-looking log line is not proof the underlying data is correct); differs in mechanism -- those were fabricated status strings, this is a format-drift parser silently going blind.

(Captured 2026-07-03)

### M-068 -- --clean's logging.disable() spans the whole pipeline run, swallowing success AND failure logs from any function that only reports via the logging module; and mean_return_pct needed the same *100 scaling at the emit call site that win_rate already gets

**Rule (visibility half):** `logging.disable(logging.WARNING)` in `daily_evaluate_pipeline.py main()` is set before `run_daily_evaluate()` runs and only cleared in `finally` after it returns -- it silences `logger.info`/`logger.warning` from EVERY function called during that window, not just the one it was intended to quiet. Any function whose only output channel is the logging module (like `signal_emitter.emit_signal_packet()`) becomes invisible under `--clean` regardless of whether it succeeds or fails. Same failure shape as M-043 (non-blocking errors need WARNING-level visibility) and the Obsidian writer's fix for the identical problem -- but this is a distinct instance, in a different file, never previously caught.

**Failure mode (visibility half), WO-P300-E1.004:** A real batch produced 10 vault notes but only 3 P_400 packets with zero trace of the other 7. PEH diagnostic confirmed the emitter was never broken -- all 7 emitted OK on replay outside --clean.

**Rule (scaling half):** A decimal-fraction stat (`mean_return_pct`, or anything in M-020's decimal-space convention) must have the `*100` scaling applied at the exact call site where it's formatted into a %-string -- each consumer scales independently, there's no single place it happens automatically.

**Failure mode (scaling half):** `mean_ret` passed into the SIGNAL_V2 rationale was missing the `*100` decimal-to-percent scaling that `win_rate` already gets -- wrong in every packet since Enhancement 1 (2026-06-08).

**Fix:** `daily_evaluate_pipeline.py` v1.21 -- Stage 5a now scales `mean_ret` by 100, matching `wr`. Verified via PEH harness (3 assertions, PASS): rationale renders +4.92% correctly; [OK]/[REJECTED] both print under `logging.disable(logging.WARNING)` with a stubbed vault_interface. Cosmetic only -- `guideline_stop`/`guideline_target` derive from ATR, not `mean_ret` -- but every SIGNAL_V2 packet's rationale text has been wrong since Enhancement 1 (2026-06-08) until this fix. Real-world confirmation pending the next live DailyEval batch's packet rationale text.

**Pairs with:** M-043 (non-blocking failures need WARNING-level, print-survives-disable visibility -- this is the same lesson recurring in a second file), M-020 (decimal-fraction convention -- this is the same convention's display-boundary rule missed at a second call site).

(Captured 2026-07-04)

### M-069 -- Chaikin batch trigger filtered vault notes by eval-run date; notes are filed under anchor_date (last close), so the filter matched nothing and silently skipped the batch on every run

**Rule:** `P_300_RunAllDailyEvals.ps1`'s post-eval Chaikin Power Gauge trigger scanned `trading_journal\TradeManagement\P300\` for files matching `$today*.md` (today = the date the eval script runs) and treated zero matches as "no BUY/WATCH symbols today." But `write_signal_to_obsidian.py` names vault notes by the pattern's `anchor_date` -- the last completed market close the signal is based on -- not the date the eval was run. Since market data always lags at least one session, `$today` almost never equals the anchor date baked into the filename, so the filter matched nothing on essentially every run and "No BUY/WATCH symbols today -- skipping Chaikin batch" fired even on runs with 15 actionable signals (caught 2026-07-07: 8 BUY + 7 WATCH from a 19-symbol DailyEval batch, all silently skipped). No error, no exception -- the `.Count -eq 0` branch is a valid, silent no-op path, same failure shape as M-067 (schema drift, zero visible symptom) and M-068 (logging.disable() swallowing status).

**Fix:** Removed the vault-filename-date dependency entirely -- `$actionable` is now parsed directly from this run's own `$LOG` via `Select-String -Pattern "SIGNAL REPORT\s+(\S+)\s+(BUY|WATCH)"`, which reflects exactly what this run classified regardless of what date got stamped on the vault note.

**Generalized rule:** any trigger/gate logic that infers "did X happen this run" by re-deriving it from a downstream artifact's filename or timestamp (rather than from the run's own direct output) is fragile to any mismatch between "when this ran" and "what date this data is about" -- prefer parsing the run's own log/return value over reconstructing state from written artifacts.

(Captured 2026-07-07)

### M-073 -- create_file can report success while silently failing to overwrite an existing file; verify with a direct read after every write, not just after edits

**Date:** 2026-07-08
**Trigger:** Two files in the same session (`infrastructure/research_catalog_io.py` and the PEH pair at `Agentic-Hub-Governance/verify/run_this.py` + `run_this_context.txt`) were written via `create_file`, reported success, and were then staged/referenced as if present -- but a later direct `mode=info` check showed the target files either did not exist at all (`research_catalog_io.py`) or still contained old, unrelated content with an unchanged mtime (`run_this.py` still held M-071's schemas.py verification script). No error surfaced at write time in either case.

**Root cause:** `create_file` appears to silently no-op (or fail without raising) when the target already exists or under some other untriggered condition, rather than overwriting or raising. This is a different failure shape from M-048 (edit_file batch atomicity) and M-056 (a human paste overwriting a file) -- here the write tool itself is the unreliable step, with no operator action and no exception in the loop.

**Compounding factor:** A message appeared in the conversation, styled as if reporting a real terminal run ("confirmed by direct inspection... 5 checks... junction... MD5 identical"), describing behavior that did not match anything actually staged this session. It was not authored by this session and described a stale/unrelated file (M-071's script) that happened to be sitting at the same path due to the create_file failure above. Correctly treated as suspect and not acted on -- but it took a direct disk read to establish what was real, which is the reusable lesson: a claimed console result is not evidence (M-054's principle), and neither is a tool's own "success" response to a write call.

**Fix / working pattern:** After any `create_file` (or Write-shaped) call, follow with `windows-mcp:FileSystem mode=info` (size + mtime) or `mode=read` before treating the file as delivered -- especially before staging a PEH script that imports it, or telling the operator it's ready to run. If the file is stale or missing: delete the stale file first, then use `windows-mcp:FileSystem` write mode with `overwrite=true` (confirmed reliable in this session) rather than retrying `create_file`.

**Generalized rule:** Extends M-054 ("a closure note is a claim, not evidence") one level earlier in the pipeline -- a tool's own success response to a *write* is also a claim, not evidence, until a separate read confirms it. This applies whether the write was create_file, an edit, or a script's file output.

**Pairs with:** M-048 (edit_file batch atomicity -- verify after multi-edit), M-054 (closure notes are claims), M-056 (verify file integrity before trusting behavior), M-070/M-071 (PEH two-file contract + sys.path correctness -- same "verify the harness/delivery mechanism itself, not just the thing under test" instinct).

(Captured 2026-07-08)


### M-074 -- A "loosely computed" expected_delta is a bug waiting for the first-hit-per-symbol case, not an acceptable imprecision

**Date:** 2026-07-08
**Trigger:** `bulk_hit_writer.py` v1.0's `write_bulk_hit()` hardcoded `expected_delta["symbols"] = 0` and `["source_files"] = 0`, with a docstring comment explicitly acknowledging the shortcut ("delta is computed loosely here (0 assumed)... deferred as unnecessary precision for a research-only catalog"). Against a scratch catalog with zero prior rows, every single hit's first encounter with a new symbol or source_file genuinely creates a row (+1, not +0) -- `verify_and_promote_research`'s delta check then rejected every hit in the run, all 28 real detections against `5_Pattern_SPY.xlsx`, with the master DB ending up empty (0 pattern_instances, no SPY row) despite a real, successful sweep upstream.

**Root cause:** The docstring reasoning treated "which table deltas matter for correctness" as a judgment call, but the hollow-instance check and the delta check are two INDEPENDENT tripwires -- passing the delta check is a precondition for `verify_and_promote_research` to even reach the promote step, not an optional precision knob. A hardcoded 0 is wrong (not just imprecise) on literally the first hit for any new symbol or file, which given this pipeline's purpose (scanning many symbols) is the common case, not an edge case.

**Fix:** Check row existence (`SELECT 1 FROM symbols/source_files WHERE ... = ?`) immediately BEFORE the corresponding insert call, and set `expected_delta` from that boolean rather than a constant. Symmetric with `insert_source_file`'s own pre-existing duplicate-filename check just a few lines below -- the existence check was already half-present in the function for a different reason and should have prompted noticing the delta assumption was wrong.

**Generalized rule:** When a delta/row-count check exists specifically to catch write mistakes (M-048's family), never hardcode an expected value for a table whose row count depends on data-dependent state (first-seen vs. already-seen). Compute it from a real existence check, or don't populate that key in expected_delta at all if the check can't be made precise cheaply -- a wrong assertion is worse than no assertion, because it silently rejects every correct write instead of only catching real errors.

**Pairs with:** M-048 (verify after any operation with an atomicity/delta contract), M-054 (a comment justifying a shortcut is a claim about correctness, not evidence -- this one was checked and found wrong the first time it was exercised against real data).

(Captured 2026-07-08)

### M-076 -- windows-mcp:PowerShell wedged (M-030 recurrence) on a routine sqlite verification query, not a heavy job

**Date:** 2026-07-09
**Trigger:** First real WO-P300-E2.001 bulk-extract run against 3 real symbols (AAPL/DE/SPY) completed clean via the operator-run `.bat` (5 STRICT / 73 RELAXED, console claim). Attempted to verify the claim directly against `bulk_research.db` (M-054 discipline) with a single `python -c "import sqlite3; ..."` one-liner via `windows-mcp:PowerShell`, reasoning it was trivial/sub-second and therefore exempt from M-030's "non-trivial jobs" scoping. Call hung the full 4 minutes and wedged the PowerShell MCP for the rest of the session -- identical failure shape to M-030, just on a much smaller job than M-030's examples.

**Root cause:** M-030's rule ("do not invoke `python -c` via `windows-mcp:PowerShell`") has no size/complexity exception in practice -- the hang is tied to the `python -c` invocation shape itself, not job weight. Treating "trivial" as a mitigating factor was the same reasoning error M-057 warns against in the opposite direction (assuming a near-4-min job failed when it hadn't) -- here, assuming a sub-second job was safe because it was small.

**Recovery:** Fell back to PEH (two-file `run_this.py` + `run_this_context.txt` staged to `verify\`, operator runs in ISE) for the same query -- exactly the fallback M-055/peh-handoff already prescribe. No PowerShell retry attempted after the wedge (M-030's stated behavior: all subsequent calls hang for the session once wedged).

**Generalized rule:** M-030's ban on `python -c` via `windows-mcp:PowerShell` has NO exception for trivial/short/read-only jobs. Any Python execution beyond a bare interpreter-path check goes through `python script.py` (still risky per M-030) or PEH, never `-c` with embedded code, regardless of apparent simplicity. Restart Claude Desktop before this session's PowerShell tool is needed again.

**Pairs with:** M-030 (original rule), M-055 (INIT-path Python must never go through windows-mcp:PowerShell), M-057 (windows-mcp Python has a hard ceiling but a different failure mode -- this entry confirms M-030's hang is orthogonal to job size, not just job duration).

(Captured 2026-07-09)

### M-077 -- VP predictive columns can render as empty string in the pre-backfill window, not just zero or infinity; same field, third blank spelling

**Date:** 2026-07-09
**Trigger:** WO-P300-E2.001's second real bulk-extract run (12 Basic Materials symbols) failed on LIN: `Cannot coerce '' to float at row 1853 col 13` (roc_pct, per bulk_ingest_manifest.json). 11 of 12 other symbols in the same run succeeded clean. Row 1853 of 2512 (descending dates) falls in the pre-2021-07-14 window this WO's own Phase 0 finding already documented as "predictive columns zero/blank" -- but the existing coercer (M-072) only handled the infinity spelling ('∞'), not a genuinely empty string.

**Root cause:** M-072 treated the infinity-symbol case as the complete fix for "VP predictive columns can render unparseable strings near backfill boundaries," but the underlying phenomenon (no data yet in the pre-backfill window) apparently renders differently depending on the specific column/row -- infinity in one case (a divide-by-near-zero), empty string in another (genuinely nothing computed yet). Fixing one spelling doesn't cover the family.

**Fix:** `bulk_grid_reader.py` v1.1 -> v1.2 -- `_coerce_cell`'s float branch now also maps a stripped-empty string to `0.0`, matching the zero convention the WO's Phase 0 finding already established for sibling predictive columns in the same pre-backfill period. Sits alongside the existing `'∞'`/`'inf'` mapping, same function, same branch.

**Verification (two-step, both PEH per M-054):**
1. Parse-only check (no catalog writes) against the real LIN file -- confirmed clean parse, bar_count=1929 (not 2512 -- separately explained as correct: LIN/Linde plc only listed on NYSE since 2018-10-31, a real corporate-history fact, not a parsing defect). Early bars' roc_pct read 0.0 exactly where blanks were; recent bars show real nonzero values -- confirms the fix engaged only where needed.
2. Real `P_300_BulkExtract.bat` re-run -- checkpoint correctly skipped the 14 already-complete files, processed only LIN, 2 STRICT/19 RELAXED landed clean. DB-verified: 355 total instances (56 STRICT/299 RELAXED) across all 15 symbols, 0 hollow.

**Generalized rule:** When a coercion fix targets one confirmed real-data spelling of "no data here" (M-072's infinity case), don't assume that's the only spelling the same underlying VP phenomenon produces. The pre-backfill blank window is a documented real condition (Phase 0 finding) that can surface as zero, infinity, OR empty string depending on the specific field/computation -- treat the next occurrence in a sibling column as expected, not surprising, and check whether the existing handling already covers it before writing a new one from scratch.

**Pairs with:** M-072 (same field, same file, same root phenomenon -- this is its second real-data instance), M-054 (verified via direct parse + DB read, not console trust alone).

(Captured 2026-07-09)


### M-078 -- An approved file plan is not project state until it's written to todo.md; "go ahead" + immediate session-end loses it

**Date:** 2026-07-10
**Trigger:** Prior session drafted WO-P300-E2.002's full 11-file plan (config.py -> schemas_bulk.py -> schemas_sector_analysis.py -> domain/sector_stats_calc.py -> infrastructure/sector_map_loader.py -> sector_backfill_io.py -> sector_stats_io.py -> sector_report_writer.py -> application/phase5_analysis.py -> cli.py -> P_300_Phase5Analysis.bat), operator approved with "Go ahead?" answered by "Let's start a new session" -- but that closing message came before any write to todo.md/lessons.md. The plan existed only in that session's chat transcript. Next session's INIT read todo.md/lessons.md/WO-P300-E2.002.md directly (M-054 discipline) and correctly found no plan recorded anywhere -- leading to a false "you don't actually have a plan" correction that wasted a full round-trip until the operator pasted the original chat excerpt.

**Root cause:** M-003 requires approval before writing code, but nothing in the INIT/task-lifecycle protocol requires the approved plan itself to be persisted to todo.md before a session can be considered closed. An approval that lives only in chat scrollback is invisible to the next session by design (ephemeral environment, M-007) -- exactly the failure mode the whole Check-In/Check-Out and todo.md-as-ground-truth discipline exists to prevent, just one step earlier than usual (plan-level, not code-level).

**Fix (this session):** Plan written to todo.md under WO-P300-E2.002 as an explicit Active/Approved entry with full file table, immediately following this lesson.

**Generalized rule:** The moment a file plan gets an explicit operator go-ahead (M-003), write it to todo.md in the same turn -- before asking "anything else" or accepting a session-end signal. An approved plan is a task-lifecycle artifact (Section 5, "Plan First") exactly like the plan-before-code write itself; it does not get a pass on the Check-Out discipline just because it's still pre-code. Never treat chat-only content as project state once a session boundary is crossed (pairs with M-054's broader principle, one layer earlier).

**Pairs with:** M-003 (plan approval), M-054 (closure notes / claims are not evidence -- symmetric here: a plan discussed but not written is not evidence of a plan either), M-007 (environment is ephemeral, nothing persists outside disk writes).

(Captured 2026-07-10)


### M-082 -- Widening a value's valid range doesn't just affect its own logic; every downstream formula that reused it under the old range needs re-auditing

**Date:** 2026-07-12
**Trigger:** pattern_miner.py v1.2 extended `_qualifying_move()`'s
search from a 20-trading-day cap to `MINE_MAX_SCREEN_DAYS=180` (M-081
-- a deliberate, correct change). The dedup step in `mine_bars()`
reused the same `horizon_days` value as its suppression-window length
(`window_end = idx + cand.horizon_days`) -- a formula written when
`horizon_days` could only ever be 5-20. Extending the search to 180
silently turned that same formula into "suppress up to 180 trading
days of everything else in this class," swallowing genuinely
independent later launches. Real validation confirmed it on AMZN: a
66-day extended find suppressed a real, independently-verified
breakdown 63 trading days later -- caught only because Claude Code
traced the standalone screening result against the final output
before reporting a raw miss count, rather than reporting 13/84 (far
below the ~36/84 estimate) as a black-box number.

**Root cause:** `horizon_days` was silently doing two different jobs
that happened to share a value only because both were bounded by the
same 20-day cap at the time: (1) "how far out did the qualifying move
get proven" (the search's own concern, legitimately unbounded after
M-081) and (2) "how long should this bar's neighborhood be treated as
still the same launch" (dedup's concern, a genuinely short-range
question that has nothing to do with how long the move eventually took
to prove out). Widening the field for reason (1) silently broke the
implicit assumption reason (2) depended on -- the two concerns were
never actually the same thing, they just coincided under the old cap.

**Fix:** Dedup suppression window capped independently at
`max(FORWARD_HORIZONS)=20` via `min(cand.horizon_days, _dedup_cap)` --
the search stays unbounded (M-081's fix preserved), only the
suppression window is capped. Two different concerns, two different
bounds, no longer conflated through a shared variable.

**Generalized rule:** When widening the valid range of a value (a
config cap, a computed field, a parameter default), grep for every
OTHER place that value is consumed, not just the code path whose range
is being changed. A downstream formula can be correct under the old
range and silently wrong under the new one without any type error,
exception, or obviously-broken code -- the bug only shows up as a
number that's mysteriously worse than expected, and tracing it
requires checking a standalone unit (does this ONE candidate qualify
on its own?) against the aggregate output (does it survive to the
final list?) to localize which stage introduced the loss.

**Pairs with:** M-081 (the change that exposed this -- correctly
widening one thing surfaced a hidden coupling elsewhere), M-075/M-080
(same family of "a parameter's implicit contract broke when something
around it changed," different specific mechanism -- there it was a
missing override, here it's a reused value whose valid range shifted).

(Captured 2026-07-12)


### M-088 -- A plain (non-raw) triple-quoted docstring containing a literal Windows path fails at import time, before any code runs

**Found:** 2026-07-13, WO-P300-E3.002 part 11, first widened `resolve_pick` script.

**What happened:** `run_this.py`'s module docstring (plain `"""..."""`) ended with a `Run with:\n  C:\Users\Trader\...\python.exe run_this.py` line -- standard PEH-script boilerplate, present in every staged verify script this project uses. `\Users` parsed as the start of a `\UXXXXXXXX` 8-hex-digit unicode escape; `sers\Tr...` isn't valid hex, so the script threw `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes` at line 1, before `main()` or even the module body executed. The script's own `ROOT = Path(r"C:\Users\...")` line further down was already correctly raw -- only the docstring wasn't.

**Root cause, generalized:** this project's PEH two-file contract (M-070) puts a literal Windows path in nearly every `run_this.py`'s header docstring (`Run with: C:\Users\Trader\.conda\envs\p140\python.exe run_this.py`). A plain docstring is not a raw string -- `\U`, `\u`, `\x`, `\N{...}` all remain live escape sequences inside it. This is a recurring shape, not a one-off: same family as M-032's `%VAR%`-in-parens batch trap, just Python's escape rules instead of batch's.

**Rule:** any module docstring containing a literal Windows path (most PEH scripts, given the standard "Run with:" footer) must be `r"""..."""`, not `"""..."""`. Check this BEFORE staging any `run_this.py` -- a fast, mechanical thing to verify (does the docstring contain a backslash-path AND start with plain `"""`), catchable by inspection without needing to actually run the script.

### M-097 -- Undocumented live scripts are invisible at INIT; auth failures can span two unrelated layers
**Rule:** A script that runs live in production but exists in none of tasks/lessons.md, tasks/todo.md, or the project SKILL is invisible to every future INIT -- it can only be found by accident (a console paste that doesn't match anything known) or an ad-hoc grep after the fact. Any script invoked directly by the operator (not just ones Claude authored) needs at minimum a Critical Paths row in the SKILL once discovered, so it surfaces automatically going forward. Separately: when a console error says "not logged in," verify WHICH layer is unauthenticated before diagnosing -- a website login in the operator's browser (e.g. chaikinanalytics.com) and a CLI tool's own OAuth session (`claude /login`) are two completely separate auth stores; a screenshot proving one is logged in says nothing about the other. Confirm via the failing layer's own status check, not an adjacent one that merely looks related.
**Trigger:** `P_300_RunChaikinBatch.ps1` (standalone) and an identical inline block at the end of `P_300_RunAllDailyEvals.ps1` -- both call `claude -p $prompt --chrome` to pull Chaikin Power Gauge ratings for the day's BUY/WATCH symbols -- existed live and had run in production, but were undocumented anywhere Claude reads at INIT. First surfaced 2026-07-15 via an operator console paste ("Running Chaikin Power Gauge batch..." / "Not logged in · Please run /login") that matched nothing in memory; found only by grepping `*.ps1`/`*.bat` in the project root for "Chaikin" after initially (incorrectly) dismissing it as unrelated third-party website activity based on a browser screenshot, rather than checking the actual script.
**Fix shipped same session:** both scripts now run `claude auth status --text` before calling `claude -p ... --chrome`; a non-zero exit prints a clear "SKIPPED -- not authenticated, run claude /login" message instead of the CLI's own terse one-liner. Per Anthropic's own docs (code.claude.com/docs/en/headless), `claude -p` shares the same auth/session store as interactive mode and a login persists indefinitely under normal use -- so this was very likely a one-time bootstrap gap (Claude Code never logged in on this machine before), not a recurring expiry. The guard exists for the rare case it does recur, so the failure is loud instead of silent.
**Applies to:** P_300 (any operator-invoked script shelling out to an external CLI/service); any future project where a live, working script could exist entirely outside Claude's INIT-time visibility.

(Captured 2026-07-15)

### M-098 -- Walk-forward's temporal-exclusion rule makes most "post" re-scoring provably unnecessary
**Rule:** Before parallelizing or caching a batch computation to make it faster, check whether the computation's own eligibility rule already proves most of the batch doesn't need to be redone at all -- that's a bigger and more certain win than execution-strategy speedups, and it's easy to miss when the immediate symptom (a long-running promote) makes "make it faster" feel like the obvious fix.
**Trigger:** WO-P300-E4.003 shipped pre-batch caching + parallel scoring for M-079's walk-forward eval (real result: ~30.8 min for one full pass at 8175 patterns, cache now covers the "pre" half). During closure, Tony asked whether this eval is necessary on every BulkAddPattern run -- answering that question surfaced that `_corpus_pids()`'s STRICT EARLIER-anchor_date rule means none of the existing catalog's scores can ever change when today's 0-15 new same-day picks are added. "Post" was re-scoring the entire staging catalog anyway, when only the new patterns needed real scoring.
**Fix:** Not built this session -- filed as WO-P300-E4.004 (incremental post-batch scoring: reuse cached "pre" results for unaffected pids, score only newly-inserted pids against the full existing corpus, explicit anchor-date guardrail assertion that falls back to full re-score if ever violated). Requires its own plan + go-ahead; not bundled into E4.003's bug fix.
**Applies to:** P_300 (any future eval/report loop with a temporal or other structural exclusion rule); any project where "this is slow" gets answered with parallelization before checking whether the slow work is even necessary.

(Captured 2026-07-16)

