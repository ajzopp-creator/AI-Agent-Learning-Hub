"""
FILE: schemas_bulk.py
VERSION: 1.2
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for WO-P300-E2.001 Bulk Pattern Extraction
    (Pipeline A-Bulk). Covers every persistent read/write against
    models/research/bulk_research.db and its supporting files, plus
    the raw parse shape for <years>[I]_Pattern_<SYMBOL>.xlsx exports.

    research_catalog.db uses the same 7-table shorthand as the live
    catalog (schemas.py) PLUS: symbols.sector, pattern_instances.
    detection_tier, forward_labels.significant_move_15, and
    data_origin_type = 'BULK_SCAN'. Models here are deliberately
    separate from schemas.py's catalog-row models rather than
    subclassed -- detection_tier and sector have no equivalent in
    the live schema, and keeping the two catalogs' row models
    independent means a live-schema change can never silently
    ripple into the bulk pipeline (Process Boundary: one reason to
    change per module).

    return_pct stays DECIMAL FRACTION per M-020; BULK_SIGNIFICANT_
    MOVE_PCT in config.py is in PERCENT space, so the comparison
    that derives significant_move_15 converts at that boundary only
    -- never store a percent value in return_pct.

    BulkBarRaw is NOT VPBarRaw. Verified against real VP bulk exports
    (10/5/3/1-year, 6-month, SPY/BP, VP-direct and IntelliScan-routed):
      - neural_index is TEXT ('up'/'down'), not a numeric score. The
        only numeric neural field is NeuralXMax (neural_x_max).
      - Triple Cross Short/Medium/Long are PRICE LEVELS (same
        magnitude as close), not the live schema's small signed
        diffs -- crossover is a sign-flip of (tc_short - tc_medium),
        not a single-field sign flip.
      - Column count (22), order, and 2-row header structure are
        identical across every window length and export path tested.
        The one confirmed drift is Triple Cross sub-header wording
        ("Short" vs "Triple Cross Short"), symbol/window-independent
        -- handled via header_sub_alt in bulk_ingest_manifest.json,
        same mechanism as the live manifest's v1.2 fix.

CHANGELOG:
    - 2026-07-10 v1.2: Removed SectorMapRow (file #2 of WO-P300-E2.002's
      11-file build). Confirmed via Select-String across the full active
      python/ tree -- zero imports anywhere outside this file's own
      definition. Moved to schemas_sector_analysis.py (file #3, next),
      extended there with asset_class + source_note per WO-P300-E2.002
      Decision 5 (ETF rows carry sector=N/A, never a fabricated sector).
      No behavior change -- this WO's sector work was never wired to
      anything before today.
    - 2026-07-08 v1.1: Added BulkBarRaw, BulkPatternFileMetadata,
      BulkPatternFileParse for the real 22-column bulk export shape
      (corrects the earlier assumption that VPBarRaw could be reused).
      BulkSourceFileRecord gained window_years and is_intelliscan_export
      (both provenance-only, never gate ingestion -- no minimum window
      length exists by design; a real detection is not less valid
      because the source file is shorter).
    - 2026-07-08 v1.0: Initial release. Models:
      BulkSourceFileRecord, BulkPatternInstanceRecord, BulkForwardLabelRecord,
      BulkCheckpoint. Pipeline B never reads this DB under this WO --
      no similarity/normalization models included (out of scope).
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from config import (
    BULK_TIER_RELAXED,
    BULK_TIER_STRICT,
    FORWARD_HORIZONS,
    ORIGIN_BULK_SCAN,
)


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class DetectionTier(str, Enum):
    """Which variant of Potential Crossover v12 fired for this instance."""
    STRICT = BULK_TIER_STRICT
    RELAXED = BULK_TIER_RELAXED


class BulkDataOriginType(str, Enum):
    """
    Single-member enum (not a shared Literal with schemas.py's
    DataOriginType) -- BULK_SCAN rows are structurally research-only
    and must never be constructible as PATTERN_IDENT/EVAL_SET or vice
    versa. Keeps the two catalogs type-isolated, not just DB-isolated.
    """
    BULK_SCAN = ORIGIN_BULK_SCAN


# ---------------------------------------------------------------------------
# INPUT -- bulk XLSX parsing (<years>[I]_Pattern_<SYMBOL>.xlsx)
# ---------------------------------------------------------------------------

class BulkBarRaw(BaseModel):
    """
    One bar as parsed from a bulk History Grid export. Field order
    matches the verified 22-column layout (col A-V). Distinct from
    schemas.py's VPBarRaw -- see module docstring for the two
    confirmed field-shape differences (neural_index, triple cross).
    """
    model_config = ConfigDict(frozen=True)

    bar_date: date
    # VP term differences (can be negative; zero pre-2021-07-14 backfill)
    stdiff: float
    mtdiff: float
    ltdiff: float
    # OHLC -- prices must be strictly positive
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    # Predicted price levels (zero pre-backfill)
    pred_high: float = Field(ge=0)
    pred_low: float = Field(ge=0)
    volume: float = Field(ge=0)
    # VP indicators -- populated even pre-backfill
    williams_emai: float
    psi: float
    roc_pct: float
    # Neural Index: TEXT direction, not a numeric score (verified).
    # 'unknown' accepted for any export-time gap; never a hard fail on
    # this field alone since it is populated throughout, backfill or not.
    neural_index: Literal["up", "down", "unknown"]
    neural_x_max: float
    # Triple Cross -- PRICE LEVELS, not diffs (verified). Zero
    # pre-backfill. Crossover direction is a derived comparison
    # (tc_short vs tc_medium), not stored as a field here.
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


class BulkPatternFileMetadata(BaseModel):
    """
    Metadata extracted from a <years>[I]_Pattern_<SYMBOL>.xlsx filename.
    window_years and is_intelliscan_export are provenance only -- never
    used to gate ingestion. Operator renames VP's default export
    ("History Grid (SYMBOL).xlsx") by hand at export time; no fixed
    window length is assumed or required.
    """
    model_config = ConfigDict(frozen=True)

    filename: str
    symbol: str = Field(min_length=1, max_length=12)
    window_years: int = Field(gt=0, le=99)
    is_intelliscan_export: bool


class BulkPatternFileParse(BaseModel):
    """
    Full result of parsing one bulk XLSX file: filename metadata plus
    all bars (sorted ascending). Minimum bar count is a small
    structural floor -- enough for one detection attempt
    (BULK_TREND_CHECK_BARS + 2) -- not a calendar-year minimum. A
    6-month export (~123 bars) is fully valid input.
    """
    metadata: BulkPatternFileMetadata
    bars: list[BulkBarRaw] = Field(min_length=5)

    @field_validator("bars")
    @classmethod
    def _bars_sorted_ascending(cls, v: list[BulkBarRaw]) -> list[BulkBarRaw]:
        dates = [b.bar_date for b in v]
        if dates != sorted(dates):
            raise ValueError("bars must be sorted ascending by bar_date")
        return v


# ---------------------------------------------------------------------------
# CATALOG ROWS -- Optional[PK] supports pre-insert and post-insert use
# ---------------------------------------------------------------------------

class BulkSourceFileRecord(BaseModel):
    """
    source_files table row (research catalog) -- provenance for one
    bulk export. Dedup key is filename, same convention as the live
    catalog's source_files table.

    window_years and is_intelliscan_export are recorded for audit
    trail only (e.g. "this detection came from a 1-year export, less
    trend history behind it than a 10-year one") -- never a filter.
    No minimum window length exists anywhere in this pipeline.
    """
    source_file_id: Optional[int] = None
    filename: str
    symbol_id: int
    imported_at: datetime
    row_count: int = Field(gt=0)
    window_years: int = Field(gt=0, le=99)
    is_intelliscan_export: bool


class BulkPatternInstanceRecord(BaseModel):
    """
    pattern_instances table row (research catalog).

    Adds detection_tier and forces data_origin_type = BULK_SCAN.
    window_length is fixed at BULK_WINDOW_LENGTH (config.py) rather
    than variable 5-20 like the live catalog -- bulk detection always
    captures the full window for bar-level comparability across the
    research pool.
    """
    pattern_instance_id: Optional[int] = None
    symbol_id: int
    source_file_id: int
    feature_set_id: int
    anchor_date: date
    window_length: int = Field(gt=0)
    data_origin_type: BulkDataOriginType = BulkDataOriginType.BULK_SCAN
    detection_tier: DetectionTier


class BulkForwardLabelRecord(BaseModel):
    """
    forward_labels table row (research catalog) -- adds
    significant_move_15 alongside the standard return fields.

    return_pct is decimal-fraction storage (M-020). significant_move_15
    is derived at write time by comparing abs(return_pct) * 100 against
    BULK_SIGNIFICANT_MOVE_PCT (percent space) -- the conversion happens
    once, at this boundary, and is never re-derived downstream.
    """
    forward_label_id: Optional[int] = None
    pattern_instance_id: int
    horizon_days: int
    future_date: date
    return_pct: float
    is_profitable: bool
    significant_move_15: bool

    @field_validator("horizon_days")
    @classmethod
    def _horizon_in_allowed_set(cls, v: int) -> int:
        if v not in FORWARD_HORIZONS:
            raise ValueError(
                f"horizon_days {v} not in allowed set {FORWARD_HORIZONS}"
            )
        return v


# ---------------------------------------------------------------------------
# CHECKPOINT -- resume state for a bulk extraction run
# ---------------------------------------------------------------------------

class BulkCheckpoint(BaseModel):
    """
    bulk_extract_checkpoint.json contents. Written after each file
    completes so a crash at file N resumes at N+1, not from zero.

    completed_filenames is the authoritative resume set (checked
    against, not last_completed_index alone) so an out-of-order
    retry queue still dedupes correctly.
    """
    run_started_at: datetime
    last_updated_at: datetime
    completed_filenames: list[str] = Field(default_factory=list)
    total_files_queued: int = Field(ge=0)
    strict_detections_total: int = Field(ge=0, default=0)
    relaxed_detections_total: int = Field(ge=0, default=0)
    last_error: Optional[str] = None
