# P_300 Task Queue

**File:** `tasks/todo.md`
**Status:** Active roadmap
**Last Updated:** 2026-06-03 (INIT reconciliation: catalog 060326catalog.db = N=156 / 136 symbols / 0 hollow / OVERALL HEALTHY; +17 patterns / +15 symbols across 3 untracked sessions (060126/060226/060326). 3 enhancements logged to Backlog: batch ingester [plan approved, build deferred], P_400 order-file integration [flagged NEXT], BUY-precision + social-sentiment layer.)
**Maintained By:** Anthony Zoppi + Claude (architect)

---

## Current State

- **Stage 1 Audit:** Complete.
- **Stage 2 Architecture:** Complete.
- **Stage 2 Closing Deliverables:** Complete.
- **Stage 3 Execution:** SEALED 2026-05-14.
- **Stage 4 Execution:** SEALED 2026-05-15.
- **Stage 5 Execution:** SEALED 2026-05-16.
- **Stage 6 Execution:** SEALED 2026-05-18.
- **Stage 7 Execution:** SEALED 2026-05-19.
- **Stage 8 Execution:** SEALED 2026-05-19.
- **Stage 9 Execution:** SEALED 2026-05-19.
- **Stage 9-followup (post-SEAL):** COMPLETE 2026-05-20.
- **2026-05-21 Pipeline A Tooling:** COMPLETE. P_300_AddPattern.bat v1.5 + archive_pattern_file.py v1.0 + cli.py v1.5.
- **2026-05-21/22 Catalog Growth:** N=25 -> N=91 (66 new patterns across two sessions).
- **2026-05-22 to 2026-05-26 Catalog Growth:** N=92 -> N=104 (13 patterns, earlier sessions).
- **2026-05-27 INIT Reconciliation:** Catalog confirmed N=104 / 052626catalog.db.
- **2026-05-27 Catalog Growth:** N=105 -> N=116 (12 patterns, 052726catalog.db mtime 2026-05-27 22:02:42).
- **2026-05-28 Pipeline B Clean Console:** daily_evaluate_pipeline.py v1.5 + report_writer.py v1.5 delivered.
- **2026-05-28 Feature Ablation + Threshold Sweep:** volume_zscore removed; BUY_MIN_Z_SCORE lowered to 0.0. config.py v1.5.
- **2026-05-29 Pipeline B Patching:** daily_evaluate_pipeline.py v1.9 + cli.py v1.6 + SIP v2.9. NVDA PASS @ h=20 validated.
- **2026-05-30 Process Boundary Refactor + Eval Session:** Process Boundary Standard formalized at Hub level. Dead code cleanup complete. Evals: ARLP BUY, COTY WATCH, DOX BUY, DD WATCH, EQX WATCH. 23 new patterns ingested (N=116->N=139 / 053026catalog.db) -- not tracked at time; gap closed 2026-05-31.
- **2026-05-31 P_800 Obsidian Note Standard + Bug Fix:** Gap 6 fixed (write_signal_to_obsidian.py v1.1). M-038 added. P_800 Obsidian Note Standard v1.1 drafted. Hub interface migration + backfill pending.
- **2026-06-03 INIT Reconciliation:** Catalog confirmed N=156 / 136 symbols / 060326catalog.db (mtime 2026-06-03 08:33:35). +17 patterns / +15 symbols added across 3 untracked sessions (060126/060226/060326) -- not tracked at time; gap closed this entry. 156 source_files / 3120 pattern_bars / 780 forward_labels / 0 hollow / OVERALL: HEALTHY. Baseline WR 60.3% @ h5, 60.9% @ h15/h20. Most recent: id=156 ENB, 155 AOS, 154 AME, 153 CMI, 152 DNOW.
- **2026-06-03 Ledger Calibration System (Phase 1–3 COMPLETE):** Signal-outcome measurement layer delivered. Captures BUY/WATCH fired signals → ledger records. Realized returns backfilled via yfinance. Confidence factors computed (realized_WR / predicted_WR). All tests passed. **WORKFLOW REMINDER:** (1) Daily eval fires BUY/WATCH → ledger record. (2) Wait 20+ trading days. (3) `python cli.py ledger-fill` → backfills realized returns. (4) `python cli.py ledger-calibration` → prints confidence report. Per-horizon metrics: sample_count, pred_WR, real_WR, confidence_factor, avg_realized_return.

---

## Completed -- Stage 3: File System Cleanup + Empty New Schema (SEALED 2026-05-14)

**Approved file plan (6 files, ~550 lines total).**

### 3.1 Foundation files
- [x] `python/config.py`
- [x] `python/schemas.py`

### 3.2 Migration scripts
- [x] `python/migrations/stage_3a_folder_setup.py`
- [x] `python/migrations/stage_3b_archive_cruft.py`
- [x] `python/migrations/stage_3c_init_new_catalog.py`

### 3.3 Surgical edit
- [x] `python/utilities/db_utils.py`

### 3.4 Documentation
- [x] `docs/migrations/STAGE_3_MIGRATION_LEDGER.md`

---

## Completed -- Stage 4: Rebuild Pipeline A (Add Pattern) (SEALED 2026-05-15)

11 of 11 files delivered. Pipeline A end-to-end validated on AAPL + OII. Full closeout: `docs/migrations/STAGE_4_CLOSEOUT.md`.

---

## Completed -- Stage 5: Re-Ingest Historical Patterns (SEALED 2026-05-16)

5 POC symbols ingested clean (AAPL, OII, SPY, QQQ, NVDA). Regression-verified. OVERALL: HEALTHY.

**Operator workflow per pattern:**

```
python cli.py integrity-check --xlsx "<path>"
python cli.py add-pattern --xlsx "<path>"
python cli.py catalog-summary
python cli.py inspect-pattern --id <N>
```

---

## Completed -- Stage 6: Rebuild Pipeline B (Daily Evaluate) (SEALED 2026-05-18)

10 of 10 files delivered. Decisions A-F locked. All success criteria green: determinism, self-match sanity, Stage 5 regression replay.

**Stage 6 architectural decisions:**
- A -- Legacy file decomposition
- B -- DTW per-feature equal-weight composite distance
- C -- Top-K = 20
- D -- All 5 horizons (5/7/10/15/20)
- E -- EVAL_SET transient in-memory only (NO catalog writes from Pipeline B)
- F -- BUY: n>=5 AND wr>=0.70 AND z>1.0; WATCH: n>=3 AND wr>=0.60 AND z>0.0

---

## Completed -- Stage 7: Broader Catalog Ingest (SEALED 2026-05-19)

20-symbol curated set ingested. ID-007 RESOLVED. Baseline win-rates below 1.0 at all 5 horizons. BUY now structurally reachable.

**Final catalog at Stage 7 SEAL:** 25 patterns / 25 symbols / 500 pattern_bars / 125 forward_labels / 0 hollow / OVERALL: HEALTHY. Active catalog: `models/051826catalog.db`.

**Final ingest table:**

| # | Symbol | pattern_instance_id | Anchor |
|---|--------|---------------------|--------|
| 1 | AVGO | 6 | 2025-06-13 |
| 2 | CAT | 7 | 2025-06-25 |
| 3 | TTD | 8 | 2025-08-07 (pre-workflow-fix offset) |
| 4 | AMD | 9 | 2025-08-18 (pre-workflow-fix offset) |
| 5 | LMT | 10 | 2025-09-02 (pre-workflow-fix offset) |
| 6 | NVO | 13 | 2025-09-11 (pre-workflow-fix offset; sub for PFE) |
| 7 | MU | 11 | 2025-09-12 (pre-workflow-fix offset) |
| 8 | SHOP | 12 | 2025-09-22 (pre-workflow-fix offset) |
| 9 | NKE | 14 | 2025-09-15 |
| 10 | GEV | 15 | 2025-09-25 |
| 11 | DIS | 16 | 2025-10-15 |
| 12 | PLTR | 17 | 2025-10-23 |
| 13 | META | 18 | 2025-11-05 |
| 14 | DE | 19 | 2025-11-20 |
| 15 | GOOGL | 20 | 2025-12-12 |
| 16 | XOM | 21 | 2026-01-15 |
| 17 | GS | 22 | 2026-01-22 |
| 18 | CVX | 23 | 2026-02-10 |
| 19 | WMT | 24 | 2026-02-25 |
| 20 | GLP | 25 | 2026-03-10 (sub for LLY) |

---

## Completed -- Stage 8: Local LLM Integration (SEALED 2026-05-19)

5 files delivered. NFR-1 preserved. `--no-narrator` flag added.

---

## Completed -- Stage 9: Parameter Sweep + Outcome Attribution (SEALED 2026-05-19)

3 utilities delivered. Sparse-N caveat alive; re-run at catalog >= 50 (Backlog).

---

## Completed -- Stage 9-followup (post-SEAL): Volatility-Divergence Flag + Process Runbooks (2026-05-20)

**Files delivered:**
- [x] `python/utilities/cap_sensitivity_audit.py` v1.0 NEW
- [x] `python/schemas_pipeline_b.py` v1.1 -> v1.2
- [x] `python/domain/volatility_divergence.py` v1.0 NEW
- [x] `python/application/daily_evaluate_pipeline.py` v1.1 -> v1.2
- [x] `python/infrastructure/report_writer.py` v1.2 -> v1.3
- [x] `docs/processes/evaluate_trade.md` v1.0 NEW
- [x] `docs/processes/add_pattern.md` v1.0 NEW

**Doc-bump SEAL (5 files):** todo.md + lessons.md + architecture v2.6->v2.7 + SIP v2.6->v2.7 + SKILL alignment -- all DONE 2026-05-20.

---

## Parked -- Milestone 6: Trade Management Module

Gated on live P_300 trading first. Consumes Aggregator output, produces position-sizing recommendation.

---

## Backlog -- Future Candidates (Not Scheduled)

- Parameter sweep + ablation re-run at N=300+ (re-tighten BUY_MIN_Z_SCORE toward 1.0 when z becomes discriminating)
- `return_pct` schema field rename to `return_fraction` (bundle with NormalizedBar shared-base refactor)
- NormalizedBar / PatternBarRecord shared-base refactor (DEBT NOTE from `schemas_pipeline_b.py`)
- `schemas_pipeline_b.py` file split (408 lines at v1.2, ~108 over; split candidates named in DEBT NOTE)
- Date-validity pre-check utility (M-026)
- Real-time intraday evaluation mode
- PEAK-anchor framing (second ingest pass)
- Legacy 14-symbol Gemini-era CSVs (abandoned 2026-05-18 -- no launch-window data)
- `lm_studio_client.py` + `task_router.py` -- LM Studio integration infrastructure not yet built (Stage 8 SEAL pending these; parked post-2026-05-29)
- `P_000_LMS_Integration_Guide.md` P_300 row -- update to complete once lm_studio_client.py + task_router.py delivered
- P_800 Obsidian Note Standard v1.1 implementation (schemas.py, config.py, filename_builder.py, frontmatter_builder.py, vault_writer.py, write_handler.py -- ~545 lines; pending operator approval)
- Historical note backfill (~60 existing P300 notes with wrong h5_win_rate / h5_mean_ret values)
- **Batch ingester (unattended catalog growth)** -- application-layer Python orchestrator + .bat launcher: glob to-ingest folder, run integrity-check + add-pattern per file, log + archive each, append one-line ledger entry that INIT reads to end tracking drift. ~150 lines / 2 new files + config.py edit. Plan approved 2026-06-03; build deferred per operator priorities. Deterministic CLI path ONLY -- not Cowork/LLM (NFR-1).
- **P_400 Trade Order Management integration (operator-flagged NEXT, 2026-06-03)** -- on BUY, Pipeline B emits a structured order-intent file for P_400 instead of / in addition to the Obsidian signal note. Deterministic file hand-off; order-file schema + P_400 ingest contract TBD.
- **BUY-precision investigation + social-sentiment confirmation layer (2026-06-03)** -- live BUYs underperforming. Levers in order: (1) MEASURE actual fired-BUY outcomes vs predicted LOO precision before changing anything; (2) re-tighten BUY_MIN_Z_SCORE toward 1.0 now at N=156 (lowered to 0.0 at N=116 per M-034); (3) orthogonal social sentiment via openbb-adanos (Reddit/X/Polymarket: buzz_score, sentiment_score, bullish_pct; needs adanos API key, ~250 free req/mo) as POST-decision confirmation or deterministic feature ONLY. LM Studio narrator stays OUT of the signal path (Anti-pattern #8 / NFR-1). Perplexity draft module (FInding_Sentiment...md) is directionally right but omits API-key setup and uses unverified method names (docs show obb.adanos.x.compare, not .sentiment) -- verify API surface before building.

---

## Active -- Live WATCH Tracking

**NOTE: All WATCH classifications below were made at N=25 baseline (WR ~0.60). Catalog is now N=139 with baseline WR ~0.58. Re-evaluate all symbols against a fresh anchor before acting.**

**Watchlist portfolio:** `P_300_WatchList_May2026.ptf` (5 symbols: AEM, NOC, NVDA, SNY, VZ).

### Live WATCH Tracking

| Symbol | Class @ horizon | wr | mean | z | Vol flag | Notes |
|--------|-----------------|----|------|---|----------|----|
| NOC | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=139 baseline. |
| VZ | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=139 baseline. |
| SNY | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=139 baseline. |
| AEM | Pending | -- | -- | -- | -- | Not yet evaluated. |
| NVDA | PASS @ h=20 | -- | -- | -- | -- | Evaluated 2026-05-29 with 9-feature config (post-ablation). |

### Workflow Design

Tabled pending P_800 Obsidian definition.

---

## Closed in Current Session (2026-05-31 -- P_800 Obsidian Note Standard + Bug Fix)

**Goal:** Design normalized Obsidian note standard for all trading systems; fix known frontmatter data bug in P_300 vault writer.

**Catalog reconciliation:** 053026catalog.db confirmed N=139 / 121 symbols / OVERALL: HEALTHY. 23 patterns added 2026-05-30 were not tracked in prior todo.md entry -- gap closed this session. Active catalog: `models/053026catalog.db` (mtime 2026-05-30 12:23:34).

**P_800 Obsidian Note Standard v1.1 drafted:**
- 10 gaps identified in current vault writing infrastructure
- Key decisions locked: signal_date filename key, verdict_history list (full classification history), signal/context-only role for Obsidian (P_020 owns position tracking), overwrite=True policy
- 9 Dataview queries defined including verdict_history-enabled slow-build BUY detection
- Doc saved: `projects/P_800_Automation_Note_Taking/docs/P_800_Obsidian_Note_Standard.md` (pending disk write to P_800 project -- currently in session artifact only)

**Gap 6 fixed -- write_signal_to_obsidian.py v1.1:**
- Root cause: `h_win_rate = wr / 100` double-divided a value already in decimal fraction form (0.800 → 0.008 in frontmatter vs correct 0.8)
- Root cause: `h_mean_ret = float(mr.rstrip('%')) / 100` wrong strip + double-divide (+4.81 → 0.0481 vs correct 4.81)
- Root cause: `overwrite=False` caused re-runs to silently skip existing notes
- Fix applied and validated: ROST re-run confirmed h5_win_rate: 0.8 / h5_mean_ret: 4.81 in vault
- File: `python/write_signal_to_obsidian.py` v1.0 -> v1.1

**M-038 added:** Always verify Hub interface before proposing any cross-project call. Hub interface for Obsidian writes: `shared_resources/python_utils/vault_interface.py` → `write_to_vault()`.

**Pending (next session):**
- [ ] Migrate `write_signal_to_obsidian.py` from `sys.path` injection to Hub interface (`write_to_vault`)
- [ ] Write `python/backfill_obsidian_notes.py` -- re-run all existing reports through fixed parser via Hub interface
- [ ] Write P_800 Obsidian Note Standard v1.1 to disk at `projects/P_800_Automation_Note_Taking/docs/`
- [ ] Implement P_800 Note Standard v1.1 (6 files, ~545 lines) -- pending operator approval

**Files delivered this session:**
- [x] `python/write_signal_to_obsidian.py` v1.0 -> v1.1 (Gap 6 fix: lines 57, 58, 98)
- [x] `tasks/lessons.md` updated (M-038 added, 2026-05-31 status entry)
- [x] `tasks/todo.md` updated (this entry)

---

## Closed in Current Session (2026-05-29 -- Pipeline B Patching + Doc Catch-Up)

**Goal:** Fix _HUB_ROOT pathing bug in daily_evaluate_pipeline.py, route cli.py --clean through main(), update SIP Step 5c failure block, capture M-036, update tracking docs.

**Root cause (M-036):** `daily_evaluate_pipeline.py` used 4 x `.parent` to reach Hub root. File is at `python/application/`, which is 5 levels below Hub root (file -> application/ -> python/ -> project root -> projects/ -> Hub root). 4 x `.parent` resolved to `projects/` instead of Hub root.

**Files delivered:**
- [x] `python/application/daily_evaluate_pipeline.py` v1.8 -> v1.9 (_HUB_ROOT: 4 x .parent -> 5 x .parent; ensure_lm_studio_ready() removed; replaced with read-only _check_lm_studio() via get_wrapper_status())
- [x] `python/cli.py` v1.5 -> v1.6 (--clean flag routed through daily_evaluate_pipeline.main() instead of run_daily_evaluate())
- [x] `docs/prompts/P_300_System_Initialization_Prompt_v2.md` v2.8 -> v2.9 (Step 5c failure block now displays exact launcher command)

**Validation:** NVDA daily-evaluate ran clean -- PASS @ h=20. LM Studio narration skipped (API server not started).

**Catalog state (unchanged -- Pipeline B read-only):** 116 patterns / 052726catalog.db.

---

## Closed in Current Session (2026-05-28 -- Feature Ablation + Threshold Sweep + config.py Tuning)

**Goal:** Run M-028 deferred parameter sweep and feature ablation at N=116; apply findings to production config.

**config.py v1.4:** removed `volume_zscore` from SIMILARITY_FEATURES.
**config.py v1.5:** lowered `BUY_MIN_Z_SCORE` from 1.0 to 0.0.

**Current production thresholds:** BUY: n>=5, wr>=0.70, z>0.0 / WATCH: n>=3, wr>=0.60, z>0.0.

**Files changed:** `python/config.py` v1.3 -> v1.5.

---

## Closed in Current Session (2026-05-28 -- Pipeline B Clean Console Output)

**Files delivered:** `daily_evaluate_pipeline.py` v1.2 -> v1.5 / `report_writer.py` v1.4 -> v1.5.

---

## Closed in Current Session (2026-05-27, INIT Catalog Reconciliation)

Catalog confirmed N=104 / 052626catalog.db. Divergence resolved (tracking showed N=91).

---

## Closed in Current Session (2026-05-22, Pipeline A Continued Growth -- 29 New Patterns)

29 new patterns (id=63-91). Catalog N=25 -> N=91. Active: `models/052226catalog.db`.

---

## Closed in Current Session (2026-05-21 -- Pipeline A Operator Tooling + 16 Pattern Ingests)

- [x] `P_300_AddPattern.bat` v1.5, `python/utilities/archive_pattern_file.py` v1.0, `python/cli.py` v1.5
- 16 patterns ingested (id=26-41). Catalog: 41 patterns / 40 symbols / OVERALL: HEALTHY.

---

## Closed in Current Session (2026-05-21, Pipeline A Catalog Growth -- 37 New Patterns)

37 new patterns (id=26-62). Catalog N=25 -> N=62. Active: `models/052126catalog.db`.

---

## Closed in Earlier Chat (2026-05-20, Volatility Divergence Flag + Process Runbooks)

Post-SEAL feature delivery. 7 files. Doc-bump SEAL complete 2026-05-20.

---

## Closed in Earlier Chat (2026-05-19, Stages 7+8+9 triple-sealed)

Stage 7: 12 ingests, catalog 13->25, ID-007 RESOLVED. Stage 8: LM Studio narrator. Stage 9: sweep + ablation + LOO utilities.

---

## Closed in Earlier Chat (2026-05-18, Stage 7 startup)

Stage 7 re-scope. 8 ingests (AVGO through NVO). Catalog 5->13.

---

## Closed in Earlier Chat (2026-05-18, Stage 6 SEAL day)

5 doc-bump SEAL files. Architecture v2.4->v2.5. SIP v2.4->v2.5. SKILL v2.4->v2.5.

---

## Closed in Earlier Chat (2026-05-17->2026-05-18, Stage 6 build)

8 files. Pipeline B operational. All 3 success criteria green.

---

## Closed in Earlier Chat (2026-05-16->2026-05-17, Stage 6 startup)

5 files. Decisions A-F locked.

---

## Closed in Earlier Chat (2026-05-16, Stage 5 SEAL day)

3 patterns reconciled. inspect_pattern.py + cli.py v1.1. ISE profile created.

---

## Closed in Earlier Chat (2026-05-15, Stage 4 SEAL day)

8 files. AAPL + OII ingested.

---

## Closed in Earlier Chat (2026-05-14, Stage 4 session 1)

5 files. schemas.py + normalization + labeler.

---

## Closed in Earlier Chat (2026-05-13)

Stage 1 Audit + Stage 2 Architecture + initial docs.

---

---

## Closed in Current Session (2026-06-03, Phase 3 Ledger Calibration System COMPLETE & VERIFIED)

**Delivered:** 10 new files + 2 edits across `python/` layers (config, schemas, infrastructure, application, domain, utilities, cli).

**Architecture:** 3-phase signal-outcome measurement system.
- **Phase 1 (Capture):** Fired signals recorded at moment of firing (BUY/WATCH). Snapshot: ticker, date, class, horizon, n_matches, wr, mean_ret, z_score.
- **Phase 2 (Fill):** Realized returns backfilled from yfinance 20+ trading days post-signal. Per-horizon return_pct stored.
- **Phase 3 (Calibrate):** Confidence factors computed: realized_WR / predicted_WR per horizon. Printed as formatted table.

**Verified Results:**
- ✅ COHR 2026-06-02 BUY h=15 n=20 wr=70.0% ret=+0.06% → ledger_id=2
- ✅ DE 2026-06-02 BUY h=5 n=20 wr=95.0% ret=+0.06% → ledger_id=1
- ✅ `python cli.py ledger-fill --dry-run` shows unfilled rows
- ✅ `python cli.py ledger-calibration` ready (will run post-wait)

**Critical Issues Found & Fixed:** 5 errors documented as lessons M-040 through M-044.
1. Incomplete test coverage (imports vs execution paths)
2. Unverified utility function calls
3. Wrong SQL schema (patterns table doesn't exist; use pattern_instances)
4. Non-blocking errors logged at ERROR instead of WARNING
5. Skipped reading SKILL docs; experimented instead

**Next Step:** Wait 20+ trading days (until ~late June 2026). Then run `ledger-fill` to backfill realized returns, then `ledger-calibration` to measure signal confidence.

**Workflow reminder:**
```
(1) python cli.py daily-evaluate --xlsx ...  # Fires BUY/WATCH → ledger record
(2) Wait 20+ trading days
(3) python cli.py ledger-fill               # Backfill realized returns from yfinance
(4) python cli.py ledger-calibration        # Print confidence report (pred_WR vs real_WR)
```

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** Every stage transition, every task completion, every newly-scoped task
- **Loaded by:** SIP at session start (Step 4 via `windows-mcp:FileSystem`, per M-015)

---

**End of P_300 Task Queue**
