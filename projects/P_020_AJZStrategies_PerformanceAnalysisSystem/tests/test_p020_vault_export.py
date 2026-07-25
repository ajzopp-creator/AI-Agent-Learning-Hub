"""
test_p020_vault_export.py -- Regression tests for WO-P020-E1.005.

Tests domain/vault_mapper.build_vault_payload() only -- pure function,
no DB or filesystem needed. Locks in Open Decisions 1-3 from the WO so
they can't silently regress:
  1. outcome passes through unchanged (no vocabulary translation)
  2. only exit_1_price is carried (exit_2/exit_3 dropped)
  3. signal_date/close_date fall back to open_date when no exit yet

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\tests\\
           test_p020_vault_export.py

Run:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest
        tests\\test_p020_vault_export.py -v
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent / "python" / "database"),
)
from domain.vault_mapper import build_vault_payload  # noqa: E402


def _base_row(**overrides):
    """Build a minimal v_trade_summary-shaped row dict for testing."""
    row = {
        "trade_id": 42,
        "account_id": "PAPER",
        "system": "P_118",
        "underlying_symbol": "QBTS",
        "open_date": "2026-07-01",
        "last_exit_date": "2026-07-05",
        "entry_price": 2.32,
        "exit_1_price": 3.14,
        "exit_2_price": 4.20,
        "exit_3_price": None,
        "qty": 4.0,
        "realized_pnl": 82.5,
        "realized_R": 1.5,
        "risk_amount": 55.0,
        "max_hold_days": 4,
        "outcome": "WIN",
        "reason": "EZB",
        "signal_strength": "A",
    }
    row.update(overrides)
    return row


def test_outcome_passes_through_unchanged():
    """Decision 1: WIN/LOSS/SCRATCH/OPEN pass through, no translation."""
    for outcome in ("WIN", "LOSS", "SCRATCH", "OPEN"):
        payload = build_vault_payload(_base_row(outcome=outcome))
        assert payload["outcome"] == outcome


def test_only_exit_1_price_carried():
    """Decision 2: exit_1_price maps to exit_price; exit_2/3 dropped."""
    payload = build_vault_payload(_base_row())
    assert payload["exit_price"] == 3.14
    assert "exit_2_price" not in payload
    assert "exit_3_price" not in payload


def test_close_date_falls_back_to_open_date():
    """Decision 3 support: partial trade with no exit yet still gets a
    valid signal_date so the vault filename builder doesn't crash."""
    payload = build_vault_payload(_base_row(last_exit_date=None))
    assert payload["signal_date"] == "2026-07-01"
    assert payload["close_date"] == "2026-07-01"


def test_signal_date_uses_close_date_when_present():
    payload = build_vault_payload(_base_row())
    assert payload["signal_date"] == "2026-07-05"


def test_field_mapping_matches_wo_table():
    """Spot-check every WO-specified field mapping in one pass."""
    payload = build_vault_payload(_base_row())
    assert payload["symbol"] == "QBTS"
    assert payload["account_id"] == "PAPER"
    assert payload["system"] == "P_118"
    assert payload["why_code"] == "EZB"
    assert payload["sig_code"] == "A"
    assert payload["open_date"] == "2026-07-01"
    assert payload["entry_price"] == 2.32
    assert payload["realized_pnl"] == 82.5
    assert payload["realized_R"] == 1.5
    assert payload["qty"] == 4
    assert payload["risk_amount"] == 55.0
    assert payload["days_held"] == 4
    assert payload["written_by"] == "P_020/write_to_obsidian"


def test_qty_rounds_to_int():
    payload = build_vault_payload(_base_row(qty=3.999))
    assert payload["qty"] == 4
    assert isinstance(payload["qty"], int)


def test_trade_id_passed_through():
    """WO-P800-E3.002 P_020-side fix: trade_id flows into the payload
    so filename_builder.py can use it to disambiguate same-day
    same-symbol collisions."""
    payload = build_vault_payload(_base_row())
    assert payload["trade_id"] == "42"
    assert isinstance(payload["trade_id"], str)


def test_missing_symbol_raises():
    """A row with no symbol must fail loudly, not write UNKNOWN.md."""
    with pytest.raises(ValueError):
        build_vault_payload(_base_row(underlying_symbol=None))
