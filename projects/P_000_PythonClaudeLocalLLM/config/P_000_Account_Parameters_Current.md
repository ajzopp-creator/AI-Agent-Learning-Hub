# P_000 Account Parameters ? All Trading Projects

**File:** P_000_Account_Parameters_Current.md
**Location:** C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\
**Last Updated:** July 01, 2026
**Next Review:** August 2026 (monthly) or when balance hits $35,000

---

## Active Parameters

| Parameter | Value |
|-----------|-------|
| Account Balance | $32,072.00 |
| Risk per Trade | 1.5% = $481.08|
| Max Position (5%) | $1,603.60 |
| Options Rule | Use underlying STOCK price as the management trigger for option positions; execute exits with stop-limit logic and bid-aware option pricing to reduce gap-through risk |

---

## Risk Mode Adjustments (from P_010_RiskConfig.json)

**Authority rule:** `risk_mode` in P_010_RiskConfig.json is the authoritative value at all times. The avg_posture thresholds below are reference ranges only ? the JSON field governs when they conflict.

| Risk Mode | Risk/Trade | Max Position | Notes |
|-----------|------------|--------------|-------|
| OFF / CORRECTION | $240.54 (50%) | $801.80 (50%) | avg_posture < -1.0 |
| HALF | $360.81 (75%) | $1,202.70 (75%) | 25% reduction |
| STANDARD | $481.08 | $1,603.60 | Base risk |
| FULL | $481.08 | $1,603.60 | Same as STANDARD |
| HOT | Tiered up to 5% | Up to $1,603.60 | avg_posture > 1.08 |

---

## Critical Rules

### Cash Balance (Separate Concept)
User provides per-trade available buying power. This is NOT account balance.
- Do NOT subtract trades from cash balance between gates
- Do NOT track remaining cash across trades
- Each trade gets independent cash allocation

### Three-Gate Position Sizing
```text
Gate 1 (Risk-Based):    $481.08 / (Entry - Stop)
Gate 2 (Cash Limit):    User-provided per trade
Gate 3 (Concentration): $1,603.60 max (or premium for options)

Final Position Size = SMALLEST of three gates
```

### Options Management Rule
For option positions, use the underlying stock price as the protection and management trigger by default.
Do NOT assume the trigger is the option Mark unless the trade plan explicitly says Mark.
When generating exits, use stop-limit structure and bid-aware option pricing where spreads are wide to improve control and reduce gap-through risk.

### Options Display Rule
Always show targets/stops with BOTH stock and option prices:
```text
Entry:       Stock $XX.XX --> Option $X.XX
Take Profit: Stock $XX.XX --> Option ~$X.XX (+XX% gain)
Stop Loss:   Stock $XX.XX --> Option ~$X.XX (-XX% loss)
```
Calculate option prices using delta. Show leverage multiple.

---

## Applies To

- P_115: Buy The Dip
- P_116: Options Income Launchpad
- P_117: Outside Recommendations
- P_118: Eddie Z Breakouts
- P_300: VantagePoint Grid
- P_400: Trade Order Management

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
| June 3, 2026 | $32,669.72| $490.04 | $1,633.47 | Monthly review -- Net Liq per broker |
| July 1, 2026 | $32,072.00 | $481.08 | $1,603.60 | Monthly review -- Net Liq per broker |

---

## Growth Projections

| Balance | Risk (1.5%) | Max Position (5%) |
|---------|-------------|-------------------|
| $32,072.00 (current) | $481.08 | $1,603.60 |
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

- May 31, 2026 ? Perplexity P_400_Trade Management System ? corrected option rule to use stock-price management trigger with stop-limit and bid-aware option exit handling.
- June 3, 2026 - Updated Account Balance
- June 3, 2026 - Synced derived tables to base $490.04 / $1,633.47 (Risk Mode Adjustments, Three-Gate block, Growth current row) 
- June 16, 2026 - Added authority rule clarifying JSON risk_mode governs over avg_posture thresholds (WO-P010-E1.001 Option A)
- July 1, 2026 - Updated Account Balance to $32,072.00 (Net Liq per broker); synced derived tables to base $481.08 / $1,603.60 (Risk Mode Adjustments, Three-Gate block, Growth current row); Next Review moved to August 2026

