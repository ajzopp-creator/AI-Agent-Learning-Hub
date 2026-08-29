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

---

## Why these 28 were archived (2026-07-26 pass)

Mechanical criterion, applied uniformly: (1) resolved same-session with
fix shipped and no later lesson citing it back (M-070,071,072,073-recur,
080,081,083,084,086,087,090,091,092,093,096,099,100,101,102,104,107,108),
(2) closure-only entry whose owning fix/WO is already settled (M-059 code-
fix note, M-095 -- systemic fix filed as WO-P300-E4.002), (3) dated status
snapshots fully superseded by tasks/todo.md Current State + CLAUDE.md
Locked Decisions (the entire former Section 4), (4) historical operational
notes superseded by later catalog/data state (O-002, O-007). M-008
(bash_tool time check) archived as superseded by M-091's real practice
(Get-Date via windows-mcp:PowerShell).

Kept live and explicitly NOT archived despite being resolved: M-079 (still
heavily cross-referenced by other live entries), M-085 and M-094 (both
still Open, Tony's call pending on each), M-103/105/106/109/110 (recent,
still-live operational risks).

---
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


### M-008 -- Check bash_tool for wall-clock time before falling back
**Rule:** When displaying the session header time, run `bash_tool` with `TZ='America/New_York' date '+%A, %B %d, %Y -- %H:%M ET'`. The "time not available" fallback applies ONLY when no shell tool is reachable. (Identified 2026-05-13.)


### O-002 -- Active symbol inventory (Stage 5 re-ingest scope)
**Lesson:** Distinct symbols for Stage 5 re-ingest: SPY, QQQ, MSFT, NVDA, AAPL, CTRA, ATGE, VOD, CME, TR, LYV, FSLY, NFLX, APPN, BRK_A, ITA, MSA, PG + singletons (HL, IPI, ICE, OII, POET, TXRH, DELL, DNN, ASTS, ESVIF). Singletons require fresh VP captures.


### O-007 -- Volatility-divergence flag first production validation (2026-05-20)
**Lesson:** First live multi-candidate eval: PLAY 2.79x and WDAY 2.14x both STRONG fires, both PASS class. Flag surfaced correctly without gating. MILD band may be too narrow -- re-evaluate at 50+ candidates.


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




---

## Third archive pass -- 2026-08-29 (age-based: oldest Section 1 entries not referenced in SKILL/SIP/CLAUDE.md)

**Archived Last-Updated history line from lessons.md:**

**Last Updated:** 2026-07-12 (WO-P300-E3.001 Scanner Loop built + PEH-verified 7/7 -- 5 files: archive_scanner_file.py NEW, scanner_report_writer.py NEW, scanner_loop.py NEW, cli.py v1.11 +scanner-loop, config.py v1.12 +SCANNER LOOP section. Data-source decision resolved same-day: reuses IntelliScan's native crossover screen + existing bulk_grid_reader.py/bulk_pattern_detector.py unchanged, point-in-time only, STRICT-only, report-only (no catalog write). M-080 added: missing reports_dir override forced test monkeypatching, same family as M-075 -- fixed at the source, not just in the test. data/bulk/nightly_scan/ folder created; real nightly-export run is next, separate step.) | 2026-07-08 (WO-P300-E2.001 Bulk Extraction: spec reviewed, scan decoded from .isc, Phase 0 verified on SPY/AAPL/DE exports (VP backfills predictions only 5 yr, boundary 2021-07-14), config.py v1.9 shipped + PEH-verified 11/11. M-070 added: PEH is a two-file contract -- run_this.py + run_this_context.txt written together, always. PowerShell MCP wedged mid-session per M-030; recovery = Claude Desktop restart.) | 2026-06-29 (ledger-fill produced its first real output ever: 4 stacked bugs found and fixed in one session -- M-060 date format, M-061 yfinance MultiIndex columns, M-062 query_unfilled checked the wrong column, M-064 persist-only-on-full-fill discarded every partial outcome. M-063 widened the fetch window. Result: h5=115/h7=97/h10=58/h15=2/h20=0 fully real, verified via before/after counts. See M-060 through M-064.) | 2026-06-29 (Ledger dedup: 175->142 rows, 33 duplicates removed across 26 groups -- COHR fired 6x, an entire 06-12 batch re-fired wholesale on 06-13/06-15. M-059 added: insert_fired_signal() has no uniqueness guard; code fix still OWED. Backup saved before delete; live-recount safety check matched dry-run exactly.) | 2026-06-28 (AddPattern batch: 31/32 ingested clean, 1 rejected as true duplicate (DOCU, source_file_id=277) -- catalog 331->362 patterns / 245 symbols. DailyEval batch: 22/22 clean, 9 BUY/12 WATCH/1 PASS, first live run under config v1.8 z>1.0. M-058 added: failed ingests leave the source file in historical_patterns\, blocking re-runs until the operator removes it. Pairs with O-009.) | 2026-06-17 (M-051 REAL fix landed: report_writer.py v1.8 -- print_signal_report_clean() no longer hardcodes [OK] written to vault / ARCHIVE OK; gated on LEDGER_LOG_CLASSES, fabricated archive block removed. Paired daily_evaluate_pipeline.py v1.20 M-043 fix -- _obsidian_write() False return now logged. M-054 added: the 2026-06-12 todo.md/lessons.md closure note for this exact bug was never verified against the file -- bug ran live in production 2026-06-12 through 2026-06-17 undetected. Caught via operator-uploaded live DailyEval console log.) | 2026-06-16 (WO-P300-E1.001 IntelliScan stop integration SHIPPED. intelliscan_reader.py v1.0 NEW; signal_schemas.py v2.1 (3 new SignalV2 fields); signal_emitter.py v2.1; daily_evaluate_pipeline.py v1.18. Smoke test PASS: 12 symbols, both support levels correct. M-052 added. WO-P115-E2.001 OPEN -- same pattern needed for P_115.) | 2026-06-12 (M-051 added -- hardcoded success string anti-pattern; falsified functional test captured in report_writer.py print_signal_report_clean().) | 2026-06-11 (M-019 instance: ledger_record.py Unicode arrow fixed; NFR-1 + report_writer smoke PASS; Enhancement 2 gate-on 3/4 done.) | 2026-06-09 (Enhancement 2 shipped -- Certainty-Equivalent BUY gate. CARA exponential utility (Kochenderfer Ch. 6) computes a risk-adjusted CE return per horizon; gates BUY when CE_GATE_ENABLED=True. Shipped OFF (observe-only). config v1.7 + schemas_pipeline_b v1.3 + domain/utility.py v1.0 NEW + aggregator v1.1 + signal_classifier v1.1 + report_writer v1.7. M-046 + M-047 added. utility.py smoke PASS verified.) | 2026-06-08 (Enhancement 1 shipped -- P_300 -> P_400 SIGNAL_V2 signal packet via the P_800 Hub interface. signal_emitter v2.0 + daily_evaluate_pipeline v1.15. M-045 added. COHR live BUY validated -> packet written to TradeOrderManagement/signals/. Architecture v2.7 Enhancement Log + Change Log updated.) | 2026-06-03 SEALED (Phase 3 Ledger Calibration System COMPLETE. M-040 through M-044 added. Ledger verified: COHR + DE signals captured. Next: 20-day wait, then ledger-fill.)

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

