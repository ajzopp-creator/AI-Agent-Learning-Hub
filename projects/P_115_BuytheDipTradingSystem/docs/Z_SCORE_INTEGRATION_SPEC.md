# Z-Score Regime Council Integration Specification
**Technical Implementation Guide**

**Version:** 1.0  
**Date:** February 10, 2026  
**Status:** PLANNED (Implementation: September 2026)  
**Related Docs:** FEATURES_ROADMAP_2026.md, SESSION_INITIALIZATION_PROMPT.md, Tracker_Log_Schema.md

---

## Table of Contents
1. [Overview](#overview)
2. [Indicator Technical Details](#indicator-technical-details)
3. [Column Schema Extensions](#column-schema-extensions)
4. [Scoring Algorithms](#scoring-algorithms)
5. [Filter Thresholds](#filter-thresholds)
6. [Workflow Integration](#workflow-integration)
7. [Implementation Phases](#implementation-phases)
8. [Testing & Validation](#testing-validation)
9. [Risk Management](#risk-management)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What Is Z-Score Regime Council?

The Z-Score Regime Council is a ThinkorSwim indicator created by @justAnotherTrader on useThinkScript forum that normalizes seven market dimensions using statistical Z-scores, revealing institutional market psychology and regime transitions.

**Key Concept:** Instead of analyzing raw values (RSI=55, Volume=2.1M shares), Z-scores reveal "how unusual is this reading compared to recent behavior?" (RSI Z=+2.5 = 98th percentile, unusually overbought).

**Seven Components Measured:**
1. **VWAP Distance Z** - How far price is from institutional positioning
2. **Volume Z** - Participation strength (direction-adjusted: positive on up days, negative on down days)
3. **OBV Z** - On Balance Volume change (money flow momentum)
4. **CMF Z** - Chaikin Money Flow intensity (institutional accumulation/distribution)
5. **RSI Z** - Momentum oscillator extremes
6. **MACD Z** - Trend momentum shifts
7. **Percentage Gain Z** - Daily performance context

**Output:**
- **Stacked Histogram:** Visual representation of layered Z-scores (wave-like pattern)
- **sumZZ:** Z-score of Z-scores (meta-indicator, typically -3 to +3)
- **Regime Label:** Plain English classification (BREAKOUT CONFIRMED, STEALTH ACCUMULATION, RANGE BOUND, etc.)

**Does NOT Repaint:** Historical bars remain stable after close (confirmed by indicator author)

---

## Indicator Technical Details

### Installation

**Source:** https://usethinkscript.com/threads/regime-council.16789/

**Code Version:** v10 (as of May 25, 2025)

**ThinkorSwim Setup:**
1. Studies → Edit Studies → thinkScript Editor
2. Paste indicator code from forum post
3. Save as "RegimeCouncil_v10"
4. Apply to chart lower panel
5. Verify labels display on right side (VWAP_Z, VOL_Z, etc.)

**Default Parameters:**
- length = 14 (RSI/CMF lookback)
- zLength = 20 (Z-score normalization window)
- macdFastLen = 12
- macdSlowLen = 26
- macdSigLen = 9
- emaLength = 9 (sumZZ smoothing)
- TripleSmoothing = yes (wave effect)
- SmoothingFactor = 3

**DO NOT MODIFY PARAMETERS** - Use defaults for consistency across all analysis

### Reading the Indicator

**Visual Elements:**

1. **Stacked Histogram (Lower Panel):**
   - Color-coded layers showing each Z-component
   - Height = strength of composite signal
   - Direction = bullish (positive) vs bearish (negative)
   - Wave pattern = sustainable trend vs unsustainable spike

2. **Labels (Right Side):**
   ```
   VWAP_Z: 2.00
   VOL_Z: -2.09
   OBV_Z: 0.36
   CMF_Z: 0.26
   RSI_Z: 0.26
   MACD_Z: -0.31
   PCT_GAIN_Z: 0.38
   sumZZ: 0.12
   ```

3. **Regime Label (Top Right):**
   ```
   RANGE BOUND
   Wait for Setup
   MODERATE
   NORMAL VOL
   ```

### Interpretation Guide

**Z-Score Ranges:**
- **Z > +2.0** → Extreme (97.5th percentile) - Very unusual strength
- **Z = +1.0 to +2.0** → Strong (84th-97th percentile) - Above average
- **Z = -1.0 to +1.0** → Normal range (16th-84th percentile)
- **Z = -1.0 to -2.0** → Weak (3rd-16th percentile) - Below average
- **Z < -2.0** → Extreme (2.5th percentile) - Very unusual weakness

**Positive vs Negative by Component:**
- **VWAP_Z**: +ve = Above VWAP (bullish positioning), -ve = Below VWAP
- **VOL_Z**: +ve = High volume on up day, -ve = High volume on down day
- **OBV_Z**: +ve = Buying pressure increasing, -ve = Selling pressure increasing
- **CMF_Z**: +ve = Money flowing IN, -ve = Money flowing OUT
- **RSI_Z**: +ve = Momentum strengthening, -ve = Momentum weakening
- **MACD_Z**: +ve = Trend accelerating, -ve = Trend decelerating
- **PCT_GAIN_Z**: +ve = Strong daily gain, -ve = Strong daily loss

**sumZZ (Composite):**
- **sumZZ > +2.0** → All forces aligned bullish (BREAKOUT CONFIRMED, UPTREND)
- **sumZZ = +1.0 to +2.0** → Moderate bullish (early UPTREND)
- **sumZZ = -1.0 to +1.0** → Neutral (RANGE BOUND, mixed signals)
- **sumZZ = -1.0 to -2.0** → Moderate bearish (early DOWNTREND)
- **sumZZ < -2.0** → All forces aligned bearish (BREAKDOWN CONFIRMED, DOWNTREND)

### Key Regime Classifications

**Bullish Regimes (Target for P_115 entries):**
- **BREAKOUT CONFIRMED:** sumZZ > +2.0, CMF > 1.0, OBV > 1.0, VOL > 1.0, PCT_GAIN > 1.0
- **UPTREND:** sumZZ > +1.0 but not extreme
- **MOMENTUM CLIMAX:** RSI_Z > 2.0, MACD_Z > 1.5, VOL > 1.0, PCT_GAIN > 1.0 (caution: blowoff risk)

**Mixed/Divergence Regimes (Requires caution):**
- **STEALTH ACCUMULATION:** OBV > 1.5, CMF > 1.0, but VOL < 0.5 and PCT_GAIN < 0.5 (smart money building)
- **BEAR TRAP:** VOL > 1.0, OBV > 1.0, CMF > 1.0, but PCT_GAIN < 0 (false weakness)
- **BULL TRAP:** VOL > 1.0, PCT_GAIN > 0, but OBV < -1.0 and CMF < -1.0 (false strength)

**Bearish Regimes (AVOID for P_115):**
- **RANGE BOUND:** sumZZ near 0, mixed signals (wait for clarity)
- **DOWNTREND:** sumZZ < -1.0
- **BREAKDOWN CONFIRMED:** sumZZ < -2.0, CMF < -1.0, OBV < -1.0
- **CAPITULATION:** sumZZ < -2.5, extreme negative (reversal watch, but high risk)

---

## Column Schema Extensions

### New Columns (28-35)

Extends existing 27-column Tracker_Log_Schema to 35 columns.

| Column # | Field Name | Data Type | Example | Source | Required |
|----------|------------|-----------|---------|--------|----------|
| **28** | **Z_sumZZ** | Decimal (2 places) | 2.35 | Indicator label | Yes |
| **29** | **Z_Regime** | Text | BREAKOUT CONFIRMED | Indicator label | Yes |
| **30** | **Z_CMF** | Decimal (2 places) | 1.20 | Indicator label | Yes |
| **31** | **Z_OBV** | Decimal (2 places) | 0.85 | Indicator label | Yes |
| **32** | **Z_VOL** | Decimal (2 places) | 1.50 | Indicator label | Yes |
| **33** | **Z_RSI** | Decimal (2 places) | 0.50 | Indicator label | Yes |
| **34** | **Z_PositiveCount** | Integer (0-7) | 5 | Manual count | Yes |
| **35** | **Z_QualityScore** | Integer (0-12) | 8 | Calculated | Yes |

### Column Definitions

**Z_sumZZ (Column 28):**
- The Z-score of the Z-scores (meta-indicator)
- Typically ranges from -3 to +3
- Shows whether the composite signal is extreme vs normal
- **Critical for filter:** PRIMARY decision criterion

**Z_Regime (Column 29):**
- Plain English classification from indicator
- Possible values: BREAKOUT CONFIRMED, UPTREND, MOMENTUM CLIMAX, RANGE BOUND, DOWNTREND, BREAKDOWN CONFIRMED, STEALTH ACCUMULATION, BEAR TRAP, BULL TRAP, PARABOLIC MOVE, CAPITULATION, RETAIL FOMO, etc.
- **Use:** Context and confidence level

**Z_CMF (Column 30):**
- Chaikin Money Flow Z-score
- Positive = money flowing IN (institutional buying)
- Negative = money flowing OUT (institutional selling)
- **Critical for filter:** Must be positive for BUY signals

**Z_OBV (Column 31):**
- On Balance Volume change Z-score
- Positive = buying pressure accumulating
- Negative = selling pressure accumulating
- **Critical for filter:** Must be positive for BUY signals

**Z_VOL (Column 32):**
- Volume Z-score (direction-adjusted)
- Positive = high volume on up day (bullish participation)
- Negative = high volume on down day (bearish distribution)
- **Use:** Confirmation, not primary filter (but extreme negative is red flag)

**Z_RSI (Column 33):**
- RSI Z-score (momentum oscillator)
- Positive = momentum strengthening
- Negative = momentum weakening
- **Use:** Supplemental, not primary

**Z_PositiveCount (Column 34):**
- Manual count of how many of the 7 Z-scores are positive
- Range: 0 to 7
- **Critical for filter:** Need ≥4 positive for BUY consideration
- **Calculation:** Count VWAP_Z, VOL_Z, OBV_Z, CMF_Z, RSI_Z, MACD_Z, PCT_GAIN_Z where value > 0

**Z_QualityScore (Column 35):**
- Composite quality score (0-12 points)
- **Calculation:** See Scoring Algorithms section below
- **Use:** Bonus points added to P_115 traditional score for conviction tiers

### Data Capture Workflow

**When processing any P_115 candidate:**

1. Load ticker in ThinkorSwim with RegimeCouncil_v10 indicator
2. Read labels from right side of chart (current bar)
3. Manually transcribe to Excel columns 28-35:
   - Columns 28-33: Direct copy from labels (2 decimal places)
   - Column 34: Count positive values (0-7)
   - Column 35: Calculate using formula (see next section)

**Time Required:** ~30 seconds per ticker

**Quality Check:**
- Verify sumZZ matches visual histogram direction (positive = green wave, negative = red wave)
- Verify Regime label matches sumZZ magnitude (e.g., sumZZ > 2.0 should show bullish regime)
- Verify PositiveCount by hand-counting labels

---

## Scoring Algorithms

### Z_QualityScore Calculation (Column 35)

**Formula:** Sum of component scores (max 12 points)

**Component 1: Z_sumZZ Score (0-3 points)**
```
IF Z_sumZZ >= 2.5 THEN 3 points
ELSE IF Z_sumZZ >= 2.0 AND < 2.5 THEN 2 points
ELSE IF Z_sumZZ >= 1.5 AND < 2.0 THEN 1 point
ELSE 0 points
```

**Component 2: Z_CMF Score (0-2 points)**
```
IF Z_CMF > 1.0 THEN 2 points
ELSE IF Z_CMF >= 0 AND <= 1.0 THEN 1 point
ELSE 0 points
```

**Component 3: Z_OBV Score (0-2 points)**
```
IF Z_OBV > 1.0 THEN 2 points
ELSE IF Z_OBV >= 0 AND <= 1.0 THEN 1 point
ELSE 0 points
```

**Component 4: Z_VOL Score (0-2 points)**
```
IF Z_VOL > 2.0 THEN 2 points
ELSE IF Z_VOL >= 1.0 AND <= 2.0 THEN 1 point
ELSE 0 points
```

**Component 5: Z_RSI Score (0-1 point)**
```
IF Z_RSI > 0 THEN 1 point
ELSE 0 points
```

**Component 6: Z_PositiveCount Score (0-2 points)**
```
IF Z_PositiveCount >= 6 THEN 2 points
ELSE IF Z_PositiveCount >= 4 AND < 6 THEN 1 point
ELSE 0 points
```

**Total Z_QualityScore:**
```
Z_QualityScore = Component1 + Component2 + Component3 + Component4 + Component5 + Component6
Minimum: 0 points
Maximum: 12 points
```

### Combined Conviction Score

**Formula:**
```
Total Score = P_115_TraditionalScore + Z_QualityScore
Maximum Possible: 112 points (assuming P_115 max = 100)
```

**Conviction Tiers:**
```
HIGH CONVICTION (≥85 total):
  - P_115 Traditional ≥75 AND Z_QualityScore ≥10
  - Position Sizing: Standard risk (1.5% or posture-adjusted)
  - Confidence Level: Maximum

STANDARD ENTRY (≥70 total):
  - P_115 Traditional ≥60 AND Z_QualityScore ≥8
  - OR P_115 Traditional ≥70 AND Z_QualityScore ≥5
  - Position Sizing: Standard risk (1.5%)
  - Confidence Level: Normal

WATCH LIST ONLY (<70 total):
  - Either P_115 or Z_QualityScore weak
  - Position Sizing: Paper trade only or reduced (1.0%)
  - Confidence Level: Low
```

**Example Calculation:**

Ticker: XYZ
- P_115 Traditional: 78 points
- Z_sumZZ: 2.3 → 2 points
- Z_CMF: 1.2 → 2 points
- Z_OBV: 0.8 → 1 point
- Z_VOL: 1.5 → 1 point
- Z_RSI: 0.5 → 1 point
- Z_PositiveCount: 5 → 1 point
- **Z_QualityScore: 8 points**

**Total: 78 + 8 = 86 → HIGH CONVICTION**

---

## Filter Thresholds

### Stage 1: Pre-Screen Filter (30-Second Decision)

**Purpose:** Eliminate weak candidates BEFORE investing time in full P_115 analysis

**GREEN LIGHT (Proceed to Full P_115) ✅**

Must meet ALL of the following:
- sumZZ ≥ 2.0
- Regime = BREAKOUT CONFIRMED, UPTREND, or MOMENTUM CLIMAX
- CMF_Z > 0 (money flowing IN)
- OBV_Z > 0 (buying pressure)
- Z_PositiveCount ≥ 4 (majority positive)

**Action:** Proceed immediately to full 27-column P_115 analysis

**YELLOW LIGHT (Higher Quality Bar Required) ⚠️**

Conditional pass if:
- sumZZ between 1.0 and 1.99 (moderate strength)
- Regime = MODERATE, early UPTREND, or STEALTH ACCUMULATION
- Z_PositiveCount ≥ 5 (stronger consensus required)

**Action:** Proceed to P_115 but expect lower conviction (may be WATCH LIST)

**RED LIGHT (Skip Immediately) ❌**

Any of the following disqualifies:
- sumZZ < 1.0 (weak or bearish composite)
- Regime = RANGE BOUND, DOWNTREND, BREAKDOWN CONFIRMED, or any bearish label
- CMF_Z < 0 (money flowing OUT)
- OBV_Z < 0 (selling pressure)
- Z_PositiveCount < 4 (majority negative/neutral)

**Action:** Skip ticker entirely, move to next candidate

**Special Cases:**

**BULL TRAP Detection:**
- Regime label = BULL TRAP
- VOL_Z > 1.0, PCT_GAIN_Z > 0 BUT CMF_Z < 0 and OBV_Z < 0
- **Action:** RED LIGHT (price up but money flowing out = fake strength)

**STEALTH ACCUMULATION Exception:**
- Regime label = STEALTH ACCUMULATION
- OBV_Z > 1.5, CMF_Z > 1.0 BUT PCT_GAIN_Z < 0.5 (price not moving much yet)
- **Action:** YELLOW LIGHT (smart money building position quietly)

### Stage 2: Quality Scoring (During P_115 Analysis)

After passing Stage 1 filter, calculate Z_QualityScore (0-12) and add to P_115 score.

**Minimum Acceptable Z_QualityScore by Conviction Tier:**
- HIGH CONVICTION: Z_QualityScore ≥ 10
- STANDARD ENTRY: Z_QualityScore ≥ 8
- WATCH LIST: Z_QualityScore < 8

### Threshold Calibration

**Initial Thresholds (September 2026):**
- Use values documented above
- Track outcomes for 10+ trades

**Adjustment Triggers:**
- If GREEN LIGHT filter passes too many losers (>40%): Raise sumZZ threshold from 2.0 to 2.5
- If GREEN LIGHT filter is too restrictive (<5 candidates/week): Lower sumZZ threshold from 2.0 to 1.75
- If Z_QualityScore shows no correlation with outcomes: Simplify to binary (PASS/FAIL based on filter only)

**Review Schedule:**
- Weekly during Phase 2 (September 16-30)
- Monthly during Phase 3 (October-December)
- Quarterly after full integration (2027+)

---

## Workflow Integration

### Pre-Filter Workflow (Phase 2 Implementation)

**Old Workflow (Current):**
```
1. P_910 scan identifies candidate (or Eddie Z pick, or Chaikin signal)
2. Load in ThinkorSwim
3. Run full P_115 analysis (5 minutes)
4. Calculate HybridTier, AsymmetricSetup, verdict
5. Record in 27-column tracker
6. Move to next candidate
```

**New Workflow (With Z-Score Filter):**
```
1. P_910 scan identifies candidate
2. Load in ThinkorSwim WITH RegimeCouncil indicator
3. **Z-SCORE PRE-SCREEN (30 seconds):**
   a. Read sumZZ from label
   b. Read Regime label
   c. Check CMF_Z and OBV_Z positive
   d. Count positive Z-scores
   e. Make GO/NO-GO decision
4. IF RED LIGHT → Skip, move to next candidate (SAVE 5 MINUTES)
5. IF GREEN/YELLOW → Proceed to full P_115 analysis
6. Record in 35-column tracker (columns 1-27 unchanged, add 28-35)
7. Calculate combined conviction score
8. Move to next candidate
```

**Time Savings Estimate:**

Scenario: 10 candidates per day
- Without filter: 10 × 5 min = 50 minutes
- With filter (60% rejection rate): 4 skipped (4 × 0.5 min = 2 min) + 6 analyzed (6 × 5.5 min = 33 min) = 35 minutes
- **Savings: 15 minutes per day = 75 minutes per week**

### Integration with Existing Strategies

**P_115 (Buy The Dip):**
- Z-Score acts as INITIAL FILTER before P_115 diagnostics
- All 27-column methodology unchanged
- Z-Score columns 28-35 added for bonus scoring
- HybridTier calculation unchanged (Fund + Anal)
- Combined score = HybridTier-based score + Z_QualityScore

**P_118 (Eddie Z Breakouts):**
- Z-Score validates institutional backing for Eddie pattern
- GREEN LIGHT + Cup & Handle = highest conviction
- RED LIGHT + Eddie pick = consider passing (or reduce size)
- BULL TRAP regime = avoid even if pattern looks good
- Track: Does Z-Score filter improve Eddie Z win rate?

**P_117 (Ad-Hoc Signals):**
- Z-Score validates external recommendations (Chaikin, emails)
- Chaikin + GREEN LIGHT = convergence (strong signal)
- Chaikin + RED LIGHT = divergence (skeptical, deeper due diligence)
- Track: Does Z-Score reduce Chaikin false positives?

**P_116 (Options Income Launchpad):**
- Z-Score may not be primary filter (bounce patterns are different dynamics)
- Consider using for STEALTH ACCUMULATION detection (quiet base before bounce)
- Track separately: Does Z-Score apply to bounce strategies?

### Decision Trees

**P_115 Buy The Dip Decision Tree:**

```
Candidate Identified
    |
    v
Load TOS + RegimeCouncil
    |
    v
Read sumZZ, Regime, CMF_Z, OBV_Z, PositiveCount
    |
    +--- GREEN LIGHT? (sumZZ ≥ 2.0, bullish regime, CMF>0, OBV>0, ≥4 pos)
    |        |
    |        v
    |    Full P_115 Analysis → 35-column entry → Calculate Combined Score → Entry Decision
    |
    +--- YELLOW LIGHT? (sumZZ 1.0-1.99, conditional criteria)
    |        |
    |        v
    |    Full P_115 Analysis → Lower confidence tier → May be WATCH LIST
    |
    +--- RED LIGHT? (sumZZ < 1.0, bearish regime, CMF<0 or OBV<0, <4 pos)
             |
             v
         SKIP TICKER → Move to next candidate
```

**Eddie Z + Z-Score Convergence Decision Tree:**

```
Eddie Z Pick Received
    |
    v
Load TOS + RegimeCouncil
    |
    v
Read Z-Score metrics
    |
    +--- GREEN LIGHT + Pattern Confirmed?
    |        |
    |        v
    |    HIGH CONVICTION → Standard position size
    |
    +--- YELLOW LIGHT + Pattern Confirmed?
    |        |
    |        v
    |    STANDARD ENTRY → Normal position size
    |
    +--- RED LIGHT but Pattern Strong?
    |        |
    |        v
    |    CONDITIONAL → Reduce size 50% OR paper trade
    |
    +--- RED LIGHT + BULL TRAP regime?
             |
             v
         PASS → Institutional divergence, avoid
```

---

## Implementation Phases

### Phase 1: Pilot Test (September 1-15, 2026)

**Objective:** Validate data capture process and identify any issues before committing to methodology change

**Scope:** 5 trades only

**Method:** PARALLEL TRACKING
- Continue using current 27-column P_115 methodology (unchanged)
- Add Z-Score columns 28-35 alongside (do NOT use for decision-making yet)
- Compare: Would Z-Score filter have improved the decision?

**Workflow:**
1. Select 5 upcoming P_115 candidates
2. For each candidate:
   - Load chart with RegimeCouncil indicator
   - Record Z-Score data in columns 28-35
   - Continue with standard P_115 analysis (columns 1-27)
   - Make entry decision based ONLY on current methodology (ignore Z-Score)
   - Note in Comments: "Z-Score: [sumZZ], Regime: [label], Quality: [score]"
3. After trade closes:
   - Analyze: Did Z-Score correctly predict outcome?
   - Count: GREEN LIGHT winners vs losers, RED LIGHT avoided mistakes

**Success Criteria:**
- ✅ Z-Score data successfully captured for all 5 trades (no missing values, no errors)
- ✅ Time cost acceptable (≤30 seconds per trade)
- ✅ Clear pattern emerges (e.g., GREEN LIGHT = 80% win rate, RED LIGHT = 40% win rate)
- ✅ No workflow disruption (parallel tracking seamless)

**Decision Point (September 15):**
- **Proceed to Phase 2:** If success criteria met and pattern validates hypothesis
- **Modify & Retry:** If data capture issues or unclear patterns (extend Phase 1 by 5 more trades)
- **Drop Feature:** If zero correlation between Z-Score and outcomes (return to 27-column system)

**Documentation:**
- Log results in Comments field: "Phase 1 Test: [outcome]"
- Create summary table: Trade | P_115 Verdict | Z-Score Filter | Z_QualityScore | Actual Outcome | Match?

### Phase 2: Active Filter (September 16-30, 2026)

**Objective:** Test Z-Score as INITIAL FILTER (reject RED LIGHT candidates before full analysis)

**Scope:** 10+ trades

**Method:** ACTIVE FILTERING
- Use Z-Score Pre-Screen to make GO/NO-GO decisions
- Only analyze tickers that pass GREEN/YELLOW filter
- Track: Did filter reduce losers? Did filter save time?

**Workflow:**
1. Candidate identified (P_910, Eddie Z, Chaikin, etc.)
2. Load chart with RegimeCouncil indicator
3. Apply Stage 1 Filter:
   - GREEN LIGHT → Proceed to full P_115
   - YELLOW LIGHT → Proceed with caution (expect lower conviction)
   - RED LIGHT → SKIP (log ticker in "Rejected" tab with reason)
4. For GREEN/YELLOW candidates:
   - Complete full 35-column analysis
   - Make entry decision based on Combined Conviction Score
5. Track rejection rate and outcomes

**Success Criteria:**
- ✅ 10+ trades processed with Z-filter active
- ✅ RED LIGHT rejections avoided losers (validate filter effectiveness)
- ✅ GREEN LIGHT signals showed higher win rate than YELLOW (validate quality indicator)
- ✅ Time savings measurable (≥30 min/week)
- ✅ No regrets (no "should have entered" RED LIGHT skips that became big winners)

**Risk Management:**
- If RED LIGHT skip becomes obvious winner (e.g., 50%+ gain in week after skip): Document as "false negative" and review filter criteria
- Allow max 2 false negatives before adjusting thresholds

**Decision Point (September 30):**
- **Proceed to Phase 3:** If success criteria met and filter improved win rate ≥5%
- **Modify Thresholds:** If marginal improvement (1-4%), adjust sumZZ or other thresholds and extend Phase 2
- **Simplify or Drop:** If no improvement or negative, either simplify to binary PASS/FAIL or drop feature

**Documentation:**
- Create "Filter Rejections" tab in tracker: Date | Symbol | Source | sumZZ | Regime | Reason | Follow-Up Outcome
- Weekly review: Did rejected tickers remain weak? Did any become winners?

### Phase 3: Full Integration (October 2026)

**Objective:** Make Z-Score Council permanent part of trading system

**Scope:** All trades going forward

**Method:** FULL INTEGRATION
- Z-Score Pre-Screen is mandatory first step
- 35-column tracker becomes standard
- Combined Conviction Score used for position sizing tiers
- Documentation updated (SESSION_INITIALIZATION_PROMPT v2.8, Tracker_Log_Schema v9.5)

**Workflow Changes:**
- Update INIT prompt to reference 35-column schema
- Update QUICK_REFERENCE with Z-Score filter criteria
- Update SESSION_INITIALIZATION_PROMPT with new workflow
- Archive Phase 1 & 2 test data for future reference

**Ongoing Monitoring:**
- Monthly review: Z-Score quality score correlation with outcomes
- Quarterly threshold adjustment (if needed)
- Annual feature performance review (End of Q4 2026)

**Rollback Plan:**
- If Z-Score adds no value after 3 months: Return to 27-column system
- Keep Z-Score data archived but stop using for decisions
- Document lessons learned

---

## Testing & Validation

### Validation Metrics

**Primary Metrics:**

1. **Filter Effectiveness:**
   ```
   RED LIGHT Rejection Win Rate = (Rejected tickers that stayed weak) / (Total RED LIGHT rejections)
   Target: >70% (most rejections correctly avoided losers)
   ```

2. **Quality Indicator:**
   ```
   GREEN LIGHT Win Rate vs YELLOW LIGHT Win Rate
   Target: GREEN ≥10% higher than YELLOW
   ```

3. **Time Savings:**
   ```
   Minutes Saved = (Rejected tickers × 5 min) - (All tickers × 0.5 min filter time)
   Target: ≥30 minutes per week
   ```

4. **Win Rate Improvement:**
   ```
   Z-Filtered Win Rate vs Baseline Win Rate
   Target: +10% improvement (e.g., 60% → 66%)
   ```

**Secondary Metrics:**

5. **Conviction Tier Performance:**
   ```
   HIGH CONVICTION Win Rate (Z-Score ≥10)
   STANDARD ENTRY Win Rate (Z-Score 8-9)
   WATCH LIST Win Rate (Z-Score <8)
   Expected hierarchy: HIGH > STANDARD > WATCH
   ```

6. **Component Analysis:**
   ```
   Correlation of each Z-component with outcomes:
   - VOL_Z < -2.0 (low volume) → Failed breakout rate?
   - CMF_Z < 0 (money out) → Loser rate?
   - OBV_Z < 0 (selling pressure) → Breakdown rate?
   ```

### Historical Backtesting

**Limitation:** Cannot backtest Z-Score on historical trades because RegimeCouncil indicator was not loaded on those charts

**Alternative Validation:**
- Review past 10-20 trades from December 2025 - January 2026
- For each trade, re-load chart and add RegimeCouncil indicator
- Check: What was Z-Score reading on entry bar?
- Analyze: Would filter have improved decisions?

**Caution:** This is illustrative only (not true backtest), as RegimeCouncil may behave slightly differently on historical data

### Test Cases

**Test Case 1: BREAKOUT CONFIRMED**
- Setup: sumZZ ≥ 2.5, all Z-scores positive, Regime = BREAKOUT CONFIRMED
- Expected: GREEN LIGHT, Z_QualityScore ≥ 10, HIGH CONVICTION
- P_115 Action: Full analysis, standard position size
- Success Metric: 70%+ win rate

**Test Case 2: RANGE BOUND**
- Setup: sumZZ = 0.12, mixed Z-scores, Regime = RANGE BOUND
- Expected: RED LIGHT or YELLOW LIGHT (depending on CMF/OBV)
- P_115 Action: Skip or proceed with caution
- Success Metric: Lower win rate than GREEN LIGHT (validates filter)

**Test Case 3: BULL TRAP**
- Setup: VOL_Z > 1.0, PCT_GAIN_Z > 0, BUT CMF_Z < -1.0, OBV_Z < -1.0
- Expected: RED LIGHT (institutional divergence detected)
- P_115 Action: Skip (avoid fake strength)
- Success Metric: Most BULL TRAP signals should fail or underperform

**Test Case 4: STEALTH ACCUMULATION**
- Setup: OBV_Z > 1.5, CMF_Z > 1.0, BUT VOL_Z < 0.5, PCT_GAIN_Z < 0.5
- Expected: YELLOW LIGHT (smart money building, but not obvious yet)
- P_115 Action: Proceed if P_115 confirms, watch for breakout
- Success Metric: These should become GREEN LIGHT within 5-10 bars

**Test Case 5: LOW VOLUME WARNING**
- Setup: VOL_Z < -2.0 (extremely low participation)
- Expected: RED LIGHT or reduced conviction
- P_115 Action: Skip or reduce size 50%
- Success Metric: Low volume correlates with failed breakouts (50%+ failure rate)

---

## Risk Management

### Integration Risks

**Risk 1: Analysis Paralysis**
- **Concern:** Too many indicators → slower decisions, confusion, second-guessing
- **Mitigation:**
  - Z-Score is PRE-FILTER only (binary decision in 30 seconds)
  - Not part of P_115 core analysis (just bonus points)
  - Clear thresholds (no gray area judgment calls)
- **Monitoring:** Track decision time per trade (should not increase)

**Risk 2: False Negatives (Missed Winners)**
- **Concern:** RED LIGHT filter rejects setups that would have worked
- **Mitigation:**
  - Track all rejections in "Filter Rejections" tab
  - Review weekly: Did any become 20%+ winners?
  - Adjust thresholds if false negative rate >10%
- **Acceptance Criteria:** False negatives <10% of rejections

**Risk 3: Overconfidence Bias**
- **Concern:** HIGH CONVICTION label → oversizing, ignoring other risk factors
- **Mitigation:**
  - Position sizing still capped by account rules (max 5%)
  - Risk % still capped by market posture (CORRECTION mode overrides)
  - HIGH CONVICTION = standard size, not larger
- **Rule:** Z-Score never justifies exceeding risk limits

**Risk 4: Curve Fitting / Overfitting**
- **Concern:** Thresholds optimized for past data → won't work in different market regimes
- **Mitigation:**
  - Test in both rally and correction periods (Q3 includes both)
  - Use simple thresholds (sumZZ ≥ 2.0), not complex multi-variable equations
  - Pilot test with small sample before committing
- **Monitoring:** Quarterly review of threshold performance

**Risk 5: Technical Failure**
- **Concern:** Indicator breaks, data missing, false readings
- **Mitigation:**
  - Indicator proven stable on forum (hundreds of users, no major bugs)
  - Author confirms "does not repaint"
  - Fallback: If indicator fails to load, proceed without it (don't block workflow)
- **Contingency:** If persistent issues, drop feature immediately

**Risk 6: Sunk Cost Fallacy**
- **Concern:** Invested time/effort → reluctance to drop if not working
- **Mitigation:**
  - Pre-defined decision criteria (if no +5% win rate improvement → drop)
  - 5-trade pilot limit (low commitment)
  - Clear DROP threshold documented before starting
- **Discipline:** Follow decision matrix regardless of personal preference

### Position Sizing with Z-Score

**Rule: Z-Score NEVER overrides risk limits**

**Correct Usage:**
```
Account Balance: $35,000
Risk %: 1.5% standard (or 0.75% in CORRECTION mode)
Max Risk Capital: $525 (or $262.50 in CORRECTION)

Scenario: HIGH CONVICTION trade (P_115=78, Z-Score=10, Total=88)
Position Size: Calculate normally using Risk Capital ÷ (Entry - Stop)
  - If stock: Use full capital allocation
  - If options: Check spread, OI, R:R (standard criteria)
  - NO OVERSIZING beyond standard risk
```

**Incorrect Usage:**
```
❌ "This is HIGH CONVICTION, so I'll use 3% risk instead of 1.5%"
❌ "Z-Score is 10, so I'll add extra contracts"
❌ "This is GREEN LIGHT, so I'll ignore the spread being >10%"
```

**Conviction Tiers Impact:**
- **HIGH CONVICTION:** Use standard risk (don't reduce), prioritize this trade over others if capital constrained
- **STANDARD ENTRY:** Use standard risk, normal prioritization
- **WATCH LIST:** Consider reducing to 1.0% risk or paper trade

**Market Posture Interaction:**
- CORRECTION mode (50% risk reduction) applies REGARDLESS of Z-Score
- HOT MARKET mode (tiered risk) can be influenced by Z-Score (e.g., HT9 + HIGH CONVICTION = justify 5% risk)

---

## Troubleshooting

### Common Issues

**Issue 1: Indicator Not Displaying**
- **Symptom:** RegimeCouncil panel is blank or shows error
- **Causes:**
  - Script not saved properly
  - Parameter syntax error
  - TOS study limit reached (max 20 studies per chart)
- **Solution:**
  - Verify script copied completely (no truncation)
  - Remove unnecessary studies to free up slots
  - Restart TOS platform
  - Re-add indicator from Studies menu

**Issue 2: Labels Not Showing**
- **Symptom:** Histogram visible but labels missing from right side
- **Causes:**
  - Chart too narrow (labels hidden)
  - Label display disabled in TOS settings
- **Solution:**
  - Widen chart window
  - Right-click indicator → Show Labels

**Issue 3: Z-Scores All Near Zero**
- **Symptom:** All Z-scores reading 0.00 to 0.50
- **Causes:**
  - Stock in tight consolidation (low volatility)
  - Recent IPO (insufficient history for Z-length=20)
- **Solution:**
  - Normal behavior for low-volatility stocks
  - Interpret as RANGE BOUND (neutral)
  - May need longer history before Z-scores become meaningful

**Issue 4: sumZZ vs Regime Mismatch**
- **Symptom:** sumZZ = 0.5 but Regime says "UPTREND"
- **Causes:**
  - Regime logic uses additional criteria beyond just sumZZ
  - Regime may be forward-looking (trend forming but not extreme yet)
- **Solution:**
  - Trust sumZZ as primary filter criterion
  - Use Regime as context only
  - If mismatch persists, prioritize sumZZ threshold

**Issue 5: Extreme Z-Scores (>5 or <-5)**
- **Symptom:** Individual Z-component reading +7.2 or -6.8
- **Causes:**
  - Unusual event (earnings, halt, major news)
  - Data spike or anomaly
  - Low float stock with erratic behavior
- **Solution:**
  - Verify with news/earnings calendar
  - Treat as outlier (extreme but possibly valid)
  - Exercise caution (extreme readings = higher risk)

**Issue 6: Column Misalignment in Excel**
- **Symptom:** Z-Score data pasted into wrong columns
- **Causes:**
  - Skipped column during data entry
  - Copy-paste error from multiple sources
- **Solution:**
  - Use tab-delimited format strictly
  - Verify column headers match schema
  - Cross-check sample entries against documentation

**Issue 7: Filter Too Restrictive (No GREEN LIGHTS)**
- **Symptom:** 20+ candidates screened, zero GREEN LIGHTS in a week
- **Causes:**
  - Market in CORRECTION mode (expected)
  - Thresholds too strict (sumZZ ≥ 2.0 may be too high)
- **Solution:**
  - Review market regime (is SPY/QQQ weak?)
  - Consider lowering threshold temporarily (sumZZ ≥ 1.75)
  - Accept that CORRECTION periods naturally have fewer setups

**Issue 8: Filter Too Permissive (Many GREEN LIGHTS but Low Win Rate)**
- **Symptom:** 10+ GREEN LIGHTS per week, but only 40% win rate
- **Causes:**
  - Thresholds too loose
  - Other factors (market regime, stock quality) not addressed by Z-Score
- **Solution:**
  - Raise thresholds (sumZZ ≥ 2.5 instead of 2.0)
  - Add stricter filters (e.g., require VOL_Z > 0, not just CMF/OBV)
  - Re-evaluate if Z-Score adds value (consider dropping feature)

### Data Quality Checks

**Daily Check:**
- Verify no missing values in columns 28-35
- Verify Z_PositiveCount matches manual count
- Verify Z_QualityScore calculation correct

**Weekly Check:**
- Compare GREEN LIGHT vs RED LIGHT outcomes
- Review "Filter Rejections" tab for false negatives
- Check for indicator technical issues (missing data, errors)

**Monthly Check:**
- Correlation analysis: Z_QualityScore vs realized R:R
- Threshold effectiveness review
- Decision on threshold adjustments

---

## Appendix

### Quick Reference Card

**Z-Score Pre-Screen Checklist:**
```
[ ] Load chart with RegimeCouncil indicator
[ ] Read sumZZ: _____ (need ≥2.0 for GREEN)
[ ] Read Regime: ___________ (need bullish label)
[ ] Check CMF_Z > 0: [ ] Yes [ ] No
[ ] Check OBV_Z > 0: [ ] Yes [ ] No
[ ] Count positive Z-scores: _____ (need ≥4)

Decision:
[ ] GREEN LIGHT → Proceed to P_115
[ ] YELLOW LIGHT → Proceed with caution
[ ] RED LIGHT → Skip ticker
```

**35-Column Data Entry Template:**
```
[Columns 1-27: Standard P_115 fields]
28. Z_sumZZ: ___.___ 
29. Z_Regime: ___________
30. Z_CMF: ___.___ 
31. Z_OBV: ___.___ 
32. Z_VOL: ___.___ 
33. Z_RSI: ___.___ 
34. Z_PositiveCount: ___ (0-7)
35. Z_QualityScore: ___ (0-12, calculated)
```

**Z_QualityScore Calculator:**
```
Component 1 (sumZZ):
  ≥2.5 → 3 pts | 2.0-2.49 → 2 pts | 1.5-1.99 → 1 pt | <1.5 → 0 pts
  Score: _____

Component 2 (CMF):
  >1.0 → 2 pts | 0-1.0 → 1 pt | <0 → 0 pts
  Score: _____

Component 3 (OBV):
  >1.0 → 2 pts | 0-1.0 → 1 pt | <0 → 0 pts
  Score: _____

Component 4 (VOL):
  >2.0 → 2 pts | 1.0-2.0 → 1 pt | <1.0 → 0 pts
  Score: _____

Component 5 (RSI):
  >0 → 1 pt | ≤0 → 0 pts
  Score: _____

Component 6 (PositiveCount):
  ≥6 → 2 pts | 4-5 → 1 pt | <4 → 0 pts
  Score: _____

Total Z_QualityScore: _____ (sum of above, max 12)
```

### Glossary

**Z-Score:** Statistical measure showing how many standard deviations a value is from the mean. Z=+2 means 97.5th percentile (very high), Z=-2 means 2.5th percentile (very low).

**sumZZ:** Z-score of Z-scores. Meta-indicator showing whether the composite signal is unusual vs normal.

**Regime Council:** The 7-component indicator stack revealing market psychology through normalized technical factors.

**VWAP Distance:** How far price is from Volume-Weighted Average Price (institutional positioning baseline).

**CMF (Chaikin Money Flow):** Measures money flow volume, positive = accumulation, negative = distribution.

**OBV (On Balance Volume):** Cumulative buying/selling pressure based on volume.

**Direction-Adjusted Volume:** Volume sign flips based on price direction (positive on up days, negative on down days).

**Histogram Stack:** Visual representation of layered Z-scores, height = signal strength, direction = bullish/bearish.

**Pre-Screen Filter:** First-pass binary decision (GO/NO-GO) before deep analysis.

**Quality Score:** Composite 0-12 point score added to P_115 traditional score for conviction tiering.

**GREEN LIGHT:** Pass pre-screen filter, proceed to full analysis with high confidence.

**YELLOW LIGHT:** Conditional pass, proceed with caution and higher quality bar.

**RED LIGHT:** Fail pre-screen filter, skip ticker immediately.

**HIGH CONVICTION:** Total score ≥85 (P_115 ≥75 + Z-Score ≥10), maximum confidence entry.

**STANDARD ENTRY:** Total score ≥70, normal confidence and standard position sizing.

**WATCH LIST:** Total score <70, low confidence, paper trade or reduce size.

**Parallel Tracking:** Collecting data without using it for decisions (validation phase).

**Active Filtering:** Using filter to make GO/NO-GO decisions (implementation phase).

**False Negative:** Ticker rejected by filter that would have been a winner (cost of filtering).

**False Positive:** Ticker passed by filter but became a loser (failure of filter).

---

## Document Control

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 10, 2026 | Claude | Initial specification created |

**Related Documents:**
- FEATURES_ROADMAP_2026.md (parent document)
- SESSION_INITIALIZATION_PROMPT.md (will be updated to v2.8 in September)
- Tracker_Log_Schema.md (will be updated to v9.5 in September)
- QUICK_REFERENCE_V110.md (will be updated with Z-Score filter)

**Review Schedule:**
- Weekly during Phase 1 & 2 (September 2026)
- Monthly during Phase 3 (October-December 2026)
- Quarterly after full integration (2027+)

**Approval Required:**
- User approval before Phase 1 start (September 1, 2026)
- User approval before Phase 2 start (September 16, 2026)
- User approval before Phase 3 start (October 1, 2026)

**Sunset Clause:**
- If feature shows no improvement after Q3 2026, return to 27-column system
- Archive this specification for future reference
- Document lessons learned in SYSTEM_CORRECTIONS_LOG.md

---

**END OF Z-SCORE INTEGRATION SPECIFICATION v1.0**
