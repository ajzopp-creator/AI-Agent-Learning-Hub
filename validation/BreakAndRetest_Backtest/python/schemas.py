"""
FILE: schemas.py
VERSION: 1.0
DATE: 2026-08-26
AUTHOR: Tony + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for the Break-and-Retest backtest.

    BulkBarRaw is copied from P_300's schemas_bulk.py (v1.2, verified
    against real 10-year bulk VP exports -- 22-column layout, neural_index
    as text, triple cross as price levels). Copied rather than imported
    live to keep this standalone script decoupled from P_300's config.py
    and package path.

    BreakRetestSignal is new -- one row per completed backtest trade.

CHANGELOG:
    - 2026-08-26 v1.0: Initial build.
"""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BulkBarRaw(BaseModel):
    """One bar as parsed from a bulk History Grid export (22-column layout).

    Copied verbatim from P_300 schemas_bulk.py v1.2 -- see that file's
    docstring for the verified field-shape notes (neural_index is text,
    triple cross are price levels, not diffs).
    """
    model_config = ConfigDict(frozen=True)

    bar_date: date
    stdiff: float
    mtdiff: float
    ltdiff: float
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    pred_high: float = Field(ge=0)
    pred_low: float = Field(ge=0)
    volume: float = Field(ge=0)
    williams_emai: float
    psi: float
    roc_pct: float
    neural_index: Literal["up", "down", "unknown"]
    neural_x_max: float
    tc_short: float = Field(ge=0)
    tc_medium: float = Field(ge=0)
    tc_long: float = Field(ge=0)
    pred_high_diff: float
    pred_low_diff: float
    pred_range: float = Field(ge=0)

    @model_validator(mode="after")
    def _high_ge_low(self) -> "BulkBarRaw":
        if self.high < self.low:
            raise ValueError(f"high ({self.high}) < low ({self.low}) for bar")
        return self


class BreakRetestSignal(BaseModel):
    """One completed backtest trade -- one row per signal fired."""
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(min_length=1, max_length=12)
    zone_low: float = Field(gt=0)
    zone_high: float = Field(gt=0)
    breakout_date: date
    breakout_close: float = Field(gt=0)
    retest_date: date
    entry_date: date
    entry_price: float = Field(gt=0)
    stop_loss: float = Field(gt=0)
    take_profit: float = Field(gt=0)
    exit_date: date
    exit_price: float = Field(gt=0)
    r_multiple: float
    exit_reason: Literal["stop", "target", "time"]
    is_win: bool
