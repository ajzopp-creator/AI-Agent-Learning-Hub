"""test_evaluate_signal_spread.py -- Spread plausibility gate tests.

Split out of test_evaluate_signal.py (which was over the 250-line split
trigger) rather than added there -- same pattern as test_tape_price_basis.py
splitting off test_council.py. Covers WO-P400-E4.004 (regular-hours
threshold, moved here unchanged) and WO-P400-E7.001 (separate, wider
threshold for price_basis="extended").
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from shared_resources.python_utils.signal_schemas import SignalV2


# ---------------------------------------------------------------------------
# Helpers (duplicated from test_evaluate_signal.py -- self-contained,
# no cross-test-file imports)
# ---------------------------------------------------------------------------

def _make_packet(entry: float, stop: float, target: float, symbol: str = "TEST") -> SignalV2:
    return SignalV2(
        signal_id=f"P300-2026-06-12-{symbol}-001",
        signal_timestamp="2026-06-12T13:00:00Z",
        signal_source="P_300",
        strategy="pattern_analog",
        symbol=symbol,
        asset_class="stock",
        guideline_entry=entry,
        guideline_stop=stop,
        guideline_target=target,
        signal_horizon="5 trading days",
        confidence_level="HIGH",
        position_size=0,
        context={
            "close_at_signal": entry,
            "trailing_volume_30d": 1000000.0,
            "signal_rationale": "test",
            "atm_at_signal": 1.0,
        },
        signal_metadata={
            "session_date": "2026-06-12",
            "chart_timeframe": "1D",
            "signal_source_link": "test",
        },
    )


def _make_snapshot(price: float, entry: float, stop: float, price_basis: str = "live") -> dict:
    return {
        "symbol": "TEST",
        "price": price,
        "bid": price - 0.01,
        "ask": price + 0.01,
        "price_timestamp": datetime.now(timezone.utc).isoformat(),
        "price_delay_seconds": 5,
        "atr_14": abs(entry - stop),
        "avg_volume_20d": 1000000,
        "data_source": "web",
        "today_volume": None,
        "next_earnings_date": None,
        "binary_events": [],
        "sector": None,
        "iv_rank": None,
        "option_chain_ref": None,
        "market_open": True,
        "guideline_stop_override": None,
        "price_basis": price_basis,
    }


def _mock_infra(posture="STANDARD", balance=32669.72, risk=490.04, max_pos=1633.47):
    """Return patch targets for infra reads."""
    posture_mock = MagicMock(risk_mode=posture, avg_posture=0.0)
    params_mock = MagicMock(
        account_balance=balance,
        risk_per_trade=risk,
        max_position=max_pos,
    )
    records_mock = []
    return posture_mock, params_mock, records_mock


def _run(packet, snap):
    posture_mock, params_mock, records_mock = _mock_infra()
    with patch("application.evaluate_signal.read_posture", return_value=posture_mock), \
         patch("application.evaluate_signal.read_params", return_value=params_mock), \
         patch("application.evaluate_signal.load_book", return_value=records_mock):
        from application.evaluate_signal import evaluate_signal
        return evaluate_signal(packet, snap, cash_available=5000.0)


# ---------------------------------------------------------------------------
# Regular-hours threshold (WO-P400-E4.004, moved unchanged from
# test_evaluate_signal.py)
# ---------------------------------------------------------------------------

def test_spread_too_wide_blocks_before_rr_math():
    """Half-spread > 2.0% of price BLOCKs on SPREAD_TOO_WIDE before any
    R:R computation runs -- CAE fixture, half_spread=$2.34 on price=$25.20
    (spread_pct ~9.3%), found live 2026-07-26."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)  # honest 2.0 R:R
    snap = _make_snapshot(price=100.0, entry=100.0, stop=98.0)
    snap["bid"] = 94.0
    snap["ask"] = 106.0  # half_spread=6.0 -> 6.0% of price, over 2.0% threshold

    result = _run(packet, snap)

    assert result.verdict == "BLOCKED"
    assert any("SPREAD_TOO_WIDE" in str(v.reason_code) for v in result.council.votes)
    # Confirms the gate fired before R:R math -- rr_after_drift stays the
    # 0.0 default, never a corrupted negative value from the bad spread.
    assert result.rr_after_drift == 0.0


def test_spread_under_threshold_not_blocked_by_spread_gate():
    """Half-spread just under 2.0% of price does not trip SPREAD_TOO_WIDE
    (setup still R:R 2.0 at guideline, so should proceed past this gate)."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=100.0, entry=100.0, stop=98.0)
    snap["bid"] = 98.2
    snap["ask"] = 101.8  # half_spread=1.8 -> 1.8% of price, under threshold

    result = _run(packet, snap)

    spread_blocks = [c for c in result.council.block_codes if "SPREAD" in c]
    assert spread_blocks == [], f"Unexpected spread block under threshold: {spread_blocks}"


# ---------------------------------------------------------------------------
# Extended-hours threshold (WO-P400-E7.001)
# ---------------------------------------------------------------------------

def test_extended_basis_uses_wider_threshold_not_blocked():
    """A spread that would BLOCK on the regular-hours 2.0% threshold does
    NOT block when price_basis="extended" and it's under the wider
    extended-hours ceiling (5.0%, config.py MAX_PLAUSIBLE_SPREAD_PCT_EXTENDED)."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=100.0, entry=100.0, stop=98.0, price_basis="extended")
    snap["bid"] = 98.0
    snap["ask"] = 102.0  # half_spread=2.0 -> 2.0% of price: over the 2.0% regular
                          # threshold's strict ">" only at exactly 2.0 it would NOT
                          # block on regular either; use a value that actually
                          # differentiates the two thresholds below.

    result = _run(packet, snap)
    spread_blocks = [c for c in result.council.block_codes if "SPREAD" in c]
    assert spread_blocks == [], f"Unexpected spread block under extended threshold: {spread_blocks}"


def test_extended_basis_spread_between_regular_and_extended_threshold_not_blocked():
    """3.5% spread: over the regular-hours 2.0% ceiling, under the
    extended-hours 5.0% ceiling. Must NOT block when price_basis="extended"
    -- this is the case that actually proves the two thresholds are
    independent, not just that "extended" always passes."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=100.0, entry=100.0, stop=98.0, price_basis="extended")
    snap["bid"] = 96.5
    snap["ask"] = 103.5  # half_spread=3.5 -> 3.5% of price

    result = _run(packet, snap)
    spread_blocks = [c for c in result.council.block_codes if "SPREAD" in c]
    assert spread_blocks == [], f"Unexpected spread block at 3.5% under extended threshold: {spread_blocks}"


def test_extended_basis_still_blocks_past_its_own_threshold():
    """A spread wide enough to exceed even the extended-hours 5.0% ceiling
    still BLOCKs -- the wider threshold is not "anything goes" for
    extended-hours data."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)
    snap = _make_snapshot(price=100.0, entry=100.0, stop=98.0, price_basis="extended")
    snap["bid"] = 94.0
    snap["ask"] = 106.0  # half_spread=6.0 -> 6.0% of price, over 5.0% extended threshold

    result = _run(packet, snap)

    assert result.verdict == "BLOCKED"
    assert any("SPREAD_TOO_WIDE" in str(v.reason_code) for v in result.council.votes)


def test_same_spread_blocks_on_regular_but_not_extended():
    """The exact same 3.5%-spread snapshot: BLOCKs when price_basis="live"
    (over the 2.0% regular threshold), passes when price_basis="extended"
    (under the 5.0% extended threshold) -- proves the gate reads
    price_basis, not just a single global constant."""
    packet = _make_packet(entry=100.0, stop=98.0, target=104.0)

    snap_live = _make_snapshot(price=100.0, entry=100.0, stop=98.0, price_basis="live")
    snap_live["bid"] = 96.5
    snap_live["ask"] = 103.5
    result_live = _run(packet, snap_live)
    assert result_live.verdict == "BLOCKED"
    assert any("SPREAD_TOO_WIDE" in str(v.reason_code) for v in result_live.council.votes)

    snap_ext = _make_snapshot(price=100.0, entry=100.0, stop=98.0, price_basis="extended")
    snap_ext["bid"] = 96.5
    snap_ext["ask"] = 103.5
    result_ext = _run(packet, snap_ext)
    spread_blocks = [c for c in result_ext.council.block_codes if "SPREAD" in c]
    assert spread_blocks == [], f"Unexpected spread block on extended basis: {spread_blocks}"