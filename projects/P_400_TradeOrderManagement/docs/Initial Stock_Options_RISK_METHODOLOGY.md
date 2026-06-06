# Options Risk Management - Hybrid Methodology

## Philosophy

Two complementary approaches for options stop placement:
1. **Chart-Based** (PRIMARY): Connects stops to market structure
2. **Risk-Budget-First** (SECONDARY): Enforces capital limits

**Risk budget acts as:**
- **Chart-Based method**: Position sizing gate
- **Risk-Budget-First method**: Stop calculation input

---

## PRIMARY METHOD: Chart-Based with Delta Translation

### When to Use
- ✅ Clear technical setup on stock chart
- ✅ Defined support/resistance levels
- ✅ ATR-based stop placement makes sense
- ✅ Standard systematic trading approach

### Workflow

**Step 1: Stock Analysis**
```
Entry Price: $81.53
Technical Stop: $74.00 (consolidation support)
Risk per Share: $81.53 - $74.00 = $7.53
Target Price: $104.12
R:R: ($104.12 - $81.53) / $7.53 = 3:1
```

**Step 2: Options Translation**
```
Contract: MCHP260320C80
Entry Premium: $5.40
Delta: 0.6074

Stop Premium Calculation:
= Entry Premium + (Delta × Stock Price Movement)
= $5.40 + (0.6074 × -$7.53)
= $5.40 - $4.57
= $0.83

Target Premium:
= $5.40 + (0.6074 × $22.59)
= $5.40 + $13.72
= $19.12

Risk per Contract:
= (Entry - Stop) × 100
= ($5.40 - $0.83) × 100
= $457
```

**Step 3: Position Sizing (Three Gates)**
```
Gate 1 - Risk Budget: $262.50 (CORRECTION mode)
Contracts = $262.50 ÷ $457 = 0.57 → 0 contracts

Gate 2 - Cash Available: $7,090
Contracts = $7,090 ÷ ($5.40 × 100) = 13.1 contracts

Gate 3 - Max 5% Position: $35,000 × 0.05 = $1,750
Contracts = $1,750 ÷ ($5.40 × 100) = 3.2 contracts

SMALLEST GATE: 0 contracts (Gate 1)
```

**Step 4: Decision**
- **Option A**: OVERRIDE to 1 contract (document justification)
- **Option B**: FALLBACK to stock (21 shares × $81.53)
- **Option C**: REJECT trade (wait for better opportunity)

### Advantages
- ✅ Stops connected to market structure
- ✅ Invalidation point has technical meaning
- ✅ Standard industry practice
- ✅ Easy to communicate and backtest

### Disadvantages
- ❌ May produce risk > budget (requires override)
- ❌ Fractional contracts round to 0 or 1
- ❌ CORRECTION mode often triggers overrides

---

## SECONDARY METHOD: Risk-Budget-First

### When to Use
- ✅ No clear technical stop on chart
- ✅ Maximum capital preservation required
- ✅ Testing new strategy with tight limits
- ✅ Weak or ambiguous chart setup

### Workflow

**Step 1: Risk Budget Determination**
```
Account Balance: $35,000
Risk %: 0.75% (CORRECTION mode)
Risk Budget: $35,000 × 0.0075 = $262.50
```

**Step 2: Stop Calculation (Method A - Pure Risk Budget)**
```
Entry Premium: $5.40
Max Premium Loss: $262.50 ÷ 100 = $2.625
Stop Premium: $5.40 - $2.625 = $2.775 (round to $2.78)
Risk: $262.50 ✅
```

**Step 3: Validation (Method B - 2 ATR Floor)**
```
Stock ATR: $3.22
2 ATRs: $3.22 × 2 = $6.44
Delta-adjusted: $6.44 × 0.6074 = $3.91
Stop Premium: $5.40 - $3.91 = $1.49
Risk: $3.91 × 100 = $391
```

**Step 4: Select Tighter Stop**
```
Risk-Budget Stop: $2.78 (risk $262)
2-ATR Stop: $1.49 (risk $391)

FINAL: $1.49 (tighter = 2-ATR)
ACTUAL RISK: $391 (exceeds budget by $128)
```

**Step 5: Decision**
- Risk $391 > Budget $262.50
- Still requires override OR
- Use Risk-Budget stop $2.78 (may be too tight vs. volatility)

### Advantages
- ✅ Enforces strict capital limits
- ✅ Automatic position sizing (1 contract if within budget)
- ✅ No mental math needed
- ✅ Conservative approach

### Disadvantages
- ❌ Stops may be arbitrary (no technical basis)
- ❌ Can be too tight for normal volatility
- ❌ May stop out prematurely
- ❌ Still often exceeds budget (due to 2-ATR floor)

---

## Method Comparison Example: MCHP Trade

### Scenario
- Account: $35,000
- Mode: CORRECTION (0.75% risk = $262.50)
- Stock: MCHP @ $81.53, Stop $74.00, ATR $3.22
- Option: Entry $5.40, Delta 0.6074

### Chart-Based Method
```
Stock stop → $74.00
Option stop → $0.83 (delta-adjusted)
Risk → $457
Position → 0.57 contracts → 0
Decision → OVERRIDE to 1 contract
Justification → Eddie Z breakout, volume confirmed
Result → Execute 1 contract, document $194 overshoot
```

### Risk-Budget-First Method
```
Risk budget → $262.50
Option stop → $2.78 (risk-budget) or $1.49 (2-ATR)
Risk → $262 or $391
Position → 1 contract (if using $2.78 stop)
Decision → Execute with tight stop OR reject due to 2-ATR floor
Result → Tight stop may not respect volatility
```

### Recommendation: Chart-Based with Override
**Why:** Eddie Z pattern provides technical context, chart stop at $74 has structural meaning, risk overshoot is acceptable for high-conviction setup.

---

## Decision Framework

### Use Chart-Based When:
1. ✅ Eddie Z pattern confirmed
2. ✅ P_115 shows strong HybridTier (even if "No Signal")
3. ✅ Clear support/resistance on daily chart
4. ✅ ATR-based stop makes technical sense
5. ✅ Pattern has clear invalidation point

### Use Risk-Budget-First When:
1. ✅ No clear technical structure
2. ✅ Testing new strategy conservatively
3. ✅ Maximum capital preservation required
4. ✅ Weak chart setup but other confluence
5. ✅ Learning/paper-trading phase

### Neither Method Works If:
- ❌ Chart-based produces risk > 2× budget (too aggressive)
- ❌ Risk-budget produces stop < $0.10 (unmanageable)
- ❌ 2-ATR floor produces risk > 3× budget (too volatile)
→ **Fallback to stock or reject trade**

---

## Override Protocol (Applies to Both Methods)

### When to Override
- Strong confluence across multiple systems (P_115 + P_118 + P_300)
- Exceptional chart setup (breakout + volume)
- Pattern-based signal from trusted source (Eddie Z)
- Risk overshoot < 100% of budget

### Documentation Requirements
**Must include in SimulationNotes:**
1. Method used (Chart-Based or Risk-Budget-First)
2. Calculated risk vs. budget
3. Overshoot amount and percentage  
4. Specific justification (not generic)

**Format:**
```
1 contract [SYMBOL], Entry: $X.XX, Stop: $Y.YY (chart-based/risk-budget), 
Target: $Z.ZZ, Risk: $RRR (exceeds [MODE] budget $BBB by $OOO/PP%, 
approved for [specific reason: breakout/pattern/confluence])
```

**Example:**
```
1 contract MCHP260320C80, Entry: $5.40, Stop: $0.83 (chart-based at $74 stock), 
Target: $19.12, Risk: $457 (exceeds CORRECTION budget $262.50 by $194/74%, 
approved for Eddie Z High Handle breakout with volume surge)
```

---

## Integration with Strategy Systems

### P_115 (Buy The Dip)
- **Method**: Chart-Based (PRIMARY)
- **Stops**: Support levels, value zones, wickAlign points
- **Options**: Translate support stop via delta

### P_116 (Options Income)
- **Method**: Risk-Budget-First OR Chart-Based
- **Stops**: Premium decay consideration, bounce failure
- **Options**: Native options strategy, premium-focused

### P_118 (Eddie Z Breakouts)
- **Method**: Chart-Based (PRIMARY)
- **Stops**: Pattern invalidation (handle breakdown)
- **Options**: Leverage breakout moves with chart stops

### P_117 (Outside Recommendations)
- **Method**: Depends on source quality
- **Stops**: Chart-Based if technicals provided
- **Options**: Case-by-case evaluation

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using stock stop without delta translation
```
WRONG: Stock stop $74, so option stop is also $74
RIGHT: Stock stop $74, option stop = Entry + (Delta × Stock Risk)
```

### ❌ Mistake 2: Ignoring risk budget entirely
```
WRONG: Chart says stop at $0.50, so I'll use that regardless of risk
RIGHT: Chart stop produces $590 risk vs $262 budget → requires override
```

### ❌ Mistake 3: Treating maximum loss = calculated risk
```
WRONG: My risk is $457, that's the most I can lose
RIGHT: Maximum loss is 100% of premium ($540), calculated risk is exit point
```

### ❌ Mistake 4: Rounding 0.57 contracts to 1 without override
```
WRONG: Risk math gives 0.57, I'll just do 1 contract
RIGHT: 0.57 → 0 contracts, need explicit override to execute 1
```

### ❌ Mistake 5: Using risk-budget method with strong chart setup
```
WRONG: Chart shows perfect setup, but I'll use risk-budget stop for safety
RIGHT: Chart-Based method respects market structure, use that
```

---

## Validation Checklist

Before executing ANY options trade:

**Method Selection:**
- [ ] Clear technical stop exists? → Chart-Based
- [ ] Weak/no technical stop? → Risk-Budget-First
- [ ] Method selection justified

**Calculation (Chart-Based):**
- [ ] Stock entry/stop/target identified
- [ ] Option stop calculated via delta translation
- [ ] Risk per contract = (Entry - Stop) × 100
- [ ] Position sized via three gates
- [ ] Override documented if position < 1

**Calculation (Risk-Budget-First):**
- [ ] Risk budget determined
- [ ] Risk-budget stop calculated
- [ ] 2-ATR stop calculated
- [ ] Tighter stop selected
- [ ] Risk validated ≤ budget (or override)

**Liquidity (Both Methods):**
- [ ] Spread ≤ 10% of mid
- [ ] Open Interest ≥ 150
- [ ] Option R:R ≥ Stock R:R

**Documentation (Both Methods):**
- [ ] Method used noted in Comments
- [ ] Override justified in SimulationNotes (if applicable)
- [ ] All 27 columns populated
- [ ] Audit trail complete

---

## Example Trade Log Entries

### Chart-Based (No Override Needed)
```
Symbol: XYZ
Entry: $3.20
Stop: $2.50 (chart-based at $65 stock)
Target: $8.30
Risk: $70 per contract
Risk Budget: $525 (normal mode)
Position: 7 contracts
Method: Chart-Based ✅
```

### Chart-Based (Override Required)
```
Symbol: MCHP  
Entry: $5.40
Stop: $0.83 (chart-based at $74 stock)
Target: $19.12
Risk: $457 per contract
Risk Budget: $262.50 (CORRECTION mode)
Position: 1 contract (override)
Method: Chart-Based + Override ⚠️
Justification: Eddie Z High Handle, volume surge, HybridTier=4
```

### Risk-Budget-First (Within Budget)
```
Symbol: ABC
Entry: $2.80
Stop: $1.90 (risk-budget method)
Target: $6.50
Risk: $90 per contract
Risk Budget: $262.50 (CORRECTION mode)
Position: 2 contracts
Method: Risk-Budget-First ✅
Note: No clear chart stop, used conservative capital limits
```

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Status:** Active - Hybrid methodology approved
