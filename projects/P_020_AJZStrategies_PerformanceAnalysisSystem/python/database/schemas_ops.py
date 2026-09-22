"""P_020 Pydantic schemas — weekly-update state and P_400 order models.

Split from schemas.py (WO-P020-E1.018 Independent Review follow-up,
2026-09-19). LastRunFile: P_020_last_run.json tracker. Order: P_400's
SQLite source-of-truth order record (WO-P400-E6.001 Scope item 2).
"""

from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# ── Weekly-update state ─────────────────────────────────────────────────────

class LastRunFile(BaseModel):
    """P_020_last_run.json — tracks the last successful weekly update."""

    last_run_date:     str
    last_run_datetime: Optional[str] = Field(
        default=None,
        description="Full ISO timestamp of last successful run; date-only for legacy files.",
    )


# ── Order model (WO-P400-E6.001 Scope item 2) ──────────────────────────────

class Order(BaseModel):
    """Represents a single P_400-submitted order (SQLite source of truth).

    Maps to the `orders` table (migration_add_orders_table.py). Attribution
    fields (why_code/sig_code/source_project/confidence_tier) follow the
    Signal Source ID + confidence-tier vocabulary defined by WO-P000-E22.001,
    per WO-P400-E6.001's 2026-09-06 coordination note -- not a competing
    scheme.

    entry_fill_price/asset_type/put_call added 2026-09-07 (file 6 sizing):
    promote_order_to_trade() needs the actual fill price (not just the
    planned one) and a real EQUITY/OPTION + putCall pair to map through
    schwab_mapper.py's existing _map_asset_type() into Trade.asset_type.
    """

    order_id:               Optional[int]      = None
    account_id:             str
    symbol:                 str
    side:                   Literal["long", "short"]
    qty:                    float
    planned_entry_price:    Optional[float]    = None
    planned_stop_price:     Optional[float]    = None
    planned_target_price:   Optional[float]    = None
    trade_mode:             Literal["REAL", "PAPER"] = "REAL"
    submitted_ts:           datetime
    schwab_order_id:        Optional[str]      = None
    status:                 Literal[
        "pending", "working", "filled", "canceled", "expired", "closed"
    ] = "pending"
    council_verdict:        Optional[str]      = None
    why_code:                Optional[str]      = None
    sig_code:                Optional[str]      = None
    source_project:          str                = "P400"
    confidence_tier:        Literal[
        "CONFIRMED", "INFERRED", "UNRESOLVED"
    ] = "CONFIRMED"
    entry_date:              Optional[date]     = None
    close_date:              Optional[date]     = None
    realized_pnl:            Optional[float]    = None
    entry_fill_price:        Optional[float]    = None
    asset_type:              Optional[Literal["EQUITY", "OPTION"]] = None
    put_call:                Optional[Literal["CALL", "PUT"]]      = None
