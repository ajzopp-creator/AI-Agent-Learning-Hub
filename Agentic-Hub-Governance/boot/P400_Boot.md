**Suggested chat name:** P400 Saturday, September 26, 2026

# P_400 Trade Order Management — Boot Summary
Generated: 2026-09-26, updated at the end of the day's session (commit `b816abe`, pushed). Sources: WO-P400-* files read live, `p400-project-context` SKILL.md (changelog through 2026-09-26), P_020 `orders` table, `tasks\todo.md` (latest entry 2026-09-21, now partly stale -- see Flags).

## Work Order Status (open WOs only)

No WO is BLOCKED. Market closed today (Saturday).

| WO | Task | Status | Note |
| :--- | :--- | :--- | :--- |
| E3.010 | Spec cache miss on CAUTION/SEVERE_WARNING verdicts | CODE FIX BUILT (2026-07-25) | Needs a live evaluate→spec run for both verdict tiers in one session. Stale ~2 months. |
| E3.011 | VERDICT_MAP missing SEVERE_WARNING | P_800 ACK RECEIVED (2026-07-24) | Needs one live SEVERE_WARNING record write before OWNER_DONE. |
| E5.003 | Tier-2B batch runner | IN_PROGRESS (9/11 acceptance) | 2 criteria left before OWNER_DONE. |
| E6.001 | Order lifecycle reconciliation (`orders` table) | IN_PROGRESS | Build done 2026-09-07, migration Gate 1 passed 2026-09-08; remaining gates in the WO. |
| E7.001 | Extended-hours pricing basis | CODE BUILT, live-verified | 5.0% `MAX_PLAUSIBLE_SPREAD_PCT_EXTENDED` still an uncalibrated placeholder. |
| E8.001 | p020_order_writer bridge (schemas collision) | OWNER_DONE (2026-09-26) | Items 2-4 superseded by/covered in E9.002 (Tony's call); gate added. Needs Independent Review. |
| E8.002 | Earnings-cache gate validity | OWNER_DONE (2026-09-26) | Gate completed (PREMISE VERIFICATION + Acks). Needs Independent Review. |
| E8.003 | Packet-free `size-option` + T1/T2 scale-out | OWNER_DONE (2026-09-26) | Gate added; `--target-2` on evaluate/spec scoped out (no follow-on WO); skill now documents `size-option`. Needs Independent Review. |
| E9.001 | hub_mcp_launcher console-log capture | OWNER_DONE on its Status line, but **not actually OWNER_DONE** | 2 acceptance items open (Invoke-HubBat test; 6 non-P_400 callers) and 3 gate boxes unchecked (Imperative Sweep, downstream notify, deferral). Per Enforcement, this is still BUILD COMPLETE. |
| E9.002 | p020_order_writer `schemas_ops` fix | OWNER_DONE (2026-09-21) | All 4 acceptance items done (AMZN resync, tests, consumer audit); gate complete. Needs Independent Review. |
| E9.003 | Chain auto-select ignores affordability | PENDING (filed 2026-09-22) | Not filed as built, but the working tree has uncommitted edits in `chain_selector.py`, `options_sizer.py`, `cli.py`, `fetch_chain.py`, `batch_2b_scoring.py` + tests -- likely in-progress E9.003 work from another session. Not reviewed or committed. |
| E9.004 | Auto-widen stops made too tight by price drift | PENDING (filed 2026-09-25) | Not built. Touches council/verdict paths -- Must Not #7 applies. |
| E9.005 | `record` wrote qty=0 to P_020 for option/spread trades | OWNER_DONE (2026-09-26) | Fixed + 2 regression tests; full suite 418 passed. P_020 Ack pending (Direct). One MONITORING item: check qty on the next live option `record`. |

## Flags / Blockers
- **Five WOs need a separate-session Independent Review:** E8.001, E8.002, E8.003, E9.002, E9.005. None can be closed by the session that did the work.
- **E9.001's Status line overstates it.** Two acceptance items and three gate boxes are open. Either finish them or correct the Status line to BUILD COMPLETE.
- **Uncommitted in-progress code in the P_400 tree** (see E9.003 row). Don't commit it blind, and don't overwrite it -- find out which session owns it first.
- **P_020 data changed today (not in git):** `orders` row 13 AMZN qty 0→1, row 11 NFLX qty 0→4 (NFLX's recorded plan was 4, not the sizer's retroactive 2). DB backups: `P_020_trades.db.backup_2026-09-26` and `..._pre-NFLX`.
- **Skill Bugs table still has no E9.001 or E9.002 rows** (E9.005 row added today).
- **`tasks\todo.md` is stale:** it still says the AMZN P_020 sync is unconfirmed and E8.x are un-gated. Both are resolved.
- **`.backup_2026-09-26` files** for the edited WOs, skill and three code files are on disk, untracked.
- **Posture:** risk_mode was HALF at the last trading session. Read `P_010_RiskConfig.json` live before sizing.

## Lessons Bearing on Open WOs
`tasks\lessons.md` does not exist in this project. The lessons below come from todo.md's "Do NOT" sections, the skill's Must/Must Not rules and today's session:
- **E9.001 (and any WO):** OWNER_DONE without a complete Completion Gate block is not OWNER_DONE (WO_COMPLETION_GATE.md Enforcement).
- **E9.005 / any `record` work:** option and spread records always carry `position_size=0`; the contract count is `option_contracts`. Anything reading size off a P400 record must pick by vehicle.
- **Boot summaries:** check the WO files, not todo.md alone -- today's first boot summary carried a stale AMZN flag from todo.md that E9.002 had already resolved on 9/22.
- **E9.004 (and E3.010/E3.011):** any verdict/council output change must be checked against every verdict-string consumer (spec cache, record allow-list, `VERDICT_MAP`, tests). Gone wrong 4 times. New reason codes go in `council_codes.py` with a test.
- **E9.003:** fix contract affordability as a council vote, not a log line (E3.005 pattern).
- **Skill sync:** doc-sync gaps have recurred 4+ times. Any shipped fix needs its Bugs row and test in the same session.
- **E7.001:** Schwab extended-hours bid/ask of 0.0 means no quote, not a free fill.
- **Tests on Windows:** pytest's default temp dir can throw PermissionError; use `--basetemp` pointed at a scratch folder.

## Suggested Next Step
Run the Independent Review on E8.001, E8.002, E8.003, E9.002 and E9.005 in a fresh session (not this one). All five have their evidence recorded in their WO files, so a reviewer can close them straight from those files.
