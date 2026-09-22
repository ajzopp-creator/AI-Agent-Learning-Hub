"""P_020 Pydantic schemas — trade domain models.

Split from schemas.py (WO-P020-E1.018 Independent Review follow-up,
2026-09-19) -- schemas.py was 303 lines, over the 300-line hard cap.
Account/TradingSystem/Trade/Exit/SpreadLeg/TradeParams: the core trade
domain, used across ingestion, writers, and tests. Tracker Dashboard
models moved to schemas_tracker.py; LastRunFile/Order moved to
schemas_ops.py.
"""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ── Seed data models ───────────────────────────────────────────────────────

class Account(BaseModel):
    """Represents a single tracked brokerage account."""

    account_id:         str
    account_name:       str
    account_type:       Literal["live", "invest", "paper"]
    broker:             str
    distribution_years: Optional[int] = Field(
        default=None,
        description="IRA distribution window in years — null for non-IRA accounts.",
    )


class TradingSystem(BaseModel):
    """Represents a named trading system (P_115, P_118, etc.)."""

    system_id:   str
    system_name: str
    description: str
    active:      int = 1


# ── Core trade models ──────────────────────────────────────────────────────

class Trade(BaseModel):
    """Represents a single opened position."""

    trade_id:              Optional[int]      = None
    account_id:            str
    system:                str
    underlying_symbol:     str
    asset_type:            Literal["stock", "etf", "call", "put", "spread"]
    direction:              Literal["long", "short"]
    open_date:              date
    open_datetime:          Optional[datetime] = None
    qty:                    float
    entry_price:            float
    stop_price:             Optional[float]    = None
    risk_amount:            Optional[float]    = None
    total_commissions:      float              = 0.0
    status:                 Literal["open", "partial", "closed"] = "open"
    tags:                   Optional[str]      = None
    notes:                  Optional[str]      = None
    source:                 str                = "schwab_api"
    schwab_transaction_id:  Optional[str]      = None
    reason:                 Optional[str]      = None
    signal_strength:        Optional[str]      = None
    expiration_date:        Optional[date]     = Field(
        default=None,
        description="Option expiration date, captured at entry-parse time "
                    "(WO-P020-E1.018). None for stock/etf.",
    )
    settlement_price:       Optional[float]    = Field(
        default=None,
        description="Schwab instrument.closingPrice snapshot at entry-parse "
                    "time -- used as the synthetic exit price when a 0DTE "
                    "cash-settled option expires with no closing "
                    "transaction (WO-P020-E1.018). None for stock/etf.",
    )
    spread_group_id:         Optional[str]     = Field(
        default=None,
        description="Shared key linking every leg-trade of one multi-leg "
                    "spread order (WO-P020-E1.021) -- legs sharing a live "
                    "Schwab orderId at entry get the same value here, e.g. "
                    "'SG_<order_id>'. None for a standalone single-leg "
                    "trade. Reporting nets legs sharing this value into one "
                    "win/loss/R unit via v_trade_summary_grouped instead of "
                    "counting each leg as its own trade.",
    )


class Exit(BaseModel):
    """Represents one exit leg of a trade (partial or full)."""

    exit_id:          Optional[int]      = None
    trade_id:         int
    exit_number:      int                = Field(ge=1, description="1, 2, or 3")
    exit_date:        date
    exit_datetime:    Optional[datetime] = None
    qty_exited:       float
    exit_price:       float
    exit_commissions: float              = 0.0
    exit_pnl:         float
    hold_days:        int


class SpreadLeg(BaseModel):
    """One leg of a multi-leg spread trade (WO-P020-E1.002)."""

    leg_id:          Optional[int]                      = None
    trade_id:        int
    leg_number:      int                                = Field(ge=1)
    full_symbol:     str
    put_call:        Optional[Literal["CALL", "PUT"]]    = None
    position_effect: str                                = "OPENING"
    direction:       Literal["long", "short"]
    qty:             float
    price:           float


# ── Config / params model ──────────────────────────────────────────────────

class TradeParams(BaseModel):
    """Business parameters loaded from P_020_Account_Params.json."""

    default_risk_pct:             float = Field(gt=0, lt=1)
    options_multiplier:           int   = Field(gt=0)
    consolidation_window_minutes: int   = Field(gt=0)
    default_system_name:          str
