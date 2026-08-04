This document explains every key VantagePoint indicator used in our **Bullish Trend Pattern**.  
Think of these as the “ingredients” in our recipe for high-probability bullish setups.

---

## Core Predictive Indicators

### 1. Predictive Differences (Short, Medium, Long Term)
- **Short_Term_Difference**: Predicts **tomorrow’s** price direction (1 day ahead).  
- **Medium_Term_Difference**: Predicts the next **2 days**.  
- **Long_Term_Difference**: Predicts the next **3 days**.  

**Bullish Rule**:  
- Short_Term must cross from negative to **positive** (crossover).  
- Medium or Long Term should be **≥ 1.5** (strong momentum).  
- Best: All three positive and stacked (Triple Cross).

### 2. Triple Cross
- Compares the three predictive lines (Short > Medium > Long).  
- **Bullish**: All three aligned upward → strongest trend confirmation.  
- Gives a **+0.10 DL bonus** when aligned.

---

## Larry Williams Indicators

### 3. Williams EMAI (Electronic Market Accumulation Index)
- Tracks **institutional (“smart money”) buying and selling**.  
- **Rising EMAI** = Institutions are quietly **accumulating** shares → **Very Bullish**.  
- We require an **upward slope** over the last 5–10 days → **+0.30 DL bonus** (one of our strongest edges).

### 4. Professional Sentiment Index (PSI) + PSI ROC
- Measures how bullish **professional traders** are (0–100%).  
- **PSI ROC** = how fast sentiment is changing.  
- **Inverse Signal** (key V2.5 edge): EMAI rising **while** PSI is flat or falling → Smart money buying while crowd is cautious → **+0.15–0.20 DL bonus**.

---

## Neural & Strength Indicators

### 5. Neural Index (NeuralX and NeuralXMax)
- AI-powered prediction: Will price go **up** or **down** in the next 1–2 days?  
- **Green / “up”** = Bullish.  
- **NeuralXMax** = Strength of the signal (0–100). Higher = more confident.  

**Our Rule**:  
- “up” on **at least 2 of the prior 3 days** + NIMAX ≥ 35–40.

### 6. Volume
- Number of shares traded each day.  
- **Bullish Confirmation**: Volume on up days > **30% above** 20-day average → real buying pressure → **+0.25 DL bonus**.

---

## Price Context

### 7. Price vs 50-day SMA
- **50-day Simple Moving Average** = average closing price of last 50 trading days.  
- **Required**: Current Close must be **above** the 50-day SMA (stock is in overall uptrend).

---

## Final Score: DL Score (Decision Layer)

- A single number from **0.0 to 1.0** that combines **all** the above with weighted bonuses.  
- **Pattern-Match Threshold**: **DL ≥ 0.74** = Strong candidate (even in Risk OFF mode for visibility).  

**Signal Levels**:
- ≥ 0.90 → **Strong Buy**
- 0.75–0.89 → **Buy**
- 0.60–0.74 → **Hold/Watch**
- < 0.60 → **Pass/Reject**

---

## Quick Visual Checklist for a Perfect Pattern

- [ ] Short_Term just crossed positive  
- [ ] Medium/Long Term ≥ 1.5 (or strong override)  
- [ ] Williams EMAI rising (last 5–10 days)  
- [ ] Neural Index “up” 2-of-3 days + good NIMAX  
- [ ] Volume surge on strength days  
- [ ] Price above 50-day SMA  
- [ ] Triple Cross aligned (bonus)  
- [ ] Inverse PSI/EMAI present (bonus)  

**DL Score ≥ 0.74 = Pattern Match!**

---

**Related Files**:
- `p301_pattern_matcher.py` – Python program that scores any grid using these rules
- `P_301_TREND_FILTER.py` – Additional trend validation layer
- Project Instructions (V2.5) – Full execution rules

**Tip**: Print this file and keep it next to your trading screen!

---
*Built for Bullish Trend Pattern Project V2.5 – Tony Zoppi*

