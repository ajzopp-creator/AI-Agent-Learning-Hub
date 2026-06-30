"""
FILE: test_atr.py
VERSION: 1.0
DATE: 2026-06-10
AUTHOR: Anthony Zoppi + Claude
LAYER: domain test (shared hub utility)
DESCRIPTION:
    Regression tests for shared_resources/python_utils/atr.py.

    Proves: True Range picks up both up-gaps and down-gaps; Wilder RMA
    matches a hand-computed value; the sub-period path degrades to a
    simple mean; empty input is 0.0; period < 1 raises.

    Run (p140):
        python shared_resources\\python_utils\\test_atr.py
    Imports via the editable install, so a clean run also confirms the
    shared import path resolves.

CHANGELOG:
    - 2026-06-10 v1.0: Initial release alongside atr.py v1.0.
"""
from __future__ import annotations

import math

from shared_resources.python_utils.atr import compute_atr_wilder, true_range


def test_true_range_up_gap() -> None:
    # prev close (8) below today's low (10): high-vs-prev-close dominates.
    assert true_range(12.0, 10.0, 8.0) == 4.0


def test_true_range_down_gap() -> None:
    # prev close (12) above today's high (9): low-vs-prev-close dominates.
    assert true_range(9.0, 7.0, 12.0) == 5.0


def test_true_range_inside() -> None:
    # prev close inside the bar: plain high - low wins.
    assert true_range(11.0, 9.0, 10.0) == 2.0


def test_sub_period_simple_mean() -> None:
    # 3 bars, period 14 -> simple mean of TRs (2, 6, 4) = 4.0.
    bars = [(10.0, 8.0, 9.0), (15.0, 13.0, 14.0), (12.0, 10.0, 11.0)]
    assert math.isclose(compute_atr_wilder(bars, period=14), 4.0, rel_tol=1e-12)


def test_wilder_hand_computed() -> None:
    # period 3, 5 bars. TRs = [2, 3, 3, 3, 4].
    # seed = (2+3+3)/3 = 8/3; smooth TR3=3 -> 25/9; smooth TR4=4 -> 86/27.
    bars = [
        (10.0, 8.0, 9.0),
        (12.0, 9.0, 11.0),
        (13.0, 10.0, 12.0),
        (11.0, 9.0, 10.0),
        (14.0, 10.0, 13.0),
    ]
    assert math.isclose(compute_atr_wilder(bars, period=3), 86.0 / 27.0, rel_tol=1e-12)


def test_n_equals_period_is_seed() -> None:
    # exactly period bars -> seed only, no smoothing. TRs (2,3,3) -> 8/3.
    bars = [(10.0, 8.0, 9.0), (12.0, 9.0, 11.0), (13.0, 10.0, 12.0)]
    assert math.isclose(compute_atr_wilder(bars, period=3), 8.0 / 3.0, rel_tol=1e-12)


def test_empty_is_zero() -> None:
    assert compute_atr_wilder([]) == 0.0


def test_single_bar_is_range() -> None:
    assert compute_atr_wilder([(10.0, 8.0, 9.0)]) == 2.0


def test_bad_period_raises() -> None:
    try:
        compute_atr_wilder([(10.0, 8.0, 9.0)], period=0)
    except ValueError:
        return
    raise AssertionError("period=0 did not raise ValueError")


def main() -> int:
    tests = [
        test_true_range_up_gap,
        test_true_range_down_gap,
        test_true_range_inside,
        test_sub_period_simple_mean,
        test_wilder_hand_computed,
        test_n_equals_period_is_seed,
        test_empty_is_zero,
        test_single_bar_is_range,
        test_bad_period_raises,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print("PASS " + t.__name__)
        except AssertionError as exc:
            failed += 1
            print("FAIL " + t.__name__ + " -- " + str(exc))
    print("-" * 40)
    print("ATR tests: " + str(len(tests) - failed) + "/" + str(len(tests)) + " passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
