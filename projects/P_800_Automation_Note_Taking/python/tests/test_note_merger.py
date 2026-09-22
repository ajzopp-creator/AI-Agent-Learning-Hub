"""Tests for p400_regenerate.domain.note_merger -- strips P_800's own
injected bookkeeping keys and applies the reconciled outcome onto an
existing P_400 vault note (WO-P400-E6.001, P_800 presentation layer).
No sys.path setup here -- this project's conftest.py already puts
python\\ on sys.path; a local sys.path.insert() is forbidden.
"""

from datetime import date

from p400_regenerate.domain.note_merger import merge_reconciled_order


def _existing_note() -> dict:
    return {
        "ticker": "SPY",
        "signal_date": "2026-09-08",
        "lifecycle_status": "SUBMITTED",
        "entry_date": None,
        "close_date": None,
        "realized_pnl": None,
        "note_version": "3",
        "write_route": "p400_direct",
        "write_route_history": "[]",
        "source": "P400",
        "_note_path": "TradeOrderManagement/P400/2026-09-08_SPY.md",
        "_schema": "P400Record",
    }


def test_merge_strips_p800_bookkeeping_keys():
    order = {"entry_date": date(2026, 9, 8), "close_date": date(2026, 9, 8), "realized_pnl": 3.00}
    merged = merge_reconciled_order(_existing_note(), order)
    for key in ("note_version", "write_route", "write_route_history",
                "source", "_note_path", "_schema"):
        assert key not in merged


def test_merge_preserves_untouched_fields():
    order = {"entry_date": date(2026, 9, 8), "close_date": date(2026, 9, 8), "realized_pnl": 3.00}
    merged = merge_reconciled_order(_existing_note(), order)
    assert merged["ticker"] == "SPY"
    assert merged["signal_date"] == "2026-09-08"


def test_merge_sets_reconciled_outcome():
    order = {"entry_date": date(2026, 9, 8), "close_date": date(2026, 9, 9), "realized_pnl": 3.00}
    merged = merge_reconciled_order(_existing_note(), order)
    assert merged["lifecycle_status"] == "CLOSED"
    assert merged["entry_date"] == "2026-09-08"
    assert merged["close_date"] == "2026-09-09"
    assert merged["realized_pnl"] == 3.00


def test_merge_handles_missing_dates_as_none():
    order = {"realized_pnl": None}
    merged = merge_reconciled_order(_existing_note(), order)
    assert merged["entry_date"] is None
    assert merged["close_date"] is None
