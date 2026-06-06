"""
FILE: signal_classifier.py
VERSION: 1.0
DATE: 2026-05-17
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-math BUY / WATCH / PASS classifier for Pipeline B. Consumes a
    dict of AggregatedSignalPerHorizon (built by domain/aggregator.py)
    and produces (signal_class, chosen_horizon) — the two fields the
    orchestrator needs to populate SignalReport.

    Layer rules:
        - No I/O. No DB. No logging. No print() outside __main__.
        - Pure functions. Single-pattern AND-gate decision; cross-
          horizon "strongest horizon wins" with shortest-horizon
          tiebreak.

    Decision F (locked 2026-05-16, config.py v1.2):
        BUY:   n_matches >= BUY_MIN_MATCHES
               AND win_rate >= BUY_MIN_WIN_RATE
               AND z_score >  BUY_MIN_Z_SCORE
        WATCH: n_matches >= WATCH_MIN_MATCHES
               AND win_rate >= WATCH_MIN_WIN_RATE
               AND z_score >  WATCH_MIN_Z_SCORE
        PASS:  otherwise

        All three conditions must hold for a class — AND-gate.
        Currently tuned loose (BUY thresholds 5 / 0.70 / 1.0; WATCH
        thresholds 3 / 0.60 / 0.0). Parameter sweep against the
        broader 14-symbol catalog will refine (Stage 8 Backlog).

    Cross-horizon rule (schemas_pipeline_b SignalReport docstring):
        Signal class = strongest class achieved at any horizon.
        BUY > WATCH > PASS. Ties at the strongest class are broken by
        shortest horizon (sooner-actionable signals preferred).

        PASS-only reports: chosen_horizon names the horizon with the
        highest z_score among all horizons (closest to clearing the
        threshold). Ties broken by shortest horizon.

CHANGELOG:
    - 2026-05-17 v1.0: Initial release. Stage 6 file #6 of 9.
"""
from __future__ import annotations

import sys
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    BUY_MIN_MATCHES, BUY_MIN_WIN_RATE, BUY_MIN_Z_SCORE,
    WATCH_MIN_MATCHES, WATCH_MIN_WIN_RATE, WATCH_MIN_Z_SCORE,
)
from schemas_pipeline_b import (  # noqa: E402
    AggregatedSignalPerHorizon,
    SignalClass,
)

# Class precedence — BUY (2) > WATCH (1) > PASS (0). Used internally
# for cross-horizon comparison. Caller never sees the ints.
_CLASS_RANK: dict[SignalClass, int] = {
    SignalClass.PASS: 0,
    SignalClass.WATCH: 1,
    SignalClass.BUY: 2,
}


# ─────────────────────────────────────────────────────────────────────────────
# Per-horizon classification — AND-gate
# ─────────────────────────────────────────────────────────────────────────────

def classify_per_horizon(stats: AggregatedSignalPerHorizon) -> SignalClass:
    """Apply Decision F AND-gate to one horizon's stats."""
    if (stats.n_matches >= BUY_MIN_MATCHES
            and stats.win_rate >= BUY_MIN_WIN_RATE
            and stats.z_score > BUY_MIN_Z_SCORE):
        return SignalClass.BUY
    if (stats.n_matches >= WATCH_MIN_MATCHES
            and stats.win_rate >= WATCH_MIN_WIN_RATE
            and stats.z_score > WATCH_MIN_Z_SCORE):
        return SignalClass.WATCH
    return SignalClass.PASS


# ─────────────────────────────────────────────────────────────────────────────
# Cross-horizon classification — strongest class wins
# ─────────────────────────────────────────────────────────────────────────────

def classify_signal(
    per_horizon_stats: dict[int, AggregatedSignalPerHorizon],
) -> tuple[SignalClass, int]:
    """Roll per-horizon classifications up to a single (class, horizon).

    Strongest-class-wins with shortest-horizon tiebreak among
    horizons sharing the winning class. PASS-only reports name the
    horizon with the highest z_score (ties broken by shortest
    horizon).

    Args:
        per_horizon_stats: dict keyed by horizon_days; every horizon
            in the dict is considered. Empty dict raises ValueError.

    Returns:
        Tuple (signal_class, chosen_horizon). Caller populates the
        matching fields on SignalReport.
    """
    if not per_horizon_stats:
        raise ValueError("per_horizon_stats is empty")

    classified: list[tuple[int, SignalClass, AggregatedSignalPerHorizon]] = [
        (horizon, classify_per_horizon(stats), stats)
        for horizon, stats in per_horizon_stats.items()
    ]
    best_rank = max(_CLASS_RANK[cls] for _, cls, _ in classified)
    winners = [
        (h, cls, stats) for h, cls, stats in classified
        if _CLASS_RANK[cls] == best_rank
    ]

    if best_rank > 0:
        # BUY or WATCH: shortest horizon among winners.
        winners.sort(key=lambda t: t[0])
        return winners[0][1], winners[0][0]

    # PASS: highest z_score, shortest horizon on ties. Sort ascending
    # on (-z, horizon) so highest z lands first; +inf z (degenerate
    # baseline=0 case) sorts ahead of all finite values.
    winners.sort(key=lambda t: (-t[2].z_score, t[0]))
    return winners[0][1], winners[0][0]


# ─────────────────────────────────────────────────────────────────────────────
# Smoke harness — `python domain/signal_classifier.py`
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Fixtures use only AggregatedSignalPerHorizon — no catalog dep.

    def stats(h: int, n: int, wr: float, mr: float, sr: float,
              z: float) -> AggregatedSignalPerHorizon:
        return AggregatedSignalPerHorizon(
            horizon_days=h, n_matches=n, win_rate=wr,
            mean_return_pct=mr, std_return_pct=sr, z_score=z,
        )

    # 1. Per-horizon: clear BUY (n=10, wr=0.8, z=1.5)
    print(f"BUY gate (10, 0.8, 1.5):       "
          f"{classify_per_horizon(stats(7, 10, 0.8, 3.5, 1.2, 1.5))} "
          f"(expect SignalClass.BUY)")

    # 2. Per-horizon: WATCH (n=5, wr=0.65, z=0.5) — fails BUY (z<=1.0
    #    and wr<0.7), passes WATCH (n>=3, wr>=0.6, z>0)
    print(f"WATCH gate (5, 0.65, 0.5):     "
          f"{classify_per_horizon(stats(7, 5, 0.65, 2.0, 1.0, 0.5))} "
          f"(expect SignalClass.WATCH)")

    # 3. Per-horizon: PASS (n=3, wr=0.5 — fails WATCH wr threshold)
    print(f"PASS gate (3, 0.5, 0.4):       "
          f"{classify_per_horizon(stats(7, 3, 0.5, 1.0, 0.5, 0.4))} "
          f"(expect SignalClass.PASS)")

    # 4. Per-horizon: BUY win_rate met but z fails (1.0 not > 1.0) → WATCH
    print(f"WATCH (z=1.0 strict-gt fails): "
          f"{classify_per_horizon(stats(7, 10, 0.8, 3.5, 1.0, 1.0))} "
          f"(expect SignalClass.WATCH)")

    # 5. Cross-horizon: BUY at 15 beats WATCH at 10 beats PASS at 5
    mixed = {
        5: stats(5, 3, 0.5, 1.0, 0.5, 0.2),
        10: stats(10, 5, 0.65, 2.0, 1.0, 0.5),
        15: stats(15, 10, 0.8, 4.0, 1.5, 1.5),
    }
    cls, h = classify_signal(mixed)
    print(f"mixed BUY at 15:               ({cls}, {h}) "
          f"(expect (SignalClass.BUY, 15))")

    # 6. Tie at WATCH between horizons 5 and 10 — shortest wins
    tied = {
        5: stats(5, 5, 0.65, 2.0, 1.0, 0.5),
        10: stats(10, 5, 0.65, 2.0, 1.0, 0.5),
        15: stats(15, 3, 0.5, 1.0, 0.5, 0.2),
    }
    cls, h = classify_signal(tied)
    print(f"tie WATCH 5 vs 10:             ({cls}, {h}) "
          f"(expect (SignalClass.WATCH, 5))")

    # 7. All-PASS: chosen_horizon = horizon with highest z (h=10, z=0.5)
    allpass = {
        5: stats(5, 3, 0.5, 0.0, 0.0, -1.0),
        10: stats(10, 3, 0.5, 0.0, 0.0, 0.5),  # highest z, still PASS (wr<0.6)
        15: stats(15, 3, 0.5, 0.0, 0.0, -2.0),
    }
    cls, h = classify_signal(allpass)
    print(f"all-PASS pick highest z:       ({cls}, {h}) "
          f"(expect (SignalClass.PASS, 10))")

    # 8. Empty dict raises
    try:
        classify_signal({})
        print("FAIL: empty dict should have raised")
    except ValueError as err:
        print(f"empty dict raises:             OK ({err})")
