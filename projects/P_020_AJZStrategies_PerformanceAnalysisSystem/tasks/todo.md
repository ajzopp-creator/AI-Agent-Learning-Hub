# P_020 Current State

## 2026-09-02

Session covered five items: E1.015 WO rewrite + Independent-Review-ready, monthly review, a token failure + reauth, closing 12 pre-2026 trades, and a stop-price gap fix.

- **E1.015 (IRA ingestion):** WO file rewritten to match reality -- Status PENDING -> OWNER_DONE. Every Acceptance Criteria item live-reverified this session (not carried from memory): 9/9 IRA9885 trades confirmed `system=reason='P_117'`, `signal_strength='B'`, zero NULLs; `system_attribution.py` line 118 IRA bypass gate read directly; all 4 touched files compile-clean. Independent Review still needs a separate session -- can't self-certify. Backup of stale file saved (`WO-P020-E1.015_backup_2026-09-02.md`).
- **Monthly review (AJZ6348, Jan-Aug):** August closed -$2,011.50 (12 trades, 16.7% WR), second straight sub-17% month. Cumulative closed P&L -$8,118.79, no new equity high since 1/29. Only P_118 clears 40% WR profitably (71.4%, +$2,586, small sample). Two structural flags: **all 18 open AJZ trades had `stop_price=NULL`** (see fix below), and 12 of those were pre-2026 legacy positions (300-629 days old) -- see closeout below. 60.9% of closed trades landed below -2R (avg -26.89R) -- likely connected to the missing-stop gap, not purely a discipline issue.
- **E1.010 (Schwab token):** `analyze` run hit `invalid_grant` -- first real failure since 8/18, breaking the "no failure since 8/18" premise the 8/30 wait-and-see decision was conditioned on. Tony reauthed (`P_020_Schwab_Auth.bat`). Live-verified working (`balance --account AJZ`, 200 OK). P_400 token confirmed same ALL-mode grant, byte-identical. Logged into WO-P020-E1.010's Occurrence Log and Status header. Tony's direction decision (separate app registration vs. accept-reauth) is due now, not just at the 9/5 checkpoint.
- **Pre-2026 trade closeout:** Tony's directive -- 12 trades open since 2024-2025 (SMLR, OKLO, DOCU, PLTR, DIS, BMY, RBLX, BBY, SWPPX, PM, SOFI, QQQ) have no relevance to 2026 strategy tracking. Closed via direct `status='closed'` update with an explanatory note per row (no fabricated exit prices -- these were never given real closing data). Verified: 0 pre-2026 trades remain open, 6 legitimate 2026-dated AJZ trades untouched.
- **Stop-price gap fix:** Root cause: `_apply_stop_prices()` in `ingest_pipeline.py` was hard-gated to PAPER accounts only -- live AJZ trades never had a stop-price source wired up at all, not a bug in the traditional sense, just never built for live. Tony's call: extend the existing Tracker Dashboard lookup (`match_stop_price()`, StopLevel/SLLevel columns) to live too. Fixed: gate now skips only IRA9885 (which already bypasses Tracker/vault per E1.015 Decision 1) instead of allow-listing PAPER. File stayed exactly 300 lines (was already at the hard cap) -- edit was line-neutral. New `tests/test_ingest_pipeline.py` (5 tests: AJZ gets stop, IRA still skips, PAPER regression unchanged, no-lookup safe no-op, no-match falls through clean). Baseline 70 tests passed before the edit; 75/75 passing after. Both files compile-clean under `-W error::SyntaxWarning`. **No WO filed for this yet** -- flagging in case Tony wants one; logged here and in `P_020_Future_Enhancements.md` Recently Completed in the meantime.
- **db_writer.py -- systems FK auto-registration (found mid-afternoon, scoping an IRA follow-up):** `trades.system` carries a hard FK against `systems` (10 seeded codes). ThinkLog tag override writes the WHY tag straight into `system` -- open-vocabulary by design per `thinklog_override.py`'s own docstring, but the FK wasn't honoring that: any tag outside the 10 (`INV`, `BTD`, `OIL`, a future project code) would throw an uncaught `IntegrityError` mid-loop and crash the whole ingest run before the audit log writes. Live risk for AJZ ThinkLog tags today, not just IRA. Fixed: `ensure_system_registered()` added to `db_writer.py`, `INSERT OR IGNORE` inside `insert_trade()`'s own transaction so it commits/rolls back with the trade row. Regression gate run before (3/3) and after (4/4 `test_db_writer.py`, 76/76 full suite).
- **P_020_Balance_Snapshot.py path bug + first successful run:** `BASE_DIR` was `parent.parent` (resolves to `python\`), should be `parent.parent.parent` (project root) -- config was never found, script had apparently never run successfully before. Fixed; first live run pulled both accounts clean: AJZ6348 $29,458.74 Net Liq, IRA9885 $46,129.22 (cash available -$677.59, buying power $0.00 on the IRA -- flagged to Tony, not investigated further this session). History CSV created (`data\balance_snapshots\P_020_Balance_History.csv`).
- **September monthly review completed (account params -- separate from the AJZ6348 performance review above):** root cause for why it hadn't run this morning -- the `analyze` token failure (see E1.010 above) blocked the live balance pull; reauth fixed the token in time for the 10:00 AM batch-2b cash/buying-power refresh, but the balance/risk/max side never got circled back to. Ran now: AJZ6348 $29,458.74 -> Risk $441.88 / Max $1,472.94 (down from Aug 4's $470.23/$1,567.42). `P_000_Account_Parameters_Current.md` updated (all derived tables, new History row, Next Review -> October 2026); backup saved (`_backup_2026-09-02.md`). Claude memory updated to match.
- **WO-P020-E1.015 file-integrity check:** this session's earlier IRA/systems-table work risked an accidental full overwrite of the WO file rewritten this morning. Verified after the fact -- still intact, `OWNER_DONE`, Occurrence Log through the morning rewrite unchanged. No data lost.


## 2026-08-30

- Backfilled this file (had been stale since 7/21) with dated entries covering 7/25 through 8/29 -- see that entry below for the full catch-up.
- **E1.015 (IRA ingestion):** found the 9 already-live IRA9885 trades (from the 8/22 dry-run-bug incident) were tagged generic `system='INV'`, `signal_strength=NULL`. Tony's call: retag all 9 as `P_117` (external recommendation) with real descriptions instead of leaving them generic. Built a manual ThinkLog-format CSV from Tony's one-line notes per symbol (`data\tos_exports\live\P_020_IRA_ThinkLog_Manual_Backfill_2026-08-30.csv`), ran `thinklog --account IRA9885` dry-run preview, then `--commit`. All 9 trades now `system=reason='P_117'`, `signal_strength='B'`, verified against the DB directly. E1.015's SCOPE is otherwise already built (Schwab pull, account resolution, vault/Tracker bypass) -- this was the last real gap. WO-P020-E1.015.md itself still needs a rewrite to match reality before it can go to Independent Review -- not done yet.
- **E1.010 (Schwab token collision):** live-tested both P_020's and P_400's tokens right now (read-only `get_account_numbers()`, no new logins) -- both succeeded, even though P_400's file had sat untouched for 2 days through at least one of P_020's own refreshes. This directly contradicts the 2026-08-18 Occurrence Log conclusion that a routine, non-login refresh kills the other project's copy. Logged both this contradiction and the 2026-08-22 decision-deferral ("not ready to make call, nothing failed") into WO-P020-E1.010.md, which previously only reflected state through 8/18. Tony's decision this session: explicit wait-and-see, no separate Schwab app registration, no formal accept-reauth -- current ALL-mode design keeps running. Review checkpoint: 2026-09-05 (next Saturday weekly run), or sooner if either project actually fails.
- Both WOs (E1.010, E1.015) remain open. E1.010 IN_PROGRESS (decision recorded, direction still pending). E1.015 close to ready for Independent Review once its WO file is rewritten.

## 2026-08-29

Weekly automated run (Cowork) completed successfully. DB: 93 trades, 17 open, latest trade 8/25. Dashboard regenerated (`docs\P_020_Dashboard.html`).

## 2026-08-22 -- Major closeout session (6 WOs Independent-Reviewed to CLOSED)

Independent Review performed on E1.002, E1.007, E1.009, E1.011, E1.014, E1.016 -- separate session from implementation, all -> CLOSED same day.

- **E1.002** (multi-leg spreads, paper): wiring gap fixed -- spread detection existed but was never reachable from the command Tony actually runs; wired `paper_import.py` -> `paper_spread_import.py`. VERTICAL/IRON CONDOR leg-direction rule locked (within each right, first listed strike = container's action, second = opposite). Backfilled 4 real spread trades (trade_id 3141-3144, tagged `system=P_010`; P_010 newly seeded into `systems` table -- never existed before). WO file was accidentally overwritten (`mode="write"` instead of `"append"`) and reconstructed from git + tool-call history same session -- see the file's own RECOVERY NOTE.
- **E1.007** (3 parts): Part 1 token pre-flight verified live via that morning's real scheduled run. Part 2 P_400 vault shadow-mode attribution verified live (2 symbols now show real attribution, confirming a same-session-window P_400 `why_code` persistence fix from 8/16 works end-to-end in production). Part 3 live ThinkLog tagging confirmed fail-soft (no live ThinkLog export existed yet this run -- correct no-op, not a defect).
- **E1.009 / E1.011 / E1.014**: Buying Power/Cash Available + full account params (Balance/Risk/Max/History) now auto-write into `P_000_Account_Parameters_Current.md`, threshold-gated (+/-10% vs. baseline), now timestamped on write.
- **E1.016**: `cash_available` field-fallback fix (`availableFunds` when `cashAvailableForTrading` absent) confirmed live 2 days post-fix -- real $19,630.49 pulled 8/22.
- **Dry-run bug found & fixed**: `--dry-run` only skipped `last_run.json`; DB writes still committed regardless. Caught live -- **9 IRA9885 trades wrote to the DB without approval** during this session's testing (still in the DB today: trade_ids 3132-3140, tagged `system='INV'`, `reason='INV'`, `signal_strength=NULL` -- see E1.015 note below, this needs a decision). Fixed in the ingest/write path; 4 regression tests added proving zero writes in dry-run mode.
- **Schema fix**: `_create_trades_table()` was missing `reason`/`signal_strength` in the CREATE statement (only ever added via a migration) -- would've broken a fresh `init-db`. Fixed.
- **E1.015 (IRA ingestion) status correction**: the WO ledger file still says PENDING/not-started, but most of its SCOPE was actually built this session as a side effect of the dry-run-bug fix work: `P_020_Schwab_Trade_Pull.py` already accepts `--account IRA/BOTH`; `import_command.py` already resolves IRA -> `IRA9885` + `inherited_roth` pull folder; `system_attribution.py` already bypasses vault/Tracker for IRA9885 per the WO's Decision 1. **Not done**: the 9 live IRA rows have `signal_strength=NULL`, which fails the WO's own Acceptance Criteria ("reason/signal_strength populated from ThinkLog, not NULL") -- these look like they came from a default `INV` fallback, not a real ThinkLog join. Needs a decision: re-tag from real ThinkLog data, or accept `INV`/NULL as sufficient and move on.

## 2026-08-20

E1.015 opened. Decisions locked same session (system/tag source = ThinkLog `INV`-or-real-project-code, bypass `system_resolver.py`; date scope 1/1/26 forward; Symbol+Date join same as paper). WO file says PENDING, build not started -- see 8/22 entry above for what was actually built days later.

## 2026-08-18

E1.010: `cli.py --project` default changed to `ALL`. The 7-day shared-token-stability assumption was FALSIFIED -- a shared ALL-mode grant did not survive even one project's routine, non-login refresh call. Fresh ALL-mode grant re-established 19:09 ET, P_400/P_020 token files confirmed byte-identical (SHA-256). Still IN_PROGRESS -- needs Tony's decision: separate Schwab app registration for P_400, or accept recurring reauth as a permanent cost.

## 2026-08-16

E1.007 Part 3: live-account ThinkLog tagging built (`why_code`/system override, OCC option symbol normalization, 3-day forward window, standalone backfill command). 61 tests passing. Same session: found and fixed a P_400 bug where `record_writer.py` received `signal_source` on every call but discarded it before persisting `why_code` -- one-line fix, `why_code` now populates correctly for P_115/P_300 flow.

## 2026-07-26

E1.002 core logic built (multi-leg spread detection, paper-first) -- corrected from a mis-scoped original WO (real affected file was the legacy TOS CSV parser, not `schwab_mapper.py`).
E1.009 implemented: Schwab balance pull now writes Buying Power/Cash Available into P_000 Account Parameters.

## 2026-07-25

E1.007 Part 1: scheduled weekly update had failed silently on an expired Schwab token (buried in the log, nothing surfaced it). Added a fail-fast pre-flight check (Step 0), distinct exit code + STATUS_FILE flag.
E1.007 Part 2 opened: P_400 vault shadow-mode system attribution built (measurement only, Tracker stays authoritative) -- Tracker coverage found structurally thin for P_116/SNT/DAY trades.
All trade projects began routing through P_400 as of this date.

## 2026-07-21

**WO-P800-E3.002** (same-day same-symbol vault filename collision) --
P_020-side COMPLETE, Tony acked in chat. Independent review
(WO_COMPLETION_GATE.md) is the only remaining gate before this WO closes
-- needs a separate session.

What happened this session:
- `python\database\domain\vault_mapper.py`: added `trade_id` to the
  payload (str-cast via new `_to_str()` helper -- first attempt passed
  a raw int and failed P_800's Pydantic validation on all 201 rows,
  caught pre-write, 0 files touched). 90 -> 96 lines.
- `tests\test_p020_vault_export.py`: +1 test
  (`test_trade_id_passed_through`). 8/8 passing.
- Re-ran `write_to_obsidian.py --commit`: 201 written, 0 errors, 0
  skipped. Confirmed via read-only validation against
  `obsidian_writers.domain.validator.validate` before the real commit.
- Found and archived 190 stale pre-fix vault notes (old symbol-only
  filenames from the 2026-07-11 run, including the original
  POWL/VSAT/GOOG collision-collapsed ones) to
  `trading_journal\TradeManagement\_archive\P020_pre_tradeid_fix\`
  -- moved outside `TradeManagement/P020` specifically because
  `P020_Performance.base` matches on a folder-path substring, not an
  exact path (see SKILL.md Vault Export section, added this session).
- `p020-project-context/SKILL.md` bumped to v2.4 with both findings.

**Next session:** independent review of WO-P800-E3.002 against its
Acceptance Criteria (fresh eyes, not this session) is the only thing
blocking CLOSE.
