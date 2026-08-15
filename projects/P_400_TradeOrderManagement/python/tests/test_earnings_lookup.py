"""Tests for WO-P400-E5.002: application/earnings_lookup.py.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_earnings_lookup.py -v
"""

import pytest

from schemas import EarningsCalendarCache, EarningsEntry
from infrastructure.earnings_calendar_client import NasdaqRequestError
from application import earnings_lookup as lookup_mod


def _cache(entries=None, pulled_date="2026-08-08"):
    return EarningsCalendarCache(pulled_date=pulled_date, entries=entries or {})


def test_missing_cache_raises(monkeypatch):
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: None)
    with pytest.raises(lookup_mod.EarningsCacheMissing):
        lookup_mod.build_entries_for_symbols(["AAPL"])


def test_cached_symbol_returns_entry_with_live_sector(monkeypatch):
    cache = _cache({"AAPL": EarningsEntry(symbol="AAPL", next_earnings_date="2026-11-01")})
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: cache)
    monkeypatch.setattr(lookup_mod, "is_stale", lambda c: False)
    monkeypatch.setattr(lookup_mod, "_lookup_sector", lambda s: "Health Care")

    entries = lookup_mod.build_entries_for_symbols(["AAPL"])
    assert entries["AAPL"].next_earnings_date == "2026-11-01"
    assert entries["AAPL"].sector == "Health Care"


def test_symbol_absent_from_cache_raises(monkeypatch):
    """WO-P400-E5.002 correction, 2026-08-08: absence is a hard fail, not an
    honest null. Honest-null was the original design under FMP's free tier,
    which capped coverage to ~73 large-cap symbols -- absence there meant
    'not a mega-cap', not 'no earnings', and would have silently disabled
    the MACRO gate. Switched to Nasdaq's full-coverage public calendar, but
    the hard-fail stays as the correct default regardless of source."""
    cache = _cache({})
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: cache)
    monkeypatch.setattr(lookup_mod, "is_stale", lambda c: False)
    monkeypatch.setattr(lookup_mod, "_lookup_sector", lambda s: None)

    with pytest.raises(lookup_mod.EarningsDataMissing):
        lookup_mod.build_entries_for_symbols(["ZZZZ"])


def test_stale_cache_still_returns_entries(monkeypatch, capsys):
    cache = _cache({"AAPL": EarningsEntry(symbol="AAPL")})
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: cache)
    monkeypatch.setattr(lookup_mod, "is_stale", lambda c: True)
    monkeypatch.setattr(lookup_mod, "_lookup_sector", lambda s: None)

    entries = lookup_mod.build_entries_for_symbols(["AAPL"])
    assert "AAPL" in entries
    captured = capsys.readouterr()
    assert "stale" in captured.out.lower()


def test_sector_fetch_failure_degrades_to_none(monkeypatch):
    cache = _cache({"AAPL": EarningsEntry(symbol="AAPL")})
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: cache)
    monkeypatch.setattr(lookup_mod, "is_stale", lambda c: False)

    def _raise(symbol):
        raise NasdaqRequestError("network down")
    monkeypatch.setattr(lookup_mod, "fetch_company_sector", _raise)

    entries = lookup_mod.build_entries_for_symbols(["AAPL"])
    assert entries["AAPL"].sector is None