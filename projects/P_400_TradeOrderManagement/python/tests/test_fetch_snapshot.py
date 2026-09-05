"""test_fetch_snapshot.py -- Unit tests for application/fetch_snapshot.py.

New file, WO-P400-E5.005. No dedicated test file existed before this WO --
infrastructure (Schwab calls, spread cache) and market-hours are
monkeypatched so no real credentials or network access are required.

WO-P400-E7.001: _patch_common now patches get_session_state (returns a
session string) instead of is_market_open_now (returned a bool) --
fetch_snapshot.py branches on the three-way session now, not a boolean.
Added extended-hours (pre_market/after_hours) coverage.
"""

import json

import pytest

from application import fetch_snapshot as fs_module
from application.fetch_snapshot import cmd_fetch_snapshot
from schemas import SymbolSpreadEntry

_BARS = [(105.0 + i, 100.0 + i, 102.0 + i) for i in range(20)]  # (high, low, close)
_VOLUMES = [1_000_000 + i * 1000 for i in range(20)]


def _patch_common(monkeypatch, session: str):
    monkeypatch.setattr(fs_module, "get_session_state", lambda now=None: session)
    import infrastructure.schwab_market_data as smd
    monkeypatch.setattr(smd, "get_daily_bars", lambda *a, **k: (_BARS, _VOLUMES))
    return smd


def test_market_open_uses_live_quote_and_records_spread(monkeypatch, tmp_path, capsys):
    smd = _patch_common(monkeypatch, session="regular")
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
    smd = _patch_common(monkeypatch, session="closed")
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
    smd = _patch_common(monkeypatch, session="closed")
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)
    monkeypatch.setattr(fs_module, "get_last_spread", lambda symbol: None)  # never fetched live

    rc = cmd_fetch_snapshot("ZZZZ")
    assert rc == 1
    assert not (tmp_path / "snapshot_ZZZZ.json").exists()


def test_market_closed_no_bars_errors_no_file(monkeypatch, tmp_path):
    _patch_common(monkeypatch, session="closed")
    import infrastructure.schwab_market_data as smd
    monkeypatch.setattr(smd, "get_daily_bars", lambda *a, **k: ([], []))
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)

    rc = cmd_fetch_snapshot("ZZZZ")
    assert rc == 1
    assert not (tmp_path / "snapshot_ZZZZ.json").exists()


# --- WO-P400-E7.001: extended-hours (pre_market / after_hours) -------------

@pytest.mark.parametrize("session", ["pre_market", "after_hours"])
def test_extended_hours_uses_extended_quote(monkeypatch, tmp_path, session):
    smd = _patch_common(monkeypatch, session=session)
    monkeypatch.setattr(smd, "get_extended_quote_data", lambda *a, **k: {
        "price": 118.20, "bid": 118.00, "ask": 118.40, "today_volume": 12000,
    })
    monkeypatch.setattr(smd, "get_quote_data",
                         lambda *a, **k: pytest.fail("regular quote called during extended session"))
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)

    rc = cmd_fetch_snapshot("AAPL")
    assert rc == 0

    out = json.loads((tmp_path / "snapshot_AAPL.json").read_text())
    assert out["price_basis"] == "extended"
    assert out["data_source"] == "schwab_api_extended"
    assert out["market_open"] is False
    assert out["price"] == 118.20
    assert out["bid"] == 118.00 and out["ask"] == 118.40
    assert out["today_volume"] == 12000


def test_extended_hours_no_extended_quote_errors_no_file(monkeypatch, tmp_path):
    # No live extended quote available (e.g. never fetched, or Schwab has
    # no extended session for this symbol) -- fail loud, never fall back
    # to close+cached-spread silently. Symmetric with the closed-market
    # "no cached spread" failure mode.
    smd = _patch_common(monkeypatch, session="after_hours")
    monkeypatch.setattr(smd, "get_extended_quote_data", lambda *a, **k: None)
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)

    rc = cmd_fetch_snapshot("ZZZZ")
    assert rc == 1
    assert not (tmp_path / "snapshot_ZZZZ.json").exists()


def test_extended_hours_does_not_touch_last_spread_cache(monkeypatch, tmp_path):
    # Extended-basis snapshots price off a live extended quote directly --
    # unlike the regular-session path, there is no half-spread to record
    # for later reuse (record_live_spread must not be called).
    smd = _patch_common(monkeypatch, session="pre_market")
    monkeypatch.setattr(smd, "get_extended_quote_data", lambda *a, **k: {
        "price": 118.20, "bid": 118.00, "ask": 118.40, "today_volume": None,
    })
    monkeypatch.setattr(fs_module, "PYTHON_DIR", tmp_path)
    monkeypatch.setattr(fs_module, "record_live_spread",
                         lambda *a, **k: pytest.fail("record_live_spread called during extended session"))

    rc = cmd_fetch_snapshot("AAPL")
    assert rc == 0