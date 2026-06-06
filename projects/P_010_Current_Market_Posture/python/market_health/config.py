"""
P_010 Market Health -- config.py

Central configuration for the Distribution Day Tracker.
All paths, thresholds, and tunable constants live here.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture"
)
DATA_DIR = PROJECT_ROOT / "data" / "excel_exports"
OUTPUT_JSON = PROJECT_ROOT / "P_010_MarketHealth.json"
LOG_DIR = PROJECT_ROOT / "logs" / "market_health"
SNAPSHOT_DIR = PROJECT_ROOT / "data" / "snapshots" / "market_health"

# VP Excel files (schema verified 2026-04-25; row 0 is a garbage label row)
VP_FILES = {
    "SPY": DATA_DIR / "History Grid (SPY)_v3.xlsx",
    "QQQ": DATA_DIR / "History Grid (QQQ)_v3.xlsx",
}

# Excel column names (note literal newlines in headers as parsed by pandas)
COL_DATE = "Date"
COL_OPEN = "Open\nPrice"
COL_HIGH = "High\nPrice"
COL_LOW = "Low\nPrice"
COL_CLOSE = "Close\nPrice"
COL_VOLUME = "Volume"

# ---------------------------------------------------------------------------
# Distribution day thresholds
# ---------------------------------------------------------------------------

# A distribution day requires ALL of:
#   close[t]  <  close[t-1]
#   volume[t] >  volume[t-1]
#   abs(pct_change_close) >= MIN_DISTRIBUTION_PCT
MIN_DISTRIBUTION_PCT = 0.20  # percent

# Rolling lookback window for live distribution count
DISTRIBUTION_WINDOW_DAYS = 25

# Rally reset trigger -- gain >= this from rally low wipes prior dist count
RALLY_RESET_PCT = 5.0  # percent

# Live dist count that invalidates an active FTD_CONFIRMED state
DIST_COUNT_INVALIDATES_FTD = 4

# ---------------------------------------------------------------------------
# Stalling day thresholds (Phase 2 -- pre-calibration defaults)
# ---------------------------------------------------------------------------

# A stalling day requires ALL of:
#   close[t]  >  close[t-1]                     (up day)
#   pct_change_close <= STALLING_MAX_GAIN_PCT   (small gain)
#   volume[t] >= volume[t-1] * STALLING_VOLUME_RATIO_MIN  (volume confirms)
#   (close - low) / (high - low) <= STALLING_CLOSE_IN_RANGE_MAX  (close weak)
#
# These defaults are IBD-derived starting points. Calibrate against
# real backtest data in Workstream C/D before enabling stalling days
# in count_distribution_days(). See spec Section 10 Q4.
STALLING_MAX_GAIN_PCT = 0.20            # percent -- gain must be smaller than this
STALLING_VOLUME_RATIO_MIN = 1.0         # volume[t] / volume[t-1] floor
STALLING_CLOSE_IN_RANGE_MAX = 0.50      # close position in day's range (0=low, 1=high)

# ---------------------------------------------------------------------------
# Follow-through day thresholds
# ---------------------------------------------------------------------------

# FTD must occur on day N of the rally attempt where MIN <= N <= MAX
FTD_DAY_MIN = 4
FTD_DAY_MAX = 7

# Minimum close-to-close gain on the FTD candidate day
FTD_MIN_GAIN_PCT = 1.5  # percent

# ---------------------------------------------------------------------------
# Market phase thresholds (consumed by market_phase.py)
# ---------------------------------------------------------------------------

# Banding on max_dist_count across SPY and QQQ
PHASE_DIST_HEALTHY_MAX = 2        # 0-2 dist days -> healthy
PHASE_DIST_CAUTION_MAX = 3        # 3 dist days -> caution
PHASE_DIST_DETERIORATING_MAX = 4  # 4 dist days -> deteriorating
# 5+ dist days -> correction

# FTD freshness window -- how recent FTD must be to still count as confirmation
FTD_FRESH_DAYS = 25

# ---------------------------------------------------------------------------
# History lookback
# ---------------------------------------------------------------------------

# Number of trailing trading days of VP rows to load. Must exceed the
# distribution window plus a rally-lookback buffer.
LOOKBACK_DAYS = 300

# ---------------------------------------------------------------------------
# Workstream D -- Trade bucket analysis
# ---------------------------------------------------------------------------

# Hub root derived from PROJECT_ROOT (two levels up)
HUB_ROOT = PROJECT_ROOT.parent.parent

# P_020 trade database (read-only)
P_020_DB_PATH = (HUB_ROOT / 'projects' /
                 'P_020_AJZStrategies_PerformanceAnalysisSystem' /
                 'data' / 'database' / 'P_020_trades.db')

# Systems included in bucket analysis
BUCKET_SYSTEMS = ('P_115', 'P_118')

# Minimum trades per bucket -- below this, flag as low-sample
BUCKET_MIN_TRADES = 10

# Win-rate delta threshold for Phase 3 go/no-go (percentage points)
BUCKET_DELTA_THRESHOLD = 10.0

# Output path for trade bucket report
BUCKET_REPORT_PATH = PROJECT_ROOT / 'outputs' / 'trade_bucket_report.md'
