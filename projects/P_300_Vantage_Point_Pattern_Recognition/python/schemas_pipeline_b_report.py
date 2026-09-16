"""
FILE: schemas_pipeline_b_report.py
VERSION: 1.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Split out of schemas_pipeline_b.py (WO-P300-E5.001, debt note item 2 --
    the split this file executes was designed and backlogged at v1.2,
    2026-05-20). Report/classification half of Pipeline B's in-memory
    contracts: AggregatedSignalPerHorizon, Severity, VolatilityDivergence,
    SignalClass, SignalReport.

    See schemas_pipeline_b_bar.py for the sibling half (NormalizedBar,
    LiveCandidate, ForwardLabelLite, MatchResult, PatternMetadata) and
    schemas_pipeline_b.py's own docstring for the full original file
    history (CHANGELOG entries predate this split and are not duplicated
    here -- see that file for the v1.0-v1.3 history of every field below).

    schemas_pipeline_b.py re-exports every name in this file for backward
    compatibility -- existing `from schemas_pipeline_b import X` call sites
    were not touched.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from config import FORWARD_HORIZONS
from schemas_pipeline_b_bar import MatchResult


# ─────────────────────────────────────────────────────────────────────────────
# AGGREGATED SIGNAL — per-horizon stats across top-K matches
# ─────────────────────────────────────────────────────────────────────────────

class AggregatedSignalPerHorizon(BaseModel):
    """
    Stats for one candidate at one horizon, across the top-K matches.
    Produced by domain/aggregator.py; consumed by domain/signal.py for
    BUY/WATCH/PASS classification per Stage 6 decision F.

    z_score = standardized excess win-rate of this candidate's top-K
    matches at this horizon vs. the catalog's baseline win-rate at the
    same horizon. Z > 0 = matches win more often than typical catalog
    analogs; Z > 1.0 = significantly above baseline.

    certainty_equivalent (v1.3): risk-adjusted forward return of the top-K
    analog cluster at this horizon, computed via CARA exponential utility
    in domain/utility.py (Kochenderfer Ch. 6). Decimal fraction, same space
    as mean_return_pct (M-020). For any non-degenerate spread of analog
    returns, CE < mean_return_pct; the gap is the risk penalty. None when
    not computed (callers built before v1.3, or a degenerate cluster the
    utility module guards out). The risk-aversion lambda is NOT stored here
    (one lambda per run -- it lives on the report header and ledger record
    per the config v1.7 provenance rule).
    """
    model_config = ConfigDict(frozen=True)

    horizon_days: int
    n_matches: int = Field(ge=0)
    win_rate: float = Field(ge=0, le=1)
    mean_return_pct: float
    std_return_pct: float = Field(ge=0)
    z_score: float
    certainty_equivalent: float | None = None

    @field_validator("horizon_days")
    @classmethod
    def _horizon_valid(cls, v: int) -> int:
        if v not in FORWARD_HORIZONS:
            raise ValueError(
                f"horizon {v} not in allowed set {FORWARD_HORIZONS}"
            )
        return v


# ─────────────────────────────────────────────────────────────────────────────
# VOLATILITY DIVERGENCE — post-classification cap/volatility regime check
# ─────────────────────────────────────────────────────────────────────────────

class Severity(str, Enum):
    """Volatility-divergence flag severity (set by domain/volatility_divergence.py)."""
    NONE = "NONE"
    MILD = "MILD"
    STRONG = "STRONG"


class VolatilityDivergence(BaseModel):
    """
    Volatility-regime divergence between a live candidate and its top-K
    historical matches, computed post-classification.

    Symmetric ratio: max(candidate_median, topk_median) / min(...). A
    small-cap candidate matched against mega-cap analogs flags at the
    same magnitude as the reverse. Severity classification is set by
    the compute helper (domain/volatility_divergence.py), not here —
    the schema stores whatever the helper sets, same pattern as
    composite_distance on MatchResult.

    See schemas_pipeline_b.py's v1.2 CHANGELOG for the audit context
    that led to range_pct as the chosen divergence axis (vs volume_zscore
    or close_pct_from_anchor).
    """
    model_config = ConfigDict(frozen=True)

    candidate_median_range_pct: float = Field(ge=0)
    topk_median_range_pct: float = Field(ge=0)
    ratio: float = Field(ge=1.0)
    severity: Severity
    n_topk_matches: int = Field(ge=0)


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL CLASS + REPORT — final classified output
# ─────────────────────────────────────────────────────────────────────────────

class SignalClass(str, Enum):
    """Pipeline B classification output (Stage 6 decision F)."""
    BUY = "BUY"
    WATCH = "WATCH"
    PASS = "PASS"


class SignalReport(BaseModel):
    """
    Final classified output for one live candidate.

    Cross-horizon classification is "strongest horizon wins" — signal_class
    is the highest class achieved at any horizon, and chosen_horizon names
    which one. If multiple horizons tie at the highest class, the shortest
    horizon wins (sooner-actionable signals preferred).

    PASS classification: chosen_horizon may be any horizon; it names the
    horizon with the best stats even though none cleared WATCH/BUY.

    narration (Stage 8): optional human-readable summary produced by the
    Post-Decision Narrator after classify_signal() emits. Decoupled from
    the deterministic decision path — NFR-1 hard rule. None when the
    narrator is disabled (config.NARRATOR_ENABLED=False or cli --no-narrator),
    when LM Studio is unreachable, or when the LLM call fails. Text content
    is allowed to vary between runs (DeepSeek R1 requires temperature >= 0.6,
    so sampling non-determinism is expected and accepted). Stored as plain
    string; ASCII sanitization for stdout happens at the report_writer
    boundary per M-019, not here — the in-memory model carries the raw text.

    volatility_divergence (v1.2): optional cap/volatility regime check
    against top-K matches via range_pct medians. Computed post-classification
    by domain/volatility_divergence.py and attached to the report so the
    renderer and the narrator both see the same metric. None when not
    computed (upstream callers built before v1.2, or future flag that
    disables the check). The validator below enforces n_topk_matches ==
    len(top_matches) when the field is set, catching orchestrator bugs at
    SignalReport construction time rather than at report-write time.
    """
    model_config = ConfigDict(frozen=True)

    ticker: str = Field(min_length=1, max_length=12)
    anchor_date: date
    signal_class: SignalClass
    chosen_horizon: int
    per_horizon_stats: dict[int, AggregatedSignalPerHorizon]
    top_matches: list[MatchResult]
    generated_at: datetime
    narration: str | None = None
    volatility_divergence: VolatilityDivergence | None = None

    @field_validator("chosen_horizon")
    @classmethod
    def _chosen_horizon_valid(cls, v: int) -> int:
        if v not in FORWARD_HORIZONS:
            raise ValueError(
                f"chosen_horizon {v} not in allowed set {FORWARD_HORIZONS}"
            )
        return v

    @model_validator(mode="after")
    def _chosen_horizon_in_stats(self) -> "SignalReport":
        if self.chosen_horizon not in self.per_horizon_stats:
            raise ValueError(
                f"chosen_horizon {self.chosen_horizon} missing from per_horizon_stats"
            )
        return self

    @model_validator(mode="after")
    def _volatility_divergence_consistency(self) -> "SignalReport":
        if self.volatility_divergence is not None:
            actual = len(self.top_matches)
            expected = self.volatility_divergence.n_topk_matches
            if actual != expected:
                raise ValueError(
                    f"volatility_divergence.n_topk_matches ({expected}) "
                    f"!= len(top_matches) ({actual})"
                )
        return self
