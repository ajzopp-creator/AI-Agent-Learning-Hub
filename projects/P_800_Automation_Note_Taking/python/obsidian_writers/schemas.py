"""schemas.py — Pydantic models for all vault interface schemas.

Each model represents the fields a sending project passes to write_to_vault().
P_800 validates incoming data against these models before writing to Obsidian.

Required base fields (Note Standard v1.1 — md schemas only):
  signal_date   The date the signal applies to; used in filename construction.
  run_date      Calendar date the pipeline ran (YYYY-MM-DD string).
  run_ts        Full ISO 8601 datetime of pipeline run.
  ticker        Uppercase symbol (P300/P400/KB) or symbol (P115/P020).
  verdict       Normalized: BUY | WATCH | PASS (mapped by write_handler).
  written_by    Source module string, e.g. "P_300/daily_evaluate_pipeline".
  note_version  Auto-incremented by vault_writer on every overwrite.
  verdict_history  List of prior verdict entries; managed by vault_writer.

Sending systems supply signal_date, run_date, run_ts, written_by, and their
native classification value. write_handler maps the native value to verdict
and injects note_version / verdict_history from disk.

P400SIG is the exception: a raw JSON signal packet (P_115 -> P_400 handoff),
not an Obsidian note. It uses its own nested shape (P400SignalRecord) and skips
the Note Standard base fields, verdict normalization, and provenance tracking.

CHANGELOG:
  v2.1  2026-06-02  Added P400SignalRecord (+ SignalContext, SignalMetadata)
                    and registered "P400SIG". Locked to
                    P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0. Enables the JSON
                    emit path for P_115 -> P_400 signal packets (Enh. 1).
  v2.0  2026-06-01  Note Standard v1.1 — added required base fields to all
                    records. 'date' retained as deprecated optional fallback.
                    'signal' retained on P300Record for backward compat (v3.0
                    migration). VERDICT_MAP moved to config.py.
  v1.0  2026-05-22  Initial version.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ── P_115 EVALUATION RECORD ───────────────────────────────────────────────────

class P115Record(BaseModel):
    """One P_115 trade evaluation row."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD — used in filename
    run_date: str                                # YYYY-MM-DD — calendar date pipeline ran
    run_ts: str                                  # ISO 8601 full datetime
    written_by: str                              # e.g. "P_115/tracker_writer"
    verdict: Optional[str] = None               # BUY | WATCH | PASS — set by write_handler
    note_version: int = 1                        # auto-managed by vault_writer
    verdict_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition; use signal_date going forward
    date: Optional[date] = None

    # P_115-specific fields (27-column tracker schema)
    symbol: str = ""
    signal_source: str = "P_115"
    step1_verdict: Optional[str] = None         # BUY | ASYM | PASS
    pattern_type: Optional[str] = None
    breakout_verdict: Optional[str] = None
    breakout_volume_multiple: Optional[float] = None
    distribution_day_count: Optional[int] = None
    follow_through_day: Optional[str] = None
    market_direction: Optional[str] = None
    rs_vs_spy: Optional[float] = None
    fundamentals_tier: Optional[int] = None
    analysis_tier: Optional[int] = None
    candle_tier: Optional[int] = None
    setup_score: Optional[int] = None
    liquidity_tier: Optional[int] = None
    traded: Optional[str] = "N"                 # Y | N
    entry_price: Optional[float] = None
    tp_level: Optional[float] = None
    sl_level: Optional[float] = None
    stop_level: Optional[float] = None
    risk_pct: Optional[float] = None
    account_balance: Optional[float] = None
    outcome: Optional[str] = None               # TP Hit | SL Hit | Manual
    recheck_status: Optional[str] = None
    simulation_notes: Optional[str] = ""
    comments: Optional[str] = ""
    why_code: Optional[str] = None              # P_020 WHY vocabulary
    sig_code: Optional[str] = None              # P_020 SIG vocabulary


# ── P_300 SIGNAL RECORD ───────────────────────────────────────────────────────

class P300Record(BaseModel):
    """One P_300 signal report."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD — used in filename
    run_date: str                                # YYYY-MM-DD — calendar date pipeline ran
    run_ts: str                                  # ISO 8601 full datetime
    written_by: str                              # e.g. "P_300/daily_evaluate_pipeline"
    verdict: Optional[str] = None               # BUY | WATCH | PASS — set by write_handler
    note_version: int = 1                        # auto-managed by vault_writer
    verdict_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition; use signal_date going forward
    date: Optional[date] = None

    # P_300-specific fields
    ticker: str = ""
    anchor_date: Optional[date] = None
    signal: Optional[str] = None                # BUY | WATCH | PASS — kept for backward compat (remove in v3.0)
    signal_horizon: Optional[int] = None
    generated_dt: Optional[str] = None
    h5_win_rate: Optional[float] = None
    h5_mean_ret: Optional[float] = None
    h5_z_score: Optional[float] = None
    h5_class: Optional[str] = None
    h7_win_rate: Optional[float] = None
    h7_mean_ret: Optional[float] = None
    h7_z_score: Optional[float] = None
    h7_class: Optional[str] = None
    h10_win_rate: Optional[float] = None
    h10_mean_ret: Optional[float] = None
    h10_z_score: Optional[float] = None
    h10_class: Optional[str] = None
    h15_win_rate: Optional[float] = None
    h15_mean_ret: Optional[float] = None
    h15_z_score: Optional[float] = None
    h15_class: Optional[str] = None
    h20_win_rate: Optional[float] = None
    h20_mean_ret: Optional[float] = None
    h20_z_score: Optional[float] = None
    h20_class: Optional[str] = None
    top_analog_1: Optional[str] = None
    top_analog_2: Optional[str] = None
    top_analog_3: Optional[str] = None
    top_comp_dist_1: Optional[float] = None
    n_matches: Optional[int] = None


# ── P_020 PERFORMANCE RECORD ──────────────────────────────────────────────────

class P020Record(BaseModel):
    """One closed trade performance record from P_020 SQLite."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD — close_date as signal key
    run_date: str                                # YYYY-MM-DD — calendar date pipeline ran
    run_ts: str                                  # ISO 8601 full datetime
    written_by: str                              # e.g. "P_020/performance_writer"
    verdict: Optional[str] = None               # TBD — confirm when P_020 wired
    note_version: int = 1                        # auto-managed by vault_writer
    verdict_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition
    date: Optional[date] = None

    # P_020-specific fields
    symbol: str = ""
    account_id: Optional[str] = None            # AJZ6348 | IRA9885 | PAPER
    system: Optional[str] = None
    why_code: Optional[str] = None
    sig_code: Optional[str] = None
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    qty: Optional[int] = None
    realized_pnl: Optional[float] = None
    realized_R: Optional[float] = None
    risk_amount: Optional[float] = None
    outcome: Optional[str] = None              # TP Hit | SL Hit | Manual
    days_held: Optional[int] = None
    signal_strength: Optional[str] = None


# ── P_400 TRADE LIFECYCLE RECORD ──────────────────────────────────────────────

class P400Record(BaseModel):
    """One P_400 trade lifecycle entry (schema v0.1 — evolves with P_400 build)."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD
    run_date: str                                # YYYY-MM-DD
    run_ts: str                                  # ISO 8601
    written_by: str                              # e.g. "P_400/council_writer"
    verdict: Optional[str] = None               # BUY | WATCH | PASS — set by write_handler
    note_version: int = 1
    verdict_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition
    date: Optional[date] = None

    # P_400-specific fields
    ticker: str = ""
    account_id: Optional[str] = None
    council_verdict: Optional[str] = None       # Approve | Approve with Caution | Block | Override Required
    risk_mode: Optional[str] = None
    entry_price: Optional[float] = None
    stop_price: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    position_size: Optional[float] = None
    order_type: Optional[str] = None
    lifecycle_status: Optional[str] = "PENDING" # PENDING | OPEN | PARTIAL | CLOSED
    entry_date: Optional[date] = None
    close_date: Optional[date] = None
    realized_pnl: Optional[float] = None
    why_code: Optional[str] = None
    sig_code: Optional[str] = None
    p115_linked: Optional[bool] = False
    p300_linked: Optional[bool] = False


# ── KNOWLEDGE BASE RECORD ─────────────────────────────────────────────────────

class KBRecord(BaseModel):
    """One knowledge base article or AI summary."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD — publication/capture date
    run_date: str                                # YYYY-MM-DD
    run_ts: str                                  # ISO 8601
    written_by: str                              # e.g. "KB/manual" or "KB/web_clipper"
    verdict: Optional[str] = None               # not applicable for KB; set to null
    note_version: int = 1
    verdict_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition
    date: Optional[date] = None

    # KB-specific fields
    title: str = ""
    kb_type: Optional[str] = None              # Article | AI Summary | Research | Transcript
    origin: Optional[str] = None               # Web Clipper | PDF | AI Summary | Manual
    ai_summarized: Optional[bool] = False
    tags: Optional[List[str]] = Field(default_factory=list)
    ticker_relevance: Optional[List[str]] = Field(default_factory=list)
    sector: Optional[str] = None
    market_regime: Optional[str] = None
    linked_trades: Optional[List[str]] = Field(default_factory=list)


# ── P_400 SIGNAL PACKET (P400SIG) ─────────────────────────────────────────────
# Raw JSON handoff, NOT an Obsidian note. Locked to
# P_115_P400_SIGNAL_PACKET_SCHEMA_v1_0. Nested shape; no Note Standard fields,
# no verdict normalization, no provenance tracking.

class SignalContext(BaseModel):
    """context{} sub-object of a P_400 signal packet."""
    close_at_signal: float                       # close price at signal generation (audit)
    trailing_volume_30d: float                   # avg daily volume, last 30 days
    signal_rationale: str                        # short thesis summary
    atm_at_signal: Optional[float] = None        # ATR(14) at signal time (optional)


class SignalMetadata(BaseModel):
    """signal_metadata{} sub-object of a P_400 signal packet."""
    p115_session_date: str                       # YYYY-MM-DD of generating P_115 session
    p115_chart_timeframe: str                    # 1D | 4H | 1H | etc
    signal_source_link: str                      # path to upstream P_115/P_300 .md (audit)


class P400SignalRecord(BaseModel):
    """One P_115 -> P_400 signal packet (JSON emit, Enhancement 1)."""
    signal_id: str                               # e.g. P115-2026-06-02-AMTM-001
    signal_timestamp: str                        # ISO 8601 (UTC) of generation
    signal_source: str                           # P_115 | P_300 | manual
    strategy: str                                # dip_buy | breakout | mean_reversion | etc
    symbol: str                                  # uppercase ticker
    guideline_entry: float                       # recommended entry price
    guideline_stop: float                        # recommended stop-loss
    guideline_target: float                      # recommended profit target
    signal_horizon: str                          # e.g. "3-5 days"
    confidence_level: str                        # HIGH | MEDIUM | LOW
    context: SignalContext
    signal_metadata: SignalMetadata


# ── SCHEMA REGISTRY ───────────────────────────────────────────────────────────

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "P115":    P115Record,
    "P300":    P300Record,
    "P020":    P020Record,
    "P400":    P400Record,
    "P400SIG": P400SignalRecord,
    "KB":      KBRecord,
}

# ============================================================================
# v2.0 Signal Schema — Unified for Stocks and Options
# ============================================================================

from enum import Enum
from pydantic import BaseModel, field_validator
from typing import Optional

class AssetClass(str, Enum):
    """Discriminator for stock vs options signals."""
    STOCK = "stock"
    OPTION = "option"


class OptionType(str, Enum):
    """Options-only: call or put."""
    CALL = "call"
    PUT = "put"


class SignalContext(BaseModel):
    """Context data for signal generation (shared by stocks and options)."""
    atm_at_signal: Optional[float] = None
    close_at_signal: float
    trailing_volume_30d: float
    signal_rationale: str


class SignalMetadata(BaseModel):
    """Metadata linking signal back to upstream system."""
    p115_session_date: str
    p115_chart_timeframe: str
    signal_source_link: str


class SignalV2(BaseModel):
    """Unified v2.0 signal schema for stocks and options."""
    signal_id: str
    signal_timestamp: str
    signal_source: str
    strategy: str
    symbol: str
    asset_class: AssetClass
    guideline_entry: float
    guideline_stop: float
    guideline_target: float
    signal_horizon: str
    confidence_level: str
    position_size: int
    strike_price: Optional[float] = None
    underlying_price: Optional[float] = None
    option_type: Optional[OptionType] = None
    expiration_date: Optional[str] = None
    context: SignalContext
    signal_metadata: SignalMetadata

    class Config:
        use_enum_values = True

    @field_validator("asset_class")
    @classmethod
    def validate_asset_class(cls, v):
        if v not in [AssetClass.STOCK, AssetClass.OPTION]:
            raise ValueError(f"asset_class must be ''stock'' or ''option'', got {v}")
        return v

    @field_validator("expiration_date")
    @classmethod
    def validate_option_expiration(cls, v, info):
        asset_class = info.data.get("asset_class")
        if asset_class == AssetClass.OPTION:
            if v is None:
                raise ValueError("expiration_date required for options")
            try:
                from datetime import datetime
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError(f"expiration_date must be YYYY-MM-DD, got {v}")
        elif asset_class == AssetClass.STOCK:
            if v is not None:
                raise ValueError("expiration_date must be null for stocks")
        return v

    @field_validator("strike_price", "underlying_price")
    @classmethod
    def validate_option_prices(cls, v, info):
        field_name = info.field_name
        asset_class = info.data.get("asset_class")
        if asset_class == AssetClass.OPTION and v is None:
            raise ValueError(f"{field_name} required for options")
        elif asset_class == AssetClass.STOCK and v is not None:
            raise ValueError(f"{field_name} must be null for stocks")
        return v

    @field_validator("option_type")
    @classmethod
    def validate_option_type(cls, v, info):
        asset_class = info.data.get("asset_class")
        if asset_class == AssetClass.OPTION:
            if v is None:
                raise ValueError("option_type required for options")
            if v not in [OptionType.CALL, OptionType.PUT]:
                raise ValueError(f"option_type must be ''call'' or ''put'', got {v}")
        elif asset_class == AssetClass.STOCK and v is not None:
            raise ValueError("option_type must be null for stocks")
        return v

    @field_validator("confidence_level")
    @classmethod
    def validate_confidence(cls, v):
        if v not in ["HIGH", "MEDIUM", "LOW"]:
            raise ValueError(f"confidence_level must be HIGH, MEDIUM, or LOW, got {v}")
        return v

    @field_validator("guideline_entry", "guideline_stop", "guideline_target")
    @classmethod
    def validate_prices_positive(cls, v):
        if v <= 0:
            raise ValueError(f"Price must be positive, got {v}")
        return v

    @field_validator("guideline_target")
    @classmethod
    def validate_price_logic(cls, v, info):
        entry = info.data.get("guideline_entry")
        stop = info.data.get("guideline_stop")
        if entry and v <= entry:
            raise ValueError(f"guideline_target ({v}) must be > guideline_entry ({entry})")
        if entry and stop and entry <= stop:
            raise ValueError(f"guideline_entry ({entry}) must be > guideline_stop ({stop})")
        return v