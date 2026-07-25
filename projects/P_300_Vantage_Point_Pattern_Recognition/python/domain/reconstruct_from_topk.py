"""
FILE: reconstruct_from_topk.py
VERSION: 1.0
DATE: 2026-07-23
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    WO-P300-E5.004 Part A (candidate 2). Reconstructs one pattern's
    WalkForwardResult from a pre-loaded topk_cache entry instead of a
    fresh similarity.rank_by_distance() DTW pass -- the one expensive
    step in domain/eval_scoring.py's score_one(). Everything else
    (baseline win-rate, classification) is cheap label aggregation with
    no distance computation, confirmed by reading aggregator.py's
    catalog_baseline_win_rates() directly (WO-P300-E5.004 research,
    2026-07-23) -- this file does NOT reimplement that, it calls the
    real thing.

    _corpus_pids, _classify_signal_overridable, _label_correctness are
    imported directly from domain.eval_scoring, not duplicated (M-082)
    -- the entire point of this file is to match score_one()'s output
    exactly, so the classification logic must be the SAME code, not a
    parallel copy that could silently drift.

    Gap handling: a pid with zero topk_cache rows is EITHER genuinely
    degenerate (corpus_size == 0, correct and expected -- topk_cache.py's
    _rank_topk() returns [] for an empty corpus by design) OR a real,
    unexpected gap (corpus_size > 0 but topk_cache still has nothing --
    should not happen per the 2026-07-23 live-catalog check, but this
    file does not assume that check stays true forever). classify_topk_
    gap() makes this distinction explicit; callers (application/
    reconstruct_pre_batch.py) must not silently treat a real gap as
    degenerate.

    Layer rules: no file/DB/network I/O, no logging (domain/ pure logic
    only -- infrastructure/topk_cache_io.py owns all SQLite I/O for
    this table; application/reconstruct_pre_batch.py owns orchestration
    and the real-gap fallback).

CHANGELOG:
    - 2026-07-23 v1.0: WO-P300-E5.004 Part A. Initial release.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain import aggregator  # noqa: E402
from domain.eval_scoring import (  # noqa: E402
    _classify_signal_overridable, _corpus_pids, _label_correctness,
)
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_eval import (  # noqa: E402
    ThresholdOverrides, TopKMatch, WalkForwardResult,
)
from schemas_pipeline_b import ForwardLabelLite  # noqa: E402

GapStatus = Literal["ok", "degenerate", "gap"]


def classify_topk_gap(corpus_size: int, topk_matches: list[TopKMatch]) -> GapStatus:
    """Distinguishes a correctly-empty topk_cache entry from a real gap.

    "ok": topk_matches is non-empty -- normal case, use directly.
    "degenerate": topk_matches is empty AND corpus_size == 0 -- correct,
        expected (this pattern's anchor_date is at or before the
        earliest anything else in the catalog; there was nothing to
        rank it against, so topk_cache.py's _rank_topk() correctly
        wrote zero rows). NOT an error.
    "gap": topk_matches is empty but corpus_size > 0 -- a real corpus
        existed and topk_cache still has nothing for this pid. Should
        not happen (confirmed against the live catalog 2026-07-23, 0
        of 6 empty-topk pids fell in this bucket) but is not assumed
        to stay that way forever. Caller must fall back to a real
        (fresh DTW) score for pids in this bucket, never guess.
    """
    if topk_matches:
        return "ok"
    if corpus_size == 0:
        return "degenerate"
    return "gap"


def score_one_from_topk_cache(
    pattern_id: int,
    all_metadata: dict[int, PatternMetadata],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    topk_matches: list[TopKMatch],
    threshold_overrides: ThresholdOverrides | None = None,
) -> WalkForwardResult:
    """Same output contract as domain.eval_scoring.score_one(), built
    from a pre-loaded topk_cache entry instead of a fresh DTW pass.

    Caller must have already resolved this pid's gap status via
    classify_topk_gap() -- this function does not itself distinguish
    "degenerate" from "gap"; it treats topk_matches as authoritative
    for whichever pids the caller decided are safe to reconstruct this
    way. Calling this on a "gap" pid produces a result that LOOKS like
    a degenerate-corpus PASS but isn't one -- that is the caller's
    mistake to avoid, not this function's to detect twice.
    """
    meta = all_metadata[pattern_id]
    own_labels = all_labels.get(pattern_id, {})

    corpus_pids = _corpus_pids(pattern_id, all_metadata)
    corpus_size = len(corpus_pids)
    degenerate = corpus_size == 0

    corpus_labels = {pid: all_labels.get(pid, {}) for pid in corpus_pids}

    top_k_pids = [
        m.matched_pid for m in sorted(topk_matches, key=lambda m: m.rank)
    ]
    top_k_label_map = {pid: corpus_labels.get(pid, {}) for pid in top_k_pids}

    baseline = aggregator.catalog_baseline_win_rates(corpus_labels)
    per_horizon_stats = aggregator.aggregate_top_k(top_k_label_map, baseline)
    final_signal, final_horizon = _classify_signal_overridable(
        per_horizon_stats, threshold_overrides,
    )

    actual = own_labels.get(final_horizon)
    return WalkForwardResult(
        pattern_instance_id=pattern_id,
        symbol=meta.ticker,
        anchor_date=meta.anchor_date,
        corpus_size=corpus_size,
        degenerate_corpus=degenerate,
        signal_class=final_signal,
        chosen_horizon=final_horizon,
        per_horizon=per_horizon_stats,
        actual_return_pct=actual.return_pct if actual else None,
        actual_is_profitable=actual.is_profitable if actual else None,
        correctness=(
            _label_correctness(final_signal, actual.is_profitable)
            if actual else None
        ),
    )
