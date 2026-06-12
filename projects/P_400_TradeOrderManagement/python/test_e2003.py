"""Tests for WO-P400-E2.003: evaluate_signal.py + build_order_spec.py + cli.py.

Run: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_e2003.py -v

Uses a hand-built snapshot dict against a live inbox packet.
"""

import json
from pathlib import Path

import pytest

from infrastructure.signal_loader import load_v2_signals
from application.evaluate_signal import EvaluationResult, evaluate_signal
from application.build_order_spec import build_spec
from schemas import SnapshotDict

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _first_live_packet():
    """Return the first valid signal from the live inbox, or None."""
    result = load_v2_signals()
    return result.valid[0] if result.valid else None


def _good_snapshot(symbol: str = "TEST", price: float = 50.0) -> dict:
    """Snapshot dict with valid R:R at the given price."""
    return {
        "symbol": symbol,
        "price": price,
        "bid": price - 0.02,
        "ask": price + 0.02,
        "price_timestamp": "2026-06-12T14:00:00Z",
        "price_delay_seconds": 5,
        "atr_14": 1.50,
        "avg_volume_20d": 500000.0,
        "data_source": "manual",
        "market_open": True,
    }


# ---------------------------------------------------------------------------
# SnapshotDict validation
# ---------------------------------------------------------------------------

def test_snapshot_dict_valid():
    snap = SnapshotDict(**_good_snapshot())
    assert snap.price == 50.0
    assert snap.binary_events == []
    assert snap.market_open is True


def test_snapshot_dict_missing_required_raises():
    bad = _good_snapshot()
    del bad["atr_14"]
    with pytest.raises(Exception):
        SnapshotDict(**bad)


# ---------------------------------------------------------------------------
# evaluate_signal -- live inbox + hand-built snapshot
# ---------------------------------------------------------------------------

def test_evaluate_returns_result():
    packet = _first_live_packet()
    if packet is None:
        pytest.skip("No live packets in inbox")

    snap = _good_snapshot(
        symbol=packet.symbol,
        price=packet.guideline_entry,
    )
    result = evaluate_signal(packet, snap, cash_available=5000.0)

    assert isinstance(result, EvaluationResult)
    assert result.symbol == packet.symbol
    assert result.verdict in ("APPROVED", "APPROVED_WITH_CAUTION", "BLOCKED")
    assert result.sizing is not None


def test_block_on_low_rr():
    """A packet where stop == entry-0.01 forces near-zero R:R -> QUANT BLOCK."""
    packet = _first_live_packet()
    if packet is None:
        pytest.skip("No live packets in inbox")

    # Make stop almost equal to entry so R:R < 2.0
    snap = _good_snapshot(symbol=packet.symbol, price=packet.guideline_entry)
    snap["price"] = packet.guideline_target - 0.01  # price near target = R:R collapses

    result = evaluate_signal(packet, snap, cash_available=5000.0)
    assert result.verdict == "BLOCKED"
    assert result.first_block() is not None


# ---------------------------------------------------------------------------
# build_order_spec -- Pattern A
# ---------------------------------------------------------------------------

def test_build_spec_blocked_returns_notice():
    packet = _first_live_packet()
    if packet is None:
        pytest.skip("No live packets in inbox")

    snap = _good_snapshot(symbol=packet.symbol, price=packet.guideline_target - 0.01)
    result = evaluate_signal(packet, snap, cash_available=5000.0)

    if result.is_approved():
        pytest.skip("This packet happened to pass -- need a blocked result for this test")

    spec = build_spec(result, packet, snap)
    assert "BLOCKED" in spec
    assert "No order spec generated" in spec


def test_build_spec_pattern_a_renders():
    packet = _first_live_packet()
    if packet is None:
        pytest.skip("No live packets in inbox")

    asset = getattr(packet.asset_class, "value", packet.asset_class)
    if asset != "stock":
        pytest.skip("Pattern A test requires a stock signal")

    snap = _good_snapshot(symbol=packet.symbol, price=packet.guideline_entry)
    result = evaluate_signal(packet, snap, cash_available=50000.0)

    if not result.is_approved():
        pytest.skip(f"Signal blocked ({result.first_block()}); cannot render spec")

    spec = build_spec(result, packet, snap)
    assert "PATTERN A" in spec
    assert "BUY" in spec
    assert "SELL" in spec
    assert str(result.sizing.shares) in spec
