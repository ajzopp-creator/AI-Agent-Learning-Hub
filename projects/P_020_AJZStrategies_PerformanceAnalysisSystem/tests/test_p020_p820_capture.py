"""test_p020_p820_capture.py -- Regression tests for the P_820 Order
Signal Capture override (Tony directive, 2026-08-16 P_020 session).

Covers: domain/p820_override.get_override() (forward-window resolution,
structured -- no text parsing needed) and application/p820_capture.
apply_p820_overrides() (the caller applied in ingest_pipeline.py, highest
priority in the chain -- wins over ThinkLog too). No real vault I/O --
lookups are built in-memory from synthetic P820Entry dicts.
"""
import sys
from datetime import date
from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[1] / "python" / "database"
sys.path.insert(0, str(DB_DIR))

from infrastructure.p820_reader import P820Entry
from domain.p820_override import get_override
from application.p820_capture import apply_p820_overrides


def _entry(symbol, why_code, sig_code=None, notes=None) -> P820Entry:
    return P820Entry(
        symbol=symbol, signal_date=date(2026, 1, 1),  # overwritten by lookup key
        why_code=why_code, sig_code=sig_code,
        entry_price=None, stop_price=None, target_price=None, notes=notes,
    )


def _lookup(entries):
    """Build a {(symbol, date): P820Entry} lookup from (symbol, iso_date, entry) tuples."""
    return {(sym, date.fromisoformat(d)): e for sym, d, e in entries}


# ---------------------------------------------------------------------------
# get_override() -- core resolution
# ---------------------------------------------------------------------------

def test_no_entry_returns_none():
    assert get_override("AAPL", "2026-08-10", {}, "TOS_Import") is None


def test_exact_date_match():
    lookup = _lookup([("MRK", "2026-07-13", _entry("MRK", "SNT", "A"))])
    result = get_override("MRK", "2026-07-13", lookup, "TOS_Import")
    assert result.system == "SNT"
    assert result.gap_days == 0


def test_forward_window_one_day_earlier():
    lookup = _lookup([("MRK", "2026-07-12", _entry("MRK", "SNT", "A"))])
    result = get_override("MRK", "2026-07-13", lookup, "TOS_Import")
    assert result is not None
    assert result.gap_days == 1


def test_beyond_window_returns_none():
    lookup = _lookup([("MRK", "2026-07-08", _entry("MRK", "SNT", "A"))])
    assert get_override("MRK", "2026-07-13", lookup, "TOS_Import") is None


def test_overrides_whatever_prior_system_was():
    # P_820 wins over anything -- including a real prior resolution.
    lookup = _lookup([("ASX", "2026-08-10", _entry("ASX", "P_117"))])
    result = get_override("ASX", "2026-08-10", lookup, "P_116")
    assert result.system == "P_117"
    assert result.previous_system == "P_116"


def test_open_vocabulary_new_code_flows_through():
    lookup = _lookup([("XYZ", "2026-08-10", _entry("XYZ", "WSZ"))])
    assert get_override("XYZ", "2026-08-10", lookup, "TOS_Import").system == "WSZ"


def test_empty_why_code_returns_none():
    lookup = _lookup([("AAPL", "2026-08-10", _entry("AAPL", ""))])
    assert get_override("AAPL", "2026-08-10", lookup, "TOS_Import") is None


def test_no_symbol_match_returns_none():
    lookup = _lookup([("AAPL", "2026-08-10", _entry("AAPL", "SNT"))])
    assert get_override("MSFT", "2026-08-10", lookup, "TOS_Import") is None


# ---------------------------------------------------------------------------
# apply_p820_overrides() -- ingest pipeline caller
# ---------------------------------------------------------------------------

def test_apply_overrides_mutates_trades_in_place():
    trades = [
        {"underlying_symbol": "MRK", "open_date": "2026-07-13", "system": "TOS_Import"},
        {"underlying_symbol": "DAL", "open_date": "2026-08-13", "system": "P_116"},
    ]
    lookup = _lookup([("MRK", "2026-07-13", _entry("MRK", "SNT", "A"))])
    audit = []
    count = apply_p820_overrides(trades, lookup, audit)
    assert count == 1
    assert trades[0]["system"] == "SNT"
    assert trades[0]["reason"] == "SNT"
    assert trades[0]["signal_strength"] == "A"
    assert trades[1]["system"] == "P_116"  # untouched, no P_820 entry for DAL
    assert len(audit) == 1
    assert "MRK" in audit[0]


def test_apply_overrides_wins_over_thinklog_style_prior_value():
    # Simulates a trade ThinkLog already resolved -- P_820 must still win.
    trades = [{"underlying_symbol": "ASX", "open_date": "2026-08-10", "system": "P_117"}]
    lookup = _lookup([("ASX", "2026-08-10", _entry("ASX", "P_116"))])
    audit = []
    count = apply_p820_overrides(trades, lookup, audit)
    assert count == 1
    assert trades[0]["system"] == "P_116"


def test_apply_overrides_empty_lookup_is_noop():
    trades = [{"underlying_symbol": "MRK", "open_date": "2026-07-13", "system": "TOS_Import"}]
    audit = []
    count = apply_p820_overrides(trades, {}, audit)
    assert count == 0
    assert trades[0]["system"] == "TOS_Import"
    assert audit == []
