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


def test_symbol_absent_from_cache_is_confirmed_clear(monkeypatch):
    """WO-P400-E6.004 Revision 2, 2026-08-19 -- supersedes the original
    WO-P400-E5.002 hard-fail-on-absence design this test used to assert.
    That design's fear (FMP's ~73-symbol coverage meant absence was
    unrelated to earnings timing) no longer applies: the calendar pull
    window (config.py EARNINGS_CALENDAR_LOOKAHEAD_DAYS/LOOKBACK_BUFFER_DAYS,
    now 7/5) was narrowed to match MACRO's actual gate
    (domain/earnings_window.py, fixed 3-forward/2-back). A miss in that
    narrow, gate-matched window now means 'no report in the only window
    that matters' -- a confirmed clear, not raised as EarningsDataMissing.
    Stale test found and fixed same session as WO-P400-E6.003 while
    running the full suite (2026-08-20) -- E6.004 itself was never updated
    to match Revision 2's own behavior change.

    WO-P400-E8.002 (2026-09-15) added a precondition: this confirmed-clear
    path only applies while is_valid_for_current_gate() is True --
    monkeypatched True here deliberately; see
    test_symbol_absent_and_gate_invalid_returns_uncertain below for the
    False case this test used to not distinguish."""
    cache = _cache({})
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: cache)
    monkeypatch.setattr(lookup_mod, "is_stale", lambda c: False)
    monkeypatch.setattr(lookup_mod, "is_valid_for_current_gate", lambda c: True)
    monkeypatch.setattr(lookup_mod, "_lookup_sector", lambda s: None)

    entries = lookup_mod.build_entries_for_symbols(["ZZZZ"])
    assert "ZZZZ" in entries
    assert entries["ZZZZ"].next_earnings_date is None
    assert entries["ZZZZ"].source == lookup_mod.SOURCE_CONFIRMED_CLEAR
    assert entries["ZZZZ"].date_confirmed is True


def test_symbol_absent_and_gate_invalid_returns_uncertain(monkeypatch):
    """WO-P400-E8.002 (found live 2026-09-14, NFLX/EHC/SELF): once the
    cache's own capture window no longer reaches today's gate window,
    'absent from cache' must stop meaning 'confirmed clear' -- it means
    genuinely unknown, and batch_2b_scoring.py's per-symbol skip is the
    correct place to act on that, not a silent clear default here."""
    cache = _cache({})
    monkeypatch.setattr(lookup_mod, "load_cache", lambda: cache)
    monkeypatch.setattr(lookup_mod, "is_stale", lambda c: False)
    monkeypatch.setattr(lookup_mod, "is_valid_for_current_gate", lambda c: False)
    monkeypatch.setattr(lookup_mod, "_lookup_sector", lambda s: None)

    entries = lookup_mod.build_entries_for_symbols(["ZZZZ"])
    assert "ZZZZ" in entries
    assert entries["ZZZZ"].next_earnings_date is None
    assert entries["ZZZZ"].source == lookup_mod.SOURCE_GATE_UNCERTAIN
    assert entries["ZZZZ"].date_confirmed is False


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