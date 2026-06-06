# SESSION_INITIALIZATION_PROMPT.md - ADD THIS SECTION

## Location: After the "Position Sizing" section

---

## Options Risk Management - Hybrid Methodology

### Two-Method System

Options stops can be calculated using TWO methods. Choose based on market conditions and setup quality.

---

#### **PRIMARY METHOD: Chart-Based with Delta Translation** (Standard Practice)

Use when: Strong technical setup with clear chart-based stop levels

**Workflow:**
1. Identify stock technical stop (support, trendline, ATR-based)
2. Calculate stock risk: Entry Price - Stop Price
3. Translate to option stop: Entry Premium + (Delta × Stock Risk)
4. Calculate option risk: (Entry Premium - Stop Premium) × 100
5. Validate against risk budget (acts as position sizing gate)

**Example:**
```
Stock Entry: $81.53
Stock Stop: $74.00 (chart support)
Stock Risk: $7.53

Option Entry: $5.40
Option Delta: 0.6074
Option Stop: $5.40 + (0.6074 × -$7.53) = $0.83
Option Risk: ($5.40 - $0.83) × 100 = $457

Risk Budget: $262.50 (CORRECTION mode)
Position Size: $262.50 ÷ $457 = 0.57 → 0 contracts
Decision: REJECT or OVERRIDE to 1 contract
```

**Result:** Stop placement driven by market structure (chart), position size limited by risk budget.

---

#### **SECONDARY METHOD: Risk-Budget-First** (Conservative)

Use when: Weak technical setup, no clear chart stop, or maximum capital preservation required

**Workflow:**
1. Determine risk budget for trade
2. Calculate max premium loss: Risk Budget ÷ 100
3. Calculate stop premium: Entry Premium - Max Premium Loss
4. Validate using 2-ATR method: (Stock ATR × 2 × Delta)
5. Use TIGHTER of: (a) risk-budget stop, or (b) 2-ATR stop

**Example:**
```
Risk Budget: $262.50
Entry Premium: $5.40
Max Loss: $262.50 ÷ 100 = $2.625
Stop Premium: $5.40 - $2.625 = $2.775

2-ATR Validation:
Stock ATR: $3.22
2 ATRs: $6.44
Delta-adjusted: $6.44 × 0.6074 = $3.91
Stop Premium: $5.40 - $3.91 = $1.49

FINAL STOP: $1.49 (tighter = 2-ATR)
ACTUAL RISK: $391 (exceeds budget, requires override)
```

**Result:** Stop placement driven by capital limits, may disconnect from chart structure.

---

### Method Selection Decision Tree

```
Strong chart setup with clear technical stop?
├─ YES → Use Chart-Based Method (PRIMARY)
│         Risk budget validates position size
│         If position < 1 contract → Override or fallback to stock
│
└─ NO → Use Risk-Budget-First Method (SECONDARY)
          Stop disconnected from technicals
          Maximum capital preservation
          Higher probability of tight/arbitrary stops
```

---

### Position Sizing with Either Method

**Three-Gate System (applies to both methods):**

**Gate 1: Risk-Based**
- Contracts = Risk Budget ÷ Risk per Contract
- Result may be fractional (0.57) → rounds to 0 or 1

**Gate 2: Cash Available**
- Contracts = Cash ÷ (Entry Premium × 100)

**Gate 3: Max 5% Position**
- Contracts = (Account × 0.05) ÷ (Entry Premium × 100)

**Final Position = Smallest of three gates**

**If Gate 1 produces < 1.0 contract:**
- Option A: OVERRIDE to 1 contract (document in SimulationNotes)
- Option B: FALLBACK to stock position
- Option C: REJECT trade (wait for better setup)

---

### Manual Override Protocol

**When risk exceeds budget but setup is strong:**

**Documentation Requirements:**
1. Which method was used (Chart-Based or Risk-Budget-First)
2. Calculated risk vs. budget
3. Overshoot amount and percentage
4. Justification (chart confirmation, pattern quality, confluence)

**Example SimulationNotes:**
```
1 contract MCHP260320C80, Entry: $5.40, Stop: $0.83 (chart-based at $74 stock), 
Target: $19.12, Risk: $457 (exceeds CORRECTION budget $262.50 by $194/74%, 
approved for Eddie Z breakout with volume confirmation)
```

---

### Liquidity Gates (Required for ALL Options)

Must pass ALL three regardless of method used:
- ✅ Spread ≤ 10% of mid price
- ✅ Open Interest ≥ 150
- ✅ Option R:R ≥ Stock R:R (leverage must be justified)

**If any gate fails → Fallback to stock or reject trade**

---

### Quick Reference Summary

| Factor | Chart-Based (PRIMARY) | Risk-Budget-First (SECONDARY) |
|--------|----------------------|-------------------------------|
| **When to use** | Strong technical setup | Weak/no chart stop |
| **Stop source** | Chart structure | Capital limits |
| **Advantage** | Market-connected | Maximum protection |
| **Disadvantage** | May exceed risk budget | May be too tight |
| **Risk budget role** | Position size gate | Stop calculation input |
| **Common outcome** | Need override in CORRECTION | Tight/arbitrary stops |
