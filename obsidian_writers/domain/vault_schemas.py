"""vault_schemas.py — Pydantic models for Obsidian frontmatter records.

One model per source project (P_115, P_300, P_020, P_400, KB).
Each represents the fields that source system passes to write_to_vault().

P_800 validates incoming data against these models before writing to vault.

Required base fields (Note Standard v1.1 — md schemas only):
  signal_date   The date the signal applies to; used in filename construction.
  run_date      Calendar date the pipeline ran (YYYY-MM-DD string).
  run_ts        Full ISO 8601 datetime of pipeline run.
  written_by    Source module string, e.g. "P_300/daily_evaluate_pipeline".
  write_route   Normalized: BUY | WATCH | PASS (mapped by write_handler).
                Routing-only — files the note into the right vault folder.
                Renamed from 'verdict' 2026-07-10 (WO-P400-E2.020).
  note_version  Auto-incremented by vault_writer on every overwrite.
  write_route_history  List of prior write_route entries; managed by vault_writer.

Sending systems supply signal_date, run_date, run_ts, written_by, and their
native classification value. write_handler maps the native value to
write_route and injects note_version / write_route_history from disk.
"""

from datetime import date as _date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ── P_115 EVALUATION RECORD ───────────────────────────────────────────────────

class P115Record(BaseModel):
    """One P_115 trade evaluation row."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD — used in filename
    run_date: str                                # YYYY-MM-DD — calendar date pipeline ran
    run_ts: str                                  # ISO 8601 full datetime
    written_by: str                              # e.g. "P_115/tracker_writer"
    write_route: Optional[str] = None            # BUY | WATCH | PASS — set by write_handler
    note_version: int = 1                        # auto-managed by vault_writer
    write_route_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition; use signal_date going forward
    date: Optional[_date] = None

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
    write_route: Optional[str] = None            # BUY | WATCH | PASS — set by write_handler
    note_version: int = 1                        # auto-managed by vault_writer
    write_route_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition; use signal_date going forward
    date: Optional[_date] = None

    # P_300-specific fields
    ticker: str = ""
    anchor_date: Optional[_date] = None
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
    write_route: Optional[str] = None            # TBD — confirm when P_020 wired
    note_version: int = 1                        # auto-managed by vault_writer
    write_route_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition
    date: Optional[_date] = None

    # P_020-specific fields
    trade_id: Optional[str] = None            # source DB PK -- filename disambiguator (WO-P800-E3.002)
    symbol: str = ""
    account_id: Optional[str] = None            # AJZ6348 | IRA9885 | PAPER
    system: Optional[str] = None
    why_code: Optional[str] = None
    sig_code: Optional[str] = None
    open_date: Optional[_date] = None
    close_date: Optional[_date] = None
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
    write_route: Optional[str] = None            # BUY | WATCH | PASS — set by write_handler
    note_version: int = 1
    write_route_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition
    date: Optional[_date] = None

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
    order_id: Optional[str] = None  # broker order id, reported back by Tony after manual Schwab entry (WO-P400-E3.006)
    lifecycle_status: Optional[str] = "PENDING" # PENDING | OPEN | PARTIAL | CLOSED
    entry_date: Optional[_date] = None
    close_date: Optional[_date] = None
    realized_pnl: Optional[float] = None
    why_code: Optional[str] = None
    sig_code: Optional[str] = None
    p115_linked: Optional[bool] = False
    p300_linked: Optional[bool] = False
    drop_reason: Optional[str] = None         # ENTRY_MISSED | RR_INVALID | MANUAL_PASS | COUNCIL_BLOCK

    # Options fields (WO-P400-E3.004 scope item 5) -- all None for stock trades
    option_method: Optional[str] = None                    # chart_based | risk_budget_first
    option_structure: Optional[str] = None                 # single_leg | vertical_spread
    option_contract: Optional[str] = None                  # e.g. "ADBE260717C215"
    option_entry_premium: Optional[float] = None
    option_stop_premium: Optional[float] = None
    option_target_premium: Optional[float] = None
    option_contracts: Optional[int] = None
    option_override: Optional[bool] = None
    option_override_justification: Optional[str] = None
    iv_rank: Optional[float] = None

    # Vertical spread fields (WO-P400-E3.004 item 5 follow-up) -- None for
    # single-leg options and stock trades. option_contract holds the
    # short-leg OCC symbol in this case; long leg lives in option_contract's
    # sibling option_method context -- use spread_long_strike/short_strike
    # as the authoritative strike pair for spreads.
    spread_long_strike: Optional[float] = None
    spread_short_strike: Optional[float] = None
    spread_debit: Optional[float] = None
    spread_max_profit: Optional[float] = None
    spread_max_loss: Optional[float] = None
    spread_breakeven: Optional[float] = None

    # Injected unconditionally by write_handler._handle_md() for every md
    # schema (provenance tracking for vault_writer rebuild on overwrite).
    # P400 is the only schema with extra="forbid" -- the other four models
    # silently tolerate this injected key; P400 needs it modeled explicitly
    # or every P400 write fails validation. Found live 2026-06-30 -- this
    # means the pre-existing stock BLOCKED-write path was silently broken
    # too, not just the new options/spread paths added this session.
    source: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


# ── KNOWLEDGE BASE RECORD ─────────────────────────────────────────────────────

class KBRecord(BaseModel):
    """One knowledge base article or AI summary."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD — publication/capture date
    run_date: str                                # YYYY-MM-DD
    run_ts: str                                  # ISO 8601
    written_by: str                              # e.g. "KB/manual" or "KB/web_clipper"
    write_route: Optional[str] = None            # not applicable for KB; set to null
    note_version: int = 1
    write_route_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Deprecated — kept for transition
    date: Optional[_date] = None

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


# ── P_820 ORDER SIGNAL CAPTURE ─────────────────────────────────────────────
# Added 2026-08-16 (Tony directive, P_020 session). Thin capture record for
# non-Hub-generated signal sources (SNT, OIL/P_116, WSZ/P_117, Eddie Z/P_118)
# -- no council/verdict/sizing fields, viability is already decided upstream
# (subscription service or Tony's own verification) by the time this is
# logged. Highest-priority source in P_020's resolver: P_820 > ThinkLog >
# Tracker Dashboard > default.

class P820Record(BaseModel):
    """One dictated signal-source capture, logged at or near order time."""
    # Required base fields (Note Standard v1.1)
    signal_date: str                             # YYYY-MM-DD
    run_date: str                                # YYYY-MM-DD
    run_ts: str                                  # ISO 8601
    written_by: str                              # e.g. "P_820/chat_dictation"
    write_route: Optional[str] = None            # not applicable -- no verdict concept
    note_version: int = 1
    write_route_history: List[Dict[str, Any]] = Field(default_factory=list)

    # P_820-specific fields
    symbol: str = ""
    why_code: str = ""                         # open vocabulary: SNT, P_116, P_117, WSZ, etc.
                                                # -- becomes trades.system directly in P_020
    sig_code: Optional[str] = None
    entry_price: Optional[float] = None
    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    notes: Optional[str] = None
