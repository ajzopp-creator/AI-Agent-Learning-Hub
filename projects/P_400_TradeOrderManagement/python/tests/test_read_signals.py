"""P_400 Signal Reader — standalone tests.

Runs entirely against temp-dir fixtures (WO-P400-E3.008) -- no longer
depends on what happens to be sitting in the live signals folder at the
moment this runs. No pytest dependency required:
    python test_read_signals.py
"""

import json
import tempfile
from pathlib import Path

from domain.packet_classifier import PacketKind, classify
from infrastructure.signal_loader import load_v2_signals
from application.read_signals import read_signals


def test_classify() -> None:
    assert classify("2026-06-08_BATRA_v2.0.json") is PacketKind.V2
    assert classify("2026-06-08_BATRA_signal.json") is PacketKind.LEGACY
    assert classify("notes.md") is PacketKind.UNKNOWN
    print("PASS test_classify")


def _valid_v2_packet() -> dict:
    """One known-good SignalV2 packet, fields confirmed against
    shared_resources/python_utils/signal_schemas.py (WO-P400-E3.008)."""
    return {
        "signal_id": "TEST-2026-07-08-AAA-001",
        "signal_timestamp": "2026-07-08T10:00:00Z",
        "signal_source": "manual",
        "strategy": "dip_buy",
        "symbol": "AAPL",
        "asset_class": "stock",
        "guideline_entry": 50.0,
        "guideline_stop": 48.0,
        "guideline_target": 54.0,
        "signal_horizon": "swing",
        "confidence_level": "MEDIUM",
        "position_size": 100,
        "context": {
            "close_at_signal": 50.0,
            "trailing_volume_30d": 1000000.0,
            "signal_rationale": "Hermetic fixture packet for test_read_signals.py.",
        },
        "signal_metadata": {
            "session_date": "2026-07-08",
            "chart_timeframe": "1D",
            "signal_source_link": "test_fixture",
        },
    }


def test_valid_v2_packet_parses() -> None:
    """Hermetic replacement for the old live-folder check (WO-P400-E3.008).

    The old version of this test asserted against the live SIGNALS_DIR and
    only passed when Tony happened to have an unprocessed packet sitting
    in the vault at the moment pytest ran -- that's a live-state smoke
    check, not a test of the loader. This seeds a temp dir with one
    known-good v2 packet instead, so pass/fail depends only on
    load_v2_signals() behavior, never on what's currently in the vault.
    """
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "2026-07-08_AAPL_v2.0.json").write_text(
            json.dumps(_valid_v2_packet()), encoding="utf-8"
        )
        result = load_v2_signals(d)
        assert len(result.valid) == 1, f"unexpected rejects: {result.rejected}"
        assert result.valid[0].symbol == "AAPL"
        assert not result.rejected
    print("PASS test_valid_v2_packet_parses")


def test_malformed_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        # Missing required fields -> must reject, not repair.
        (d / "bad_v2.0.json").write_text(
            json.dumps({"symbol": "BAD"}), encoding="utf-8"
        )
        # Not even JSON.
        (d / "broken_v2.0.json").write_text("{ not json", encoding="utf-8")
        result = load_v2_signals(d)
        assert len(result.valid) == 0, "malformed packet should not validate"
        assert len(result.rejected) == 2, f"expected 2 rejects, got {len(result.rejected)}"
    print("PASS test_malformed_rejected")


def test_read_signals_summary() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "2026-07-08_AAPL_v2.0.json").write_text(
            json.dumps(_valid_v2_packet()), encoding="utf-8"
        )
        result = read_signals(d)
        assert result.valid_count == 1
        assert result.rejected_count == 0
    print("PASS test_read_signals_summary")


def main() -> int:
    tests = [
        test_classify,
        test_valid_v2_packet_parses,
        test_malformed_rejected,
        test_read_signals_summary,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as exc:
            print(f"FAIL {t.__name__}: {exc}")
    print(f"\n{passed}/{len(tests)} passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    raise SystemExit(main())
