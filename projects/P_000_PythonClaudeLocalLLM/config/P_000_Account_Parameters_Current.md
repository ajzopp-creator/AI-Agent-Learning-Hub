# P_000 Account Parameters ? All Trading Projects

**File:** P_000_Account_Parameters_Current.md
**Location:** C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\
**Last Updated:** August 04, 2026
**Next Review:** September 2026 (monthly) or when balance hits $35,000

---

## Active Parameters

| Parameter | Value |
|-----------|-------|
| Account Balance | $31,348.39 |
| Risk per Trade | 1.5% = $470.23|
| Max Position (5%) | $1,567.42 |
| Options Rule | Use underlying STOCK price as the management trigger for option positions; execute exits with stop-limit logic and bid-aware option pricing to reduce gap-through risk |
| Buying Power | $35,965.70 (pulled Aug 29, 2026 9:05 AM) |
| Cash Available for Trading | $17,982.85 (pulled Aug 29, 2026 9:05 AM) |

---

## Risk Mode Adjustments (from P_010_RiskConfig.json)

**Authority rule:** `risk_mode` in P_010_RiskConfig.json is the authoritative value at all times. The avg_posture thresholds below are reference ranges only ? the JSON field governs when they conflict.

| Risk Mode | Risk/Trade | Max Position | Notes |
|-----------|------------|--------------|-------|
| OFF / CORRECTION | $235.12 (50%) | $783.71 (50%) | avg_posture < -1.0 |
| HALF | $352.67 (75%) | $1,175.57 (75%) | 25% reduction |
| STANDARD | $470.23 | $1,567.42 | Base risk |
| FULL | $470.23 | $1,567.42 | Same as STANDARD |
| HOT | Tiered up to 5% | Up to $1,567.42 | avg_posture > 1.08 |

---

## Critical Rules

### Cash Balance (Separate Concept)
**Note (WO-P020-E1.009):** Buying Power and Cash Available for Trading in the table above are broker-reported reference numbers only. P_400's `--cash` flag on evaluate/spec/compare stays a manual figure Tony types himself -- never auto-read from these fields. Exception (2026-08-25): batch-2b auto-reads Cash Available for Trading from this file via P_400_Batch2b_CashPull.bat / P_400_Batch2bCashPull_mcp.ps1, which pulls a fresh balance first. evaluate/spec/compare are unaffected.
User provides per-trade available buying power. This is NOT account balance.
- Do NOT subtract trades from cash balance between gates
- Do NOT track remaining cash across trades
- Each trade gets independent cash allocation

### Three-Gate Position Sizing
```text
Gate 1 (Risk-Based):    $470.23 / (Entry - Stop)
Gate 2 (Cash Limit):    User-provided per trade
Gate 3 (Concentration): $1,567.42 max (or premium for options)

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
| Aug 4, 2026 | $31,348.39 | $470.23 | $1,567.42 | Monthly review -- Net Liq per broker (live pull) |

---

## Growth Projections

| Balance | Risk (1.5%) | Max Position (5%) |
|---------|-------------|-------------------|
| $31,348.39 (current) | $470.23 | $1,567.42 |
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
- August 4, 2026 - Updated Account Balance to $31,348.39 (Net Liq per broker, live Schwab pull); synced derived tables to base $470.23 / $1,567.42 (Risk Mode Adjustments, Three-Gate block, Growth current row); Next Review moved to September 2026. Buying Power / Cash Available auto-written by the same pull per WO-P020-E1.009.

