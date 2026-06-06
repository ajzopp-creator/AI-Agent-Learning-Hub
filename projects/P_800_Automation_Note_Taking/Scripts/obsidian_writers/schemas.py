"""schemas.py — Pydantic models for all vault interface schemas.

Each model represents the fields a sending project passes to write_to_vault().
P_800 validates incoming data against these models before writing to Obsidian.
All fields not supplied by the sender default to None — P_800 never invents values.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


# ── P_115 EVALUATION RECORD ───────────────────────────────────────────────────

class P115Record(BaseModel):
    """One P_115 trade evaluation row."""
    date: date
    symbol: str
    signal_source: str = "P_115"
    step1_verdict: Optional[str] = None          # BUY | ASYM | PASS
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
    traded: Optional[str] = "N"                  # Y | N
    entry_price: Optional[float] = None
    tp_level: Optional[float] = None
    sl_level: Optional[float] = None
    stop_level: Optional[float] = None
    risk_pct: Optional[float] = None
    account_balance: Optional[float] = None
    outcome: Optional[str] = None                # TP Hit | SL Hit | Manual
    recheck_status: Optional[str] = None
    simulation_notes: Optional[str] = ""
    comments: Optional[str] = ""
    why_code: Optional[str] = None               # P_020 WHY vocabulary
    sig_code: Optional[str] = None               # P_020 SIG vocabulary


# ── P_300 SIGNAL RECORD ───────────────────────────────────────────────────────

class P300Record(BaseModel):
    """One P_300 signal report."""
    date: date
    ticker: str
    anchor_date: Optional[date] = None
    signal: Optional[str] = None                 # BUY | SELL | PASS
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
    date: date                                   # close_date (primary sort key)
    symbol: str
    account_id: Optional[str] = None             # AJZ6348 | IRA9885 | PAPER
    system: Optional[str] = None                 # WHY code
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
    outcome: Optional[str] = None               # TP Hit | SL Hit | Manual
    days_held: Optional[int] = None
    signal_strength: Optional[str] = None


# ── P_400 TRADE LIFECYCLE RECORD ──────────────────────────────────────────────

class P400Record(BaseModel):
    """One P_400 trade lifecycle entry (schema v0.1 — evolves with P_400 build)."""
    date: date
    ticker: str
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
    date: date
    title: str
    kb_type: Optional[str] = None               # Article | AI Summary | Research | Transcript
    origin: Optional[str] = None                # Web Clipper | PDF | AI Summary | Manual
    ai_summarized: Optional[bool] = False
    tags: Optional[List[str]] = Field(default_factory=list)
    ticker_relevance: Optional[List[str]] = Field(default_factory=list)
    sector: Optional[str] = None
    market_regime: Optional[str] = None
    linked_trades: Optional[List[str]] = Field(default_factory=list)


# ── SCHEMA REGISTRY ───────────────────────────────────────────────────────────

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "P115": P115Record,
    "P300": P300Record,
    "P020": P020Record,
    "P400": P400Record,
    "KB":   KBRecord,
}
