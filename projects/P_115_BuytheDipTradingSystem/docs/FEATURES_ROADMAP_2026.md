# Features Roadmap 2026
**Trading System Enhancement Plan**

---

## Current System Status (Q1 2026)

### Active Strategies
- **P_115**: Buy The Dip (Core anticipation strategy)
- **P_116**: Options Income Launchpad (Bounce patterns, premium collection)
- **P_117**: Ad-Hoc Signals (External sources: Chaikin, emails, recommendations)
- **P_118**: Eddie Z Breakouts (Pattern confirmation: C&H, DB, Flat Base, High Handle)

### System Version
- Tracker Schema: v9.4.0
- Scoring Logic: v9.2 (calibrated December 2025)
- 27-column unified tracking
- Multi-strategy convergence analysis

### Current Focus: **VALIDATION PHASE (Q1-Q2 2026)**
- Build 20+ trade sample size
- Measure baseline win rates by strategy
- Paper trade new signals before live capital
- Establish performance benchmarks

---

## Q1-Q2 2026: Validation Phase (CURRENT)

### Primary Objectives
1. **Complete 20+ trades** across all strategies
2. **Measure baseline performance:**
   - P_115 win rate: Target >60%
   - P_118 (Eddie Z) win rate: Target >50%
   - P_117 (Chaikin) win rate: Target >55%
   - BUY signal vs ASYM: Expect +15% delta
3. **Validate execution:**
   - Options vs stock R:R
   - Theta impact on 30-40 DTE
   - Liquidity management (OI, spreads)
4. **Pattern analysis:**
   - Which Eddie Z patterns perform best? (C&H vs DB vs Flat Base)
   - Does CandleTier=2 outperform CandleTier=0?
   - HybridTier=6 vs HybridTier=5 performance delta

### Success Criteria (End of Q2)
- YES 20+ completed trades logged
- YES Overall win rate >55%
- YES Positive R:R (>1.5:1 realized)
- YES Strategy performance ranked
- YES Decision framework for Q3 (keep/drop/scale)

### Constraints
- NO new features during validation
- NO automation projects
- NO additional data sources
- FOCUS on execution, logging, analysis

---

## Q3 2026: Enhancement Phase (PLANNED)

### Feature 1: Insider Data Integration (PRIORITY 1)

**Status:** Parked from Q1 conversation (Jan 12, 2026)

**Rationale:**
- Free, publicly available conviction signal
- Validates/invalidates external signals (Chaikin, Eddie Z)
- Early warning for company inflection points
- Tiebreaker for similar setups

**Implementation Plan:**

#### Phase 1: Manual Integration (July 2026)
```
Workflow Addition:
P_117 STEP 1 -> [Signal] -> P_115 Recheck -> INSIDER CHECK -> Convergence -> Verdict

Data Source: Dataroma.com/m/ins/ins.php
Frequency: Weekly (Sunday evening review)
Time: 15 minutes/week
```

**Checklist:**
1. Visit Dataroma
2. Filter: Last 7 days, Purchases only, >$100K
3. Flag: CEO/CFO/Board buys, cluster buying (3+ insiders)
4. Cross-reference with watchlist
5. Document in Comments field

**Integration Points:**
- P_117: Add "Insider Check" to Step 1 workflow
- Comments field: "Insider (30d): [activity summary]"
- Scoring bonus: +1-2 FundamentalsTier for conviction buying

#### Phase 2: Automation (August-September 2026)
```
Tech Stack: Python + Dataroma scraping/API
Frequency: Daily automated scan
Output: Alert on conviction buys (CEO/CFO >$250K)
```

**Automation Tasks:**
1. Daily Dataroma scrape
2. Filter: Buys >$250K, CEO/CFO/Board only
3. Exclude IPO noise (<30 days trading)
4. Auto-run P_115 on flagged tickers
5. Email alert if BUY/ASYM match

**Success Metrics:**
- Does insider filter improve win rate by +5%?
- Reduce false positives on Chaikin signals?
- Early detection of 2+ high-conviction trades per quarter?

---

### Feature 2: 60-Min Chart Analysis (PRIORITY 2)

**Status:** Eddie Z's "secret weapon" - conditional on Eddie Z validation

**Rationale:**
- Intraday confirmation of daily patterns
- Mini cup-and-handle inside daily handle
- Volume surge timing for entries
- Institutional entry point detection

**Prerequisites:**
- Eddie Z must show >50% win rate in Q1-Q2
- Minimum 10 Eddie Z trades completed
- Clear pattern performance data (which patterns work?)

**Implementation Plan:**

#### Phase 1: Manual Checklist (August 2026)
```
When: After Eddie Z pick passes P_115 recheck
What: Zoom into handle area on 60-min chart
Look for:
1. Mini cup-and-handle formation
2. Volume surge on 60-min breakout
3. Institutional buying (large candles, tight spreads)
```

**Integration:**
- Add to P_118 Step 1: "60-min confirmation: [YES/NO]"
- Track: Does 60-min confirmation improve win rate?
- Comments field: "60-min mini-handle confirmed, volume surge"

#### Phase 2: Systematic Scoring (September 2026)
```
Add to CandleTier or create new "IntraConfirmation" tier
Scoring:
+1: 60-min mini-handle present
+1: 60-min volume surge (>150% avg)
+1: 60-min tight consolidation in handle

Max bonus: +3 to SetupScore
```

**Success Metrics:**
- 60-min confirmation -> +10% win rate improvement?
- Reduce premature Eddie Z entries?
- Validate as mandatory vs. optional check?

---

### Feature 3: Distribution Day Tracker (PRIORITY 3)

**Status:** Market regime overlay for breakout probability adjustment

**Rationale:**
- 4-5 distribution days in 3-5 weeks = market top
- Breakout success drops from 70% to 40% in corrections
- Follow-through days signal rally attempts
- Position sizing should scale with market direction

**Implementation Plan:**

#### Phase 1: Manual Tracking (July 2026)
```
Weekly Task (Sunday):
1. Count distribution days (SPY/QQQ down on higher volume)
2. Note in tracker: DistributionDayCount column
3. Identify follow-through days (day 3-10 of rally, >1.5% on volume)
4. Set MarketDirection: Rally / Correction / Neutral
```

**Integration:**
- Update existing columns (already in schema, just unused)
- DistributionDayCount: [0-5+]
- FollowThroughDay: [Yes/No/Date]
- MarketDirection: [Rally/Correction/Neutral]

#### Phase 2: Probability Adjustment (August 2026)
```
Breakout Probability by Market Regime:
Rally (0-3 dist days): 70% -> Use standard position sizing
Correction (4-5 dist days): 40% -> Reduce size by 50%
Follow-through day: 70% -> Resume standard sizing

Position Sizing Multiplier:
Rally: 1.0x (full size)
Correction: 0.5x (half size)
```

**Success Metrics:**
- Avoid breakout failures in distribution phase?
- Improve timing of re-entry after corrections?
- Reduce drawdowns by 20%+?

---

### Feature 4: Z-Score Regime Council Integration (PRIORITY 4)

**Status:** Planned for Q3 2026 (September) - Conditional on Q1-Q2 validation complete

**What Is It:**
Multi-factor Z-score indicator (justAnotherTrader's "Regime Council") that normalizes 7 market dimensions into unified market psychology signal:
- VWAP Distance Z (positioning)
- Volume Z (participation, direction-adjusted)
- OBV Z (money flow momentum)
- CMF Z (Chaikin money flow intensity)
- RSI Z (momentum oscillator)
- MACD Z (trend momentum)
- Percentage Gain Z (daily performance)

Stacked histogram + composite sumZZ score reveals market regime (BREAKOUT CONFIRMED, STEALTH ACCUMULATION, BEAR TRAP, RANGE BOUND, etc.)

**Problem It Solves:**
1. **Time Efficiency:** Filter out weak setups in 30 seconds before investing 5 minutes in full P_115 analysis
2. **Quality Enhancement:** Detect hidden institutional divergence (price down but money flow positive = stealth accumulation)
3. **Risk Reduction:** Avoid "good-looking" dips that are actually breakdowns (price up but money flow negative = bull trap)
4. **Pattern Validation:** Confirm Eddie Z breakouts have institutional backing, not just retail FOMO

**Hypothesis:**
- Z-Score pre-screen will eliminate 60-70% of weak candidates before full analysis
- High Z-Score quality (sumZZ >=2.0, 6-7 positive indicators) will correlate with +10-15% higher win rate
- Low volume (VOL_Z < -2.0) will be early warning for failed breakouts
- Combined P_115 + Z-Score scoring will create clearer conviction tiers (HIGH/STANDARD/WATCH)

**Prerequisites (MUST BE MET):**
- Q1-Q2 validation complete (20+ trades, June 30, 2026)
- Baseline win rates established by strategy (P_115, P_117, P_118)
- Distribution Day Tracker implemented (Priority 3 complete)
- Clear decision framework: Keep current system if win rate >60%, enhance if 50-60%, overhaul if <50%
- Regime Council indicator already loaded in ThinkorSwim (confirmed working)

**Implementation Plan:**

#### Phase 1: Pilot Test (September 1-15, 2026)
```
Scope: 5 trades only (paper or small position size)
Method: PARALLEL TRACKING (run alongside existing P_115, don't change verdicts)

Workflow:
1. Candidate ticker identified (P_910 scan, Eddie Z, Chaikin, etc.)
2. Load in TOS with Regime Council indicator
3. Record Z-Score readings in NEW columns (28-35)
4. Continue with standard P_115 analysis (unchanged)
5. Track: Would Z-filter have improved decision?

Success Criteria for Phase 1:
- Z-Score data successfully captured for 5 trades
- Clear pattern emerges (high Z-Score = better outcomes?)
- Time cost acceptable (<30 seconds per trade)
- Decision: Proceed to Phase 2, Modify, or Drop
```

**New Columns (Phase 1 - Columns 28-35):**
| Column # | Field Name | Data Source | Notes |
|----------|------------|-------------|-------|
| 28 | Z_sumZZ | Indicator label | Composite Z-score (-3 to +3 typical) |
| 29 | Z_Regime | Indicator label | BREAKOUT/UPTREND/MOMENTUM/RANGE BOUND/DOWNTREND |
| 30 | Z_CMF | Indicator label | Chaikin Money Flow Z-score |
| 31 | Z_OBV | Indicator label | On Balance Volume Z-score |
| 32 | Z_VOL | Indicator label | Volume Z-score (direction-adjusted) |
| 33 | Z_RSI | Indicator label | RSI Z-score |
| 34 | Z_PositiveCount | Manual count | Count of positive Z-scores (0-7) |
| 35 | Z_QualityScore | Calculated | Composite quality score (0-12) |

#### Phase 2: Pre-Screen Filter (September 16-30, 2026)
```
If Phase 1 validates hypothesis, activate as INITIAL FILTER

Stage 1: Z-Score Pre-Screen (30 seconds)
  GREEN LIGHT -> Proceed to P_115 analysis
    - sumZZ >= 2.0
    - Regime: BREAKOUT/UPTREND/MOMENTUM
    - CMF_Z > 0 AND OBV_Z > 0
    - >=4 out of 7 positive Z-scores

  YELLOW LIGHT -> Higher quality bar
    - sumZZ 1.0-1.99
    - Regime: MODERATE/early UPTREND
    - >=5 out of 7 positive

  RED LIGHT -> Skip immediately
    - sumZZ < 1.0
    - RANGE BOUND/DOWNTREND/bearish regime
    - CMF_Z < 0 OR OBV_Z < 0
    - <4 positive Z-scores

Stage 2: Full P_115 Analysis (if GREEN/YELLOW)
  - Run standard 27-column methodology
  - Add Z-Score bonus (0-12 points)
  - Combined conviction score = P_115 base + Z bonus

Success Criteria for Phase 2:
- 10+ trades processed with Z-filter active
- RED LIGHT rejections = fewer losers? (validate filter effectiveness)
- GREEN LIGHT signals = higher win rate? (validate quality indicator)
- Time savings = 30+ minutes per week? (validate efficiency gain)
```

#### Phase 3: Full Integration (October 2026)
```
If Phase 2 validates improvement, make permanent

Combined Scoring System:
- P_115 Traditional Score: 0-100 points (existing)
- Z-Score Quality Bonus: 0-12 points (new)
- TOTAL POSSIBLE: 112 points

Entry Thresholds:
- HIGH CONVICTION (>=85 total): Traditional >=75 + Z-Score >=10
- STANDARD ENTRY (>=70 total): Traditional >=60 + Z-Score >=8
- WATCH LIST ONLY (<70 total): Need improvement

Documentation Updates:
- SESSION_INITIALIZATION_PROMPT v2.8
- Tracker_Log_Schema v9.5 (35 columns)
- QUICK_REFERENCE with Z-Score thresholds
```

**Success Metrics (End of Q3 2026):**

Quantitative:
- Z-Score filter eliminated >=60% of weak setups before full analysis?
- HIGH CONVICTION trades (Z-Score >=10) achieved >=70% win rate?
- STANDARD ENTRY trades (Z-Score 8-9) achieved >=60% win rate?
- VOL_Z < -2.0 flagged >=50% of failed breakouts?
- Time savings >=30 minutes per week?

Qualitative:
- Z-Regime labels provided actionable context (not just noise)?
- Prevented at least 2 high-conviction mistakes (bull traps, weak volume)?
- Integration smooth (no workflow disruption)?
- Data capture reliable (no column misalignment issues)?

**Decision Matrix (End of Q3):**
```
Z-Score Performance -> Action
Improved win rate +10%+ -> KEEP, make permanent
Improved win rate +5-9% -> KEEP, minor refinements
Improved win rate +0-4% -> CONDITIONAL (extend test or simplify)
No improvement or negative -> DROP (return to 27-column system)
```

**Integration with Other Q3 Features:**
- Synergy with Distribution Day Tracker: Market-level + stock-level regime = complete context
- Synergy with 60-Min Analysis: Z-Score + 60-min confirmation + P_115 = three-layer validation
- Synergy with Insider Data: Z-Score GREEN + Insider conviction = strongest convergence

**Technical Details:**
See Z_SCORE_INTEGRATION_SPEC.md for complete implementation specifications

---

### Feature 5: Morning Star Pattern — PA6 Integration (PRIORITY 5)

**Status:** Proposed Q3 2026 — PA Pattern Code Expansion Series

**Rationale:**
- First multi-candle PA code — extends the pattern library beyond single-candle reversals
- Natural P_115 convergence signal: oversold + support + three-candle buyer confirmation = highest-probability bounce setup in the system
- Visible without indicators — pure price action, no data dependency
- Directly boosts CandleTier and SetupScore when confirmed at the 44-day low support zone
- Strongest possible P_115 signal: scan surfaces the ticker AND the chart prints a Morning Star at support on the same day

**PA Code:** PA6 = Morning Star (Multi-Candle Bullish Reversal)

**What Is It:**
The Morning Star is a three-candle bullish reversal that signals a shift from downtrend to uptrend:
- Candle 1: Strong bearish candle — sellers in control, continues the downtrend
- Candle 2: Small body (bullish, bearish, or doji) — indecision; selling pressure slowing
- Candle 3: Strong bullish candle — closes above the midpoint of Candle 1 body; buyers in control

**Scoring Impact:**
- CandleTier: T2 minimum on pattern alone; T3 with volume surge on Candle 3 (>125% of 20-day avg)
- SetupScore: +1 for CandleTier >= 2 (existing rule — no schema change required)
- FundamentalsTier: No impact (purely technical pattern)
- HybridTier: Benefits indirectly via CandleTier elevation

**Detection Criteria (ThinkScript — future automation):**
```
Candle 1: bearish body > 0.6x daily ATR
Candle 2: body < 0.3x Candle 1 body (indecision)
Candle 3: bullish, closes above midpoint of Candle 1 body
           + price within 2% of 44-day low (nearSupport zone)
Optional boost: Candle 3 volume > 125% of 20-day avg volume
```

**Workflow Integration:**

STEP 1 — Detection:
- When Morning Star identified on chart: CandleTier = T2 min (T3 if C3 volume surge)
- Log PA6 in Comments field: "PA6 - Morning Star at 44-day low. C3 closed above C1 midpoint. Vol [surge/normal]"
- SimulationNotes: "Morning Star at [support level] — [date]"

STEP 2 — Position Sizing:
- Stop placed below Candle 2 low (tight) OR Candle 3 low (standard) — document in SLLevel
- No sizing bonus beyond standard three-gate system

**Entry Method Alignment with P_115:**
- Close of C3 = standard close-of-signal-day entry (default)
- 60-min mini-handle forming after C3 = highest confirmation (synergy with Feature 2)
- Pullback into C3 body after close = best R:R entry

**Stop-Loss Options:**
- Below Candle 2 low: tightest — ideal when at major support level
- Below Candle 3 low: standard — most common placement
- Below pattern low (all three candles): widest — use for volatile/wide-range candles

**Relationship to Existing PA Codes:**
- PA1-PA5: Single-candle patterns (BOSS, Pin Bar, Inside Bar, DZC, RRR)
- PA6+: Multi-candle patterns — new sub-series opened by Morning Star
- Future: PA7 = Evening Star (bearish reversal mirror), PA8 = Three White Soldiers

**Prerequisites:**
- PA4 (DZC) and PA5 (RRR) implemented first — sequential PA code build
- 5+ Morning Star setups documented manually before ThinkScript automation
- No 27-column schema changes required (Comments field absorbs PA6 code)

**Priority:** Q3 2026 — after PA4/PA5; no dependency on validation phase completion

**Success Metrics:**
- PA6 Morning Star signals achieve R:R >= 2:1 baseline
- T3 CandleTier (volume surge on C3) shows higher win rate than T2 alone
- ThinkScript detection fires correctly on known historical examples

---

## Q4 2026: Automation & Scale (FUTURE)

### Feature 6: Python Excel Auto-Logger (PRIORITY 1 - Q4)

**Status:** Approved Apr 8, 2026 — Ready to build

**Problem:** Manual copy/paste of tab-delimited rows into Excel tracker causes friction and misalignment errors.

**What It Does:**
- Python script (openpyxl) appends 27-column rows directly to tracker .xlsx
- Called via Windows-MCP PowerShell from Claude session
- Input: tab-delimited string | Output: row appended to .xlsx
- Eliminates manual paste step entirely

**Tech Stack:** Python + openpyxl | p140 conda env | Local file — no broker connection

**Prerequisites:**
- Tracker .xlsx path confirmed by Tony
- Test on backup copy before live tracker

**Notes:** Precursor to Schwab API auto-log (Feature 10). Low complexity, high daily impact.

---

### Feature 7: Automated Position Alerts

**Status:** Requires stable baseline + validated strategies

**What:**
- Email/SMS when position approaching TP/SL
- Daily P&L summary
- New Eddie Z picks auto-notification
- Chaikin rating changes for held positions

**Tech Stack:**
- Python scheduler (cron)
- TOS/broker API for position tracking
- Email/SMS gateway

---

### Feature 8: Performance Dashboard

**Status:** After 50+ trades completed

**What:**
- Win rate by strategy (P_115, P_117, P_118)
- Win rate by signal type (BUY vs ASYM)
- Win rate by pattern (C&H vs DB vs Flat Base)
- Win rate by market regime (Rally vs Correction)
- Average R:R realized vs. planned
- Drawdown analysis
- Source performance (Eddie Z vs Chaikin vs Direct)

**Tech Stack:**
- Python + Pandas
- Visualization: Matplotlib or Plotly
- Auto-update from tracker CSV

---

### Feature 9: Correlation Analysis

**Status:** Multi-position portfolio management

**What:**
- Detect sector concentration risk
- Flag correlated positions (>0.7 correlation)
- Suggest diversification opportunities
- Portfolio-level risk calculation

---

### Feature 10: Schwab API Auto-Log (PRIORITY 2 - Q4)

**Status:** Planned — requires Feature 6 (Python Excel Auto-Logger) validated first

**Problem It Solves:**
- Even with Excel Auto-Logger, trade logging still requires a manual trigger
- Outcome updates (SL Hit / TP Hit) require manual STEP 3 each time
- No live connection between broker executions and tracker

**What It Does:**
- Connects directly to Schwab brokerage API (OAuth)
- Pulls live fill data: executions, prices, timestamps
- Auto-logs new trades to tracker on fill confirmation
- Auto-updates Outcome column when TP/SL hit
- Daily P&L sync to AccountBalance field

**Tech Stack:** Python + Schwab API (OAuth) + openpyxl (Feature 6 dependency)

**Prerequisites:**
- Feature 6 live and validated
- Schwab API credentials configured, OAuth flow tested
- 20+ trade validation baseline complete

**Notes:** End-state for fully automated logging. High complexity. Feature 6 is the manual bridge until this is ready.

---

## Features Parking Lot (Post-2026)

### Low Priority / Experimental

1. **Machine Learning Signal Generation**
   - Train model on historical P_115 data
   - Predict next-day HybridTier scores
   - Compare ML vs. rules-based

2. **News/Catalyst Integration**
   - Auto-fetch earnings dates
   - FDA approval calendars (biotech)
   - Sector rotation news alerts

3. **Social Sentiment Analysis**
   - Twitter/Reddit sentiment scoring
   - Correlation with breakout success
   - Early warning system

4. **Options Strategy Optimizer**
   - Compare vertical spreads vs. long calls
   - Iron condors for income
   - Covered call automation

5. **Backtesting Engine**
   - Test historical P_115 signals
   - Validate scoring changes
   - Monte Carlo simulations

---

## Decision Framework

### When to Add a Feature

**GREEN LIGHT (Proceed):**
- Validation phase complete (20+ trades)
- Baseline win rate established
- Feature addresses proven pain point
- Time investment <10 hours to implement
- No disruption to current workflow

**YELLOW LIGHT (Pilot):**
- Feature has theoretical value but unproven
- Requires paper trading to validate
- Small-scale test first (5 trades)
- Can be abandoned without sunk cost

**RED LIGHT (Reject):**
- Validation phase incomplete
- No clear performance improvement expected
- High complexity, high maintenance
- Distracts from core execution
- Duplicates existing capability

---

## Quarterly Review Process

### End of Q2 2026 (June 30)
**Questions to Answer:**
1. Which strategy has highest win rate?
2. Should we drop any strategy? (If <45% win rate)
3. Should we scale up capital? (If >60% overall)
4. Is Eddie Z worth the subscription? (Needs >50% + >2:1 R:R)
5. Is Chaikin reliable? (Compare to P_115 convergence)
6. Ready for Q3 features? (Baseline established?)

**Decision Matrix:**
```
Strategy Performance -> Action
>70% win rate -> Scale up, add automation
55-70% win rate -> Continue, minor tweaks
45-55% win rate -> Re-evaluate, extended validation
<45% win rate -> Drop or major overhaul
```

### End of Q3 2026 (September 30)
**Questions to Answer:**
1. Did insider data improve win rate?
2. Did 60-min analysis add value?
3. Did distribution day tracking reduce drawdowns?
4. Did Z-Score Council filter improve win rate and/or save time?
5. Should Z-Score be kept, modified, or dropped?
6. Ready for full automation?
7. Portfolio size ready to scale?

---

## Version History

### v1.3 - April 12, 2026
- Added Feature 5 (Q3): Morning Star Pattern — PA6 Integration
- Defined PA6 as first multi-candle PA code (Morning Star)
- Documented ThinkScript detection criteria, scoring impact, and full P_115 workflow integration
- Established PA6+ as multi-candle pattern sub-series (PA7=Evening Star, PA8=Three White Soldiers planned)
- No 27-column schema changes required; Comments field absorbs PA6 code
- Renumbered Q4 features to 6-10 (previously 5-9) to accommodate Q3 Feature 5

### v1.2 - April 8, 2026
- Added Feature 6 (Q4): Python Excel Auto-Logger (Priority 1)
- Added Feature 10 (Q4): Schwab API Auto-Log (Priority 2)
- Renumbered Q4 features: Alerts=7, Dashboard=8, Correlation=9
- Excel Auto-Logger positioned as manual bridge before Schwab API

### v1.1 - February 10, 2026
- Added Z-Score Regime Council Integration as Q3 Priority 4
- Documented 3-phase implementation plan (Pilot -> Filter -> Integration)
- Defined success metrics and decision criteria
- Updated Q3 review questions
- Renumbered Q4 features (5, 6, 7)
- Created companion Z_SCORE_INTEGRATION_SPEC.md

### v1.0 - January 12, 2026
- Initial features roadmap created
- Insider data feature documented (parked from Q1)
- Q1-Q2 validation phase defined
- Q3-Q4 enhancement phases outlined
- Decision framework established

---

## Notes

**Philosophy:**
- "Master one thing before adding another"
- Validate before automating
- Data-driven decisions, not gut feel
- Every feature must improve win rate or reduce time

**Constraints:**
- Q1-Q2: NO new features (validation only)
- Q3: Add features ONLY if baseline proven
- Q4: Automate ONLY if manual process validated

**Success Definition:**
- Not "how many features" but "how consistent the profits"
- A simple system executed well > complex system executed poorly
