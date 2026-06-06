# Tracker_Log_Schema_v9_4_0.md - UPDATE SimulationNotes Field

## Find the "SimulationNotes" field description and ADD this section:

---

### SimulationNotes Field - Options Trades

**Required Elements:**
1. Contract count and symbol
2. Entry premium (actual or target)
3. Stop premium with METHOD notation
4. Target premium (delta-adjusted)
5. Actual risk in dollars
6. Method used (Chart-Based or Risk-Budget-First)
7. Override details (if applicable)

**Format - Chart-Based Method:**
```
[N] contract [SYMBOL], Entry: $X.XX, Stop: $Y.YY (chart-based at $[stock stop]), 
Target: $Z.ZZ, Risk: $RRR, Method: Chart-Based
```

**Format - Risk-Budget-First Method:**
```
[N] contract [SYMBOL], Entry: $X.XX, Stop: $Y.YY (risk-budget/2-ATR), 
Target: $Z.ZZ, Risk: $RRR, Method: Risk-Budget-First
```

**Format - Override Required:**
```
[N] contract [SYMBOL], Entry: $X.XX, Stop: $Y.YY (chart-based at $[stock stop]), 
Target: $Z.ZZ, Risk: $RRR (exceeds [MODE] budget $BBB by $OOO/PP%, 
approved for [specific reason]), Method: Chart-Based + Override
```

**Examples:**

Normal execution:
```
1 contract XYZ260221C50, Entry: $3.20, Stop: $2.50 (chart-based at $65 stock), 
Target: $8.30, Risk: $70, Method: Chart-Based
```

Override execution:
```
1 contract MCHP260320C80, Entry: $5.40, Stop: $0.83 (chart-based at $74 stock), 
Target: $19.12, Risk: $457 (exceeds CORRECTION budget $262.50 by $194/74%, 
approved for Eddie Z High Handle breakout with volume confirmation), 
Method: Chart-Based + Override
```

Conservative execution:
```
2 contracts ABC260307C45, Entry: $2.80, Stop: $1.90 (2-ATR floor), 
Target: $6.50, Risk: $180, Method: Risk-Budget-First
```

---
