<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# P_110_TrueBounceConfirmation_DailyStrict_Chart_V3  , P_110_TradeTheBounceBounce_DailyStrict_Scan_V2   reads watchlist created by P_110_TradeTheBounceSetupScan_v1    Watchlist:P_110_TtradeTheBounceSetup_mmddyy   and You didn't decribe indicators to change for Intraday

Understood. I’ll clean this up so the names and workflow are explicit:

- **Setup scan:** `P_110_TradeTheBounceSetupScan_v1`
- **Setup watchlist:** `P_110_TtradeTheBounceSetup_mmddyy`
- **Strict daily scan:** `P_110_TradeTheBounceBounce_DailyStrict_Scan_V2`
- **Strict daily chart:** `P_110_TrueBounceConfirmation_DailyStrict_Chart_V3`

And for intraday, I’ll spell out the indicator changes so the daily logic and intraday logic do not get mixed.[^1][^2][^3]

## Correct workflow

The clean workflow is:

1. Run `P_110_TradeTheBounceSetupScan_v1` on **daily** bars.[^2]
2. Save the results into the watchlist `P_110_TtradeTheBounceSetup_mmddyy`.[^4][^3]
3. Run `P_110_TradeTheBounceBounce_DailyStrict_Scan_V2` against that watchlist on **daily** bars.[^2]
4. Use `P_110_TrueBounceConfirmation_DailyStrict_Chart_V3` on the chart to verify the confirmation bar visually.[^5][^6]

That is the best way to keep setup discovery separate from confirmation execution.[^7][^8]

## Daily chart settings

For daily charts, the key idea is **structure first** and **confirmation second**. VWAP is usually not the main daily driver, so the daily logic should rely more on support, prior-high reclaim, EMA reclaim, RSI, and volume.[^9][^10][^11]

Recommended daily settings:

- `supportLookback = 5`
- `proximityPercent = 0.50`
- `rsiOversold = 45`
- `volumeMultiplier = 1.1`
- `minRangePercent = 0.4`
- `requireTrendImprovement = yes`
- `requireAboveLongEMA = no`

If the daily scan is too strict, loosen `volumeMultiplier` to 1.0 and `proximityPercent` to 0.75 before changing anything else.[^8][^2]

## Intraday chart settings

For intraday charts, the most important change is that **VWAP becomes relevant** because it is an intraday reference, not a daily one. VWAP can serve as a real-time support/resistance guide on 15-minute or 1-hour charts, and using it in reclaim logic makes the bounce confirmation more meaningful intraday.[^12][^10][^9]

Recommended intraday changes:

- Set aggregation to **15 min** or **1 hour**.
- Change `useVWAP = yes`.
- Lower `supportLookback` to 3 or 5 depending on how noisy the chart is.
- Tighten `proximityPercent` to around 0.25 to 0.40.
- Keep `volumeMultiplier` at 1.2 or raise it to 1.5 for stronger names.
- Optionally lower `rsiOversold` to 40 to 45 for intraday pullbacks.[^13][^9][^8]


## Indicator changes by timeframe

| Element | Daily | Intraday |
| :-- | :-- | :-- |
| VWAP | Usually off or ignored. [^9][^10] | On, and used for reclaim logic. [^9][^10] |
| Support lookback | 5 bars is fine. | 3 to 5 bars is usually better. [^11] |
| RSI threshold | 45 is a good start. | 40 to 45 is better. [^8] |
| Volume requirement | 1.0 to 1.1x average is enough. | 1.2 to 1.5x average is better. [^13][^8] |
| Confirmation | Prior-high reclaim matters most. [^6] | VWAP reclaim or EMA reclaim matters most. [^9][^10] |

## What I would change next

I would make two separate intraday versions:

- **15-minute bounce confirmation** using VWAP reclaim.
- **1-hour bounce confirmation** using EMA reclaim and strong close logic.[^10][^9]

That lets you keep the daily workflow stable while adapting the confirmation bar to the pace of the chart you are trading.[^7][^8]

## Naming cleanup

You also flagged the naming, and that is worth fixing because it reduces confusion later. The name `P_110_TradeTheBounceBounce_DailyStrict_Scan_V2` should probably be shortened to `P_110_TradeTheBounce_DailyStrict_Scan_V2` so the file names are consistent and easier to manage.[^3][^1]

Would you like me to rewrite the **full final package** next with:

1. the cleaned daily setup scan,
2. the strict daily scan,
3. the strict daily chart,
4. and two intraday versions?
<span style="display:none">[^14][^15][^16][^17][^18][^19][^20]</span>

<div align="center">⁂</div>

[^1]: https://toslc.thinkorswim.com/center/howToTos/thinkManual/Left-Sidebar/Watch-Lists

[^2]: https://toslc.thinkorswim.com/center/howToTos/thinkManual/Scan/Stock-Hacker/studyfilters

[^3]: https://www.schwab.com/learn/story/create-and-customize-watchlists-on-thinkorswim

[^4]: https://www.hahn-tech.com/thinkorswim-scans-to-watchlist/

[^5]: https://toslc.thinkorswim.com/center/reference/thinkScript/Constants/PaintingStrategy/PaintingStrategy-BOOLEAN-ARROW-UP

[^6]: https://www.reddit.com/r/thinkorswim/comments/vlccpi/scan_current_price_abovebelow_previous_days/

[^7]: https://www.perplexity.ai/search/4d892d92-3d66-4dc2-815d-0c198b2c057d

[^8]: https://www.perplexity.ai/search/b4945b0f-c4bd-4383-9670-42e2f97bf615

[^9]: https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Fundamentals/vwap

[^10]: https://www.schwab.com/learn/story/how-to-use-volume-weighted-indicators-trading

[^11]: https://www.tradingsim.com/blog/bounce-trading-strategy

[^12]: https://thevwap.com/free-vwap-indicator-thinkorswim/

[^13]: https://usethinkscript.com/threads/relative-volume-strategy-and-momentum-scanner-for-thinkorswim.3002/

[^14]: https://usethinkscript.com/threads/how-to-create-a-custom-watchlist-column-a-tutorial-for-thinkorswim.9709/

[^15]: https://www.reddit.com/r/thinkorswim/comments/1312rob/is_it_possible_to_create_a_scan_that_returns_a/

[^16]: https://tosindicators.com/scans/monthly-watchlist

[^17]: https://www.youtube.com/watch?v=EU8AzpBh0Ng

[^18]: https://tosindicators.com/scans/anchored-vwap-scan

[^19]: https://www.youtube.com/watch?v=jxVI1wxnn9A

[^20]: https://www.youtube.com/watch?v=pRAXNUh2sCw

