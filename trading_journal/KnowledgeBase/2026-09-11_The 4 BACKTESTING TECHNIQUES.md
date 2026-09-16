---
title: "Post by @RohOnChain on X"
source: "https://x.com/RohOnChain/status/2098486986583757043"
author:
  - "[[@RohOnChain]]"
date: "2026-09-11"
published: 2026-09-11
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
The 4 BACKTESTING TECHNIQUES behind WINNING Strategies:

i've spent the last 2 years running backtests on everything from mean reversion setups to volatility arbitrage to prediction market signals

some strategies survived and tbh most of them died and the difference was never the strategy itself, it was how i tested it

a backtest is not proof your strategy works, it's a stress test to see how easily it breaks

here are the 4 techniques i've actually run, what worked, what broke AND what i still use

\---------------

technique 1: standard in-sample / out-of-sample split

verdict: broken by default, NEVER TRUST THIS

the setup is easy, take 5 years of data and train on the first 4, test on the last 1

the problem is subtle - every time you tweak the strategy and re-run, you're peeking at the test data and after 30 iterations your "out-of-sample" is FULLY contaminated

the first strategy i ever backtested was a simple pairs trade between two energy stocks that showed a Sharpe of 2.1 on the standard split, so i deployed $2,000 of my own money and lost 40% of it in 3 months

going back later i realized i'd re-run that backtest 47 times during tuning, the test data was never really untouched

use this only for a quick first look, NEVER as the final validation

\---------------

technique 2: walk-forward validation

verdict: the real workhorse, this is what i actually use

instead of splitting once, you slide a window through the data

train on 2018-2020, test on 2021

train on 2019-2021, test on 2022

keep sliding

each test window is data the model has never seen and you get 5 or 6 test periods instead of JUST ONE

what this catches:

\> strategies that only worked in one regime (the pattern shows up immediately)

\> parameters that shift wildly when retuned (unstable strategy, red flag)

\> strategies that survive across every window (this is real edge)

at our fund we killed a stat arb strategy that showed Sharpe 2.4 on a standard split, but walk-forward revealed it worked beautifully in 2019-2020 and completely died in 2021-2022, the regime had shifted underneath us and it saved us months of losses

but this is slower and more painful than a standard split and it's also the reason institutional backtests match live P&L :)

\---------------

technique 3: purged k-fold cross-validation

verdict: fixes a hidden bug in walk-forward

financial data has memory, today's price is not independent of yesterday's

when your training window ends on december 31 and your test window starts january 1, information leaks across that boundary and your Sharpe looks better than it should

purged k-fold fixes this, Marcos Lopez de Prado covers it in Advances in Financial Machine Learning

the idea is simple:

\> split data into folds like standard cross-validation

\> when a fold is used for testing, remove the adjacent observations that overlap in time

\> this eliminates the leakage

a QUANT friend of mine who runs an ML-based factor model showed me his numbers before and after adding purging, Sharpe dropped from 1.9 to 1.4 on the same strategy with the same data and the extra 0.5 was pure leakage he didn't know he had

use this when you're training ML models on financial data, the leakage in tree-based models is brutal without it

\---------------

technique 4: monte carlo trade shuffling

verdict: the reality check that saves capital EVERY SINGLE TIME

your backtest shows one sequence of trades, Monte Carlo randomizes the order and runs it thousands of times

why this matters:

\> your backtest might have gotten lucky with sequencing, what if the drawdown happened in month 2 instead of month 10

\> the max drawdown you observed is one path, Monte Carlo shows the full range

\> the 5th percentile drawdown is often 2 to 3 times worse than what you saw

few months ago (during the hype of 15-min BTC markets) i built a systematic prediction market strategy that showed 12% max drawdown across 18 months of backtest, but before deploying i ran Monte Carlo with 10,000 shuffled sequences and the 5th percentile scenario showed a 34% drawdown

ofc i didn't deploy at full size, i sized it at 25% of what i originally planned and three months in the strategy hit a 22% drawdown, but the smaller size meant i could hold through it and the strategy recovered to finish the year up 31%

Monte Carlo is why i stayed in that trade instead of blowing up

\---------------

what i actually use in production NOW:

\> walk-forward validation as the primary test

\> purged k-fold when the strategy uses ML models

\> Monte Carlo shuffling on strategies that survive both, before any real capital

\> standard in-sample/out-of-sample only for the very first pass (rarely tho)

if your backtest is designed to make you feel good, it's designed to LOSE you money for real.

![Image](https://pbs.twimg.com/media/HR9SUVFagAAXoqc?format=jpg&name=large)