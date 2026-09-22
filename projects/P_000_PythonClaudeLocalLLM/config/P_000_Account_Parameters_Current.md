# P_000 Account Parameters — All Trading Projects
**File:** P_000_Account_Parameters_Current.md
**Location:** C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\
**Last Updated:** September 02, 2026
**Next Review:** October 2026 (monthly) or when balance hits $35,000

---

## Active Parameters

| Parameter | Value |
|-----------|-------|
| Account Balance | $29,458.74 |
| Risk per Trade | 1.5% = $441.88 |
| Max Position (5%) | $1,472.94 |
| Options Rule | Use underlying STOCK price as the management trigger for option positions; execute exits with stop-limit logic and bid-aware option pricing to reduce gap-through risk |
| Buying Power | $30,016.30 (pulled Sep 22, 2026 9:34 AM) |
| Cash Available for Trading | $15,008.15 (pulled Sep 22, 2026 9:34 AM) |

*Refreshes automatically at 9:30 AM and 2:00 PM (P_010 daily/intraday cycle). P_400's `--cash` flag can still override this per trade when supplied.*

---

## Risk Mode Adjustments (from P_010_RiskConfig.json)

**Authority rule:** `risk_mode` in P_010_RiskConfig.json is the authoritative value at all times. The avg_posture thresholds below are reference ranges only -- the JSON field governs when they conflict.

| Risk Mode | Risk/Trade | Max Position | Notes |
|-----------|------------|--------------|-------|
| OFF / CORRECTION | $220.94 (50%) | $736.47 (50%) | avg_posture < -1.0 |
| HALF | $331.41 (75%) | $1,104.71 (75%) | 25% reduction |
| STANDARD | $441.88 | $1,472.94 | Base risk |
| FULL | $441.88 | $1,472.94 | Same as STANDARD |
| HOT | Tiered up to 5% | Up to $1,472.94 | avg_posture > 1.08 |

---

## Sizing & Options Rules

Canonical source: P_400 (`P_400_TradeOrderManagement_Architecture_v2_0.md` Sec 3.3/3.4, `P_400_PositionSizing_TradeManagement_v1_0.md`). This file holds only the dollar figures P_400 reads -- balance, risk, max position, cash. Rule text (cash-per-trade, three-gate formula, options management/display) lives in P_400, not here.

---

## Applies To

- P_116: Options Income Launchpad
- P_117: Outside Recommendations
- P_118: Eddie Z Breakouts
- P_300: VantagePoint Grid
- P_400: Trade Order Management (sizes P_115 trades on its behalf -- P_115 itself does not size)

---

## Update Triggers

1. End of each month (mandatory review)
2. Account growth >= 10% from last update
3. Milestones: $35K | $40K | $50K | $75K

---

## Parameter History

| Date | Balance | Risk (1.5%) | Max (5%) | Notes |
|------|---------|-------------|----------|-------|
| Jan 23, 2026 | $30,000 | $450.00 | $1,500.00 | System initialization |
| Mar 9, 2026 | $32,298 | $484.47 | $1,614.90 | Monthly review update |
| Apr 8, 2026 | $31,668.31 | $475.02 | $1,583.42 | Monthly review -- Net Liq per broker |
| May 1, 2026 | $32,812.00 | $492.18 | $1,640.60 | Monthly review -- Net Liq per broker |
| June 3, 2026 | $32,669.72 | $490.04 | $1,633.47 | Monthly review -- Net Liq per broker |
| July 1, 2026 | $32,072.00 | $481.08 | $1,603.60 | Monthly review -- Net Liq per broker |
| Aug 4, 2026 | $31,348.39 | $470.23 | $1,567.42 | Monthly review -- Net Liq per broker (live Schwab pull) |
| Sep 2, 2026 | $29,458.74 | $441.88 | $1,472.94 | Monthly review -- Net Liq per broker |

---

## Growth Projections

| Balance | Risk (1.5%) | Max Position (5%) |
|---------|-------------|-------------------|
| $29,458.74 (current) | $441.88 | $1,472.94 |
| $35,000 | $525.00 | $1,750.00 |
| $40,000 | $600.00 | $2,000.00 |
| $50,000 | $750.00 | $2,500.00 |
| $75,000 | $1,125.00 | $3,750.00 |
| $100,000 | $1,500.00 | $5,000.00 |

---

## Monthly Review Checklist

- [ ] Pull current balance from broker
- [ ] Calculate new Risk Capital (Balance x 0.015)
- [ ] Calculate new Max Position (Balance x 0.05)
- [ ] Update this file (balance, risk, max, history table)
- [ ] Update Claude memory via memory_user_edits tool
- [ ] No changes needed to SESSION_INITIALIZATION_PROMPT.md (reads from here)

---

## Change Log

- May 31, 2026 -- Perplexity P_400_Trade Management System -- corrected option rule to use stock-price management trigger with stop-limit and bid-aware option exit handling.
- June 3, 2026 - Updated Account Balance
- June 3, 2026 - Synced derived tables to base $490.04 / $1,633.47 (Risk Mode Adjustments, Three-Gate block, Growth current row)
- June 16, 2026 - Added authority rule clarifying JSON risk_mode governs over avg_posture thresholds (WO-P010-E1.001 Option A)
- July 1, 2026 - Updated Account Balance to $32,072.00 (Net Liq per broker); synced derived tables to base $481.08 / $1,603.60 (Risk Mode Adjustments, Three-Gate block, Growth current row); Next Review moved to August 2026
- Aug 4, 2026 - Updated Account Balance to $31,348.39 (live Schwab pull, Net Liq per broker); synced derived tables to base $470.23 / $1,567.42; Next Review moved to September 2026
- Sep 2, 2026 - Updated Account Balance to $29,458.74 (Net Liq per broker); synced derived tables to base $441.88 / $1,472.94 (Risk Mode Adjustments, Three-Gate block, Growth current row); Next Review moved to October 2026. Prior live file had reverted to stale May 1 content (missing Buying Power/Cash Available fields, missing Options Management Rule detail, missing Aug 4 update) -- restored full structure from the Aug 4 pre-edit backup and reconstructed the Aug 4 history row from session record.
- Sep 15, 2026 - Removed Critical Rules section (Cash Balance, Three-Gate, Options Management/Display rules) -- all already canonical in P_400 Architecture v2.0 / PositionSizing docs; replaced with a pointer. Removed P_115 from Applies To (P_400 sizes P_115 trades on its behalf; P_115 itself does not size). Cash Available for Trading now refreshes automatically 9:30 AM + 2:00 PM via P_010's daily/intraday cycle (WO-P010 cash automation); P_400's `--cash` flag still overrides per trade when supplied, no longer required on every call.