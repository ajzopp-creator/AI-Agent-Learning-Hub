"""test_signal_v2_e2e.py — End-to-end check for the JSON signal path (WO-P800-E2.001).

Exercises the REAL consumer contract:
    from shared_resources.python_utils.vault_interface import write_to_vault

Covers:
  1. SIGNAL_V2 stock packet  -> writes YYYY-MM-DD_SYMBOL_v2.0.json
  2. SIGNAL_V2 option packet -> writes, options fields validated
  3. P400SIG legacy packet   -> writes YYYY-MM-DD_SYMBOL_signal.json (dual-window)
  4. Rejection: target <= entry            -> ValueError
  5. Rejection: option missing strike_price -> ValueError

Writes to a clearly-fake symbol (ZZTEST) and deletes its files at the end, so
the real signals/ folder is left clean. Run in your own PowerShell:

  & "C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe" `
    "C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\P_800_Automation_Note_Taking\\python\\tests\\test_signal_v2_e2e.py"
"""

import json
import sys
from pathlib import Path

from shared_resources.python_utils.vault_interface import write_to_vault
from obsidian_writers.config import SIGNALS_DIR

SYMBOL = "ZZTEST"
TS = "2026-06-07T13:45:00Z"
DATE = "2026-06-07"

results: list[tuple[str, bool, str]] = []


def _stock_packet() -> dict:
    return {
        "signal_id": f"TEST-{DATE}-{SYMBOL}-001",
        "signal_timestamp": TS,
        "signal_source": "P_300",
        "strategy": "breakout",
        "symbol": SYMBOL,
        "asset_class": "stock",
        "guideline_entry": 100.0,
        "guideline_stop": 95.0,
        "guideline_target": 112.0,
        "signal_horizon": "3-5 days",
        "confidence_level": "HIGH",
        "position_size": 25,
        "context": {
            "close_at_signal": 99.5,
            "trailing_volume_30d": 1000000,
            "signal_rationale": "e2e stock test",
        },
        "signal_metadata": {
            "session_date": DATE,
            "chart_timeframe": "1D",
            "signal_source_link": "TradeManagement/P300/test.md",
        },
    }


def _option_packet() -> dict:
    pkt = _stock_packet()
    pkt.update({
        "asset_class": "option",
        "strike_price": 105.0,
        "underlying_price": 99.5,
        "option_type": "call",
        "expiration_date": "2026-07-17",
    })
    return pkt


def _v1_packet() -> dict:
    return {
        "signal_id": f"TEST-{DATE}-{SYMBOL}-V1",
        "signal_timestamp": TS,
        "signal_source": "P_115",
        "strategy": "dip_buy",
        "symbol": SYMBOL,
        "guideline_entry": 100.0,
        "guideline_stop": 95.0,
        "guideline_target": 112.0,
        "signal_horizon": "3-5 days",
        "confidence_level": "MEDIUM",
        "context": {
            "close_at_signal": 99.5,
            "trailing_volume_30d": 1000000,
            "signal_rationale": "e2e v1 test",
        },
        "signal_metadata": {
            "session_date": DATE,
            "chart_timeframe": "1D",
            "signal_source_link": "TradeManagement/P115/test.md",
        },
    }


def _record(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))


def test_write_and_readback(name: str, schema: str, packet: dict, expected: str) -> None:
    """Write a packet, confirm the file lands, read it back, check the symbol."""
    try:
        written = write_to_vault(schema, packet)
        path = SIGNALS_DIR / expected
        if not written or not path.exists():
            _record(name, False, f"file not found: {path}")
            return
        loaded = json.loads(path.read_text(encoding="utf-8"))
        ok = loaded.get("symbol") == SYMBOL
        _record(name, ok, "" if ok else "symbol mismatch on readback")
    except Exception as exc:  # noqa: BLE001 - test harness reports any failure
        _record(name, False, f"{type(exc).__name__}: {exc}")


def test_rejection(name: str, packet: dict) -> None:
    """A malformed packet must raise ValueError (no file written)."""
    try:
        write_to_vault("SIGNAL_V2", packet)
        _record(name, False, "expected ValueError, none raised")
    except ValueError:
        _record(name, True)
    except Exception as exc:  # noqa: BLE001
        _record(name, False, f"wrong exception: {type(exc).__name__}: {exc}")


def cleanup() -> None:
    """Remove the test artifacts written to signals/."""
    for f in SIGNALS_DIR.glob(f"{DATE}_{SYMBOL}_*.json"):
        try:
            f.unlink()
        except OSError:
            pass


def main() -> int:
    test_write_and_readback(
        "1. SIGNAL_V2 stock write", "SIGNAL_V2", _stock_packet(),
        f"{DATE}_{SYMBOL}_v2.0.json",
    )
    test_write_and_readback(
        "2. SIGNAL_V2 option write", "SIGNAL_V2", _option_packet(),
        f"{DATE}_{SYMBOL}_v2.0.json",
    )
    test_write_and_readback(
        "3. P400SIG legacy write", "P400SIG", _v1_packet(),
        f"{DATE}_{SYMBOL}_signal.json",
    )

    bad_target = _stock_packet()
    bad_target["guideline_target"] = 90.0   # <= entry
    test_rejection("4. reject target<=entry", bad_target)

    bad_option = _option_packet()
    del bad_option["strike_price"]          # option missing strike
    test_rejection("5. reject option no-strike", bad_option)

    cleanup()

    print("\n" + "=" * 56)
    print("  SIGNAL_V2 END-TO-END TEST  (WO-P800-E2.001)")
    print("=" * 56)
    passed = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        line = f"  [{mark}] {name}"
        if detail:
            line += f"  -- {detail}"
        print(line)
        passed += int(ok)
    print("-" * 56)
    print(f"  {passed}/{len(results)} passed")
    print("=" * 56)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
