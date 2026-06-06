TRADE MANAGEMENT FRAMEWORK v1.2
Council-Integrated Master Framework — May 2026
Universal post-entry rules for all P_115 framework strategies

Purpose & Scope
This framework governs everything that happens after STEP 2 sizing produces a Traded=Y row. Entry signal logic lives in each strategy guide, and position sizing math lives in the sizing reference document. Strategy-specific overrides remain in each system’s “Trade Management Overrides” section.

This version merges the original lifecycle structure with council-driven decision roles, regime awareness, macro guardrails, liquidity filters, and behavioral controls.

Council Roles
01 — The Quant Strategist
Focus: downside protection, risk architecture, volatility regimes, drawdown control.

Responsibilities:

Regime detection.

ATR expansion monitoring.

Portfolio heat analysis.

Stop architecture validation.

Risk-to-reward integrity checks.

Decision weight:

Can block entries when risk structure is weak, volatility is unstable, or stop logic is invalid.

02 — The Macro Economist
Focus: liquidity, credit, global macro cycles.

Responsibilities:

Liquidity backdrop.

Fed posture and rate expectations.

Credit spreads and stress indicators.

Dollar trend and cross-asset flows.

Sector-level macro alignment.

Decision weight:

Can freeze new entries around macro events or when macro conditions are clearly hostile.

03 — The Momentum & Tape Reader
Focus: upside asymmetry, continuation behavior, price-action psychology.

Responsibilities:

Relative strength.

Breakout quality.

Trend continuation confirmation.

Tape strength and closing behavior.

Power-trend validation.

Decision weight:

Can block entries when price action is weak, choppy, or not confirming the setup.

04 — The Risk Manager
Focus: capital preservation, execution discipline, position control.

Responsibilities:

Position sizing discipline.

Partial-fill handling.

Stop movement rules.

Cooldown enforcement.

Risk drift prevention.

Decision weight:

Can block any action that increases risk beyond the approved plan.

05 — The Behavioral Judge
Focus: rule adherence, emotional discipline, decision quality.

Responsibilities:

Override discipline.

Process consistency.

“Do not force trades” enforcement.

Lesson capture and review.

Prevention of revenge trading and impulsive changes.

Decision weight:

Can veto entries or exits that are emotional rather than rule-based.

Council Decision Process
Before any new entry or management override, the Council should answer these questions:

Is the setup technically valid?

Is the risk structure acceptable?

Is the macro backdrop supportive?

Is the tape confirming?

Is the trade being managed according to plan?

Suggested outcome states:

Approve — all critical roles pass.

Approve with caution — one role flags a non-blocking concern.

Block — any critical risk, macro, or tape failure.

Override required — manual approval needed from Tony.

A trade should not proceed if any blocking role identifies a major failure in regime, macro, tape, or risk structure.

Stage 1 — Pre-Entry Validation
1.1 Signal Durability Check
Re-run STEP 1 using the latest chart data. If BUY/ASYM flips to No Signal:

Update RecheckStatus="Flipped" and Outcome="Not Taken".

Log the flip price and reason.

Skip entry and do not substitute another ticker.

1.2 Cash Re-Confirm
Verify Tony’s cash balance has not changed. If buying power has dropped below the STEP 2 value, re-run sizing using the smaller amount.

1.3 Posture Re-Read
Re-read P_010_RiskConfig.json. If risk_mode changes to OFF or CORRECTION:

Halt entry.

Request Tony’s confirmation.

Do not auto-resize.

1.4 Spread Sanity Check
For options, if spread exceeds 10% of mid at the moment of entry:

Abort.

Wait for tighter pricing or fall back to stock.

1.5 Macro Event Guardrail
If CPI, FOMC, or NFP is within 24 hours:

Freeze entry.

Require explicit override.

1.6 Sector Liquidity Check
If the sector ETF is showing a down day with relative volume greater than 2x average:

Freeze entry.

Require explicit override.

1.7 Volatility and Regime Check
The Quant Strategist reviews regime, ATR expansion, and portfolio heat before approval.

If volatility is expanding too quickly or portfolio heat is elevated, the trade should be blocked or resized only by explicit approval.

1.8 Pre-Entry Output
Use a single-line confirmation:

text
PRE-ENTRY [TICKER] OK | Signal=[BUY/ASYM] | Cash=$X,XXX | Posture=[mode] | Spread=X.X% | Macro=[Clear] | Sector=[Clear] | Regime=[Clear] | Proceed
Stage 2 — Entry Execution
2.1 Order Type
Default order type is limit:

Stock: last printed price + 1 tick.

Options: mid + $0.01.

Never use a market order for entry.

2.2 Fill Window
Allow 5 minutes for fill:

Stock: re-quote at last + 2 ticks if needed; abort after 10 minutes total if still unfilled.

Options: re-quote at mid; abort after 10 minutes total if still unfilled.

2.3 Partial-Fill Handling
If the position fills partially:

Accept the partial fill.

Record actual filled quantity.

Recalculate risk percentage.

Do not re-enter later in the same session to complete the size.

2.4 Entry Logging
On fill, populate:

Traded=Y

EntryPrice

TPLevel

SLLevel

StopLevel

RiskPct

Use the actual fill price, or VWAP if multiple fills occurred.

Stage 3 — Active Management
3.1 Default Exit Structure
The default structure is two tranches:

T1: 50%.

T2: 50% with trailing stop.

3.2 Stop Adjustment Rules
Move to break-even at +1R.

After T1 hits, trail the remaining half by 1x weekly ATR below the highest close since entry.

Stops only move toward profit.

Never widen a stop.

3.3 Add-To Prohibition
Adding to a winning position is a separate trade and requires its own STEP 1, STEP 2, and tracker row.

3.4 Time Stops
Stock: no time stop, chart drives exit.

Long options: close at 21 DTE.

Credit spreads: close at 50% max profit or 21 DTE, whichever comes first.

3.5 Mid-Trade Posture Flip
If risk_mode flips to OFF mid-trade:

Tighten stops to break-even or current support, whichever is tighter.

Do not panic-exit.

Block all new entries until posture recovers.

3.6 Earnings Approach
More than 5 sessions out: hold normally.

3–5 sessions out: tighten stops; for options, close 50%.

2 or fewer sessions: close full position or require explicit override for stock; close full options position.

3.7 Manual Exit Triggers
Exit immediately if any of the following occur:

Pattern invalidation.

Material news.

Gap down greater than 5% on no news.

Sector ETF breaks below the 200-MA on heavy volume.

Stage 4 — Exit Execution
4.1 T1 Hit Procedure
Sell 50% at T1 or better.

Move stop on the remainder to break-even.

Activate weekly ATR trailing stop.

Mark outcome as T1 Hit (Partial).

4.2 T2 Hit Procedure
Sell remaining 50% at T2 or better.

Mark outcome as T2 Hit.

Calculate realized R:R using the original stop, not the moved stop.

4.3 SL Hit Procedure
Sell remaining position at market or limit, based on liquidity.

Mark outcome as SL Hit.

No second-guessing.

Apply 5-session cooldown on that ticker.

4.4 Trailing Exit Procedure
When the trailing stop on the back half triggers:

Exit at market open next session.

Mark outcome as Trail Exit.

Log trail high and exit price.

4.5 Options Exit Specifics
Every options exit logs both stock price and option price using the delta at exit.

Stage 5 — Post-Trade Review
5.1 Outcome Logging
Immediately on close, update:

Outcome.

RecheckStatus.

Comments with exit price(s), realized R:R, and lesson if applicable.

5.2 Realized R:R Calculation
Always reference the original stop. A trade that reached break-even after T1 still keeps its earned R from T1; a trade that scratched at break-even without hitting T1 is a 0R result.

5.3 Cooldown Rules
SL Hit: 5 sessions on the same ticker.

Manual Exit due to pattern fail: 10 sessions on the same ticker.

Three consecutive SL hits across the portfolio: halt new entries for 1 session and review process.

5.4 Lessons Captured
If the trade reveals a process gap, prefix the comment with LESSON: and review it in the weekly framework update.

5.5 Drawdown Awareness
If portfolio drawdown crosses -10% from peak, trigger a posture review independent of P_010.

Override Hierarchy
When rules conflict, use this order:

Hard risk blocks.

Macro and event freezes.

Council veto.

Strategy-specific overrides.

Default framework rules.

Recommended strategy override template:

text
## Trade Management Overrides (vs Framework v1.2)

**Stage 1 — Pre-Entry:** [overrides or "None"]
**Stage 2 — Entry:** [overrides or "None"]
**Stage 3 — Active Management:** [overrides or "None"]
**Stage 4 — Exit:** [overrides or "None"]
**Stage 5 — Post-Trade:** [overrides or "None"]

**Council Notes:** [which roles require different handling]
**Rationale:** [why this strategy needs different treatment]
Version History
Version	Date	Author	Notes
1.2	2026-05-04	Tony / Claude	Council-integrated merge of v1.0 and v1.1 with unified lifecycle, regime controls, macro guardrails, and behavioral checks.
Related Docs
THE-STOCK-MARKET-DECISION-COUNCIL.md — role structure and decision logic.

POSITION_SIZING_THREE_GATE_REFERENCE.md — sizing math.

OPTIONS_RISK_METHODOLOGY.md — chart-based vs risk-budget-first stops.

Tracker_Log_Schema_v9_4_0_1.md — tracker schema.

SESSION_INITIALIZATION_PROMPT.md — INIT and posture re-read rules.

If you want, I can turn this into a tighter “production” version with cleaner wording, stronger section numbering, and zero duplication so it reads like a final internal standard.

I like the condensed Idea Can You identify what can be automated in Generation an TOS Order and wqhat would need to be a skill that is triggered by a Generated TOS Order For now Simulated later Schwab API)

To bridge the gap between your framework and execution (TOS/Schwab), you should categorize tasks by Deterministic Automation (rules that need no human judgment) and Skill-Based Triggering (processes requiring council approval or human nuance).

1. Deterministic Automation (Ready for Code)
These tasks follow strict mathematical or conditional logic and should be handled by your system’s backend.

Pre-Entry Gate Validation: Automated script checks against current market data (Signal Durability, Cash Re-confirm, Spread Sanity, Macro/Sector triggers) and logs the output string.

Order Generation: Based on a "Proceed" status, generate the JSON/XML order payload (limit price, quantity, stop-loss, take-profit) formatted for TOS/Schwab.

Order Routing & Management: Automated submission of the order, 5-minute wait loops, and re-quoting logic based on the 10-minute abort window.

Post-Trade Logging: Once a fill occurs, the system automatically pulls the fill data (price, quantity) and populates the 27-column tracker schema.

2. Skill-Based Triggers (Council-Required - GEMS )
These tasks involve trade-offs and judgment; these require a "human-in-the-loop" skill or approval before the order generator takes action.

Council Approval Skill: Before generating the TOS order, the system requests a "Council Vote" (Quant, Macro, Momentum) if any warning flags (e.g., sector liquidity or volatility) are present.

Override Management Skill: Triggered when the system identifies a "Manual Exit" scenario (e.g., news events or pattern failure). The skill pauses automated management and requests an explicit "Kill" or "Modify" instruction.

Posture Re-Read/Governor Skill: When the system detects a P_010 risk_mode shift to OFF, it triggers a "Posture Review" skill that forces the framework to pause, recalculate stop-loss distances, and request a human sign-off on open positions.

Appendix A     Trading Plan
1. Define your risk per trade
With a 35,000 USD account:

Conservative (capital preservation): risk 0.25–0.5% per trade → 87.50–175 USD per trade.

Moderate: risk 1% per trade → 350 USD per trade.

In a risk‑off, choppy market I strongly prefer the conservative end (0.25–0.5%) so one or two losing trades do not matter much.

2. Set daily and weekly loss limits
To avoid death by many small cuts in consolidation:

Daily max loss: 1–1.5% of equity → 350–525 USD per day.

Weekly max loss: 3–4% of equity → 1,050–1,400 USD per week.

When you hit either limit, you stop trading for that period.

3. Translate this into number of trades
Using 0.5% risk per trade (175 USD):

Per day: with a 1% daily cap (350 USD), you can take 2 full‑risk trades (175 × 2 = 350).

Per week: with a 4% weekly cap (1,400 USD), that is at most 8 full‑risk trades (175 × 8 = 1,400).

If you choose 0.25% risk (87.50 USD), you could take up to 4 trades per day or 16 per week, but I would still limit yourself to 2–3 A‑quality setups per day in consolidation.

4. Adjust for your current portfolio
From your screenshot, you are:

Holding several swing positions (equities/ETFs and mutual funds) that already use a chunk of your buying power.

Up on the year with realized and unrealized gains, so protecting open profit is important in this phase.

Because you are partially invested already, treat new trades as incremental risk and cut the numbers above by about half:

New active trades: 1–2 new trades per day, 4–6 per week, sized at 0.25–0.5% risk each.

5. Practical checklist for each trade
Before entering any trade in this market condition:

Is this truly an A‑setup (clear level, tight stop, good R:R of at least 2:1)?

Does the position keep total open risk under 3–4% of account if all stops hit?

Does today’s new risk stay within your daily/weekly loss limits?

If you’d like, tell me your typical stop size (in % or dollars) and whether these are mostly options or stock, and I can give you exact share/contract size and a tailored “max trades per day/week” plan.

Current Account Parameters
Balance: $35,000
Risk per trade: 1.5% ($525)
Max position: 5% ($1,750)

With those parameters, you’re running an aggressive but usable model; the key is controlling total and correlated risk.

1. Check if the raw numbers make sense
Account balance: 35,000 USD.

Risk per trade 1.5% = 525 USD maximum loss if the stop is hit.

Max position 5% = 1,750 USD per single position, which is a common upper bound in position‑sizing frameworks.

This means every trade must be sized so that the dollar loss from entry to stop is ≤ 525 USD while the capital committed is ≤ 1,750 USD.

2. How many trades can you hold?
You now need portfolio‑level limits, not just trade‑level:

Total open risk (sum of max losses if all stops hit) should generally stay under 4–6% of the account.

With 1.5% risk per trade, that implies 2–3 open trades at full risk:

2 trades × 1.5% = 3% total risk (conservative).

3 trades × 1.5% = 4.5% total (upper end but still reasonable).

So in a risk‑off consolidation environment, I would cap it at 2 full‑risk trades at a time, occasionally 3 if they are in different, weakly‑correlated themes (for example: one index ETF, one individual stock in another sector).

3. Daily and weekly loss limits for your settings
Given 1.5% risk per trade:

Daily loss limit: 1.5–2% of account (525–700 USD); two losers should end your day.

Weekly loss limit: about 5–6% of account (1,750–2,100 USD); three to four full‑risk losses in a week is your hard stop.

This prevents a short consolidation streak from turning into a deep drawdown while still letting your edge play out.

4. Translating to “number of trades I should take”
Using your parameters and a risk‑off mindset:

Max open trades at full size: 2–3, with total open risk capped at 4–5% of equity.

New trades per day: 1–3, depending on whether earlier trades have hit target or stop.

If you want more trade frequency, reduce risk per trade to 1% (350 USD) and you can safely run 3–4 concurrent trades while keeping total risk in the same 4–5% band.

This way “how many trades” is always governed by total open risk and correlation, not just a fixed count.

5. Quick rule‑set for your plan
Per trade: max loss 525 USD, max capital 1,750 USD.

Portfolio: total potential loss if all stops hit ≤ 1,750 USD (5%) in this risk‑off phase.

Correlated names (for example multiple big‑tech or multiple index ETFs) count as one bucket toward that 5% cap.

If you tell me your usual stop distance (for example 2%, 3%, 5%), I can give you exact share/contract sizes that match 525 USD risk and 1,750 USD max position for your typical trades.

Appendix B    Option Sppread Management 

(Replacing #1006220058453) SELL -8 BAC 100 18 JUN 26 52.5 CALL MKT GTC TRG BY #1006142400348 OCO #1006142400349 WHEN BAC MARK AT OR BELOW 51.20 [TO CLOSE]
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

