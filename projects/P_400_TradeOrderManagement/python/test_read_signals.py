"""P_400 Signal Reader — standalone tests.

Runs against the live signals folder plus a temp dir with a deliberately
malformed packet. No pytest dependency required:
    python test_read_signals.py
"""

import json
import tempfile
from pathlib import Path

from config import SIGNALS_DIR
from domain.packet_classifier import PacketKind, classify
from infrastructure.signal_loader import load_v2_signals
from application.read_signals import read_signals


def test_classify() -> None:
    assert classify("2026-06-08_BATRA_v2.0.json") is PacketKind.V2
    assert classify("2026-06-08_BATRA_signal.json") is PacketKind.LEGACY
    assert classify("notes.md") is PacketKind.UNKNOWN
    print("PASS test_classify")


def test_live_packets_parse() -> None:
    result = load_v2_signals(SIGNALS_DIR)
    assert result.valid, "expected at least one valid live packet"
    assert not result.rejected, f"unexpected rejects: {result.rejected}"
    print(f"PASS test_live_packets_parse ({len(result.valid)} valid)")


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
    result = read_signals(SIGNALS_DIR)
    assert result.valid_count >= 0
    assert result.rejected_count == 0
    print(f"PASS test_read_signals_summary "
          f"(valid={result.valid_count}, legacy={result.legacy_count})")


def main() -> int:
    tests = [
        test_classify,
        test_live_packets_parse,
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
