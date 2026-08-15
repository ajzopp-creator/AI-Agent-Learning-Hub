"""test_earnings_window.py — MACRO earnings-window boundary tests.

Tests earnings_in_window() (domain/earnings_window.py) against the
configured EARNINGS_WINDOW_FORWARD_DAYS / EARNINGS_WINDOW_BACKWARD_DAYS
(config.py, Tony's call 2026-07-28: 3 forward, 2 back). Split into its own
file rather than appended to test_evaluate_signal.py, which was already at
296/300 lines -- no room left there.

All dates computed relative to date.today() -- never hardcoded (see
WO-P400-E2.017 and the E4.006 test-fixture note for why a fixed date breaks
silently on a different day).

Import corrected 2026-08-05 (WO-P000-E13.001 Phase 2): this file imported
_earnings_in_window from application.evaluate_signal, where it lived as a
private helper until WO-P000-E10.001 moved it to domain/earnings_window.py
as a public function. That move did not propagate here, and the stale
module-level import blocked collection of the entire P_400 suite. Signature
and behavior are unchanged -- the move's own docstring records it as "a
move, not a rewrite" -- so only the import path and the name's underscore
prefix changed. No assertion was altered.
"""
from datetime import date, timedelta

from domain.earnings_window import earnings_in_window
from config import EARNINGS_WINDOW_FORWARD_DAYS, EARNINGS_WINDOW_BACKWARD_DAYS


def _iso(delta_days: int) -> str:
    return (date.today() + timedelta(days=delta_days)).isoformat()


def test_none_date_is_clear():
    assert earnings_in_window(None) is False


def test_forward_boundary_in_window():
    assert earnings_in_window(_iso(EARNINGS_WINDOW_FORWARD_DAYS)) is True


def test_forward_boundary_plus_one_is_clear():
    assert earnings_in_window(_iso(EARNINGS_WINDOW_FORWARD_DAYS + 1)) is False


def test_backward_boundary_in_window():
    assert earnings_in_window(_iso(-EARNINGS_WINDOW_BACKWARD_DAYS)) is True


def test_backward_boundary_minus_one_is_clear():
    assert earnings_in_window(_iso(-EARNINGS_WINDOW_BACKWARD_DAYS - 1)) is False


def test_today_is_in_window():
    assert earnings_in_window(_iso(0)) is True


def test_malformed_date_is_clear():
    assert earnings_in_window("not-a-date") is False