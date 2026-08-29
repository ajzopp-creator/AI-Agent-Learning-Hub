Here is the complete summary and universal pseudocode formatted in clean, copyable Markdown:

\`\`\`markdown

\# Jesse Livermore 3-Indicator Strategy: Universal Pseudocode & Architecture

This document summarizes the core market framework presented in the video \*\*"90% of Traders Use WRONG Indicators \| Here's the 3 That Work"\*\* by \*Jesse Livermore's Trading Code\* into a clean, universal algorithmic blueprint and execution pseudocode.

\---

\#\# 1. Core Philosophy & The 3 Universal Tools

The strategy rejects indicator overload (oscillators, clouds, bands) and reduces analysis to two fundamental data inputs that govern all financial markets: \*\*Price\*\* and \*\*Volume\*\*.

1\. \*\*Direction — The Moving Average (Line of Least Resistance)\*\*

\- \*\*Role:\*\* Directional filter and guard rail (answers \*"Which way is the river flowing?"\*).

\- \*\*Rule:\*\* Never use the moving average as a direct buy/sell trigger. Longs are only permitted above a rising MA; shorts/cash only below a falling MA.

2\. \*\*Location — Price Action & Pivotal Points\*\*

\- \*\*Role:\*\* Structural identification (answers \*"Where is the line in the sand?"\*).

\- \*\*Rule:\*\* Identify clear multi-touch ceilings (resistance) and floors (support). Wait for price to cross and hold beyond the level (structural conversion: ceiling becomes floor, floor becomes ceiling).

3\. \*\*Confirmation — Volume (The Truth Serum)\*\*

\- \*\*Role:\*\* Institutional validation (answers \*"Is there real conviction behind the move?"\*).

\- \*\*Rule:\*\* Breakouts on thin/flat volume are liquidity traps. Only commit capital when volume expands significantly above its baseline average.

\---

\#\# 2. Universal Strategy Blueprint (Pseudocode)

\`\`\`python

"""

UNIVERSAL TRADING FRAMEWORK: 3-STEP DIRECTION / LOCATION / CONFIRMATION

Architecture:

\- Step 1: Direction Filter (Moving Average / Trend Compass)

\- Step 2: Structural Location (Pivotal Breakout / Support & Resistance)

\- Step 3: Conviction Confirmation (Relative Volume Surge)

Applicable to: Equities, Forex, Futures, Crypto, Commodities across any timeframe.

"""

\# ==============================================================================

\# 1. PARAMETERS & CONFIGURATION

\# ==============================================================================

INPUT MA_PERIOD = 50 \# Moving Average period for trend filter

INPUT VOL_AVG_PERIOD = 20 \# Lookback period for volume moving average

INPUT VOL_SURGE_MULTIPLIER = 1.5 \# Minimum multiplier for volume expansion (e.g., 1.5x)

INPUT PIVOTAL_LOOKBACK = 50 \# Lookback bars to identify key swing highs/lows

INPUT BUFFER_TICKS = 2 \# Invalidation buffer below/above pivotal line

INPUT POSITION_SIZE_PCT = 0.02 \# Risk percentage per trade (2% max equity risk)

\# ==============================================================================

\# 2. MAIN EXECUTION ENGINE (Evaluated at the Close of Every Bar)

\# ==============================================================================

FOR EACH BAR IN MARKET_DATA:

\# -------------------------------------------------------------------------

\# STEP 1: DIRECTION FILTER (Trend Compass)

\# -------------------------------------------------------------------------

MA_Current = Calculate_SMA(CLOSE, MA_PERIOD)

MA_Slope = MA_Current - MA_Current[1]

is_bullish_regime = (CLOSE \> MA_Current) AND (MA_Slope \> 0)

is_bearish_regime = (CLOSE \< MA_Current) AND (MA_Slope \< 0)

is_neutral_regime = NOT (is_bullish_regime OR is_bearish_regime)

\# -------------------------------------------------------------------------

\# STEP 2: LOCATION (Pivotal Points & Structural Levels)

\# -------------------------------------------------------------------------

\# Identify multi-touch horizontal ceilings (Resistance) and floors (Support)

Pivotal_Ceiling = Find_Key_Resistance_Level(Lookback=PIVOTAL_LOOKBACK)

Pivotal_Floor = Find_Key_Support_Level(Lookback=PIVOTAL_LOOKBACK)

\# -------------------------------------------------------------------------

\# STEP 3: CONVICTION (Volume Verification)

\# -------------------------------------------------------------------------

Avg_Volume = Calculate_SMA(VOLUME, VOL_AVG_PERIOD)

has_volume_surge = (VOLUME \>= Avg_Volume \* VOL_SURGE_MULTIPLIER)

has_volume_fade = (VOLUME \< Avg_Volume \* 0.8)

\# =========================================================================

\# 3. ENTRY TRIGGER LOGIC

\# =========================================================================

IF NOT IN_POSITION:

\# --- LONG ENTRY SETUP ---

\# 1. Direction: Upward trend regime

\# 2. Location: Price cleanly closes above pivotal ceiling (holding the level)

\# 3. Confirmation: Volume surges with strong institutional participation

IF is_bullish_regime:

IF (CLOSE \> Pivotal_Ceiling) AND (CLOSE[1] \<= Pivotal_Ceiling):

IF has_volume_surge:

ENTRY_PRICE = CLOSE

STOP_LOSS = Pivotal_Ceiling - BUFFER_TICKS \# Tucked just beneath the converted floor

POSITION_SZ = Calculate_Risk_Sizing(Capital=EQUITY, RiskPct=POSITION_SIZE_PCT, Entry=ENTRY_PRICE, Stop=STOP_LOSS)

EXECUTE_ORDER(Side="BUY", Quantity=POSITION_SZ, OrderType="MARKET", StopLoss=STOP_LOSS)

ELSE:

\# Low-volume breakout = High risk of bull trap -\> DO NOTHING

LOG("Bullish breakout rejected: Lack of volume conviction.")

\# --- SHORT ENTRY SETUP ---

\# 1. Direction: Downward trend regime

\# 2. Location: Price cleanly closes below pivotal floor

\# 3. Confirmation: Selling volume expands significantly

IF is_bearish_regime:

IF (CLOSE \< Pivotal_Floor) AND (CLOSE[1] \>= Pivotal_Floor):

IF has_volume_surge:

ENTRY_PRICE = CLOSE

STOP_LOSS = Pivotal_Floor + BUFFER_TICKS \# Tucked just above the converted ceiling

POSITION_SZ = Calculate_Risk_Sizing(Capital=EQUITY, RiskPct=POSITION_SIZE_PCT, Entry=ENTRY_PRICE, Stop=STOP_LOSS)

EXECUTE_ORDER(Side="SELL_SHORT", Quantity=POSITION_SZ, OrderType="MARKET", StopLoss=STOP_LOSS)

ELSE:

\# Low-volume breakdown = High risk of bear trap -\> DO NOTHING

LOG("Bearish breakdown rejected: Lack of volume conviction.")

\# =========================================================================

\# 4. TRADE MANAGEMENT & EXIT RULES

\# =========================================================================

IF IN_POSITION:

\# --- A. Structural Invalidation Exit ---

\# If price falls back through the broken pivotal level, market changed its mind

IF POSITION_TYPE == "LONG" AND CLOSE \< STOP_LOSS:

CLOSE_POSITION(Reason="Structural Level Violated (Ceiling Failed as Floor)")

IF POSITION_TYPE == "SHORT" AND CLOSE \> STOP_LOSS:

CLOSE_POSITION(Reason="Structural Level Violated (Floor Failed as Ceiling)")

\# --- B. Volume Climax / Exhaustion Management ---

\# Massive volume spike (\> 3.0x avg) after an extended run often signals exhaustion

IF (VOLUME \>= Avg_Volume \* 3.0) AND Is_Extended_Trend(BarsInTrend=10):

TRAIL_STOP_TO_PREVIOUS_BAR_EXTREME()

LOG("Volume Climax detected: Trailing stops tightened.")

\# --- C. Macro Trend Inversion Exit ---

\# Exit if underlying line of least resistance is lost

IF POSITION_TYPE == "LONG" AND CLOSE \< MA_Current:

CLOSE_POSITION(Reason="Line of Least Resistance Lost (Close \< MA)")

IF POSITION_TYPE == "SHORT" AND CLOSE \> MA_Current:

CLOSE_POSITION(Reason="Line of Least Resistance Lost (Close \> MA)")

**3. Key Strategy Heuristics & Rules of Thumb**

| **Component**         | **Rule**                                                          | **Failure Mode Prevented**                         |
|-----------------------|-------------------------------------------------------------------|----------------------------------------------------|
| **Moving Average**    | Must only align directional bias; never trigger entry on cross.   | Prevents whipsaws in choppy / ranging markets.     |
| **Pivotal Points**    | Wait for close beyond the level to confirm the break.             | Prevents jumping the gun on intra-bar fakeouts.    |
| **Volume Surge**      | Require $$\geq 1 . 5 \times$$volume baseline on pivotal breakout. | Prevents buying into hollow, low-liquidity drifts. |
| **Volume Climax**     | Extreme volume spikes after long runs signal buyer exhaustion.    | Prevents round-tripping profits at cycle tops.     |
| **Risk Invalidation** | Stop-loss placed tightly behind the converted pivotal line.       | Enforces asymmetrical risk/reward on every setup.  |
