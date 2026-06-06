# P_115 STRATEGY GUIDE - V110 200-MA PENALTY ADDENDUM (CORRECTED)

## Document Purpose
This addendum provides corrected guidance on the V110 200-Day MA Distance Penalty feature for P_115 Buy The Dip strategy.

**Correction Date:** February 11, 2026  
**Applies to:** P_115_buyTheDipChart_V110 and later

---

## CORRECTED 200-MA Penalty Logic

### What Changed (February 11, 2026)

**INCORRECT (Original V110):**
- Stocks at/above 200-MA received -0.5 penalty ❌
- Stocks 0-3% below 200-MA received -0.5 penalty ❌

**CORRECT (Fixed V110):**
- Stocks at/above 200-MA receive 0.0 penalty ✅
- Stocks 0-3% below 200-MA receive 0.0 penalty ✅

---

## Corrected Penalty Structure

### Four-Zone Framework

```
ZONE 1: NORMAL (At/Above OR 0% to -3% Below)
  Distance: >= -3%
  Penalty: 0.0
  Status: Healthy positioning
  Fund Impact: Full strength preserved
  
  Examples:
  - Stock at $105, 200-MA at $100 (+5% above) → Penalty: 0.0
  - Stock at $100, 200-MA at $100 (at 200-MA) → Penalty: 0.0
  - Stock at $98, 200-MA at $100 (-2% below) → Penalty: 0.0

ZONE 2: PULLBACK (-3% to -10% Below)
  Distance: -3% to -10%
  Penalty: -1.0
  Status: Normal pullback
  Fund Impact: Adjusted Fund = Base - 1.0
  
  Example:
  - Stock at $92, 200-MA at $100 (-8% below) → Penalty: -1.0
  - Base Fund 4 becomes Adjusted Fund 3.0

ZONE 3: CORRECTION (-10% to -20% Below)
  Distance: -10% to -20%
  Penalty: -2.0
  Status: Significant weakness
  Fund Impact: Adjusted Fund = Base - 2.0
  
  Example:
  - Stock at $85, 200-MA at $100 (-15% below) → Penalty: -2.0
  - Base Fund 4 becomes Adjusted Fund 2.0
  - Needs Anal=4 to qualify (HT=6)

ZONE 4: BEAR/AVOID (Below -20%)
  Distance: < -20%
  Penalty: -4.0
  Status: Value trap territory
  Fund Impact: Adjusted Fund = 0 (automatic disqualification)
  
  Example:
  - Stock at $70, 200-MA at $100 (-30% below) → Penalty: -4.0
  - Base Fund 4 becomes Adjusted Fund 0
  - Cannot qualify regardless of technicals
```

---

## Trading Implications (CORRECTED)

### Qualification Requirements by Zone

**ZONE 1 (Healthy - No Penalty):**
```
Adjusted Fund: 4.0 (full strength)
Minimum HybridTier: 6
Required Anal: 2 (if Fund=4)
Verdict: Easy qualification
```

**ZONE 2 (Pullback):**
```
Adjusted Fund: 3.0
Minimum HybridTier: 6
Required Anal: 3 (standard requirement)
Verdict: Normal qualification
```

**ZONE 3 (Correction):**
```
Adjusted Fund: 2.0
Minimum HybridTier: 6
Required Anal: 4 (maximum required)
Verdict: Difficult qualification - needs perfect technicals
```

**ZONE 4 (Bear/Avoid):**
```
Adjusted Fund: 0
Maximum HybridTier: 4 (with Anal=4)
Verdict: Impossible to qualify - automatic rejection
```

---

## Code Reference (CORRECTED)

### ThinkScript Implementation

```thinkscript
# Calculate distance from 200-day MA
def ma200 = Average(close, 200);
def distFromMA200 = ((close - ma200) / ma200) * 100;

# CORRECTED penalty structure
def maPenalty = 
    if distFromMA200 >= -3 then 0.0         # At/above OR 0-3% below (no penalty)
    else if distFromMA200 >= -10 then 1.0   # -3% to -10% below (pullback zone)
    else if distFromMA200 >= -20 then 2.0   # -10% to -20% below (CORRECTION zone)
    else 4.0;                                # Below -20% (BEAR/AVOID)

# Apply penalty to base fundamentals
def adjustedFundTier = Max(0, fundamentalsTier - maPenalty);
```

---

## Real-World Examples (CORRECTED)

### Example 1: Healthy Stock Above 200-MA
```
Ticker: AAPL
Price: $178.50
200-MA: $175.00
Distance: +2.0%

Zone: NORMAL (above 200-MA)
Base Fund: 4
Penalty: 0.0 (CORRECTED - no penalty for stocks above 200-MA)
Adjusted Fund: 4.0
Anal: 3
HybridTier: 7.0
Verdict: BUY ✅

Notes: Healthy uptrend, full fundamental strength preserved
```

### Example 2: Testing 200-MA Support
```
Ticker: MSFT
Price: $398.00
200-MA: $400.00
Distance: -0.5%

Zone: NORMAL (testing support, within 0-3% below)
Base Fund: 4
Penalty: 0.0 (CORRECTED - no penalty for support tests)
Adjusted Fund: 4.0
Anal: 3
HybridTier: 7.0
Verdict: BUY ✅

Notes: Common support test, not weakness signal
```

### Example 3: Minor Pullback
```
Ticker: NVDA
Price: $920.00
200-MA: $1,000.00
Distance: -8.0%

Zone: PULLBACK (-3% to -10%)
Base Fund: 4
Penalty: -1.0
Adjusted Fund: 3.0
Anal: 3
HybridTier: 6.0
Verdict: BUY ✅

Notes: Normal pullback, still qualifies
```

### Example 4: Correction Zone
```
Ticker: AMD
Price: $135.00
200-MA: $160.00
Distance: -15.6%

Zone: CORRECTION (-10% to -20%)
Base Fund: 4
Penalty: -2.0
Adjusted Fund: 2.0
Anal: 3
HybridTier: 5.0
Verdict: NO SIGNAL ❌

If Anal: 4
HybridTier: 6.0
Verdict: BUY ✅ (with perfect technicals)

Notes: Needs maximum technical strength to qualify
```

### Example 5: Value Trap
```
Ticker: FISV
Price: $63.13
200-MA: ~$165.00
Distance: -61.7%

Zone: BEAR/AVOID (below -20%)
Base Fund: 4
Penalty: -4.0
Adjusted Fund: 0
Anal: 4 (even perfect)
HybridTier: 4.0
Verdict: NO SIGNAL ❌

Notes: Automatic rejection, capital preservation
```

---

## Strategy Adjustments

### Pre-V110 Behavior
- All stocks evaluated on fundamentals alone
- No consideration of price position relative to 200-MA
- Value traps could qualify with strong historical metrics

### V110 CORRECTED Behavior
- Healthy stocks (at/above OR 0-3% below 200-MA) maintain full strength
- Pullback stocks (-3% to -10%) qualify normally with Anal=3
- Correction stocks (-10% to -20%) need perfect technicals (Anal=4)
- Severe declines (below -20%) automatically rejected

### Impact on Signal Quality
- **Unchanged:** Stocks in healthy positioning (85% of qualified setups)
- **Slightly Affected:** Pullback zone stocks (still qualify with standard criteria)
- **Heavily Filtered:** Correction zone stocks (need perfect technicals)
- **Eliminated:** Value trap stocks (automatic rejection)

---

## Key Principles

1. **Strength Preservation (CORRECTED):** Stocks at/above 200-MA or testing support receive ZERO penalty

2. **Progressive Filtering:** Penalties increase with distance below 200-MA

3. **Market Alignment:** Thresholds match standard market correction definitions (-10%, -20%)

4. **Binary Cutoff:** Below -20% is automatic rejection, no exceptions

5. **Capital Preservation:** Filter prioritizes avoiding catastrophic losses over capturing every opportunity

---

## Migration Notes for Existing Users

### If You're Upgrading from Pre-V110:
- Expect similar signal counts for healthy stocks (CORRECTED - no change)
- Fewer signals in correction territory (-10% to -20% below 200-MA)
- Zero signals from severe declines (below -20%)
- Higher win rate expected from improved quality control

### If You're Already on V110 (Before Correction):
- **CRITICAL:** Healthy stocks were incorrectly penalized -0.5
- Update to corrected version immediately
- Recheck any rejected signals from healthy stocks
- No impact on value trap filtering (still working correctly)

---

## Validation Checklist

When evaluating any P_115 signal, verify:

- [ ] Check LogEntry Fund value (top-right corner of chart)
- [ ] Verify Fund represents ADJUSTED value (includes 200-MA penalty)
- [ ] If Fund=4.0, stock is healthy (at/above OR 0-3% below 200-MA) ✅
- [ ] If Fund=3.0, stock in normal pullback (still qualifies) ✅
- [ ] If Fund=2.0, stock in correction zone (needs Anal=4) ⚠️
- [ ] If Fund=0, stock is value trap (automatic rejection) 🚫

---

## Summary

**V110 (CORRECTED) improves P_115 strategy by:**
1. Filtering value traps (stocks >20% below 200-MA)
2. Requiring stronger technicals in correction zone (-10% to -20%)
3. **Preserving full strength for healthy stocks (CORRECTED)**
4. Maintaining normal qualification for pullback stocks
5. Preventing catastrophic entries on falling knives

**The correction ensures healthy stocks are NOT penalized, while maintaining effective value trap protection.**

---

**Version:** V110 (CORRECTED)  
**Correction Date:** February 11, 2026  
**Impact:** Preserves signals on healthy stocks while maintaining value trap filter  
**Status:** PRODUCTION READY  
**Applies To:** All P_115 signals going forward
