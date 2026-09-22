# Alphalens Factor Validation — Detailed Summary Mapped to P_300

**Source:** "Factor Analysis in Python (with Alphalens)" — Quant Scientist Newsletter (Matt Dancho, April 21, 2024)
https://quantscience.io/newsletter/b/stock-factor-analysis-alphalens
**Supporting references:** official Alphalens repo (https://github.com/quantopian/alphalens), maintained fork alphalens-reloaded (https://github.com/stefan-jansen/alphalens-reloaded), PyQuant News IC walkthrough (https://www.pyquantnews.com/free-python-resources/real-factor-alpha-how-to-measure-it-with-information-coefficient-and-alphalens-in-python)

---

## 1. What the Newsletter Covered

The edition is a deep dive into factor analysis with Alphalens, the open-source Python library originally built by Quantopian for performance analysis of predictive (alpha) stock factors. Key points from the article:

- **What factor analysis is:** describing variability among observed variables using a smaller number of underlying "factors" that condense information without significant loss.
- **Finance applications:** risk management and portfolio construction, performance attribution, strategic asset allocation.
- **How hedge funds use it:** identifying alpha, style analysis, risk factor modeling, quantitative trading.
- **What Alphalens is:** a library that lets quant analysts and portfolio managers evaluate the effectiveness of alpha factors for stock selection. Integrates with pandas/NumPy/SciPy and is often paired with backtesting libraries such as Zipline.
- **Core Alphalens features:**
  1. Factor analysis (predictive performance of factors on returns)
  2. Returns analysis (forward returns based on factors)
  3. Information Coefficient (IC) — rank correlation between factor values and subsequent returns
  4. Quantile analysis — factor values ranked 1 (worst) to 5 (best)
  5. Turnover analysis — understanding trading costs
  6. Integration with portfolio-construction tools (Pyfolio, Zipline, custom optimizers)

The tutorial's five-step workflow (subscriber code lives in the QS015-alphalens folder):

| Step | Action | Detail |
|---|---|---|
| 1 | Download stock data from yfinance | Universe of stocks to analyze |
| 2 | Make one or more factors | Simple 90-day price change (momentum factor) used to score the universe best-to-worst |
| 3 | Prepare factor data + prices | Two datasets: **factor values** (data frame, one factor column, MultiIndex of date + asset) and **aligned prices** (assets in columns, date index aligned to factor dates) |
| 4 | Run the factor analysis | Alphalens produces forward returns for 1, 5, and 10 days plus the factor quantile ranking (5 = best, 1 = worst) |
| 5 | Analyze the factors | Tear sheets are the headline functionality — quantile return spreads, IC, turnover |

The article closes with the caveat that factor analysis is one stage in a longer pipeline: you still need to generate strategies, backtest them, and execute trades.

---

## 2. The Standard Alphalens API (Public Version of the Member Code)

The member code is paywalled, but the canonical workflow is documented in the official repo (https://github.com/quantopian/alphalens):

```python
import alphalens

# Two inputs: factor values (date x asset) and pricing (date x asset, wide)
factor_data = alphalens.utils.get_clean_factor_and_forward_returns(
    factor,           # pd.Series with MultiIndex (date, asset)
    pricing,          # pd.DataFrame: dates x assets, ENTRY prices
    quantiles=5,      # bucket count
    periods=(1, 5, 10)  # forward-return horizons
)

# Full tear sheet
alphalens.tears.create_full_tear_sheet(factor_data)
```

What `get_clean_factor_and_forward_returns()` does:

1. Computes **forward returns** at each horizon from the pricing data (entry price must be the next available price AFTER the factor observation — no look-ahead).
2. **Sorts assets into quantiles** by factor value each period.
3. Aligns everything into one clean DataFrame: forward returns per horizon, factor value, factor quantile.

The full tear sheet then produces, in one call:

- **Returns analysis by quantile** — mean return of each quantile basket over time; a good factor shows a monotonic spread (Q5 > Q4 > ... > Q1)
- **Information Coefficient analysis** — Spearman rank correlation between factor values and forward returns, per period, with mean IC, IC standard deviation, and t-stat. PyQuant News's rule of thumb: mean IC above 0.10 is already strong for equities; above 0.20 is rare
- **Turnover analysis** — how much the factor's rankings churn period to period (proxy for trading costs)
- **Grouped analysis** — returns/IC broken down by sector or other grouping
- **Factor decay** — how the IC and quantile spread change as the horizon lengthens

Installation: the original `pip install alphalens` is stale on modern Python — use `pip install alphalens-reloaded` (maintained fork by Stefan Jansen, https://github.com/stefan-jansen/alphalens-reloaded).

---

## 3. Mapping: Alphalens Concepts → P_300 Catalog

The structural fit is direct — P_300's catalog already contains everything Alphalens needs, in three of the seven schema tables:

| Alphalens concept | P_300 equivalent | Source table(s) |
|---|---|---|
| Factor value (per date, per asset) | Composite similarity score (inverse of equal-weight DTW distance) between the live candidate and each historical pattern instance | Pipeline B `similarity.composite_distance` output, computed from `pattern_bars` normalized columns |
| Pricing data (for forward returns) | **Already computed and stored** — `forward_labels.return_pct` at horizons 5, 7, 10, 15, 20 days | `forward_labels` |
| Forward-return horizons (1/5/10 days) | Catalog horizons are 5/7/10/15/20 days — richer than the tutorial's; use them all | `forward_labels.horizon_days` |
| Quantile (1–5 buckets) | Similarity-rank buckets over the matched instances — BUY/WATCH/PASS is effectively a coarse 3-bucket quantile already | `aggregator.aggregate_top_k` output |
| Quantile return spread | Mean `return_pct` by similarity quintile — does the top similarity bucket actually out-earn the bottom? | `pattern_features` + `forward_labels` join |
| Information Coefficient | Spearman correlation, per anchor date, between similarity rank and `return_pct` — replaces the binary win-rate test with a graded, statistically testable one | join above |
| Factor decay (IC vs horizon) | Which horizon (5 vs 10 vs 20 day) carries the most predictability — directly informs trade-management holding-period assumptions | `forward_labels.horizon_days` |
| Universe selection | Pattern instances per anchor date (cross-section = instances matched that day) | `pattern_instances` |
| Turnover | Not directly relevant (P_300 is not a rebalancing portfolio) — skip or treat as diagnostic only | — |
| Grouped analysis | Group IC/spread by `data_origin_type`, symbol, or feature version | `pattern_instances` |

Two important schema cautions (per the P_300 project rules):

- `return_pct` is a **decimal fraction** (0.0672 = 6.72%). Multiply by 100 only at the display boundary — never inside the math (EC-070).
- Similarity math must use the **10 normalized `pattern_bars` columns only** — never raw dollar values (EC-046/048/022).

---

## 4. How the Validation Would Run Against the Catalog

Conceptual flow (read-only, Pipeline B style — Decision E forbids inserting EVAL_SET rows, and nothing here writes to the catalog):

```
pattern_instances (anchor_date, symbol_id)
  → similarity ranking of instances (existing composite_distance)
  → factor series: one value per (anchor_date, instance) = similarity score
  → join forward_labels (5/7/10/15/20-day return_pct per instance)
  → quantile buckets by similarity rank (quintiles per anchor date)
  → outputs: quantile return spread, rolling IC per horizon, IC decay curve
```

Because P_300 already stores forward returns, you do **not** need Alphalens's pricing input at all — the expensive half of `get_clean_factor_and_forward_returns()` is already done in the catalog. Two implementation options:

1. **Native Alphalens:** build the factor Series with a `(anchor_date, instance_id)` MultiIndex and call Alphalens with pricing reconstructed from `pattern_bars` — works, but you must supply entry prices aligned so no look-ahead leaks, and Alphalens will recompute returns you already have.
2. **Alphalens-style, catalog-native (lighter):** compute quantile spreads and Spearman IC directly from the `forward_labels` join with pandas/scipy. You get the same three headline outputs (quantile spread, mean IC + t-stat, decay by horizon) without the pricing plumbing. This fits the existing Pipeline B layer flow and avoids re-deriving returns.

Option 2 is the more natural fit for the P_300 architecture; option 1 is worth it only if you want Alphalens's full tear-sheet visualizations.

---

## 5. What the Outputs Would Tell You (Interpretation Guide)

**Quantile return spread.** Bucket all matched historical instances by similarity quintile and compare mean forward return per horizon. A healthy signal is monotonic: Q5 (most similar) should out-earn Q1 (least similar) consistently. This directly tests whether the current top-K selection logic (which feeds BUY/WATCH/PASS) is ranking on real edge rather than noise.

**Information Coefficient.** Per anchor date, Spearman-correlate similarity rank against realized `return_pct`. Track mean IC, IC standard deviation, and the t-stat across dates:

- Mean IC > 0.10 with low variance = genuinely strong for equities
- IC jumping around = unstable or overfit signal
- Compare against the current thresholds: BUY requires n ≥ 5 matches, win rate ≥ 0.70, z > 0.0. Win rate is a coarser statistic than IC — the same matches could show a high win rate but near-zero mean return (small wins, and wins of uneven size). IC catches that; win rate alone does not.

**Decay by horizon.** Mean IC at 5 vs 7 vs 10 vs 15 vs 20 days. If the signal peaks at 5–7 days and decays by 20, that argues for faster profit-taking at T1 — an input directly relevant to trade-management holding-period decisions in the AJZ framework, and consistent with the 1× ATR post-target protection refinement already in flight.

**Robustness slices.** IC and spreads grouped by symbol, feature version (`feature_sets`), or time window — checks whether edge concentrates in a few names/periods (the PyQuant News piece emphasizes any edge should be steady, not outlier-driven).

---

## 6. P_300 Alignment Notes

- **No catalog writes.** This is pure read-side analysis — same contract as Pipeline B. No EVAL_SET inserts (Decision E), no Check-Out/Check-In needed unless something writes.
- **No LLM in the path.** All of this is deterministic pandas/scipy math — the LLM boundary rule is unaffected.
- **Paths and layers.** Any future script must use `db_utils.get_latest_catalog()` (never a hardcoded DB path), live in `infrastructure/` for the catalog read and `domain/` for the IC/quantile math, and follow the versioned-header and file-plan-approval rules. Per the project's operating rules, this note is a methodology summary only — no code is proposed until INIT has run and a plan is approved.
- **Numbers caveat.** The tutorial's 90-day momentum factor is just a demo factor; for P_300 the "factor" is similarity score. The methodology transfers; the specific factor does not.

---

## 7. Bottom Line

The newsletter's core message maps cleanly onto an open question in P_300: the catalog currently validates matches with **count, win rate, and Z-score**; Alphens-style validation would add **graded rank correlation (IC), quantile monotonicity, and horizon decay** computed from the `forward_labels` already in the catalog. That is a validation-layer upgrade, not a signal-logic change — it would sit beside `signal_classifier`, not inside it, and would produce evidence for (or against) the wr ≥ 0.70 BUY threshold using statistics that are more sensitive than win rate alone.
