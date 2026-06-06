# P_000 Account Parameters — All Trading Projects
**File:** P_000_Account_Parameters_Current.md
**Location:** C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\
**Last Updated:** April 8, 2026
**Next Review:** May 2026 (monthly) or when balance hits $35,000

---

## Active Parameters

| Parameter | Value |
|-----------|-------|
| Account Balance | $31,668.31 |
| Risk per Trade | 1.5% = $475.02 |
| Max Position (5%) | $1,583.42 |
| Options Rule | 5% limit applies to PREMIUM PAID, not notional exposure |

---

## Risk Mode Adjustments (from P_010_RiskConfig.json)

| Risk Mode | Risk/Trade | Max Position | Notes |
|-----------|------------|--------------|-------|
| OFF / CORRECTION | $237.51 (50%) | $791.71 (50%) | avg_posture < -1.0 |
| HALF | $356.27 (75%) | $1,187.57 (75%) | 25% reduction |
| STANDARD | $475.02 | $1,583.42 | Base risk |
| FULL | $475.02 | $1,583.42 | Same as STANDARD |
| HOT | Tiered up to 5% | Up to $1,583.42 | avg_posture > 1.08 |

---

## Critical Rules

### Cash Balance (Separate Concept)
User provides per-trade available buying power. This is NOT account balance.
- Do NOT subtract trades from cash balance between gates
- Do NOT track remaining cash across trades
- Each trade gets independent cash allocation

### Three-Gate Position Sizing
```
Gate 1 (Risk-Based):    $475.02 / (Entry - Stop)
Gate 2 (Cash Limit):    User-provided per trade
Gate 3 (Concentration): $1,583.42 max (or premium for options)

Final Position Size = SMALLEST of three gates
```

### Options Display Rule
Always show targets/stops with BOTH stock and option prices:
```
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

---

## Growth Projections

| Balance | Risk (1.5%) | Max Position (5%) |
|---------|-------------|-------------------|
| $31,668.31 (current) | $475.02 | $1,583.42 |
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

