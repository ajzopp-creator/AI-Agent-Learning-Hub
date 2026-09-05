"""
P_025 AJZ Institutional Portfolio Tracker — Configuration

All constants, paths, thresholds, and account definitions live here.
No hardcoded values are permitted outside this module.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Final, Literal

# ---------------------------------------------------------------------------
# Environment & Root Paths
# ---------------------------------------------------------------------------

# HUB_ROOT env wins. Do not fall back to OneDrive — that writes an empty
# build when OneDrive is set and HUB_ROOT is not.
_DEFAULT_HUB_ROOT: Final[str] = r"C:\Users\Trader\AI-Agent-Learning-Hub"
HUB_ROOT: Final[Path] = Path(os.environ.get("HUB_ROOT", _DEFAULT_HUB_ROOT))

PROJECT_ROOT: Final[Path] = HUB_ROOT / "projects" / "P_025_AJZ_Institutional_Portfolio_Tracker"
PYTHON_ROOT: Final[Path] = PROJECT_ROOT / "python"
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# P_020 Source of Truth
# ---------------------------------------------------------------------------

# Primary SQLite database produced by P_020.
# Confirmed live path (2026-08-21):
# C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db
P020_DB_PATH: Final[Path] = Path(
    os.environ.get(
        "P020_DB_PATH",
        str(
            HUB_ROOT
            / "projects"
            / "P_020_AJZStrategies_PerformanceAnalysisSystem"
            / "data"
            / "database"
            / "P_020_trades.db"
        ),
    )
)

# Optional CSV fallback (useful for testing or when SQLite is unavailable)
P020_CSV_FALLBACK: Final[Path | None] = None

# ---------------------------------------------------------------------------
# Account Definitions (Locked per System Documentation v1.1)
# ---------------------------------------------------------------------------

ACCOUNT_AJZ6348: Final[str] = "AJZ6348"
ACCOUNT_IRA9885: Final[str] = "5232-9885"          # Inherited Roth
ACCOUNT_PAPER: Final[str] = "PAPER"

# Accounts that appear in primary reporting
PRIMARY_ACCOUNTS: Final[tuple[str, ...]] = (
    ACCOUNT_AJZ6348,
    ACCOUNT_IRA9885,
)

# IRA feed is live — Inherited Roth (5232-9885) is included in all pulls.
# Flip back to False only if the P_020 feed regresses.
IRA_FEED_READY: Final[bool] = True

# ---------------------------------------------------------------------------
# Analysis Mode (lookback window for Daily_* / Market_Data / Equity_Curve)
# ---------------------------------------------------------------------------

AnalysisMode = Literal["full", "yearly", "ytd"]

# Default mode; override with env P025_ANALYSIS_MODE or CLI --mode
_DEFAULT_MODE: Final[str] = os.environ.get("P025_ANALYSIS_MODE", "full").lower()
ANALYSIS_MODE: Final[str] = _DEFAULT_MODE if _DEFAULT_MODE in ("full", "yearly", "ytd") else "full"

LOOKBACK_DAYS_FULL: Final[int] = 365 * 3   # 3 years trailing
LOOKBACK_DAYS_YEARLY: Final[int] = 365     # 1 year trailing (best-practice risk window)
LOOKBACK_DAYS_UPDATE: Final[int] = 14     # recent window for daily / weekly update


def resolve_start_date(end_date: date, mode: str | None = None) -> date:
    """
    Resolve analysis start date from mode.

    full   → trailing LOOKBACK_DAYS_FULL (3y)
    yearly → trailing LOOKBACK_DAYS_YEARLY (365d)
    ytd    → 1 January of end_date.year
    """
    from datetime import timedelta
    m = (mode or ANALYSIS_MODE).lower()
    if m == "ytd":
        return date(end_date.year, 1, 1)
    if m == "yearly":
        return end_date - timedelta(days=LOOKBACK_DAYS_YEARLY)
    # full (default)
    return end_date - timedelta(days=LOOKBACK_DAYS_FULL)


# ---------------------------------------------------------------------------
# Output Workbook
# ---------------------------------------------------------------------------

WORKBOOK_NAME: Final[str] = "P_025_Portfolio_BUILT.xlsx"
WORKBOOK_PATH: Final[Path] = OUTPUT_DIR / WORKBOOK_NAME

# Data Lake sheet names (exact match to System Documentation Section 9.1)
SHEET_TRADE_LOG: Final[str] = "Trade_Log"
SHEET_MARKET_DATA: Final[str] = "Market_Data"
SHEET_REFERENCE_DATA: Final[str] = "Reference_Data"
SHEET_DAILY_UNITS: Final[str] = "Daily_Units"
SHEET_DAILY_CASH: Final[str] = "Daily_Cash"
SHEET_DAILY_INVESTED: Final[str] = "Daily_Invested"
SHEET_COST_BASIS: Final[str] = "Cost_Basis"
SHEET_FIFO_LOTS: Final[str] = "Fifo_Lots"
SHEET_FIFO_COST: Final[str] = "Fifo_Cost"
CORREL_TICKER_CAP: Final[int] = 20

# Analytics sheet names
SHEET_DASHBOARD: Final[str] = "Dashboard"
SHEET_POSITIONS: Final[str] = "Positions"
SHEET_EQUITY_CURVE: Final[str] = "Equity_Curve"
SHEET_SECTOR_EXPOSURE: Final[str] = "Sector_Exposure"
SHEET_GEOGRAPHIC_EXPOSURE: Final[str] = "Geographic_Exposure"
SHEET_CORRELATION: Final[str] = "Correlation"
SHEET_RISK_METRICS: Final[str] = "Risk_Metrics"
SHEET_STRESS_TESTING: Final[str] = "Stress_Testing"
SHEET_INVESTMENT_THESES: Final[str] = "Investment_Theses"

DATA_LAKE_SHEETS: Final[tuple[str, ...]] = (
    SHEET_TRADE_LOG,
    SHEET_MARKET_DATA,
    SHEET_REFERENCE_DATA,
    SHEET_DAILY_UNITS,
    SHEET_DAILY_CASH,
    SHEET_DAILY_INVESTED,
    SHEET_COST_BASIS,
    SHEET_FIFO_LOTS,
    SHEET_FIFO_COST,
)

# ---------------------------------------------------------------------------
# yfinance / Market Data Settings
# ---------------------------------------------------------------------------

YFINANCE_TIMEOUT: Final[int] = 30          # seconds
YFINANCE_RETRIES: Final[int] = 3

# Risk-free rate used in Sharpe / Sortino (annualised)
RISK_FREE_RATE: Final[float] = 0.045       # 4.5 % — update as needed

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_LEVEL: Final[str] = os.environ.get("P025_LOG_LEVEL", "INFO")
LOG_FORMAT: Final[str] = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
