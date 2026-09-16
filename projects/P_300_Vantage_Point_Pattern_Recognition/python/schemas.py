"""
FILE: schemas.py
VERSION: 3.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for the ingest-manifest / VP-input-config half of
    P_300's schemas (WO-P300-E5.001 file-size split). DataOriginType +
    the MANIFEST family (SourceFormat, ColumnMapEntry, IgnoredColumnEntry,
    ValidationRules, IngestManifest) stay here -- this is the file's own
    core, ~290 lines at Stage 4 before later additions pushed it to 422.

    Two other families that were previously in this file moved out at
    this split and are re-exported below for backward compatibility:
      - INPUT models (VP XLSX parsing) -> schemas_vp_raw.py: VPBarRaw,
        PatternFileMetadata, PatternFileParse.
      - CATALOG ROW models -> schemas_catalog_records.py: SymbolRecord,
        SourceFileRecord, FeatureSetRecord, PatternInstanceRecord,
        PatternBarRecord, ForwardLabelRecord, PowerGaugeResult.

    schemas_catalog_records.py imports DataOriginType back from this file
    (PatternInstanceRecord.data_origin_type needs it). Catalog-row names
    are re-exported lazily via __getattr__ so that importing
    schemas_catalog_records first (it needs DataOriginType from here)
    does not re-enter that module while it is still initializing.
    DataOriginType stays defined in this file; do not move the class
    below the re-export helpers.

    LAUNCH framing convention:
      - anchor_date = launch date (start of the trend the operator flagged)
      - bar_offset = 0 at the anchor (architecture §1.5)
      - Setup bars span offsets -(window_length-1) through 0
      - Forward labels measure return at +5/+7/+10/+15/+20 trading days
        from the anchor close

    pattern_features table NOT modeled here -- scope trim D2 leaves the
    table empty for the POC.

CHANGELOG:
    - 2026-09-10 v3.0: Split (WO-P300-E5.001). INPUT models moved to
      schemas_vp_raw.py, CATALOG ROW models moved to schemas_catalog_
      records.py, both re-exported below. Catalog-row re-exports are
      lazy (__getattr__) so importing schemas_catalog_records first
      does not circular-import FeatureSetRecord from a partially
      initialized module. This file reduced from 422 lines to the
      manifest/DataOriginType core. No field, validator, or behavior
      changed on any moved model.
    - 2026-07-10 v2.4: Added BULK_SCAN to DataOriginType (WO-P300-E2.003
      file #1 of 7 -- physical merge of research_catalog.db STRICT-tier
      patterns into the live catalog). Purely additive -- no existing
      member changed, no existing row's data_origin_type value affected.
    - 2026-07-08 v2.3: Widened ColumnMapEntry.type from Literal["date",
      "float"] to Literal["date", "float", "text"] (WO-P300-E2.001).
      Purely additive -- every existing manifest entry uses "date" or
      "float" only, so ingest_manifest.json validates identically.
      Enables bulk_ingest_manifest.json to declare the bulk export's
      Neural Index column (text 'up'/'down', not the numeric NeuralXMax
      value the live manifest maps under the same field name) without a
      parallel, fully-duplicated manifest schema in schemas_bulk.py.
      vp_xlsx_reader.py's _coerce_cell has no "text" branch and does not
      need one today -- no live manifest entry uses it; the bulk reader
      (infrastructure/bulk_grid_reader.py) adds its own text handling.
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

import importlib
from datetime import date
from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from config import (
    ORIGIN_BULK_SCAN,
    ORIGIN_EVAL_SET,
    ORIGIN_PATTERN_IDENT,
)


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class DataOriginType(str, Enum):
    """Catalog row provenance -- controls similarity-search inclusion.
    BULK_SCAN added 2026-07-10 (WO-P300-E2.003 file #1 of 7) -- merged
    research-catalog patterns keep their real provenance (mechanically
    detected) rather than being relabeled PATTERN_IDENT, which would
    have erased the audit trail the two-catalog type isolation
    (schemas_bulk.py's BulkDataOriginType) was built to protect.
    catalog_reader.py and eval_io.py both updated (files #2-3) to
    include BULK_SCAN in their similarity-search / eval-load filters --
    without those changes this new member alone would make merged rows
    silently invisible everywhere that still hard-filters PATTERN_IDENT."""
    PATTERN_IDENT = ORIGIN_PATTERN_IDENT   # permanent training row
    EVAL_SET = ORIGIN_EVAL_SET             # transient Pipeline B candidate
    BULK_SCAN = ORIGIN_BULK_SCAN           # merged from research_catalog.db (WO-P300-E2.003)


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

    type "text": added v2.3 for bulk manifest support (WO-P300-E2.001).
    No live ingest_manifest.json entry uses it today; vp_xlsx_reader.py's
    _coerce_cell has no "text" branch and doesn't need one unless/until
    a live manifest entry actually declares type="text".
    """
    model_config = ConfigDict(frozen=True)

    field: str = Field(min_length=1)
    type: Literal["date", "float", "text"]
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
# RE-EXPORTS -- moved to schemas_vp_raw.py / schemas_catalog_records.py
# (WO-P300-E5.001 split). Kept here so every existing `from schemas import X`
# call site continues to work unchanged. VP-raw names are imported
# eagerly (no cycle). Catalog-row names are resolved by __getattr__
# below so schemas_catalog_records can import DataOriginType from here
# without re-entering a partially-initialized catalog_records module.
# ---------------------------------------------------------------------------

from schemas_vp_raw import (  # noqa: E402
    PatternFileMetadata,
    PatternFileParse,
    VPBarRaw,
)

_CATALOG_RECORD_NAMES = frozenset({
    "FeatureSetRecord",
    "ForwardLabelRecord",
    "PatternBarRecord",
    "PatternInstanceRecord",
    "PowerGaugeResult",
    "SourceFileRecord",
    "SymbolRecord",
})


def __getattr__(name: str):
    """Load catalog-row re-exports on first access.

    Breaks the schemas <-> schemas_catalog_records cycle that fires
    when catalog_records is imported before this shim.
    """
    if name in _CATALOG_RECORD_NAMES:
        mod = importlib.import_module("schemas_catalog_records")
        value = getattr(mod, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "DataOriginType",
    "SourceFormat",
    "ColumnMapEntry",
    "IgnoredColumnEntry",
    "ValidationRules",
    "IngestManifest",
    "VPBarRaw",
    "PatternFileMetadata",
    "PatternFileParse",
    "SymbolRecord",
    "SourceFileRecord",
    "FeatureSetRecord",
    "PatternInstanceRecord",
    "PatternBarRecord",
    "ForwardLabelRecord",
    "PowerGaugeResult",
]
