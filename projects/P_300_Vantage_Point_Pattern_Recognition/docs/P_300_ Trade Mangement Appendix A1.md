<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# .BAC260618C52.5  (Replacing \#1006220058453) SELL -8 BAC 100 18 JUN 26 52.5 CALL MKT GTC TRG BY \#1006142400348 OCO \#1006142400349 WHEN BAC MARK AT OR BELOW 51.20 [TO CLOSE] I have this as A condition in my stop order. The option keeps dropping in value. But the stop order Hi I think I'll pull out 5120. So I am losing money and not stopping out. How I avoid this in the future?.

Your stop is behaving like a **stop-market** on the option, so once the trigger condition is met it can sell at the best available bid, which may be far below the stop price in a thin or fast-moving option market. That means the option can keep losing value even if the underlying never cleanly trades through your ideal exit, because the trigger and the actual fill are not the same thing.[^1_1]

## What happened

- You used a conditional trigger on BAC at or below 51.20 to close the call, but the option itself can still gap, slide, or trade with a wide spread before the order converts to a market sell.[^1_1]
- In illiquid or fast options, a stop-market often fills worse than the stop level because the order hits whatever bid exists at that moment.[^1_1]
- So the “stop” is not a guaranteed exit price; it is only the point where the market sell is released.[^1_1]


## How to avoid it

- Use a **stop-limit** instead of a stop-market if you want price control, but accept the risk of not getting filled at all.[^1_1]
- If the option is thin, consider exiting with a manual limit order or a mental stop rather than relying on a hard stop in the option itself.[^1_1]
- Set the exit based on the option’s liquidity, not just the stock trigger; wide spreads mean more slippage risk.[^1_1]
- Avoid moving the stop too close to the current price during the day, because a small wiggle can trigger a bad fill.[^1_1]


## Practical setup

1. Pick a max loss before entry.
2. Use a stop-limit with a limit price you can tolerate.
3. If the contract is illiquid, reduce size or choose a more liquid strike/expiration.
4. For active monitoring, use a mental stop and place a limit sell near the bid when the trigger hits.[^1_1]

## Example

If your stock trigger is 51.20 but the option spread is wide, a stop-market can dump you at a much lower option price than expected. A stop-limit gives you a floor, such as “trigger at 51.20, do not sell below my chosen limit,” which prevents a terrible fill but may leave you still holding the position.[^1_1]

The core fix is to stop thinking of the trigger as the exit price and start treating it as only an alert that the order should be managed.[^1_1]
<span style="display:none">[^1_2][^1_3][^1_4][^1_5]</span>

<div align="center">⁂</div>

[^1_1]: what-is-the-best-method-to-det-M22ZPhwzRNm.XyfC57DXXQ.md

[^1_2]: here-is-the-trading-plan-pleas-BRV29rK.SKq.FNxBZbQy7g.md

[^1_3]: market-direction-exposure-40-6-xq9kjyOsSfi9rgTKX5xn_g.md

[^1_4]: we-are-in-section-3-please-rev-TZnScr8VRLqkV4vGEWh7dg.md

[^1_5]: i-have-built-a-trading-plan-th-Kcq7qxjdQFm8AZmd7gl_3w.md


---

# How do I determine if a stock is illiquid?

A stock is usually **illiquid** when it trades infrequently, has a wide bid-ask spread, and has limited depth at the inside market.[^2_1][^2_2]

## What to check

- **Average daily volume:** Low volume is the easiest red flag. Stocks with very low daily shares traded are harder to enter and exit without moving the price.[^2_3][^2_1]
- **Bid-ask spread:** A wide spread usually means poor liquidity. Tight spreads suggest more active trading and easier execution.[^2_4][^2_1]
- **Market depth / size:** If there are only a few shares available at the bid and ask, the stock is more likely illiquid.[^2_5][^2_1]
- **How often it trades:** If prints are sparse or it goes long periods without trades, that is another sign.[^2_2][^2_1]


## Practical rule

A quick screen is:

- Low average volume.
- Wide spread relative to price.
- Small size at bid and ask.
- Large price jumps from modest order size.[^2_6][^2_1]


## Simple example

If a \$2 stock has a \$1.98 bid and \$2.05 ask, that spread is large enough to be a warning sign. If you also see only a few hundred or a few thousand shares traded per day, it is very likely illiquid.[^2_1][^2_2]

## For your options problem

For options, the same idea applies: look at option volume, open interest, bid-ask spread, and quoted size. High volume and open interest with a tight spread usually means the contract is more liquid.[^2_7][^2_8][^2_5]

A useful rule for trading is: if the spread is wide enough that your round-trip cost is a meaningful chunk of the trade, treat it as illiquid and use limit orders instead of marketable exits.[^2_9][^2_6]
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15]</span>

<div align="center">⁂</div>

[^2_1]: https://trendspider.com/learning-center/what-is-liquidity-in-stocks-liquid-vs-illiquid-stocks/

[^2_2]: https://fyers.in/blog/what-are-illiquid-stocks/

[^2_3]: https://www.stockgro.club/blogs/stock-market-101/what-is-illiquid-stocks/

[^2_4]: https://www.chartguys.com/articles/bid-ask-spread

[^2_5]: https://www.tradingblock.com/blog/options-liquidity

[^2_6]: https://journalplus.co/mistakes/trading-illiquid-markets

[^2_7]: https://tackletrading.com/options-101-bidask-open-interest-and-volume/

[^2_8]: https://www.moomoo.com/us/learn/detail-options-volume-vs-open-interest-117044-240246026

[^2_9]: https://www.great-option-trading-strategies.com/trading-illiquid-options.html

[^2_10]: https://www.investopedia.com/ask/answers/050615/what-difference-between-open-interest-and-volume.asp

[^2_11]: https://www.heygotrade.com/en/blog/options-liquidity-explained/

[^2_12]: https://www.tradingsim.com/blog/illiquid-stocks

[^2_13]: https://navi.com/blog/illiquid-stocks/

[^2_14]: https://www-2.rotman.utoronto.ca/~wei/research/JBF_2010.pdf

[^2_15]: https://www.5paisa.com/stock-market-guide/stock-share-market/what-are-illiquid-stock


---

# I usually use the rule. of less than 10%. to buy the stock. For a bid-ask spread. Using the mark Mark value.

Using a rule like “spread less than 10%” is a reasonable **screen**, but it should be based on the spread relative to the mid or ask price, not just the raw difference.[^3_1][^3_2]

## How to measure it

A common formula is:

$$
\text{Spread \%} = \frac{\text{Ask} - \text{Bid}}{\text{Ask}} \times 100
$$

Some traders use midpoint instead of ask, but the main idea is the same: you want the spread to be small compared with the price.[^3_3][^3_4][^3_1]

## How to use your 10% rule

- If the spread is under 10% of the option price, it is usually more tradable than something wider.[^3_5][^3_6]
- If the spread is over 10%, the trade cost starts to become meaningful, especially on short-term trades.[^3_7][^3_8]
- For stocks, a 10% spread is often a sign of poor liquidity unless the stock is very cheap.[^3_9][^3_10]


## Important nuance

Your “mark” is just the midpoint or broker estimate, not a guaranteed executable price.[^3_11][^3_4]
So a stock or option can look cheap on the mark, but if the bid is much lower, your real exit may be worse than the mark suggests.[^3_12][^3_11]

## Practical rule

A better habit is:

- Check the spread percentage.
- Check actual volume and depth.
- Prefer liquid names where the spread is tight enough that round-trip friction is small.[^3_4][^3_13][^3_12]

For options, I would be especially cautious once the spread gets into double-digit percentages, because that often means you are paying too much friction to enter and exit.[^3_6][^3_7]
<span style="display:none">[^3_14][^3_15][^3_16]</span>

<div align="center">⁂</div>

[^3_1]: https://www.ig.com/en/trading-strategies/bid-ask-spread--what-is-it-and-how-does-it-work--250207

[^3_2]: https://www.stockopedia.com/ratios/bid-ask-spread-5063/

[^3_3]: https://www.home.saxo/learn/guides/trading-strategies/bid-vs-ask-price

[^3_4]: https://en.wikipedia.org/wiki/Bid–ask_spread

[^3_5]: https://www.reddit.com/r/options/comments/5ipexq/how_much_bidask_spread_is_tolerable/

[^3_6]: https://www.chaimekstein.com/blog/understanding-the-bid-ask-spread-in-options-trading

[^3_7]: https://wandererfinancial.com/the-bid-ask-spread/

[^3_8]: https://www.bankrate.com/investing/what-is-bid-ask-spread/

[^3_9]: https://www.heygotrade.com/en/blog/what-is-bid-ask-spread/

[^3_10]: https://smartasset.com/investing/bid-ask-spread-2

[^3_11]: https://www.investopedia.com/terms/b/bid-askspread.asp

[^3_12]: https://www.chartguys.com/articles/bid-ask-spread

[^3_13]: https://trendspider.com/learning-center/what-is-liquidity-in-stocks-liquid-vs-illiquid-stocks/

[^3_14]: https://www.sciencedirect.com/science/article/pii/S0304405X21001458

[^3_15]: https://www.reddit.com/r/algotrading/comments/qdul1h/appropriate_price_under_the_spread_of_bid_and_ask/

[^3_16]: https://www.linkedin.com/pulse/bid-price-vs-ask-spread-liquidity-trading-lhcef


---

# Alternatives to bid-ask spread for liquidity checks

Yes—besides bid-ask spread, the most useful liquidity checks are **average daily volume, order-book depth, and for options, volume plus open interest**.[^4_1][^4_2][^4_3]

## Better liquidity checks

- **Average Daily Volume (ADV):** Higher ADV usually means easier execution and less price impact.[^4_2][^4_4]
- **Order-book depth:** Look at how many shares are sitting at the bid and ask near the top of the book; shallow size often means poor liquidity.[^4_5][^4_1]
- **Trade frequency:** If shares print regularly throughout the day, liquidity is generally better than a name that trades in bursts.[^4_1]
- **Relative volume:** Compare today’s volume to its normal average; weak participation can signal thin trading.[^4_6]


## For options

- **Volume:** More contracts traded today usually improves fill quality.[^4_7][^4_8]
- **Open interest:** Higher open interest suggests a larger pool of active contracts and better depth.[^4_9][^4_10]
- **Quoted size:** Contracts available at the bid and ask matter as much as price spread.[^4_8]
- **Slippage behavior:** If the contract moves sharply when you place even a small order, it is effectively illiquid.[^4_3][^4_5]


## Practical screening rule

A good workflow is:

1. Check ADV.
2. Check whether quotes update actively during the session.
3. Check size at the inside market.
4. For options, confirm volume and open interest are healthy.[^4_2][^4_9][^4_1]

## Rule of thumb

If a stock has high volume but very shallow book depth, it may still be hard to trade size cleanly. If an option has good open interest but no current volume, it can still be slow to fill intraday.[^4_10][^4_8][^4_3]

For your trading style, the best non-spread filter is probably **volume plus depth**, and for options, add **open interest** as a secondary check.[^4_9][^4_1]
<span style="display:none">[^4_11][^4_12][^4_13][^4_14][^4_15]</span>

<div align="center">⁂</div>

[^4_1]: https://bookmap.com/blog/evaluating-stock-liquidity-what-every-trader-should-know

[^4_2]: https://www.northstarrisk.com/average-daily-volume

[^4_3]: https://blog.traderspost.io/article/identifying-options-with-high-open-interest-and-volume

[^4_4]: https://www.investing.com/academy/analysis/average-daily-volume-definition/

[^4_5]: https://simpleswap.io/blog/liquidity-crypto-metrics-reading-order-books-market-depth-and-volume

[^4_6]: https://tradefundrr.com/market-liquidity/

[^4_7]: https://www.sophie-ai-finance.com/articles/decoding-options-market-volume-open-interest-analysis

[^4_8]: https://www.tradingblock.com/blog/options-liquidity

[^4_9]: https://steadyoptions.com/articles/options-volume-vs-open-interest-explained-r780/

[^4_10]: https://www.investopedia.com/ask/answers/050615/what-difference-between-open-interest-and-volume.asp

[^4_11]: https://www.reddit.com/r/Trading/comments/ybdyya/metrics_that_measure_liquidity_other_than_bidask/

[^4_12]: https://www.proshares.com/globalassets/proshares/commentary-pdfs/analyzing-etf-liquidity_beyond-bid-ask-spread.pdf

[^4_13]: https://revfin.org/what-are-the-best-liquidity-proxies-for-global-research/

[^4_14]: https://rpc.cfainstitute.org/research/cfa-digest/2015/02/a-practical-approach-to-liquidity-calculation-digest-summary

[^4_15]: https://www.cmegroup.com/articles/2025/reassessing-liquidity-beyond-order-book-depth.html

