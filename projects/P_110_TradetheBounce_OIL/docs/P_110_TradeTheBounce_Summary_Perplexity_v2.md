# Trade the Bounce Workflow — Merged Reference Guide

## Overview

This document combines the earlier workflow summary with the Version 2 package details into a single reference guide for a Thinkorswim bounce-trade process. The final model separates **setup discovery** from **entry confirmation**, then maps those steps to named scans, watchlists, and chart studies so the workflow is practical to run and easy to maintain.

## What was built

The merged workflow produces five practical components:

-   A **daily setup scan** for identifying bounce candidates near support.
-   A **strict daily confirmation scan** for identifying the bar that confirms the bounce.
-   A **strict daily chart study** that visually matches the daily confirmation scan.
-   A **15-minute intraday confirmation chart** for VWAP-sensitive execution.
-   A **1-hour intraday confirmation chart** for slower tactical confirmation.

This approach fits Thinkorswim well because Stock Hacker custom study filters work best when they end in a single true/false plot, and scan aggregation is controlled from the scan filter itself.[cite:39][cite:36][cite:103]

## Key design decisions

Early versions plotted too many arrows because the chart study marked every bar where the bounce condition stayed true. Thinkorswim boolean arrows mark all bars where a boolean plot is true, so a broad state condition naturally creates clusters unless the trigger is narrowed to a single event bar.[cite:51][cite:64]

The solution was to distinguish between:

-   **Setup zone**: price is in a location where a bounce could develop.
-   **Confirmation bar**: price action shows that buyers have actually regained control.

That separation is more aligned with the trading literature, which treats support as a location and reversal confirmation as a distinct event rather than treating support-touch alone as the trade signal.[cite:16][cite:20][cite:32]

## Package names used in the final workflow

The final workflow uses the following package names: **P_110_TradeTheBounceSetupScan_v1** for the daily setup scan, **P_110_TradeTheBounceBounce_DailyStrict_Scan_V2** for the strict daily confirmation scan, **P_110_TrueBounceConfirmation_DailyStrict_Chart_V3** for the matching daily chart study, and corresponding intraday chart studies for 15-minute and 1-hour confirmation. The daily setup scan feeds a saved watchlist named **P_110_TtradeTheBounceSetup_mmddyy**, which then serves as the source list for the stricter confirmation workflow.

## Final process

### Step 1: Run the loose daily setup scan

Use **P_110_TradeTheBounceSetupScan_v1** on a **daily** aggregation to generate candidate names for the saved watchlist **P_110_TtradeTheBounceSetup_mmddyy**. Its role is to find stocks near support with bounce potential, not to declare a finished entry signal.

Recommended filters around the setup scan:

-   Last price at least 10.
-   Average volume at least 750,000 to 1,000,000.
-   Universe set to a liquid stock set such as All Stocks or All Optionable.[cite:43][cite:98]

### Step 2: Save the setup results to a watchlist

Save the setup results into a dynamic watchlist named **P_110_TtradeTheBounceSetup_mmddyy**. This watchlist becomes the controlled candidate universe for the strict daily confirmation scan and any intraday chart review.

### Step 3: Run the strict confirmation scan on the watchlist

Run **P_110_TradeTheBounceBounce_DailyStrict_Scan_V2** against the setup watchlist to find only those names printing a valid daily confirmation bar. This strict scan is intended to identify the reclaim bar, not just a stock that continues to sit near support.

The final strict daily confirmation logic included:

-   Green bar.
-   Strong close location within the bar.
-   Close above prior close.
-   Close above prior high.
-   Relative volume support.
-   Short-EMA reclaim and trend-improvement checks.[cite:178][cite:32]

This is why the scan may return only one or a few results on a given day; that is expected behavior for a true confirmation scan rather than a broad discovery scan.[cite:43][cite:13]

### Step 4: Verify the signal on the chart study

Use **P_110_TrueBounceConfirmation_DailyStrict_Chart_V3** on the chart so the visual marker appears on the same bar the strict daily scan would accept. For tactical execution, use the intraday chart studies to look for VWAP- or EMA-based reclaim confirmation after a symbol has already qualified as a daily setup candidate.

-   A **setup dot** when the stock is in a valid bounce zone.
-   A **single arrow** on the confirmation bar when the bounce is actually confirmed.

This makes the chart more interpretable than earlier versions that either plotted arrows on every qualifying bar or only plotted arrows on the last bar regardless of event quality.[cite:51][cite:64]

## Daily chart option

The **daily** version is best for swing-style bounce candidates. It should emphasize structure, support proximity, RSI softness, adequate range, and a reclaim bar that closes above the previous day’s high. On daily charts, standard VWAP is usually less useful than it is intraday, so the daily logic is better anchored in price structure, EMA reclaim, and prior-high reclaim rather than VWAP reclaim.[cite:131][cite:141][cite:178]

A good daily use case is building a list after the close or before the next session opens, then checking which names progress from setup to confirmation. This is especially useful when the goal is to avoid low-quality dead-cat bounces inside broader downtrends.[cite:16][cite:20]

### Daily strengths

-   Cleaner support/resistance context.
-   Fewer false signals caused by noise.
-   Better for swing entries and options timing built around multi-day bounces.[cite:32][cite:31]

### Daily trade-off

-   Fewer signals.
-   Later entries than intraday charts.
-   Confirmation can occur after some of the initial move has already happened.[cite:20][cite:135]

## Intraday chart option

The **intraday** version is better for earlier entries and more tactical execution. On intraday charts, VWAP becomes more meaningful because it is an intraday reference level, and requiring price to reclaim VWAP or a short EMA can improve the quality of a bounce confirmation.[cite:131][cite:141][cite:32]

A common intraday workflow is:

1.  Use the daily setup scan to generate candidates.
2.  Monitor those names on a 15-minute or 1-hour chart.
3.  Use a stricter intraday confirmation rule, often including VWAP reclaim, relative volume, and a strong close bar.[cite:39][cite:32]

### Intraday strengths

-   Earlier recognition of a real reversal.
-   Better use of VWAP as confirmation.
-   More precise entries and tighter risk definition.[cite:131][cite:141]

### Intraday trade-off

-   More noise.
-   More false positives if volume and reclaim logic are too loose.
-   Requires more active monitoring.[cite:32][cite:126]

## Recommended operating model

The strongest overall process is a **two-stage daily-to-intraday workflow**:

| Stage               | Tool                                       | Purpose                                                                 |
|---------------------|--------------------------------------------|-------------------------------------------------------------------------|
| Candidate discovery | Loose daily setup scan                     | Find stocks near support with bounce potential.[cite:39]                |
| Watchlist creation  | Saved dynamic watchlist                    | Maintain a liquid candidate universe.[cite:162][cite:165]               |
| Entry trigger       | Strict daily or intraday confirmation scan | Identify the actual confirmation bar.[cite:36][cite:39]                 |
| Visual validation   | Matching chart study                       | Confirm that the bar is a real reclaim, not just a weak pause.[cite:51] |

This process reflects the user’s stated preference for support, VWAP, RSI, and volume **confluence** rather than a one-indicator trigger.[cite:32][cite:31]

## Practical interpretation

A stock that shows **Setup: YES** and **Confirm: NO** is a valid watchlist candidate but not yet a trade. A stock that shows **Setup: YES** and **Confirm: YES** has printed the bar that passes the stricter confirmation rules and is much closer to the intended bounce-trade definition.[cite:176]

In other words:

-   Setup means “watch.”
-   Confirmation means “consider action.”

That distinction is the most important outcome of the whole workflow redesign.[cite:32][cite:16]

## Suggested next refinements

Potential future enhancements include:

-   A custom watchlist column showing `SETUP`, `CONFIRM`, or `NONE` for faster sorting.[cite:62]
-   A separate intraday confirmation scan using VWAP reclaim for 15-minute charts.[cite:131]
-   Symbol-universe tuning by sector or liquidity profile, since threshold behavior can vary significantly between small caps, energy names, and large-cap liquid stocks.[cite:20][cite:32]

## Code Package Appendix

This appendix consolidates the script package names into one place so the main workflow stays readable while the implementation references remain easy to find.

-   **P_110_TradeTheBounceSetupScan_v1** — Daily setup scan used to discover bounce candidates near support.
-   **P_110_TtradeTheBounceSetup_mmddyy** — Dynamic watchlist populated from the daily setup scan results.
-   **P_110_TradeTheBounceBounce_DailyStrict_Scan_V2** — Strict daily confirmation scan used to find the reclaim bar.
-   **P_110_TrueBounceConfirmation_DailyStrict_Chart_V3** — Daily chart study aligned with the strict daily confirmation logic.
-   **15-minute intraday confirmation chart study** — Tactical intraday chart for earlier VWAP- or EMA-based confirmation.
-   **1-hour intraday confirmation chart study** — Slower intraday confirmation view for tactical execution and validation.

## Takeaway

The most effective bounce-trade workflow in Thinkorswim is not a single all-purpose script. It is a layered process: a loose setup scan to discover candidates, a strict confirmation scan to identify the real trade bar, and a chart study that visually marks setup versus confirmation. That structure is both operationally practical in Thinkorswim and conceptually closer to support/resistance and mean-reversion research than the earlier “many arrows” versions.[cite:39][cite:16][cite:20]
