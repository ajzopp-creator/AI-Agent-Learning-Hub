"""
FILE: aggregator.py
VERSION: 1.1
DATE: 2026-06-09
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pure-math aggregation for Pipeline B. Consumes top-K matches'
    forward labels (loaded by infrastructure/catalog_reader.py) plus
    a per-horizon catalog baseline win-rate, and produces one
    AggregatedSignalPerHorizon per horizon for the signal classifier.

    Layer rules:
        - No I/O. No DB. No logging. No print() outside __main__.
          Pure functions consuming dicts of ForwardLabelLite,
          producing dicts of AggregatedSignalPerHorizon.
        - config.FORWARD_HORIZONS is the canonical horizon set.
        - Pydantic field validators on AggregatedSignalPerHorizon
          (n_matches ge=0, win_rate ge=0 le=1, std_return_pct ge=0)
          fire at construction; aggregator must produce valid values
          for every horizon, including absent ones (n=0 with zero
          stats — see below).

    Output shape:
        Every horizon in `horizons` appears in the returned dict.
        Horizons with no top-K labels get n_matches=0 and all stats
        set to 0.0 (z_score=0.0 included). This keeps File #7's
        report layout consistent and lets the signal classifier
        filter via the n_matches threshold rather than checking dict
        membership.

    Z-score semantics (architecture §2.2 + config.py docstring):
        Two-proportion z under the null that the top-K win-rate is
        drawn from the catalog's baseline win-rate at the same horizon.
        SE = sqrt(p0 * (1 - p0) / n). Z > 0 = top-K wins more often
        than typical catalog analogs; Z > 1.0 = significantly above
        baseline (Decision F BUY threshold).

        Degenerate baselines:
            baseline=1.0 means every catalog pattern wins at this
            horizon — SE collapses to 0 and the standard formula
            divides by zero. Guarded: if sample also 1.0 → 0.0
            (no excess possible); else -inf.
            baseline=0.0 mirror image: sample 0.0 → 0.0; else +inf.

        Small-catalog caveat:
            With Stage 5's 5-POC catalog, baseline win-rate is 1.0
            at horizons 5/7/10/15 and 0.8 at 20. BUY signals
            (requires z > 1.0) are therefore effectively unreachable
            at four of five horizons by construction; only horizon
            20 admits a meaningful z. This is a catalog-size issue,
            not a math bug — z gates start firing once the broader
            14-symbol historical set is ingested.

CHANGELOG:
    - 2026-06-09 v1.1: aggregate_top_k now computes the certainty-equivalent
      return per horizon (domain/utility.certainty_equivalent) and attaches it
      to AggregatedSignalPerHorizon.certainty_equivalent. lambda is read from
      config.RISK_AVERSION_LAMBDA and passed into the pure utility kernel.
      Decimal-space throughout (M-020): the `returns` list is already decimal
      fractions, so CE is decimal too -- no scaling here. CE is computed for
      every non-empty horizon regardless of CE_GATE_ENABLED; the flag only
      controls whether signal_classifier USES it (config v1.7). Empty horizons
      keep certainty_equivalent=None. Does not alter any existing stat, so the
      determinism regression stays byte-identical until the gate is flipped on.
    - 2026-05-17 v1.0: Initial release. Stage 6 file #5 of 9.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import FORWARD_HORIZONS, RISK_AVERSION_LAMBDA  # noqa: E402
from schemas_pipeline_b import (  # noqa: E402
    AggregatedSignalPerHorizon,
    ForwardLabelLite,
)
from domain.utility import certainty_equivalent  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _mean(values: list[float]) -> float:
    """Arithmetic mean; empty input raises ValueError."""
    if not values:
        raise ValueError("_mean called on empty list")
    return sum(values) / len(values)


def _population_std(values: list[float], mean: float) -> float:
    """Population std (ddof=0). Empty/single-value input returns 0.0."""
    if len(values) <= 1:
        return 0.0
    return math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))


# ─────────────────────────────────────────────────────────────────────────────
# Public helpers — callable from signal.py, report_writer.py, or directly
# ─────────────────────────────────────────────────────────────────────────────

def win_rate(labels: list[ForwardLabelLite]) -> float:
    """Fraction of labels with is_profitable=True.

    Empty input raises — caller must guard via n=0 check first; mixing
    the empty case with a 0.0 sentinel hides bugs.
    """
    if not labels:
        raise ValueError("win_rate called on empty list")
    wins = sum(1 for lbl in labels if lbl.is_profitable)
    return wins / len(labels)


def z_score(
    sample_win_rate: float,
    sample_n: int,
    baseline_win_rate: float,
) -> float:
    """Two-proportion z-statistic under the null that the sample is
    drawn from the baseline population.

    Returns:
        Standardized excess win-rate. See module docstring for the
        degenerate-baseline contract (returns 0.0 / +inf / -inf as
        appropriate when baseline ∈ {0.0, 1.0}).

    Args:
        sample_win_rate: top-K win-rate at this horizon (0.0–1.0)
        sample_n: count of top-K matches at this horizon
        baseline_win_rate: catalog-wide win-rate at this horizon

    Returns 0.0 if sample_n == 0 (no data — caller filters).
    """
    if sample_n == 0:
        return 0.0
    if baseline_win_rate == 1.0:
        return 0.0 if sample_win_rate == 1.0 else -math.inf
    if baseline_win_rate == 0.0:
        return 0.0 if sample_win_rate == 0.0 else math.inf
    se = math.sqrt(baseline_win_rate * (1.0 - baseline_win_rate) / sample_n)
    return (sample_win_rate - baseline_win_rate) / se


# ─────────────────────────────────────────────────────────────────────────────
# Baseline win-rate — catalog-wide, per horizon
# ─────────────────────────────────────────────────────────────────────────────

def catalog_baseline_win_rates(
    all_labels_by_pid: dict[int, dict[int, ForwardLabelLite]],
    horizons: tuple[int, ...] = FORWARD_HORIZONS,
) -> dict[int, float]:
    """Per-horizon mean is_profitable across all catalog patterns.

    Args:
        all_labels_by_pid: output of
            catalog_reader.bulk_load_forward_labels(conn, all_pattern_ids).
            Outer dict keyed by pattern_instance_id; inner dict keyed
            by horizon_days.
        horizons: tuple of horizons to score. Defaults to
            FORWARD_HORIZONS (5, 7, 10, 15, 20).

    Returns:
        dict[int, float] keyed by horizon; value is the fraction of
        catalog patterns profitable at that horizon. A horizon with
        no labeled patterns returns 0.0 (will trigger the degenerate-
        baseline path in z_score for any sample at that horizon).
    """
    out: dict[int, float] = {}
    for horizon in horizons:
        total = 0
        wins = 0
        for pid_labels in all_labels_by_pid.values():
            if horizon in pid_labels:
                total += 1
                if pid_labels[horizon].is_profitable:
                    wins += 1
        out[horizon] = wins / total if total > 0 else 0.0
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Top-K aggregation — the public entry point
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_top_k(
    top_k_labels_by_pid: dict[int, dict[int, ForwardLabelLite]],
    baseline_win_rates: dict[int, float],
    horizons: tuple[int, ...] = FORWARD_HORIZONS,
) -> dict[int, AggregatedSignalPerHorizon]:
    """Build per-horizon stats for the top-K matches.

    For each horizon, collects the ForwardLabelLite entries present in
    the top-K, computes n_matches / win_rate / mean_return_pct /
    std_return_pct / z_score, and constructs an AggregatedSignalPerHorizon.

    Horizons with no top-K labels are still emitted with n_matches=0
    and zero stats — keeps report shape consistent and lets the signal
    classifier filter on n_matches alone.
    """
    out: dict[int, AggregatedSignalPerHorizon] = {}
    for horizon in horizons:
        labels_at_h: list[ForwardLabelLite] = [
            pid_labels[horizon]
            for pid_labels in top_k_labels_by_pid.values()
            if horizon in pid_labels
        ]
        n = len(labels_at_h)
        if n == 0:
            out[horizon] = AggregatedSignalPerHorizon(
                horizon_days=horizon, n_matches=0, win_rate=0.0,
                mean_return_pct=0.0, std_return_pct=0.0, z_score=0.0,
                certainty_equivalent=None,
            )
            continue
        returns = [lbl.return_pct for lbl in labels_at_h]
        wr = win_rate(labels_at_h)
        mr = _mean(returns)
        sr = _population_std(returns, mr)
        baseline = baseline_win_rates.get(horizon, 0.0)
        z = z_score(wr, n, baseline)
        # Risk-adjusted CE of this horizon's analog returns (decimal space,
        # M-020). Computed unconditionally; CE_GATE_ENABLED governs USE in
        # signal_classifier, not computation here. lambda is provenance --
        # stamped on the report header + ledger record (config v1.7).
        ce = certainty_equivalent(returns, RISK_AVERSION_LAMBDA)
        out[horizon] = AggregatedSignalPerHorizon(
            horizon_days=horizon, n_matches=n, win_rate=wr,
            mean_return_pct=mr, std_return_pct=sr, z_score=z,
            certainty_equivalent=ce,
        )
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Smoke harness — `python domain/aggregator.py`
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # No catalog dependency — fixtures are inline ForwardLabelLite.

    # 1. win_rate on 2-of-3 profitable.
    wr_in = [
        ForwardLabelLite(return_pct=5.0, is_profitable=True),
        ForwardLabelLite(return_pct=3.0, is_profitable=True),
        ForwardLabelLite(return_pct=-1.0, is_profitable=False),
    ]
    print(f"win_rate 2/3:                  {win_rate(wr_in):.4f} (expect 0.6667)")

    # 2. z_score normal case: p=0.8, n=10, baseline=0.5
    #    SE = sqrt(0.25/10) = 0.158113883; z = 0.3 / SE ≈ 1.8974
    print(f"z_score normal (0.8, 10, 0.5): {z_score(0.8, 10, 0.5):.4f} (expect 1.8974)")

    # 3. z_score baseline=1.0, sample=1.0 -> 0.0 (no excess possible)
    print(f"z_score deg base=1, samp=1:    {z_score(1.0, 10, 1.0)} (expect 0.0)")

    # 4. z_score baseline=1.0, sample<1.0 -> -inf
    print(f"z_score deg base=1, samp=0.8:  {z_score(0.8, 10, 1.0)} (expect -inf)")

    # 5. z_score baseline=0.0, sample>0.0 -> +inf
    print(f"z_score deg base=0, samp=0.4:  {z_score(0.4, 10, 0.0)} (expect inf)")

    # 6. z_score n=0 -> 0.0
    print(f"z_score n=0:                   {z_score(0.5, 0, 0.5)} (expect 0.0)")

    # 7. catalog_baseline_win_rates on 4 patterns; horizon 5: 3/4=0.75; 10: 2/4=0.50.
    fixt_all = {
        1: {5: ForwardLabelLite(return_pct=3.0, is_profitable=True),
            10: ForwardLabelLite(return_pct=4.0, is_profitable=True)},
        2: {5: ForwardLabelLite(return_pct=-1.0, is_profitable=False),
            10: ForwardLabelLite(return_pct=2.0, is_profitable=True)},
        3: {5: ForwardLabelLite(return_pct=2.0, is_profitable=True),
            10: ForwardLabelLite(return_pct=-1.0, is_profitable=False)},
        4: {5: ForwardLabelLite(return_pct=1.0, is_profitable=True),
            10: ForwardLabelLite(return_pct=-2.0, is_profitable=False)},
    }
    bl = catalog_baseline_win_rates(fixt_all, horizons=(5, 10, 15))
    print(f"baseline_win_rates:            {bl} "
          f"(expect {{5: 0.75, 10: 0.5, 15: 0.0}})")

    # 8. aggregate_top_k: use 3-of-4 as top-K against the same baseline.
    top_k = {pid: fixt_all[pid] for pid in (1, 2, 3)}
    per_h = aggregate_top_k(top_k, bl, horizons=(5, 10, 15))
    print("aggregate_top_k:")
    for h in (5, 10, 15):
        s = per_h[h]
        print(f"  h={h}: n={s.n_matches} wr={s.win_rate:.4f} "
              f"mean={s.mean_return_pct:.4f} std={s.std_return_pct:.4f} "
              f"z={s.z_score:.4f}")
    print("  expect h=5: n=3 wr=0.6667 mean=1.3333 std=1.6997 z=-0.3333")
    print("  expect h=10: n=3 wr=0.6667 mean=1.6667 std=2.0548 z=0.5774")
    print("  expect h=15: n=0 wr=0.0 mean=0.0 std=0.0 z=0.0")
