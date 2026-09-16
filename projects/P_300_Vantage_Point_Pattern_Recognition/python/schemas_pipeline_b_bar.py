"""
FILE: schemas_pipeline_b_bar.py
VERSION: 1.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Split out of schemas_pipeline_b.py (WO-P300-E5.001, debt note item 2 --
    the split this file executes was designed and backlogged at v1.2,
    2026-05-20). Bar/candidate/match half of Pipeline B's in-memory
    contracts: NormalizedBar, LiveCandidate, ForwardLabelLite, MatchResult.

    PatternMetadata joins this file too (moved from infrastructure/
    catalog_reader.py, same WO) -- it's the same in-memory, no-persistence
    category as the four models above, just built by the infrastructure
    read layer instead of by normalization. Domain modules that need it
    (eval_incremental, eval_scoring, reconstruct_from_topk, topk_cache)
    were importing it from infrastructure.catalog_reader directly, which
    is the domain-importing-infrastructure violation this WO exists to
    stop; importing it from here instead removes the violation without
    changing PatternMetadata's shape, fields, or behavior at all.

    schemas_pipeline_b.py re-exports every name in this file for backward
    compatibility -- existing `from schemas_pipeline_b import X` call sites
    were not touched.

    See schemas_pipeline_b_report.py for the sibling half (Aggregated
    SignalPerHorizon, Severity, VolatilityDivergence, SignalClass,
    SignalReport) and schemas_pipeline_b.py's own docstring for the
    full original file history (CHANGELOG entries predate this split
    and are not duplicated here).

DEBT NOTE (carried over, still open):
    NormalizedBar duplicates PatternBarRecord's (schemas_catalog_records.py)
    raw + normalized field set (16 + 10 = 26 columns, similar Field
    constraints). Proper fix is a shared base class -- not done here,
    this split is the file-size fix only (debt item 2); the shared-base
    refactor (debt item 1) stays in Backlog, unchanged by this WO.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from config import (
    FORWARD_HORIZONS,
    MAX_WINDOW_LENGTH,
    MIN_WINDOW_LENGTH,
)


# ─────────────────────────────────────────────────────────────────────────────
# IN-MEMORY BAR — raw VP + normalized columns, no catalog identity
# ─────────────────────────────────────────────────────────────────────────────

class NormalizedBar(BaseModel):
    """
    One bar carrying raw VP data + normalized columns (architecture §9.3),
    in memory only. Mirrors pattern_bars column shape minus DB identity
    fields (pattern_bar_id, pattern_instance_id).

    Shape parity with PatternBarRecord lets the matching engine consume
    catalog bars and candidate bars through the same interface — similarity
    functions don't care which side the bars came from.
    """
    model_config = ConfigDict(frozen=True)

    bar_offset: int = Field(le=0, ge=-(MAX_WINDOW_LENGTH - 1))
    bar_date: date

    # Raw VP data (audit + reporting; not used directly in similarity)
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

    # Normalized columns (architecture §9.3) — what similarity actually consumes
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

    @model_validator(mode="after")
    def _high_ge_low(self) -> "NormalizedBar":
        if self.high < self.low:
            raise ValueError(f"high ({self.high}) < low ({self.low})")
        return self


# ─────────────────────────────────────────────────────────────────────────────
# LIVE CANDIDATE — Pipeline B's input unit
# ─────────────────────────────────────────────────────────────────────────────

class LiveCandidate(BaseModel):
    """
    Parsed live `History Grid (<symbol>).xlsx`, normalized, ready for
    matching against the catalog's PATTERN_IDENT historical patterns.

    anchor_date = the most recent bar's date (the "today" of the candidate);
    sits at bar_offset = 0. The remaining bars run -(window_length-1) → -1,
    so the full offset range is contiguous and ends at the anchor.

    Not inserted into the catalog (Stage 6 decision E: transient in-memory only).
    """
    model_config = ConfigDict(frozen=True)

    ticker: str = Field(min_length=1, max_length=12)
    anchor_date: date
    window_length: int = Field(ge=MIN_WINDOW_LENGTH, le=MAX_WINDOW_LENGTH)
    bars: list[NormalizedBar]

    @model_validator(mode="after")
    def _bars_match_window(self) -> "LiveCandidate":
        if len(self.bars) != self.window_length:
            raise ValueError(
                f"len(bars)={len(self.bars)} != window_length={self.window_length}"
            )
        offsets = [b.bar_offset for b in self.bars]
        expected = set(range(-(self.window_length - 1), 1))
        if set(offsets) != expected:
            raise ValueError(
                f"bar_offsets must be contiguous {sorted(expected)}; got {sorted(offsets)}"
            )
        # Anchor bar's date must match anchor_date
        anchor_bar = next(b for b in self.bars if b.bar_offset == 0)
        if anchor_bar.bar_date != self.anchor_date:
            raise ValueError(
                f"anchor_bar.bar_date ({anchor_bar.bar_date}) != anchor_date ({self.anchor_date})"
            )
        return self


# ─────────────────────────────────────────────────────────────────────────────
# FORWARD LABEL (LITE) — in-memory shape, no DB identity
# ─────────────────────────────────────────────────────────────────────────────

class ForwardLabelLite(BaseModel):
    """
    Minimal forward-label shape for in-memory matching. Distinct from
    schemas_catalog_records.py:ForwardLabelRecord (which carries DB
    identity fields). Used inside MatchResult.forward_labels dict, keyed
    by horizon_days.
    """
    model_config = ConfigDict(frozen=True)

    return_pct: float
    is_profitable: bool


# ─────────────────────────────────────────────────────────────────────────────
# MATCH RESULT — one historical analog
# ─────────────────────────────────────────────────────────────────────────────

class MatchResult(BaseModel):
    """
    One historical analog for a live candidate, produced by
    domain/similarity.py + infrastructure/catalog_reader.py.

    composite_distance = equal-weight sum of per_feature_distances across
    the 10 SIMILARITY_FEATURES (Stage 6 decision B).

    forward_labels carries every horizon that exists in forward_labels
    table for this pattern — typically all 5 (5/7/10/15/20), but a
    pattern near the edge of capturable history may have fewer.
    """
    model_config = ConfigDict(frozen=True)

    pattern_instance_id: int
    ticker: str = Field(min_length=1, max_length=12)
    anchor_date: date
    composite_distance: float = Field(ge=0)
    per_feature_distances: dict[str, float]
    forward_labels: dict[int, ForwardLabelLite]

    @field_validator("forward_labels")
    @classmethod
    def _horizons_valid(
        cls, v: dict[int, ForwardLabelLite]
    ) -> dict[int, ForwardLabelLite]:
        for h in v.keys():
            if h not in FORWARD_HORIZONS:
                raise ValueError(
                    f"horizon {h} not in allowed set {FORWARD_HORIZONS}"
                )
        return v

    @field_validator("per_feature_distances")
    @classmethod
    def _distances_non_negative(cls, v: dict[str, float]) -> dict[str, float]:
        negative = {f: d for f, d in v.items() if d < 0}
        if negative:
            raise ValueError(
                f"per-feature distances must be >= 0; negative entries: {negative}"
            )
        return v


# ─────────────────────────────────────────────────────────────────────────────
# PATTERN METADATA — infrastructure-built, domain-consumed identity fields
# ─────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PatternMetadata:
    """Identity + provenance fields joined from symbols + pattern_instances.

    In-memory only — doesn't cross the persistence boundary, same category
    as NormalizedBar/LiveCandidate/MatchResult above (not a DB row model;
    see schemas_catalog_records.py for those). Built by infrastructure/
    catalog_reader.py's query functions; domain layers consume it to
    populate MatchResult.ticker and MatchResult.anchor_date when building
    match results.

    Moved here from infrastructure/catalog_reader.py (WO-P300-E5.001) --
    domain modules were importing it directly from infrastructure, which
    the import-linter contract this WO adds forbids. No field, no
    behavior, no validation changed by the move.
    """
    pattern_instance_id: int
    ticker: str
    anchor_date: date
    window_length: int
