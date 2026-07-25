"""
FILE: schemas_eval.py
VERSION: 1.2
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for the Stage 6 walk-forward eval loop. Read-only
    measurement scaffold -- no catalog writes, no SQLite table maps
    to these models (mirrors schemas_pipeline_b.py's Pipeline B
    contract: Stage 6 decision E, transient in-memory only).

    Walk-forward differs from utilities/loo_replay.py's leave-one-out
    design: the corpus for each pattern is restricted to patterns
    with an EARLIER anchor_date only (temporal exclusion), not "every
    other pattern in the catalog" (LOO exclusion). No minimum-corpus-
    size floor is applied -- every PATTERN_IDENT pattern is scored,
    and a pattern with zero eligible prior patterns is flagged via
    degenerate_corpus rather than skipped or specially classified
    (operator decision, 2026-06-28).

    Reuses AggregatedSignalPerHorizon + SignalClass from
    schemas_pipeline_b.py -- no duplicate stat shape.

    Models:
      - ThresholdOverrides -- optional AND-gate threshold overrides
        for the eval harness only (mirrors utilities/loo_replay.py's
        model of the same name; redefined here rather than imported
        -- schemas/ must not depend on utilities/). None fields fall
        back to config.py defaults. Production signal_classifier.py
        and config.py are never touched by this -- the override is
        applied only inside domain/eval_scoring.py's own gate copy.
      - WalkForwardResult   -- one pattern's walk-forward outcome
      - WalkForwardBatch    -- full-catalog walk-forward run
      - TopKMatch           -- one ranked entry in a pattern's cached
        top-K set (WO-P300-E4.006). This is the ONLY model in this
        file with a real SQLite table behind it (topk_cache, decision
        #2) -- everything else here stays the transient, read-only
        contract described above. Added here rather than a new file
        because it belongs to the same walk-forward domain
        (TOP_K_MATCHES, decision #4) and this file has headroom.

CHANGELOG:
    - 2026-07-19 v1.2 (WO-P300-E4.006): Added TopKMatch -- schema
      required before infrastructure/topk_cache_io.py or
      domain/topk_cache.py per the project's schema-before-persistent-
      I/O rule (python-project-architecture skill). Mirrors the
      topk_cache table columns 1:1 (decision #5's final schema,
      confirmed 2026-07-19).
    - 2026-06-28 v1.1: Added ThresholdOverrides (BUY_MIN_Z_SCORE
      comparison run, post-N=300-ablation backlog item). WalkForward
      Batch gained threshold_overrides field so a written report is
      self-documenting about which gate produced it.
    - 2026-06-28 v1.0: Initial release. Stage 6 eval loop file #1 of 5
      (schemas_eval -> eval_scoring -> eval_io -> run_eval_loop -> .bat).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

_PYTHON_DIR = Path(__file__).resolve().parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from schemas_pipeline_b import AggregatedSignalPerHorizon, SignalClass  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Correctness label -- mirrors utilities/loo_replay.py's Correctness
# Literal. Redefined locally rather than imported: schemas/ is the
# lowest layer after config.py and must not depend on utilities/.
# ─────────────────────────────────────────────────────────────────────────────
Correctness = Literal[
    "correct_buy", "false_positive", "correct_pass", "missed", "neutral",
]


class ThresholdOverrides(BaseModel):
    """BUY/WATCH AND-gate threshold overrides for the eval harness.

    None = use config.py's live default for that field. Mirrors
    utilities/loo_replay.py's ThresholdOverrides field-for-field;
    redefined rather than imported (schemas/ must not depend on
    utilities/). Production config.py and signal_classifier.py are
    never modified by this -- domain/eval_scoring.py applies these
    in its own gate copy only.
    """

    model_config = ConfigDict(frozen=True)

    buy_min_n: int | None = None
    buy_min_win_rate: float | None = None
    buy_min_z_score: float | None = None
    watch_min_n: int | None = None
    watch_min_win_rate: float | None = None
    watch_min_z_score: float | None = None


class WalkForwardResult(BaseModel):
    """One pattern's walk-forward outcome.

    corpus_size is the count of PATTERN_IDENT patterns with
    anchor_date strictly earlier than this pattern's anchor_date --
    the only set this pattern is ranked against. No minimum-size
    floor: thin corpora (corpus_size 1, 2, 3...) are scored and
    reported honestly rather than skipped (operator decision,
    2026-06-28).

    degenerate_corpus is True iff corpus_size == 0 -- the earliest
    pattern(s) by anchor_date, which have nothing prior to compare
    against. signal_class still passes through the existing
    degenerate-baseline contract unmodified in that case (PASS,
    z_score=0.0, per aggregator.z_score's baseline=0.0 branch) --
    this flag exists so the output table doesn't read that PASS as
    a real evaluated rejection. No equivalent flag exists for thin
    (non-zero) corpora; corpus_size itself is the honest signal.

    actual_return_pct / actual_is_profitable / correctness are None
    when chosen_horizon has no forward_labels row for this pattern
    (edge-of-history patterns near the most recent anchor dates).
    """

    model_config = ConfigDict(frozen=True)

    pattern_instance_id: int
    symbol: str
    anchor_date: date
    corpus_size: int
    degenerate_corpus: bool
    signal_class: SignalClass
    chosen_horizon: int
    per_horizon: dict[int, AggregatedSignalPerHorizon]
    actual_return_pct: float | None = None
    actual_is_profitable: bool | None = None
    correctness: Correctness | None = None


class WalkForwardBatch(BaseModel):
    """Full-catalog walk-forward run -- one WalkForwardResult per pattern.

    n_patterns is len(results). n_degenerate is the count of results
    with degenerate_corpus=True (informational only -- not a quality
    gate; no floor was applied per operator decision, 2026-06-28).
    threshold_overrides is None when the run used config.py defaults
    unmodified -- stamped here so a written report file is self-
    documenting about which gate produced it without relying on the
    filename alone.
    """

    model_config = ConfigDict(frozen=True)

    catalog_path: str
    n_patterns: int
    n_degenerate: int
    threshold_overrides: ThresholdOverrides | None = None
    results: list[WalkForwardResult]


class TopKMatch(BaseModel):
    """One ranked entry in a pattern's cached top-K set (WO-P300-E4.006).

    Mirrors the topk_cache table's columns 1:1 -- unlike every other
    model in this file, this one has a real SQLite table behind it
    (decision #2: single source of truth, inside catalog.db itself,
    not a side file). rank is 1-indexed, closest analog first, 1..20
    (TOP_K_MATCHES, decision #4 -- exact, no headroom). matched_pid is
    the historical pattern this entry points to; composite_distance is
    the same DTW composite similarity.rank_by_distance() already
    computes (this model doesn't redefine the metric, only the
    persisted shape of its top-20 output).

    No feature_set_id field (decision #5): a feature-version bump
    invalidates every cached row at once, not selectively, so a full
    rebuild is the correct response rather than per-row version
    tracking -- validity is a whole-cache property, not a per-row one.
    """

    model_config = ConfigDict(frozen=True)

    pattern_instance_id: int
    rank: int
    matched_pid: int
    composite_distance: float
