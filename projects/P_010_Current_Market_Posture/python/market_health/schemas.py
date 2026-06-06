"""
P_010 Market Health -- schemas.py

Pydantic models defining the shape of inputs (parsed VP rows),
intermediate state (per-index health), and the final JSON output.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Section 6
"""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Type aliases for state machine values
# ---------------------------------------------------------------------------

RallyState = Literal[
    "NO_RALLY",
    "RALLY_LOW_SET",
    "RALLY_ATTEMPT",
    "FTD_CONFIRMED",
    "STALE_RALLY",
]

MarketPhase = Literal[
    "CONFIRMED_UPTREND",
    "UPTREND_UNDER_PRESSURE",
    "RALLY_ATTEMPT",
    "DETERIORATING",
    "CORRECTION",
    "NEUTRAL",
]

Ticker = Literal["SPY", "QQQ"]


# ---------------------------------------------------------------------------
# Input row -- one parsed day from VP Excel
# ---------------------------------------------------------------------------

class VPDailyRow(BaseModel):
    """One trading day's OHLCV from a VP grid Excel file."""

    trade_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float

    # Computed at load time vs prior row
    pct_change: Optional[float] = None   # close[t] vs close[t-1], percent
    volume_up: Optional[bool] = None     # volume[t] > volume[t-1]


# ---------------------------------------------------------------------------
# Per-index summary
# ---------------------------------------------------------------------------

class IndexHealth(BaseModel):
    """Distribution + rally state for a single index (SPY or QQQ)."""

    ticker: Ticker
    last_date: date
    last_close: float

    # Distribution
    dist_count: int = Field(ge=0, description="Distribution days within window")
    dist_dates: list[date] = Field(default_factory=list)

    # Rally state machine
    rally_state: RallyState
    rally_low: Optional[float] = None
    rally_low_date: Optional[date] = None
    rally_attempt_day: Optional[int] = Field(default=None, ge=0)

    # Follow-through
    follow_through_day: Optional[date] = None
    ftd_age_days: Optional[int] = Field(default=None, ge=0)


# ---------------------------------------------------------------------------
# Top-level output JSON
# ---------------------------------------------------------------------------

class MarketHealthOutput(BaseModel):
    """Final P_010_MarketHealth.json contract."""

    schema_version: str = "1.1"
    generated_at: datetime
    as_of_date: date

    spy: IndexHealth
    qqq: IndexHealth

    max_dist_count: int = Field(ge=0)
    market_phase: MarketPhase
    phase_reason: str

    source: str = "VP_Grid_XLSX"

# ---------------------------------------------------------------------------
# Workstream D -- Trade bucket analysis schemas
# ---------------------------------------------------------------------------

class TradeRecord(BaseModel):
    """Single closed trade from P_020 database."""

    trade_id: int
    system: str
    underlying_symbol: str
    open_date: date
    exit_date: Optional[date]
    exit_pnl: Optional[float]
    risk_amount: Optional[float]
    market_phase: Optional[str] = None  # filled after snapshot lookup


class BucketResult(BaseModel):
    """Win-rate stats for one market_phase bucket."""

    phase: str
    trade_count: int
    win_count: int
    win_rate: float          # 0.0 - 1.0
    avg_pnl: float
    avg_r: Optional[float]   # None if risk_amount missing for any trade
    low_sample: bool         # True if trade_count < BUCKET_MIN_TRADES
