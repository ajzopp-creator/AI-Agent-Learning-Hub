"""
FILE: eval_scoring.py
VERSION: 1.2
DATE: 2026-07-16
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure walk-forward scoring for the Stage 6 eval loop. Per pattern:
    corpus = every PATTERN_IDENT pattern with a STRICTLY EARLIER
    anchor_date, scored via the same similarity/aggregator chain
    Pipeline B uses live, classified via an inlined overridable
    AND-gate (v1.1, mirrors utilities/loo_replay.py verbatim) so
    BUY_MIN_Z_SCORE comparison runs never touch production config.py
    or signal_classifier.py.

    CE-term caveat: the gate copy does NOT apply signal_classifier's
    CE term. Harmless while CE_GATE_ENABLED=False; if ever flipped
    True in production, overrides=None here silently stops matching
    live classify_signal until both gate copies are updated. Parity
    at overrides=None confirmed empirically 2026-06-28 (155/70/106
    BUY/WATCH/PASS vs. the v1.0 direct-call run), not test-enforced.

    No minimum-corpus-size floor (2026-06-28): similarity.rank_by_
    distance, aggregator.aggregate_top_k, and aggregator.catalog_
    baseline_win_rates all have existing empty-input branches for
    corpus_size == 0 (degenerate_corpus).

    Layer rules: no file/DB/network I/O, no logging. score_one() and
    run_walk_forward(parallel=False) are unchanged pure functions. The
    v1.2 parallel path (WO-P300-E4.003, M-096) is process-level
    fan-out via stdlib concurrent.futures -- CPU dispatch, not I/O --
    cutting wall-clock with zero change to the math: parallel and
    serial call the same score_one() and must be byte-identical (see
    tests/test_eval_scoring.py).

CHANGELOG:
    - 2026-07-16 v1.2: WO-P300-E4.003 (M-096) -- run_walk_forward()
      gains parallel/max_workers. parallel=True fans score_one() out
      via ProcessPoolExecutor; _init_worker sets per-process globals
      ONCE (not re-pickled per pattern); executor.map preserves
      ordered_pids order, matching serial output. Serial path
      unchanged.
    - 2026-06-28 v1.1: Overridable AND-gate for BUY_MIN_Z_SCORE runs;
      WalkForwardBatch stamps threshold_overrides.
    - 2026-06-28 v1.0: Initial release. Stage 6 eval loop file #2 of 5.
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    BUY_MIN_MATCHES, BUY_MIN_WIN_RATE, BUY_MIN_Z_SCORE, FORWARD_HORIZONS,
    TOP_K_MATCHES, WALK_FORWARD_SERIAL_MS_PER_PAIR, WATCH_MIN_MATCHES,
    WATCH_MIN_WIN_RATE, WATCH_MIN_Z_SCORE,
)
from domain import aggregator, similarity  # noqa: E402
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_eval import (  # noqa: E402
    Correctness, ThresholdOverrides, WalkForwardBatch, WalkForwardResult,
)
from schemas_pipeline_b import (  # noqa: E402
    AggregatedSignalPerHorizon, ForwardLabelLite, NormalizedBar, SignalClass,
)

_CLASS_RANK = {SignalClass.PASS: 0, SignalClass.WATCH: 1, SignalClass.BUY: 2}


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _label_correctness(signal: SignalClass, is_profitable: bool) -> Correctness:
    """Mirrors loo_replay._label_correctness -- redefined, not imported.

    domain/ must not depend on utilities/ (layer rule); this is a
    4-line pure function, not worth a shared-helper module.
    """
    if signal == SignalClass.BUY:
        return "correct_buy" if is_profitable else "false_positive"
    if signal == SignalClass.PASS:
        return "missed" if is_profitable else "correct_pass"
    return "neutral"


def _corpus_pids(
    pattern_id: int,
    all_metadata: dict[int, PatternMetadata],
) -> list[int]:
    """Every PATTERN_IDENT pid with anchor_date strictly earlier than
    pattern_id's anchor_date. Ties on anchor_date are excluded (not
    "earlier") -- same-day patterns did not exist as analogs to each
    other at evaluation time.
    """
    target_date = all_metadata[pattern_id].anchor_date
    return [
        pid for pid, meta in all_metadata.items()
        if pid != pattern_id and meta.anchor_date < target_date
    ]


def _classify_per_horizon_overridable(
    stats: AggregatedSignalPerHorizon,
    overrides: ThresholdOverrides | None,
) -> SignalClass:
    """AND-gate with overrides; None fields fall back to config.py.

    No CE term -- see module docstring caveat (harmless while
    CE_GATE_ENABLED=False).
    """
    o = overrides
    bn = BUY_MIN_MATCHES if o is None or o.buy_min_n is None else o.buy_min_n
    bwr = (BUY_MIN_WIN_RATE if o is None or o.buy_min_win_rate is None
           else o.buy_min_win_rate)
    bz = (BUY_MIN_Z_SCORE if o is None or o.buy_min_z_score is None
          else o.buy_min_z_score)
    wn = (WATCH_MIN_MATCHES if o is None or o.watch_min_n is None
          else o.watch_min_n)
    wwr = (WATCH_MIN_WIN_RATE if o is None or o.watch_min_win_rate is None
           else o.watch_min_win_rate)
    wz = (WATCH_MIN_Z_SCORE if o is None or o.watch_min_z_score is None
          else o.watch_min_z_score)
    if stats.n_matches >= bn and stats.win_rate >= bwr and stats.z_score > bz:
        return SignalClass.BUY
    if stats.n_matches >= wn and stats.win_rate >= wwr and stats.z_score > wz:
        return SignalClass.WATCH
    return SignalClass.PASS


def _classify_signal_overridable(
    per_horizon_stats: dict[int, AggregatedSignalPerHorizon],
    overrides: ThresholdOverrides | None,
) -> tuple[SignalClass, int]:
    """Cross-horizon arbiter mirroring signal_classifier.classify_signal,
    routed through the overridable per-horizon gate above.
    """
    if not per_horizon_stats:
        raise ValueError("per_horizon_stats is empty")
    classified = [
        (h, _classify_per_horizon_overridable(s, overrides), s)
        for h, s in per_horizon_stats.items()
    ]
    best_rank = max(_CLASS_RANK[cls] for _, cls, _ in classified)
    winners = [
        (h, cls, s) for h, cls, s in classified
        if _CLASS_RANK[cls] == best_rank
    ]
    if best_rank > 0:
        winners.sort(key=lambda t: t[0])
        return winners[0][1], winners[0][0]
    winners.sort(key=lambda t: (-t[2].z_score, t[0]))
    return winners[0][1], winners[0][0]


# ─────────────────────────────────────────────────────────────────────────────
# Public entry points
# ─────────────────────────────────────────────────────────────────────────────

def score_one(
    pattern_id: int,
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    threshold_overrides: ThresholdOverrides | None = None,
) -> WalkForwardResult:
    """Run one pattern's walk-forward evaluation against its date-
    filtered corpus. all_metadata/historical_windows/all_labels are
    every PATTERN_IDENT pid's data (from catalog_reader's bulk_load_*
    functions), keyed by pattern_instance_id. threshold_overrides:
    optional AND-gate overrides; None uses config.py defaults.

    Returns:
        WalkForwardResult for this pattern. degenerate_corpus=True
        iff no earlier-dated patterns exist.
    """
    meta = all_metadata[pattern_id]
    candidate_bars = historical_windows[pattern_id]
    own_labels = all_labels.get(pattern_id, {})

    corpus_pids = _corpus_pids(pattern_id, all_metadata)
    corpus_size = len(corpus_pids)
    degenerate = corpus_size == 0

    corpus_windows = {pid: historical_windows[pid] for pid in corpus_pids}
    corpus_labels = {pid: all_labels.get(pid, {}) for pid in corpus_pids}

    ranked = similarity.rank_by_distance(candidate_bars, corpus_windows)
    top_k_pids = [pid for pid, _dist, _per_feat in ranked[:TOP_K_MATCHES]]
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


# ─────────────────────────────────────────────────────────────────────────────
# Parallel path -- WO-P300-E4.003 (M-096)
# ─────────────────────────────────────────────────────────────────────────────
# _init_worker runs once per worker process, storing that worker's own copy
# of the three read-only dicts as globals; _score_one_worker then takes just
# a pattern_id per task -- dicts pickled once per worker, not once per task.

_worker_metadata: dict[int, PatternMetadata] | None = None
_worker_windows: dict[int, list[NormalizedBar]] | None = None
_worker_labels: dict[int, dict[int, ForwardLabelLite]] | None = None
_worker_overrides: ThresholdOverrides | None = None


def _init_worker(
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    threshold_overrides: ThresholdOverrides | None,
) -> None:
    """ProcessPoolExecutor initializer -- see module note above."""
    global _worker_metadata, _worker_windows, _worker_labels, _worker_overrides
    _worker_metadata = all_metadata
    _worker_windows = historical_windows
    _worker_labels = all_labels
    _worker_overrides = threshold_overrides


def _score_one_worker(pattern_id: int) -> WalkForwardResult:
    """Reads this process's _init_worker globals, scores one pattern.
    Only valid inside a pool started with initializer=_init_worker."""
    return score_one(
        pattern_id, _worker_metadata, _worker_windows, _worker_labels,
        _worker_overrides,
    )


def run_walk_forward(
    catalog_path: str,
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    threshold_overrides: ThresholdOverrides | None = None,
    parallel: bool = False,
    max_workers: int | None = None,
) -> WalkForwardBatch:
    """Score every pid, oldest anchor_date first (sort order doesn't
    affect scoring -- corpus is date-filtered independently per
    pattern). parallel=False (default): unchanged serial path.
    parallel=True: ProcessPoolExecutor fan-out (see module note);
    executor.map preserves order, matching the serial path exactly.
    max_workers=None defers to ProcessPoolExecutor's own default.
    """
    ordered_pids = sorted(
        all_metadata.keys(),
        key=lambda pid: all_metadata[pid].anchor_date,
    )
    if parallel and len(ordered_pids) > 1:
        with ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_init_worker,
            initargs=(all_metadata, historical_windows, all_labels,
                      threshold_overrides),
        ) as executor:
            results = list(executor.map(_score_one_worker, ordered_pids))
    else:
        results = [
            score_one(
                pid, all_metadata, historical_windows, all_labels,
                threshold_overrides,
            )
            for pid in ordered_pids
        ]
    n_degenerate = sum(1 for r in results if r.degenerate_corpus)
    return WalkForwardBatch(
        catalog_path=catalog_path,
        n_patterns=len(results),
        n_degenerate=n_degenerate,
        threshold_overrides=threshold_overrides,
        results=results,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Full-rescore cost estimate -- WO-P300-E5.004
# ─────────────────────────────────────────────────────────────────────────────

def estimate_full_rescore_seconds(corpus_size: int) -> float:
    """Estimated wall time for a full, uncached, serial run_walk_forward()
    over corpus_size patterns (parallel=False -- EVAL_PARALLEL_ENABLED is
    False, WO-P300-E4.005 Phase 2c).

    Per-pattern cost grows with that pattern's own corpus (every earlier-
    dated pattern, see _corpus_pids), so scoring N patterns oldest-first
    costs roughly WALK_FORWARD_SERIAL_MS_PER_PAIR x (0 + 1 + ... + N-1) =
    WALK_FORWARD_SERIAL_MS_PER_PAIR x N(N-1)/2 -- integrating the measured
    per-pair rate (config.py, WO-P300-E4.005) over a linearly growing
    corpus. APPROXIMATION -- see config.py's constant docstring for
    caveats (not re-measured for this WO, may drift with catalog
    composition). Used only for the WO-P300-E5.004 confirm-before-rescore
    gate, not a scheduling guarantee.

    Returns 0.0 for corpus_size <= 1 (nothing to integrate).
    """
    if corpus_size <= 1:
        return 0.0
    total_ms = (
        WALK_FORWARD_SERIAL_MS_PER_PAIR * corpus_size * (corpus_size - 1) / 2
    )
    return total_ms / 1000.0
