# Trade the Bounce Workflow Summary

## Overview

This document summarizes the bounce-trade Thinkorswim work completed in the session, including the progression from an initial multi-timeframe chart study to a two-stage scan workflow and a stricter confirmation-bar chart study. The final process separates **setup discovery** from **entry confirmation**, which is more consistent with support-and-resistance and mean-reversion logic than using a single script for both purposes.[cite:16][cite:20][cite:18]

## What was built

The work produced three practical components:

- A **loose daily setup scan** to find stocks near support with oversold or bounce-potential characteristics.
- A **strict daily confirmation scan** to find only those names printing a valid confirmation bar.
- A **matching chart study** that shows a setup marker and a single confirmation arrow on the bar that confirms the bounce trade.

This approach fits Thinkorswim well because Stock Hacker custom study filters work best when they end in a single true/false plot, and scan aggregation is controlled from the scan filter itself.[cite:39][cite:36][cite:103]

## Key design decisions

Early versions plotted too many arrows because the chart study marked every bar where the bounce condition stayed true. Thinkorswim boolean arrows mark all bars where a boolean plot is true, so a broad state condition naturally creates clusters unless the trigger is narrowed to a single event bar.[cite:51][cite:64]

The solution was to distinguish between:

- **Setup zone**: price is in a location where a bounce could develop.
- **Confirmation bar**: price action shows that buyers have actually regained control.

That separation is more aligned with the trading literature, which treats support as a location and reversal confirmation as a distinct event rather than treating support-touch alone as the trade signal.[cite:16][cite:20][cite:32]

## Final process

### Step 1: Run the loose daily setup scan

Use the loose setup scan first on a **daily** aggregation. Its job is not to produce trade entries; its job is to populate a candidate list of stocks that are near support, have enough range to matter, and show some oversold or stabilizing behavior.[cite:39][cite:98][cite:32]

Recommended filters around the setup scan:

- Last price at least 10.
- Average volume at least 750,000 to 1,000,000.
- Universe set to a liquid stock set such as All Stocks or All Optionable.[cite:43][cite:98]

### Step 2: Save the setup results to a watchlist

Thinkorswim supports using scan results to create dynamic watchlists, which makes it practical to maintain a candidate universe that updates as the daily setup changes.[cite:162][cite:165]

This watchlist becomes the source list for the stricter confirmation scan.

### Step 3: Run the strict confirmation scan on the watchlist

Use the stricter daily confirmation scan against the watchlist created from the setup scan. The strict scan should require the current bar to confirm the bounce, not just sit near support.[cite:39][cite:36]

The final strict daily confirmation logic included:

- Green bar.
- Strong close location within the bar.
- Close above prior close.
- Close above prior high.
- Relative volume support.
- Short-EMA reclaim and trend-improvement checks.[cite:178][cite:32]

This is why the scan may return only one or a few results on a given day; that is expected behavior for a true confirmation scan rather than a broad discovery scan.[cite:43][cite:13]

### Step 4: Verify the signal on the chart study

The chart study should match the strict daily confirmation scan. It should show:

- A **setup dot** when the stock is in a valid bounce zone.
- A **single arrow** on the confirmation bar when the bounce is actually confirmed.

This makes the chart more interpretable than earlier versions that either plotted arrows on every qualifying bar or only plotted arrows on the last bar regardless of event quality.[cite:51][cite:64]

## Daily chart option

The **daily** version is best for swing-style bounce candidates. It should emphasize structure, support proximity, RSI softness, adequate range, and a reclaim bar that closes above the previous day’s high. On daily charts, standard VWAP is usually less useful than it is intraday, so the daily logic is better anchored in price structure, EMA reclaim, and prior-high reclaim rather than VWAP reclaim.[cite:131][cite:141][cite:178]

A good daily use case is building a list after the close or before the next session opens, then checking which names progress from setup to confirmation. This is especially useful when the goal is to avoid low-quality dead-cat bounces inside broader downtrends.[cite:16][cite:20]

### Daily strengths

- Cleaner support/resistance context.
- Fewer false signals caused by noise.
- Better for swing entries and options timing built around multi-day bounces.[cite:32][cite:31]

### Daily trade-off

- Fewer signals.
- Later entries than intraday charts.
- Confirmation can occur after some of the initial move has already happened.[cite:20][cite:135]

## Intraday chart option

The **intraday** version is better for earlier entries and more tactical execution. On intraday charts, VWAP becomes more meaningful because it is an intraday reference level, and requiring price to reclaim VWAP or a short EMA can improve the quality of a bounce confirmation.[cite:131][cite:141][cite:32]

A common intraday workflow is:

1. Use the daily setup scan to generate candidates.
2. Monitor those names on a 15-minute or 1-hour chart.
3. Use a stricter intraday confirmation rule, often including VWAP reclaim, relative volume, and a strong close bar.[cite:39][cite:32]

### Intraday strengths

- Earlier recognition of a real reversal.
- Better use of VWAP as confirmation.
- More precise entries and tighter risk definition.[cite:131][cite:141]

### Intraday trade-off

- More noise.
- More false positives if volume and reclaim logic are too loose.
- Requires more active monitoring.[cite:32][cite:126]

## Recommended operating model

The strongest overall process is a **two-stage daily-to-intraday workflow**:

| Stage | Tool | Purpose |
|---|---|---|
| Candidate discovery | Loose daily setup scan | Find stocks near support with bounce potential.[cite:39] |
| Watchlist creation | Saved dynamic watchlist | Maintain a liquid candidate universe.[cite:162][cite:165] |
| Entry trigger | Strict daily or intraday confirmation scan | Identify the actual confirmation bar.[cite:36][cite:39] |
| Visual validation | Matching chart study | Confirm that the bar is a real reclaim, not just a weak pause.[cite:51] |

This process reflects the user’s stated preference for support, VWAP, RSI, and volume **confluence** rather than a one-indicator trigger.[cite:32][cite:31]

## Practical interpretation

A stock that shows **Setup: YES** and **Confirm: NO** is a valid watchlist candidate but not yet a trade. A stock that shows **Setup: YES** and **Confirm: YES** has printed the bar that passes the stricter confirmation rules and is much closer to the intended bounce-trade definition.[cite:176]

In other words:

- Setup means “watch.”
- Confirmation means “consider action.”

That distinction is the most important outcome of the whole workflow redesign.[cite:32][cite:16]

## Suggested next refinements

Potential future enhancements include:

- A custom watchlist column showing `SETUP`, `CONFIRM`, or `NONE` for faster sorting.[cite:62]
- A separate intraday confirmation scan using VWAP reclaim for 15-minute charts.[cite:131]
- Symbol-universe tuning by sector or liquidity profile, since threshold behavior can vary significantly between small caps, energy names, and large-cap liquid stocks.[cite:20][cite:32]

## Takeaway

The most effective bounce-trade workflow in Thinkorswim is not a single all-purpose script. It is a layered process: a loose setup scan to discover candidates, a strict confirmation scan to identify the real trade bar, and a chart study that visually marks setup versus confirmation. That structure is both operationally practical in Thinkorswim and conceptually closer to support/resistance and mean-reversion research than the earlier “many arrows” versions.[cite:39][cite:16][cite:20]
