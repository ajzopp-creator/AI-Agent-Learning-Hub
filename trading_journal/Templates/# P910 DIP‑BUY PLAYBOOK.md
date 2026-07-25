
# P910 DIP‑BUY PLAYBOOK

## 1. Core Thesis
P910 is a controlled dip‑buy engine designed to capture mean‑reversion setups in structurally stable names after volatility compression, earnings resets, or liquidity shocks.

It is not a breakout system.  
It is not a momentum system.  
It is not a high‑tier technical pattern system.

P910 exists to exploit temporary dislocations in fundamentally intact assets.

---

## 2. Eligibility Filters

### A. Structural Fundamentals
A stock qualifies if:
- No distress signals  
- No deterioration in business model  
- No liquidity crisis  
- No accounting red flags  
- No sector‑specific structural collapse  

#### REIT Structural Override
Mortgage REIT leverage is structural, not distress.  
Do **not** penalize leverage unless:
- Book value deterioration  
- Spread compression  
- Dividend instability  
- Repo funding stress  

---

### B. Post‑Earnings Window
Preferred window: **2–7 sessions after earnings**  
Characteristics:
- Volatility compression  
- Mean‑reversion behavior  
- No guidance shock  
- No liquidity vacuum  

---

### C. Technical Conditions
Minimum requirements:
- CandleTier ≥ 2  
- AnalysisTier ≥ 2  
- RS vs SPY ≥ 3  
- LiquidityTier = Y or N  
- No breakdown below multi‑week support  

Not required:
- BreakoutVerdict  
- PatternType  
- VolumeMultiple  
- SetupScore  

---

## 3. Entry Logic

### A. Trigger Conditions
BUY emitted when:
- Price dips into controlled zone  
- Volatility compresses  
- Fundamentals intact  
- Candle structure stabilizes  
- Market context not contradictory  

### B. Execution
- Enter on stabilization candle  
- Avoid chasing  
- Avoid liquidity vacuums  
- Avoid macro shock days  

---

## 4. Risk Management

### A. Stop Placement
StopLevel placed:
- Below local swing low  
- Below volatility compression floor  
- Below structural support  

### B. Target Placement
TPLevel placed at:
- Mean‑reversion target  
- Prior liquidity shelf  
- Volatility expansion zone  

### C. RiskPct Auto‑Calculation


\[
\text{RiskPct} = \frac{\text{Entry} - \text{Stop}}{\text{AccountBalance}}
\]



Must be computed before sending to P400.

---

## 5. Disqualifiers
Reject trade if:
- Structural fundamentals deteriorate  
- Earnings shock persists  
- Liquidity collapses  
- RS vs SPY < 3  
- CandleTier < 2  
- AnalysisTier < 2  
- Macro context hostile  

---

## 6. Automation Rules

### A. REIT Override Module
If sector = REIT and leverage = structural → do not downgrade FundamentalsTier.

### B. Post‑Earnings Module
If earnings within 2–7 sessions → increase dip‑buy confidence.

### C. P910 Tagging
All P910 trades must be tagged:

`DIP_BUY_P910`

### D. RiskPct Auto‑Fill
Compute and attach RiskPct before sending to P400.

---

## 7. P400 Review Pipeline Requirements
P910 trades forwarded to P400 must include:
- EntryPrice  
- StopLevel  
- TPLevel  
- RiskPct  
- FundamentalsTier (with REIT override applied)  
- CandleTier  
- AnalysisTier  
- RS vs SPY  
- LiquidityTier  
- SimulationNotes  

---

## 8. Example — AGNC (7/24/2026)
AGNC passed because:
- REIT leverage = structural  
- Earnings 4 sessions past  
- Dip‑buy volatility compression  
- CandleTier 2  
- AnalysisTier 2  
- RS 4  
- Liquidity adequate  
- No breakout metrics required  

This is a textbook P910 dip‑buy.

---

## 9. Related Modules
- P115 — Dip‑Buy Signal Engine  
- P400 — Trade Review Pipeline  
- P300 — Market Context Engine  
- P_910 — Dip‑Buy Execution Module  

---
