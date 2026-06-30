"""
FILE: signal_classifier.py
VERSION: 1.2
DATE: 2026-06-09
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

    Decision F (locked 2026-05-16, config.py v1.2; CE term added v1.7):
        BUY:   n_matches >= BUY_MIN_MATCHES
               AND win_rate >= BUY_MIN_WIN_RATE
               AND z_score >  BUY_MIN_Z_SCORE
               AND (CE gate -- see below)
        WATCH: n_matches >= WATCH_MIN_MATCHES
               AND win_rate >= WATCH_MIN_WIN_RATE
               AND z_score >  WATCH_MIN_Z_SCORE
        PASS:  otherwise

        All conditions must hold for a class — AND-gate.
        Currently tuned loose (BUY thresholds 5 / 0.70 / 1.0; WATCH
        thresholds 3 / 0.60 / 0.0). Parameter sweep against the
        broader 14-symbol catalog will refine (Stage 8 Backlog).

    CE gate (config v1.7; Kochenderfer Ch. 6 -- BUY only):
        When CE_GATE_ENABLED is True, a horizon must additionally clear
        certainty_equivalent >= CE_MIN_THRESHOLD to qualify as BUY. The
        CE is the risk-adjusted forward return of the analog cluster
        (domain/utility.py); requiring it to clear a floor rejects BUYs
        whose raw mean is dragged up by a fat upside tail while the
        downside tail makes the risk-averse certainty-equivalent
        unattractive. WATCH is intentionally NOT CE-gated -- WATCH is a
        surveillance class, not a capital-commit decision.

        DETERMINISM: CE_GATE_ENABLED defaults False (config v1.7). While
        off, the CE term short-circuits True and classify_per_horizon is
        byte-identical to v1.0 -- the determinism regression is preserved
        until the operator flips the flag after tuning lambda. A None CE
        (horizon with no matches, which can never be BUY-eligible anyway)
        defensively passes the term rather than raising.

    Cross-horizon rule (schemas_pipeline_b SignalReport docstring):
        Signal class = strongest class achieved at any horizon.
        BUY > WATCH > PASS. Ties at the strongest class are broken by
        shortest horizon (sooner-actionable signals preferred).

        PASS-only reports: chosen_horizon names the horizon with the
        highest z_score among all horizons (closest to clearing the
        threshold). Ties broken by shortest horizon.

CHANGELOG:
    - 2026-06-09 v1.2: Smoke harness gains gate-ON coverage (cases 9-11):
      CE above threshold -> BUY survives; CE below threshold -> BUY blocked,
      drops to WATCH; gate OFF -> below-threshold CE ignored (no-op). The
      harness rebinds this module's own CE_GATE_ENABLED local (not
      config.CE_GATE_ENABLED) because the flag is bound at import time -- see
      IMPORT-TIME BINDING note below. Save/restore brackets the flip so state
      cannot leak into other runs. No change to the decision path.
    - 2026-06-09 v1.1: Added the Certainty-Equivalent BUY term to the
      Decision F AND-gate, guarded by config.CE_GATE_ENABLED (default False).
      BUY now also requires certainty_equivalent >= CE_MIN_THRESHOLD when the
      flag is on. WATCH unchanged. While the flag is off the term is a no-op
      (short-circuits True) and classification is byte-identical to v1.0,
      preserving the determinism regression. CE term applies to BUY only.
    - 2026-05-17 v1.0: Initial release. Stage 6 file #6 of 9.

IMPORT-TIME BINDING (CE_GATE_ENABLED / CE_MIN_THRESHOLD):
    These are imported by value at module load, so _ce_term_ok reads this
    module's local copy -- NOT config.CE_GATE_ENABLED live. Flipping the
    gate in production therefore means: edit config.py, then run a FRESH
    process (the next batch run). In-process toggling has no effect. This
    is correct for the workflow (set-once-per-run config), not a defect.
    The smoke harness flips the gate by rebinding the local on this module
    object, which is why it must `import domain.signal_classifier as sc`
    and set `sc.CE_GATE_ENABLED`, not `config.CE_GATE_ENABLED`.
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
    CE_GATE_ENABLED, CE_MIN_THRESHOLD,
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

def _ce_term_ok(stats: AggregatedSignalPerHorizon) -> bool:
    """CE BUY-gate term. True (no-op) when CE_GATE_ENABLED is False or the
    horizon has no CE; otherwise requires CE >= CE_MIN_THRESHOLD.

    Isolated so the short-circuit logic reads clearly and the BUY branch
    stays a flat AND-chain. While the gate is off this returns True
    unconditionally, keeping classification byte-identical to v1.0.
    """
    if not CE_GATE_ENABLED:
        return True
    if stats.certainty_equivalent is None:
        return True
    return stats.certainty_equivalent >= CE_MIN_THRESHOLD


def classify_per_horizon(stats: AggregatedSignalPerHorizon) -> SignalClass:
    """Apply Decision F AND-gate to one horizon's stats."""
    if (stats.n_matches >= BUY_MIN_MATCHES
            and stats.win_rate >= BUY_MIN_WIN_RATE
            and stats.z_score > BUY_MIN_Z_SCORE
            and _ce_term_ok(stats)):
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

    # 4. Per-horizon: clear BUY at the live z gate. BUY_MIN_Z_SCORE is 0.0
    #    (M-034, lowered 2026-05-28), so z=1.0 > 0.0 passes; n/wr also clear.
    #    (Originally written against the retired z>1.0 gate; updated v1.2.)
    print(f"BUY (z=1.0 vs live gate 0.0):  "
          f"{classify_per_horizon(stats(7, 10, 0.8, 3.5, 1.0, 1.0))} "
          f"(expect SignalClass.BUY)")

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

    # ---------------------------------------------------------------------
    # CE GATE coverage (cases 9-11). The gate value is read as a module
    # global by _ce_term_ok, so we must flip it on the SAME module object
    # that function lives in. When this file is run directly that module is
    # __main__, NOT the re-imported `domain.signal_classifier` (that would be
    # a second, separate copy -- the v1.2-first-cut bug). Resolve the real
    # module via the function's __module__ so it is correct under any
    # invocation. Save/restore brackets the flip so state cannot leak.
    # ---------------------------------------------------------------------
    import sys as _sys
    _selfmod = _sys.modules[classify_per_horizon.__module__]

    def ce_stats(h: int, n: int, wr: float, z: float,
                 ce: float) -> AggregatedSignalPerHorizon:
        """BUY-shaped stats with an explicit certainty_equivalent."""
        return AggregatedSignalPerHorizon(
            horizon_days=h, n_matches=n, win_rate=wr,
            mean_return_pct=0.05, std_return_pct=0.02, z_score=z,
            certainty_equivalent=ce,
        )

    print("-" * 60)
    print("CE GATE coverage (flag flipped on the live module object):")

    _saved_flag = _selfmod.CE_GATE_ENABLED
    _saved_thresh = _selfmod.CE_MIN_THRESHOLD
    ce_fails = 0
    try:
        _selfmod.CE_GATE_ENABLED = True
        _selfmod.CE_MIN_THRESHOLD = 0.0

        # 9. Gate ON, CE above threshold (+0.05) -> BUY survives.
        r9 = classify_per_horizon(ce_stats(7, 10, 0.8, 1.5, 0.05))
        ok9 = r9 == SignalClass.BUY
        ce_fails += 0 if ok9 else 1
        print(f"  9. gate ON, CE=+0.05 (>=0):   {r9} "
              f"(expect SignalClass.BUY){'' if ok9 else '  <<< FAIL'}")

        # 10. Gate ON, CE below threshold (-0.04) -> BUY blocked, falls to
        #     WATCH (n/wr/z still clear the WATCH gate; CE term is BUY-only).
        r10 = classify_per_horizon(ce_stats(7, 10, 0.8, 1.5, -0.04))
        ok10 = r10 == SignalClass.WATCH
        ce_fails += 0 if ok10 else 1
        print(f"  10. gate ON, CE=-0.04 (<0):   {r10} "
              f"(expect SignalClass.WATCH){'' if ok10 else '  <<< FAIL'}")

        # Restore BEFORE case 11 so it tests the genuine gate-OFF path.
        _selfmod.CE_GATE_ENABLED = _saved_flag
        _selfmod.CE_MIN_THRESHOLD = _saved_thresh

        # 11. Gate OFF, same below-threshold CE -> CE ignored, BUY survives
        #     (no-op proof: with the flag off the term short-circuits True).
        r11 = classify_per_horizon(ce_stats(7, 10, 0.8, 1.5, -0.04))
        ok11 = r11 == SignalClass.BUY
        ce_fails += 0 if ok11 else 1
        print(f"  11. gate OFF, CE=-0.04 ignored:{r11} "
              f"(expect SignalClass.BUY){'' if ok11 else '  <<< FAIL'}")
    finally:
        # Guarantee restore even if a case raised.
        _selfmod.CE_GATE_ENABLED = _saved_flag
        _selfmod.CE_MIN_THRESHOLD = _saved_thresh

    print("-" * 60)
    print("CE GATE: PASS" if ce_fails == 0
          else f"CE GATE: FAIL ({ce_fails} failing checks)")
