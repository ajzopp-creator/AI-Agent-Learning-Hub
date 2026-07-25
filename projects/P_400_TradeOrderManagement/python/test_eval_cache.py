"""test_eval_cache.py -- WO-P400-E3.006: eval_cache read/write round-trip."""

from __future__ import annotations

import shutil

import infrastructure.eval_cache as eval_cache


def _clear(symbol: str) -> None:
    path = eval_cache._cache_path(symbol)
    if path.exists():
        path.unlink()


def test_write_then_read_round_trip():
    _clear("ZZZTEST")
    fields = {
        "symbol": "ZZZTEST", "verdict": "APPROVED", "risk_mode": "OFF",
        "entry_price": 101.96, "stop_price": 90.81, "target_1": 136.25,
        "position_size": 7, "signal_source": "P_300",
        "trade_mode_value": "REAL", "drop_reason": None,
        "signal_date": "2026-07-02",
    }
    assert eval_cache.write_eval_cache("ZZZTEST", fields) is True
    got = eval_cache.read_eval_cache("ZZZTEST")
    assert got == fields
    _clear("ZZZTEST")


def test_read_missing_returns_none():
    _clear("ZZZNOPE")
    assert eval_cache.read_eval_cache("ZZZNOPE") is None


def test_write_overwrites_previous():
    _clear("ZZZOVERWRITE")
    eval_cache.write_eval_cache("ZZZOVERWRITE", {"verdict": "BLOCKED"})
    eval_cache.write_eval_cache("ZZZOVERWRITE", {"verdict": "APPROVED"})
    got = eval_cache.read_eval_cache("ZZZOVERWRITE")
    assert got["verdict"] == "APPROVED"
    _clear("ZZZOVERWRITE")


def test_symbol_case_insensitive():
    _clear("ZZZCASE")
    eval_cache.write_eval_cache("zzzcase", {"verdict": "APPROVED"})
    got = eval_cache.read_eval_cache("ZZZCASE")
    assert got is not None
    assert got["verdict"] == "APPROVED"
    _clear("ZZZCASE")