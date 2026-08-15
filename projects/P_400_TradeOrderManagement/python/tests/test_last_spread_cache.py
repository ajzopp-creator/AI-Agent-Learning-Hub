r"""Tests for WO-P400-E5.005: infrastructure/last_spread_cache.py.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest tests\test_last_spread_cache.py -v
"""

from schemas import LastSpreadCache, SymbolSpreadEntry
from infrastructure import last_spread_cache as cache_mod


def test_load_cache_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "LAST_SPREAD_CACHE_PATH", tmp_path / "nope.json")
    cache = cache_mod.load_cache()
    assert cache.entries == {}


def test_save_then_load_roundtrip(tmp_path, monkeypatch):
    path = tmp_path / "cache.json"
    monkeypatch.setattr(cache_mod, "LAST_SPREAD_CACHE_PATH", path)
    cache = LastSpreadCache(entries={
        "AAPL": SymbolSpreadEntry(half_spread=0.05, price=220.10, observed_at="2026-08-10T15:00:00Z"),
    })
    cache_mod.save_cache(cache)
    loaded = cache_mod.load_cache()
    assert loaded.entries["AAPL"].half_spread == 0.05


def test_load_cache_malformed_json_raises(tmp_path, monkeypatch):
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(cache_mod, "LAST_SPREAD_CACHE_PATH", path)
    import pytest
    with pytest.raises(ValueError):
        cache_mod.load_cache()


def test_record_live_spread_then_get(tmp_path, monkeypatch):
    path = tmp_path / "cache.json"
    monkeypatch.setattr(cache_mod, "LAST_SPREAD_CACHE_PATH", path)
    cache_mod.record_live_spread("MSFT", half_spread=0.03, price=410.0, observed_at="2026-08-10T14:00:00Z")
    entry = cache_mod.get_last_spread("MSFT")
    assert entry is not None
    assert entry.half_spread == 0.03
    assert entry.price == 410.0


def test_get_last_spread_unknown_symbol_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(cache_mod, "LAST_SPREAD_CACHE_PATH", tmp_path / "nope.json")
    assert cache_mod.get_last_spread("ZZZZ") is None


def test_record_live_spread_updates_existing_entry(tmp_path, monkeypatch):
    path = tmp_path / "cache.json"
    monkeypatch.setattr(cache_mod, "LAST_SPREAD_CACHE_PATH", path)
    cache_mod.record_live_spread("MSFT", half_spread=0.03, price=410.0, observed_at="2026-08-10T14:00:00Z")
    cache_mod.record_live_spread("MSFT", half_spread=0.07, price=411.5, observed_at="2026-08-10T15:30:00Z")
    entry = cache_mod.get_last_spread("MSFT")
    assert entry.half_spread == 0.07  # latest observation wins, not accumulated