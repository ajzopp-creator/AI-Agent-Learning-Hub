# Regime Council for ThinkOrSwim — Deep Technical Review

**Reviewer angle:** rather than opine on the design, I rebuilt the entire study line-by-line in Python (population `StDev`, Wilder RSI, `alpha = 2/(length+1)` EMA — all matching thinkScript semantics) and ran it over real data: SPY / NVDA / AAPL 5-minute bars (2026-06-16 → 2026-09-02, 4,218 bars each) and 5 years of daily bars (1,255 bars each), pulled from Yahoo Finance's chart API. Every number below is measured on the actual code, not estimated.

Replica + analysis scripts are in the workspace: `regime_replicate.py`, `analyze1.py`–`analyze7.py`, `rule_variant_results.csv`.

---

## 1. Bottom line

The study is a well-crafted *visualization* built on a statistically invalid *aggregation*. Six findings dominate everything else:

| # | Finding | Evidence |
|---|---|---|
| 1 | The 7 z-scores are not 7 independent signals — effective dimensionality is **~3.2–3.5**, and two of them are algebraically the same primitive | PCA participation ratio 3.19–3.45; `obvChange ≡ signed volume` exactly |
| 2 | The triple EMA silently **re-weights** the ensemble: after smoothing, CMF+RSI+MACD supply **~77%** of `sumZ` variance, and VWAP/VOL/OBV/PctGain **~23%** combined (design intent: 14.3% each) | variance-contribution decomposition, 3 datasets |
| 3 | `upperExtreme = 7.5` / `lowerExtreme = -7.5` are **unreachable**: they fire on **0.00%–0.19%** of bars. The "highest bullish color" is decorative | P(sumZema ≥ 7.5) = 0.000% (SPY 5m & daily), 0.024% (NVDA 5m) |
| 4 | **3 of 11 regimes are structurally impossible or permanently masked** (STEALTH ACCUMULATION, BULL TRAP, HELICOPTER MONEY, FIRE SALE never appear as the final state), and 97.6–97.9% of bars fall through to the trivial UPTREND/DOWNTREND/RANGE BOUND branch | regime frequency table |
| 5 | On 5-minute charts, **46% of all "HIGH VOL" flags land in the last 30 minutes of the session** and the 09:30 bar is flagged 16–55% of the time vs a 4% baseline — the volume "regime" is largely a clock artifact, not information | time-of-day breakdown |
| 6 | The composite's directional information content is **~0** (\|Spearman IC\| ≤ 0.07, sign flips by symbol), and where it is non-zero it is **mean-reverting** — the opposite of the "Trend Following" guidance the label prints | IC tables + rule variants |

None of these are fatal to the *idea*. They are fatal to the *current calibration*. Section 10 has a prioritized fix list and Section 11 a drop-in rewrite of the parts that matter.

---

## 2. Statistical validity of the z-score layer

### 2.1 Two of the seven inputs are the same number

This is provable from the source, not just correlation:

```
def obv = TotalSum(if close > close[1] then volume else if close < close[1] then -volume else 0);
def obvChange = obv - obv[1];
```

`TotalSum` "returns the sum of all values from the first bar to the current" ([thinkorswim Learning Center](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Math---Trig/TotalSum)). A cumulative sum differenced by one bar returns the summand exactly. I verified numerically: `obvChange == signed volume` is `True` on every bar of all six datasets. So:

- `obvZ` = z-score of **signed volume**
- `adjVolumeZ` = **sign-flipped** z-score of volume

These are two encodings of one primitive. Correlation is diluted only because the mean/σ are taken over different series; conditioned on bar direction the redundancy is obvious:

| Dataset | corr(obvZ, adjVolumeZ) all bars | up bars only | down bars only |
|---|---|---|---|
| SPY 5m | 0.56 | **0.88** | **0.86** |
| NVDA 5m | 0.42 | 0.83 | 0.79 |
| SPY daily | 0.27 | 0.74 | 0.74 |

Also note `TotalSum` makes the OBV level dependent on the chart's first loaded bar — harmless here only because the difference cancels it, which means the whole OBV block is pure wasted computation.

### 2.2 VWAP distance is not VWAP distance — it is the CMF numerator

```
def vwap = (high + low + close) / 3;      # this is Typical Price, not VWAP
def vwapDist = close - vwap;              # = (2c - h - l)/3
def mfMultiplier = ((close-low)-(high-close))/(high-low);   # = (2c - h - l)/(h - l)
```

`vwapDist` and the Chaikin money-flow multiplier share the **identical numerator** `(2c − h − l)`; they differ only in denominator (a constant 3 vs the bar range). And `pctGain = (close − open)/open` measures nearly the same thing — where the close sits relative to the bar. Measured:

corr(vwapZ, pctGainZ) = **0.87 / 0.87 / 0.91 / 0.90** (SPY 5m / NVDA 5m / SPY daily / NVDA daily).

Two further redundancies: corr(rsiZ, macdZ) = **0.75–0.82** (both are EMA-smoothed close momentum; TOS RSI uses Wilder's average by default, per the [RSI study docs](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/R-S/RSI)), and corr(cmfZ, rsiZ) = 0.50–0.64.

Correlation matrix, SPY 5-minute (NVDA/AAPL/daily are within ±0.06 of these):

|  | vwapZ | adjVolZ | obvZ | cmfZ | rsiZ | macdZ | pctGainZ |
|---|---|---|---|---|---|---|---|
| **vwapZ** | 1.00 | 0.12 | 0.60 | 0.24 | 0.34 | 0.17 | **0.87** |
| **adjVolZ** | | 1.00 | 0.56 | 0.12 | 0.16 | 0.09 | 0.16 |
| **obvZ** | | | 1.00 | 0.20 | 0.37 | 0.18 | **0.69** |
| **cmfZ** | | | | 1.00 | 0.50 | 0.42 | 0.19 |
| **rsiZ** | | | | | 1.00 | **0.75** | 0.38 |
| **macdZ** | | | | | | 1.00 | 0.19 |

Eigenvalues: 3.19, 1.54, 1.06, 0.64, 0.25, 0.21, 0.11 → PC1 = 45.6% of variance, PC1+PC2 = 67.6%, **participation ratio = 3.45 effective dimensions**. So `sumZ` is a 7-term sum of ~3 facts: *close-in-bar / short momentum*, *participation*, *slow trend*.

### 2.3 Why that breaks the thresholds

Summing correlated z-scores is only "adding standard deviations" if they are independent. For independent unit-variance components, SD(Σ) = √7 = 2.65. Measured SD of the raw 7-z sum: **5.41 / 5.51 / 5.45 / 5.34**. The composite is ~2× more volatile than the implicit assumption, which is exactly why ±2.0 ("moderate") is not a moderate reading at all:

| Threshold on `sumZema` | Intended meaning | Actual firing rate (SPY 5m / NVDA 5m / SPY daily) |
|---|---|---|
| ≥ +2.0 | moderate bullish | **24.1% / 25.2% / 22.1%** |
| ≤ −2.0 | moderate bearish | **24.5% / 23.7% / 29.3%** |
| ≥ +7.5 | extreme bullish | **0.000% / 0.024% / 0.000%** |
| ≤ −7.5 | extreme bearish | 0.142% / 0.190% / 0.000% |

`sumZema` is also platykurtic (excess kurtosis −0.48 to −0.76): its 99th percentile is only ≈ +5.2 (5m) / +4.6 (daily). So the study spends ~50% of its life in a "moderate" colour and ~0% in the "extreme" colour it was designed to highlight. **Empirically correct replacements: moderate ≈ ±2.7 (≈1σ, ~30% of bars), extreme ≈ ±4.2 (95th pct) or ±5.2 (99th pct) on 5m.** Better still, derive them at runtime (Section 11).

The right fix for correlated aggregation is not just threshold tuning — it is whitening. The canonical finance version is Mahalanobis distance: Kritzman and Li's **turbulence index** measures "multivariate unusualness" by inverting the covariance matrix, precisely so that correlated inputs cannot double-count ([Portfolio Optimizer](https://portfoliooptimizer.io/blog/the-turbulence-index-measuring-financial-risk/), [Kritzman & Li, *Skulls, Financial Turbulence, and Risk Management*, FAJ 2010](https://www.top1000funds.com/wp-content/uploads/2010/11/FAJskulls.pdf); the technique traces back to [Mahalanobis distance](https://en.wikipedia.org/wiki/Mahalanobis_distance)). A full covariance inversion isn't practical in thinkScript, but block-averaging (Section 11) captures most of the benefit.

### 2.4 Per-component tails are wildly inconsistent — one z threshold does not mean one rarity

The regime block applies the same numeric cut-offs (1.0, 1.5, 2.0) to all components. Their tail behaviour is not comparable (SPY 5m; Gaussian reference = 4.55% beyond |2|, 0.27% beyond |3|):

| Component | P(\|z\|>2) | P(\|z\|>3) | excess kurtosis |
|---|---|---|---|
| vwapZ | 4.7% | 0.6% | +0.25 |
| **adjVolumeZ** | **8.8%** | **4.1%** | **+2.33** |
| obvZ | 5.6% | 1.7% | +0.85 |
| cmfZ | 9.7% | 0.4% | −0.81 |
| rsiZ | 10.9% | 0.8% | −0.62 |
| **macdZ** | **13.5%** | 1.2% | −0.75 |
| pctGainZ | 4.9% | 0.8% | +0.45 |

So `volSpike = 2.0` is a **1-in-11** event, `macdPos = 1.5` is roughly a 1-in-4 event, and `rsiPos = 2.0` a 1-in-9 event. The thresholds imply a shared "σ" language that the data doesn't honour. Volume is the worst offender because raw share volume is heavy-tailed; the literature models it as approximately log-normal in the main body of the distribution ([arXiv:1904.01412](https://arxiv.org/pdf/1904.01412)) with power-law upper tails ([Sinha et al.](https://www.imsc.res.in/~sitabhra/papers/Vikram_Sinha_Econophysics_2011.pdf)). Taking a log first cuts kurtosis from +2.05 to +0.03 and P(z>3) from 4.08% to 1.09% (SPY 5m) — a one-line fix with real effect.

Also structural: `StDev` is a **population** standard deviation (`Sqrt(Average(Sqr(data),length) − Sqr(Average(data,length)))`, dividing by `length`, per the [StDev reference](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Statistical/StDev)), and it is computed over the *same* 20 bars that include the current observation. With n = 20 and the point inside its own window, |z| is mathematically bounded at (n−1)/√n = **4.25**. Every dataset above tops out at 4.0–4.3 — that is the bound, not the market. A "z-score of 5" can never happen, so any threshold above ~4 is dead code.

### 2.5 Non-stationarity: the 20-bar window and the trading clock

On 5-minute bars a 20-bar window is 100 minutes and spans overnight gaps and session boundaries with no reset. That produces systematic, mechanical distortions:

| SPY 5m, time of day | mean adjVolumeZ | P(adjVolumeZ > 2) | mean \|pctGainZ\| |
|---|---|---|---|
| 09:30 | +0.23 | **16.4%** (NVDA: **54.5%**) | 1.86 (NVDA 2.29) |
| 09:35 | +0.10 | **0.0%** | 0.93 |
| 09:40 | −0.05 | **0.0%** | 1.19 |
| 15:45 | +0.36 | 33.3% | 0.76 |
| 15:50 | −0.13 | 42.6% | 1.48 |
| 15:55 | −0.62 | 42.6% | 1.32 |
| *all bars* | — | 4.0% | — |

**46.2% of every "HIGH VOL" event on SPY (37.2% on NVDA) occurs in the final 30 minutes**, a window that is 7.7% of bars; 09:35–09:45 can *never* be flagged because the open bar has just inflated the window's mean and σ. Normalising volume by its own time-of-day profile (log volume ÷ same-bar-of-day median, then z) brings the tail rate back to ~4.3–4.8% and removes the clock effect. This is the single highest-value change for an intraday user.

### 2.6 The "z-score of a z-score" adds almost nothing

`sumZZ` re-standardises `sumZ` over the *same* 20 bars — but `sumZ` has lag-1 autocorrelation of **0.96–0.97** after triple smoothing. Standardising a near-unit-root series against a 20-bar window measures "is the composite above its own very recent average", which is largely a differencing operation. Consequences: |sumZZ| > 2 occurs on 13.1–14.3% of bars (Gaussian: 4.6%), |sumZZ| > 3 on 0.24–0.62%, and the "EXTREME" label (|sumZZ| > 3) is nearly unreachable while "STRONG" (>2) is common. Also `sumZZ` inherits the same (n−1)/√n = 4.25 cap.

Worth noting: `sumZ` (used for `sumZZ`) is built from the **smoothed** components, while every regime rule tests the **raw** components — see 5.4.

---

## 3. The triple ExpAverage is not neutral smoothing — it is a hidden weighting scheme

`SmoothingFactor = 3` → α = 2/(3+1) = **0.5** per pass ([ExpAverage docs](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Tech-Analysis/ExpAverage)). Three cascaded passes attenuate high-frequency content by ~1/27 in variance. But the seven inputs have very different spectra: `vwapZ`, `adjVolumeZ`, `obvZ`, `pctGainZ` are essentially bar-level white noise; `cmfZ`, `rsiZ`, `macdZ` are already heavily smoothed (14-bar Wilder / 12-26-9 EMAs). So the filter crushes the fast four and passes the slow three almost untouched:

| Component | SD after triple smoothing | Variance contribution to `sumZ` | Contribution if unsmoothed |
|---|---|---|---|
| vwapZS | 0.36 | 6.3% | 12.7% |
| adjVolumeZS | 0.39 | **3.7%** | 10.2% |
| obvZS | 0.37 | 6.8% | 14.7% |
| cmfZS | 1.02 | **21.2%** | 14.1% |
| rsiZS | 1.01 | **26.1%** | 18.5% |
| macdZS | 1.16 | **29.4%** | 16.5% |
| pctGainZS | 0.36 | 6.4% | 13.3% |

(SPY 5m; NVDA 5m and SPY daily reproduce this to within ~3 points — CMF+RSI+MACD = 76.7% / 75.1% / 76.7%.)

Two consequences:

1. **The composite is a slow trend indicator wearing a volume/flow costume.** Volume — arguably the whole point of a "participation" council — contributes 3.7% of the signal's variance.
2. **The stacked histogram lies visually.** Each colour band's height is proportional to its smoothed contribution, so the orange (VWAP) / magenta (VOL) / yellow (OBV) bands are visually squashed by construction; a viewer reads that as "flow is quiet" when it is really "the filter removed it".

**Lag.** Measured by cross-correlation argmax, the triple EMA delays each component by **2 bars**, `sumZ` by **2 bars**, and `sumZema` (a 4th EMA pass, length 9) by **5 bars**. Correlation between the raw and displayed `vwapZ` is only **0.33 at lag 0** (0.49 at lag 2) — the label `VWAP_Z: x.xx` is showing something that has little to do with the current bar's VWAP stretch. On a 5-minute chart, 5 bars = 25 minutes of latency on the primary plot; for RSI/MACD components the true latency is larger still, since Wilder(14) and EMA(26) smoothing precede it.

If the goal is a smooth *wave* look with less delay, use a zero-lag-ish construction (e.g. `2*EMA(x,n) − EMA(EMA(x,n),n)`, i.e. DEMA-style, or Hull) or, cleaner: apply *equal* smoothing to *comparable* inputs only, and don't smooth what you then threshold.

---

## 4. Does any of it predict? (the uncomfortable part)

Spearman rank IC of each signal against forward returns (5m: 12 bars ahead = 1 hour; daily: 5 days):

| Signal | SPY 5m | NVDA 5m | AAPL 5m | SPY daily | NVDA daily |
|---|---|---|---|---|---|
| sumZ | −0.034 | −0.052 | +0.037 | −0.002 | +0.016 |
| sumZema | −0.022 | −0.011 | −0.006 | +0.002 | +0.036 |
| **sumZZ** | **−0.027** | **−0.068** | **+0.058** | −0.002 | −0.016 |
| best single component | cmfZ −0.066 | macdZ −0.065 | — | pctGainZS −0.064 | macdZS +0.033 |

Everything is inside noise (|IC| ≤ 0.07), and **the sign is not stable across symbols**. Where it is non-zero on SPY and NVDA it is *negative* — high composite readings precede lower returns. Decile analysis on NVDA 5m makes this vivid: decile 1 (lowest sumZZ) → +0.267% mean 1-hour forward return, 56.9% win; decile 6 → −0.114%, 46.4% win.

Directional rule tests (long unless stated; forward 12 bars on 5m, 5 days on daily):

| Rule | SPY 5m | NVDA 5m | AAPL 5m | SPY daily | NVDA daily | AAPL daily |
|---|---|---|---|---|---|---|
| baseline (all bars) | 51.4% / t 1.27 | 51.0% / 1.79 | 52.6% / 2.18 | 59.0% / 3.95 | 57.7% / 6.09 | 55.0% / 3.65 |
| **`sumZZ > 1` → long** (script's "Trend Following") | 49.8% / **0.12** | 48.8% / **−0.96** | 56.2% / 5.23 | 58.3% / 1.83 | 58.4% / 4.43 | 54.5% / 0.15 |
| `sumZZ < −1` → long | 52.0% / 2.77 | **55.0% / 4.97** | — | 59.0% / 2.04 | — | — |
| **`sumZZ < −2` and price > EMA200** (fade the dip) | 54.6% / 1.86 | **62.7% / 3.19** | 40.8% / 0.64 | **64.4% / 2.89** | **80.0% / 5.29** | 50.0% / −1.01 |
| `sumZZ > 2` and price < EMA200 → short | 50.0% / −0.40 | 66.7% / 1.46 | 32.6% / −4.05 | 33.3% / −1.89 | 56.2% / −0.25 | 37.0% / −2.33 |

Read this carefully, because the honest conclusion cuts both ways:

- The script's own action guidance ("`sumZZ > 1` → Trend Following") **fails to beat buy-and-hold on 4 of 6 datasets** and is negative on NVDA 5m.
- The mirror-image rule (fade a depressed composite inside an uptrend) beats baseline on SPY 5m, NVDA 5m, SPY daily and NVDA daily — and *loses* on both AAPL series.
- Regime-conditional returns show the same polarity confusion: on NVDA 5m, `BREAKDOWN CONFIRMED` (n=43) averaged **+0.63%** over the next hour with a 58% win rate (t = +2.03), while `BREAKOUT CONFIRMED` (n=31) averaged **−0.19%**, 39% win. On NVDA daily, `BREAKDOWN CONFIRMED` (n=16) averaged **+4.86%** over 5 days, 81% win (t = +2.64). The bearish labels were the bullish signals.

**Interpretation.** This composite is an *oscillator*, not a trend confirmer — as constructed it is a stretched-vs-recent-history measure with roughly zero standalone directional edge whose sign depends on the instrument's mean-reversion/momentum character. Fixed prose like "All Systems Green" / "Trend Following" bakes in a directional assumption the math does not support. That is the deepest reason the study doesn't produce "more successful trades": **it labels states without ever measuring what follows those states.**

*Sample caveats, stated plainly:* 5m samples cover 2.5 months and one volatility environment; regime cells have n = 4–44, so individual t-stats there are indicative only. I tested ~30 rule/parameter combinations, so a naive best-of t-stat needs deflation for selection bias — the standard corrections are the [Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675) and the [Probability of Backtest Overfitting / CSCV](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253) of Bailey & López de Prado. The robust claim is not "fade extremes works"; it is **"the shipped polarity is unvalidated and at least as often wrong as right."**

---

## 5. Audit of the 11-regime classifier

### 5.1 Firing frequencies (measured)

| # | Regime | SPY 5m final / raw | NVDA 5m final / raw | SPY daily final / raw |
|---|---|---|---|---|
| 1 | BREAKOUT CONFIRMED | 22 / 22 | 31 / 31 | 0 / 0 |
| 2 | BREAKDOWN CONFIRMED | 36 / 36 | 44 / 44 | 25 / 25 |
| 3 | PARABOLIC MOVE | 7 / **12** | 9 / **15** | 0 / 0 |
| 4 | CAPITULATION | 6 / **13** | 7 / **15** | 0 / **10** |
| 5 | RETAIL FOMO | 2 / 2 | 0 / 0 | 0 / 0 |
| 6 | MOMENTUM CLIMAX | 16 / **29** | 22 / **42** | 1 / 1 |
| 7 | **STEALTH ACCUMULATION** | **0 / 0** | **0 / 0** | **0 / 0** |
| 8 | **BULL TRAP** | **0 / 0** | **0 / 0** | **0 / 0** |
| 9 | BEAR TRAP | 11 / 11 | 10 / 10 | 0 / 0 |
| 10 | **HELICOPTER MONEY** | **0** / 6 | **0** / 10 | 0 / 0 |
| 11 | **FIRE SALE** | **0** / 1 | **0** / 2 | 0 / 0 |
| 0 | none (falls through) | **97.63%** | **97.08%** | **97.89%** |

("final" = after `else if` precedence; "raw" = clause true in isolation.)

### 5.2 Three rules are logically self-contradicting, not merely rare

Because `obvZ` and `adjVolumeZ` are both functions of signed volume (§2.1), several clauses ask for states the algebra forbids:

- **Rule 7 / STEALTH ACCUMULATION**: `obvZ > 1.5*obvPos and cmfZ > cmfPos and adjVolumeZ < volPos/2`. `obvZ > 1.5` essentially requires a large *up*-volume bar, which forces `adjVolumeZ` high — while the rule demands `adjVolumeZ < 0.5`. Measured P(obvZ>1.5 **and** adjVolumeZ<0.5) = **0.166% / 0.213% / 0.081%**, and with the CMF and pctGain conditions added: **exactly 0.0000% on all three datasets** (0 of 9,671 bars). "Smart money quietly accumulating" is unreachable by construction.
- **Rule 8 / BULL TRAP**: `adjVolumeZ > 1 and obvZ < −1` — high signed-volume z with strongly negative signed-volume z. P = 0.21% / 0.38% / 0.97% for the pair; **0 occurrences** once `cmfZ < −1` and `pctGainZ > 0` are stacked on.
- **Rule 5 / RETAIL FOMO**: `adjVolumeZ > 2 and obvZ < 0.5` — P = 0.14–0.17%; fires 2 times in 4,218 bars on SPY, 0 on NVDA.

These four "most interesting" regimes (the divergence/trap states, which are exactly where an edge would live) are the ones the construction makes impossible. **The fix is not threshold tuning; it is giving the flow axis a genuinely independent second measurement** — e.g. up-volume vs down-volume from a lower aggregation, or bar-range-weighted delta, so "price up while flow down" becomes expressible.

### 5.3 Clauses are not mutually exclusive, and precedence silently deletes labels

Multiple clauses are simultaneously true on 0.59–0.81% of bars — which sounds small until you compare it to the 2.1–2.9% of bars where *any* regime fires: **roughly a quarter of all regime events are ambiguous**. Overlaps found on SPY 5m: BREAKOUT∩MOMENTUM CLIMAX (12), BREAKOUT∩HELICOPTER MONEY (6), BREAKOUT∩PARABOLIC (5), BREAKDOWN∩CAPITULATION (7), PARABOLIC∩HELICOPTER (4), MOMENTUM CLIMAX∩HELICOPTER (2), CAPITULATION∩FIRE SALE (1).

Because `else if` resolves by *authoring order*, not by severity or specificity:
- HELICOPTER MONEY (rule 10) and FIRE SALE (rule 11) — the most extreme states in the taxonomy — **never display**, always pre-empted by rules 1/3/6 and 2/4.
- CAPITULATION loses 54% of its occurrences to BREAKDOWN CONFIRMED; MOMENTUM CLIMAX loses 45–48% to BREAKOUT.

Fix: order clauses by *specificity* (most restrictive first: 10, 11, 3, 4, 6, 1, 2, then the divergences), or better, score each state and take the max, or emit a bitmask so co-occurring states are visible.

### 5.4 Regime logic reads raw z, labels display smoothed z

`sumZZ` is derived from the *smoothed* sum, but every other term in the regime block (`cmfZ`, `obvZ`, `adjVolumeZ`, `pctGainZ`, `rsiZ`, `macdZ`, `vwapZ`) is **raw**, while the on-screen labels print the *smoothed* versions. The two disagree even in sign on:

| | vwapZ | adjVolZ | obvZ | cmfZ | rsiZ | macdZ | pctGainZ |
|---|---|---|---|---|---|---|---|
| sign disagreement (SPY 5m) | **38%** | **39%** | **37%** | 19% | 19% | 17% | **37%** |

So the panel can read `VOL_Z: −0.4` at the exact moment the classifier is firing on `adjVolumeZ = +2.3`. This makes the study impossible to debug or trust by eye — and it means the displayed labels cannot be used to reason about why a regime appeared. Pick one representation (I'd use raw for logic, and display raw with a *separate* smoothed plot).

### 5.5 Label flicker

Counting the displayed state (regime, else UPTREND/DOWNTREND/RANGE BOUND): the label **changes every 5.0–5.4 bars** on average (784 changes / 4,218 bars on SPY 5m), median run length 4–5 bars, 90th percentile 10–11. On a 5-minute chart that is a new market narrative every ~27 minutes. There is no hysteresis, no minimum dwell time, and no confirmation requirement. Real regime frameworks impose persistence explicitly — an HMM's transition matrix penalises switching, which is precisely why HMMs are the default tool for regime inference ([QuantStart](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/), [Quantified Strategies](https://www.quantifiedstrategies.com/hidden-markov-model-market-regimes-how-hmm-detects-market-regimes-in-trading-strategies/)). A cheap thinkScript analogue: require the condition to hold N consecutive bars, and require asymmetric enter/exit thresholds (Schmitt trigger).

### 5.6 Overfitting risk

11 rules × 2–5 conditions each × 15 tunable thresholds ≈ 40+ free parameters, hand-tuned, with no out-of-sample test and — critically — **no outcome variable anywhere in the design**. The rules were selected on *plausibility of the narrative*, not on measured forward behaviour, so they are not "overfit" in the usual sense; they are *unfit*. That is worse: overfit rules at least worked once. Any validation program should score each regime by forward return / hit rate / MFE-MAE and be corrected for the number of variants tried (PBO/CSCV, deflated Sharpe — [Bailey et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)).

---

## 6. The dead adaptive block

```
def adaptiveMean  = Average(sumZZ, zLength);
def adaptiveStdev = StDev(sumZZ, zLength);
def adaptiveUpper = adaptiveMean + adaptiveStdev;      # only 1σ
def adaptiveLower  = adaptiveMean - adaptiveStdev;
plot unusualExtreme = sumZZ > adaptiveUpper or sumZZ < adaptiveLower;
```

Three separate problems:

1. **It is triple-standardised.** `sumZZ` is already a z-score of a z-score; this makes it a z-score of a z-score of a z-score, over the *same* 20 bars for the third time. Any information about "unusual" magnitude has been normalised away by construction.
2. **±1σ is not unusual.** Measured firing rate: **53.4% (SPY 5m), 53.0% (NVDA 5m), 50.8% (SPY daily)**. It flags a coin flip. A meaningful "unusual extreme" needs (a) a *long* baseline (200+ bars, or the day's/prior sessions' distribution), (b) ≥2σ or a percentile rank, and (c) a non-normalised input.
3. **It is plotted as a boolean into a panel scaled to ±10.** A 0/1 line at the bottom of a lower study whose y-range is roughly −8 to +7 is visually invisible, and it also perturbs auto-scaling. Use `AddCloud`, `AssignValueColor` on the existing plot, an arrow via `SetPaintingStrategy(PaintingStrategy.BOOLEAN_ARROW_UP)`, or [`AddChartBubble`](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Look---Feel/AddChartBubble) / [`AddCloud`](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Look---Feel/AddCloud).

The comment "you'll need to implement using recursive variables" is a red herring: nothing here needs recursion, and `rec` is obsolete anyway — "`rec` variables … can be completely replaced by `def`" ([thinkScript reference](https://toslc.thinkorswim.com/center/reference/thinkScript/Reserved-Words/rec)). What you actually want (state persistence, dwell counters, hysteresis) *is* a legitimate recursive-variable use case, and `def state = if cond then 1 else state[1];` compiles fine.

---

## 7. Other code-quality and thinkScript-specific issues

| Issue | Detail | Fix |
|---|---|---|
| **`input chop = 0.5` unused** | Declared, never referenced. Dead input that implies a chop filter exists — an ADX/choppiness gate is arguably the most valuable missing filter, so this is a promise unkept | implement (see §11: `ADX` or efficiency ratio gate) or delete |
| **`def vwap` shadows the built-in** | thinkScript has a real [`vwap()`](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Fundamentals/vwap) fundamental returning true volume-weighted average price. The script names typical price `vwap`, so every downstream reader mis-reads what `vwapZ` measures | rename to `typicalPrice`, and use `vwap()` if you actually want VWAP stretch (much more useful intraday) |
| **8 plots + 5 labels recomputed every tick** | 7 histogram plots each recomputing partial sums of the same 7 series, plus 7×(Average + StDev) + 3 more Average/StDev pairs. Every `StDev` internally does 2 rolling averages | precompute each `…Smooth` once (already done), build stacks by cumulative `def`s, drop the redundant OBV block entirely (§2.1), consider `plot` count ≤ 4 |
| **`TotalSum` on every bar** | Cumulative from the chart's first bar, then immediately differenced away | replace whole block with `def signedVol = if close>close[1] then volume else if close<close[1] then -volume else 0;` |
| **Chart-range dependence / prefetch** | EMAs use prefetch (ExpAverage fetches ~4×length extra bars) so they are approximately range-independent ([Past/Future Offset and Prefetch](https://toslc.thinkorswim.com/center/reference/thinkScript/tutorials/Advanced/Chapter-12---Past-Offset-and-Prefetch)), but stacked EMAs-of-EMAs-of-z-scores whose inputs need 20 bars of warm-up still differ on the first ~30 bars of any chart. Expect small differences across chart lookbacks | ignore the first `zLength + 4*SmoothingFactor` bars; hide plots with `if BarNumber() < warmup then Double.NaN` |
| **Intra-bar repainting of the current bar** | Not lookahead repainting (no future offsets, no HTF aggregation), but every z, label, and regime recomputes tick-by-tick on the forming bar. A regime can appear and vanish before the close | evaluate signals on `[1]` (last closed bar) for anything actionable, and use `Alert(..., Alert.BAR, ...)` |
| **No `Alert()` anywhere** | The study cannot notify you of anything; it must be watched. [`Alert`](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Others/Alert) supports `Alert.BAR` for once-per-bar firing | add alerts on confirmed, closed-bar transitions |
| **Not scannable** | Labels/plots only; nothing exposes a single scannable value | expose one `plot Signal` and one `plot Regime` so the study works in the Scan tab and in Conditional Orders |
| **Stacked-histogram overlap** | Cumulative stacks with `SetLineWeight(4)` overplot each other whenever a component flips sign (the stack is not monotone), so band heights misread when components have opposite signs | plot positive and negative contributions as separate stacks, or use `AddCloud` between successive cumulative sums |

If you later add multi-timeframe confirmation, use the closed higher-TF bar: `close(period = AggregationPeriod.THIRTY_MIN)[1]`. Referencing the *forming* HTF bar is the classic repaint trap — the community guidance is explicit that studies should use the previous HTF bar to avoid repainting ([useThinkScript MTF pitfalls](https://usethinkscript.com/threads/mtf-multi-timeframe-repainting-pitfalls.16359/), [MTF clarification thread](https://usethinkscript.com/threads/clarification-on-multi-timeframe-issue.13704/)).

---

## 8. What a standard regime framework has that this doesn't

| Missing dimension | Why it matters here | Cheapest thinkScript implementation |
|---|---|---|
| **Volatility regime (ATR)** | Zero of the 7 inputs measures volatility, yet every threshold's meaning depends on it. My conditional test shows the composite's IC differs by ATR tercile (SPY daily: −0.087 low-ATR vs +0.042 high-ATR) — the sign of the edge is vol-dependent | `def atrPct = ATR(14)/close;` percentile-rank over 200 bars; gate signals and widen/narrow thresholds by regime |
| **Choppiness / trend-efficiency** | The unused `chop` input. Range-bound tape is where a stretched oscillator whipsaws | `ADX(14) < 20` gate, or efficiency ratio `AbsValue(close-close[n]) / Sum(AbsValue(close-close[1]),n)` |
| **Relative strength vs SPY** | Council role 03 explicitly wants relative strength; the study is 100% single-name absolute | `def rs = close/close("SPY");` then z-score `rs` — one extra line, genuinely orthogonal to all 7 existing inputs |
| **Market breadth / internals** | Distinguishes idiosyncratic moves from index-wide regime | `close("$ADD")`, `close("$TICK")`, `close("$VIX")` z-scores; VIX term structure `close("VIX")/close("VIX3M")` |
| **Multi-timeframe confirmation** | Cuts the 5-bar label flicker dramatically | require sign agreement between the current-TF composite and the same composite on the closed HTF bar |
| **Session/anchored context** | Overnight gaps, opening range, prior-day levels | `vwap()` distance, opening-range breakout state |
| **Outcome measurement** | Nothing in the study knows whether a regime ever worked | see §11's trailing edge monitor |
| **Whitened aggregation** | Correlated inputs double-count (§2.3) | block-average instead of sum |
| **Walk-forward validation** | 40+ hand-set thresholds, no OOS test | export to Python/`pandas` (my replica does this), test across symbols and periods, deflate for multiple testing |

---

## 9. What the study is genuinely good at (keep this)

- The **stacked-contribution visualization** is a legitimately good UX idea for signal attribution — few retail indicators show *why* a composite is where it is.
- The **z-score framing** ("how unusual is this vs recent history") is the right primitive for cross-instrument comparability.
- The **taxonomy** (breakout vs parabolic vs trap vs stealth) is thoughtful and maps well onto the council roles. The vocabulary is worth keeping; only the arithmetic behind it needs replacing.
- Zero lookahead repainting: no future offsets, no HTF references, no `…All` functions in the logic path. That's better hygiene than most published studies.

---

## 10. Prioritized fix list

**P0 — correctness (do these first; they are small and change results materially)**

1. Delete the OBV block; it is algebraically identical to signed volume (§2.1). Replace the freed slot with a genuinely orthogonal input: **relative strength vs SPY**.
2. Log-transform volume and **normalize by time-of-day** before z-scoring (§2.5). Biggest single win for intraday use.
3. Make regime logic and displayed labels use the **same** series (§5.4).
4. Recalibrate thresholds to measured percentiles, or compute them at runtime: moderate ≈ ±1σ of the composite, extreme ≈ 95th/99th percentile. Current ±7.5 is unreachable (§2.3).
5. Rename `def vwap` → `typicalPrice`; if you want VWAP stretch, use `vwap()` (§7).
6. Either implement or delete `chop`; fix or delete the adaptive block; never plot a boolean into a z-scaled panel (§6).

**P1 — statistical integrity**

7. Replace `sumZ = Σ(7 z)` with **block averages** over 3 orthogonal blocks (location/stretch, participation, momentum) — this is the practical stand-in for whitening (§2.3).
8. Standardize the composite over a **long** window (200+ bars) instead of re-z-scoring over the same 20 (§2.6).
9. Reduce the smoothing cascade to one stage on the *fast* inputs only, so the ensemble weighting is intentional rather than a filter artifact (§3). Accept ≤2 bars lag, not 5.
10. Add **hysteresis + minimum dwell** to the regime state (enter at 2σ, exit at 1σ, hold ≥3 bars) to kill the every-5-bar flicker (§5.5).

**P2 — make the regimes usable as trade signals**

11. Reorder clauses by specificity so extreme states are reachable; or score-and-max; or emit a bitmask (§5.3).
12. Rewrite the impossible clauses (7, 8, 5) using an independent flow measure so divergences are expressible (§5.2).
13. Add a **volatility-regime gate** and a **trend filter** (EMA200 or closed-HTF composite sign). In my tests, adding an EMA200 trend filter is what turned the composite from noise into something with a measurable (if symbol-dependent) tilt (§4).
14. Add `Alert()` on **closed-bar** confirmed transitions, and expose one scannable `plot` for the Scan tab (§7).
15. Replace fixed prose ("All Systems Green", "Trend Following") with **measured** guidance from the trailing edge monitor (§11) — the current guidance was directionally wrong in 4 of 6 datasets.

**P3 — validation program (the part that actually produces "more successful trades")**

16. Port the study to Python (my `regime_replicate.py` already does it) and, for each regime: n, mean forward return over 3 horizons, hit rate, MFE/MAE, and stability across symbols/periods.
17. Prune to the ≤4 regimes that survive out-of-sample, and deflate the surviving statistics for the number of variants tried ([Deflated Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675), [PBO/CSCV](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)).
18. If you want a true regime model, fit an HMM offline on 2–3 features (returns, realized vol, participation) and port only the resulting decision boundaries to thinkScript ([QuantStart](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/)).

---

## 11. Drop-in rewrite of the parts that matter (thinkScript)

This is not a cosmetic refactor — it changes the aggregation, the normalization, the thresholds, and adds the missing outcome feedback. Test on paper before trusting it.

```thinkscript
#  REGIME COUNCIL v2  — orthogonalized, clock-normalized, self-calibrating
#  Changes vs v1: OBV removed (identical to signed volume); log+time-of-day volume;
#  3-block averaging instead of 7-way sum; long-window standardization;
#  hysteresis + dwell; closed-bar alerts; trailing edge monitor.
declare lower;

input length          = 14;    # RSI / CMF lookback
input zLength         = 20;    # short normalization window
input baseLength      = 200;   # long window for composite standardization
input barsPerDay      = 78;    # 5-min RTH bars; 26 for 15-min; 1 for daily
input todDays         = 10;    # days of time-of-day volume history
input smoothLen       = 3;     # ONE smoothing pass on fast inputs only
input dwellBars       = 3;     # minimum bars a regime must persist
input evalHorizon     = 12;    # bars ahead used by the edge monitor
input evalLookback    = 500;   # bars of history for the edge monitor
input useRelStrength  = yes;
input benchmark       = "SPY";

def na = Double.NaN;
def warm = Max(baseLength, zLength + 4 * smoothLen);

# ---------- helpers ----------
script zs { input x = close; input n = 20;
    def m = Average(x, n); def s = StDev(x, n);
    plot z = if s == 0 or IsNaN(s) then 0 else (x - m) / s; }

# ---------- BLOCK A: location / stretch (uses REAL vwap, not typical price) ----------
def vw        = vwap();                                   # built-in VWAP
def vwStretch = if IsNaN(vw) or vw == 0 then 0 else (close - vw) / close;
def aVwap     = zs(vwStretch, zLength);
def pctGain   = (close - open) / open * 100;
def aPct      = zs(pctGain, zLength);
def blockA    = (aVwap + aPct) / 2;                       # these are ~0.9 correlated -> average, don't add

# ---------- BLOCK B: participation (log volume, de-seasonalized by time of day) ----------
def todAvgVol = if barsPerDay <= 1 then Average(volume, zLength)
                else (fold i = 1 to todDays + 1 with s = 0.0
                      do s + GetValue(volume, i * barsPerDay)) / todDays;
def rvol      = if todAvgVol <= 0 then 1 else volume / todAvgVol;
def logRvol   = Log(Max(rvol, 0.01));
def volZ      = zs(logRvol, zLength);                     # magnitude only, unsigned
def signedVol = if close > close[1] then volume else if close < close[1] then -volume else 0;
def flowZ     = zs(signedVol / Max(todAvgVol, 1), zLength);  # direction of participation
def mfMult    = if high == low then 0 else ((close - low) - (high - close)) / (high - low);
def cmfRaw    = if Sum(volume, length) == 0 then 0 else Sum(mfMult * volume, length) / Sum(volume, length);
def cmfZ      = zs(cmfRaw, zLength);
def blockB    = (flowZ + cmfZ) / 2;

# ---------- BLOCK C: momentum / trend ----------
def rsiZ      = zs(RSI(length = length), zLength);
def macdH     = MACDHistogram(fastLength = 12, slowLength = 26, MACDLength = 9);
def macdZ     = zs(macdH, zLength);
def blockC    = (rsiZ + macdZ) / 2;                       # ~0.8 correlated -> average

# ---------- BLOCK D: relative strength (genuinely orthogonal) ----------
def rs        = if useRelStrength and close(benchmark) > 0 then close / close(benchmark) else 1;
def blockD    = if useRelStrength then zs(rs, zLength) else 0;

# ---------- composite: equal-weight the BLOCKS, then standardize on a LONG window ----------
def nb        = if useRelStrength then 4 else 3;
def rawComp   = (blockA + blockB + blockC + blockD) / nb;
def comp      = ExpAverage(rawComp, smoothLen);           # ONE pass, ~1 bar lag
def compZ     = zs(comp, baseLength);                     # thresholds now mean something

plot Composite = if BarNumber() < warm then na else compZ;
Composite.SetLineWeight(3);

# ---------- runtime-calibrated thresholds (no magic 7.5) ----------
def sdC   = StDev(comp, baseLength);
def modUp = 1.0;  def modDn = -1.0;      # ~1 sigma of a properly scaled composite
def extUp = 2.0;  def extDn = -2.0;      # ~2 sigma
Composite.AssignValueColor(
    if compZ >= extUp then Color.ORANGE
    else if compZ >= modUp then Color.GREEN
    else if compZ <= extDn then Color.CYAN
    else if compZ <= modDn then Color.DARK_RED
    else Color.LIGHT_GRAY);

plot Zero = if BarNumber() < warm then na else 0;  Zero.SetStyle(Curve.SHORT_DASH);
AddCloud(if compZ >= modUp then compZ else 0, if compZ >= modUp then modUp else 0,
         Color.DARK_GREEN, Color.DARK_GREEN);
AddCloud(if compZ <= modDn then modDn else 0, if compZ <= modDn then compZ else 0,
         Color.DARK_RED, Color.DARK_RED);

# ---------- context gates: volatility regime, chop, higher-timeframe ----------
def atrPct  = ATR(length = 14) / close;
def atrRank = (fold j = 1 to baseLength with cnt = 0
               do cnt + (if GetValue(atrPct, j) < atrPct then 1 else 0)) / baseLength;
def volRegime = if atrRank > 0.7 then 2 else if atrRank < 0.3 then 0 else 1;   # 0 quiet 1 normal 2 stressed
def trending  = ADX(length = 14) >= 20;                    # the 'chop' input v1 never used
def htfComp   = compZ(period = AggregationPeriod.THIRTY_MIN)[1];   # CLOSED htf bar: no repaint
def htfOK_up  = IsNaN(htfComp) or htfComp > 0;
def htfOK_dn  = IsNaN(htfComp) or htfComp < 0;
def trendUp   = close > ExpAverage(close, 200);

# ---------- regime state with hysteresis + minimum dwell ----------
#  ordered MOST SPECIFIC FIRST so extreme states are reachable (v1 buried them)
def cand =
    if  compZ > extUp and volZ > 1.5 and blockA > 1.5 and trending then 10        # HELICOPTER MONEY
    else if compZ < extDn and volZ > 1.5 and blockA < -1.5 and trending then 11   # FIRE SALE
    else if blockA > 1.5 and compZ > extUp then 3                                 # PARABOLIC
    else if blockA < -1.5 and compZ < extDn then 4                                # CAPITULATION
    else if blockC > 1.5 and volZ > 1.0 and blockA > 1.0 then 6                   # MOMENTUM CLIMAX
    else if compZ > modUp and blockB > 1.0 and volZ > 0.5 and trending then 1      # BREAKOUT CONFIRMED
    else if compZ < modDn and blockB < -1.0 and trending then 2                    # BREAKDOWN CONFIRMED
    else if blockA > 0.5 and blockB < -1.0 then 8                                  # BULL TRAP  (now possible:
    else if blockA < -0.5 and blockB > 1.0 then 9                                  # BEAR TRAP   flow is independent)
    else if blockB > 1.0 and volZ < 0 and AbsValue(blockA) < 0.5 then 7            # STEALTH ACCUMULATION
    else if volZ > 1.5 and blockB < 0.5 and blockA > 0 then 5                      # RETAIL FOMO
    else 0;

def dwell  = if cand == cand[1] then dwell[1] + 1 else 1;     # legitimate recursive use
def regime = if dwell >= dwellBars then cand else regime[1];  # confirmed state only
plot RegimeCode = regime;  RegimeCode.SetHiding(yes);          # scannable / conditional-order hook

# ---------- trailing EDGE MONITOR: measure, don't assume, the polarity ----------
#  hit rate of "compZ > modUp" states over the last evalLookback bars, evaluated
#  only on bars old enough to have a realized evalHorizon outcome. No lookahead.
def upN = fold k = evalHorizon to evalLookback with a = 0
          do a + (if GetValue(compZ, k) > modUp then 1 else 0);
def upW = fold k2 = evalHorizon to evalLookback with b = 0
          do b + (if GetValue(compZ, k2) > modUp and GetValue(close, k2 - evalHorizon) > GetValue(close, k2)
                  then 1 else 0);
def dnN = fold k3 = evalHorizon to evalLookback with c = 0
          do c + (if GetValue(compZ, k3) < modDn then 1 else 0);
def dnW = fold k4 = evalHorizon to evalLookback with d = 0
          do d + (if GetValue(compZ, k4) < modDn and GetValue(close, k4 - evalHorizon) > GetValue(close, k4)
                  then 1 else 0);
def upHit = if upN > 0 then upW / upN else Double.NaN;   # P(price higher h bars later | high composite)
def dnHit = if dnN > 0 then dnW / dnN else Double.NaN;   # P(price higher h bars later | low composite)

AddLabel(yes, "EDGE(" + evalHorizon + "b): high-comp " + Round(upHit * 100, 0) + "% (n=" + upN + ")  |  " +
              "low-comp " + Round(dnHit * 100, 0) + "% (n=" + dnN + ")",
    if upHit > dnHit + 0.05 then Color.GREEN
    else if dnHit > upHit + 0.05 then Color.CYAN else Color.GRAY);
AddLabel(yes, if upHit > dnHit + 0.05 then "MODE: MOMENTUM"
              else if dnHit > upHit + 0.05 then "MODE: MEAN-REVERT" else "MODE: NO EDGE",
         Color.WHITE);

# ---------- labels ----------
AddLabel(yes, GetSymbol() + "  Z=" + Round(compZ, 2), Color.WHITE);
AddLabel(yes, "A loc " + Round(blockA, 2) + " | B flow " + Round(blockB, 2) +
              " | C mom " + Round(blockC, 2) + (if useRelStrength then " | D rs " + Round(blockD, 2) else ""),
         Color.LIGHT_GRAY);
AddLabel(yes, "VOL " + Round(volZ, 2) + "  ATRrank " + Round(atrRank * 100, 0) + "%  " +
              (if volRegime == 2 then "STRESSED" else if volRegime == 0 then "QUIET" else "NORMAL"),
         if volRegime == 2 then Color.MAGENTA else Color.GRAY);
AddLabel(regime > 0,
    if regime == 1 then "BREAKOUT CONFIRMED" else if regime == 2 then "BREAKDOWN CONFIRMED"
    else if regime == 3 then "PARABOLIC MOVE"  else if regime == 4 then "CAPITULATION"
    else if regime == 5 then "RETAIL FOMO"     else if regime == 6 then "MOMENTUM CLIMAX"
    else if regime == 7 then "STEALTH ACCUMULATION" else if regime == 8 then "BULL TRAP"
    else if regime == 9 then "BEAR TRAP"       else if regime == 10 then "HELICOPTER MONEY"
    else "FIRE SALE",
    if regime == 1 or regime == 3 or regime == 10 then Color.ORANGE
    else if regime == 2 or regime == 4 or regime == 11 then Color.CYAN else Color.YELLOW);
AddLabel(regime == 0, if !trending then "CHOP - stand down"
                      else if compZ > modUp then "TREND UP (unconfirmed)"
                      else if compZ < modDn then "TREND DOWN (unconfirmed)" else "RANGE BOUND",
         Color.GRAY);

# ---------- alerts on CONFIRMED, CLOSED-bar transitions only ----------
def newRegime = regime != regime[1] and regime > 0 and !IsNaN(close[1]);
Alert(newRegime[1] and regime[1] == 1 and trendUp[1] and htfOK_up[1],
      "REGIME: Breakout confirmed + HTF aligned", Alert.BAR, Sound.Ding);
Alert(newRegime[1] and regime[1] == 2 and !trendUp[1] and htfOK_dn[1],
      "REGIME: Breakdown confirmed + HTF aligned", Alert.BAR, Sound.Bell);
Alert(newRegime[1] and (regime[1] == 3 or regime[1] == 6),
      "REGIME: Exhaustion risk - manage/trim", Alert.BAR, Sound.Chimes);
Alert(compZ[1] < extDn and trendUp[1] and volRegime[1] < 2,
      "SETUP: Composite washed out inside uptrend", Alert.BAR, Sound.Ring);
```

Implementation notes / caveats on the code:
- `zs(...)` is a `script` so the 20 duplicated Average/StDev pairs in v1 collapse to one definition; note that calling a user script with a `period =` argument (`compZ(period = ...)`) only works if the script is defined at top level, so if the HTF line errors on your build, replace it with a plain `close(period = AggregationPeriod.THIRTY_MIN)` comparison — the `[1]` is the important part.
- `vwap()` returns NaN on daily+ aggregations; the `IsNaN` guard falls back to 0 so Block A degrades to `pctGain` only.
- `barsPerDay` must match your chart aggregation for the time-of-day normalization to work; set it to 1 on daily charts.
- The `fold` loops (ATR rank, edge monitor) are the main compute cost — `evalLookback = 500` is fine, 5,000 will crawl.
- The edge monitor is descriptive, not predictive: it tells you what this state *has* paid on this symbol lately, which is exactly the missing feedback loop. Treat n < 30 as noise.

---

## 12. Mapping to your council roles

| Role | What v1 gives it | What to add |
|---|---|---|
| 01 Quant Strategist | nothing on volatility | `atrRank` / `volRegime` (P2 #13) — this role explicitly wants ATR expansion monitoring and v1 has zero volatility inputs |
| 02 Macro Economist | nothing | `$VIX`, VIX/VIX3M term structure, `$ADD`/`$TICK` breadth z-scores (§8) |
| 03 Momentum & Tape Reader | Blocks A/C, but 5-bar-flickering | dwell/hysteresis + relative strength vs SPY (P1 #10, P0 #1) |
| 04 Risk Manager | nothing actionable | ATR-based stop distance in the panel; block entries when `volRegime == 2` |
| 05 Behavioral Judge | prose guidance that was wrong in 4/6 datasets | the edge monitor label — a measured "MODE: NO EDGE" is the strongest anti-force-trade device you can put on a chart |

---

## 13. Limitations of this review

- 5-minute samples cover 2026-06-16 → 2026-09-02 (one regime, one volatility environment); daily samples cover 5 years, 3 symbols. Cross-sectional breadth is thin.
- My Python replica matches thinkScript semantics as documented (population `StDev`, α = 2/(length+1), Wilder RSI) but is not bit-identical to TOS: prefetch warm-up, extended-hours inclusion, and tick-level volume differ. Frequency and correlation results are robust to these; individual regime timestamps may differ slightly.
- Forward-return tables use bar closes with no slippage, commissions, or stop logic. They diagnose *calibration*, not tradability.
- ~30 rule/threshold variants were examined; treat any single t-statistic as inflated by selection until deflated ([DSR](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675) / [PBO](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)).

---

## 14. One-paragraph answer to the question asked

Yes — but not by adding indicators. The three changes with the largest expected effect on *trade success* are, in order: (1) fix the arithmetic so the composite measures what it claims — drop the duplicated OBV term, average correlated blocks instead of summing seven near-collinear z-scores, log/time-of-day-normalize volume, and recalibrate thresholds from measured percentiles instead of an unreachable ±7.5; (2) stop asserting polarity — the study currently prints "Trend Following" on a signal whose measured directional IC is ≈0 and whose sign flips by symbol, so replace fixed prose with a trailing, closed-bar edge monitor that reports what the state has actually paid on this instrument; and (3) add the two context dimensions the framework is missing entirely — a volatility regime (ATR percentile) and an independent trend/HTF filter — plus confirmation dwell and `Alert()` on closed bars, so a "regime" is something you can be notified about and act on rather than a caption that changes every 27 minutes.

---

### Sources

- thinkScript reference: [StDev](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Statistical/StDev) · [ExpAverage](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Tech-Analysis/ExpAverage) · [TotalSum](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Math---Trig/TotalSum) · [rec](https://toslc.thinkorswim.com/center/reference/thinkScript/Reserved-Words/rec) · [Alert](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Others/Alert) · [vwap](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Fundamentals/vwap) · [RSI study (Wilder default)](https://toslc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/R-S/RSI) · [Past/Future Offset and Prefetch](https://toslc.thinkorswim.com/center/reference/thinkScript/tutorials/Advanced/Chapter-12---Past-Offset-and-Prefetch) · [AddCloud](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Look---Feel/AddCloud) · [AddChartBubble](https://toslc.thinkorswim.com/center/reference/thinkScript/Functions/Look---Feel/AddChartBubble) · [reference](https://toslc.thinkorswim.com/center/reference/thinkScript/Reserved-Words/reference)
- MTF repainting practice: [useThinkScript — MTF pitfalls](https://usethinkscript.com/threads/mtf-multi-timeframe-repainting-pitfalls.16359/) · [MTF clarification](https://usethinkscript.com/threads/clarification-on-multi-timeframe-issue.13704/)
- Correlated-signal aggregation / turbulence: [Kritzman & Li, *Skulls, Financial Turbulence, and Risk Management* (FAJ 2010)](https://www.top1000funds.com/wp-content/uploads/2010/11/FAJskulls.pdf) · [Portfolio Optimizer — The Turbulence Index](https://portfoliooptimizer.io/blog/the-turbulence-index-measuring-financial-risk/) · [Mahalanobis distance](https://en.wikipedia.org/wiki/Mahalanobis_distance)
- Regime modelling: [QuantStart — HMM regime detection](https://www.quantstart.com/articles/market-regime-detection-using-hidden-markov-models-in-qstrader/) · [Quantified Strategies — HMM market regimes](https://www.quantifiedstrategies.com/hidden-markov-model-market-regimes-how-hmm-detects-market-regimes-in-trading-strategies/) · [Market Regime Identification Using HMMs (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3406068)
- Backtest validity: [Bailey, Borwein, López de Prado & Zhu — The Probability of Backtest Overfitting (CSCV)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253) · [López de Prado — Deflating the Sharpe Ratio](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2465675)
- Volume distribution: [arXiv:1904.01412 — log-normal volume](https://arxiv.org/pdf/1904.01412) · [Sinha et al. — trading volume distributions](https://www.imsc.res.in/~sitabhra/papers/Vikram_Sinha_Econophysics_2011.pdf)
- Price data: Yahoo Finance chart API (SPY/NVDA/AAPL, 5-minute and daily), retrieved 2026-09-02.
