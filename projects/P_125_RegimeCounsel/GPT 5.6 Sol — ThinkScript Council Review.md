# Technical Review: Regime Council for Thinkorswim

## Bottom line

Yes, this study can be improved materially—but not by adding more indicators to the existing vote. The highest-value changes are to correct two semantic bugs, remove duplicated information, separate persistent market state from short-lived event tags, and validate an explicit trading rule rather than optimizing descriptive labels.

The present script is a useful **diagnostic dashboard**, not yet a statistically defensible trading system. It has no entry/exit definition, holding period, transaction-cost model, position sizing, stop logic, or simulated orders. Therefore, no win rate or expectancy can be attributed to it as written. The most important defects are:

1. **`vwap` is not VWAP.** Lines 31–35 define `(high + low + close) / 3`, which is typical price. Consequently, `vwapDist` simplifies to \((2C-H-L)/3\): a close-location-in-the-bar measure, not distance from volume-weighted average price. Thinkorswim has a genuine `vwap()` function that returns volume-weighted average price and accepts aggregation periods ([Schwab thinkScript VWAP documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Fundamentals/vwap)).
2. **`adjVolumeZ` does not mean volume participation.** It mixes volume surprise with direction in a way that reverses low-volume down bars into positive “high-volume” readings. That corrupts several regime rules and the volume label.
3. **OBV change and signed volume are effectively the same feature.** `obvChange` is exactly \(+\text{volume}\), \(-\text{volume}\), or zero according to the close-to-close sign. It substantially double-counts the same flow represented by `adjVolumeZ`; CMF adds a third volume/close-location expression.
4. **The seven inputs are not seven independent votes.** They are mostly repeated views of two latent themes: price momentum and volume/flow. An unadjusted sum silently overweights whichever theme has the most correlated proxies.
5. **The regime taxonomy mixes states and events.** “Uptrend/range/downtrend” are persistent states; “breakout,” “capitulation,” “climax,” and “trap” are transient events. Putting all of them in one ordered `if/else` chain forces false exclusivity and hides overlapping conditions.
6. **The script uses inconsistent time scales.** `sumZZ` is based on triple-smoothed components, while nearly every regime predicate uses the unsmoothed component. The visual `sumZema` is smoothed again but is not used in regime classification.
7. **The 11 threshold rules are hypotheses, not calibrated models.** Their firing rates, overlap rates, forward returns, drawdowns, and stability are unknown.

The recommended redesign is a two-layer model:

- **State layer:** trend direction × volatility state × trend quality, with hysteresis and minimum duration.
- **Event layer:** breakout, exhaustion, capitulation, and price-flow divergence as independent tags that may coexist.

Only after those outputs are converted into exact next-bar trade rules and pass walk-forward, multi-symbol, multi-regime testing should the labels be used as entry gates.

---

## 1. What the script actually measures

| Code label | Actual quantity | Main issue |
|---|---|---|
| `vwapZ` | Z-score of close minus typical price | Not VWAP; mostly bar close location |
| `adjVolumeZ` | Rolling volume z-score multiplied by close-to-close direction | Sign and magnitude are entangled |
| `obvZ` | Z-score of signed raw volume | Nearly redundant with signed volume |
| `cmfZ` | Z-score of a 14-bar volume-weighted close-location oscillator | Overlaps both flow and bar-location information |
| `rsiZ` | Z-score of a bounded, smoothed momentum oscillator | Distribution is bounded and regime-dependent |
| `macdZ` | Z-score of a smoothed trend-acceleration measure | Overlaps price momentum and adds lag |
| `pctGainZ` | Z-score of current-bar close-to-open percentage return | Not close-to-close return; meaning changes with aggregation |

The script calls `RSI(length = length)` without specifying price or average type. Thinkorswim’s built-in RSI uses Wilder’s average by default, so the feature already contains smoothing before it receives three more EMAs ([Schwab RSI documentation](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/R-S/RSI)).

### The false-VWAP defect

The current calculation is:

\[
\text{vwapDist}
= C-\frac{H+L+C}{3}
= \frac{2C-H-L}{3}.
\]

It is positive when the close is in the upper part of the bar and negative when the close is in the lower part. That may be a useful candle-location feature, but it must be named accordingly. It does not measure institutional positioning relative to VWAP.

For intraday use, replace it with:

```thinkscript
input vwapPeriod = AggregationPeriod.DAY;
def trueVWAP = vwap(period = vwapPeriod);
def atr = reference ATR(length = 14).ATR;
def vwapDistance = if atr > 0 then (close - trueVWAP) / atr else 0;
```

ATR normalization makes the distance more comparable across symbols and price levels. Thinkorswim defines ATR from true range, which includes the current high-low range and gaps to the prior close, and defaults to a 14-period Wilder average ([Schwab ATR documentation](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/A-B/ATR)). On daily charts, decide explicitly whether the desired anchor is daily, weekly, monthly, or event-anchored VWAP; a “daily VWAP distance” does not have the same meaning on every chart aggregation.

### The signed-volume defect

`adjVolumeZ` has the following behavior:

| Close-to-close direction | Raw `volumeZ` | `adjVolumeZ` | What the script may infer |
|---|---:|---:|---|
| Up | High positive | Positive | Positive/high participation |
| Up | Low negative | Negative | Negative/low participation |
| Down | High positive | Negative | Negative/“low volume” |
| Down | Low negative | Positive | Positive/“high volume” |

Thus, `adjVolumeZ > 2` can mean either unusually high volume on an up close **or unusually low volume on a down close**. Conversely, `adjVolumeZ < -1` can mean high down volume, yet the label calls it “LOW VOL.” Direction and participation must be separate:

```thinkscript
def direction =
    if close > close[1] then 1
    else if close < close[1] then -1
    else 0;

def volumeMean = Average(volume[1], zLength);
def volumeSd   = StDev(volume[1], zLength);
def volumeZ    = if volumeSd > 0 then (volume - volumeMean) / volumeSd else 0;

def signedVolume = direction * volume;
def signedVolMean = Average(signedVolume[1], zLength);
def signedVolSd   = StDev(signedVolume[1], zLength);
def signedFlowZ   =
    if signedVolSd > 0
    then (signedVolume - signedVolMean) / signedVolSd
    else 0;
```

Use `volumeZ` or relative volume for participation and `signedFlowZ` for directional flow. Do not use one field for both.

`TotalSum` is also unnecessary here. Thinkorswim defines it as the sum from the first chart bar through the current bar ([Schwab TotalSum documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Math---Trig/TotalSum)). Since the code immediately differences OBV, `obv - obv[1]` algebraically reduces to signed current-bar volume. Calculating the cumulative series first adds work and chart-start dependence without adding information.

---

## 2. Statistical validity of the z-scores

### A rolling z-score is a scale transform, not a probability statement

The comments equating \(z=2\) with the 97.5th percentile are only approximately true for an observation drawn from a fixed normal distribution with known parameters. Here:

- the mean and variance are estimated from only 20 observations;
- the current observation is included in its own baseline;
- the inputs are bounded, autocorrelated, smoothed, skewed, or heavy-tailed;
- their distributions change across trend, volatility, session, and liquidity regimes.

Stationarity requires stable mean, variance, and autocorrelation structure; that is a demanding assumption for market features ([NIST stationarity guidance](https://www.itl.nist.gov/div898/handbook/pmc/section4/pmc442.htm)). Autocorrelation also violates the “independent observations” intuition commonly attached to standard-normal tail probabilities ([NIST autocorrelation guidance](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35c.htm)).

Thinkorswim’s `StDev` divides squared deviations by `length`, i.e., it uses the population-style rolling variance ([Schwab StDev documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Statistical/StDev)). With the scored observation included in a 20-point window, an internally studentized z-score has a finite maximum magnitude of \(\sqrt{19}\approx4.36\). NIST independently warns that ordinary z-scores can be misleading for small samples because the score has a sample-size-dependent maximum, and recommends median/MAD-based modified z-scores for robust outlier screening ([NIST outlier guidance](https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm)).

The most important improvement is therefore to score the current value against a **lagged baseline**:

```thinkscript
script LaggedZ {
    input x = close;
    input n = 60;
    def mu = Average(x[1], n);
    def sd = StDev(x[1], n);
    plot z = if sd > 0 then (x - mu) / sd else 0;
}
```

This asks the proper causal question: “How unusual is the new observation relative to information available before it arrived?” It also prevents the shock from inflating its own denominator and muting itself. A 20-bar window is generally too unstable for rare-event labels such as “capitulation”; test 60, 100, and 252 bars for daily data, or session-aware equivalents intraday.

### `sumZZ` does not create independent confirmation

`sumZZ` is simply a rolling standardization of a weighted sum whose weights are all one:

\[
S_t=\sum_{i=1}^{7}\widetilde z_{i,t}, \qquad
\text{sumZZ}_t=\frac{S_t-\bar S_t}{s(S)_t}.
\]

It is useful for putting the aggregate on a local scale, but it does not create a new source of information. Because `sumZZ` is mathematically built from the same components later used in each rule, a condition such as “`sumZZ > 2` and `cmfZ > 1` and `obvZ > 1`” is not independent multi-factor confirmation. It is partially requiring the same evidence twice.

The re-standardization does account for the **total recent variance** of the sum, including covariance, but it does not cure duplicated features or stabilize each component’s economic importance. Research on composite indicators shows that assigned weights need not equal actual influence when component variances and correlations differ; correlated inputs can dominate the result despite apparently equal nominal weights ([Becker et al., *Weights and importance in composite indicators*](https://pmc.ncbi.nlm.nih.gov/articles/PMC5473177/)).

### The seven-way sum double-counts two clusters

A practical feature map is:

- **Price/momentum cluster:** RSI, MACD histogram, close-to-open return, and the mislabeled “VWAP” close-location term.
- **Volume/flow cluster:** signed volume, OBV change, and CMF.

Summing all seven gives the flow cluster three votes and momentum approximately four votes. The effective weight changes by symbol and regime because their correlations change.

A better composite is hierarchical:

\[
\text{MomentumScore}=\frac{z_{\text{return}}+z_{\text{MACD}}+z_{\text{RSI}}}{3},
\]

\[
\text{FlowScore}=\frac{z_{\text{signed flow}}+z_{\text{CMF}}}{2},
\]

\[
\text{LocationScore}=z_{\text{true VWAP distance}},
\]

\[
\text{Composite}
=w_M\text{MomentumScore}
+w_F\text{FlowScore}
+w_L\text{LocationScore}.
\]

This gives each economic theme one vote rather than each implementation one vote. Offline, estimate the feature correlation matrix by symbol class and volatility regime. A covariance-aware score can be normalized as:

\[
S_t=\frac{w^\top z_t}{\sqrt{w^\top\Sigma_t w}}.
\]

If a stable covariance estimate is not feasible inside ThinkScript, use equal weights across the three groups, cap each input to a range such as \([-3,3]\), and calibrate the grouped model offline. PCA is another offline diagnostic—not necessarily the live trading model—to reveal how many independent dimensions the seven inputs truly contain. Regime-classification research has used PCA specifically to transform correlated macro series into uncorrelated components before classification ([Akioyamen et al., *A Hybrid Learning Approach to Detecting Regime Switches*](https://arxiv.org/pdf/2108.05801.pdf)).

### The 20-bar window is not one universal horizon

`zLength = 20` means 20 minutes on a one-minute chart, 100 minutes on a five-minute chart, and roughly one trading month on a daily chart. These are different models. Intraday volume also has strong time-of-day structure; comparing the open with the immediately preceding 20 bars is not equivalent to comparing that open with prior opens.

Use presets by intended trading horizon:

- **Intraday:** session-reset logic, regular-hours filtering, and same-time-of-day relative-volume baselines where possible.
- **Swing:** 60–126 bars for feature normalization and 100–252 bars for regime thresholds.
- **Position:** weekly confirmation and longer volatility/state baselines.

Avoid dynamically selecting the lookback from recent performance; that simply moves overfitting into the window-selection rule. A safer “adaptive” design uses a small predeclared set of horizons and chooses among them only by an independently defined volatility state.

---

## 3. Smoothing and latency

`ExpAverage` uses \(\alpha=2/(N+1)\) and historical prefetch; prefetch uses earlier data, not future data ([Schwab ExpAverage documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Tech-Analysis/ExpAverage)). Three cascaded length-3 EMAs have approximately three bars of low-frequency group delay. The plotted length-9 EMA of their sum adds approximately another four bars. Therefore:

- the component waves and `sumZZ` are approximately three bars behind slow changes;
- `sumZemaPlot` is approximately seven bars behind slow changes;
- RSI and MACD already contain internal smoothing before the three added EMAs;
- a “breakout confirmed” label may arrive after a meaningful portion of the move.

The source comment “lower = smoother” for `SmoothingFactor` is backward. With EMA length \(N\), a lower \(N\) gives a larger \(\alpha\), more responsiveness, and **less** smoothing.

This cascade is also not the conventional TEMA construction designed to reduce lag; it is simply EMA-of-EMA-of-EMA. For trade timing:

1. Use one EMA of length 3–5, not three cascades.
2. Use the same version—raw or smoothed—consistently throughout score and regime logic.
3. Keep a slower state estimate and a faster event trigger rather than blending both indiscriminately.
4. Require a threshold cross plus persistence, not merely “value remains above threshold.”

One sensible separation is:

- state: 20–50-bar trend/ADX and 60–126-bar volatility percentile;
- trigger: current or once-smoothed impulse crossing a calibrated threshold;
- confirmation: prior bar closed, breadth/relative strength agrees, and liquidity passes.

---

## 4. Review of the 11 regime rules

The `else if` structure makes the output mechanically mutually exclusive, but the underlying conditions are not logically exclusive. Earlier rules silently win. For example, rules 1, 3, and 10 can overlap; rules 2, 4, and 11 can overlap. Their ordering is therefore an undocumented priority model.

| Rule | Current label | Technical problem | Better definition |
|---:|---|---|---|
| 1 | Breakout confirmed | No actual breakout level, prior range, close confirmation, or retest; overlaps rule 10 | Close above prior \(N\)-bar high/Keltner band, positive relative strength, high unsigned volume, positive breadth, closed-bar confirmation |
| 2 | Breakdown confirmed | Asymmetric with rule 1 because it lacks a volume condition | Mirror the breakout specification and test long/short separately |
| 3 | Parabolic move | Uses false VWAP and a one-bar return z-score; no acceleration measure | Trend slope/curvature, ATR expansion, distance from EMA or true VWAP in ATR units |
| 4 | Capitulation | No explicit high-volume or volatility-spike requirement | Large negative return, high unsigned volume, high ATR regime, breadth washout, then stabilization/reclaim |
| 5 | Retail FOMO | `cmfZ < 0.5` and `obvZ < 0.5` have no lower bounds; “volume spike” is direction-contaminated | Rename to “price-volume divergence”; require positive price impulse, high unsigned volume, and weak/negative flow in bounded ranges |
| 6 | Momentum climax | Strong RSI/MACD can be healthy continuation; no loss of momentum or reversal | Require stretched trend plus deceleration, bearish divergence, failed high, or reversal bar |
| 7 | Stealth accumulation | “Low volume” test is one-sided; price condition permits arbitrarily negative moves | Require positive cumulative flow, low **absolute** participation, stable price/low downside volatility, persistence |
| 8 | Bull trap | No breakout-then-failure sequence | Prior breakout followed by close back below breakout level/VWAP within \(K\) bars, with negative flow |
| 9 | Bear trap | No breakdown-then-reclaim sequence | Prior breakdown followed by reclaim within \(K\) bars, with positive flow |
| 10 | Helicopter money | Duplicates extreme bullish impulse; name implies macro causality absent from OHLCV | Rename “high-volume upside impulse”; reserve macro labels for actual liquidity inputs |
| 11 | Fire sale | Usually conflicts with the signed-volume implementation: high down volume makes `adjVolumeZ` negative, while rule requires it above +2 | Use negative return + **positive unsigned** volume z-score + negative signed-flow score + high volatility |

The fallback is also mislabeled. `sumZZ > 1` means the composite is unusually high relative to its recent distribution; it does not prove an uptrend. A rebound inside a structural downtrend can satisfy it. Trend direction should come from price structure or slope; trend quality should come from ADX/choppiness; volatility should be a separate axis.

### A more coherent taxonomy

**Persistent state**

1. Uptrend / low volatility  
2. Uptrend / high volatility  
3. Range / low volatility  
4. Range / high volatility  
5. Downtrend / low volatility  
6. Downtrend / high volatility  

**Independent event flags**

- confirmed breakout;
- confirmed breakdown;
- upside exhaustion;
- downside capitulation;
- bullish price-flow divergence;
- bearish price-flow divergence;
- volatility shock.

This avoids forcing “uptrend” and “breakout” to compete for one label. It also makes strategy logic explicit: for example, a breakout entry may be allowed only in an uptrend/normal-volatility state and blocked in a high-volatility state.

### `chop` is unused

`input chop = 0.5` is never referenced. It should either be removed or replaced by a real trend-quality gate. Suitable choices include:

- ADX or DMI trend strength;
- Choppiness Index;
- Kaufman efficiency ratio;
- absolute regression slope divided by ATR;
- proportion of directional movement to total path length.

The `chop` threshold should correspond to the scale of the selected indicator. A generic 0.5 has no meaning until the variable is defined.

### The “adaptive extreme” block is orphaned

Lines 275–281 calculate another rolling mean and standard deviation of `sumZZ`, then plot a Boolean 0/1 series. It is not connected to regime logic, labels, or alerts. The comment saying it “needs recursive variables” is incorrect: `Average` and `StDev` are already rolling calculations and require no user recursion.

It also defines “unusual” as one rolling standard deviation from a 20-bar mean. Under an ideal normal model, that would flag roughly 32% of observations across both tails—not an extreme. Because the Boolean plot shares the lower pane with z-score waves, it can also clutter scaling and interpretation.

Either delete it or make it a purposeful, longer-horizon trigger:

```thinkscript
input adaptiveLength = 100;
input extremeK = 2.0;
def baseMean = Average(composite[1], adaptiveLength);
def baseSd = StDev(composite[1], adaptiveLength);
def upper = baseMean + extremeK * baseSd;
def lower = baseMean - extremeK * baseSd;
def upsideExtreme = composite > upper;
def downsideExtreme = composite < lower;
```

Keep upside and downside separate; a single Boolean discards direction.

---

## 5. Missing dimensions

### Volatility regime

The study has no explicit volatility state, although volatility determines whether a z-score extreme is likely to mean continuation, exhaustion, or noise. Add:

- ATR/close or APTR percentile;
- short/long realized-volatility ratio;
- ATR expansion rate;
- gap magnitude;
- optional implied-volatility/VIX context for equity index trading.

Modern regime work explicitly treats financial volatility as nonstationary and uses change-point detection plus locally stationary segments before clustering volatility states ([Prakash et al., *Structural clustering of volatility regimes*](http://arxiv.org/abs/2004.09963)). ThinkScript cannot reproduce that full model efficiently, but a slow/fast ATR ratio with hysteresis is a credible approximation.

### Relative strength and market context

For single-stock signals, add:

- return relative to SPY;
- return relative to the relevant sector ETF;
- index trend and volatility;
- market breadth or advance/decline confirmation where data are available;
- liquidity/spread and minimum dollar-volume gates.

“Helicopter money,” “smart money,” and “retail FOMO” cannot be inferred reliably from the present seven OHLCV transforms. Either include actual cross-asset/macro proxies or rename the states to observable descriptions.

ThinkScript can reference another symbol and a higher aggregation, but a secondary aggregation cannot be lower than the chart aggregation, and mixed aggregation contexts have restrictions ([Schwab secondary-aggregation documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/tutorials/Advanced/Chapter-11---Referencing-Secondary-Aggregation)). Build chart and scan versions separately because Stock Hacker does not support all study features and secondary aggregations.

### Multi-timeframe confirmation

A practical hierarchy is:

- weekly/daily state;
- daily/60-minute setup;
- chart-timeframe trigger.

Do not simply add the same seven indicators again on another timeframe; that multiplies redundancy. Use a small number of orthogonal questions:

1. Is the higher-timeframe trend supportive?
2. Is volatility acceptable?
3. Is the instrument outperforming its benchmark/sector?
4. Is the current event confirmed by participation?

### Persistence and hysteresis

Threshold-only regimes will chatter around cutoffs. Add:

- entry threshold greater than exit threshold;
- two closed bars of confirmation;
- minimum state duration;
- cooldown after exit;
- explicit transition rules.

This is where recursive state is appropriate. Initialize it with `CompoundValue`; Thinkorswim documents `CompoundValue` specifically for recursive studies ([Schwab CompoundValue documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Others/CompoundValue)).

---

## 6. Repainting, execution, and alerts

### Repainting assessment

The supplied study has no negative price offsets and does not use future values. Therefore, it does **not** exhibit classic historical look-ahead repainting. EMA prefetch is historical initialization, not future leakage; Thinkorswim states that `ExpAverage` uses prior bars to become range-independent ([Schwab past-offset and prefetch documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/tutorials/Advanced/Chapter-12---Past-Offset-and-Prefetch)).

However, every input based on the current bar’s high, low, close, and volume changes while that bar forms. Regime labels can appear and disappear intrabar. That is live-bar flicker, and it can create optimistic visual recollection if traders remember the signal but not the failed interim states.

For higher-integrity signals:

```thinkscript
def longSetupClosed = longSetupRaw[1];
def newLongSignal = longSetupClosed and !longSetupRaw[2];
Alert(newLongSignal, "Regime Council long setup", Alert.BAR, Sound.Ding);
```

Thinkorswim’s `Alert` function triggers from a Boolean condition and supports once-per-bar alerts ([Schwab Alert documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Others/Alert)). The one-bar offset intentionally waits for confirmation; it should be reflected in the backtest fill.

### The study has guidance but no trade signals

Labels such as “All Systems Green,” “Exit Zone,” and “Fade Setup” are not executable definitions. Add separate Booleans for:

- `longSetup`;
- `longEntry`;
- `longExit`;
- `shortSetup`;
- `shortEntry`;
- `shortExit`;
- `riskBlock`.

For validation, create a separate strategy study using `AddOrder`. Thinkorswim adds an order on the next bar when its condition is true, with next-bar open as the default modeled price ([Schwab AddOrder documentation](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Others/AddOrder)). This avoids implicitly treating a closing-bar signal as if it were filled at that same close.

Alerts should fire only on a state transition or threshold cross, not on every bar that remains in a regime.

---

## 7. ThinkScript code quality and performance

### Computation

The code performs:

- seven rolling means and seven rolling standard deviations for components;
- another mean/standard deviation for `sumZZ`;
- another mean/standard deviation for the adaptive block;
- 21 component EMA calls;
- one aggregate EMA;
- a cumulative `TotalSum` that is immediately differenced.

This is usually manageable on one chart but unnecessarily heavy for many symbols, watchlist columns, or scans. Improvements:

1. Delete `TotalSum` and calculate signed volume directly.
2. Define `sumVolume = Sum(volume, length)` once for CMF.
3. Use a reusable `script Z` block to prevent inconsistent guards and baselines.
4. Use one smoothing pass.
5. Remove unused/dead plots and diagnostic labels in production.
6. Build separate chart, scan, and strategy variants rather than making one script do everything.

### Histogram “stacking”

The seven histogram plots are cumulative values all painted from zero. They are overlaid, not true non-overlapping stacked segments. Later plots can obscure earlier ones, and the visible color depends on plot order and sign. For diagnosis, either:

- plot each standardized component as a thin line;
- plot group scores in separate rows;
- use clouds between cumulative boundaries if true stacked bands are required;
- show a contribution table/labels only on the last bar.

The visualization should never be mistaken for seven independent confirmations.

### Defensive checks

Add validation or safe floors for:

- `zLength > 1`;
- smoothing length at least 1;
- `open != 0`;
- adequate warm-up before signals;
- nonzero standard deviation;
- missing secondary-symbol data;
- regular-hours versus extended-hours behavior;
- low-liquidity symbols and zero-volume bars.

The regime output should be `NaN` or “WARMING UP” until all longest-lookback features are valid rather than returning false neutrality.

---

## 8. Recommended implementation sequence

### Priority 0 — Correctness before optimization

1. Replace typical price with real VWAP, or rename the feature “bar close location.”
2. Split unsigned `volumeZ` from directional `signedFlowZ`.
3. Remove OBV change from the composite because it duplicates signed volume.
4. Correct “lower = smoother.”
5. Delete or fully wire the adaptive block.
6. Rename causal labels such as “retail,” “smart money,” and “helicopter money” to observable descriptions.

These changes may alter historical labels substantially. That is desirable: the current labels are partially driven by misdefined variables.

### Priority 1 — Rebuild the signal architecture

1. Use lagged baselines for current-bar surprises.
2. Group correlated inputs into momentum, flow, and location scores.
3. Add volatility state and trend-quality/chop state.
4. Separate persistent state from event flags.
5. Use consistent smoothing and explicit horizon presets.
6. Add hysteresis, persistence, and closed-bar confirmation.

### Priority 2 — Add context and execution

1. Add SPY and sector relative strength.
2. Add market breadth where available.
3. Add higher-timeframe state confirmation.
4. Add liquidity and spread proxies.
5. Define exact entries, exits, invalidation, ATR-based risk, and alerts.
6. Keep the indicator advisory: the broader council’s macro, risk, and behavioral blocks should remain external vetoes rather than being inferred from a chart oscillator.

### Priority 3 — Validate before tuning

For every rule and regime, record:

- number of firings and percentage of bars;
- median and mean forward returns at 1, 3, 5, 10, and 20 bars;
- hit rate with confidence interval;
- expectancy in R-multiples after spread/slippage;
- maximum adverse and favorable excursion;
- turnover and average holding period;
- maximum drawdown, profit factor, Sharpe/Sortino;
- transition frequency and median regime duration;
- performance by volatility state, symbol, sector, year, and long/short side.

Use chronological walk-forward testing:

1. **Development period:** define features and economic rationale.
2. **Calibration period:** estimate thresholds/weights.
3. **Validation period:** select no further parameters.
4. **Sealed holdout or paper-trade period:** one final evaluation.

Include delisted/failed names where relevant, realistic costs, earnings gaps, and extended-hours assumptions. Do not tune all 15+ thresholds on the same history. Bailey et al. show that repeated strategy selection on the same data increases false discoveries and propose comparing in-sample winners with their out-of-sample ranks through the Probability of Backtest Overfitting framework ([Bailey et al., *The Probability of Backtest Overfitting*](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)).

### Required ablation tests

Run the complete model and then remove one group at a time:

- no momentum group;
- no flow group;
- no VWAP/location group;
- no volatility gate;
- no market-context gate;
- no multi-timeframe confirmation.

If removing a component does not reduce out-of-sample expectancy or risk-adjusted performance, it is complexity without demonstrated value. Also compare:

- current 20-bar internal z-score;
- lagged 60-bar z-score;
- lagged 100/252-bar z-score;
- capped z-score;
- rank/percentile or robust median/MAD score;
- one EMA versus triple EMA;
- hard 11-rule classifier versus state-plus-event architecture.

Do not optimize for win rate alone. A filter can raise win rate by eliminating high-payoff outliers or by producing very few trades. Primary objectives should be after-cost expectancy, drawdown, tail loss, stability, and sufficient sample size.

---

## 9. A practical version-2 blueprint

The following is the recommended logical flow, not a drop-in full rewrite:

```text
RAW DATA
  price, true VWAP, volume, benchmark, sector, ATR
      |
CAUSAL FEATURES (all baselines lagged)
  return surprise
  MACD/RSI momentum
  true-VWAP distance in ATR units
  unsigned volume surprise
  signed-flow surprise
  CMF
  relative strength
      |
GROUP SCORES
  momentum | flow | location | relative strength
      |
STATE FILTERS
  trend direction | trend quality/chop | volatility | market/breadth
      |
PERSISTENT STATE
  up/range/down × low/normal/high volatility
      |
EVENT TAGS
  breakout | breakdown | exhaustion | capitulation | divergence
      |
TRADE GATE
  setup + state + council risk/macro veto + liquidity
      |
CLOSED-BAR TRIGGER
  one-shot alert; next-bar modeled entry; explicit stop/exit
```

An initial high-conviction long candidate might require:

- higher-timeframe uptrend;
- normal—not extreme—volatility;
- positive SPY and sector relative strength;
- actual close above a prior range/Keltner boundary;
- unsigned volume z-score above a calibrated threshold;
- positive flow score;
- no bearish breadth or macro veto;
- signal confirmed on the closed bar;
- projected reward-to-risk above the council’s minimum.

That construction is more likely to improve trade quality than adding an eighth oscillator because each condition answers a different question.

---

## Final assessment

The script’s central idea—normalize heterogeneous evidence and combine it into an interpretable council—is sound. The implementation currently overstates what the evidence supports. The “VWAP” and signed-volume defects should be fixed immediately; OBV duplication should be removed; the composite should be grouped by latent factor; and regime state should be separated from transient events.

The best path to “more successful trades” is not to make the labels more elaborate. It is to make them **causal, orthogonal, persistent, context-aware, executable, and falsifiable**. A leaner model with three independent group scores, a real volatility/trend state, market confirmation, closed-bar triggers, and rigorous walk-forward validation is likely to be more reliable than the present 11-rule taxonomy—even if it produces fewer signals.
