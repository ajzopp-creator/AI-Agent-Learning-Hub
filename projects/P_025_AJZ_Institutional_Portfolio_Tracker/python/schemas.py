"""
P_025 AJZ Institutional Portfolio Tracker — Pydantic Schemas

All persistent data structures that are read from or written to non-temporary
files must be defined here. Domain and infrastructure layers import these
models; they never invent their own shapes.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Trade Log (source: P_020)
# ---------------------------------------------------------------------------

class TradeRecord(BaseModel):
    """Single trade row as produced by P_020 (or CSV fallback)."""

    trade_id: int
    account_id: str
    system: Optional[str] = None
    underlying_symbol: str
    asset_type: Literal["stock", "etf", "call", "put"] = "stock"
    direction: Literal["long", "short"] = "long"
    open_date: date
    open_datetime: Optional[datetime] = None
    qty: float
    entry_price: float
    stop_price: Optional[float] = None
    risk_amount: Optional[float] = None
    total_commissions: float = 0.0
    status: Literal["open", "partial", "closed"] = "open"
    realized_pnl: Optional[float] = None
    realized_R: Optional[float] = None
    schwab_transaction_id: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("account_id")
    @classmethod
    def normalise_account(cls, v: str) -> str:
        return v.strip().upper() if v else v

    @field_validator("underlying_symbol")
    @classmethod
    def upper_symbol(cls, v: str) -> str:
        return v.strip().upper()


# ---------------------------------------------------------------------------
# Market Data (yfinance closes)
# ---------------------------------------------------------------------------

class MarketDataRow(BaseModel):
    """One trading day of closing prices across tickers."""

    date: date
    prices: dict[str, float] = Field(default_factory=dict)
    # keys = ticker symbols, values = adjusted close


# ---------------------------------------------------------------------------
# Reference Data (static ticker metadata)
# ---------------------------------------------------------------------------

class ReferenceData(BaseModel):
    """Static reference information for a single ticker."""

    ticker: str
    company: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    beta: Optional[float] = None
    asset_class: Optional[str] = None

    @field_validator("ticker")
    @classmethod
    def upper_ticker(cls, v: str) -> str:
        return v.strip().upper()


# ---------------------------------------------------------------------------
# Daily Units (shares held end-of-day)
# ---------------------------------------------------------------------------

class DailyUnitsRow(BaseModel):
    """Shares held of each ticker at the close of a given date."""

    date: date
    units: dict[str, float] = Field(default_factory=dict)
    # keys = ticker, values = net shares (can be negative for short)


# ---------------------------------------------------------------------------
# Daily Cash
# ---------------------------------------------------------------------------

class DailyCashRow(BaseModel):
    """Cash balance for one account on one date."""

    date: date
    account_id: str
    cash_balance: float


class DailyInvestedRow(BaseModel):
    """Total invested market value (shares × price) for one date."""

    date: date
    invested_value: float


class CostBasisRow(BaseModel):
    """Lifetime long VWAP × current long shares. Not FIFO remaining cost."""

    ticker: str
    avg_cost: float
    current_shares: float
    total_cost_basis: float
    account_id: str = "AJZ6348"


class FifoLotRow(BaseModel):
    """One remaining long lot after FIFO consumption."""

    account_id: str
    ticker: str
    open_date: date
    remaining_qty: float
    lot_price: float
    remaining_cost: float
    source_trade_id: int


class FifoCostRow(BaseModel):
    """Remaining FIFO cost rolled up by account + ticker."""

    ticker: str
    account_id: str
    remaining_shares: float
    remaining_cost: float


# ---------------------------------------------------------------------------
# Convenience container used by application layer
# ---------------------------------------------------------------------------

class PortfolioSnapshot(BaseModel):
    """Complete in-memory snapshot before writing to Excel."""

    trades: list[TradeRecord] = Field(default_factory=list)
    market_data: list[MarketDataRow] = Field(default_factory=list)
    reference_data: list[ReferenceData] = Field(default_factory=list)
    daily_units: list[DailyUnitsRow] = Field(default_factory=list)
    daily_cash: list[DailyCashRow] = Field(default_factory=list)
    daily_invested: list[DailyInvestedRow] = Field(default_factory=list)
    cost_basis: list[CostBasisRow] = Field(default_factory=list)
    fifo_lots: list[FifoLotRow] = Field(default_factory=list)
    fifo_cost: list[FifoCostRow] = Field(default_factory=list)

    def tickers(self) -> set[str]:
        """Return the unique set of tickers present in trades."""
        return {t.underlying_symbol for t in self.trades}
