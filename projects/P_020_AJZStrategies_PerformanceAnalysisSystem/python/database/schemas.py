"""P_020 Pydantic schemas — required for all non-temporary file I/O."""

from datetime import date, datetime
from typing import Dict, Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


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
    direction:             Literal["long", "short"]
    open_date:             date
    open_datetime:         Optional[datetime] = None
    qty:                   float
    entry_price:           float
    stop_price:            Optional[float]    = None
    risk_amount:           Optional[float]    = None
    total_commissions:     float              = 0.0
    status:                Literal["open", "partial", "closed"] = "open"
    tags:                  Optional[str]      = None
    notes:                 Optional[str]      = None
    source:                str                = "schwab_api"
    schwab_transaction_id: Optional[str]      = None
    reason:                Optional[str]      = None
    signal_strength:       Optional[str]      = None


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


# ── Tracker Dashboard models ───────────────────────────────────────────────

class TrackerEntry(BaseModel):
    """Represents one row from the Tracker Dashboard signal log.

    Maps to P_115_118_TrackerDashboard_V2.xlsx — Tracker Log sheet.
    Only rows where traded=True are loaded into the lookup.
    """

    trade_date:    date   = Field(description="Date column — signal evaluation date")
    symbol:        str    = Field(description="Ticker symbol — base symbol only, no suffix")
    signal_source: str    = Field(description="SignalSource column — e.g. P_115, P_118, P_300")
    traded:        bool   = Field(
        default=False,
        description="Traded column — 'Yes' means actually executed, 'No' means simulated only",
    )
    entry_price:   Optional[float] = Field(
        default=None,
        description="EntryPrice column — actual entry price if traded",
    )
    outcome:       Optional[str]   = Field(
        default=None,
        description="Outcome column — TP Hit, SL Hit, No Trade, etc.",
    )
    stop_level:    Optional[float] = Field(
        default=None,
        description="StopLevel column (col 21) — chart/analyst-set hard stop",
    )
    sl_level:      Optional[float] = Field(
        default=None,
        description="SLLevel column (col 20) — ATR-formula stop, fallback when StopLevel absent",
    )
    stop_level:    Optional[float] = Field(
        default=None,
        description="StopLevel column (col 21) — chart/analyst-set hard stop",
    )
    sl_level:      Optional[float] = Field(
        default=None,
        description="SLLevel column (col 20) — ATR-formula stop, fallback when StopLevel absent",
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """Strip option suffixes and whitespace, return uppercase base symbol."""
        return str(v).strip().split()[0].upper()

    @field_validator("signal_source", mode="before")
    @classmethod
    def normalize_signal_source(cls, v: str) -> str:
        """Strip whitespace from signal source value."""
        return str(v).strip()

    @field_validator("traded", mode="before")
    @classmethod
    def parse_traded(cls, v) -> bool:
        """Convert 'Yes'/'No'/'-'/None string to boolean."""
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in ("yes", "true", "1", "y")

    @property
    def lookup_key(self) -> Tuple[str, str]:
        """Return (symbol, 'YYYY-MM-DD') tuple used as lookup dict key."""
        return (self.symbol, self.trade_date.strftime("%Y-%m-%d"))


class TrackerLookup(BaseModel):
    """In-memory lookup table built from Tracker Dashboard rows.

    Keyed by (symbol, 'YYYY-MM-DD') → system_id string.
    Only includes rows where traded=True.
    """

    entries:       Dict[Tuple[str, str], str]                   = Field(default_factory=dict)
    stop_prices:   Dict[Tuple[str, str], Optional[float]]       = Field(default_factory=dict)
    total_rows:    int = 0
    traded_rows:   int = 0
    skipped_rows:  int = 0
    source_file:   str = ""

    def get(self, symbol: str, trade_date: str, default: str = "TOS_Import") -> str:
        """Look up system name for a symbol + date pair.

        Tries exact date first, then widens to a ±3-day window so signal
        date and trade date mismatches (common for options) still resolve.

        Args:
            symbol: Underlying symbol (normalized to uppercase before lookup).
            trade_date: Date string 'YYYY-MM-DD'.
            default: Fallback value if no match found.

        Returns:
            Matched system_id string or default.
        """
        from datetime import date, timedelta
        sym = symbol.strip().upper()
        base = date.fromisoformat(trade_date)
        # Exact match first
        key = (sym, trade_date)
        if key in self.entries:
            return self.entries[key]
        # Walk ±1, ±2, ±3 days
        for delta in [1, -1, 2, -2, 3, -3]:
            candidate = (sym, (base + timedelta(days=delta)).strftime("%Y-%m-%d"))
            if candidate in self.entries:
                return self.entries[candidate]
        return default

    def get_stop(self, symbol: str, trade_date: str) -> Optional[float]:
        """Look up the resolved stop price for a symbol + date pair.

        Applies StopLevel-first / SLLevel-fallback logic at read time.
        Returns None if no stop price was recorded for this entry.

        Args:
            symbol: Underlying symbol (normalized to uppercase before lookup).
            trade_date: Date string 'YYYY-MM-DD'.

        Returns:
            Stop price as float, or None if not found.
        """
        key = (symbol.strip().upper(), trade_date)
        return self.stop_prices.get(key)

    def summary(self) -> str:
        """Return a one-line summary for logging."""
        return (
            f"TrackerLookup: {len(self.entries)} entries loaded "
            f"({self.traded_rows} traded / {self.total_rows} total rows) "
            f"from {self.source_file}"
        )


# ── Weekly-update state ─────────────────────────────────────────────────────

class LastRunFile(BaseModel):
    """P_020_last_run.json — tracks the last successful weekly update."""

    last_run_date:     str
    last_run_datetime: Optional[str] = Field(
        default=None,
        description="Full ISO timestamp of last successful run; date-only for legacy files.",
    )
