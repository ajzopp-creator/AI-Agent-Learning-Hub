"""Tests for WO-P400-E5.002: application/refresh_earnings_calendar.py.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_refresh_earnings_calendar.py -v
"""

from datetime import date

from infrastructure.earnings_calendar_client import NasdaqRequestError
from application.refresh_earnings_calendar import (
    _collapse_to_entries,
    _date_range,
    _pull_all_records,
)


def test_date_range_spans_lookback_and_lookahead():
    """Window narrowed by WO-P400-E6.004 Revision 2 (2026-08-19) to match
    MACRO's actual gate (3-forward/2-back) -- was 7-day back/83-day forward,
    now 5-day back/7-day forward (config.py
    EARNINGS_CALENDAR_LOOKBACK_BUFFER_DAYS/LOOKAHEAD_DAYS). Stale expected
    values found and fixed same session as WO-P400-E6.003 (2026-08-20)."""
    days = _date_range(today=date(2026, 8, 8))
    assert days[0] == date(2026, 8, 3)     # 5-day backward buffer
    assert days[-1] == date(2026, 8, 15)   # 7-day forward lookahead
    assert len(days) == 13                 # inclusive of both ends


def test_pull_all_records_merges_days(monkeypatch):
    def _fake(day_str):
        return [{"symbol": "AAPL"}] if day_str == "2026-08-08" else []
    monkeypatch.setattr(
        "application.refresh_earnings_calendar.fetch_earnings_for_date", _fake,
    )
    records = _pull_all_records([date(2026, 8, 8), date(2026, 8, 9)])
    assert len(records) == 1
    assert records[0]["symbol"] == "AAPL"
    assert records[0]["date"] == "2026-08-08"   # date stamped onto the row


def test_pull_all_records_one_bad_day_does_not_fail_the_rest(monkeypatch):
    def _fake(day_str):
        if day_str == "2026-08-08":
            raise NasdaqRequestError("blocked")
        return [{"symbol": "MSFT"}]
    monkeypatch.setattr(
        "application.refresh_earnings_calendar.fetch_earnings_for_date", _fake,
    )
    records = _pull_all_records([date(2026, 8, 8), date(2026, 8, 9)])
    assert len(records) == 1
    assert records[0]["symbol"] == "MSFT"


def test_future_only_symbol_gets_next_no_last():
    records = [{"symbol": "aapl", "date": "2026-11-01"}]
    entries = _collapse_to_entries(records, today=date(2026, 8, 8))
    assert entries["AAPL"].next_earnings_date == "2026-11-01"
    assert entries["AAPL"].last_earnings_date is None


def test_past_only_symbol_gets_last_no_next():
    records = [{"symbol": "CGON", "date": "2026-08-06"}]
    entries = _collapse_to_entries(records, today=date(2026, 8, 8))
    assert entries["CGON"].last_earnings_date == "2026-08-06"
    assert entries["CGON"].next_earnings_date is None


def test_symbol_with_both_past_and_future_reports():
    records = [
        {"symbol": "MSFT", "date": "2026-05-01"},   # past
        {"symbol": "MSFT", "date": "2026-11-01"},   # future
    ]
    entries = _collapse_to_entries(records, today=date(2026, 8, 8))
    assert entries["MSFT"].last_earnings_date == "2026-05-01"
    assert entries["MSFT"].next_earnings_date == "2026-11-01"


def test_duplicate_future_dates_keeps_nearest():
    records = [
        {"symbol": "TSLA", "date": "2026-11-15"},
        {"symbol": "TSLA", "date": "2026-10-20"},   # nearer -- should win
    ]
    entries = _collapse_to_entries(records, today=date(2026, 8, 8))
    assert entries["TSLA"].next_earnings_date == "2026-10-20"


def test_malformed_row_skipped_not_raised():
    records = [
        {"symbol": "GOOD", "date": "2026-11-01"},
        {"symbol": "BAD", "date": "not-a-date"},
        {"symbol": None, "date": "2026-11-01"},
        {"date": "2026-11-01"},   # no symbol key
    ]
    entries = _collapse_to_entries(records, today=date(2026, 8, 8))
    assert "GOOD" in entries
    assert "BAD" not in entries
    assert len(entries) == 1


def test_entries_marked_date_confirmed_true():
    records = [{"symbol": "AAPL", "date": "2026-11-01"}]
    entries = _collapse_to_entries(records, today=date(2026, 8, 8))
    assert entries["AAPL"].date_confirmed is True
    assert entries["AAPL"].source == "nasdaq_calendar"
    assert entries["AAPL"].sector is None