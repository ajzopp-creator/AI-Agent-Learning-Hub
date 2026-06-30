"""
FILE: schemas_pipeline_b.py
VERSION: 1.3
DATE: 2026-06-09
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for Pipeline B (Daily Evaluate) — in-memory only.
    Sibling to schemas.py; kept separate to honor §8.4.2 300-line file
    limit (schemas.py was already at ~290 lines after Stage 4).

    Pipeline B does NOT write live candidates to the catalog (Stage 6
    decision E: transient in-memory only), so none of these models map
    to a SQLite table. They define the data contracts flowing between:

        vp_xlsx_reader  →  normalization  →  similarity  →  aggregator
                                                              ↓
                                          signal classifier → report
                                                                ↓
                                                      narrator (Stage 8)

    Models:
      - NormalizedBar               — one bar with raw + normalized columns
      - LiveCandidate               — parsed live XLSX window, ready for matching
      - ForwardLabelLite            — minimal forward-label shape (no DB IDs)
      - MatchResult                 — one historical analog with distances + labels
      - AggregatedSignalPerHorizon  — per-horizon stats across top-K matches
      - Severity                    — NONE / MILD / STRONG volatility flag
      - VolatilityDivergence        — cap/volatility regime check on top-K
      - SignalClass                 — BUY / WATCH / PASS enum
      - SignalReport                — final classified output (+ optional narration + optional volatility_divergence)

    Imports DataOriginType from schemas.py if/when catalog filtering needs
    the type discriminator — not used in this file directly.

CHANGELOG:
    - 2026-06-09 v1.3: Added optional `certainty_equivalent: float | None = None`
      field to AggregatedSignalPerHorizon for the Certainty-Equivalent BUY gate
      (config v1.7; Kochenderfer "Algorithms for Decision Making" Ch. 6). The
      CE is the risk-adjusted forward return of this horizon's top-K analog
      cluster, computed in domain/utility.py and attached by domain/aggregator.py.
      Default None preserves backward compatibility and keeps the determinism
      regression byte-identical while CE_GATE_ENABLED=False -- existing callers
      that construct AggregatedSignalPerHorizon without CE continue unchanged.
      Decimal-space throughout (M-020): CE is a decimal fraction like
      mean_return_pct, x100 only at the report-writer display boundary. The
      risk-aversion lambda under which the CE was computed is NOT stored per
      horizon (one lambda per run); it is stamped on the report header and the
      ledger record instead (config v1.7 provenance rule). File remains over the
      Section 8.4.2 limit (M-031); one-field add only, split stays backlogged.
    - 2026-05-20 v1.2: Added Severity enum, VolatilityDivergence model, and
      optional `volatility_divergence` field on SignalReport, plus a
      model_validator enforcing n_topk_matches == len(top_matches) when the
      field is set. Implements the post-filter divergence flag from the
      2026-05-20 cap-sensitivity audit (utilities/cap_sensitivity_audit.py
      v1.0): range_pct is the cleanest cap/volatility-class axis among the
      10 normalized similarity features (OII ~0.046 vs SPY ~0.009, ~5x
      ratio); volume_zscore and close_pct_from_anchor have larger raw
      dispersion but encode volume regime and trend bias, not cap. Severity
      thresholds (NONE < 1.5, MILD [1.5, 2.0), STRONG >= 2.0) are domain
      logic and live in domain/volatility_divergence.py (turn 2 of the
      4-file change), same pattern as BUY/WATCH/PASS thresholds in
      domain/signal_classifier.py.
    - 2026-05-19 v1.1: Added optional `narration: str | None = None` field
      to SignalReport for the Stage 8 Post-Decision Narrator path. Default
      None preserves backward compatibility — all existing Pipeline B
      callers that construct SignalReport without narration continue to
      work unchanged. The narrator runs AFTER classify_signal() emits the
      structured report; failure to reach LM Studio leaves narration=None
      and report_writer renders `NARRATIVE: unavailable` (NFR-1 hard rule:
      LLM is never in the BUY/WATCH/PASS decision path). Also rode along
      the DEBT NOTE stage reference forward (Stage 8 → Stage 9) per the
      2026-05-18 stage renumber.
    - 2026-05-16 v1.0: Initial Stage 6 release. Stage 6 planning decisions
      locked in config.py v1.2 (B: DTW per-feature equal-weight across 10
      normalized columns; C: TOP_K_MATCHES=20; F: BUY/WATCH/PASS AND-gate
      thresholds). This file defines the data contracts; the actual math
      lives in domain/similarity.py, domain/aggregator.py, domain/signal.py.

DEBT NOTE:
    (1) NormalizedBar duplicates PatternBarRecord's raw + normalized field
    set (16 + 10 = 26 columns, with similar Field constraints). The clean
    refactor is a shared base class (PatternBarRecord adds DB identity,
    NormalizedBar doesn't). Reclassified Stage 9 -> Backlog at v2.6 SEAL.

    (2) File size has exceeded the §8.4.2 300-line limit: 329 lines at v1.1,
    ~380 lines at v1.2 after VolatilityDivergence + Severity additions.
    The proper fix is a file split — e.g., schemas_pipeline_b_bar.py
    (NormalizedBar, LiveCandidate, ForwardLabelLite, MatchResult) and
    schemas_pipeline_b_report.py (AggregatedSignalPerHorizon, Severity,
    VolatilityDivergence, SignalClass, SignalReport). Should pair with
    debt (1) since both touch NormalizedBar's neighborhood. Backlog.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum

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
    schemas.py:ForwardLabelRecord (which carries DB identity fields).
    Used inside MatchResult.forward_labels dict, keyed by horizon_days.
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

    See v1.2 CHANGELOG for the audit context that led to range_pct as
    the chosen divergence axis (vs volume_zscore or close_pct_from_anchor).
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
