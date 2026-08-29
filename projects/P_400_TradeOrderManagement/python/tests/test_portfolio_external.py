r"""Tests for WO-P400-E6.003 -- external (non-P_400-managed) position tagging.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest tests\test_portfolio_external.py -v

Covers two files: domain\portfolio.py (heat/count/sector exclusion, symbol
inclusion) and application\audit_book.py (reporting split). audit_book's
_audit_managed/_audit_external take a plain real-positions dict, so no
Schwab mock is needed here.
"""

from datetime import date

from schemas import BookRecord
from domain.portfolio import build_portfolio_state
from application.audit_book import _audit_managed, _audit_external


def _managed(symbol, risk=100.0, sector="Tech"):
    return BookRecord(
        symbol=symbol, status="FILLED", sector=sector,
        open_risk_dollars=risk,
    )


def _external(symbol, source_label="P_116", vehicle="STOCK", qty=1.0):
    return BookRecord(
        symbol=symbol, status="FILLED",
        source_label=source_label, vehicle=vehicle, qty=qty,
    )


def test_external_record_excluded_from_heat_count_sector():
    records = [_managed("V", risk=100.0, sector="Tech"), _external("CSX")]
    state = build_portfolio_state(records, today=date(2026, 8, 20))
    assert state.heat_dollars == 100.0
    assert state.open_position_count == 1
    assert state.open_sector_counts == {"Tech": 1}


def test_external_record_included_in_open_symbols():
    records = [_managed("V"), _external("CSX")]
    state = build_portfolio_state(records, today=date(2026, 8, 20))
    assert state.has_duplicate("CSX")
    assert state.has_duplicate("V")


def test_audit_managed_reports_match_and_no_match(capsys):
    records = [_managed("V"), _managed("DLO")]
    real = {"V": 3}
    mismatches = _audit_managed(records, real)
    out = capsys.readouterr().out
    assert mismatches == 1
    assert "MATCH    V" in out
    assert "NO MATCH DLO" in out


def test_audit_external_confirmed_and_missing(capsys):
    records = [_external("CSX", qty=6), _external("CVNA", qty=1)]
    real = {"CSX": 6}  # CVNA no longer held
    _audit_external(records, real)
    out = capsys.readouterr().out
    assert "Known external, not P_400-managed" in out
    assert "CSX" in out and "confirmed held" in out
    assert "CVNA" in out and "NOT found in broker" in out
