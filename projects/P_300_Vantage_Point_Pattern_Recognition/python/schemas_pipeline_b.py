"""
FILE: schemas_pipeline_b.py
VERSION: 2.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Backward-compatible re-export shim (WO-P300-E5.001). The real Pipeline
    B model definitions moved to schemas_pipeline_b_bar.py (NormalizedBar,
    LiveCandidate, ForwardLabelLite, MatchResult, PatternMetadata) and
    schemas_pipeline_b_report.py (AggregatedSignalPerHorizon, Severity,
    VolatilityDivergence, SignalClass, SignalReport) -- this file's own
    DEBT NOTE (debt item 2, backlogged since v1.2 2026-05-20) named this
    exact split; executed here, not redesigned.

    Every existing `from schemas_pipeline_b import X` call site (20 files
    as of this split) keeps working unchanged -- nothing outside this
    file and the two new files was touched to make this split happen.
    New code should import directly from schemas_pipeline_b_bar /
    schemas_pipeline_b_report; this shim exists for the existing callers,
    not as the preferred import path going forward.

    Full field-level history (v1.0-v1.3, 2026-05-16 through 2026-06-09)
    lives in the two split files' own docstrings, copied verbatim from
    this file's prior CHANGELOG at split time -- not repeated here.

CHANGELOG:
    - 2026-09-10 v2.0: Split into schemas_pipeline_b_bar.py +
      schemas_pipeline_b_report.py (WO-P300-E5.001, executing this file's
      own v1.2 DEBT NOTE item 2). This file reduced from 433 lines to a
      re-export shim. PatternMetadata also moved in from infrastructure/
      catalog_reader.py in the same pass (same WO, the actual import-
      linter violation being fixed) and is re-exported here too, though
      it was never part of this file's own model set before now.
"""
from __future__ import annotations

from schemas_pipeline_b_bar import (
    ForwardLabelLite,
    LiveCandidate,
    MatchResult,
    NormalizedBar,
    PatternMetadata,
)
from schemas_pipeline_b_report import (
    AggregatedSignalPerHorizon,
    Severity,
    SignalClass,
    SignalReport,
    VolatilityDivergence,
)

__all__ = [
    "NormalizedBar",
    "LiveCandidate",
    "ForwardLabelLite",
    "MatchResult",
    "PatternMetadata",
    "AggregatedSignalPerHorizon",
    "Severity",
    "VolatilityDivergence",
    "SignalClass",
    "SignalReport",
]
