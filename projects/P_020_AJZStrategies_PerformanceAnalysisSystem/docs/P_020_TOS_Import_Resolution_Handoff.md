# P_020 TOS_Import Resolution — Handoff to P_020 Session
**Date:** 2026-06-01
**Purpose:** Resolve system=TOS_Import trades so Workstream D (trade-bucket analysis) has a usable sample.

---

## Why This Matters

P_010 Phase 2 Workstream D needs to bucket closed P_115/P_118 trades by market_phase and compute win-rate delta. Currently only 41 trades are properly tagged. The 385 TOS_Import trades are untagged and unusable for the analysis.

---

## Current Database State

**Already tagged (usable now):**
| System | Trades | Date Range |
|--------|--------|------------|
| P_115 | 9 | 2026-01-02 to 2026-04-09 |
| P_118 | 32 | 2026-01-08 to 2026-05-22 |
| P_116 | 20 | 2024-12-04 to 2026-04-27 |
| P_117 | 14 | 2026-01-09 to 2026-03-06 |
| **Total** | **75** | |

**Unresolved TOS_Import (385 trades):**
| Source | Count | Date Range |
|--------|-------|------------|
| schwab_api | 325 | 2024-10-29 to 2026-05-27 |
| tos_import | 60 | 2026-01-02 to 2026-04-09 |

Monthly volume: roughly 10–43 trades/month going back to Oct 2024.

---

## What Needs to Happen in P_020

The 325 schwab_api + 60 tos_import trades with system=TOS_Import need their `system` and `tags` fields updated to the correct strategy name.

**Matching approach (use ThinkLog entries):**
- ThinkLog format: `MMDD: [WHY] [SIG] free text`
- WHY codes: BTD=P_115 | OIL=P_116 | EXT=P_117 | EZB=P_118 | VPT=P_300 | SNT=BigTrends
- Match on: open_date + underlying_symbol → look up ThinkLog entry for that date/symbol → assign system from WHY tag

**For trades with no ThinkLog match:**
- Manual review needed, or accept as unresolvable and exclude from Workstream D

---

## Priority

The most valuable trades to resolve are those that overlap with the snapshot archive window (Apr 23 onward) OR can extend the P_115/P_118 sample back into 2025 where there's more phase variety (corrections, uptrends) for a meaningful bucket analysis.

The 60 tos_import source trades (Jan–Apr 2026) are most likely to be P_115/P_118 given the date range aligns exactly with when those systems were active. Resolve these first.

---

## What to Tell P_020 Claude

> "I have 385 closed trades with system=TOS_Import and tags=None in P_020_trades.db. I need to resolve as many as possible to their correct system (P_115, P_116, P_117, P_118) using ThinkLog entries. The 60 tos_import source trades from Jan–Apr 2026 are highest priority. After resolution, I need the total P_115+P_118 count to exceed 50 for a downstream analysis."

---

## After Resolution — Return to P_010

Come back to this P_010 session (or start a new P_010 session) with:
- Updated count of resolved P_115 and P_118 trades
- Date range of those trades

Workstream D can then proceed with backfilling the phase archive to cover that date range and running the bucket analysis.

