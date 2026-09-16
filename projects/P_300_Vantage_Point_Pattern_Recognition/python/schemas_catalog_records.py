"""
FILE: schemas_catalog_records.py
VERSION: 1.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Split out of schemas.py (WO-P300-E5.001, file-size fix -- schemas.py
    had no prior DEBT NOTE naming this split; grouping follows schemas.py's
    own docstring, which already documented "CATALOG ROW models:
    SymbolRecord, SourceFileRecord, FeatureSetRecord, PatternInstanceRecord,
    PatternBarRecord, ForwardLabelRecord" as a distinct group before this
    split existed -- PowerGaugeResult added later at v2.x, same group by
    kind: every one of these seven is a real catalog/persistence row shape).

    The seven-table catalog schema's Pydantic row models: symbols,
    source_files, feature_sets, pattern_instances, pattern_bars,
    forward_labels, plus PowerGaugeResult (Chaikin scrape result,
    persisted alongside but not part of the original 7-table DDL).

    PatternInstanceRecord.data_origin_type is typed against
    schemas.py:DataOriginType -- imported back from schemas.py, which
    still owns that enum (it wasn't part of this split; it's a Stage-4
    core type schemas.py's own docstring groups separately from both
    the INPUT and CATALOG ROW model families).

    schemas.py re-exports every name in this file for backward
    compatibility -- existing `from schemas import X` call sites for
    these seven models were not touched.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from config import FORWARD_HORIZONS, MAX_WINDOW_LENGTH, MIN_WINDOW_LENGTH
from schemas import DataOriginType


# ---------------------------------------------------------------------------
# CATALOG ROWS -- Optional[PK] supports pre-insert and post-insert use
# ---------------------------------------------------------------------------

class SymbolRecord(BaseModel):
    """symbols table row -- identity lookup."""
    symbol_id: Optional[int] = None
    ticker: str = Field(min_length=1, max_length=12)


class SourceFileRecord(BaseModel):
    """source_files table row -- pattern provenance."""
    source_file_id: Optional[int] = None
    filename: str
    symbol_id: int
    imported_at: datetime
    row_count: int = Field(gt=0)


class FeatureSetRecord(BaseModel):
    """feature_sets table row -- feature-engineering version metadata."""
    feature_set_id: Optional[int] = None
    feature_version: str = Field(min_length=1, max_length=32)
    description: Optional[str] = None
    created_at: datetime


class PatternInstanceRecord(BaseModel):
    """
    pattern_instances table row.

    LAUNCH framing: anchor_date = launch date (start of trend).
    window_length = count of bars stored in pattern_bars for this pattern
    (5..20). Setup bars span offsets -(window_length-1) through 0.
    """
    pattern_instance_id: Optional[int] = None
    symbol_id: int
    source_file_id: int
    feature_set_id: int
    anchor_date: date
    window_length: int = Field(ge=MIN_WINDOW_LENGTH, le=MAX_WINDOW_LENGTH)
    data_origin_type: DataOriginType


class PatternBarRecord(BaseModel):
    """
    pattern_bars table row -- raw VP fields plus normalized columns.

    bar_offset = 0 is the anchor (launch day); negative offsets are
    setup bars before the launch. The bar_offset constraint here is
    the global bound (-19..0); per-pattern range is implicitly
    constrained by that pattern's window_length.
    """
    pattern_bar_id: Optional[int] = None
    pattern_instance_id: int
    bar_offset: int = Field(le=0, ge=-(MAX_WINDOW_LENGTH - 1))
    bar_date: date

    # Raw VP data (audit trail) -- mirrors VPBarRaw
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    stdiff: float
    mtdiff: float
    ltdiff: float
    pred_high: float = Field(gt=0)
    pred_low: float = Field(gt=0)
    pred_range: float = Field(ge=0)
    williams_emai: float
    psi: float
    neural_index: float
    triple_cross_short: float
    triple_cross_medium: float
    triple_cross_long: float

    # Normalization layer (architecture §9.3) -- cross-symbol comparability
    close_pct_from_anchor: float
    range_pct: float = Field(ge=0)
    body_pct: float
    volume_zscore: float
    stdiff_pct: float
    mtdiff_pct: float
    ltdiff_pct: float
    pred_high_pct: float
    pred_low_pct: float
    pred_range_pct: float = Field(ge=0)


class ForwardLabelRecord(BaseModel):
    """
    forward_labels table row -- outcome at one horizon for one pattern.
    horizon_days must be one of architecture-defined horizons (5/7/10/15/20).
    """
    forward_label_id: Optional[int] = None
    pattern_instance_id: int
    horizon_days: int
    future_date: date
    return_pct: float
    is_profitable: bool

    @field_validator("horizon_days")
    @classmethod
    def _horizon_in_allowed_set(cls, v: int) -> int:
        if v not in FORWARD_HORIZONS:
            raise ValueError(
                f"horizon_days {v} not in allowed set {FORWARD_HORIZONS}"
            )
        return v


class PowerGaugeResult(BaseModel):
    """
    Chaikin Analytics Power Gauge Rating scrape result for one symbol.

    Read-only external data -- not part of the BUY/WATCH/PASS decision
    path (NFR-1). Attached to the P300 Obsidian note as supplementary
    context for P_400, never fed back into signal_classifier.
    """
    ticker: str
    rating: str          # e.g. "Very Bullish", "Bullish", "Neutral", "Bearish", "Very Bearish"
    rating_score: Optional[float] = None   # numeric score if Chaikin exposes one, else None
    scraped_at: datetime
    source_url: str
