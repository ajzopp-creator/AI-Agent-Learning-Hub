"""test_market_holidays.py -- WO-P400-E4.006 regression coverage.

Confirms is_market_holiday() against NYSE's published 2026 holiday
calendar (all ten full closures) plus a weekend-shift case in a
different year and the documented New Year's Day non-observance
exception, so the rule-based (not per-year-data) approach is pinned
against real dates, not just internal self-consistency.
"""

from __future__ import annotations

from datetime import date

from domain.market_holidays import is_market_holiday


def test_2026_new_years_day():
    assert is_market_holiday(date(2026, 1, 1)) is True


def test_2026_mlk_day():
    assert is_market_holiday(date(2026, 1, 19)) is True


def test_2026_presidents_day():
    assert is_market_holiday(date(2026, 2, 16)) is True


def test_2026_good_friday():
    # Easter Sunday 2026 is April 5 -- Good Friday (the 3rd) is computed
    # via the Anonymous Gregorian algorithm, not a lookup table.
    assert is_market_holiday(date(2026, 4, 3)) is True


def test_2026_memorial_day():
    assert is_market_holiday(date(2026, 5, 25)) is True


def test_2026_juneteenth():
    assert is_market_holiday(date(2026, 6, 19)) is True


def test_2026_independence_day_observed_friday():
    # July 4 2026 is a Saturday -- NYSE observes it Friday July 3.
    assert is_market_holiday(date(2026, 7, 3)) is True
    # The Saturday itself is not flagged here -- weekend logic already
    # covers it in market_hours.py, this module shouldn't double-count it.
    assert is_market_holiday(date(2026, 7, 4)) is False


def test_2026_labor_day():
    assert is_market_holiday(date(2026, 9, 7)) is True


def test_2026_thanksgiving():
    assert is_market_holiday(date(2026, 11, 26)) is True


def test_2026_christmas():
    assert is_market_holiday(date(2026, 12, 25)) is True


def test_ordinary_weekday_is_not_a_holiday():
    assert is_market_holiday(date(2026, 7, 28)) is False


def test_2027_juneteenth_shifts_to_friday():
    # June 19 2027 is a Saturday -- NYSE has announced it will observe
    # the holiday Friday June 18, 2027. Confirms the weekend-shift rule
    # generalizes across years with zero per-year data to maintain.
    assert is_market_holiday(date(2027, 6, 18)) is True
    assert is_market_holiday(date(2027, 6, 19)) is False


def test_2028_new_years_day_not_observed_on_saturday():
    # January 1 2028 is a Saturday. Unlike other Saturday-landing
    # holidays, NYSE does NOT shift New Year's Day to the preceding
    # Friday -- it simply isn't observed that year.
    assert is_market_holiday(date(2028, 1, 1)) is False
    assert is_market_holiday(date(2027, 12, 31)) is False