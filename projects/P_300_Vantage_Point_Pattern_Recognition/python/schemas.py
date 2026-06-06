"""
FILE: schemas.py
VERSION: 2.2
DATE: 2026-05-20
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for every persistent file read or write in P_300.
    Validates data at the I/O boundary, not after corruption.

    Stage 4 POC scope:
      - INPUT models (VP XLSX parsing): VPBarRaw, PatternFileMetadata,
        PatternFileParse.
      - MANIFEST models (ingest_manifest.json validation): IngestManifest
        with SourceFormat / ColumnMapEntry / IgnoredColumnEntry /
        ValidationRules. Loaded by vp_xlsx_reader.py at startup; structural
        errors in the manifest surface at load time, not at runtime.
      - CATALOG ROW models: SymbolRecord, SourceFileRecord, FeatureSetRecord,
        PatternInstanceRecord, PatternBarRecord, ForwardLabelRecord.

    LAUNCH framing convention:
      - anchor_date = launch date (start of the trend the operator flagged)
      - bar_offset = 0 at the anchor (architecture §1.5)
      - Setup bars span offsets -(window_length-1) through 0
      - Forward labels measure return at +5/+7/+10/+15/+20 trading days
        from the anchor close

    pattern_features table NOT modeled here -- scope trim D2 leaves the
    table empty for the POC.

CHANGELOG:
    - 2026-05-20 v2.2: Added `header_sub_alt: Optional[str] = None` to
      ColumnMapEntry. Supports VP export format drift where a column's
      sub-header text changes between VP versions (e.g. triple_cross
      columns changed from 'Short'/'Medium'/'Long' to 'Triple Cross
      Short'/'Triple Cross Medium'/'Triple Cross Long' in VP
      v10.0.2504.0114). When header_sub_alt is set in the manifest,
      vp_xlsx_reader._verify_header_text accepts either value. Primary
      header_sub should always reflect the current VP version; alt
      provides backward compatibility during transition periods.
    - 2026-05-14 v2.1: Added MANIFEST section with IngestManifest,
      SourceFormat, ColumnMapEntry, IgnoredColumnEntry, ValidationRules.
    - 2026-05-14 v2.0.1: Fix -- high>=low check moved to
      @model_validator(mode="after").
    - 2026-05-14 v2.0: Stage 4 POC release.
    - 2026-05-13 v1.1: Removed PreservationPattern.
    - 2026-05-13 v1.0: Initial Stage 3 foundation.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from config import (
    FORWARD_HORIZONS,
    MAX_WINDOW_LENGTH,
    MIN_WINDOW_LENGTH,
    ORIGIN_EVAL_SET,
    ORIGIN_PATTERN_IDENT,
)


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class DataOriginType(str, Enum):
    """Catalog row provenance -- controls similarity-search inclusion."""
    PATTERN_IDENT = ORIGIN_PATTERN_IDENT   # permanent training row
    EVAL_SET = ORIGIN_EVAL_SET             # transient Pipeline B candidate


# ---------------------------------------------------------------------------
# MANIFEST -- validates ingest_manifest.json structure at load time
# ---------------------------------------------------------------------------

class SourceFormat(BaseModel):
    """Describes the vendor file shape that the manifest applies to."""
    model_config = ConfigDict(frozen=True)

    vendor: str = Field(min_length=1)
    export_type: str = Field(min_length=1)
    header_rows: int = Field(gt=0)
    data_start_row_index: int = Field(ge=0)
    date_order: Literal["ascending", "descending"]
    expected_column_count: int = Field(gt=0)
    minimum_bars_required: int = Field(gt=0)


class ColumnMapEntry(BaseModel):
    """One column-index -> pattern_bars field mapping.

    header_sub_alt: optional alternate sub-header text accepted during
    VP version transitions. When set, _verify_header_text accepts either
    header_sub OR header_sub_alt. Primary header_sub should reflect the
    current VP version; alt covers legacy exports still in the queue.
    """
    model_config = ConfigDict(frozen=True)

    field: str = Field(min_length=1)
    type: Literal["date", "float"]
    header_top: Optional[str] = None      # null on merged-cell continuation
    header_sub: Optional[str] = None      # primary (current VP version)
    header_sub_alt: Optional[str] = None  # alternate (prior VP version)


class IgnoredColumnEntry(BaseModel):
    """One column that exists in the source but is intentionally not mapped."""
    model_config = ConfigDict(frozen=True)

    header_top: Optional[str] = None
    header_sub: Optional[str] = None
    reason: str = Field(min_length=1)


class ValidationRules(BaseModel):
    """Toggles for parse-time validation behavior in vp_xlsx_reader.py."""
    model_config = ConfigDict(frozen=True)

    verify_header_text: bool
    strict_column_count: bool
    raise_on_unmapped_column: bool
    raise_on_missing_mapped_column: bool
    raise_on_header_mismatch: bool


class IngestManifest(BaseModel):
    """
    Validates ingest_manifest.json at load time. Cross-field model_validator
    enforces column-index coverage: every index in [0, expected_column_count)
    must be either mapped or ignored, with no overlap and no out-of-range.

    `extra="allow"` permits the `_comment` field (and any future metadata
    fields) without rejecting the load.
    """
    model_config = ConfigDict(extra="allow", frozen=True)

    manifest_version: str = Field(min_length=1)
    manifest_date: date
    pairs_with_schema_version: str
    pairs_with_architecture: str
    source_format: SourceFormat
    column_mapping: dict[int, ColumnMapEntry]
    ignored_columns: dict[int, IgnoredColumnEntry]
    validation_rules: ValidationRules

    @model_validator(mode="after")
    def _validate_column_indices(self) -> "IngestManifest":
        expected = self.source_format.expected_column_count
        mapped = set(self.column_mapping.keys())
        ignored = set(self.ignored_columns.keys())

        overlap = mapped & ignored
        if overlap:
            raise ValueError(
                f"Columns appear in both column_mapping and ignored_columns: "
                f"{sorted(overlap)}"
            )

        all_indices = mapped | ignored
        out_of_range = {i for i in all_indices if i < 0 or i >= expected}
        if out_of_range:
            raise ValueError(
                f"Column indices outside [0, {expected}): {sorted(out_of_range)}"
            )

        missing = set(range(expected)) - all_indices
        if missing:
            raise ValueError(
                f"Column indices neither mapped nor ignored: {sorted(missing)}"
            )

        return self


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
