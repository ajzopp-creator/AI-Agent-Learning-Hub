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
    "EarningsEntry",
    "EarningsCalendarCache",
    "SymbolSpreadEntry",
    "LastSpreadCache",
    "RankedCandidate",
    "BatchReport",
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
    order_date: Optional[str] = None        # YYYY-MM-DD; from filename prefix (WO-P000-E10.001)


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
    price_basis: str = "live"          # "live" | "close" -- set by fetch_snapshot when market closed, WO-P400-E5.005
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


# ---------------------------------------------------------------------------
# Tier-2B batch runner (WO-P400-E5.003)
# ---------------------------------------------------------------------------

class EarningsEntry(BaseModel):
    """One symbol's earnings/sector data from the session-scoped earnings file.

    Bridge until WO-P400-E5.002 automates acquisition. Written once per
    session from the manual web-search pass; read by batch-2b.

    next_earnings_date is Optional because "no confirmed date" is a real,
    honest state (PNR, E5.002 log entry 2026-07-29). It is NOT the same as
    "clear" -- None means unknown, and the runner must surface that rather
    than treat it as no-earnings. Never fabricate a date to fill this.
    """

    symbol: str
    next_earnings_date: Optional[str] = None    # YYYY-MM-DD, None = unknown
    last_earnings_date: Optional[str] = None    # YYYY-MM-DD
    sector: Optional[str] = None
    source: str = "web_search"
    date_confirmed: bool = False                # False = estimated from cadence

    @field_validator("next_earnings_date", "last_earnings_date")
    @classmethod
    def iso_date_or_none(cls, v: Optional[str]) -> Optional[str]:
        """Reject malformed dates loudly rather than silently treating as clear."""
        if v is None:
            return v
        from datetime import date
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError(f"earnings date {v!r} is not ISO YYYY-MM-DD")
        return v


class EarningsCalendarCache(BaseModel):
    """Locally cached earnings calendar, refreshed on a monthly manual run
    (WO-P400-E5.002).

    Reuses EarningsEntry per-symbol -- same fields, same honest-null rules,
    whether an entry came from the old manual web-search file or this
    automated pull. pulled_date is the cache's own freshness marker, not
    per-symbol -- the whole cache refreshes in one FMP call.
    """

    pulled_date: str    # YYYY-MM-DD, ET, when this cache was built
    entries: Dict[str, EarningsEntry]


class SymbolSpreadEntry(BaseModel):
    """One symbol's last observed live regular-session half-spread.

    WO-P400-E5.005: written every time a live (market-open) quote is
    fetched, read when pricing a closed-market snapshot off the day's
    close -- real observed friction, just measured earlier, not a
    synthetic zero.
    """

    half_spread: float
    price: float          # price at observation time, sanity/audit only
    observed_at: str      # ISO-8601 UTC, live quote timestamp


class LastSpreadCache(BaseModel):
    """Locally cached per-symbol half-spreads (WO-P400-E5.005).

    No single pulled_date like EarningsCalendarCache -- each symbol updates
    independently on its own next live fetch, not a batch refresh.
    """

    entries: Dict[str, SymbolSpreadEntry] = {}


class RankedCandidate(BaseModel):
    """One scored row in the batch-2b ranked table.

    `score` is a deterministic composite. It is explicitly NOT a probability
    and NOT a confidence estimate -- P_400 has no probability model and this
    field must never be presented as one. score_components is carried so the
    ordering is auditable: a rank with no visible derivation is a number to
    argue with, not a number to trade on.
    """

    symbol: str
    rank: int
    score: float = Field(ge=0.0, le=1.0)
    score_components: Dict[str, float]

    vehicle: Literal["STOCK", "OPTION", "SPREAD", "OPTION_OVERRIDE_ONLY", "NEITHER"]
    verdict: str

    rr_at_t1: float
    atr_headroom: float          # stop distance / atr_14; >= 1.0 by QUANT gate
    spread_pct_of_price: float
    drift_pct: float
    dollar_risk: float
    quantity: int                # shares or contracts, per vehicle

    @field_validator("atr_headroom")
    @classmethod
    def headroom_at_least_floor(cls, v: float) -> float:
        """Anything ranked has cleared QUANT's stop >= 1x ATR gate.

        A value below 1.0 means a BLOCKED candidate reached ranking -- that is
        a wiring bug, not a low score, and must fail loudly rather than sort
        to the bottom where nobody looks. Live shape this guards against:
        INDI 2026-08-05, R:R 22.78 on a 0.05 stop against 0.31 ATR (0.16x).
        """
        if v < 1.0:
            raise ValueError(
                f"atr_headroom {v} < 1.0 -- candidate should have been BLOCKED "
                "by QUANT STOP_TOO_TIGHT and never reached ranking"
            )
        return v


class BatchReport(BaseModel):
    """Persisted output of one batch-2b run.

    cumulative_risk_if_all_taken is reported, never enforced (WO-P400-E5.003
    Scope 4, Tony's decision): each evaluate sizes independently against the
    book as it stands, and the runner shows the summed figure rather than
    silently arbitrating which trades a batch may contain.
    """

    run_timestamp: str
    session_date: str
    cash_available: float
    posture: str

    screened_count: int
    passed_tier1: int
    evaluated: int

    candidates: List[RankedCandidate] = []
    skipped: List[Dict[str, str]] = []      # {symbol, reason}

    cumulative_risk_if_all_taken: float
    heat_cap: float
    heat_warning: Optional[str] = None