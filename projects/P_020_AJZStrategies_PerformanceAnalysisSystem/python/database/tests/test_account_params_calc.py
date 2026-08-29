"""Tests for domain.account_params_calc -- pure calculation logic behind
the WO-P020-E1.011 threshold-gated sync. No file I/O in this module, so
no tmp_path fixtures needed here.
"""

from datetime import date

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.account_params_calc import (
    WRITE_THRESHOLD_PCT,
    calculate_derived_params,
    compute_next_review,
    should_write,
)


# ---------------------------------------------------------------------
# should_write
# ---------------------------------------------------------------------

def test_should_write_none_baseline_always_writes():
    """First run / unparseable baseline -- never silently blocks sync."""
    assert should_write(30000.0, None) is True


def test_should_write_zero_baseline_always_writes():
    assert should_write(30000.0, 0.0) is True


def test_should_write_small_move_is_noop():
    """-3.65% move (real 2026-08-22 case: 30203.56 vs 31348.39) stays
    under the 10% gate."""
    assert should_write(30203.56, 31348.39) is False


def test_should_write_exact_threshold_triggers():
    """Exactly WRITE_THRESHOLD_PCT away triggers (>=, not >)."""
    baseline = 31348.39
    exactly_10pct_down = baseline * (1 - WRITE_THRESHOLD_PCT)
    assert should_write(exactly_10pct_down, baseline) is True


def test_should_write_positive_move_triggers():
    """Threshold is symmetric -- a gain also triggers, not just a loss."""
    baseline = 31348.39
    up_12pct = baseline * 1.123
    assert should_write(up_12pct, baseline) is True


def test_should_write_negative_move_triggers():
    baseline = 31348.39
    down_12pct = baseline * 0.877
    assert should_write(down_12pct, baseline) is True


# ---------------------------------------------------------------------
# calculate_derived_params
# ---------------------------------------------------------------------

def test_calculate_derived_params_active_params_values():
    derived = calculate_derived_params(31348.39, 0.015, 0.05)
    assert derived["balance"] == 31348.39
    assert round(derived["risk_per_trade"], 2) == 470.23
    assert round(derived["max_position"], 2) == 1567.42
    assert derived["active_params"]["Account Balance"] == "$31,348.39"
    assert derived["active_params"]["Risk per Trade"] == "1.5% = $470.23"
    assert derived["active_params"]["Max Position (5%)"] == "$1,567.42"


def test_calculate_derived_params_risk_mode_rows_percentages():
    derived = calculate_derived_params(31348.39, 0.015, 0.05)
    rows = derived["risk_mode_rows"]
    assert rows["OFF / CORRECTION"] == ("$235.11 (50%)", "$783.71 (50%)")
    assert rows["HALF"] == ("$352.67 (75%)", "$1,175.56 (75%)")
    assert rows["STANDARD"] == ("$470.23", "$1,567.42")
    assert rows["FULL"] == rows["STANDARD"]


def test_calculate_derived_params_hot_row_never_derived_from_multiplier():
    """HOT's Risk cell is fixed prose, not a percentage of base -- must
    never accidentally become a dollar figure."""
    derived = calculate_derived_params(31348.39, 0.015, 0.05)
    risk_cell, max_cell = derived["risk_mode_rows"]["HOT"]
    assert risk_cell == "Tiered up to 5%"
    assert max_cell == "Up to $1,567.42"


def test_calculate_derived_params_gate_text():
    derived = calculate_derived_params(31348.39, 0.015, 0.05)
    assert derived["gate1_text"] == "Gate 1 (Risk-Based):    $470.23 / (Entry - Stop)"
    assert derived["gate3_text"] == (
        "Gate 3 (Concentration): $1,567.42 max (or premium for options)"
    )


def test_calculate_derived_params_growth_current_row():
    derived = calculate_derived_params(31348.39, 0.015, 0.05)
    assert derived["growth_current_row"] == (
        "| $31,348.39 (current) | $470.23 | $1,567.42 |"
    )


# ---------------------------------------------------------------------
# compute_next_review
# ---------------------------------------------------------------------

def test_compute_next_review_rolls_one_month_forward():
    result = compute_next_review(date(2026, 8, 22))
    assert result == "September 2026 (monthly) or when balance hits $35,000"


def test_compute_next_review_december_rolls_to_january_next_year():
    result = compute_next_review(date(2026, 12, 15))
    assert result == "January 2027 (monthly) or when balance hits $35,000"
