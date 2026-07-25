"""P_400 schema definitions and re-exports.

Canonical signal models from shared contract -- never import from P_800 internals.
P_400-owned schemas: BookRecord, PostureSnapshot, AccountParams, OptionChainInput.
"""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator
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
    "SnapshotDict",
    "OptionChainInput",
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

    Required fields must be present -- missing required keys raise ValidationError.
    Use null (None) for honestly unknown values. Never fabricate.

    Architecture v2.1 Section 6.2.
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
    last_earnings_date: Optional[str] = None  # YYYY-MM-DD, WO-P400-E2.023
    binary_events: List[str] = []
    sector: Optional[str] = None
    iv_rank: Optional[float] = None
    option_chain_ref: Optional[Dict] = None
    market_open: bool = True       # set False for pre-market; tape_vote uses this
    guideline_stop_override: Optional[float] = None   # P_400 re-derived stop (drift reconciliation)


class OptionChainInput(BaseModel):
    """Single-strike option chain data supplied by Tony via chain_SYMBOL.json.

    Required for all options evaluation paths (E3.001+).
    Source priority: TOS -> ChartExchange -> Yahoo Finance -> Barchart/Nasdaq.
    Never fabricate values -- use null for honestly unknown fields.

    Architecture v2.1 Section 7.3 (WO-P400-E3.003).
    """

    symbol: str
    underlying_price: float
    expiration: str                             # YYYY-MM-DD
    strike: float
    option_type: Literal["call", "put"]
    bid: float
    ask: float
    mid: float
    delta: float = Field(..., ge=-1.0, le=1.0)
    iv: float = Field(..., ge=0.0)              # implied volatility as decimal (0.31 = 31%)
    open_interest: int = Field(..., ge=0)
    spread_pct_of_mid: float                    # (ask - bid) / mid * 100
    data_source: str                            # "tos" | "chartexchange" | "yahoo" | "barchart" | "manual"
    chain_timestamp: str                        # ISO-8601

    @field_validator("mid")
    @classmethod
    def mid_between_bid_ask(cls, v: float, info) -> float:
        """Mid must be between bid and ask."""
        bid = info.data.get("bid")
        ask = info.data.get("ask")
        if bid is not None and ask is not None:
            if not (bid <= v <= ask):
                raise ValueError(f"mid {v} must be between bid {bid} and ask {ask}")
        return v
