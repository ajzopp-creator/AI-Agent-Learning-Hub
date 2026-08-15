"""Tests for WO-P400-E5.002: infrastructure/earnings_calendar_cache.py.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_earnings_calendar_cache.py -v
"""

from datetime import date, timedelta

import pytest

from schemas import EarningsCalendarCache, EarningsEntry
from infrastructure import earnings_calendar_cache as cache_mod


def _cache(pulled_date: str) -> EarningsCalendarCache:
    return EarningsCalendarCache(
        pulled_date=pulled_date,
        entries={"AAPL": EarningsEntry(symbol="AAPL", next_earnings_date="2026-11-01")},
    )


def test_load_cache_missing_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "EARNINGS_CALENDAR_CACHE_PATH", tmp_path / "nope.json")
    assert cache_mod.load_cache() is None


def test_save_then_load_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "cache.json"
    monkeypatch.setattr(cache_mod, "EARNINGS_CALENDAR_CACHE_PATH", path)
    cache_mod.save_cache(_cache("2026-08-08"))
    loaded = cache_mod.load_cache()
    assert loaded is not None
    assert loaded.pulled_date == "2026-08-08"
    assert loaded.entries["AAPL"].next_earnings_date == "2026-11-01"


def test_load_cache_malformed_json_raises(tmp_path, monkeypatch):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(cache_mod, "EARNINGS_CALENDAR_CACHE_PATH", path)
    with pytest.raises(ValueError):
        cache_mod.load_cache()


def test_load_cache_schema_violation_raises(tmp_path, monkeypatch):
    path = tmp_path / "bad_schema.json"
    path.write_text('{"pulled_date": "2026-08-08"}', encoding="utf-8")  # missing entries
    monkeypatch.setattr(cache_mod, "EARNINGS_CALENDAR_CACHE_PATH", path)
    with pytest.raises(ValueError):
        cache_mod.load_cache()


def test_cache_age_days():
    today = date(2026, 8, 8)
    cache = _cache("2026-07-30")
    assert cache_mod.cache_age_days(cache, today=today) == 9


def test_is_stale_within_threshold():
    today = date(2026, 8, 8)
    cache = _cache((today - timedelta(days=10)).isoformat())
    assert cache_mod.is_stale(cache, today=today) is False


def test_is_stale_past_threshold():
    today = date(2026, 8, 8)
    cache = _cache((today - timedelta(days=40)).isoformat())
    assert cache_mod.is_stale(cache, today=today) is True


def test_is_stale_exactly_at_threshold_not_stale():
    today = date(2026, 8, 8)
    cache = _cache((today - timedelta(days=35)).isoformat())
    assert cache_mod.is_stale(cache, today=today) is False  # > not >=