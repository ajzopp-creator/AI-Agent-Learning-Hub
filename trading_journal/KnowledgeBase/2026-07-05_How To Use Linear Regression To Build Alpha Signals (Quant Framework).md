---
title: "How To Use Linear Regression To Build Alpha Signals (Quant Framework)"
source: "https://x.com/rohonchain/article/2063992615721435154"
author:
  - "[[Roan (@RohOnChain)]]"
date: "2026-07-05"
published: 2026-06-08
tags:
  - "kb"
kb_type: "article"
ticker_relevance:
  - "X (formerly Twitter)"
sector:
origin:
---
![Image](https://pbs.twimg.com/media/HKSRoeVbIAAdPNF?format=jpg&name=large)

I am going to break down how to use linear regression to win every single trade, build a real alpha signal & share the exact winning code. Let's get straight to it.

> **Bookmark This** - I'm Roan, a backend developer working on system design, HFT-style execution, and quantitative trading systems. My work focuses on how prediction markets actually behave under load. For any suggestions, thoughtful collaborations, partnerships DMs are open.

Every quant has a version of this story. You spend a week on a model. The backtest looks perfect, the equity curve points straight up and you think you finally found it. You go live. Two weeks later it is down money and you have no idea why.

I have seen this one cycle end more quant careers than any market crash. The model was never real. It was noise dressed up as a signal. And the most valuable skill in this entire field is learning to tell those two apart before you risk a single dollar.

That skill starts with the most underrated tool in quantitative finance. **Linear regression.**

I know how that sounds. Linear regression is the thing everyone thinks they learned in an afternoon and moved past. But here is what took me years and real losses to understand. The people running billions at the top firms are not using exotic deep learning monsters for most of their core signals. They use linear regression, understood far deeper than most people ever go, applied with a discipline most people never build.

Look at the most successful trading operation in history. Jim Simons built Renaissance Technologies on this exact foundation. His Medallion Fund averaged roughly 66 percent gross annual returns from 1988 to 2018, the best record ever recorded. And by his own team's account, the fund was right on only about 50.75 percent of its trades. Across millions of trades that razor thin edge compounded into more than 100 billion dollars. They were not predicting the future. They were pulling a tiny, real, repeatable signal out of an ocean of noise, which is exactly what regression is built to do. AQR, now managing around 179 billion dollars, built its empire on regression based factor models. PDT Partners ran statistical arbitrage for years without a single losing year.

This is the version of linear regression nobody taught you.

By the end of this article you will understand what linear regression really is, what alpha actually means, how to build a single and multi factor signal from scratch with real code, how to read a regression output like an institutional researcher, the exact tests that separate a real signal from a coincidence and why even a real signal eventually dies.

**Note: This article is deliberately long and every part builds on the one before it. If you are serious about building signals that survive live markets, read every single word. If you want a magic indicator, this is not for you.**

## Part 1: What Linear Regression Actually Is

![Image](https://pbs.twimg.com/media/HKIIAYIa0AAZAuR?format=jpg&name=large)

Linear regression finds the single straight line that sits closest to every data point at once.

Forget finance for a second. **Linear regression is just the math of drawing the best straight line through a cloud of dots.**

Picture plotting house size against house price. Bigger houses cost more, so the dots drift upward. Linear regression finds the one straight line that sits closest to all those dots at once. Feed in the size of a new house and you read off its predicted price. That is the whole idea. It is a machine that learns the relationship between an input and an output, then uses it to predict.

Andrew Ng opens his famous Stanford machine learning course with this exact house price example, because it is the simplest learning algorithm there is and the foundation everything else builds on.

The line has the formula you already know from school:

> **y = a + b x**

Here y is what you predict, x is your input, b is the slope, how steeply y rises as x rises, and a is the intercept, the value of y when x is zero. The method that finds the best a and b is Ordinary Least Squares, or OLS. Out of every possible line, OLS picks the one that makes the sum of the squared gaps between the line and the actual dots as small as possible. Squared, so misses above and below both count, and big misses get punished far more than small ones.

You can see the whole thing in a few lines:

```python
import numpy as np
import statsmodels.api as sm

x = np.array([1400, 1600, 1700, 1875, 2350, 2450])   # house size
y = np.array([245, 312, 279, 308, 405, 324])          # price in thousands

X = sm.add_constant(x)            # adds the intercept term 'a'
model = sm.OLS(y, X).fit()
print(model.params)               # gives you a and b
```

Now bring it into markets. In trading your y becomes the return of an asset, and your x becomes a factor you believe predicts that return. The slope becomes your sensitivity to that factor. And that humble intercept, a, becomes the single most important number in quantitative finance. Here is why.

## Part 2: What Alpha Actually Is

![Image](https://pbs.twimg.com/media/HKIIZHNa0AAN4JR?format=jpg&name=large)

Total return splits into beta, the part the market explains, and alpha, the part it cannot.

Most traders use the word alpha to mean profit. That is wrong, and the mistake is expensive.

Alpha is the return your strategy makes that cannot be explained by exposure to known risk factors. If you earned 20 percent in a year but the market also earned 20 percent, your alpha is zero. You were just holding beta, the return you collect for taking market risk. You got paid for riding the wave, not for skill.

This distinction is the whole game, and regression is the blade that separates the two. The foundational model. The return of your strategy at time t, written rₜ, is a baseline plus its exposure to a factor Xₜ plus noise:

> **rₜ = α + β Xₜ + εₜ**

Read it slowly. The β is your sensitivity to the factor. If the factor is the market, beta says how hard you move when the market moves. The εₜ is random noise, the part no factor explains. And α, the intercept, is the return you earn on average when the factor contributes nothing.

That intercept is the entire prize. If after stripping out every known risk factor your strategy still shows a positive, statistically significant alpha, you found something real. If the alpha vanishes the moment you account for the factors, you never had edge. You had disguised beta dressed up as genius.

Michael Jensen first framed skill this way in 1968 when he tested whether mutual fund managers could actually beat the market. He ran this exact regression and asked one question. Is the intercept different from zero? Almost sixty years later this is still how institutional performance is judged. It is called Jensen's alpha, and it is the bedrock of the discipline.

**So when you build a signal, your job is never to maximize raw return. It is to produce a positive intercept that survives after the known factors are gone. Hold that. Everything else serves it.**

## Part 3: Building Your First Signal From Scratch

![Image](https://pbs.twimg.com/media/HKIJBCZa8AAFoO-?format=jpg&name=large)

A real signal measures alpha only after every known factor has been stripped out.

Let us build the simplest real model, then make it institutional grade. Suppose you believe one asset's return can be partly predicted by a factor. A related asset's prior return, a momentum measure, a value metric. The single factor regression is:

> **rₜ = α + β Xₜ + εₜ**

In Python it is a handful of lines, and the intercept is the part you must never skip:

```python
import statsmodels.api as sm

# X is your factor series, y is the asset return you want to explain
X = sm.add_constant(X)        # THIS line creates your alpha intercept
model = sm.OLS(y, X).fit()
print(model.summary())
```

That add\_constant line is not a formality. It is the line that creates your alpha term. Forget it and you force the line through zero, throwing away the most important number in the whole output.

But the real world is never one factor. A serious signal accounts for many influences at once. That is the multi factor model:

> **rₜ = α + β₁X₁ₜ + β₂X₂ₜ + ... + βₖXₖₜ + εₜ**

Each beta now measures the effect of its own factor while holding all the others constant. That phrase, holding the others constant, is the quiet superpower of regression. It isolates the unique contribution of each factor and strips away the overlap. When you regress your strategy returns against the established factors, market, size, value, momentum, whatever alpha is left in that intercept is the slice of your edge that none of the known factors can explain.

```python
import statsmodels.api as sm

# factors is a DataFrame, each column one factor, aligned to returns y
X = sm.add_constant(factors)
model = sm.OLS(y, X).fit()

alpha   = model.params['const']     # your candidate edge
p_alpha = model.pvalues['const']    # how much to trust it
print("Alpha:", round(alpha, 5))
print("Alpha p-value:", round(p_alpha, 4))
```

That residual intercept is your candidate signal. Everything from here is about proving whether it is real.

This is exactly where most public tutorials stop, and where the institutional work actually begins. The factor construction, the neutralization, the weighting schemes that turn a raw signal into a tradeable book. If you want to see exactly how a firm like AQR turns these regressions into a live factor portfolio, that breakdown is where I take it all the way.

## Part 4: Reading the Output Like an Institutional Researcher

![Image](https://pbs.twimg.com/media/HKIJYFgbgAArvt0?format=jpg&name=large)

The professional does not ask how big the return is. They ask how confident they are it is not an accident.

When you run that summary, most people glance at one number and move on. A trained researcher reads it like a diagnostic report. Here is what actually matters.

**The coefficient and its sign.** Each beta gives direction and strength. Before trusting any number, ask whether the sign even makes economic sense. If your model says buy when something is more expensive and you cannot explain why, you found a fluke, not a factor.

**The p-value.** This is the heart of everything. It answers one question. If this factor truly had no effect, how likely is it I would see a relationship this strong purely by chance? A p-value of 0.62 means a 62 percent chance you are staring at random luck. Below 0.05 is the conventional bar to take a result seriously. A quant looking at a failed model with a p-value of 0.62 is not looking at a weak signal. He is looking at pure noise.

**R-squared.** The fraction of return variation your model explains, and here is the part that flips beginners upside down. In return prediction a high R-squared is usually a warning, not a trophy. Real return signals are weak. An R-squared of 0.01 or 0.02 can be wildly profitable if it is persistent and real. If you see 0.9 on a return prediction you almost certainly have look-ahead bias or you are regressing something on itself by accident.

**The t-statistic.** The coefficient divided by its standard error. A rough rule is a t-stat above 2 in absolute value matches the 0.05 threshold. Serious researchers demand 3 or higher on a brand new signal, precisely because they know how many signals they quietly tested before this one.

You can pull these straight out instead of reading the whole table:

```python
print("t-stats:\n", model.tvalues)
print("p-values:\n", model.pvalues)
print("R-squared:", round(model.rsquared, 4))
```

Internalize the shift. The beginner asks how big is the return. The professional asks how confident am I that this return is not an accident. That single change in the question is the whole difference.

## Part 5: The Tests That Separate Real Signal From Noise, and Why Signals Die

![Image](https://pbs.twimg.com/media/HKIJyCkbkAAhu3F?format=jpg&name=large)

Run every candidate through the same gauntlet. Almost nothing survives, and that is the point.

Here is the brutal truth. If you test enough random signals, some will look profitable by pure chance. Test 100 useless signals at the 0.05 level and about 5 will pass on luck alone. This is the multiple testing problem and it is the number one reason backtests lie. Here is how serious desks defend against it.

**Out of sample testing.** Never judge a signal on the data you built it on. Split your history. Build on the first portion, test on a portion the model has never seen. A real signal survives the crossing. A fitted fantasy collapses the instant it meets fresh data. Non negotiable.

```python
split = int(len(y) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

model = sm.OLS(y_train, X_train).fit()
oos_pred = model.predict(X_test)          # test on unseen data
```

**Information Coefficient.** Institutional factor researchers rarely live or die by one regression. They compute the IC, the correlation between a factor's value and the actual forward return, again and again across time. A factor with a mean IC above roughly 0.03 to 0.05 that stays stable across many periods beats one with a single gorgeous backtest every time. Stability across regimes is the real tell.

**Newey-West standard errors.** Financial data breaks a core OLS assumption because returns and volatility cluster in time. Raw p-values will lie, usually flattering your signal. Newey-West corrects your standard errors for this. Using it quietly marks someone who knows what they are doing.

```python
# Newey-West corrected significance, the institutional default
model = sm.OLS(y, X).fit(cov_type='HAC', cov_kwds={'maxlags': 5})
print(model.summary())
```

**Multiple testing correction.** If you tried 50 signals you cannot judge the winner against the normal bar. The simple defense is Bonferroni, dividing your threshold by the number of things you tested. Tried 50 signals? Demand a p-value below 0.001, not 0.05. It is brutal, and that is the point. It forces honesty about how many times you went fishing.

Run a candidate through out of sample validation, a stable IC, Newey-West significance, and a multiple testing correction, and if it is still standing, you have something most retail traders never produce in their lives. A signal you genuinely earned the right to trust.

But understand the final truth. Even a real signal decays. Alpha lives in market inefficiency, and the moment a signal is known and traded, the trading itself pushes the inefficiency away. Recent research on factor crowding shows mechanical, easily copied signals like simple momentum decay along a sharp predictable curve as capital piles in, and that this crowding accelerated sharply once factor investing became cheap through ETFs. The simplest signals are the most crowded and die fastest. Durable edge lives in signals that take real work to build, and in a research process that produces new ones faster than the old ones erode. That is why Renaissance never stopped researching for a single day in thirty years.

**Homework:** Take a signal you currently believe in. Run it on the most recent 20 percent of your data, which you will pretend you have never seen. If the alpha disappears, you just saved yourself real money. It is the most valuable test you will ever run.

## Part 6: What You Just Built, End to End

![Image](https://pbs.twimg.com/media/HKIKQBHbcAARUdz?format=jpg&name=large)

Every real signal erodes as it gets crowded. The research engine that replaces them is the actual edge.

Step back and look at the full machine you now have, because the pieces connect into one clean pipeline.

You start with a factor, anything you believe carries information about future returns. You regress your asset's returns on that factor with OLS, always including the intercept, and that intercept is your candidate alpha. You expand to a multi factor regression so that your alpha is measured only after the known risk factors, market, size, value, momentum, have been stripped out. What remains in the intercept is pure, unexplained edge.

Then you interrogate it. You read the p-value to ask whether it could be luck. You check the sign for economic sense. You ignore the seductive high R-squared and respect the small honest one. You validate out of sample on data the model has never touched. You compute the Information Coefficient across many periods to confirm it is stable, not a one time fluke. You correct your standard errors with Newey-West so the time structure of markets does not fool you. And you apply a multiple testing correction so the number of signals you tried cannot manufacture a false winner.

What comes out the other side is not a guess. It is a signal with a measured edge, a known confidence level, proof it survives on unseen data, and an honest accounting of how likely it is to be real. That is the difference between the person whose model dies in two weeks and the person who builds something that holds.

And here is how it actually makes money. A signal with a small but genuine and stable edge, traded across many independent opportunities, compounds. Renaissance was right barely more than half the time and turned that into the greatest fortune in market history, because the edge was real, it was repeatable, and they sized it correctly across enormous numbers of bets. You are now working from the same blueprint. Build the signal, prove it is real, size it sensibly, and replace it the moment its IC starts to fade.

That replacement loop is the whole career. One signal is a trade. A research process that keeps producing real signals faster than they decay is a franchise.

## The Summary

Linear regression is not the boring tool you skipped. It draws the best line through your data, it defines what alpha actually is, it builds your first real signal, it tests whether that signal is genuine or noise, and it warns you when the signal begins to die.

Alpha is the intercept that survives after every known risk factor is removed. You build a candidate with OLS, single factor first, then multi factor. You read the output like a researcher, where the p-value and stability matter more than the size of the return. You defend against the multiple testing trap with out of sample validation, a stable Information Coefficient, Newey-West errors, and a correction for how many signals you tried. And you accept that every real signal decays, which means the true edge is the research engine, not any single model. The same engine that built the greatest fund in history.

The quant staring at a Sharpe of 0.03 and a p-value of 0.62 is not unlucky. He skipped the discipline in this article. Do not be him.

Here is the question I want you to sit with.

If real alpha decays the moment it becomes widely known, then publishing a signal destroys it, while hoarding a signal means it still slowly dies as others independently discover it.

So where does durable edge actually come from? The signals themselves, or the speed of the research process that replaces them?

Your answer reveals whether you think like a trader chasing one big win, or like a quant building a machine that prints edge for decades.

Drop your answer in the comments. There is no wrong answer. But there are very revealing ones.