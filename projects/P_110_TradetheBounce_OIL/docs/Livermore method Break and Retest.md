\# Break and Retest Trading Strategy: Python Architecture & Implementation Specification

Based on the core price action principles from Jesse Livermore's Break and Retest methodology, this document outlines the algorithmic state machine and Python logic required to automate the strategy.

\---

\#\# 1. System Architecture & State Machine

To translate price action into quantitative code, the strategy operates as a deterministic \*\*Finite State Machine (FSM)\*\* with four distinct operational states:

\`\`\`

[STATE 0: ZONE_SCAN] ---\> [STATE 1: BREAKOUT_PENDING] ---\> [STATE 2: RETEST_LOOKUP] ---\> [STATE 3: IN_TRADE]

\`\`\`

\#\#\# State 0: Zone Identification (\`ZONE_SCAN\`)

\* \*\*Objective:\*\* Detect key historical support and resistance levels across higher timeframes (e.g., Daily / 4-Hour).

\* \*\*Conditions:\*\*

\* \*\*Touch Count:\*\* Identify price levels where \$\\ge 3\$ swing highs or swing lows cluster within a defined tolerance.

\* \*\*Tolerance Band:\*\* Convert precise price points into a zone using an \$N \\times \\text{ATR}\$ or percentage threshold:

\$\$\\text{Zone Upper} = P_{\\text{level}} + (0.25 \\times \\text{ATR})\$\$

\$\$\\text{Zone Lower} = P_{\\text{level}} - (0.25 \\times \\text{ATR})\$\$

\#\#\# State 1: Breakout Confirmation (\`BREAKOUT_PENDING\`)

\* \*\*Objective:\*\* Filter false breakouts and verify institutional participation.

\* \*\*Conditions:\*\*

\* \*\*Candle Body Close:\*\* The candle's closing price must land strictly outside the zone boundary on the execution timeframe (e.g., \$\\text{Close} \> \\text{Zone Upper}\$ for Longs). Wicks through the level are ignored.

\* \*\*Volume Expansion:\*\* Breakout candle volume must exceed a rolling moving average:

\$\$\\text{Volume}_{\\text{breakout}} \> 1.5 \\times \\text{SMA}(\\text{Volume}, 20)\$\$

\#\#\# State 2: Retest & Rejection Signal (\`RETEST_LOOKUP\`)

\* \*\*Objective:\*\* Wait for price to pull back and confirm the former resistance as new support (or vice-versa).

\* \*\*Conditions:\*\*

\* \*\*Zone Touch:\*\* Price returns to touch or penetrate the established zone boundary within \$M\$ candles.

\* \*\*Rejection Candlestick:\*\* Look for a rejection wick or reversal pattern:

\$\$\\text{Lower Wick Ratio} = \\frac{\\min(\\text{Open}, \\text{Close}) - \\text{Low}}{\\text{High} - \\text{Low}} \\ge 0.60\$\$

\* \*\*Invalidation Trigger:\*\* If a candle closes fully back inside/past the zone, the setup is invalidated and reset to \`ZONE_SCAN\`.

\#\#\# State 3: Execution & Position Sizing (\`IN_TRADE\`)

\* \*\*Objective:\*\* Enter near the level, set strict risk parameters, and manage trade execution.

\* \*\*Risk Formula:\*\*

\$\$\\text{Position Size (Units)} = \\frac{\\text{Account Balance} \\times \\text{Risk \\%}}{\\text{Entry Price} - \\text{Stop Loss Price}}\$\$

\* \*\*Stop Loss:\*\* Placed just beyond the opposite edge of the zone boundary or below the retest candle's swing low.

\* \*\*Take Profit:\*\* Target set at the next major historical structure level (minimum \$1:3\$ Risk-to-Reward ratio).

\---

\#\# 2. Python Implementation Code

\`\`\`python

import numpy as np

import pandas as pd

class BreakAndRetestStrategy:

def \__init__(

self,

risk_per_trade: float = 0.01,

volume_mult: float = 1.5,

wick_ratio_threshold: float = 0.60,

):

self.risk_per_trade = risk_per_trade

self.volume_mult = volume_mult

self.wick_ratio_threshold = wick_ratio_threshold

def calculate_atr(self, df: pd.DataFrame, period: int = 14) -\> pd.Series:

"""Calculates Average True Range (ATR)."""

high_low = df["high"] - df["low"]

high_close = np.abs(df["high"] - df["close"].shift())

low_close = np.abs(df["low"] - df["close"].shift())

ranges = pd.concat([high_low, high_close, low_close], axis=1)

true_range = np.max(ranges, axis=1)

return true_range.rolling(period).mean()

def evaluate_signals(

self,

df: pd.DataFrame,

zone_high: float,

zone_low: float,

trend: str = "BULLISH",

) -\> dict \| None:

"""Evaluates DataFrame for Break and Retest setup conditions."""

df = df.copy()

df["atr"] = self.calculate_atr(df)

df["vol_sma"] = df["volume"].rolling(20).mean()

df["body_min"] = df[["open", "close"]].min(axis=1)

breakout_found = False

breakout_idx = None

for i in range(1, len(df)):

\# 1. Breakout Check

if not breakout_found:

if trend == "BULLISH":

clean_close = df["close"].iloc[i] \> zone_high

volume_surge = (

df["volume"].iloc[i]

\> self.volume_mult \* df["vol_sma"].iloc[i]

)

if clean_close and volume_surge:

breakout_found = True

breakout_idx = i

continue

\# 2. Retest & Rejection Check

if breakout_found and i \> breakout_idx:

c_high = df["high"].iloc[i]

c_low = df["low"].iloc[i]

c_close = df["close"].iloc[i]

\# Ensure price touches zone

touches_zone = c_low \<= zone_high and c_high \>= zone_low

\# Invalidation Check: Candle closes back inside/below zone

if c_close \< zone_low:

breakout_found = False \# Invalidate setup

continue

\# Calculate rejection wick ratio

candle_range = c_high - c_low

lower_wick = (

df["body_min"].iloc[i] - c_low if candle_range \> 0 else 0

)

wick_ratio = (

lower_wick / candle_range if candle_range \> 0 else 0

)

if touches_zone and wick_ratio \>= self.wick_ratio_threshold:

entry_price = c_close

stop_loss = zone_low - (0.5 \* df["atr"].iloc[i])

return {

"timestamp": df.index[i],

"signal": "BUY",

"entry_price": entry_price,

"stop_loss": stop_loss,

"risk_per_share": entry_price - stop_loss,

}

return None

\`\`\`

\---

\#\# 3. Quantitative Guardrails & Filters

1\. \*\*Trend Alignment:\*\* Require multi-timeframe confirmation (e.g., \$\\text{Price} \> 200\\text{-SMA}\$ on Daily).

2\. \*\*Expiry Window:\*\* If a retest does not occur within \$N\$ candles following a breakout, terminate the lookup to avoid late entries.

3\. \*\*Strict Invalidation:\*\* Cancel the setup immediately if a retest candle closes back below the broken structure.
