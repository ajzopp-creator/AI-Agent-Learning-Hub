"""
FILE: python/tests/test_promote_gate.py
VERSION: 1.1
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E5.005's decision logic,
    domain/promote_gate.py.

    The gate is pure, so every case here is constructed directly from
    WalkForwardMetrics values -- no fixtures, no files, no catalog.

    THE TESTS THAT MATTER MOST ARE THE BOUNDARY AND THE WAIVER.

    Boundary: the 3pp threshold is the largest TOLERATED regression,
    not the smallest rejected one. A drop of exactly 3.00pp must
    PROMOTE; 3.01pp must STOP. Both directions are tested because a
    later refactor flipping `<` to `<=` would otherwise pass silently
    while changing production behaviour on every marginal batch.

    Waiver: a waived gate is NOT a passed gate. The waiver test uses a
    catastrophic -20pp drop with a below-floor sample and asserts the
    verdict is still PROMOTE but small_n_waived is True -- proving the
    comparison was skipped rather than passed. If waiver ever collapses
    into a plain PROMOTE, that test fails.

    Also asserts bad input pairs RAISE rather than returning STOP. STOP
    means "this batch is bad" and sends the operator to inspect a batch
    that is probably fine; a reversed or stale report pair is an input
    fault with different remediation.

CHANGELOG:
    - 2026-07-29 v1.1: moved from tests/ (project root) to python/tests/
      to match the python-project-architecture skill's documented
      convention -- the original 2026-07-26 approved plan dropped the
      python/ prefix for this row only (every production-file row in
      the same table had it). _PYTHON_DIR path logic fixed to match
      the new location (_HERE.parent, not _HERE.parent / "python").
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.

RUN (from python/ as cwd, p140 active):
    python tests/test_promote_gate.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain.promote_gate import evaluate_promote_gate  # noqa: E402
from schemas_promote_gate import (  # noqa: E402
    GateThresholds, WalkForwardMetrics,
)


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _m(buy_pct: float, buy_n: int, pass_pct: float, pass_n: int,
       corpus: int = 16801) -> WalkForwardMetrics:
    """Build metrics with exactly-specified percentages.

    Percentages are passed in directly rather than derived from
    correct/n so boundary cases land on exactly-representable floats.
    Real parsed values come from division and will rarely sit exactly
    on the threshold -- the boundary tests below are about the
    comparison's DIRECTION, not float equality.
    """
    return WalkForwardMetrics(
        source_path=f"/synthetic/{corpus}.txt",
        source_mtime=datetime(2026, 7, 28, 6, 0, 0),
        total_rows=corpus * 5,
        chosen_rows=corpus,
        corpus_size=corpus,
        buy_n=buy_n,
        buy_correct=int(round(buy_pct / 100.0 * buy_n)),
        buy_precision_pct=buy_pct,
        pass_n=pass_n,
        pass_correct=int(round(pass_pct / 100.0 * pass_n)),
        pass_accuracy_pct=pass_pct,
        watch_n=100,
    )


def _bigger(m: WalkForwardMetrics) -> int:
    return m.corpus_size + 4446


def _test_clean_pass() -> None:
    """Today's real numbers: BUY -0.06pp, PASS +1.34pp."""
    pre = _m(69.11, 6983, 61.29, 6593, 16801)
    stg = _m(69.05, 9260, 62.63, 7741, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "PROMOTE":
        fail(f"real 2026-07-28 numbers should PROMOTE, got {v.decision}")
    if v.small_n_waived:
        fail("n=9260 must not trigger the small-n waiver")
    ok("real 2026-07-28 batch -> PROMOTE, not waived")


def _test_buy_breach_stops() -> None:
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(64.0, 6000, 61.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "STOP":
        fail(f"BUY -5.00pp should STOP, got {v.decision}")
    ok("BUY -5.00pp -> STOP")


def _test_pass_breach_stops() -> None:
    """PASS must gate independently -- BUY is flat here."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(69.0, 6000, 55.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "STOP":
        fail(f"PASS -6.00pp should STOP even with BUY flat, got {v.decision}")
    ok("PASS -6.00pp with BUY flat -> STOP")


def _test_boundary_exactly_3pp_promotes() -> None:
    """Threshold is the largest TOLERATED drop. Exactly 3.00 passes."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(66.0, 6000, 61.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if abs(v.buy_delta_pp - (-3.0)) > 1e-9:
        fail(f"expected delta exactly -3.0, got {v.buy_delta_pp!r}")
    if v.decision != "PROMOTE":
        fail(f"exactly -3.00pp must PROMOTE (inclusive), got {v.decision}")
    ok("BUY exactly -3.00pp -> PROMOTE (boundary inclusive)")


def _test_boundary_just_over_3pp_stops() -> None:
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(65.9, 6000, 61.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "STOP":
        fail(f"-3.10pp must STOP, got {v.decision}")
    ok("BUY -3.10pp -> STOP (just past the boundary)")


def _test_small_n_waives_not_passes() -> None:
    """A catastrophic drop on a below-floor sample. Must PROMOTE, but
    must be flagged as waived -- untested, not cleared."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(49.0, 120, 41.0, 120, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "PROMOTE":
        fail(f"below-floor sample should PROMOTE (untestable), got {v.decision}")
    if not v.small_n_waived:
        fail("below-floor sample MUST set small_n_waived -- waived != passed")
    if not any("WAIVED" in r for r in v.reasons):
        fail("reasons must state the comparison was waived, not passed")
    ok("BUY n=120 with -20pp drop -> PROMOTE but small_n_waived=True")


def _test_improvement_promotes() -> None:
    pre = _m(65.0, 5000, 58.0, 5000, 16801)
    stg = _m(72.0, 6000, 64.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "PROMOTE" or v.small_n_waived:
        fail(f"improvement should cleanly PROMOTE, got {v.decision}")
    ok("BUY +7.00pp / PASS +6.00pp -> PROMOTE")


def _test_volume_flag_never_blocks() -> None:
    """BUY volume doubling is flagged but must not change the decision."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(69.0, 12000, 61.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if v.decision != "PROMOTE":
        fail(f"volume change must never block, got {v.decision}")
    if v.buy_volume_change_pct <= 50.0:
        fail(f"expected >50% volume change, got {v.buy_volume_change_pct}")
    if not any("flagged" in r for r in v.reasons):
        fail("a >50% volume change should be flagged in reasons")
    ok("BUY volume +140% -> flagged in reasons, still PROMOTE")


def _test_reasons_populated_on_promote() -> None:
    """Reasons must explain WHY it passed, not merely that it did."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(69.0, 6000, 61.0, 6000, 21247)
    v = evaluate_promote_gate(pre, stg)
    if len(v.reasons) < 4:
        fail(f"expected >=4 reason lines on PROMOTE, got {len(v.reasons)}")
    if not any("BUY precision" in r for r in v.reasons):
        fail("reasons must name the BUY comparison even on PROMOTE")
    ok(f"PROMOTE carries {len(v.reasons)} reason lines")


def _expect_raise(fn, label: str) -> None:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        ok(f"{label} -> raised {type(exc).__name__}")
        return
    fail(f"{label} -> NO exception (must raise, not return STOP)")


def _test_reversed_pair_raises() -> None:
    """Staging smaller than baseline: an input fault, not a bad batch."""
    pre = _m(69.0, 5000, 61.0, 5000, 21247)
    stg = _m(69.0, 6000, 61.0, 6000, 16801)
    _expect_raise(lambda: evaluate_promote_gate(pre, stg),
                  "staging corpus smaller than baseline")


def _test_identical_corpus_raises() -> None:
    """Same corpus size means no ingest happened -- stale pair."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(69.0, 5000, 61.0, 5000, 16801)
    _expect_raise(lambda: evaluate_promote_gate(pre, stg),
                  "identical corpus sizes (stale pair)")


def _test_custom_thresholds_respected() -> None:
    """A stricter bar must actually bite."""
    pre = _m(69.0, 5000, 61.0, 5000, 16801)
    stg = _m(67.5, 6000, 61.0, 6000, 21247)
    loose = evaluate_promote_gate(pre, stg)
    strict = evaluate_promote_gate(
        pre, stg, GateThresholds(max_buy_precision_drop_pp=1.0)
    )
    if loose.decision != "PROMOTE":
        fail("-1.50pp should PROMOTE under the default 3pp bar")
    if strict.decision != "STOP":
        fail("-1.50pp should STOP under a 1pp bar")
    ok("-1.50pp -> PROMOTE at 3pp, STOP at 1pp (thresholds honoured)")


def _test_thresholds_reachable_via_cli() -> None:
    """WO-P000-E10.001 item 3.2: thresholds must be reachable from a
    real caller, not just a dead default. cli_commands/promote_gate.py
    builds a real GateThresholds from CLI args (--buy-drop-pp,
    --pass-drop-pp, --min-buy-n) and passes it positionally --
    exactly the shape a keyword-arg-only AST scan misses. The
    domain-level behavior (a custom threshold actually changes the
    verdict) is already proven by _test_custom_thresholds_respected()
    above; this only confirms the CLI wiring specifically.
    """
    src = (_PYTHON_DIR / "cli_commands" / "promote_gate.py").read_text(encoding="utf-8")
    ok_build = "GateThresholds(" in src and "args.buy_drop_pp" in src
    ok_pass = "evaluate_promote_gate(" in src
    if ok_build and ok_pass:
        ok("cli_commands/promote_gate.py builds real GateThresholds from CLI args and passes to evaluate_promote_gate()")
    else:
        fail("cli_commands/promote_gate.py no longer builds/passes GateThresholds from CLI args -- "
             "re-check WO-P000-E10.001 item 3.2")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== decision: pass and fail ===")
    _test_clean_pass()
    _test_improvement_promotes()
    _test_buy_breach_stops()
    _test_pass_breach_stops()

    print("\n=== threshold boundary (inclusive) ===")
    _test_boundary_exactly_3pp_promotes()
    _test_boundary_just_over_3pp_stops()
    _test_custom_thresholds_respected()

    print("\n=== WO-P000-E10.001 item 3.2 -- thresholds reachable via CLI ===")
    _test_thresholds_reachable_via_cli()

    print("\n=== waiver is not a pass ===")
    _test_small_n_waives_not_passes()

    print("\n=== reporting ===")
    _test_volume_flag_never_blocks()
    _test_reasons_populated_on_promote()

    print("\n=== bad input pairs raise, never STOP ===")
    _test_reversed_pair_raises()
    _test_identical_corpus_raises()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
