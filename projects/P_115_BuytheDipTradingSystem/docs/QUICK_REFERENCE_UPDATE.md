# Quick_Reference_V110_200MA_PENALTY.md - REPLACE OPTIONS SECTION

## Find the existing "OPTIONS POSITION SIZING" section and REPLACE with this:

---

### OPTIONS POSITION SIZING - HYBRID SYSTEM

**PRIMARY: Chart-Based Method** (use for strong technical setups)
1. Stock stop from chart (support/resistance/ATR)
2. Option stop = Entry + (Delta × Stock Risk)
3. Risk = (Entry - Stop) × 100
4. Position = Risk Budget ÷ Risk per Contract
5. If < 1 contract → Override or fallback

**SECONDARY: Risk-Budget-First** (use for weak technicals)
1. Max Loss = Risk Budget ÷ 100
2. Stop = Entry - Max Loss
3. Validate vs. 2-ATR: (ATR × 2 × Delta)
4. Use tighter stop
5. Position = 1 contract if within budget

**Method Selection:**
- Strong chart setup → Chart-Based ✅
- Weak/no chart stop → Risk-Budget-First
- Override available for both

**Liquidity Gates (must pass ALL):**
- Spread ≤ 10% of mid
- OI ≥ 150
- Option R:R ≥ Stock R:R

**Three-Gate Position Sizing:**
Smallest of: Risk-based / Cash / 5% max concentration

**Override Documentation:**
```
Method: [Chart-Based/Risk-Budget-First]
Risk: $XXX (exceeds budget $YYY by $ZZZ/PP%)
Justification: [specific reason]
```

---
