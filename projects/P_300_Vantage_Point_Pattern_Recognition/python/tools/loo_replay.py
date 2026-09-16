"""
FILE: loo_replay.py
VERSION: 1.0.1
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
LAYER: utility
DESCRIPTION:
    Leave-one-out replay harness for Stage 9. For each pid: hold it out,
    run Pipeline B math (similarity + aggregator + threshold-overridable
    AND-gate) against the other N-1, compare emitted signal vs the
    held-out pattern's actual forward returns. Read-only on catalog
    (M-012). signal_classifier NOT called — harness inlines a threshold-
    overridable AND-gate so the NFR-1-locked Stage 6 classifier stays
    frozen. Parity at config defaults verified by tests/smoke_loo_replay.py.
    Caveat: at N=25 LOO estimates are noisy; correctness labels are a
    measurement scaffold, not ground truth.
CHANGELOG:
    - 2026-05-19 v1.0.1: Removed inline smoke harness; moved to
      tests/smoke_loo_replay.py to keep this file under the 300-line
      standard. No functional change to the API or math.
    - 2026-05-19 v1.0: Initial release. Stage 9 file #1 of 3.
"""
from __future__ import annotations

import logging
import sys
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    BUY_MIN_MATCHES, BUY_MIN_WIN_RATE, BUY_MIN_Z_SCORE,
    FORWARD_HORIZONS, ORIGIN_PATTERN_IDENT, SIMILARITY_FEATURES,
    TOP_K_MATCHES, WATCH_MIN_MATCHES, WATCH_MIN_WIN_RATE,
    WATCH_MIN_Z_SCORE,
)
from domain import aggregator, similarity  # noqa: E402
from infrastructure import catalog_reader  # noqa: E402
from schemas_pipeline_b import (  # noqa: E402
    AggregatedSignalPerHorizon, LiveCandidate, NormalizedBar, SignalClass,
)
from utilities.db_connect import connection_context  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s",
                    stream=sys.stdout)
logger = logging.getLogger(__name__)


# ─── Pydantic models ────────────────────────────────────────────────────────

class ThresholdOverrides(BaseModel):
    """BUY/WATCH AND-gate threshold overrides; None = config default."""
    model_config = ConfigDict(frozen=True)
    buy_min_n: int | None = None
    buy_min_win_rate: float | None = None
    buy_min_z_score: float | None = None
    watch_min_n: int | None = None
    watch_min_win_rate: float | None = None
    watch_min_z_score: float | None = None


class FeatureMask(BaseModel):
    """Per-feature include flag. True=equal-weight, False=zero. All-False raises."""
    model_config = ConfigDict(frozen=True)
    close_pct_from_anchor: bool = True
    range_pct: bool = True
    body_pct: bool = True
    volume_zscore: bool = True
    stdiff_pct: bool = True
    mtdiff_pct: bool = True
    ltdiff_pct: bool = True
    pred_high_pct: bool = True
    pred_low_pct: bool = True
    pred_range_pct: bool = True

    def active_features(self) -> list[str]:
        return [f for f in SIMILARITY_FEATURES if getattr(self, f)]


Correctness = Literal[
    "correct_buy", "false_positive", "correct_pass", "missed", "neutral",
]


class HorizonResult(BaseModel):
    """Per-horizon: Pipeline-B-saw stats + emitted signal vs ground truth."""
    model_config = ConfigDict(frozen=True)
    horizon_days: int
    n_analogs: int
    cluster_win_rate: float
    cluster_mean_return: float
    cluster_std_return: float
    z_score: float
    signal_class: SignalClass
    actual_return: float
    actual_is_profitable: bool
    correctness: Correctness


class LooReplayResult(BaseModel):
    """One held-out pattern's signal vs reality across all 5 horizons."""
    model_config = ConfigDict(frozen=True)
    held_out_pattern_id: int
    held_out_symbol: str
    held_out_anchor_date: date
    horizon_results: list[HorizonResult]
    final_signal: SignalClass
    final_horizon: int


class LooReplayBatch(BaseModel):
    """Full-catalog replay — one LooReplayResult per pattern."""
    model_config = ConfigDict(frozen=True)
    catalog_path: str
    n_patterns: int
    threshold_overrides: ThresholdOverrides | None
    feature_mask: FeatureMask | None
    results: list[LooReplayResult]


# ─── Private helpers ────────────────────────────────────────────────────────

def _build_candidate(
    meta: catalog_reader.PatternMetadata, bars: list[NormalizedBar],
) -> LiveCandidate:
    return LiveCandidate(ticker=meta.ticker, anchor_date=meta.anchor_date,
                         window_length=meta.window_length, bars=bars)


def _masked_composite(per_feat: dict[str, float], mask: FeatureMask) -> float:
    active = mask.active_features()
    if not active:
        raise ValueError("FeatureMask has no active features; ranking undefined")
    return sum(per_feat[f] for f in active)


def _rank_with_optional_mask(
    candidate_bars: list[NormalizedBar],
    corpus: dict[int, list[NormalizedBar]],
    mask: FeatureMask | None,
) -> list[tuple[int, float, dict[str, float]]]:
    """Rank corpus ascending by composite distance; mask reweights post-call."""
    ranked = similarity.rank_by_distance(candidate_bars, corpus)
    if mask is None:
        return ranked
    rescored = [(pid, _masked_composite(per_feat, mask), per_feat)
                for pid, _comp, per_feat in ranked]
    rescored.sort(key=lambda t: t[1])
    return rescored


def _classify_per_horizon_overridable(
    stats: AggregatedSignalPerHorizon,
    overrides: ThresholdOverrides | None,
) -> SignalClass:
    """AND-gate Decision F with overrides. Parity at overrides=None == config defaults."""
    o = overrides
    bn = BUY_MIN_MATCHES if o is None or o.buy_min_n is None else o.buy_min_n
    bwr = BUY_MIN_WIN_RATE if o is None or o.buy_min_win_rate is None else o.buy_min_win_rate
    bz = BUY_MIN_Z_SCORE if o is None or o.buy_min_z_score is None else o.buy_min_z_score
    wn = WATCH_MIN_MATCHES if o is None or o.watch_min_n is None else o.watch_min_n
    wwr = WATCH_MIN_WIN_RATE if o is None or o.watch_min_win_rate is None else o.watch_min_win_rate
    wz = WATCH_MIN_Z_SCORE if o is None or o.watch_min_z_score is None else o.watch_min_z_score
    if stats.n_matches >= bn and stats.win_rate >= bwr and stats.z_score > bz:
        return SignalClass.BUY
    if stats.n_matches >= wn and stats.win_rate >= wwr and stats.z_score > wz:
        return SignalClass.WATCH
    return SignalClass.PASS


_CLASS_RANK = {SignalClass.PASS: 0, SignalClass.WATCH: 1, SignalClass.BUY: 2}


def _classify_signal_overridable(
    per_horizon_stats: dict[int, AggregatedSignalPerHorizon],
    overrides: ThresholdOverrides | None,
) -> tuple[SignalClass, int]:
    """Cross-horizon arbiter mirroring signal_classifier.classify_signal."""
    if not per_horizon_stats:
        raise ValueError("per_horizon_stats is empty")
    classified = [(h, _classify_per_horizon_overridable(s, overrides), s)
                  for h, s in per_horizon_stats.items()]
    best_rank = max(_CLASS_RANK[cls] for _, cls, _ in classified)
    winners = [(h, cls, s) for h, cls, s in classified
               if _CLASS_RANK[cls] == best_rank]
    if best_rank > 0:
        winners.sort(key=lambda t: t[0])
        return winners[0][1], winners[0][0]
    winners.sort(key=lambda t: (-t[2].z_score, t[0]))
    return winners[0][1], winners[0][0]


def _label_correctness(signal: SignalClass, is_profitable: bool) -> Correctness:
    if signal == SignalClass.BUY:
        return "correct_buy" if is_profitable else "false_positive"
    if signal == SignalClass.PASS:
        return "missed" if is_profitable else "correct_pass"
    return "neutral"


# ─── Public entry points ────────────────────────────────────────────────────

def replay_one(
    held_out_pattern_id: int,
    all_pids: list[int],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict,
    all_metadata: dict,
    *,
    threshold_overrides: ThresholdOverrides | None = None,
    feature_mask: FeatureMask | None = None,
) -> LooReplayResult:
    """Run one LOO replay against pre-loaded catalog data."""
    held_meta = all_metadata[held_out_pattern_id]
    held_bars = historical_windows[held_out_pattern_id]
    held_labels = all_labels.get(held_out_pattern_id, {})
    candidate = _build_candidate(held_meta, held_bars)

    corpus_pids = [p for p in all_pids if p != held_out_pattern_id]
    corpus_windows = {p: historical_windows[p] for p in corpus_pids}
    corpus_labels = {p: all_labels.get(p, {}) for p in corpus_pids}

    ranked = _rank_with_optional_mask(candidate.bars, corpus_windows, feature_mask)
    top_k_pids = [t[0] for t in ranked[:TOP_K_MATCHES]]
    top_k_label_map = {p: corpus_labels.get(p, {}) for p in top_k_pids}

    baseline = aggregator.catalog_baseline_win_rates(corpus_labels)
    per_horizon_stats = aggregator.aggregate_top_k(top_k_label_map, baseline)
    final_signal, final_horizon = _classify_signal_overridable(
        per_horizon_stats, threshold_overrides,
    )

    horizon_results: list[HorizonResult] = []
    for h in FORWARD_HORIZONS:
        if h not in per_horizon_stats or h not in held_labels:
            continue
        s = per_horizon_stats[h]
        actual = held_labels[h]
        sig_h = _classify_per_horizon_overridable(s, threshold_overrides)
        horizon_results.append(HorizonResult(
            horizon_days=h, n_analogs=s.n_matches, cluster_win_rate=s.win_rate,
            cluster_mean_return=s.mean_return_pct,
            cluster_std_return=s.std_return_pct, z_score=s.z_score,
            signal_class=sig_h, actual_return=actual.return_pct,
            actual_is_profitable=actual.is_profitable,
            correctness=_label_correctness(sig_h, actual.is_profitable),
        ))
    return LooReplayResult(
        held_out_pattern_id=held_out_pattern_id,
        held_out_symbol=held_meta.ticker,
        held_out_anchor_date=held_meta.anchor_date,
        horizon_results=horizon_results,
        final_signal=final_signal, final_horizon=final_horizon,
    )


def replay_all(
    threshold_overrides: ThresholdOverrides | None = None,
    feature_mask: FeatureMask | None = None,
) -> LooReplayBatch:
    """LOO replay across every PATTERN_IDENT pid in the latest catalog."""
    from utilities.db_utils import get_latest_catalog
    catalog_path = get_latest_catalog()
    with connection_context() as conn:
        all_pids = catalog_reader.get_all_pattern_ids(
            conn, origin_types=(ORIGIN_PATTERN_IDENT,))
        historical_windows = catalog_reader.bulk_load_normalized_windows(conn, all_pids)
        all_labels = catalog_reader.bulk_load_forward_labels(conn, all_pids)
        all_metadata = catalog_reader.bulk_load_pattern_metadata(conn, all_pids)
    logger.info("LOO replay over %d patterns", len(all_pids))
    results = [
        replay_one(pid, all_pids, historical_windows, all_labels, all_metadata,
                   threshold_overrides=threshold_overrides, feature_mask=feature_mask)
        for pid in all_pids
    ]
    return LooReplayBatch(
        catalog_path=str(catalog_path), n_patterns=len(all_pids),
        threshold_overrides=threshold_overrides, feature_mask=feature_mask,
        results=results,
    )
