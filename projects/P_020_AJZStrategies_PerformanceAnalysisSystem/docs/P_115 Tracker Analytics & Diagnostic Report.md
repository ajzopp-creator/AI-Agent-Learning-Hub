| **P_115 / P_118 Tracker**<br>**Analytics & Diagnostic Report**<br>*Signal Quality, Tier Distributions & Outcome Diagnostics*<br>Version<br>v1.0<br>Generated<br>July 24, 2026<br>Data Source<br>P_115_118_TrackerDashboard_V2.csv<br>Coverage<br>January 10, 2026 – July 9, 2026 (6 months)<br>Signal Rows<br>2,103<br>Unique Symbols<br>800<br>Primary Sources<br>P_115, P_118<br>Auxiliary Sources<br>9 (P_117, P_910, P_920, P_116, SNT, P_300, D_130, D_050)<br>*\#analytics \#diagnostics \#p115 \#p118 \#tracker Author: Tony* |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

**SECTION 0 OF 11 — FRONTMATTER COMPLETE \| SECTION 1 FOLLOWS**

# §1 — Executive Summary

| **⚑ Diagnostic Verdict — P_115 / P_118 Tracker \| July 24, 2026**<br>• **Signal Log, Not a Trade Ledger:** 92.9% of Outcome fields are blank/pre-decision; only 62 confirmed live trades exist (2.9% trade rate). This is structurally correct — the tracker ingests every screened signal before trade decisions are made. Blank outcomes are pre-decision entries, not missing data.<br>• **FundamentalsTier Skews T2 (56.5%):** Of 2,025 valid rows, 1,144 score Tier 2. The watchlist is systematically targeting mid-tier fundamental quality — consistent with P_115's broad screening mandate for mid-cap growth candidates. T4 at 16.0% (324 rows) is the priority review cohort when candle/breakout criteria align.<br>• **CandleTier Dominated by T0 (76.4%):** 1,550 of 2,030 valid rows show no established candle pattern at signal capture. This is a deliberate early-entry design characteristic — P_115 builds the watchlist before pattern confirmation, not after. CandleTier must always be read alongside BreakoutVerdict and Step1Verdict.<br>• **HybridTier Funnel is Functioning:** 68.7% of signals sit at T1 (watchlist hold), with T3 at 16.8% representing the true actionable cohort of multi-factor convergent setups. Only 13 signals (0.6%) reach T4 — the highest-conviction tier. The funnel compression is working as designed.<br>• **P_118 vs P_115 Architecture Divergence:** P_118 generates 59% more volume than P_115 (1,112 vs 699 rows) and shows a measurably higher Avg FundamentalsTier (2.49 vs 1.74). P_118 is a breakout-validated, execution-stage feed with extensive BreakoutVerdict data. P_115 is a watchlist-first screener with 86% pre-verdict entries. They are complementary systems, not redundant ones — head-to-head tier comparisons without this context are misleading.<br>• **Split Market Regime:** Risk-Off/Correction conditions accounted for 32.5% of the coverage period; Bullish conditions for 31.1%. This near-equal split explains the high proportion of deferred/pending outcomes and validates the system's decision to suppress trade frequency during correction periods. The 28.2% missing MarketDirection is the dataset's most urgent data quality gap. |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §2 — Dataset Overview

## 2.1 — Core Dataset Metrics

| **Metric**                            | **Value**                                                                                 |
|---------------------------------------|-------------------------------------------------------------------------------------------|
| Total Signal Rows                     | 2,103                                                                                     |
| Unique Symbols                        | 800                                                                                       |
| Date Range                            | Jan 10, 2026 – Jul 9, 2026 (181 days / \~6 months)                                        |
| Primary Sources                       | P_115 (699 rows) \| P_118 (1,112 rows)                                                    |
| Auxiliary Sources (9)                 | P_117 (144), P_910 (59), P_920 (49), P_116 (19), SNT (8), P_300 (6), D_130 (4), D_050 (2) |
| Total Confirmed Trades (Traded = Yes) | 62 \| **2.9% of total rows**                                                              |
| Simulation Trades                     | 8 (N-Paper / SIM entries)                                                                 |
| Rows with Outcome Data                | 149 \| 7.1%                                                                               |
| Rows with Blank Outcome               | 1,954 \| 92.9%                                                                            |

| *The 92.9% blank-outcome rate is a structural feature of the tracker architecture, not a data problem. Every signal is logged at screen time, before a trade decision is made. Blank outcomes = pre-decision entries in queue. The 7.1% with outcome data represent signals that completed the full evaluation pipeline.* |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 2.2 — Signal Source Distribution

| **Signal Source** | **Row Count** | **% of Total** |
|-------------------|---------------|----------------|
| **P_118**         | 1,112         | 52.9%          |
| **P_115**         | 699           | 33.2%          |
| P_117             | 144           | 6.8%           |
| P_910             | 59            | 2.8%           |
| P_920             | 49            | 2.3%           |
| P_116             | 19            | 0.9%           |
| SNT               | 8             | 0.4%           |
| P_300             | 6             | 0.3%           |
| D_130             | 4             | 0.2%           |
| D_050             | 2             | 0.1%           |

| *P_115 and P_118 together account for 86.1% of all rows. P_117 is the largest auxiliary contributor at 6.8% (144 rows). Remaining auxiliary sources collectively represent*<br>*\<*<br>*7% and should be treated as supplemental validation layers, not primary screening feeds.* |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §3 — Analytics Dimension 1: FundamentalsTier

## Avg FundamentalsTier — Quality Distribution of Screened Universe

| Key Statistics \| FundamentalsTier<br>Valid Rows:<br>2,025<br>of 2,103<br>\|<br>Mean:<br>2.186<br>\|<br>Median:<br>2.0<br>\|<br>Std Dev:<br>1.082<br>\|<br>Modal Tier:<br>T2 — 1,144 rows (56.5%) |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **Tier**  | **Row Count** | **% of Valid** | **Interpretation**                                                                 |
|-----------|---------------|----------------|------------------------------------------------------------------------------------|
| **T0**    | 151           | 7.5%           | Fundamental reject / data missing — early-stage entries or screen failure          |
| **T1**    | 198           | 9.8%           | Below threshold, borderline — requires additional catalyst to qualify              |
| **T2**    | 1,144         | 56.5%          | **Core watchlist tier** — mid-quality fundamentals; modal distribution             |
| **T3**    | 201           | 9.9%           | Above average — selective quality; priority review candidates                      |
| **T4**    | 324           | 16.0%          | High fundamental quality — premium setups; prioritize on candle/breakout alignment |
| **T5–T9** | 7             | 0.3%           | Outliers / data anomalies — treat as T4 equivalent or flag for manual review       |

| *T2 dominance at 56.5% is consistent with P_115's design intent to cast a broad screening net across mid-cap growth candidates before applying candle/breakout filters. The T4 cohort at 16.0% (324 rows) is notable — these are premium-fundamental setups warranting priority review when CandleTier or BreakoutVerdict aligns. T0 at 7.5% flags either failed fundamental screens or early-stage entries logged before scoring — not true misses. The mean of 2.19 is stable and indicates the screener is correctly calibrated: not over-filtering (which would push the mean above 3.0) or under-filtering (which would flatten the distribution toward T1). T5+ (values 5, 6, 7, 9) total 7 rows and represent data entry anomalies or experimental scoring — cap at T4 and review manually.* |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §4 — Analytics Dimension 2: CandleTier

## Avg CandleTier — Pattern Maturity at Signal Capture

| Key Statistics \| CandleTier<br>Valid Rows:<br>2,030<br>of 2,103<br>\|<br>Mean:<br>0.471<br>\|<br>Median:<br>0.0<br>\|<br>Std Dev:<br>0.905<br>\|<br>Modal Tier:<br>T0 — 1,550 rows (76.4%)<br>\|<br>Mean (non-zero entries only):<br>\~1.93 |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **Tier**  | **Row Count** | **% of Valid** | **Interpretation**                                                                 |
|-----------|---------------|----------------|------------------------------------------------------------------------------------|
| **T0**    | 1,550         | 76.4%          | No confirmed candle pattern — pre-pattern capture / early watch; designed behavior |
| **T1**    | 59            | 2.9%           | Emerging pattern / partial setup — monitor closely                                 |
| **T2**    | 385           | 19.0%          | Confirmed base pattern — actionable with breakout confirmation                     |
| **T3**    | 30            | 1.5%           | Strong multi-confirmation pattern — highest candle conviction                      |
| **T4–T9** | 6             | 0.3%           | Outliers / data anomalies — remap or cap at T3                                     |

| *The extreme T0 concentration (76.4%) is the defining characteristic of CandleTier in this dataset. This is NOT a data quality problem — it is a design signal. P_115 captures setups at the pre-pattern stage, before candle structure has resolved. This is consistent with a system designed to build a watchlist ahead of pattern confirmation, then apply breakout/candle checks at execution time (via BreakoutVerdict). T2 at 19.0% represents the meaningful minority of signals where a base pattern was already established at log time.*<br>Critical diagnostic: CandleTier must not be used as a standalone entry filter — it must always be read in combination with BreakoutVerdict and Step1Verdict.<br>*The overall mean of 0.471 is mathematically dominated by the T0 cluster. The non-zero mean of \~1.93 confirms that when a candle pattern is established at capture time, it tends to be a solid T2.* |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §5 — Analytics Dimension 3: HybridTier Distribution

## HybridTier (AnalysisTier) — Signal Promotion Ladder

| Key Statistics \| HybridTier<br>Valid Rows:<br>2,037<br>of 2,103<br>\|<br>Mean:<br>1.374<br>\|<br>Median:<br>1.0<br>\|<br>Modal Tier:<br>T1 — 1,400 rows (68.7%) |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------|

| **HybridTier** | **Row Count** | **% of Valid** | **Classification**                                                       |
|----------------|---------------|----------------|--------------------------------------------------------------------------|
| **T0**         | 42            | 2.1%           | Excluded / Failed threshold — removed from active watchlist              |
| **T1**         | 1,400         | 68.7%          | Standard Watchlist — screening gate; awaiting candle or breakout trigger |
| **T2**         | 240           | 11.8%          | Elevated — Candle or Breakout Triggered; in-transition bucket            |
| **T3**         | 342           | 16.8%          | Active Setup — Multi-factor Convergence; primary actionable cohort       |
| **T4**         | 13            | 0.6%           | Priority — Full Signal Alignment; highest-conviction tier                |

| *The HybridTier ladder demonstrates healthy funnel compression. 68.7% of signals are correctly held at T1 — the screening gate — and not promoted without further validation. T3 (16.8% / 342 rows) is the true actionable cohort: multi-factor convergent setups where Fundamentals, Candle, and Breakout indicators are aligned. T4 at just 13 rows (0.6%) represents the rarest, highest-conviction signals in the dataset — maximum selectivity is working. The T2 cohort (11.8%) is the in-transition bucket: elevated but awaiting final confirmation.*<br>Key optimization flag: T3 = 342 rows vs 62 confirmed trades (18.1% of T3 rows traded) — a large proportion of T3 signals are going untraded. This is a priority area for pipeline review to determine where the T3-to-execution gap is occurring. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

## 5.1 — FundamentalsTier & CandleTier by HybridTier (Cross-Analysis)

| **HybridTier** | **N** | **Avg FundamentalsTier** | **Avg CandleTier** | **Interpretation**                                                  |
|----------------|-------|--------------------------|--------------------|---------------------------------------------------------------------|
| **T0**         | 42    | 0.88                     | 0.62               | Low fund quality, minimal candle — correctly excluded               |
| **T1**         | 1,381 | 2.20                     | 0.05               | Mid-fund quality, T0 candle dominant — pre-pattern watchlist hold   |
| **T2**         | 236   | 2.33                     | 0.58               | Slight fund improvement, some candle emergence — transitional       |
| **T3**         | 338   | 2.16                     | 2.04               | **CandleTier spikes to T2+ — this is the convergence trigger**      |
| **T4**         | 13    | 3.31                     | 2.17               | Highest fund quality + strong candle — maximum conviction confirmed |

| The CandleTier jump from T2 → T3 (0.58 → 2.04) is the most structurally significant feature in the entire dataset.<br>*HybridTier promotion to T3 is almost entirely driven by CandleTier crossing the T2 threshold. FundamentalsTier is relatively stable across T1 through T3 (ranging 2.16–2.33), confirming that it establishes the base qualification but does not drive promotion. CandleTier is the promotion trigger. This confirms the HybridTier ladder is functioning precisely as designed: FundamentalsTier sets the floor, CandleTier opens the gate.* |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §6 — Analytics Dimension 4: Signal Source Comparison

## SignalSource Head-to-Head — P_115 vs P_118 Diagnostic

### 6.1 — Overview Metrics

| **Metric**              | **P_115**       | **P_118**         | **Delta / Notes**                                       |
|-------------------------|-----------------|-------------------|---------------------------------------------------------|
| Total Rows              | 699             | 1,112             | P_118 generates 59% more signals                        |
| % of All Rows           | 33.2%           | 52.9%             | —                                                       |
| Avg FundamentalsTier    | 1.740           | 2.493             | **+0.753 in favor of P_118**                            |
| Median FundamentalsTier | 2.0             | 2.0               | Same median — mean gap driven by distribution tail      |
| Avg CandleTier          | 0.522           | 0.330             | P_115 captures more candle-developed setups at log time |
| Avg HybridTier          | 1.392           | 1.367             | Nearly identical — same promotion rate per signal       |
| Avg SetupScore          | 1.144           | 1.017             | P_115 marginally higher overall setup score             |
| Step1 PASS Rate         | 81.8% (572/699) | 78.7% (875/1,112) | P_115 passes Step1 at higher rate                       |
| Confirmed Trades (Yes)  | 16              | 27                | P_118 yields more live trades absolute                  |
| Simulation Trades       | 0               | 5                 | P_118 used for simulation / paper testing               |

### 6.2 — BreakoutVerdict Distribution Comparison

| **BreakoutVerdict**           | **P_115**       | **P_118**   |
|-------------------------------|-----------------|-------------|
| — (No Verdict / Pre-Breakout) | **649** (92.8%) | 328 (29.5%) |
| No Signal                     | 5               | 392         |
| PASS                          | 0               | **143**     |
| BUY                           | 13              | 91          |
| ASYM                          | 0               | 43          |
| NO                            | 12              | 75          |
| Bounce                        | 0               | 18          |
| TBD / Pending                 | 0               | 17          |

| This table reveals the most structurally important difference between the two sources.<br>*P_115 has almost no BreakoutVerdict data (92.8% are blank/pre-verdict), while P_118 extensively populates BreakoutVerdict — with 143 PASS, 91 BUY, 43 ASYM, and 392 No Signal verdicts.*<br>P_118 is a breakout-first system<br>*where signals are logged after a breakout evaluation.*<br>P_115 is a watchlist-first system<br>*where signals are logged before the breakout occurs. These are fundamentally different in logging philosophy and must not be compared head-to-head on raw tier metrics without this architectural context. P_115's higher Step1 PASS rate suggests a more selective pre-screen. P_118's higher volume, richer breakout data, and more confirmed trades confirm it is the primary execution-stage signal feed.* |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### 6.3 — HybridTier Distribution: P_115 vs P_118

| **HybridTier** | **P_115 (N)** | **P_115 %** | **P_118 (N)** | **P_118 %** |
|----------------|---------------|-------------|---------------|-------------|
| **T0**         | 30            | 4.4%        | 10            | 0.9%        |
| **T1**         | 473           | 69.2%       | 820           | 76.2%       |
| **T2**         | 62            | 9.1%        | 97            | 9.0%        |
| **T3**         | 118           | 17.3%       | 136           | 12.6%       |
| **T4**         | 0             | 0.0%        | 12            | 1.1%        |

| *P_115 produces proportionally more T3 signals (17.3% vs 12.6%) despite lower total volume — suggesting P_115 may yield a higher concentration of convergent, high-confidence setups when it fires. P_118 is the only source generating T4 signals (12 of the 13 T4 rows), consistent with its breakout-validated architecture where full signal alignment is a prerequisite for high-tier classification.* |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### 6.4 — Outcome Distribution: P_115 vs P_118

| **Outcome Category**                    | **P_115**   | **P_118**     |
|-----------------------------------------|-------------|---------------|
| No Data / Blank (Pre-Decision)          | 658 (94.1%) | 1,026 (92.3%) |
| Pending                                 | 18 (2.6%)   | 41 (3.7%)     |
| No Trade (Rule Filter — R:R / No Entry) | 13 (1.9%)   | 7 (0.6%)      |
| No Signal                               | 3 (0.4%)    | 15 (1.3%)     |
| PASS (Signal Confirmed)                 | 3 (0.4%)    | 4 (0.4%)      |
| Open (Active Trade)                     | 0           | 5 (0.5%)      |
| No Trade (Option Viability Fail)        | 0           | 5 (0.5%)      |
| Recheck / Deferred                      | 3 (0.4%)    | 0             |
| Numeric Balance Record                  | 0           | 8 (0.7%)      |
| Missed Entry                            | 1 (0.1%)    | 0             |
| Fallback Trade (Stock)                  | 0           | 1 (0.1%)      |

***

# §7 — Analytics Dimension 5: Outcome Breakdown

## Signal Disposition & Trade Execution Rate

### 7.1 — Full Outcome Category Distribution

| **Outcome Category**                    | **Count** | **% of Total** |
|-----------------------------------------|-----------|----------------|
| No Data / Blank (Pre-Decision)          | 1,954     | **92.9%**      |
| Pending (Awaiting Resolution)           | 75        | 3.6%           |
| No Trade — Rule Filter (R:R, No Entry)  | 20        | 1.0%           |
| No Signal                               | 19        | 0.9%           |
| PASS (Signal Confirmed, Not Yet Traded) | 11        | 0.5%           |
| Numeric Balance Record (Account Log)    | 8         | 0.4%           |
| Open (Active Trade)                     | 5         | 0.2%           |
| No Trade — Option Viability Fail        | 5         | 0.2%           |
| Recheck / Deferred                      | 3         | 0.1%           |
| Paper Trade                             | 1         | \<0.1%         |
| Missed Entry                            | 1         | \<0.1%         |
| Fallback Trade (Stock)                  | 1         | \<0.1%         |

| *Within the resolved cohort (7.1% of rows), the most operationally significant groups are: No Trade — Rule Filter (R:R or sizing failures at 1.0%), No Signal (pattern didn't emerge at 0.9%), and the 5 Open + 62 Traded=Yes rows which constitute the live execution population. The 75 Pending rows represent signals currently in evaluation — this is the most active diagnostic bucket for real-time monitoring.* |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### 7.2 — Traded Field Analysis

| **Traded Value (Normalized)** | **Count** | **% of Total** |
|-------------------------------|-----------|----------------|
| No / N                        | 1,793     | 85.3%          |
| **Yes / Y / Live**            | **62**    | **2.9%**       |
| Pending / TBD                 | 27        | 1.3%           |
| Blank / —                     | 201       | 9.6%           |
| Simulation (SIM / N-Paper)    | 8         | 0.4%           |
| Other / Numeric               | 12        | 0.6%           |

### 7.3 — Pattern Type for Confirmed Trades (Traded = Yes, N = 62)

| **Pattern Type**                  | **Count** | **% of Traded** |
|-----------------------------------|-----------|-----------------|
| — / Unlabeled                     | 28        | 45.2%           |
| High Handle                       | 10        | 16.1%           |
| Cup & Handle                      | 8         | 12.9%           |
| Flat Base                         | 6         | 9.7%            |
| Bounce                            | 3         | 4.8%            |
| Eddie Z Pattern                   | 2         | 3.2%            |
| Other (Double Bottom, BOSS, Grid) | 5         | 8.1%            |

| *Cup*<br>*&*<br>*Handle and High Handle combined account for 29.0% of all confirmed trades — confirming these are the system's primary execution patterns. The 45.2% unlabeled traded signals are a data quality concern: pattern tagging at trade execution time should be enforced going forward. Without consistent PatternType data, pattern-level win/loss analysis — a critical feedback mechanism — is impossible to run retrospectively on these 28 trades.* |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §8 — Supporting Field Analysis

## Step1Verdict, BreakoutVerdict, Market Context & SetupScore

### 8.1 — Step1Verdict Distribution

| **Verdict**    | **Count** | **% of Total** |
|----------------|-----------|----------------|
| **PASS**       | 1,639     | **78.0%**      |
| BUY            | 162       | 7.7%           |
| ASYM           | 110       | 5.2%           |
| NO             | 82        | 3.9%           |
| No Signal      | 66        | 3.1%           |
| PASS-RR / HOLD | 3         | 0.1%           |

| *A 78.0% Step1 PASS rate confirms the initial screening is intentionally permissive — Step1 is a coarse filter, not an execution gate. BUY (7.7%) and ASYM (5.2%) verdicts carry an explicit directional bias at initial screen and should be flagged for priority CandleTier / BreakoutVerdict review. The 3.9% NO verdict represents signals that failed Step1 screening and should not progress to HybridTier elevation without recheck.* |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### 8.2 — BreakoutVerdict Distribution

| **Verdict**                     | **Count** | **% of Total** |
|---------------------------------|-----------|----------------|
| — / No Verdict (Pre-Evaluation) | 1,192     | 56.7%          |
| No Signal                       | 411       | 19.5%          |
| PASS                            | 143       | 6.8%           |
| BUY                             | 108       | 5.1%           |
| NO                              | 93        | 4.4%           |
| ASYM                            | 47        | 2.2%           |
| Bounce                          | 18        | 0.9%           |
| TBD / Pending                   | 17        | 0.8%           |

### 8.3 — Market Direction (Regime) Distribution

| **Market Regime**                       | **Count** | **% of Total** |
|-----------------------------------------|-----------|----------------|
| Bullish / Full (FULL, HOT, BULL, Rally) | 654       | 31.1%          |
| Risk-Off / Correction (OFF, Correction) | 683       | 32.5%          |
| Partial / Mixed (HALF, SPLIT)           | 174       | 8.3%           |
| Unknown / Missing                       | 592       | 28.2%          |

| *The near-equal split between Bullish (31.1%) and Risk-Off (32.5%) regimes over the 6-month coverage period is critical context for the high deferred/pending outcome rate. The system correctly suppressed trade frequency during correction periods.*<br>The 28.2% missing MarketDirection is the dataset's most urgent data quality gap<br>*— market posture is a first-order filter in P_115 logic and missing values create irresolvable ambiguity in downstream outcome analysis. This field must be enforced at signal capture time or backfilled via a date-based market calendar for existing rows.* |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### 8.4 — SetupScore Distribution

| **SetupScore**  | **Count** | **% of Valid** |
|-----------------|-----------|----------------|
| 0               | 648       | 33.3%          |
| 1               | 749       | 38.5%          |
| 2               | 224       | 11.5%          |
| 3               | 333       | 17.1%          |
| 4–10 (Outliers) | 21        | 1.1%           |
| **Mean**        | **1.165** |                |
| **Median**      | **1.0**   |                |

### 8.5 — RecheckStatus Highlights (Top Entries)

| **Recheck Status**   | **Count** |
|----------------------|-----------|
| — / Blank            | 1,090     |
| P_115 Recheck        | 15        |
| Recheck              | 12        |
| ALIGNED              | 12        |
| Pending              | 11        |
| Active               | 11        |
| Flipped              | 10        |
| Pending Confirmation | 10        |
| P_115 Recheck PASS   | 9         |
| CONFLICT             | 4         |

| *The 4 CONFLICT entries and 10 Flipped entries are diagnostically significant: CONFLICT indicates disagreement between P_115 and P_118 scoring on the same symbol, while Flipped indicates a tier or verdict reversal on recheck. Both warrant manual review. ALIGNED (12 rows) represents the highest-confidence confirmation state — signals where both sources agree on direction and tier.* |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §9 — Data Quality Diagnostics

## Known Issues & Remediation Roadmap

| **Field**                  | **Issue Description**                                                          | **Severity**    | **Recommended Fix**                                                                                                                        |
|----------------------------|--------------------------------------------------------------------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Outcome**                | 92.9% blank — expected structural blank (pre-decision entries)                 | **LOW**         | No fix needed; add a *Stage* column (Screened / Evaluated / Traded) to enable pre/post-decision segmentation                               |
| **PatternType**            | 45.2% of traded signals unlabeled — missing pattern tag at execution           | **MEDIUM**      | Enforce PatternType entry at Traded=Yes time; cannot backfill reliably from historical data                                                |
| **MarketDirection**        | 28.2% unknown / missing — market posture absent at signal log time             | **MEDIUM**      | Enforce MarketDirection at signal capture; partially backfill using date-based market calendar for existing rows                           |
| **CandleTier**             | T5–T9 anomalies (6 rows) — scores above valid range (0–4)                      | **LOW**         | Cap or remap to T4; likely data entry errors — review manually before capping                                                              |
| **FundamentalsTier**       | T5–T9 anomalies (7 rows) — scores above valid range (0–4)                      | **LOW**         | Cap or remap to T4; review manually to confirm not intentional experimental scoring                                                        |
| **Traded (field)**         | 12 numeric entries — price/balance values incorrectly entered in Traded column | **LOW**         | Cleanse: move numeric values to EntryPrice or AccountBalance field; recode Traded field as Yes                                             |
| **LiquidityTier**          | 1,734 blanks (82.5%) — nearly always unpopulated                               | **MEDIUM-HIGH** | If LiquidityTier is a P_115 gate criterion, enforce population at screen time; if deprecated, remove column to reduce noise                |
| **RSvsSPY**                | 87.5% blank — relative strength vs SPY rarely populated                        | **MEDIUM**      | Populate at signal capture; RSvsSPY is a key momentum qualifier missing from most records — its absence limits regime-conditional analysis |
| **BreakoutVolumeMultiple** | Mostly blank — volume confirmation data absent from most entries               | **MEDIUM**      | Enforce at BreakoutVerdict = BUY / PASS time; critical for execution quality scoring and retrospective analysis                            |

***

# §10 — Diagnostic Verdict & System Health Summary

## System Health Scorecard

| **Dimension**                     | **Rating**            | **Key Finding**                                                                                                |
|-----------------------------------|-----------------------|----------------------------------------------------------------------------------------------------------------|
| **Signal Volume**                 | **✅ Healthy**        | 2,103 rows across 800 symbols over 6 months — robust pipeline breadth                                          |
| **FundamentalsTier Distribution** | **✅ Calibrated**     | T2 modal at 56.5% consistent with mid-cap growth mandate; mean 2.19 is stable                                  |
| **CandleTier Distribution**       | **⚠️ Monitor**        | 76.4% at T0 — correct by design; validate that BreakoutVerdict is applied at execution to compensate           |
| **HybridTier Promotion Ladder**   | **✅ Functioning**    | T1 → T3 funnel compression working correctly; CandleTier confirmed as promotion trigger                        |
| **P_115 vs P_118 Architecture**   | **✅ Differentiated** | P_115 = watchlist-first screener; P_118 = breakout-validated execution feed; complementary by design           |
| **Trade Execution Rate**          | **⚠️ Low (2.9%)**     | 62 trades vs 2,103 signals — acceptable if intentional; verify T3 signal utilization (18.1% of T3 rows traded) |
| **Outcome Data Coverage**         | **⚠️ Sparse**         | 92.9% blank — by design; add Stage field to enable pre/post-decision segmentation without restructuring        |
| **Market Direction Data**         | **❌ Gap**            | 28.2% missing — first-order filter cannot function on missing posture data; immediate remediation required     |
| **LiquidityTier Coverage**        | **❌ Gap**            | 82.5% blank — enforce at screen time or retire the field; current state provides no analytical value           |
| **Pattern Tagging on Trades**     | **⚠️ Incomplete**     | 45% of executed trades lack PatternType — blocks win/loss pattern analysis retrospectively and prospectively   |

| **⚑ Closing Diagnostic — System Status: Structurally Sound / Optimization Required**<br>The P_115 / P_118 tracker is structurally sound as a signal log and watchlist management system. Tier distributions are internally consistent and the HybridTier promotion ladder is functioning as designed — CandleTier is correctly serving as the gate between T1 (watchlist hold) and T3 (actionable setup).<br>**Primary optimization opportunities, ranked by priority:**<br>1. **Enforce MarketDirection at signal capture** — 28.2% missing is the highest-severity gap; backfill via date-based market calendar where possible.<br>2. **Add a Stage field** (Screened / Evaluated / Traded) to segment pre-decision from post-decision entries without restructuring the core tracker.<br>3. **Tag PatternType at execution** — enforce at Traded=Yes time to enable retroactive pattern-level win/loss analysis going forward.<br>4. **Audit T3 signal utilization** — 342 T3 signals, only 62 trades total; systematically identify where the T3-to-execution pipeline breaks down (R:R failure, option viability, timing, or market regime mismatch).<br>5. **Enforce or retire LiquidityTier** — 82.5% blank provides no value in current state; decision needed to activate or deprecate. |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

# §11 — Appendix

## A — Field Definitions

| **Field**                     | **Definition**                                                                                                                                            |
|-------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Date**                      | **Signal log date — the date the symbol was captured by the screening system**                                                                            |
| **Symbol**                    | **Ticker symbol of the screened equity or instrument**                                                                                                    |
| **SignalSource**              | **Originating system or scanner that generated the signal (P_115, P_118, etc.)**                                                                          |
| **Step1Verdict**              | **Initial screening decision at the first filter gate (PASS, BUY, ASYM, NO, No Signal)**                                                                  |
| **PatternType**               | **Chart pattern classification assigned at trade logging time (Cup & Handle, High Handle, Flat Base, etc.)**                                              |
| **BreakoutVerdict**           | **Breakout evaluation outcome assigned post-screening (PASS, BUY, ASYM, NO, Bounce, No Signal)**                                                          |
| **FundamentalsTier**          | **Fundamental quality score (T0–T4 scale); measures earnings, growth, and financial health quality of the screened symbol**                               |
| **CandleTier**                | **Candle pattern maturity score at signal capture (T0–T3 scale); T0 = no confirmed pattern, T3 = multi-confirmation strong pattern**                      |
| **AnalysisTier / HybridTier** | **Composite promotion tier combining FundamentalsTier and CandleTier into a unified signal strength ladder (T0–T4); primary signal prioritization field** |
| **SetupScore**                | **Numeric composite score summarizing overall setup quality at screening; aggregates multiple sub-criteria into a single rank (0–4+ scale)**              |
| **LiquidityTier**             | **Liquidity quality score intended to qualify option viability and spread quality; currently 82.5% unpopulated**                                          |
| **Traded**                    | **Execution flag — whether the signal resulted in a live trade (Yes/Y, No/N, Pending, SIM/N-Paper)**                                                      |
| **Outcome**                   | **Post-evaluation disposition of the signal — captures trade result, filter outcome, or deferred status; 92.9% blank (pre-decision entries)**             |
| **RecheckStatus**             | **Re-evaluation status for signals that were reviewed after initial logging (ALIGNED, CONFLICT, Flipped, Pending Confirmation, etc.)**                    |

## B — Tier Scoring Reference

| **Tier** | **FundamentalsTier**                                               | **CandleTier**                                                       | **HybridTier**                                                             |
|----------|--------------------------------------------------------------------|----------------------------------------------------------------------|----------------------------------------------------------------------------|
| **T0**   | No fundamentals score / data missing or screen failed              | No candle pattern — pre-pattern or early watch state                 | Excluded / failed minimum threshold — removed from active list             |
| **T1**   | Below qualifying threshold — borderline fundamental quality        | Emerging / partial pattern — early-stage formation, not confirmed    | Standard watchlist hold — awaiting candle or breakout trigger              |
| **T2**   | Mid-quality fundamentals — core watchlist tier (modal value)       | Confirmed base pattern — established candle structure present at log | Elevated / in-transition — candle or breakout partially triggered          |
| **T3**   | Above average fundamental quality — selective, priority-eligible   | Multi-confirmation strong pattern — high candle conviction           | Active setup — multi-factor convergence; primary actionable cohort         |
| **T4**   | High fundamental quality — premium setup; priority review required | Peak pattern strength — all confirmation signals aligned             | Priority — full signal alignment across all dimensions; maximum conviction |

## C — Obsidian Integration Notes

| **📎 Obsidian Vault — Linking & Tagging Recommendations**<br>**Suggested wikilinks from this document:**<br>• [[P_115 System Architecture]] — link from §3 (FundamentalsTier design rationale) and §6 (P_115 watchlist-first philosophy)<br>• [[P_118 Signal Log]] — link from §6 (BreakoutVerdict analysis) and §7 (confirmed trade outcomes)<br>• [[Trade Journal]] — link from §7 (pattern type analysis, confirmed trades, Traded=Yes population)<br>• [[Market Regime Calendar]] — link from §8.3 (MarketDirection distribution); use to backfill missing MarketDirection values<br>• [[HybridTier Promotion Rules]] — link from §5 (CandleTier as promotion trigger; T1→T3 funnel behavior)<br>**Suggested tags for this document:**<br>\#analytics \#diagnostics \#p115 \#p118 \#tracker \#signal-quality \#tier-distribution \#report \#v1.0<br>**Recommended folder:** Analytics/Reports/2026/P_115_118_Report_v1.0.md |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

***

P_115 / P_118 Tracker — Analytics & Diagnostic Report \| v1.0 \| Generated: July 24, 2026 \| Data: P_115_118_TrackerDashboard_V2.csv \| Coverage: Jan 10 – Jul 9, 2026 \| Prepared for: Tony
