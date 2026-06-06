# Stock Prompts Inspired by Ed Thorp

Source note: The text below was adapted from a post the user said was taken from X. It has been cleaned up for readability and structured so Perplexity can interpret the prompts consistently.

## Context
In 1961, MIT math professor Ed Thorp reportedly entered a Las Vegas casino with a shoebox-sized computer hidden in his suit. He had shown that blackjack could be beaten, and casinos later changed rules in response. He later applied probabilistic thinking to Wall Street, where his hedge fund is widely described as having produced exceptional long-term returns with no losing years across a multi-decade span.

The core idea behind these prompts is not prediction theater. It is disciplined edge detection, risk sizing, assumption testing, correlation analysis, survival under drawdowns, and decision rules that can be stated before capital is committed.

## The 10 prompts

### 1. The Edge Identifier
> Analyze [market/asset/situation] and identify any statistical edge where the expected value is positive. Show the math. If there is no edge, say to walk away. Do not invent one.

Interpretation: Start with expected value and base rates. Refuse forced conclusions.

### 2. The Kelly Sizer
> Given an edge of [X%] and odds of [Y], calculate the optimal position size using the Kelly Criterion. Then cut it in half. Explain why half-Kelly survives drawdowns better than full Kelly.

Interpretation: Position sizing matters as much as idea quality. Favor survival over theoretical maximum growth.

### 3. The Assumption Killer
> List every assumption baked into this trade or decision. Rank them from most fragile to least fragile. Identify which assumption, if wrong, breaks the thesis.

Interpretation: Separate core assumptions from minor details. Focus on single-point failure risk.

### 4. The Hidden Correlation Finder
> Find non-obvious correlations between [variable A] and [variable B] that consensus may be missing. Show historical evidence. Flag which relationships look like coincidence versus durable signal.

Interpretation: Distinguish signal from narrative. Require repeatability, not one-off pattern matching.

### 5. The Counterparty Check
> Before entering this position, analyze who is likely on the other side of the trade. Why would a rational, informed participant take the opposite side? If that cannot be answered clearly, assume informational disadvantage.

Interpretation: Every trade has a counterparty. Understand their incentives, constraints, and possible informational edge.

### 6. The Drawdown Stress Test
> Simulate the worst 12-month drawdown this strategy could plausibly experience. Not the average case, the tail case. Estimate the 99th-percentile stress outcome and state whether it is survivable financially and emotionally.

Interpretation: A strategy that cannot be lived through will not be followed consistently.

### 7. The Independence Filter
> Are these [trades/bets/decisions] truly independent, or are they the same bet expressed multiple ways? Identify hidden common factors that could cause simultaneous failure.

Interpretation: Apparent diversification often collapses under stress. Look for latent factor concentration.

### 8. The Exit Trigger
> Define the exact conditions for exit before entry: price level, time limit, broken assumption, volatility change, or any other kill switch. If an exit rule cannot be defined in advance, do not enter.

Interpretation: Pre-commitment reduces hope-based decision-making.

### 9. The Survivorship Audit
> I am about to learn from [person/strategy/track record]. Audit it for survivorship bias. How many similar attempts failed? What unseen graveyard sits behind the visible winner?

Interpretation: Separate genuine skill from lucky visibility.

### 10. The Boredom Test
> Is this opportunity exciting or boring? If it feels exciting, treat that as a warning sign. The best edges are often boring, repeatable, and operationally simple. State honestly which category this belongs to.

Interpretation: Emotional intensity is often inversely related to decision quality.

## Suggested Perplexity usage guidance
- Ask for explicit math or evidence when claiming edge.
- Ask for historical analogs, not just narratives.
- Force assumptions into ranked lists.
- Require a no-trade conclusion when evidence is weak.
- Separate exploratory ideas from executable setups.
- Tie every setup to sizing, drawdown tolerance, and exit criteria.

## P300 incorporation notes
These ideas fit P300 best as a decision-support and validation layer rather than a replacement for the documented SPY-first baseline pipeline.

Proposed additions to the plan:
1. Add a prompt library entry under `docs/prompts` for the ten Thorp-style prompts.
2. Add an edge-validation checkpoint after feature generation and before ranking outputs.
3. Add position-sizing research notes as a future decision-support module, not as part of baseline catalog construction.
4. Add survivorship-bias and hidden-correlation checks to later matching-analysis reports.
5. Keep all of the above flagged as proposals until they are approved and documented in the architecture file.
