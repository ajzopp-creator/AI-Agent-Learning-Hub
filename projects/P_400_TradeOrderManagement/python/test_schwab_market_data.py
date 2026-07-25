"""test_schwab_market_data.py -- WO-P400-E4.002. Permanent regression suite
for infrastructure\schwab_market_data.py. Mocks the Schwab client entirely --
no live network calls in this suite (see peh-handoff for the live-connection
verification step, which is a separate manual run, not part of pytest).
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from infrastructure.schwab_market_data import (
    get_chain_candidates,
    get_daily_bars,
    get_quote_data,
)

CONFIG_PATH = Path("fake_config.json")
TOKEN_PATH = Path("fake_token.json")


def _mock_client(status_code: int, json_body: dict) -> MagicMock:
    client = MagicMock()
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_body
    client.get_quote.return_value = resp
    client.get_price_history_every_day.return_value = resp
    client.get_option_chain.return_value = resp
    client.Options.ContractType.CALL = "CALL"
    client.Options.ContractType.PUT = "PUT"
    return client


@patch("infrastructure.schwab_market_data.get_client")
def test_get_quote_data_parses_fields(mock_get_client):
    mock_get_client.return_value = _mock_client(200, {
        "MRCY": {"quote": {"lastPrice": 106.70, "bidPrice": 106.70, "askPrice": 106.95, "totalVolume": 30000}}
    })
    result = get_quote_data(CONFIG_PATH, TOKEN_PATH, "MRCY")
    assert result == {"price": 106.70, "bid": 106.70, "ask": 106.95, "today_volume": 30000}


@patch("infrastructure.schwab_market_data.get_client")
def test_get_quote_data_returns_none_on_non_200(mock_get_client):
    mock_get_client.return_value = _mock_client(500, {})
    assert get_quote_data(CONFIG_PATH, TOKEN_PATH, "MRCY") is None


@patch("infrastructure.schwab_market_data.get_client")
def test_get_quote_data_returns_none_on_missing_symbol_key(mock_get_client):
    mock_get_client.return_value = _mock_client(200, {"OTHER": {}})
    assert get_quote_data(CONFIG_PATH, TOKEN_PATH, "MRCY") is None


@patch("infrastructure.schwab_market_data.get_client")
def test_get_daily_bars_parses_candles_to_bar_tuples(mock_get_client):
    mock_get_client.return_value = _mock_client(200, {"candles": [
        {"open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000, "datetime": 1},
        {"open": 103, "high": 107, "low": 102, "close": 106, "volume": 1200, "datetime": 2},
    ]})
    bars, volumes = get_daily_bars(CONFIG_PATH, TOKEN_PATH, "MRCY")
    assert bars == [(105, 99, 103), (107, 102, 106)]
    assert volumes == [1000, 1200]


@patch("infrastructure.schwab_market_data.get_client")
def test_get_daily_bars_returns_none_on_empty_candles(mock_get_client):
    mock_get_client.return_value = _mock_client(200, {"candles": []})
    assert get_daily_bars(CONFIG_PATH, TOKEN_PATH, "MRCY") is None


@patch("infrastructure.schwab_market_data.get_client")
def test_get_chain_candidates_skips_incomplete_rows(mock_get_client):
    """Never fabricate -- a row missing bid/ask/delta/volatility is dropped,
    not filled with a placeholder."""
    mock_get_client.return_value = _mock_client(200, {"callExpDateMap": {
        "2026-08-23:30": {
            "100.0": [{"bid": 1.0, "ask": 1.1, "delta": 0.50, "volatility": 30.0, "openInterest": 200}],
            "105.0": [{"bid": 1.0, "ask": 1.1, "delta": None, "volatility": 30.0, "openInterest": 200}],
        }
    }})
    candidates = get_chain_candidates(CONFIG_PATH, TOKEN_PATH, "MRCY", "call")
    assert len(candidates) == 1
    assert candidates[0].strike == 100.0
    assert candidates[0].iv == 0.30


@patch("infrastructure.schwab_market_data.get_client")
def test_get_chain_candidates_returns_none_on_empty_map(mock_get_client):
    mock_get_client.return_value = _mock_client(200, {"callExpDateMap": {}})
    assert get_chain_candidates(CONFIG_PATH, TOKEN_PATH, "MRCY", "call") is None


@patch("infrastructure.schwab_market_data.get_client")
def test_get_chain_candidates_returns_none_on_client_exception(mock_get_client):
    """Mocked API failure -- network error, bad symbol, etc. Never raises
    out to the caller; returns None so the application layer can print a
    clear message and exit without writing a partial file."""
    mock_get_client.side_effect = RuntimeError("network error")
    assert get_chain_candidates(CONFIG_PATH, TOKEN_PATH, "MRCY", "call") is None