"""config.py — P_115 backfill configuration.

Column names verified against P_115_118_TrackerDashboard_V2.xlsx Row 1
on 2026-05-23. CamelCase, no spaces.

If the last columns (Outcome onward) differ from the names below,
update their left-side keys to match your actual headers.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── PATHS ─────────────────────────────────────────────────────────────────────
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

# Add HUB_ROOT to sys.path so shared_resources.python_utils is importable
if str(HUB_ROOT) not in sys.path:
    sys.path.insert(0, str(HUB_ROOT))

# Real tracker lives in OneDrive — never hardcode the drive letter
TRACKER_PATH = (
    Path(os.environ["OneDrive"])
    / "Documents"
    / "AJZStrategiesLLC"
    / "P_115_TrackerAudit"
    / "P_115_118_TrackerDashboard_V2.xlsx"
)

# Sheet name — verified 2026-05-23
TRACKER_SHEET: str = "Tracker Log"

# Row number (1-indexed) containing column headers.
HEADER_ROW: int = 1

# ── COLUMN NAME MAP ───────────────────────────────────────────────────────────
# Left  = EXACT Excel column header (verified from tracker Row 1)
# Right = P_115 schema field name (do not change right side)
#
# ⚠ Columns 24+ (Outcome onward) — verify left side before running ⚠
EXCEL_TO_SCHEMA_MAP: dict[str, str] = {
    "Date":                    "date",
    "Symbol":                  "symbol",
    "SignalSource":            "signal_source",
    "Step1Verdict":            "step1_verdict",
    "PatternType":             "pattern_type",
    "BreakoutVerdict":         "breakout_verdict",
    "BreakoutVolumeMultiple":  "breakout_volume_multiple",
    "DistributionDayCount":    "distribution_day_count",
    "FollowThroughDay":        "follow_through_day",
    "MarketDirection":         "market_direction",
    "RSvsSPY":                 "rs_vs_spy",
    "FundamentalsTier":        "fundamentals_tier",
    "AnalysisTier":            "analysis_tier",
    "CandleTier":              "candle_tier",
    "SetupScore":              "setup_score",
    "LiquidityTier":           "liquidity_tier",
    "Traded":                  "traded",
    "EntryPrice":              "entry_price",
    "TPLevel":                 "tp_level",
    "SLLevel":                 "sl_level",
    "StopLevel":               "stop_level",
    "RiskPct":                 "risk_pct",
    "AccountBalance":          "account_balance",
    # ⚠ Verify these against your actual headers ⚠
    "Outcome":                 "outcome",
    "RecheckStatus":           "recheck_status",
    "SimulationNotes":         "simulation_notes",
    "Comments":                "comments",
    # Optional — remove if not present in your tracker
    "WHYCode":                 "why_code",
    "SIGCode":                 "sig_code",
}

# ── RUNTIME BEHAVIOR ──────────────────────────────────────────────────────────
REQUIRED_FIELDS: list[str] = ["date", "symbol"]
LOG_INTERVAL: int = 100
