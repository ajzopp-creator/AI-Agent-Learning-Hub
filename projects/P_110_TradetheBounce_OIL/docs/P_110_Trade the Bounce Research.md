# Trade the Bounce — ThinkOrSwim (ThinkScript) Specification

A concise developer-focused specification and implementation blueprint to approximate the "Trade the Bounce" quantitative strategy in ThinkOrSwim. This file emphasizes which components are feasible in ThinkScript, provides inputs, pseudocode, and concrete ThinkScript snippets to implement touch-counting, a micro-decay logistic probability, dynamic exit signal, ATR-based MAE buffer, and volume/SuperTrend confirmation. Advanced PCA and ANN computations are recommended to run externally (see Compatibility & Limitations).

## Table of Contents

1.  Title & Short Description
2.  Compatibility & Limitations
3.  Inputs & Tunable Parameters
4.  Implementation Blueprints
5.  ANN & PCA Integration Patterns
6.  Example Minimal ThinkScript Study
7.  Usage & Integration Notes
8.  Versioning & License

## Title & Short Description

Title: Trade the Bounce — ThinkScript Specification

Short description: Implements level-touch detection, prior-touch bucketed micro-decay logistic probability, a dynamic exit trigger when P(b)\<0.50, ATR-based MAE buffer plotting, and volume + SuperTrend confirmation. PCA/ML components are intended to be precomputed externally and injected as inputs or custom quotes.

## Compatibility & Limitations

Directly implementable in ThinkScript:

-   Level detection (pivot/high-low), touch counting within lookback windows.
-   Bar-based or time-approximate dt measurements (bar counts, SecondsFromTime heuristics).
-   Logistic function approximation: P(b)=1/(1+Exp(-(a+b\*dt))).
-   ATR, SMA, rolling statistics (limited to available built-in functions).
-   Plotting buffers and alerts for signals.

Not feasible or ill-advised directly in ThinkScript:

-   PCA eigen decomposition, eigenvector extraction, or full ANN (MLP) training/inference at scale.
-   Persistent stateful large-window sample storage beyond fold/recs; complex matrix ops.

Recommended workarounds:

-   Precompute principal components and ANN outputs on an external server. Export results via CSV, TD Ameritrade custom quotes, or manual input fields. Feed precomputed scores into ThinkScript as inputs or via study-level custom quote fields.
-   When external integration is impractical, create weighted composite indicators in ThinkScript (standardize indicators to Z-scores, compute linear combinations to approximate PCs).

## Inputs & Tunable Parameters

-   input touchLookbackBars = 200;\#int Lookback to detect level touches
-   input touchBucket1 = 1;\#int Prior touch bucket boundaries
-   input touchBucket2 = 4;\#int b_prev\>=4 high-touch bucket
-   input a_low = 0.005;\#double Baseline intercept for low-touch
-   input a_high = 0.403;\#double Baseline intercept for high-touch
-   input b_low = -0.01;\#double Decay coefficient for low-touch (per-bar)
-   input b_high = -0.03;\#double Decay coefficient for high-touch (per-bar)
-   input decayThreshold = 0.50;\#double P(b) threshold to liquidate
-   input typicalDecayMinutesLow = 15;\#int Guidance only
-   input typicalDecayMinutesHigh = 30;\#int Guidance only
-   input ATR_length = 14;\#int ATR length for MAE buffer
-   input MAE_windowBars = 100;\#int Rolling window for MAE std-dev
-   input bufferMultiplier = 1.0;\#double Multiplier for sigma_MAE\*ATR
-   input volumeSMA_length = 20;\#int SMA of volume
-   input ANN_score = 0.0;\#double Placeholder input for precomputed ANN Buy prob (0..1)
-   input ANN_threshold = 0.75;\#double ANN threshold for execution
-   input superTrendFactor = 3.0;\#double Placeholder for SuperTrend parameter (use community impl.)
-   input showPlots = yes;\#bool Toggle plotting

## Implementation Blueprints

### 1) Touch detection & prior-touch counting

Approach: detect horizontal level candidate (pivot high/low), count how many times price touched within tolerance band in recent lookback, record bars since last touch to approximate dt.

Pseudocode:

1\. Identify level L = recent pivot high or low (user selects pivot lookback or code finds highest high / lowest low over N bars).2. Define tolerance gamma = percent or absolute ticks.3. For each bar in lookback, increment touchCount if close to L within gamma.4. Record lastTouchBar = most recent bar index where touch occurred.5. dt = currentBarNumber - lastTouchBar (or convert to minutes if intraday).

ThinkScript snippet:

\# Level detection (simple highest high / lowest low) input levelLookback = 50;input gammaTicks = 0.0005;\#for FX pairs adjust accordingly def highestHigh = Highest(high, levelLookback);def lowestLow = Lowest(low, levelLookback);\#Choose side - here show both def levelShort = highestHigh;def levelLong = lowestLow;\#Tolerance band def isTouchShort = AbsValue(close - levelShort) \<= gammaTicks;def isTouchLong = AbsValue(close - levelLong) \<= gammaTicks;\#Count touches in lookback def touchCountShort = Sum(If(isTouchShort, 1, 0), touchLookbackBars);def touchCountLong = Sum(If(isTouchLong, 1, 0), touchLookbackBars);\#Record last touch bar number def lastTouchBarShort = if isTouchShort then BarNumber() else Double.NaN;lastTouchBarShort = HighestAll(lastTouchBarShort);\#Because HighestAll persists value def lastTouchBarLong = if isTouchLong then BarNumber() else Double.NaN;lastTouchBarLong = HighestAll(lastTouchBarLong);\#dt in bars def dtBarsShort = if !IsNaN(lastTouchBarShort) then BarNumber() - lastTouchBarShort else Double.NaN;def dtBarsLong = if !IsNaN(lastTouchBarLong) then BarNumber() - lastTouchBarLong else Double.NaN;

Notes: HighestAll persists the last seen value — use with care. For intraday minute charts, dtBars \~ minutes if chart is 1-minute.

### 2) Micro-Decay Logistic Probability

Model: P(b)=1/(1+Exp(-(a + b\*dt))). Parameterize a and b by prior-touch buckets.

ThinkScript function & snippet:

\# Map bucketed a/b by touch count def b_prev = touchCountShort;\#or touchCountLong (choose side) def a_val = if b_prev \>= touchBucket2 then a_high else a_low;def b_val = if b_prev \>= touchBucket2 then b_high else b_low;\#dt use dtBarsShort (bars) def dt = dtBarsShort;\#Compute logistic safety guard def lin = a_val + b_val \* dt;def Pb = 1 / (1 + Exp(-lin));plot P_bounce = if IsNaN(Pb) then Double.NaN else Pb;P_bounce.SetDefaultColor(Color.CYAN);P_bounce.SetLineWeight(2);

Comments: ThinkScript's Exp handles exponentials. dt here is in bars — adjust b coefficients to per-bar scale. For intraday minute charts, one bar ≈ 1 minute; for other resolutions, convert appropriately (e.g., use SecondsFromTime or Minute() heuristics).

### 3) Dynamic Exit Rule

Trigger when P(b)\<decayThreshold. Provide plot/alert examples and how to connect to strategy.exit in strategy scripts.

def triggerExit = P_bounce \< decayThreshold and !IsNaN(P_bounce);plot ExitSignal = if triggerExit then low - TickSize() else Double.NaN;ExitSignal.SetPaintingStrategy(PaintingStrategy.ARROW_DOWN);ExitSignal.SetDefaultColor(Color.RED);\# Alert example Alert(triggerExit, "P(b) below threshold - consider exit", Alert.BAR, Sound.Ring);\# If used inside a strategy: AddOrder(OrderType.SELL_TO_CLOSE, triggerExit, tradeSize);

Notes: ThinkScript study cannot forcibly close external broker positions. Use strategy framework for backtests; for live alerts use study alerts to notify manual exit or use a bridging API.

### 4) MAE Buffer using ATR and rolling std-dev

Compute ATR(ATR_length), estimate sigma_MAE via rolling stdev of observed adverse moves against hypothetical entry price. Because ThinkScript cannot easily store arrays of past hypothetical entries, approximate MAE std-dev by measuring past N-bar maxima of adverse moves when price touched levels.

\# ATR def ATR = Average(TrueRange(high, close, low), ATR_length);\# Approximate adverse excursion: when a touch occurs, compute subsequent max adverse move within MAE_windowBars\# We approximate by scanning past MAE_windowBars for bars that touched and measuring their worst adverse move def adverseMove = if isTouchShort then Max(high - close, close - low) else 0;\#Better approach: track runs when touch occurred and compute max adverse in next M bars - limited in studies\# Rolling stdev approximation using StDev on high-low relative to level def relMove = (close - levelShort) / ATR;def sigmaMAE = StDev(relMove, MAE_windowBars);\#Stop-Loss buffer in price units def stopBuffer = bufferMultiplier \* sigmaMAE \* ATR;plot StopLossLevel = if showPlots and !IsNaN(levelShort) then levelShort - stopBuffer else Double.NaN;StopLossLevel.SetDefaultColor(Color.MAGENTA);StopLossLevel.SetStyle(Curve.SHORT_DASH);

Caveats: This is an approximation. True MAE requires tracking individual entry points and their subsequent adverse excursions; best done in external backtester or strategy context with AddOrder tracking.

### 5) Volume & SuperTrend confirmation

Compute volume SMA and a SuperTrend-like flip. If community SuperTrend code is available, prefer that; otherwise approximate with ATR channel.

\# Volume SMA def volSMA = Average(volume, volumeSMA_length);def volConfirm = volume \> volSMA;\# Simple SuperTrend-like flip (approximation) def upper = (high + low)/2 + superTrendFactor \* ATR;def lower = (high + low)/2 - superTrendFactor \* ATR;def trendUp = close \> lower;def trendDown = close \< upper;def superTrendFlip = trendUp and !trendDown;\# Combined execution condition def execCondition = volConfirm and superTrendFlip and (ANN_score \>= ANN_threshold);plot ExecSignal = if execCondition then low - 2\*TickSize() else Double.NaN;ExecSignal.SetDefaultColor(Color.GREEN);ExecSignal.SetPaintingStrategy(PaintingStrategy.ARROW_UP);

ANN_score is an input placeholder to receive an externally computed neural network probability.

## ANN & PCA Sections

Constraints: ThinkScript cannot perform PCA eigen decomposition or train/execute full ANN models. Suggested integration patterns:

A) External precompute pattern

1.  Run PCA+ANN on server. Export per-timestamp scores (PCs, ANN_prob) to CSV or a custom quote/data feed.
2.  Import into ThinkOrSwim via the Data Importer or map to a custom symbol (if TD supports). Alternatively, manually paste key metrics into study inputs or use a rolling webhook to set study inputs.
3.  In ThinkScript, accept ANN_score and PC1/PC2 as inputs and use them directly in execCondition.

B) On-chart approximation pattern

1.  Standardize raw indicators to Z-scores: Z = (X - Average(X, N))/StDev(X, N).
2.  Compute weighted linear combination to approximate PC1/PC2: PC1_approx = w1\*Z(SMA) + w2\*Z(Volume) + w3\*Z(ATR) ...
3.  Use PC1_approx and PC2_approx as lightweight proxies for external PCs.

ThinkScript Z-score snippet:

\# Example Z-score standardization def lenZ = 50;def smaShort = Average(close, 10);def z_smaShort = (smaShort - Average(smaShort, lenZ)) / StDev(smaShort, lenZ);\# Weighted PC approx def PC1_approx = 0.6 \* z_smaShort + 0.3 \* ((volume - Average(volume, lenZ))/StDev(volume, lenZ)) + 0.1 \* ((ATR - Average(ATR, lenZ))/StDev(ATR, lenZ));

## Example: Minimal Complete ThinkScript Study

Compact study that wires touch-count logistic, exit trigger, MAE buffer, and volume confirmation. This is focused — not full ANN/PCA.

\# TradeTheBounce_Minimal Study input touchLookbackBars = 200;input levelLookback = 50;input gammaTicks = 0.0005;input touchBucket2 = 4;input a_low = 0.005;input a_high = 0.403;input b_low = -0.01;input b_high = -0.03;input decayThreshold = 0.50;input ATR_length = 14;input MAE_windowBars = 100;input bufferMultiplier = 1.0;input volumeSMA_length = 20;input ANN_score = 0.0;input ANN_threshold = 0.75;\# Level def levelShort = Highest(high, levelLookback);def isTouchShort = AbsValue(close - levelShort) \<= gammaTicks;def touchCountShort = Sum(If(isTouchShort, 1, 0), touchLookbackBars);\# Last touch bar def lastTouchBarShort = if isTouchShort then BarNumber() else Double.NaN;lastTouchBarShort = HighestAll(lastTouchBarShort);def dtBarsShort = if !IsNaN(lastTouchBarShort) then BarNumber() - lastTouchBarShort else Double.NaN;\# Logistic P(b) def a_val = if touchCountShort \>= touchBucket2 then a_high else a_low;def b_val = if touchCountShort \>= touchBucket2 then b_high else b_low;def lin = a_val + b_val \* dtBarsShort;def Pb = if IsNaN(lin) then Double.NaN else 1 / (1 + Exp(-lin));plot P_bounce = Pb;P_bounce.SetDefaultColor(Color.CYAN);P_bounce.SetLineWeight(2);\# Exit trigger def triggerExit = Pb \< decayThreshold and !IsNaN(Pb);plot ExitSignal = if triggerExit then low - TickSize() else Double.NaN;ExitSignal.SetPaintingStrategy(PaintingStrategy.ARROW_DOWN);ExitSignal.SetDefaultColor(Color.RED);Alert(triggerExit, "TradeTheBounce: P(b) below threshold", Alert.BAR, Sound.Ring);\# ATR & Stop buffer def ATR = Average(TrueRange(high, close, low), ATR_length);def relMove = (close - levelShort) / ATR;def sigmaMAE = StDev(relMove, MAE_windowBars);def stopBuffer = bufferMultiplier \* sigmaMAE \* ATR;plot StopLossLevel = if !IsNaN(levelShort) then levelShort - stopBuffer else Double.NaN;StopLossLevel.SetDefaultColor(Color.MAGENTA);StopLossLevel.SetStyle(Curve.SHORT_DASH);\# Volume confirmation def volSMA = Average(volume, volumeSMA_length);def volConfirm = volume \> volSMA;\# Execution combined (uses ANN_score placeholder) def execCondition = volConfirm and (ANN_score \>= ANN_threshold);plot ExecSignal = if execCondition then low - 2\*TickSize() else Double.NaN;ExecSignal.SetPaintingStrategy(PaintingStrategy.ARROW_UP);ExecSignal.SetDefaultColor(Color.GREEN);

## Usage & Integration

-   Attach the study to intraday charts (1-min to 15-min preferred) to align dtBars with minutes. For higher timeframe charts, adjust b coefficients accordingly.
-   Use Study Alerts for live notifications; use strategy scripts with AddOrder/AddOrderCondition for backtesting and simulated exits.
-   For reliable ANN/PCA integration, precompute signals externally per timestamp and feed into ThinkScript as inputs or custom quotes. Consider using the strategy engine on a platform that supports external model wiring for live automated execution.
-   Be mindful: HighestAll, Highest, and persistent constructs behave differently in real-time vs historical replay. Validate on historical bars and paper trading before live use.

## Versioning & License

Version: 1.0 — 2026-07-20

License: MIT (recommended). Note: Any model training (PCA/MLP) must be performed off-platform and is not covered by this ThinkScript study.

## Final Notes

Preserved key parameters: decay threshold 0.50, prior-touch bucket a_low=0.005 for single touches and a_high=0.403 for b_prev\>=4; typical decay guideline 15–30 minutes (map to bar counts); PCA EVR\>=0.90 for selection (external); ANN threshold 0.75 for execution. Implement core logic in ThinkScript; offload PCA and ANN to external compute and ingest results as inputs or custom data feeds.
