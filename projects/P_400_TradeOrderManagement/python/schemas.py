"""P_400 schema definitions and re-exports.

Canonical signal models from shared contract — never import from P_800 internals.
P_400-owned schemas: BookRecord, PostureSnapshot, AccountParams.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel
from shared_resources.python_utils.signal_schemas import (  # noqa: F401
    AssetClass,
    SignalV2,
)

__all__ = [
    "AssetClass",
    "SignalV2",
    "BookRecord",
    "PostureSnapshot",
    "AccountParams",
]


class BookRecord(BaseModel):
    """One position record parsed from *_P400.md YAML frontmatter.

    Non-CLOSED records contribute to portfolio heat and position counts.
    CLOSED records from today contribute to realized_day_loss.
    """

    symbol: str
    status: str  # PENDING | SUBMITTED | FILLED | T1_HIT | TRAILING | CLOSED
    sector: Optional[str] = None
    open_risk_dollars: float = 0.0
    realized_pnl: Optional[float] = None   # populated on CLOSED records
    close_date: Optional[str] = None       # YYYY-MM-DD; daily-loss filter


class PostureSnapshot(BaseModel):
    """Validated fields from P_010_RiskConfig.json."""

    risk_mode: str
    avg_posture: float
    timestamp: str
    source: str = "unknown"


class AccountParams(BaseModel):
    """Account sizing parameters from P_000_Account_Parameters_Current.md."""

    account_balance: float
    risk_per_trade: float
    max_position: float


class SnapshotDict(BaseModel):
    """Live-market data block assembled by Claude and handed to the Python pipeline.

    Required fields must be present — missing required keys raise ValidationError.
    Use null (None) for honestly unknown values. Never fabricate.

    Architecture v2.0 Section 6.2.
    """

    symbol: str
    price: float
    bid: float
    ask: float
    price_timestamp: str           # ISO-8601
    price_delay_seconds: int
    atr_14: float
    avg_volume_20d: float
    data_source: str               # "web" | "schwab_api" | "manual"
    today_volume: Optional[float] = None
    next_earnings_date: Optional[str] = None    # YYYY-MM-DD
    binary_events: List[str] = []
    sector: Optional[str] = None
    iv_rank: Optional[float] = None
    option_chain_ref: Optional[Dict] = None
    market_open: bool = True       # set False for pre-market; tape_vote uses this
    guideline_stop_override: Optional[float] = None   # P_400 re-derived stop (drift reconciliation)
