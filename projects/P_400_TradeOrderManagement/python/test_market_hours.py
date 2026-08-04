"""test_market_hours.py -- WO-P400-E4.005 regression coverage.

Guards: market_open was hardcoded True in schemas.py (never computed) --
fetch_snapshot.py wrote market_open=true for every symbol regardless of
actual session state, including a full weekend session (2026-07-26,
CLF/AGNC/PSA/CAE all fetched with the market closed). These tests pin the
wall-clock boundary logic so that regression can't silently return.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from domain.market_hours import is_market_open_now

EASTERN = ZoneInfo("America/New_York")


def _et(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, tzinfo=EASTERN)


def test_weekday_midday_is_open():
    # Tuesday, 2026-07-28, 10:00 ET -- ordinary trading hours.
    assert is_market_open_now(_et(2026, 7, 28, 10, 0)) is True


def test_saturday_is_closed():
    # Saturday, 2026-07-25 -- the actual date this bug was found live.
    assert is_market_open_now(_et(2026, 7, 25, 12, 0)) is False


def test_sunday_is_closed():
    # Sunday, 2026-07-26 -- CLF/AGNC/PSA/CAE were all fetched this session
    # with market_open incorrectly true before this fix.
    assert is_market_open_now(_et(2026, 7, 26, 17, 0)) is False


def test_before_open_is_closed():
    # Weekday, 9:29 ET -- one minute before open.
    assert is_market_open_now(_et(2026, 7, 28, 9, 29)) is False


def test_at_open_boundary_is_open():
    # Weekday, exactly 9:30 ET -- inclusive lower bound.
    assert is_market_open_now(_et(2026, 7, 28, 9, 30)) is True


def test_at_close_boundary_is_closed():
    # Weekday, exactly 16:00 ET -- exclusive upper bound (market is shut).
    assert is_market_open_now(_et(2026, 7, 28, 16, 0)) is False


def test_one_minute_before_close_is_open():
    # Weekday, 15:59 ET -- still open.
    assert is_market_open_now(_et(2026, 7, 28, 15, 59)) is True


def test_weekday_holiday_is_closed():
    # Monday, 2026-09-07 -- Labor Day, a real NYSE full closure
    # (WO-P400-E4.006). Before this fix there was no holiday calendar at
    # all, so this would have incorrectly returned True.
    assert is_market_open_now(_et(2026, 9, 7, 12, 0)) is False