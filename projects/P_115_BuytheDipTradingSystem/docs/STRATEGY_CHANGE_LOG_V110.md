# STRATEGY CHANGE LOG - V110 Enhancement

---

## V112 -- June 19, 2026
**Status:** CONFIRMED -- Scan-side filter retired
**Decision by:** Tony Zoppi

### Change: P_920 Earnings Filter (V2.1) Confirmed Non-Functional -- Supersedes V2.1 Entry Below

**Root cause:** A Fund-tier mismatch pattern across three P_920 BUY signals on 6/19/26 (MTN, SUNB, VIRT) prompted a review of P_920_BuyersinControl_EOD.V2.1. Its header comments describe `noRecentEarnings = Sum(HasEarnings(), earningsLookback) == 0` as actively filtering same-day + 2-prior-session earnings reactions. This contradicts the V1->V2 changelog entry already in this script, which documents that `HasEarnings()` is unsupported in TOS Stock Hacker and that the filter attempt was reverted to V2.0. V2.1 was confirmed live in production -- the documented revert had not actually been carried forward into the running script.

**Confirmation:** Tony ran V2 and V2.1 side by side on 6/19/26. Identical result counts confirm `HasEarnings()` is inert in this scan engine (evaluates to a constant, never excludes anything). The filter has been a permanent no-op since it was added 5/8/26 -- roughly six weeks of believing the scan had earnings protection it did not have.

**Note:** This did not affect the 6/19/26 MTN/SUNB/VIRT batch specifically -- none of those three had earnings within the 3-bar lookback window regardless (MTN 8 sessions prior, SUNB upcoming 6/23/26 not yet reported, VIRT not until 7/29/26). The Fund-tier mismatches that day were a separate, already-known issue (TOS fundamental data lag, same pattern as the AEO case).

**Resolution:** V2.1 retired. V2 (pre-earnings-filter version) is confirmed as the live script -- no code change required, V2/V2.1 are behaviorally identical. Earnings filtering remains correctly handled at the review layer only (Claude's mandatory stockanalysis.com earnings-date check on every BUY/ASYM, per V110.3 below) -- that layer was never affected by this scan-side bug.

**Tracking:** WO-P920-E1.001 (CLOSED).

---

## V111 -- June 18, 2026
**Status:** PRODUCTION -- Active
**Decision by:** Tony Zoppi

### Change: Fund Verification Scope Extension -- P_118 and P_117-Recheck Mode

**Root cause:** Memory review surfaced a scope conflict -- prior memory claimed Fund Verification (V110.2) had been expanded from P_115-only to all four strategies on 4/27/2026. No corresponding change log entry exists for that date. Root cause identified: the Post-Earnings Auto-Flag Rule (V110.3, 5/8/2026) legitimately expanded to all four strategies and reuses the same stockanalysis.com fetch as Fund Verification -- the two separate rules got conflated in memory.

**Resolution:** V110.2's P_115-only scope is confirmed correct and unchanged for the original Fund Verification rule. Separately, review established that P_118 (mandatory P_115 recheck) and P_117 (optional P_115 recheck) already produce real Fund/Anal/Candle/Setup diagnostics when that recheck runs -- they are structurally P_115 signals at that point, not a different data pipeline. Extending Fund Verification to those two cases costs nothing additional (same stockanalysis.com fetch, same recompute logic already in use) and closes the same AEO-style failure mode V110.2 was built to prevent.

**Scope (clarified):**
- Fund Verification applies to: P_115 BUY/ASYM (unchanged) | P_118 BUY/ASYM (new -- via mandatory P_115 recheck) | P_117 BUY/ASYM when a P_115 recheck was performed (new -- conditional on recheck)
- Does NOT apply to: P_116 (no Fund value exists in its bounce-pattern pipeline) | P_117 rows with no recheck performed (no Fund value to verify)

**Cost:** Zero added time for the P_118/P_117-recheck cases -- same stockanalysis.com fetch already required by the recheck step itself.

---
## V110.4 -- May 21, 2026
**Status:** PRODUCTION -- Active
**Decision by:** Tony Zoppi

### Change: Options Data Lookup Sequence -- ChartExchange Added as Primary Web Fallback

**Root cause:** During OII P_118 STEP 3 on 5/21/2026, live options chain data was unavailable. Yahoo Finance returned 403, Barchart and Nasdaq blocked automated access. ChartExchange was not attempted, resulting in theoretical-only options pricing. Tony identified ChartExchange as the correct fallback that was skipped.

### New Rule (OPTIONS_RISK_METHODOLOGY.md):

Live options data lookup now follows a mandatory 4-step sequence:

1. **TOS Platform** (PRIMARY) — Pull directly from ThinkOrSwim if open. Always first.
2. **ChartExchange** — https://chartexchange.com/symbol/[TICKER]/optionchain/ — First web fallback.
3. **Yahoo Finance** — Second web fallback (browser if automated fails).
4. **Barchart / Nasdaq** — Third fallback, browser only.

**Rule:** TOS is always primary. Web sources are fallbacks. ChartExchange is the first web fallback — not Yahoo.

**Applies to:** All strategies (P_115, P_116, P_117, P_118) whenever STEP 3 options pricing is required.

---

## V110.3 -- May 8, 2026
**Status:** PRODUCTION -- Active
**Decision by:** Tony Zoppi

### Change 1: Post-Earnings Auto-Flag Rule -- MANDATORY on BUY/ASYM (All Strategies)

**Root cause:** P_920 EOD scan batch on 5/8/2026 produced two false-positive signals driven by earnings reactions, not technical dip-bounce setups:

- **AMN** (5/8/26): TOS LogEntry Fund=4 BUY. Earnings 5/7/26 ($2.10 actual vs $1.60 est). Strong 5/7 buying day was earnings reaction, not dip-bounce. Fund recompute via stockanalysis.com showed actual Fund=2 (ROE -14.19% fail, TTM loss -$95.7M), independently flipping verdict to No Signal. Earnings was the upstream cause that let a low-quality stock pass scan filters.
- **ASND** (5/8/26): TOS LogEntry Fund=2 ASYM. Earnings 5/5/26 ($11.46 actual vs $0.21 est, 53x beat). Post-earnings momentum continued through 5/7 close. Failed STEP 2 R:R gate (T1=T2=250.74 vs entry 246.14 with ATR 9.96 = R:R 0.31:1).

**ThinkScript scan filter attempted (V2.1):** Added Sum(HasEarnings(), 3) == 0 filter to P_920_BuyersinControl_EOD. **HasEarnings() is not supported in TOS Stock Hacker scans** (silently fails or errors). Reverted scan to V2.0; moved responsibility to the assistant review layer where it actually works.

### New Rule (Mandatory, no exceptions):

On every STEP 1 producing a **BUY or ASYM verdict** across **all strategies (P_115, P_116, P_117, P_118)**, Claude MUST:

1. Pull most recent earnings date from stockanalysis.com (already retrieved during Fund auto-verify -- zero added cost)
2. Compare earnings date to scan bar date (today)
3. If earnings within last 3 sessions (today + 2 prior trading bars): FLAG BEFORE STEP 2 with "Post-Earnings Pass" status
4. Document in Comments: "Post-earnings Day N (earnings M/D actual vs estimate)"
5. Hold for user resolution -- do not proceed to sizing without explicit override

**Scope:**
- Applies to ALL strategy BUY/ASYM signals: P_115, P_116, P_117, P_118
- Does NOT apply to No Signal rows
- Skipped if user states "OVERRIDE post-earnings" with reason
- Note: P_115 TOS chart script likely has its own earnings handling -- this rule applies at the review layer regardless, since P_116/P_117/P_118 inputs do not flow through P_115 chart logic

**Cost:** Zero added time -- earnings date pulled during the same Fund auto-verify stockanalysis.com fetch.

**Stabilization window rationale:** 3 sessions matches existing post-earnings auto-watch/pass practice. Day 0 (earnings) + Day 1 + Day 2 = full window. Day 3+ treated as stabilized.

### Supplementary Note: Scan-Layer vs Review-Layer Filtering

First attempt was scan-layer filtering (P_920 V2.1 with HasEarnings). TOS Stock Hacker does not support HasEarnings(). Documented limitation. Review-layer filtering during Fund auto-verify is correct architectural placement.

---
## V110.2 -- April 22, 2026
**Status:** PRODUCTION -- Active
**Decision by:** Tony Zoppi

### Change 1: Fund Verification Rule -- MANDATORY on BUY/ASYM

**Root cause:** AEO 4/21/2026 trade. TOS reported FundamentalsTier=4. User entered 4x AEO 5/15/26 19C @ $1.80 premium based on that score. Next-session price action put the position -44 percent unrealized. Post-trade audit with Chaikin Analytics ("very poor financial metrics, high long-term debt to equity") triggered a live re-scoring against stockanalysis.com data:

  - ROE = 10.73 percent (FAIL, below 15 percent threshold -- 20 pts lost)
  - Debt/Equity = 1.07, Debt/Cap ~52 percent (PASS -- 15 pts)
  - FCF = positive (PASS -- 10 pts)
  - Base score = 25 pts = **Fund 2**, not Fund 4

  HybridTier recalculation: Anal=1 + Fund=2 = 3. BUY threshold is 6. ASYM requires Anal>=3. Neither path qualified. **The trade should not have fired under V110 rules.**

**Conclusion:** TOS FundamentalsTier data is unreliable as a primary source. It aggregates from multiple vendors and reports "pretty" numbers that don't map cleanly to the three V110 input thresholds (ROE, Debt/Cap, FCF).

### New Rule (Mandatory, no exceptions):

On every P_115 STEP 1 that produces a **BUY or ASYM verdict with user-submitted Fund >= 2**, Claude MUST:

1. Pull live ROE, Debt/Capital, and FCF from stockanalysis.com via web search before STEP 2
2. Recompute Fund per V110 scoring (20+15+10 point thresholds)
3. Apply 200-MA penalty if known
4. Compare recomputed Fund vs user-submitted Fund
5. If recomputed Fund is **more than 1 tier below** submitted value -- FLAG before STEP 2 and hold for user resolution
6. If within 1 tier -- proceed, note verification in Comments column

**Scope:**
- P_115 BUY/ASYM only
- Skipped on No Signal rows (no cost to log)
- Does NOT apply to P_116, P_117, P_118 (different data pipelines)

**Cost:** ~10 seconds per BUY signal. Zero cost on the majority of rejected scans.

### Supplementary Rule: Chaikin Analytics as Tripwire

When live Fund verification is done, Chaikin Power Gauge rating can be used as a secondary sanity check:
- Use Chaikin as a **veto only**, not a trigger
- If Chaikin Rating <= Neutral AND recomputed Fund >= 3: stop and reconcile
- Prevents the "TOS Fund=4 but Chaikin Bearish" failure mode seen with AEO

---
## V110.1 -- April 17, 2026
**Status:** PRODUCTION -- Active
**Decision by:** Tony Zoppi

### Change 1: Fund=0 Auto-Reject Rule -- Narrowed to Falling Knife Only

CAUSE A -- BEAR/AVOID Zone (>20% below 200-MA) --> AUTO-REJECT
  V110 penalty = -4.0 | Identifier: STR=-2 AND Fund=0 together

CAUSE B -- Weak Fundamentals + Moderate Penalty --> FLAG FOR REVIEW (not auto-reject)
  Example: base Fund=1 + pullback -1.0 = adjusted 0 | Identifier: Fund=0 + STR > -2
  Log: RecheckStatus=Watch | SimulationNotes=Fund=0 weak-fundamental scan result

### Change 2: Authoritative Penalty Table (supersedes all prior versions)

  Zone          Distance from 200-MA     Penalty    Status
  ---------------------------------------------------------------
  NORMAL        At/above OR 0-3% below   0.0        No penalty
  PULLBACK      3-10% below              -1.0       Reduced tier
  CORRECTION    10-20% below             -2.0       Hard to qualify
  BEAR/AVOID    >20% below               -4.0       Auto-reject (falling knife only)

NOTE: MasterDoc Appendix A penalty values (-0.5, -1.0, -1.5) are SUPERSEDED.
      Update MasterDoc Appendix A at next doc review.

---

## Version: P_115_buyTheDipChart_V110
**Date:** February 10, 2026  
**Previous Version:** V101  
**Status:** PRODUCTION - Validated on live charts

---

## CRITICAL ENHANCEMENT: 200-Day MA Distance Penalty (Value Trap Filter)

### Problem Identified

**Case Study: FISV (Fiserv Inc.) - February 10, 2026**
- Current Price: $63.13
- 52-Week Performance: -73.9% (collapsed from $238.59)
- P_115 Base Fund Tier: 4 (strong historical metrics)
  - EPS Growth: 14.8% ✓
  - ROE: 13.7% ✓
  - Revenue: $21.16B ✓
- Technical Setup: R:R 2.66:1 (excellent)
- External Analysis: "Very bearish" rating, -88.7% relative weakness to SPY

**The Issue:**
System would have approved FISV based on backward-looking fundamental metrics (Fund=4) despite catastrophic -74% price decline. This is a classic **value trap** - stock appears "cheap" on traditional metrics but market is pricing in severe structural problems.

**Root Cause:**
FundamentalsTier scoring uses historical financial data (EPS, ROE, FCF) which lags real-time market sentiment. A stock can maintain strong historical metrics while entering severe downtrend, creating false buy signals on "dip buying" opportunities that are actually falling knives.

---

## Solution: Market-Aligned 200-MA Distance Penalty

### Concept

Add a **market position penalty** to Fund tier based on distance from 200-day moving average. This incorporates current market pricing into fundamental scoring, preventing entries on stocks in severe structural decline.

### Penalty Structure (Lenient Framework)

```
Distance from 200-MA          Penalty     Status          Adjusted Fund*
─────────────────────────────────────────────────────────────────────────
Above to -3% below            -0.5        NORMAL          3.5 (from 4)
-3% to -10% below             -1.0        PULLBACK        3.0 (from 4)
-10% to -20% below            -2.0        CORRECTION      2.0 (from 4)
-20%+ below (all)             -4.0        BEAR/AVOID      0.0 (disqualify)

*Assumes base Fund=4. Penalty scales proportionally for lower base tiers.
```

### Design Rationale

**1. Market-Aligned Thresholds:**
- Uses same logic as market correction definitions (-10%, -20%)
- Parallel structure to existing CORRECTION mode posture system
- Intuitive progression: Normal → Pullback → Correction → Bear

**2. Lenient on Healthy Stocks:**
- -0.5 penalty for normal 200-MA testing (-2% to -3%)
- Allows qualification with adjusted Fund 3.5
- Doesn't penalize routine volatility

**3. Progressive Severity:**
- Standard pullback (-8%): -1.0 penalty, still qualifies
- Correction zone (-15%): -2.0 penalty, needs strong technicals
- Binary cutoff at -20%: -4.0 disqualification (skips -3 for clarity)

**4. Decimal Fund Tiers:**
- Enables nuanced scoring (3.5, 2.5, etc.)
- Preserves quality signals with minor penalties
- Maximum remains 4 (no inflation)

---

## Technical Implementation

### Code Changes (P_115_buyTheDipChart_V110)

**Added After FundamentalsTier Calculation (Line ~67):**
```thinkscript
# === 200-DAY MA DISTANCE PENALTY (VALUE TRAP FILTER) ===
def ma200 = Average(close, 200);
def distFromMA200 = ((close - ma200) / ma200) * 100;

# Market-aligned lenient penalty structure
def maPenalty = 
    if distFromMA200 >= -3 then 0.5         # NORMAL
    else if distFromMA200 > -10 then 1.0    # PULLBACK
    else if distFromMA200 > -20 then 2.0    # CORRECTION
    else 4.0;                                # BEAR/AVOID

# Adjusted Fund tier (allows decimals)
def adjustedFundTier = Max(0, fundamentalsTier - maPenalty);

# Status code (0=NORMAL, 1=PULLBACK, 2=CORRECTION, 3=BEAR/AVOID)
def ma200StatusCode = 
    if distFromMA200 >= -3 then 0
    else if distFromMA200 > -10 then 1
    else if distFromMA200 > -20 then 2
    else 3;
```

**Updated HybridTier Calculation (Line ~223):**
```thinkscript
# OLD:
def hybridTier = analysisTier + fundamentalsTier;

# NEW:
def hybridTier = analysisTier + adjustedFundTier;
```

**Updated AsymmetricSetup (Line ~217):**
```thinkscript
# OLD:
def asymmetricSetup = (
    analysisTier >= 3 and fundamentalsTier >= 2 and
    (multiTimeframeSupport or wickAlign or rsiBounce4H)
);

# NEW:
def asymmetricSetup = (
    analysisTier >= 3 and adjustedFundTier >= 2 and
    (multiTimeframeSupport or wickAlign or rsiBounce4H)
);
```

**New Display Labels:**
```thinkscript
AddLabel(showTopRowLabels, "🧠 Fund Tier: " + 
    fundamentalsTier + "→" + Round(adjustedFundTier, 1) +
    " (" + [status text] + ")" + ...);

AddLabel(showTopRowLabels, "📏 200-MA Distance: " + 
    Round(distFromMA200, 1) + "% (" + [status text] + 
    ") | Penalty: -" + maPenalty, [color based on zone]);
```

**LogEntry Update (now top-right corner):**
```thinkscript
AddLabel(yes, "📊 LogEntry: " +
    GetSymbol() + " | " +
    Round(adjustedFundTier, 1) + " | " +  # Shows ADJUSTED Fund
    analysisTier + " | " + ...,
    Color.WHITE, Location.TOP_RIGHT);
```

---

## Validation & Testing

### Test Case 1: FISV (Value Trap - Prevented)

**Before V110:**
```
Price: $63.13
Fund: 4 (strong historical metrics)
Anal: 3
HybridTier: 7
Verdict: BUY ✅
Result: Would have entered failing stock
```

**After V110:**
```
Price: $63.13
200-MA: ~$165
Distance: -61.7% (BEAR zone)
Base Fund: 4
Penalty: -4.0
Adjusted Fund: 0
Anal: 3
HybridTier: 3
AsymmetricSetup: FAILS (Fund 0 < 2)
Verdict: NO SIGNAL ❌
Result: Value trap automatically rejected ✅
```

### Test Case 2: FINV (Strong Technicals, Still Rejected)

**Live Chart Validation - February 10, 2026:**
```
Price: $5.71
200-MA: ~$7.50-8.00 (declining)
Distance: ~-25% to -30% (BEAR zone)
Base Fund: Unknown
Penalty: -4.0
Adjusted Fund: 0

AnalysisTier: 4 (PERFECT - maximum possible)
SetupScore: 4 (all gates passed)
CandleTier: 2 (moderate)
Price Action: Purple arrows visible (patterns detected)

HybridTier: 4 + 0 = 4
Need ≥6: FAILS ❌
AsymmetricSetup: Anal 3 ≥ 3 ✓, Fund 0 ≱ 2 ✗ → FAILS

Final Verdict: NO SIGNAL ❌
```

**Key Finding:**
Even with PERFECT technical setup (Anal=4, Setup=4, PA patterns), the 200-MA penalty correctly overrode the signal. System prioritized risk management over opportunity.

**Chart Evidence:**
- Bottom banner: "BEAR ACTIVE: P - Days: 0 | Since: -4.8 | Below: -81"
- Visual: Declining 200-MA (yellow line at top), price well below
- Recent bounce attempt (purple arrows) = dead cat bounce territory
- Value trap filter prevented entry on technical enthusiasm

---

## Impact Analysis

### Benefits

**1. Automatic Value Trap Prevention:**
- Binary decision at -20% threshold
- No manual investigation needed for BEAR zone stocks
- Protects capital from catastrophic entries

**2. Preserves Quality Signals:**
- Stocks at -2% below 200-MA: Fund 3.5 (still qualify)
- Minor pullbacks (-8%): Fund 3.0 (still qualify with Anal 3)
- Progressive penalty, not blanket rejection

**3. Market-Aligned Logic:**
- Same thresholds as market correction definitions
- Parallel to existing CORRECTION mode posture
- Professional, institutional-grade framework

**4. Nuanced Scoring:**
- Decimal Fund tiers (3.5, 2.5) preserve signal quality
- Correction zone stocks need stronger technicals (Anal=4)
- Maintains tiered decision-making approach

### Risks Mitigated

**1. Historical Metrics Lag:**
- Traditional fundamentals can stay strong while stock fails
- 200-MA penalty adds real-time market sentiment
- Prevents "cheap on metrics" traps

**2. Falling Knife Syndrome:**
- Stocks >20% below 200-MA are in structural decline
- These rarely become successful "dip buys"
- Filter blocks entries on continued deterioration

**3. Survivorship Bias:**
- System was calibrated on stocks that recovered
- Didn't account for stocks that continued falling
- 200-MA penalty addresses this blind spot

---

## Behavioral Changes

### What Changes for Traders

**1. Fund Tier Interpretation:**
```
Old (V101 and earlier):
  LogEntry: AAPL | 4 | 3 | 2 | 3 | 1 | - | BUY
                   ↑
                   Base fundamentals only

New (V110+):
  LogEntry: AAPL | 3.5 | 3 | 2 | 3 | 1 | - | BUY
                   ↑
                   Adjusted (includes 200-MA penalty)
```

**2. Automatic Rejections:**
- Fund=0 in LogEntry → Immediate rejection, no analysis needed
- Stock is >20% below 200-MA (BEAR/AVOID territory)
- Even perfect technicals cannot override

**3. Higher Bar in Correction Zone:**
- Stocks -10% to -20% below 200-MA have Fund reduced by 2
- Need stronger technicals (Anal=4) to qualify
- Appropriate risk management in vulnerable zones

**4. Lenient on Healthy Stocks:**
- Routine 200-MA testing (-2%) barely penalized (Fund 3.5)
- System doesn't reject quality signals over noise
- Focus on severe downtrends, not normal volatility

### Workflow Integration

**Before Trade Execution:**
```
1. Check LogEntry Fund value
2. If Fund=0 → Skip to next ticker (value trap)
3. If Fund<3 → Verify strong technicals (Anal≥4)
4. If Fund≥3 → Proceed with normal analysis
```

**Chart Review:**
```
Look for Fund tier label showing:
"🧠 Fund Tier: 4→3.5 (NORMAL) (Strong)"
             ↑   ↑     ↑
          Base Adj  Status
```

**Comments Field Documentation:**
```
Example entries:
"Fund: 4→3.5 (MA200: -2.1% - NORMAL)"
"Fund: 4→2.0 (MA200: -15.3% - CORRECTION)"
"Fund: 4→0 (MA200: -62% - BEAR/AVOID - value trap)"
```

---

## Performance Expectations

### Signal Filtering

**Expected Rejection Rates:**
- Value traps (Fund=0): 1-3% of total P_115 signals
- Correction zone penalties: 5-10% of signals
- Net effect: Slightly lower signal count, much higher quality

**Quality Improvement:**
- Eliminates catastrophic entries (FISV-style collapses)
- Reduces drawdown risk on "cheap" falling stocks
- Improves win rate by filtering structural declines

### HybridTier Distribution Shift

**Before V110:**
```
HT 6-7: Most common (Fund 3-4 + Anal 3)
HT 8+: Rare (Fund 4 + Anal 4)
```

**After V110:**
```
HT 6-7: Reduced (penalty affects marginal signals)
HT 8+: Proportionally more (only strongest survive correction zone)
Signal quality: Higher average
```

---

## Documentation Updates Required

### Files Updated

1. **SESSION_INITIALIZATION_PROMPT.md** → v2.7
   - Added 200-MA penalty section
   - Updated LogEntry extraction location (top-right)
   - Added decimal Fund tier support
   - Included FISV/FINV validation examples

2. **P_115_buyTheDipChart** → V110
   - Added 200-MA calculation and penalty logic
   - Updated HybridTier and AsymmetricSetup calculations
   - New display labels for Fund adjustment
   - LogEntry moved to top-right corner

3. **Strategy_Change_Log** → This document
   - Comprehensive V110 enhancement documentation

4. **Quick_Reference_Prompts** → To be updated
   - Add 200-MA penalty quick reference
   - Update Fund tier interpretation
   - Add value trap identification guide

### Training Materials

**For New Sessions:**
- Explain Fund=0 means automatic rejection
- Show FISV/FINV examples as cautionary tales
- Emphasize 200-MA penalty is protective, not restrictive

**For Existing Users:**
- Fund tier now shows adjusted value (includes penalty)
- Decimal values (3.5, 2.5) are normal in V110
- LogEntry moved to top-right for better visibility

---

## Lessons Learned

### From FISV Discovery

**What Went Wrong:**
- Strong historical metrics masked current failure
- Backward-looking data created false confidence
- No real-time market sentiment integration

**What V110 Fixes:**
- 200-MA provides current market view
- Penalty prevents historical metric blindness
- Binary cutoff at -20% creates clear boundary

### From FINV Validation

**What We Confirmed:**
- Strong technicals alone are insufficient
- Value trap filter works even with perfect setups
- System prioritizes capital preservation over opportunity

**Design Validation:**
- Lenient structure doesn't over-filter
- Market-aligned thresholds are intuitive
- Decimal Fund tiers preserve nuance

---

## Future Considerations

### Potential Enhancements (V111+)

**1. RSI vs 200-MA Divergence:**
- Add bonus for RSI >50 when near 200-MA
- Reward "healthy testing" patterns
- Further differentiate quality pullbacks

**2. Volume at 200-MA:**
- Check volume spike at 200-MA touch
- High volume = institutional support
- Could reduce penalty slightly

**3. 200-MA Slope:**
- Rising 200-MA = healthier than declining
- Adjust penalty based on MA trend
- More forgiving on rising MAs

**4. Sector-Relative Positioning:**
- Compare stock to sector 200-MA position
- Stock outperforming weak sector = less penalty
- Context-aware adjustments

### Monitoring Plan

**Monthly Review:**
- Track rejection rate due to Fund=0
- Measure improvement in win rate
- Compare to pre-V110 performance

**Validation Metrics:**
- Count value traps prevented
- Measure avoided drawdown
- Track false negatives (missed opportunities)

---

## Conclusion

**V110 Status:** PRODUCTION READY ✅

**Validation:** Proven on live charts (FINV)

**Impact:** Prevents value trap entries while preserving quality signals

**Next Steps:**
1. Deploy V110 as primary P_115 script
2. Update Quick Reference documentation
3. Monitor performance metrics
4. Consider enhancements for V111

**Critical Success Factors:**
- FISV would have been auto-rejected (Fund=0)
- FINV correctly rejected despite perfect technicals
- System maintains discipline over opportunity

**The 200-MA penalty enhancement represents a fundamental improvement in P_115's ability to differentiate between genuine "dip buying" opportunities and value traps. This is a mandatory upgrade for capital preservation.**

---

**Version:** V110  
**Date:** February 10, 2026  
**Author:** Anthony + Claude  
**Status:** ACTIVE  
**Validation:** FISV (prevented), FINV (validated)  
**Next Review:** March 2026
