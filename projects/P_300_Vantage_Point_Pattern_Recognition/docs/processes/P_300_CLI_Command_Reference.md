# P_300 — CLI & Process Command Reference

**File:** `docs/processes/P_300_CLI_Command_Reference.md`
**Version:** 1.1
**Last Updated:** 2026-08-05
**Audience:** Anthony Zoppi
**Pairs With:** `python/cli.py` v2.0 shim + `python/cli_commands/` package (6 modules,
18 commands) -- verified directly against source, not from memory (M-054).
**Deeper narrative runbooks:** `docs/processes/add_pattern.md`,
`docs/processes/evaluate_trade.md` -- this file is the flat command index;
those two carry the operator workflow detail (D+20 rule, verification
steps, failure handling). Not duplicated here.

---

## How every command is actually invoked

Every `.bat`/`.ps1` wrapper below ultimately calls:

```
C:\Users\Trader\.conda\envs\p140\python.exe C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\cli.py <command> [args...]
```

`cli.py` is a thin shim -- real argument parsing lives in `python\cli_commands\`.
`python cli.py --help` lists all 18 commands; `python cli.py <command> --help`
prints one command's full argument list live from the source (more current
than this doc if they ever drift).

Project root (all relative paths below are relative to this):
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\`

---

## 1. Pre-session checks

### P_300_Preflight.bat
Catalog + LM Studio status snapshot. Writes `P_300_preflight_status.json`,
which INIT Step 5b/5c reads. No parameters.

```
P_300_Preflight.bat
```
Underlying: `python\utilities\preflight_status.py` (no CLI subcommand -- run direct, not through `cli.py`).

### check-pattern -- pre-export duplicate check
**This is the "reads the live folder and scans the catalog for an
existing pattern" process.** No dedicated `.bat` -- run the CLI command
directly. Defaults to scanning `data\live\`; `--symbol` overrides with an
explicit ticker list instead.

Full command line (as actually run from a shell, not project-relative):
```
C:\Users\Trader\.conda\envs\p140\python.exe C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\cli.py check-pattern
```
Same, with a symbol filter:
```
C:\Users\Trader\.conda\envs\p140\python.exe C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\cli.py check-pattern --symbol AAPL,MSFT
```
| Flag | Default | Notes |
|---|---|---|
| `--symbol` | none (scans `data\live\`) | Comma-separated tickers |
| `--catalog` | `get_latest_catalog()` | Path override |

---

## 2. Pipeline A -- Add Pattern (grows the live catalog)

### Single -- P_300_AddPattern.bat
```
P_300_AddPattern.bat "data\historical_patterns\Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx"
```
Blank arg prompts for the path interactively. Internally runs, in order:
1. `python\cli.py catalog-summary --recent 5` (baseline display, pause for confirm)
2. `python\cli.py add-pattern --xlsx "<XLSX>"`
3. `python\cli.py archive-pattern --xlsx "<XLSX>"`

`add-pattern` full args:
| Flag | Default | Notes |
|---|---|---|
| `--xlsx` | required | Path to Pattern XLSX |
| `--master` | `get_latest_catalog()` | Catalog path override |

`archive-pattern`: `--xlsx` required (same file).

### Bulk, manual loop -- P_300_RunAllPatterns.ps1
Loops `P_300_AddPattern.bat` over every `*.xlsx` in `data\historical_patterns\`, one at a time, logging to `P_300_AddPattern_Messages.txt`.
```
powershell -File P_300_RunAllPatterns.ps1
```
No parameters.

### Bulk, mined pipeline (full chain, current) -- P_300_RunBulkAddPattern.ps1 v2.0
The real "BulkAddPattern" process: `mine-patterns` (find candidates) ->
`ingest-mined` (audit gate + staging) -> `promote-gate` (quality check) ->
auto-`promote` if clean -> archive processed files. v2.0 auto-promotes on
a clean gate (WO-P300-E5.005) -- no separate manual promote step needed
when the gate passes.
```
powershell -File P_300_RunBulkAddPattern.ps1
```
No parameters -- every underlying CLI call inside uses defaults. Transcript logged to `logs\BulkAddPattern_<timestamp>.log`.

---

## 3. Pipeline B -- Daily Evaluate (reads catalog, emits BUY/WATCH/PASS)

### Single, current -- P_300_DailyEval_v2.bat (v2.4)
```
P_300_DailyEval_v2.bat SPY
```
Blank arg prompts for symbol. Internally:
1. `python\cli.py daily-evaluate --xlsx "data\live\History Grid (SPY).xlsx" --clean`
2. `python\cli.py archive-eval --xlsx "data\live\History Grid (SPY).xlsx"`

`daily-evaluate` full args:
| Flag | Default | Notes |
|---|---|---|
| `--xlsx` | required | `History Grid (SYMBOL).xlsx` |
| `--window-length` | 20 | Candidate window, bars |
| `--top-k` | `config.TOP_K_MATCHES` | Top-K matches surfaced |
| `--no-write-file` | off | Console-only, no report file |
| `--reports-dir` | none | Override report output dir |
| `--no-narrator` | off | Skip LM Studio Stage 8 narration |
| `--clean` | off | Minimal batch-friendly console output |

`archive-eval`: `--xlsx` required (same file). Moves it to `data\processed\YYYY-MM.zip` and deletes from `data\live\` on success.

### Batch -- P_300_RunAllDailyEvals.ps1
Loops `P_300_DailyEval_v2.bat` over every `History Grid (*).xlsx` in
`data\live\`, then runs the inline Chaikin chain (see Section 4) against
that run's own BUY/WATCH log.
```
powershell -File P_300_RunAllDailyEvals.ps1
```
No parameters.

---

## 4. Chaikin enrichment (vault-note only, WO-P300-E5.007 skip-list filtered as of 2026-08-05)

### Inline -- part of P_300_RunAllDailyEvals.ps1
Fires automatically at the end of the batch run above. Filters BUY/WATCH
symbols against `data\reference\chaikin_skip_list.csv` before calling out.

### Standalone re-run -- P_300_RunChaikinBatch.ps1
For re-running just the Chaikin step against an already-written log
(e.g. DailyEval already ran, XLSX already archived).
```
powershell -File P_300_RunChaikinBatch.ps1
```
No parameters -- reads `P_300_DailyEval_Messages.txt` for BUY/WATCH symbols, same skip-list filter, then `claude -p <prompt> --chrome`.

---

## 5. Bulk research pipeline (report-only / research-catalog-only -- never touches live catalog.db)

### bulk-extract -- P_300_BulkExtract.bat
```
P_300_BulkExtract.bat
```
CLI: `python\cli.py bulk-extract`
| Flag | Default |
|---|---|
| `--input-dir` | `config.DATA_BULK` |
| `--master-db` | `config.BULK_RESEARCH_DB` |
| `--temp-db` | `config.BULK_TEMP_DB` |
| `--checkpoint` | `config.BULK_CHECKPOINT_FILE` |

### scanner-loop -- P_300_ScannerLoop.bat
```
P_300_ScannerLoop.bat
```
CLI: `python\cli.py scanner-loop [--input-dir <dir>] [--reports-dir <dir>]` -- defaults `config.DATA_BULK_NIGHTLY_SCAN` / `config.SCANNER_REPORTS_DIR`.

### mine-patterns -- P_300_MinePatterns.bat
```
P_300_MinePatterns.bat
```
CLI: `python\cli.py mine-patterns [--input-dir <dir>] [--reports-dir <dir>]` -- defaults `config.DATA_BULK_MINE` / `config.MINE_REPORTS_DIR`. Writes report + `mine_candidates.csv` (edit the `keep` column before `ingest-mined`).

### phase5-analysis -- P_300_Phase5Analysis.bat
```
P_300_Phase5Analysis.bat
```
CLI: `python\cli.py phase5-analysis [--master-db <db>] [--no-backfill]`

---

## 6. Bulk promote pipeline (staging -> live, explicit promote step)

### ingest-mined -- P_300_IngestMined.bat
Build (default mode):
```
P_300_IngestMined.bat
```
CLI: `python\cli.py ingest-mined [--csv <path>] [--input-dir <dir>] [--staging-db <db>] [--live-db <db>] [--confirm-full-rescore]`

Promote (separate, explicit -- printed at the end of the build run):
```
python\cli.py ingest-mined --promote "models\staging_ingest_mined.db" [--live-db <db>]
```
`--confirm-full-rescore` (WO-P300-E5.004): required when a cold M-079 cache forces a full serial rescore that can take hours -- without it the command refuses and exits rather than running unattended.

### merge-research-catalog -- P_300_MergeResearchCatalog.bat
Build:
```
P_300_MergeResearchCatalog.bat
```
CLI: `python\cli.py merge-research-catalog [--staging-db <db>] [--live-db <db>]`

Promote:
```
python\cli.py merge-research-catalog --promote "models\staging_merge_catalog.db" [--live-db <db>]
```

### promote-gate (CLI direct -- called internally by RunBulkAddPattern.ps1, decides only, never writes a catalog)
```
python\cli.py promote-gate
```
| Flag | Default | Notes |
|---|---|---|
| `--eval-dir` | `EVAL_REPORTS_DIR` | Walk-forward report dir |
| `--baseline` / `--staging` | auto-discovered pair | Explicit paths, bypasses staleness check |
| `--staging-db` | `models\staging_ingest_mined.db` | Recorded in the marker if STOP |
| `--buy-drop-pp` | 3.0 | Max tolerated BUY precision drop, pp |
| `--pass-drop-pp` | 3.0 | Max tolerated PASS accuracy drop, pp |
| `--min-buy-n` | 400 | Below this, comparison is waived not failed |
| `--max-pair-age-minutes` | 720 | Rejects a stale baseline/staging pairing |

Exit codes: `0` PROMOTE, `2` STOP (do not promote), `1` ERROR (no verdict reached).

### archive-mined
Run after a successful `ingest-mined` promote:
```
python\cli.py archive-mined --xlsx "data\bulk\mine\<file>.xlsx"
```

---

## 7. Diagnostics / utility (CLI direct, no dedicated `.bat`)

| Command | Full line | Key flags |
|---|---|---|
| catalog-summary | `python\cli.py catalog-summary` | `--catalog <path>`, `--recent N` (default 5) |
| integrity-check | `python\cli.py integrity-check --xlsx "<path>"` | `--manifest <path>` (default `parameters\ingest_manifest.json`) |
| inspect-pattern | `python\cli.py inspect-pattern --id 1` | `--catalog <path>` |
| ledger-fill | `python\cli.py ledger-fill` | `--dry-run` (log only, no DB write) |
| ledger-calibration | `python\cli.py ledger-calibration` | none |

### run_eval_loop.bat -- walk-forward eval loop, Stage 6, read-only
```
run_eval_loop.bat
run_eval_loop.bat 1.0
```
Underlying: `python\application\run_eval_loop.py [--buy-min-z <float>]`. No arg -> `config.py` `BUY_MIN_Z_SCORE` default.

---

## 8. Removed 2026-08-05 -- confirmed unused, moved not deleted

Three scripts confirmed unused by Tony. Moved to
`E:\AI-Agent-Learning-Hub_BackupFiles\P_300_Deprecated_Scripts\` (recoverable,
not deleted) rather than left in the project root:

- **P_300_DailyEval.bat (v1.0)** -- legacy single-symbol Daily Evaluate,
  no `--clean` flag on the `daily-evaluate` call. Superseded by
  `P_300_DailyEval_v2.bat`, which is what `P_300_RunAllDailyEvals.ps1`
  actually calls.
- **run_daily_posture.bat** -- `python\P_300_Posture_v2.6.py live`,
  9:30 AM grid snapshot + risk_config writer. Also flagged before removal:
  used `SETLOCAL ENABLEDELAYEDEXPANSION`, which M-032 bans on this
  workstation.
- **run_intraday_vp_check.bat** -- `python\P_300_Intraday_VPCheck_v2.6.py`,
  read grid_snapshot_latest.json for intraday band checks. Same
  M-032 flag as above.

If posture/intraday checks are still wanted from a different project
(P_010 owns market posture canonically per memory), confirm before
re-creating these here -- this project's copies are gone.

---

## Command inventory (18 total, 6 modules)

| Module | Commands |
|---|---|
| `pipeline_a.py` | add-pattern, archive-pattern |
| `pipeline_b.py` | daily-evaluate, archive-eval |
| `bulk_research.py` | bulk-extract, scanner-loop, mine-patterns, phase5-analysis |
| `bulk_promote.py` | merge-research-catalog, ingest-mined, archive-mined |
| `promote_gate.py` | promote-gate |
| `utility.py` | catalog-summary, integrity-check, inspect-pattern, check-pattern, ledger-fill, ledger-calibration |
