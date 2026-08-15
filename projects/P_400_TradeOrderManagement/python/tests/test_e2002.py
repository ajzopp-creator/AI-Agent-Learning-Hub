"""Tests for WO-P400-E2.002: portfolio.py + posture_reader.py + params_reader.py + book_loader.py.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_e2002.py -v

Synthetic fixture tests for domain/portfolio.py logic.
Live filesystem tests for the three infrastructure readers.
"""

from datetime import date, timedelta
from pathlib import Path

from schemas import AccountParams, BookRecord, PostureSnapshot
from domain.portfolio import OPEN_STATUSES, PortfolioState, build_portfolio_state
from infrastructure.posture_reader import read_posture
from infrastructure.params_reader import read_params
from infrastructure.book_loader import load_book


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rec(**kw) -> BookRecord:
    defaults = {"symbol": "AAA", "status": "FILLED", "open_risk_dollars": 100.0}
    defaults.update(kw)
    return BookRecord(**defaults)


# ---------------------------------------------------------------------------
# portfolio.py -- synthetic fixture tests
# ---------------------------------------------------------------------------

def test_empty_book_returns_zero_state():
    state = build_portfolio_state([])
    assert state.heat_dollars == 0.0
    assert state.open_position_count == 0
    assert state.realized_day_loss_dollars == 0.0


def test_heat_sums_open_records_only():
    records = [
        _rec(symbol="AAA", status="FILLED", open_risk_dollars=200.0),
        _rec(symbol="BBB", status="TRAILING", open_risk_dollars=150.0),
        _rec(symbol="CCC", status="CLOSED", open_risk_dollars=0.0, realized_pnl=-300.0),
    ]
    state = build_portfolio_state(records)
    assert state.heat_dollars == 350.0
    assert state.open_position_count == 2


def test_all_open_statuses_count():
    records = [_rec(symbol=s, status=s) for s in OPEN_STATUSES]
    state = build_portfolio_state(records)
    assert state.open_position_count == len(OPEN_STATUSES)


def test_sector_counts_open_only():
    records = [
        _rec(symbol="AAA", status="FILLED", sector="Technology"),
        _rec(symbol="BBB", status="FILLED", sector="Technology"),
        _rec(symbol="CCC", status="CLOSED", sector="Technology"),
    ]
    state = build_portfolio_state(records)
    assert state.open_sector_counts.get("Technology") == 2


def test_duplicate_detection_case_insensitive():
    records = [_rec(symbol="AAPL", status="FILLED")]
    state = build_portfolio_state(records)
    assert state.has_duplicate("AAPL") is True
    assert state.has_duplicate("aapl") is True
    assert state.has_duplicate("MSFT") is False


def test_daily_loss_includes_closed_today_only():
    today = date.today()
    yesterday = (today - timedelta(days=1)).isoformat()
    records = [
        _rec(symbol="AAA", status="CLOSED", realized_pnl=-200.0, close_date=today.isoformat()),
        _rec(symbol="BBB", status="CLOSED", realized_pnl=-100.0, close_date=yesterday),
        _rec(symbol="CCC", status="CLOSED", realized_pnl=300.0, close_date=today.isoformat()),
    ]
    state = build_portfolio_state(records, today=today)
    assert state.realized_day_loss_dollars == 200.0


def test_no_sector_field_does_not_crash():
    records = [_rec(symbol="AAA", status="FILLED", sector=None)]
    state = build_portfolio_state(records)
    assert state.open_sector_counts == {}


# ---------------------------------------------------------------------------
# infrastructure readers -- live filesystem tests
# ---------------------------------------------------------------------------

def test_posture_reader_returns_valid_snapshot():
    snap = read_posture()
    assert isinstance(snap, PostureSnapshot)
    assert snap.risk_mode in {"OFF", "CORRECTION", "HALF", "STANDARD", "FULL", "HOT"}
    assert isinstance(snap.avg_posture, float)
    assert snap.timestamp


def test_params_reader_returns_valid_params():
    params = read_params()
    assert isinstance(params, AccountParams)
    assert params.account_balance > 0
    assert params.risk_per_trade > 0
    assert params.max_position > params.risk_per_trade


def test_book_loader_missing_dir_returns_empty(tmp_path):
    records = load_book(book_dir=tmp_path / "nonexistent")
    assert records == []


def test_book_loader_empty_dir_returns_empty(tmp_path):
    records = load_book(book_dir=tmp_path)
    assert records == []


def test_book_loader_parses_valid_record(tmp_path):
    (tmp_path / "20260612_AAPL_P400.md").write_text(
        "---\nsymbol: AAPL\nstatus: FILLED\nopen_risk_dollars: 490.04\n---\n\nBody text.",
        encoding="utf-8",
    )
    records = load_book(book_dir=tmp_path)
    assert len(records) == 1
    assert records[0].symbol == "AAPL"
    assert records[0].open_risk_dollars == 490.04


def test_book_loader_skips_malformed_record(tmp_path):
    (tmp_path / "bad_P400.md").write_text(
        "---\nnot_a_valid_field: oops\n---\n",
        encoding="utf-8",
    )
    records = load_book(book_dir=tmp_path)
    assert records == []
