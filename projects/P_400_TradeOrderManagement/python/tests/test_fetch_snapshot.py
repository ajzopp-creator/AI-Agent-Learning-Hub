"""test_fetch_snapshot.py -- Unit tests for application/fetch_snapshot.py.

New file, WO-P400-E5.005. No dedicated test file existed before this WO --
infrastructure (Schwab calls, spread cache) and market-hours are
monkeypatched so no real credentials or network access are required.
"""

import json

import pytest

from application import fetch_snapshot as fs_module
from application.fetch_snapshot import cmd_fetch_snapshot
from schemas import SymbolSpreadEntry

_BARS = [(105.0 + i, 100.0 + i, 102.0 + i) for i in range(20)]  # (high, low, close)
_VOLUMES = [1_000_000 + i * 1000 for i in range(20)]


def _patch_common(monkeypatch, market_open: bool):
    monkeypatch.setattr(fs_module, "is_market_open_now", lambda now=None: market_open)
    import infrastructure.schwab_market_data as smd
    monkeypatch.setattr(smd, "get_daily_bars", lambda *a, **k: (_BARS, _VOLUMES))
    return smd


def test_market_open_uses_live_quote_and_records_spread(monkeypatch, tmp_path, capsys):
    smd = _patch_common(monkeypatch, market_open=True)
    monkeypatch.setattr(smd, "get_quote_data", lambda *a, **k: {
        "price": 121.50, "bid": 121.45, "ask": 121.55, "today_volume": 500000,
    })
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)

    recorded = {}
    monkeypatch.setattr(fs_module, "record_live_spread",
                         lambda symbol, half_spread, price, observed_at:
                         recorded.update(symbol=symbol, half_spread=half_spread, price=price))

    rc = cmd_fetch_snapshot("AAPL")
    assert rc == 0

    out = json.loads((tmp_path / "snapshot_AAPL.json").read_text())
    assert out["price_basis"] == "live"
    assert out["data_source"] == "schwab_api"
    assert out["market_open"] is True
    assert out["bid"] == 121.45 and out["ask"] == 121.55

    # Real spread recorded for the next closed-market fetch to reuse.
    assert recorded["symbol"] == "AAPL"
    assert recorded["half_spread"] == pytest.approx(0.05)
    assert recorded["price"] == 121.50


def test_market_closed_reuses_cached_live_spread(monkeypatch, tmp_path, capsys):
    smd = _patch_common(monkeypatch, market_open=False)
    monkeypatch.setattr(smd, "get_quote_data",
                         lambda *a, **k: pytest.fail("live quote called while market closed"))
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)
    monkeypatch.setattr(fs_module, "get_last_spread",
                         lambda symbol: SymbolSpreadEntry(
                             half_spread=0.10, price=118.0, observed_at="2026-08-10T15:30:00Z"))

    rc = cmd_fetch_snapshot("AAPL")
    assert rc == 0

    out = json.loads((tmp_path / "snapshot_AAPL.json").read_text())
    expected_close = _BARS[-1][2]
    assert out["price_basis"] == "close"
    assert out["data_source"] == "schwab_api_close"
    assert out["market_open"] is False
    assert out["price"] == expected_close
    # Real, previously observed spread -- not zero, not synthetic.
    assert out["bid"] == pytest.approx(expected_close - 0.10)
    assert out["ask"] == pytest.approx(expected_close + 0.10)
    assert out["today_volume"] is None

    captured = capsys.readouterr()
    assert "Market closed" in captured.out
    assert "half_spread=0.1000" in captured.out


def test_market_closed_no_cached_spread_errors_no_file(monkeypatch, tmp_path):
    smd = _patch_common(monkeypatch, market_open=False)
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)
    monkeypatch.setattr(fs_module, "get_last_spread", lambda symbol: None)  # never fetched live

    rc = cmd_fetch_snapshot("ZZZZ")
    assert rc == 1
    assert not (tmp_path / "snapshot_ZZZZ.json").exists()


def test_market_closed_no_bars_errors_no_file(monkeypatch, tmp_path):
    monkeypatch.setattr(fs_module, "is_market_open_now", lambda now=None: False)
    import infrastructure.schwab_market_data as smd
    monkeypatch.setattr(smd, "get_daily_bars", lambda *a, **k: ([], []))
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)

    rc = cmd_fetch_snapshot("ZZZZ")
    assert rc == 1
    assert not (tmp_path / "snapshot_ZZZZ.json").exists()