"""
FILE: eval_scoring.py
VERSION: 1.1
DATE: 2026-06-28
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure walk-forward scoring for the Stage 6 eval loop. For each
    pattern: build a corpus of every PATTERN_IDENT pattern with a
    STRICTLY EARLIER anchor_date, run the same similarity/aggregator
    chain Pipeline B uses live, then classify via an inlined,
    overridable AND-gate (v1.1) instead of calling signal_classifier.
    classify_signal directly, to support BUY_MIN_Z_SCORE comparison
    runs (post-N=300-ablation backlog item) without touching
    production config.py or signal_classifier.py.

    Mirrors utilities/loo_replay.py's replay_one() call sequence and
    its _classify_per_horizon_overridable / _classify_signal_
    overridable gate copy verbatim (field names, fallback logic,
    cross-horizon arbiter). Same caveat as loo_replay: the CE term
    (_ce_term_ok in signal_classifier.py) is NOT applied in this gate
    copy. Harmless today (CE_GATE_ENABLED=False means the real
    classifier's CE term is a no-op), but if CE_GATE_ENABLED is ever
    flipped True in production, this harness's overrides=None path
    will silently stop matching live classify_signal until someone
    updates both gate copies. Parity at overrides=None is assumed by
    construction (same threshold constants imported from config.py),
    confirmed empirically this session by re-running the eval loop
    with no overrides and diffing signal counts against the v1.0
    direct-call run (155 BUY / 70 WATCH / 106 PASS, see chat log) --
    not enforced by an automated test in this delivery.

    No minimum-corpus-size floor (operator decision, 2026-06-28):
    every pattern is scored regardless of corpus_size. The chain
    handles corpus_size=0 without any special-casing here --
    similarity.rank_by_distance on an empty corpus dict returns an
    empty ranked list, aggregator.aggregate_top_k's existing n=0
    branch zero-fills every horizon, and aggregator.catalog_baseline_
    win_rates returns 0.0 baselines for an empty label set. The
    degenerate_corpus flag on WalkForwardResult is set here purely
    from corpus_size == 0, not from the chain's behavior.

    Layer rules: no I/O, no DB, no logging. Pure functions consuming
    pre-loaded dicts (from infrastructure/eval_io.py) and producing
    schemas_eval.py models.

CHANGELOG:
    - 2026-06-28 v1.1: Replaced the direct signal_classifier.
      classify_signal() call with an inlined overridable AND-gate
      (mirrors loo_replay.py) so score_one/run_walk_forward can take
      an optional ThresholdOverrides for BUY_MIN_Z_SCORE comparison
      runs. WalkForwardBatch now stamps threshold_overrides for
      report provenance.
    - 2026-06-28 v1.0: Initial release. Stage 6 eval loop file #2 of 5.
"""
from __future__ import annotations

import sys
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    BUY_MIN_MATCHES, BUY_MIN_WIN_RATE, BUY_MIN_Z_SCORE, FORWARD_HORIZONS,
    TOP_K_MATCHES, WATCH_MIN_MATCHES, WATCH_MIN_WIN_RATE, WATCH_MIN_Z_SCORE,
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
    filtered corpus.

    Args:
        pattern_id: the pattern being evaluated.
        all_metadata: every PATTERN_IDENT pid's PatternMetadata
            (from catalog_reader.bulk_load_pattern_metadata).
        historical_windows: every pid's NormalizedBar list
            (from catalog_reader.bulk_load_normalized_windows).
        all_labels: every pid's forward labels keyed by horizon_days
            (from catalog_reader.bulk_load_forward_labels).
        threshold_overrides: optional AND-gate overrides; None uses
            config.py defaults via the overridable gate above.

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


def run_walk_forward(
    catalog_path: str,
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    threshold_overrides: ThresholdOverrides | None = None,
) -> WalkForwardBatch:
    """Score every pid in all_metadata, oldest anchor_date first.

    Sort order doesn't affect scoring (each pattern's corpus is
    computed independently by date filter, not by loop position) --
    oldest-first just makes the output table read chronologically.
    """
    ordered_pids = sorted(
        all_metadata.keys(),
        key=lambda pid: all_metadata[pid].anchor_date,
    )
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
