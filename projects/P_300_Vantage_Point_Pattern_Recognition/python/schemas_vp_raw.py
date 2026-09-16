"""
FILE: schemas_vp_raw.py
VERSION: 1.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Split out of schemas.py (WO-P300-E5.001, file-size fix -- schemas.py
    had no prior DEBT NOTE naming this split; grouping follows schemas.py's
    own docstring, which already documented "INPUT models (VP XLSX
    parsing): VPBarRaw, PatternFileMetadata, PatternFileParse" as a
    distinct group before this split existed).

    Raw VP XLSX parsing shapes: one bar as read off a History Grid /
    Pattern export (VPBarRaw), the filename-derived metadata for a
    Pattern_<start>_<end>_<symbol>.xlsx file (PatternFileMetadata), and
    the combined parse result (PatternFileParse).

    schemas.py re-exports every name in this file for backward
    compatibility -- existing `from schemas import X` call sites for
    these three models were not touched.
"""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# INPUT -- VP XLSX parsing
# ---------------------------------------------------------------------------

class VPBarRaw(BaseModel):
    """
    One bar as parsed from a VantagePoint History Grid XLSX export.
    Field order matches architecture §9.2 pattern_bars raw section.
    """
    model_config = ConfigDict(frozen=True)

    bar_date: date
    # OHLC -- prices must be strictly positive
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    # Volume -- non-negative; zero permitted on rare quiet days
    volume: float = Field(ge=0)
    # VP term differences (can be negative)
    stdiff: float
    mtdiff: float
    ltdiff: float
    # Predicted price levels and range
    pred_high: float = Field(gt=0)
    pred_low: float = Field(gt=0)
    pred_range: float = Field(ge=0)
    # VP indicators (dimensionless, can be negative)
    williams_emai: float
    psi: float
    neural_index: float
    triple_cross_short: float
    triple_cross_medium: float
    triple_cross_long: float

    @model_validator(mode="after")
    def _high_ge_low(self) -> "VPBarRaw":
        if self.high < self.low:
            raise ValueError(f"high ({self.high}) < low ({self.low}) for bar")
        return self


class PatternFileMetadata(BaseModel):
    """
    Metadata extracted from a Pattern_<start>_<end>_<symbol>.xlsx filename.
    Produced by the filename parser before any bars are read.
    """
    model_config = ConfigDict(frozen=True)

    filename: str
    symbol: str = Field(min_length=1, max_length=12)
    pattern_start_date: date
    pattern_end_date: date

    @field_validator("pattern_end_date")
    @classmethod
    def _end_after_start(cls, v: date, info) -> date:
        start = info.data.get("pattern_start_date")
        if start is not None and v < start:
            raise ValueError(
                f"pattern_end_date ({v}) before pattern_start_date ({start})"
            )
        return v


class PatternFileParse(BaseModel):
    """
    Full result of parsing one Pattern XLSX file: filename metadata plus
    all bars from the underlying 6/9-month grid (sorted ascending).
    The pipeline selects the LAUNCH-anchor setup window and forward-label
    bars from this superset; the file itself contains far more than the
    window.

    Minimum 60 bars enforces operator's "20 before + trend + 20 after"
    capture rule. Real files have 130+ bars (6-month) or 190+ (9-month).
    """
    metadata: PatternFileMetadata
    bars: list[VPBarRaw] = Field(min_length=60)

    @field_validator("bars")
    @classmethod
    def _bars_sorted_ascending(cls, v: list[VPBarRaw]) -> list[VPBarRaw]:
        dates = [b.bar_date for b in v]
        if dates != sorted(dates):
            raise ValueError("bars must be sorted ascending by bar_date")
        return v
