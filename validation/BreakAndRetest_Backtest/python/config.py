"""
FILE: config.py
VERSION: 1.0
DATE: 2026-08-26
AUTHOR: Tony + Claude
LAYER: config
DESCRIPTION:
    Constants, paths, and thresholds for the Break-and-Retest backtest
    validation script. Standalone script, outside P_300's production
    pipeline -- reads P_300's bulk VP export files read-only, writes
    nothing back to any catalog.

CHANGELOG:
    - 2026-08-26 v1.0: Initial build.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
DATA_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_300_Vantage_Point_Pattern_Recognition\data\bulk\mine"
)
FILE_GLOB_PATTERN = "10_Pattern_*.xlsx"

# ---------------------------------------------------------------------------
# ZONE DETECTION (State 0: ZONE_SCAN)
# ---------------------------------------------------------------------------
SWING_ORDER = 3            # bars each side to confirm a swing high
ZONE_TOUCH_MIN = 3         # minimum touches to confirm a resistance zone
ZONE_ATR_MULT = 0.25       # zone tolerance band = level +/- ZONE_ATR_MULT * ATR
ATR_PERIOD = 14

# ---------------------------------------------------------------------------
# BREAKOUT CONFIRMATION (State 1: BREAKOUT_PENDING)
# ---------------------------------------------------------------------------
VOLUME_SMA_PERIOD = 20
VOLUME_SURGE_MULT = 1.5    # breakout volume must exceed 1.5x its SMA

# ---------------------------------------------------------------------------
# RETEST & REJECTION (State 2: RETEST_LOOKUP)
# ---------------------------------------------------------------------------
RETEST_MAX_BARS = 10       # M candles to wait for retest before expiry
RETEST_WICK_RATIO = 0.60   # minimum lower-wick ratio on the rejection candle

# ---------------------------------------------------------------------------
# TRADE SIMULATION (State 3: IN_TRADE)
# ---------------------------------------------------------------------------
STOP_ATR_BUFFER = 0.5      # stop = zone_low - STOP_ATR_BUFFER * ATR
MIN_RR = 3.0                # take profit = entry + MIN_RR * risk_per_share
MAX_HOLD_BARS = 20          # force exit at close if neither stop nor target hit

LOG_LEVEL = "INFO"
