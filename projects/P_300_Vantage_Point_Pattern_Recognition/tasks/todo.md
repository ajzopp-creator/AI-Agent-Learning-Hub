# P_300 Task Queue

**File:** `tasks/todo.md`
**Status:** Active roadmap
**Last Updated:** 2026-06-29 (Ledger dedup 175->142 rows + ledger-fill's first real output ever -- 4 stacked bugs (M-060/061/062/063/064) found and fixed in sequence; h5=115/h7=97/h10=58/h15=2/h20=0 real fills, verified via before/after counts. See Current State.) | 2026-06-28 (AddPattern + DailyEval batches run live under config v1.8 (BUY_MIN_Z_SCORE=1.0): catalog 331->362 patterns / 231->245 symbols; 9 BUY/12 WATCH/1 PASS across 22 live symbols, 0 errors. M-058 added -- see Current State.) | 2026-06-28 (Stage 6 eval loop SHIPPED -- 5 files, walk-forward run on 331-pattern catalog 062326catalog.db at z>0.0 vs z>1.0; BUY_MIN_Z_SCORE re-tightened 0.0->1.0 in config.py v1.8, closing M-034 re-eval trigger. M-057 added.) | 2026-06-17 (M-051 REAL fix shipped: report_writer.py v1.8 + daily_evaluate_pipeline.py v1.20. CORRECTS the entry below dated 2026-06-12 -- that closure was never verified against the file; report_writer.py was still v1.7 with the bug intact through today. See M-054.) | 2026-06-16 (WO-P300-E1.001 IntelliScan stop integration SHIPPED: intelliscan_reader.py v1.0 NEW + signal_schemas.py v2.1 + signal_emitter.py v2.1 + daily_evaluate_pipeline.py v1.18. Smoke PASS 12 symbols. WO-P115-E2.001 OPEN -- same pattern for P_115.) | 2026-06-12 (print_signal_report_clean() hardcoded status strings fixed via Claude Code -- M-051 closure. P_800 Hub interface (signal_emitter -> write_to_vault SIGNAL_V2) confirmed working: 2026-06-12_COF.md written to vault automatically on BUY/WATCH. WO-P300-E1.001 BACKLOG created (resistance lookup to replace VP predicted high as target formula). system-doc-initializer SKILL compressed v3.0 + M-051 added globally (Protocol D Loop F). CLAUDE.md updated: WO table corrected, schemas_signal_packet.py flagged vestigial, last-updated bumped.) | 2026-06-11 (ATR operator runtime check DONE: CGBD BUY h=5 -- signal class unchanged, guideline stop/target + atm_at_signal present and non-zero, pipeline clean exit. 061026catalog.db detected at INIT -- count unverified due to PowerShell MCP timeout; health check deferred to next session.) | 2026-06-11 (Enhancement 2 gate-on prerequisites COMPLETE: report_writer smoke PASS (all 3 scenarios) + NFR-1 determinism replay PASS (CGBD BUY h=5, all 5 horizons, signal_class/chosen_horizon/per-horizon stats identical across 2 runs, certainty_equivalent included). ledger_record.py M-019 bug fixed (Unicode arrow -> ASCII). Junk replay ledger entries (ids 41-42) deleted; fired_signals back to 40 rows. One remaining gate-on prerequisite: lambda tuning against ledger.) | 2026-06-09 (INIT reconciliation: live catalog 060826catalog.db = N=186 / 155 symbols / 0 hollow / OVERALL HEALTHY, mtime 2026-06-08 10:43:43. Corrects three stale tracking claims -- see reconciliation entry below. | Decision-flag surfacing shipped: SIP v3.0->v3.1 + SKILL aligned; M-048 added.) | 2026-06-09 (Enhancement 2 shipped: Certainty-Equivalent BUY gate. CARA exponential utility (Kochenderger Ch. 6) scores top-K analog forward returns -> risk-adjusted CE return per horizon; gates BUY when ce >= CE_MIN_THRESHOLD AND CE_GATE_ENABLED. Shipped OFF (observe-only, NARRATOR_ENABLED precedent) -- live signals byte-identical until lambda tuned + flag flipped. 6 files: config v1.7, schemas_pipeline_b v1.3, domain/utility.py v1.0 NEW, aggregator v1.1, signal_classifier v1.1, report_writer v1.7. M-046 + M-047 added. utility.py smoke PASS verified; gate-ON path + e2e determinism replay still OWED before flip.) | 2026-06-08 (Enhancement 1 shipped: P_300 -> P_400 SIGNAL_V2 signal packet via P_800 Hub interface. signal_emitter v2.0 + daily_evaluate_pipeline v1.15 + architecture v2.7 Enhancement Log. COHR live BUY validated -> packet written. M-045 added.) | 2026-06-03 (INIT reconciliation: catalog 060326catalog.db = N=156 / 136 symbols / 0 hollow / OVERALL HEALTHY; +17 patterns / +15 symbols across 3 untracked sessions (060126/060226/060326). 3 enhancements logged to Backlog: batch ingester [plan approved, build deferred], P_400 order-file integration [flagged NEXT], BUY-precision + social-sentiment layer.)
**Maintained By:** Anthony Zoppi + Claude (architect)

---

## Current State

**>>> 2026-06-30 ADDPATTERN + DAILYEVAL BATCH (22 ingested, 13 evaluated, preflight reconciled):** `P_300_RunAllPatterns.ps1` run failed silently on first attempt -- launched via `cmd` typing the filename directly, which opened the file in its associated editor (VS Code) instead of executing it; no script logic involved. 11 of 22 queued XLSX files also had a stray space after `Pattern_` (`Pattern_ 20260112...`) that would have failed the filename validator (O-009/M-058 family -- new cause, same failure shape); renamed before run via PowerShell batch rename. Re-run via `powershell -ExecutionPolicy Bypass -File P_300_RunAllPatterns.ps1`: all 22 files ingested clean, 0 errors -- pattern_instance_id 363-384, 13 new symbols (ZDGE, ZETA, WRAP, KNDI, QS, OPEN, APP, CRCL, VOC, JVA, TTMI, AXTI, TWLO). Catalog: 362->384 patterns / 245->258 symbols / 7660->7680 pattern_bars / 1915->1920 forward_labels, 062326catalog.db, 0 hollow, OVERALL HEALTHY throughout. DailyEval batch immediately after, anchor 2026-06-29: 13 symbols, 0 errors, all written to vault + XLSX archived. **8 BUY** (APP, JVA, KNDI, OPEN, QS, TWLO, WRAP, ZDGE) / **4 WATCH** (ARCC, STWD, VOC, ZETA) / **1 PASS** (FSK). M-051 fix confirmed holding in live production: FSK printed real `[SKIP] FSK not logged to vault (PASS -- vault logging is BUY/WATCH only)`, no fabricated `[OK]`. Note: 10 of 13 evaluated symbols were ingested into the catalog in the same session minutes before evaluation -- BUY/WATCH calls for those names lean partly on a freshly-added analog pool; flagged for manual analog review before acting, not a pipeline defect. `P_300_Preflight.bat` re-run after both batches: catalog reconciled 384/258/0 hollow/HEALTHY, LM Studio running (deepseek-r1-distill-qwen-14b) -- preflight snapshot now current.

**>>> 2026-06-29 LEDGER DEDUP + LEDGER-FILL FIRST REAL RUN (4 stacked bugs found and fixed):** Ledger fill-status check ahead of the ~2026-07-01 lambda-tuning window (M-046) found two separate problems, fixed in sequence:

**(1) Dedup:** `insert_fired_signal()` has no uniqueness guard (M-059, fix still owed). 26 duplicate groups / 33 duplicate rows found across 175 fired_signals (COHR fired 6x on 2026-06-02 across 4 sessions; an entire 2026-06-12 batch re-fired wholesale on both 06-13 and 06-15). Dry-run reviewed by Tony before any delete; execute pass backed up `buy_ledger.db` to a timestamped `.bak_dedup_<stamp>.db`, re-derived the duplicate set live (not from a cached id list), verified the live count matched the dry-run's 33 before touching anything. Result: 175 -> 142 rows, verified via before/after count.

**(2) ledger-fill had never successfully filled a single row since the system was built on 2026-06-03**, despite `tasks/todo.md` recording "Phase 1-3 COMPLETE" on that date. Four bugs found stacked on top of each other, in this order: M-060 (`signal_date` parsed as YYYYMMDD when it's stored as YYYY-MM-DD -- threw on every row) -> fixed -> M-061 (yfinance returns MultiIndex columns even for one ticker; `row["Close"]` returned a Series, not a scalar -- threw on every row) -> fixed -> ran clean with "Filled 0/142" and no errors, which looked like success but wasn't -> traced the code rather than the log -> found M-062 (`query_unfilled()` checked `h5_return_pct`, not `h20_return_pct` -- any partial fill would have permanently dropped out of future runs) and M-063 (fetch window of +25 calendar days yields only ~17-18 trading days, structurally short of the 21 needed for `h20`) -> fixed both -> still "Filled 0/142" but now with real per-row computed values visible in the log -> found M-064, the actual blocker (`update_realized_outcome()` was only ever called inside the `is_filled()` branch -- every partial outcome, which given the project's age was every single row, was computed correctly then silently discarded; paired with a COALESCE-based UPDATE so a None field never clobbers an already-saved value from an earlier run) -> fixed -> **first real fills landed: h5=115, h7=97, h10=58, h15=2, h20=0** (h20 expected at 0 -- DE/COHR, the oldest signals, hit their 20th trading day on the day of this fix, before market close; not a bug). 27 rows still fully unfilled, all accounted for: BF_B (delisted, no yfinance data at all) + the 06-22 batch (5 trading days elapsed, h5 needs 6) + the 06-26 batch (1 trading day elapsed). All 5 bugs logged as M-060 through M-064 in lessons.md, including the discovery sequence -- a clean exit with "0 filled" was not evidence of correctness, same family as M-054.

**>>> 2026-06-28 ADDPATTERN + DAILYEVAL BATCHES (first live run under config v1.8, BUY_MIN_Z_SCORE=1.0):** AddPattern batch of 32 source files: 31 ingested clean, 1 rejected -- `Pattern_20260109_20260203_DOCU.xlsx` already in catalog as `source_file_id=277` (ValueError, catalog untouched per design, file left in `data\historical_patterns\` since failed ingests don't archive). Operator confirmed it as a true duplicate and deleted it from `data\historical_patterns\` (verified empty post-delete). Catalog: 331->362 patterns / 231->245 symbols / 6620->7240 bars / 1655->1810 forward labels, `062326catalog.db`, 0 hollow, OVERALL HEALTHY throughout. DailyEval batch of 22 live symbols immediately after, anchor 2026-06-26 (Friday close): 0 errors, all 22 written to vault + XLSX archived. **9 BUY** (ADBE, BL, CHGG, DOCU, HTGC, LULU, PCTY, PI, WIX) / **12 WATCH** (AMYZF, FICO, FIVN, HQY, OTEX, PRDO, RRC, TDC, TR, TTD, TYL, WU) / **1 PASS** (LOPE) -- first live confirmation of the tightened z>1.0 BUY gate against a real daily batch, against a market posture that read strongly bearish at the same session's INIT (no macro filter in the signal path by design, NFR-1). M-058 added to lessons.md (DOCU duplicate-file recurrence: same filename ingested twice across sessions -- failed ingests leave the source file in `historical_patterns\`, requiring an explicit operator delete/rename before the next AddPattern run or the same file blocks the batch again).

**>>> 2026-06-28 STAGE 6 EVAL LOOP SHIPPED + BUY_MIN_Z_SCORE RE-TIGHTENED TO 1.0:** All 5 planned files delivered: `python/schemas_eval.py` (Pydantic eval models), `python/domain/eval_scoring.py` (walk-forward scoring -- corpus restricted to strictly-earlier `anchor_date` per pattern, NOT leave-one-out; supports an overridable gate copy for threshold-comparison runs without touching production `config.py`/`signal_classifier.py`), `python/infrastructure/eval_io.py` (catalog load + report write), `python/application/run_eval_loop.py` v1.1 (pure orchestration; `--buy-min-z` CLI override flag added same-day), `run_eval_loop.bat` (operator-run via p140 terminal, not `windows-mcp:PowerShell` -- M-030/M-057). Ran the full 331-pattern catalog (`062326catalog.db`) at both `z>0.0` (then-prod) and `z>1.0` (Stage 6 original) after parity-verifying the override gate copy against the live `signal_classifier`. Reports: `outputs/reports/eval/walkforward_062326catalog_default_20260628_122021.txt` (z>0.0: BUY=155, 93 correct/62 false_positive, 60.0% accuracy) and `..._bz1.0_20260628_170638.txt` (z>1.0: BUY=97, 61 correct/36 false_positive, 62.9% accuracy). WATCH absorbs exactly the 58-pattern difference; PASS bit-for-bit identical (106 patterns, 44 correct/62 missed) across both runs -- confirms the override touches only the BUY boundary. The 58 demoted patterns ran 55.2% win rate (32W/26L), below the original BUY pool's 60% average -- a real if modest edge being cut, not noise. **Decision: re-tightened `BUY_MIN_Z_SCORE` 0.0 -> 1.0 in `config.py` v1.8**, closing the M-034 re-evaluation trigger set at N=300+. M-057 also added to lessons.md (windows-mcp Python ~4-min ceiling: a near-the-line job can finish server-side after the client gives up -- both eval-loop runs took ~4:30-4:40 and the client timed out, but checking `outputs/reports/eval/` showed both reports had already written cleanly; no re-run needed). Closes the previously-pending work-order item ("Stage 6 eval loop design... pending verification of live function signatures before orchestrator can be written") -- signatures verified, orchestrator built and run successfully this session.

**>>> 2026-06-23 P_300_AddPattern.bat CORRUPTED + REBUILT:** Tony accidentally pasted PowerShell console text into the `.bat` file (clipboard mixup -- meant to paste into chat, the launcher was focused in an editor instead), reducing it to 101 bytes of stray console text. No on-disk backup or VS Code local history existed. Rebuilt from `cli.py`'s real subcommands (`add-pattern`, `archive-pattern`, `catalog-summary`) + a console transcript of a prior live run; day-rollover catalog-backup logic (no source existed anywhere) was reconstructed in pure batch, avoiding M-032's delayed-expansion trap. Verified end-to-end on a real ingest -- TSLA, pattern_instance_id=320, 227 symbols / 320 patterns / 6400 bars / 1600 labels, archived to `2026-06.zip`, clean exit. M-056 added to lessons.md.

**>>> 2026-06-18 WO-P000-E4.001 P_300 INIT EXECUTION BYPASS SHIPPED (pilot):** SIP Steps 5b/5c previously invoked `python` via `windows-mcp:PowerShell` for catalog-summary and the LM Studio check -- the exact call shape M-030/peh-handoff document as hanging on most attempts, and confirmed twice in this file already (2026-06-10/11 entries below, both "count unverified due to PowerShell MCP timeout"). Fix: new `python/utilities/preflight_status.py` (reuses `db_utils.get_latest_catalog`, `verify_ingestion._check_no_hollow_instances`, `lm_studio_api.get_wrapper_status` -- no catalog or LM Studio logic reimplemented) + `python/schemas_preflight.py` (Pydantic `PreflightStatus`) write `P_300_preflight_status.json` to the project root. New `P_300_Preflight.bat` (operator-run, outside the chat session -- same model as `P_300_AddPattern.bat` / `P_300_DailyEval_v2.bat`) invokes it. SIP bumped to v3.2 -- Steps 5b/5c rewritten to read the JSON via `windows-mcp:FileSystem` instead of invoking `python` directly; zero subprocess calls remain in INIT. `p300-project-context` SKILL.md updated to match (Critical Paths row, Layer Architecture tree, Session-Start Checklist line, Pairs-With table path fix, changelog). Session header format (`P_300 [Day, Month DD, YYYY -- HH:MM ET]`) confirmed already canonical -- P_300 was the source pattern being adopted Hub-wide; no change needed on that half of the WO. Hub-wide rollout to P_115/116/117/118/400/800 and the `P_000_SYSTEM_DOCUMENTATION.md` standard entry remain P_000's open items on WO-P000-E4.001. P_300-side Ack appended to the WO. M-055 added to lessons.md.

**>>> 2026-06-17 M-051 REAL FIX SHIPPED (correcting the false 2026-06-12 closure):** Operator uploaded live DailyEval console output (AEM/CRML/NNE) showing `print_signal_report_clean()` still printing a hardcoded `[OK] {ticker} written to vault` for every signal class -- including CRML and NNE, both PASS, where no vault write of any kind happens (daily_evaluate_pipeline only calls the real obsidian-write hook for BUY/WATCH, per LEDGER_LOG_CLASSES) -- plus a fully fabricated `[STEP 3] Archiving eval file... ARCHIVE OK -- zip: data/processed/2026-05.zip` block with zero real call behind it and a dead stale path/month. This is the exact M-051 bug from 2026-06-12 -- except `report_writer.py` was still v1.7 (2026-06-09), unchanged, the whole time. The 2026-06-12 todo.md/lessons.md entries claiming this was fixed via Claude Code were never verified against the file. Bug ran live in production 2026-06-12 through 2026-06-17 (5+ days, includes 2026-06-15/16 sessions). Fix: `report_writer.py` v1.8 -- vault-write line now gated on `LEDGER_LOG_CLASSES` (`[OK]` for BUY/WATCH, honest `[SKIP] ... not logged to vault` for PASS); fabricated archive block removed entirely (archiving is reported for real by the separate `.bat` STEP 2 / `cli.py archive-eval`); DONE footer corrected to match. Paired `daily_evaluate_pipeline.py` v1.20 -- M-043 fix, `_obsidian_write()`'s True/False return was being discarded; a clean False now logs WARNING instead of vanishing silently. Verified via PEH harness (`04-Shared-Resources/verify/run_this.py`), 9 checks: BUY case shows real `[OK]`/no fabricated archive text/correct footer; PASS case shows `[SKIP]`/no `[OK]`/no fabricated archive text/correct footer. All PASS, 2026-06-17 (Tony ISE run). M-054 added to lessons.md: a closure note in tasks/*.md is a claim, not evidence -- verify the file before trusting a prior session's DONE.

**>>> 2026-06-17 WO-P300-E1.003 STOP GUARD FIX SHIPPED:** atr_adjusted_stop = max(intelliscan_support_1, ATR floor) assumed support_1 always sits below entry. Caught by P_400 via DRD (support_1=25.46 above entry=25.40, max() picked the invalid above-entry value as the stop -- would've been used silently as P_400's primary stop input). Isolated to DRD, not systemic. Fix: `application/daily_evaluate_pipeline.py` v1.19 -- support_1 only counts as a max() candidate when it's below entry; otherwise falls back to ATR floor alone. `shared_resources/python_utils/signal_schemas.py` SignalV2 bumped to v2.3 -- added a validator rejecting any packet where atr_adjusted_stop >= guideline_entry (the acceptance criterion's reject-not-silent-pass requirement, also a safety net against recurrence). Verified the schema validator only (4 cases, PASS) -- the pipeline-side guard is inline, not a standalone function, so it wasn't unit-tested; real-world confirmation pending next live run that hits a symbol with an IntelliScan level above entry. OWNER_DONE appended to WO-P300-E1.003. P_400 Ack pending.

**>>> 2026-06-17 WO-P300-E1.002 TARGET GENERATION FIX SHIPPED:** Architecture 3.5 (Target Selection Standard) was decided but never implemented -- guideline_target was unconditionally entry + 2x ATR, ignoring any VP resistance level in the same packet. Caught by P_400 via the AG dossier (intelliscan_support_2=21.27 sitting unused above entry=19.42, target still set to 21.84 off ATR). Consequence: R:R always read exactly 2.00 by construction, so P_400's Tier-1 R:R gate couldn't filter anything. Fix: `infrastructure/signal_emitter.py` v2.2 -- `_build_signal_v2_packet` now checks both intelliscan_support_1/_2 for any level above entry, uses the nearer one as guideline_target (target_source="vp_resistance"); falls back to 2x ATR (target_source="atr_extension") only when neither clears entry. Does not hardcode support_2 as "the resistance field" -- AG happened to have support_1 below entry and support_2 above, but the check is field-agnostic. `shared_resources/python_utils/signal_schemas.py` SignalV2 bumped to v2.2 -- added target_source field + validator; without this the audit trail field would be silently dropped by write_to_vault's validation. Verified via PEH harness, 4 cases (AG real numbers, true price-discovery/no IntelliScan data, support_1-above-entry case, both-levels-above-entry case): PASS. OWNER_DONE appended to WO-P300-E1.002 (single physical file under both Agentic-Hub-Governance and 04-Shared-Resources paths -- confirmed junction, not duplicate copies). P_400 Ack pending: confirm R:R varies by symbol on re-run.

**>>> 2026-06-17 vp_xlsx_reader v1.4 FIX + BACKLOG CLEARED:** v1.3's filename.upper() regression (M-053) fixed -- 100% AddPattern failure since 2026-06-16 traced to uppercasing the whole filename before a case-sensitive regex match. Fix: re.IGNORECASE on `_FILENAME_PATTERN`, symbol-only uppercase post-match. First re-run after fix: 13/18 succeeded. Remaining 5 were genuine data issues, not the bug: DOCU (insufficient setup history) and EDVMF x2 (41 bars, need 60) recaptured with more history and re-ingested clean (3/3) -- catalog now 279 patterns / 209 symbols / 061726catalog.db (pattern_instance_id 277-279). RCl / RCL (`Pattern_20260123_20260211` and `Pattern_20260226_20260303`) -- both opened to a sheet named WDC, not RCL; both deleted by Tony as bad captures. 18/18 of the original blocked batch now resolved (16 ingested, 2 deleted).

**>>> 2026-06-16 WO-P300-E1.001 INTELLISCAN STOP INTEGRATION SHIPPED:**
- `python/utilities/intelliscan_reader.py` v1.0 NEW -- reads `data/live/P_300_HistoryGrid_IntelliscanEvalParameters.xlsx`; returns `(support_1, support_2)` per symbol; non-blocking when file absent.
- `shared_resources/python_utils/signal_schemas.py` v2.1 -- `atr_adjusted_stop`, `intelliscan_support_1`, `intelliscan_support_2` added to `SignalV2` as `Optional[float] = None`; validator added. Backward compatible.
- `python/infrastructure/signal_emitter.py` v2.1 -- 3 new optional params wired through `_build_signal_v2_packet` and `emit_signal_packet`.
- `python/application/daily_evaluate_pipeline.py` v1.18 -- `load_intelliscan()` called once at pipeline start; `get_support_levels()` per symbol; `atr_adjusted_stop = max(support_1, close - 1xATR)` or ATR floor when grid absent. All 3 fields passed to emitter.
- **Smoke test PASS**: 12 symbols, both support levels correct vs live IntelliScan grid.
- **WO-P115-E2.001 OPEN**: same integration needed for P_115 signals (separate session).
- **M-052 added**: stop architecture rule -- emit both VP support levels; P_400 decides which clears risk parameters.

**>>> 2026-06-12 PRINT_SIGNAL_REPORT_CLEAN() FIX + P_800 HUB INTERFACE CONFIRMED:**
- Hardcoded `[OK] {ticker} written to vault` and `ARCHIVE OK` strings in `report_writer.py` `print_signal_report_clean()` replaced with real call-driven output via Claude Code. M-051 closure.
- P_800 Hub interface confirmed working end-to-end: `signal_emitter.emit_signal_packet()` -> `write_to_vault("SIGNAL_V2", ...)` -> P_800 write_handler -> Obsidian vault. Validated by `2026-06-12_COF.md (version 2)` written automatically on BUY/WATCH -- no extra step needed.
- The vault write was always wired correctly via Enhancement 1 (2026-06-08). The hardcoded strings in `print_signal_report_clean()` were the only defect; the actual write path was never broken.

**>>> 2026-06-12 GOVERNANCE + DOC UPDATES:**
- WO-P300-E1.001 created (BACKLOG): resistance lookup to replace VP predicted high as target formula. Scope: P_300 emits resistance-derived `target_price` in SignalV2 only; P_400 remains final target authority (M-050). Gated on lambda tuning + CE gate flip (~2026-07-01).
- system-doc-initializer SKILL v3.0: compressed ~40% token reduction + Protocol D Loop F added (falsified output / M-051 global rule). Non-negotiable: no `[OK]`/`DONE`/`written` without real call return.
- CLAUDE.md updated: WO table corrected (P_115/P_800 CLOSED with dates; P_000-E2.003 accurate scope), `schemas_signal_packet.py` flagged vestigial in layer architecture block, last-updated bumped to 2026-06-12.
- M-051 added to lessons.md (P_300-level) and system-doc-initializer SKILL (Hub-level global rule).

**>>> 2026-06-11 ATR OPERATOR RUNTIME CHECK DONE:**
- CGBD BUY h=5, n=20, wr=0.90, z=2.55 -- signal class byte-identical to NFR-1 replay. BUY/WATCH/PASS unaffected by ATR upgrade. ✅
- guideline_stop: 10.7377, guideline_target: 11.4646, atm_at_signal: 0.2423 -- present and non-zero. ✅
- Pipeline clean exit (--no-narrator; LM Studio was not running at time of check).
- 061026catalog.db detected at INIT (newer than last known 060826catalog.db) -- catalog has grown; count unverified due to PowerShell MCP timeout. Health check deferred to next session INIT.

**>>> 2026-06-11 ENHANCEMENT 2 GATE-ON PREREQUISITES COMPLETE:**
- **report_writer smoke PASS** (2026-06-11): All 3 scenarios clean -- dense format (horizons/matches/vol-divergence/narrative), clean format with narration, clean format with narrator_warning forced on. None-CE renders as N/A in the ce column. No crashes. sys.path removal did not break imports.
- **NFR-1 determinism replay PASS** (2026-06-11): `tasks/nfr1_determinism_replay.py` ran CGBD BUY h=5 twice with `CE_GATE_ENABLED=False`, `narrator_enabled=False`. signal_class, chosen_horizon, n_matches, win_rate, mean_return_pct, std_return_pct, z_score, certainty_equivalent -- ALL IDENTICAL across both runs. CE observe-mode does NOT alter BUY/WATCH/PASS. NFR-1 confirmed for Enhancement 2.
- **ledger_record.py M-019 fix**: Unicode `->` (U+2192) in logger.info f-string replaced with ASCII `->`. Was triggering cp1252 UnicodeEncodeError on every BUY/WATCH ledger write (non-blocking but noisy). Fixed in-session.
- **Junk ledger entries cleaned**: Replay ran CGBD as a real BUY both passes, writing ledger_ids 41 and 42. Both deleted via `tasks/cleanup_replay_ledger_entries.py`. fired_signals back to 40 rows.
- **One prerequisite remaining before flipping CE_GATE_ENABLED=True:** tune lambda against ledger (requires ledger-fill at 20-trading-day mark -- earliest eligible signals from 2026-06-02; fill window opens ~2026-07-01).

**>>> 2026-06-09 INIT CATALOG RECONCILIATION (ground truth reset):** Live `catalog-summary` (operator ISE paste, PowerShell timed out in-session) = **N=186 pattern_instances / 155 symbols / 186 source_files / 3720 pattern_bars / 930 forward_labels / 0 hollow / OVERALL HEALTHY** on `models/060826catalog.db` (mtime 2026-06-08 10:43:43). Most recent: id=186 BF_B (anchor 2026-03-25), 185 BF_B, 184 BF_B, 183 BATRA, 182 HTHT. Baseline WR 61.3% @ h5/h15/h20, 60.8% @ h7/h10; avg returns +3.39/+4.18/+4.92/+5.82/+5.02% across horizons. **Three prior tracking claims corrected by this entry:** (1) the 2026-06-03 closure N=156 was the last tracked figure -- catalog has since grown +30 instances across untracked sessions (gap closed here); (2) the 2026-06-08 "N=175 / 147 symbols" growth note was never the live count -- live is 186/155; (3) the 2026-06-08 "AVXL #2 / CRK / HP #2 FAILED to ingest" entry is FALSE -- all three are present in the live catalog (AVXL 2 patterns, CRK 1, HP 2). Whatever forward-bar concern was logged that day, the ingests landed. Per M-017 the catalog is authoritative; tracking is now reset to 186/155. No partial/hollow state (0 hollow confirmed). Catalog DB naming note: latest is 060826catalog.db (not 060326).

**>>> NEXT SESSION LEAD ITEM -- DONE 2026-06-09:** Surface behavior-affecting config flags in the INIT session summary. SHIPPED: SIP v3.0->v3.1 (Step 5 greps config.py for RISK_AVERSION_LAMBDA / CE_MIN_THRESHOLD / CE_GATE_ENABLED / NARRATOR_ENABLED; Step 6 gains `Decision flags:` line; fail-fast row for unreadable flags) + SKILL aligned (checklist confirmation line, SIP ref v3.1, changelog). Grep-at-INIT not import (no PowerShell dependency; captures committed default, in-session flips operator-visible). Live flags this session: CE gate OFF (lambda 20.0, min 0.0) / Narrator ON. Doc/protocol change, no code. M-048 captured (filesystem:edit_file atomic-batch rollback).

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
- **2026-06-03 Ledger Calibration System (Phase 1-3 COMPLETE):** Signal-outcome measurement layer delivered. Captures BUY/WATCH fired signals -> ledger records. Realized returns backfilled via yfinance. Confidence factors computed (realized_WR / predicted_WR). All tests passed. **WORKFLOW REMINDER:** (1) Daily eval fires BUY/WATCH -> ledger record. (2) Wait 20+ trading days. (3) `python cli.py ledger-fill` -> backfills realized returns. (4) `python cli.py ledger-calibration` -> prints confidence report. Per-horizon metrics: sample_count, pred_WR, real_WR, confidence_factor, avg_realized_return.
- **2026-06-08 Enhancement 1 (P_300 -> P_400 Signal Packet) SHIPPED:** On BUY/WATCH, Pipeline B emits a SIGNAL_V2 JSON packet to P_400 via the P_800 Hub interface (write_to_vault SIGNAL_V2 -> trading_journal/TradeOrderManagement/signals/<date>_<SYMBOL>_v2.0.json), alongside the Obsidian md note. signal_emitter.py v2.0 + daily_evaluate_pipeline.py v1.15 (Stage 5a). Fixed the v1.14 vault_root TypeError that crashed every BUY. Boundary: P_300 emits asset_class=stock + position_size=0 sentinel; P_400 sizes (no P_000 coupling). Gate widened BUY-only -> (BUY, WATCH). COHR live BUY @ h=15 validated -> packet written, stock variant passed P_800 validation. schemas_signal_packet.py now vestigial (removal in Backlog). Architecture v2.7 Enhancement Log + Change Log + M-045. P_300 producer side of Phase E1 DONE; P_400 JSON reader + E2 remain.
- **2026-06-08 Catalog Growth:** AVXL #2 (id=173, anchor 2026-03-24), CRK (id=174, new symbol, anchor 2026-01-30), HP #2 (id=175, anchor 2026-04-21). All ingested + archived to 2026-06.zip. Catalog: 175 patterns / 147 symbols / 3500 pattern_bars / 875 forward_labels / OVERALL HEALTHY.
- **2026-06-09 Enhancement 2 (Certainty-Equivalent BUY Gate) SHIPPED -- OBSERVE-ONLY:** Risk-adjusted reasoning added to Pipeline B per Kochenderfer "Algorithms for Decision Making" Ch. 6 (maximum expected utility). CARA exponential utility u(r)=-exp(-lambda*r) scores each top-K analog's forward return; inverted mean utility = certainty-equivalent (CE) return, CE = -(1/lambda)*ln(mean(exp(-lambda*r))). For any non-degenerate spread CE < arithmetic mean; the gap is the risk penalty (fat-tailed analog distributions penalized INSIDE the decision, not just flagged afterward). Decimal-space throughout (M-020); lambda applied to decimal fractions, default RISK_AVERSION_LAMBDA=20.0 (meaningful band ~10-40). Pure domain math -- NFR-1 preserved, no LLM in path. **CE_GATE_ENABLED defaults False:** CE computed + displayed but does NOT alter any signal until flag flipped after lambda tuning. 6 files: config v1.6->v1.7, schemas_pipeline_b v1.2->v1.3 (optional certainty_equivalent field), domain/utility.py v1.0 NEW (~210 ln incl harness; longest fn ~30 ln), aggregator v1.0->v1.1, signal_classifier v1.0->v1.1 (CE term on BUY branch only, guarded), report_writer v1.6->v1.7 (ce column + lambda-stamped header). M-046 (lambda provenance) + M-047 (harness honesty) added to lessons. Validation: utility.py smoke PASS (dispersed cluster mean +4.5% -> CE -3.7% at lambda=20, 8.2pt penalty). Files over 300-ln (M-031): schemas_pipeline_b, aggregator -- splits stay backlogged, one-field/minimal adds only.
  **OWED before gate-on (do NOT flip CE_GATE_ENABLED until done):**
  - [x] signal_classifier smoke: gate-ON cases added + VERIFIED 2026-06-09 (v1.2, CE GATE: PASS -- CE>=0 keeps BUY, CE<0 blocks to WATCH, gate-OFF ignores CE). Caught + fixed a double-import test bug (flag now flipped on sys.modules[__module__]) and a stale case-4 expectation (z gate is 0.0 per M-034, not 1.0).
  - [x] report_writer smoke run (None-CE render confirm) + e2e daily-evaluate determinism replay vs pre-change run (NFR-1 proof observe-mode changed nothing) -- DONE 2026-06-11. Both PASS. See 2026-06-11 session entry above.
  - [ ] tune lambda against ledger before flipping; stamp lambda into ledger record at flip (gated on ledger-fill ~2026-07-01)
  - [x] architecture v2.7 Enhancement Log + Change Log entry DONE 2026-06-09 (in-place addendum, no version bump per Appendix G -- Change Log + §7 Enhancement Log both carry Enhancement 2). signal_classifier bumped to v1.2 (harness).

**>>> 2026-06-10 ATR UPGRADE (shared Wilder util) SHIPPED + RUNTIME CHECK DONE 2026-06-11:**
Replaced P_300's high-low-only simple-average ATR proxy with full True Range + Wilder smoothing. NEW shared hub util `shared_resources/python_utils/atr.py` v1.0 (`true_range` + `compute_atr_wilder`; pure domain; takes (h,l,c) tuples -- decoupled from any project's bar type) + `test_atr.py` (9/9 PASS, incl hand-computed Wilder 86/27; run from the P_300 dir so it also proves the shared import resolves). `daily_evaluate_pipeline.py` v1.15->v1.16 (removed local `_compute_atr_from_bars`; imports the shared util via the editable install -- NOT the _HUB_ROOT sys.path insert; call site adapts `candidate.bars`, confirmed chronological oldest-first). signal_emitter.py docstring clarified (candidate/baseline; P_400 resolves final). ATR is NOT in the classification path (only feeds atm_at_signal -> guideline stop/target) -- BUY/WATCH/PASS unaffected. **Architecture decisions (Tony; M-049/M-050):** (1) all evaluating projects emit the same baseline shape (guideline entry/target/stop); (2) P_400 is the single target authority -- resolves final entry/stop/target + RR + sizing (today only `packet_classifier.classify` exists; enforcement OWED in P_400 build-out); (3) ATR computed at eval time on bars in hand, not P_400-owned (avoids a re-fetch), shared via the editable install across the <=5 eval projects.
  - [x] Operator runtime check DONE 2026-06-11: CGBD BUY h=5 -- signal class byte-identical, guideline stop/target + atm_at_signal present and non-zero. ATR upgrade confirmed clean.
  - [ ] P_000: add `shared_resources/python_utils/atr.py` to the P_000_SYSTEM_DOCUMENTATION Document Index (WO-P000-E3.001 Completion Gate).

**>>> 2026-06-10 Cross-project ENH notes drafted (handed to owners):** (a) ENH-P000 -- promote LM Studio status to a Hub interface in `shared_resources/python_utils/` + move the external-service check out of P_300's application layer (daily_evaluate_pipeline.py line 487); blocks the E2.003 sys.path rows for that file + the three `integrations/lm_studio/infrastructure/*.py` inserts (editable install does NOT cover `integrations`, so removing those inserts breaks imports). Filed at P_000/docs/notes/. (b) ENH-P800 -- rename the `p115_`-prefixed SignalMetadata fields to `session_date`/`chart_timeframe` (origin artifact; P_300 packets carry p115_ keys that misname the owner); no P_400 consumer reads them yet, so the rename is free now. Filed at P_800/docs/. Both for the owner project to convert to a WO.

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

---

## Completed -- Stage 6: Rebuild Pipeline B (Daily Evaluate) (SEALED 2026-05-18)

10 of 10 files delivered. Decisions A-F locked. All success criteria green.

---

## Completed -- Stage 7: Broader Catalog Ingest (SEALED 2026-05-19)

20-symbol curated set ingested. ID-007 RESOLVED. Baseline win-rates below 1.0 at all 5 horizons. BUY now structurally reachable.

---

## Completed -- Stage 8: Local LLM Integration (SEALED 2026-05-19)

5 files delivered. NFR-1 preserved. `--no-narrator` flag added.

---

## Completed -- Stage 9: Parameter Sweep + Outcome Attribution (SEALED 2026-05-19)

3 utilities delivered. Sparse-N caveat alive; re-run at catalog >= 50 (Backlog).

---

## Completed -- Stage 9-followup (post-SEAL): Volatility-Divergence Flag + Process Runbooks (2026-05-20)

7 files delivered. Doc-bump SEAL complete 2026-05-20.

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
- P_800 Obsidian Note Standard v1.1 implementation (~545 lines; pending operator approval)
- Historical note backfill (~60 existing P300 notes with wrong h5_win_rate / h5_mean_ret values)
- **schemas_signal_packet.py removal** -- file is vestigial (superseded by SignalV2 in shared_resources.python_utils.signal_schemas). Remove when convenient; no active imports confirmed.
- **Batch ingester (unattended catalog growth)** -- ~150 lines / 2 new files + config.py edit. Plan approved 2026-06-03; build deferred per operator priorities.
- **WO-P300-E1.001 (BACKLOG): Resistance lookup target formula** -- replace VP predicted high with nearest grid resistance above close as `target_price` in SignalV2. Gated on lambda tuning + CE gate flip (~2026-07-01). Scope: P_300 emits only; P_400 resolves final (M-050).
- **P_400 Trade Order Management integration** -- E1 P_300 producer side DONE 2026-06-08. REMAINING: P_400 builds JSON reader (E1 consumer side); then E2 (remove P_300 STEP 2 md output so P_400 reads JSON as sole input).
- **BUY-precision investigation + social-sentiment confirmation layer** -- levers in order: (1) measure actual fired-BUY outcomes vs predicted LOO precision; (2) re-tighten BUY_MIN_Z_SCORE toward 1.0 at N=300+; (3) openbb-adanos sentiment as post-decision confirmation.

---

## Active -- Live WATCH Tracking

**NOTE: All WATCH classifications below were made at N=25 baseline (WR ~0.60). Catalog is now N=186+ with baseline WR ~0.61. Re-evaluate all symbols against a fresh anchor before acting.**

**Watchlist portfolio:** `P_300_WatchList_May2026.ptf` (5 symbols: AEM, NOC, NVDA, SNY, VZ).

| Symbol | Class @ horizon | wr | mean | z | Vol flag | Notes |
|--------|-----------------|----|------|---|----------|----|
| NOC | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=175 baseline. |
| VZ | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=175 baseline. |
| SNY | STALE -- re-eval required | -- | -- | -- | -- | Classified at N=25; not valid at N=175 baseline. |
| AEM | Pending | -- | -- | -- | -- | Not yet evaluated. |
| NVDA | PASS @ h=20 | -- | -- | -- | -- | Evaluated 2026-05-29 with 9-feature config (post-ablation). |

---

## Closed in Current Session (2026-06-18 -- WO-P000-E4.001 P_300 Pilot)

- [x] `python/schemas_preflight.py` NEW -- `PreflightStatus` Pydantic model
- [x] `python/utilities/preflight_status.py` NEW -- gathers catalog + LM Studio status, writes JSON
- [x] `P_300_Preflight.bat` NEW -- operator-run, writes `P_300_preflight_status.json`
- [x] `docs/P_300_System_Initialization_Prompt_v3_1.md` -- bumped to v3.2; Steps 5b/5c read the JSON instead of invoking python via PowerShell; backup of pre-edit v3.1 saved
- [x] `.claude/skills/p300-project-context/SKILL.md` -- Critical Paths, Layer Architecture, Session-Start Checklist, Pairs-With path fix, changelog updated to match
- [x] M-055 added to lessons.md
- [x] WO-P000-E4.001 Ack appended (P_300 side)

---

## Closed in Current Session (2026-06-17 -- Completion Gates)

- [x] WO-P300-E1.002 -- Completion Gate checklist added (7 items, all satisfied); Status header corrected PENDING -> OWNER_DONE; WO remains OWNER_DONE pending P_400 re-run confirmation
- [x] WO-P300-E1.003 -- Completion Gate checklist added (7 items, all satisfied); Status header corrected PENDING -> OWNER_DONE; WO remains OWNER_DONE pending real-world confirmation

---

## Closed in Current Session (2026-06-17 -- M-051 Real Fix)

- [x] report_writer.py v1.8 -- print_signal_report_clean() vault-write line gated on LEDGER_LOG_CLASSES; fabricated [STEP 3]/ARCHIVE OK/2026-05.zip block removed; DONE footer corrected
- [x] daily_evaluate_pipeline.py v1.20 -- _obsidian_write() False return now logged at WARNING (M-043)
- [x] PEH verification (run_this.py, 9 checks) -- PASS, confirmed by Tony 2026-06-17
- [x] M-054 added to lessons.md (closure notes are claims, not evidence)
- [x] M-051 addendum added to lessons.md noting the real fix date
- [x] 2026-06-12 false closure corrected in todo.md + lessons.md header lines

---

## Closed in Current Session (2026-06-16)

- [x] WO-P300-E1.001 IntelliScan stop integration -- 4 files shipped, smoke PASS
- [x] M-052 added to lessons.md
- [x] WO-P115-E2.001 created (OPEN)
- [x] todo.md + lessons.md updated

---

## Closed in Current Session (2026-06-12)

- [x] M-051 added to lessons.md (hardcoded success string anti-pattern)
- [x] system-doc-initializer SKILL compressed v3.0 + Protocol D Loop F (M-051 global rule)
- [x] CLAUDE.md updated (WO table, vestigial schema note, last-updated)
- [x] WO-P300-E1.001 created (BACKLOG -- resistance lookup target formula)
- [x] print_signal_report_clean() hardcoded status strings fix confirmed via Claude Code (M-051 closure)
- [x] P_800 Hub interface end-to-end confirmed: 2026-06-12_COF.md written to vault automatically

---

## Closed in Current Session (2026-06-11 -- ATR Runtime Check)

- [x] CGBD eval via `P_300_DailyEval_v2.bat` -- BUY h=5, clean exit
- [x] Signal packet verified: guideline_stop=10.7377, guideline_target=11.4646, atm_at_signal=0.2423
- [x] Signal class matches NFR-1 replay (n=20, wr=0.90, z=2.55) -- byte-identical

---

## Closed in Current Session (2026-06-11 -- Enhancement 2 Prerequisites + Bug Fix)

- [x] `tasks/smoke_report_writer.txt` -- report_writer smoke output (PASS, all 3 scenarios)
- [x] `tasks/nfr1_determinism_replay.py` -- NFR-1 determinism replay script
- [x] `tasks/nfr1_replay_out.txt` -- replay output (PASS)
- [x] `python/application/ledger_record.py` -- M-019 fix
- [x] `tasks/cleanup_replay_ledger_entries.py` -- junk entry cleanup (40 rows confirmed)

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (architect)
- **Update trigger:** Every stage transition, every task completion, every newly-scoped task
- **Loaded by:** SIP at session start (Step 4 via `windows-mcp:FileSystem`, per M-015)

---

**End of P_300 Task Queue**
