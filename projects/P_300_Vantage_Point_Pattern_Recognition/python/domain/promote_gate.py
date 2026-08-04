"""
FILE: domain/promote_gate.py
VERSION: 1.0
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    The WO-P300-E5.005 auto-promote decision. Compares a staging
    walk-forward result against its baseline and returns PROMOTE or
    STOP with the reasoning attached.

    PURE. No file IO, no database, no clock beyond the timestamp
    stamped on the verdict. Everything it needs arrives as
    WalkForwardMetrics. That is what makes it exhaustively testable
    without fixtures.

    THREE DISTINCT OUTCOMES, NOT TWO. A gate can pass, fail, or be
    untestable, and collapsing the third into either of the first two
    is how this feature would fail in practice:

      PROMOTE                -- comparison ran, deltas within bounds
      STOP                   -- comparison ran, a delta breached
      PROMOTE + waived flag  -- sample too small to test at 3pp
                                resolution; promoted, and the log says
                                it was never actually tested

    A waived gate is NOT a passed gate. At p~0.69 the standard error
    on a proportion is ~4.8pp at n=100 and ~2.4pp at n=400, so a 3pp
    bar sits inside sampling noise on small batches. Blocking on noise
    would strand a staged batch unpromoted -- precisely the failure
    this WO exists to prevent (the 2026-07-25 batch sat unpromoted for
    three days and was silently overwritten). Promoting while clearly
    recording that nothing was proven is the honest outcome.

    MISMATCHED INPUTS RAISE RATHER THAN RETURNING STOP. If staging is
    not larger than the baseline, the pair is wrong -- reversed,
    duplicated, or stale. Returning STOP would read as "this batch is
    bad" and send the operator to inspect a batch that is probably
    fine, when the real fault is the inputs. Different fault,
    different remediation, so a different failure mode.

CHANGELOG:
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.
"""
from __future__ import annotations

from datetime import datetime

from schemas_promote_gate import (
    GateThresholds, PromoteGateVerdict, WalkForwardMetrics,
)


def _precondition(pre: WalkForwardMetrics, staging: WalkForwardMetrics) -> None:
    """Structural sanity on the pair itself. Raises; never returns STOP.

    Stronger than any timestamp heuristic: a staging corpus that is not
    larger than its baseline cannot be the result of an ingest, whatever
    the file mtimes say.
    """
    if staging.corpus_size <= pre.corpus_size:
        raise ValueError(
            f"staging corpus ({staging.corpus_size}) is not larger than "
            f"baseline ({pre.corpus_size}). The report pair is reversed, "
            f"duplicated, or stale -- this is an input fault, not a batch "
            f"quality result.\n  baseline: {pre.source_path}\n"
            f"  staging:  {staging.source_path}"
        )
    if staging.chosen_rows <= 0 or pre.chosen_rows <= 0:
        raise ValueError(
            "a report has zero chosen-horizon rows -- cannot compare."
        )


def _grade(
    label: str,
    pre_pct: float,
    stg_pct: float,
    stg_n: int,
    max_drop_pp: float,
    min_n: int,
) -> tuple[float, bool, bool, str]:
    """Grade one class. Returns (delta_pp, waived, breached, reason).

    Boundary is inclusive: a drop of EXACTLY max_drop_pp passes. The
    threshold is the largest tolerated regression, not the smallest
    rejected one. Stated explicitly because this is the kind of
    comparison that silently flips during a later refactor.
    """
    delta = stg_pct - pre_pct

    if stg_n < min_n:
        return delta, True, False, (
            f"{label}: WAIVED -- staging n={stg_n} is below the {min_n} "
            f"floor, so a {max_drop_pp}pp bar is inside sampling noise. "
            f"Observed delta {delta:+.2f}pp was NOT tested."
        )

    if delta < -max_drop_pp:
        return delta, False, True, (
            f"{label}: BREACH -- {pre_pct:.2f}% -> {stg_pct:.2f}% "
            f"({delta:+.2f}pp) exceeds the {max_drop_pp}pp limit (n={stg_n})."
        )

    return delta, False, False, (
        f"{label}: OK -- {pre_pct:.2f}% -> {stg_pct:.2f}% "
        f"({delta:+.2f}pp), within the {max_drop_pp}pp limit (n={stg_n})."
    )


def _volume_change_pct(pre_n: int, stg_n: int) -> float:
    if pre_n <= 0:
        return 0.0
    return (stg_n - pre_n) / pre_n * 100.0


def _context_reasons(
    pre: WalkForwardMetrics,
    staging: WalkForwardMetrics,
    thresholds: GateThresholds,
    vol: float,
) -> list[str]:
    """Informational lines. Recorded, never decisive."""
    note = "flagged" if abs(vol) > thresholds.buy_volume_flag_pct else "normal"
    return [
        f"BUY volume: {pre.buy_n} -> {staging.buy_n} ({vol:+.1f}%, {note}"
        f" -- informational only, never blocks).",
        f"Corpus: {pre.corpus_size} -> {staging.corpus_size} "
        f"(+{staging.corpus_size - pre.corpus_size}). Deltas above are "
        f"whole-corpus and cannot be attributed to the new patterns alone.",
    ]


def evaluate_promote_gate(
    pre: WalkForwardMetrics,
    staging: WalkForwardMetrics,
    thresholds: GateThresholds | None = None,
) -> PromoteGateVerdict:
    """Compare staging against baseline. Raises only on a bad pair."""
    thresholds = thresholds or GateThresholds()
    _precondition(pre, staging)

    buy_delta, buy_waived, buy_breach, buy_reason = _grade(
        "BUY precision", pre.buy_precision_pct, staging.buy_precision_pct,
        staging.buy_n, thresholds.max_buy_precision_drop_pp,
        thresholds.min_buy_n,
    )
    pass_delta, pass_waived, pass_breach, pass_reason = _grade(
        "PASS accuracy", pre.pass_accuracy_pct, staging.pass_accuracy_pct,
        staging.pass_n, thresholds.max_pass_accuracy_drop_pp,
        thresholds.min_buy_n,
    )

    vol = _volume_change_pct(pre.buy_n, staging.buy_n)
    reasons = [buy_reason, pass_reason]
    reasons.extend(_context_reasons(pre, staging, thresholds, vol))

    breached = buy_breach or pass_breach
    decision = "STOP" if breached else "PROMOTE"
    if breached:
        reasons.insert(0, "DECISION: STOP -- staging left unpromoted.")
    else:
        reasons.insert(0, "DECISION: PROMOTE.")

    return PromoteGateVerdict(
        decision=decision,
        reasons=reasons,
        pre=pre,
        staging=staging,
        thresholds=thresholds,
        buy_delta_pp=buy_delta,
        pass_delta_pp=pass_delta,
        buy_volume_change_pct=vol,
        small_n_waived=buy_waived or pass_waived,
        evaluated_at=datetime.now(),
    )
