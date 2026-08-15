"""
TEST: signal_emitter dry-run
Validates signal_emitter.emit_signal_packet() with mock data against the
SIGNAL_V2 contract (emitter v2.x). No live vault write — write_to_vault is
monkeypatched. Checks packet assembly + SignalV2 schema validity.

Run from project python/ dir:
  python test_signal_emitter_dry_run.py

Expected output: PASS or FAIL on each step.
"""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

# Add python/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infrastructure.signal_emitter import emit_signal_packet
from shared_resources.python_utils.signal_schemas import SignalV2


def test_signal_emitter_dry_run():
    """Test signal_emitter with mock data (no live vault write)."""
    print("\n" + "=" * 70)
    print("TEST: signal_emitter dry-run")
    print("=" * 70)

    # Step 1: Create temp dir for JSON dump inspection only
    print("\n[1] Creating temp vault root...", end=" ")
    with TemporaryDirectory() as temp_vault:
        temp_vault_path = Path(temp_vault)
        print("✓ PASS")

        captured = {}

        def _fake_write_to_vault(schema_name, data, body="", overwrite=True):
            captured["schema"] = schema_name
            captured["data"] = data
            return True

        # Step 2: Call emit_signal_packet with mock data (SIGNAL_V2 signature)
        print("[2] Calling emit_signal_packet(COHR, 2026-06-07, BUY mock)...", end=" ")
        with patch(
            "shared_resources.python_utils.vault_interface.write_to_vault",
            side_effect=_fake_write_to_vault,
        ):
            success, msg = emit_signal_packet(
                symbol="COHR",
                signal_date="2026-06-07",
                chosen_horizon=10,
                n_matches=15,
                wr=75.0,  # 75% win rate
                mean_ret=3.45,  # +3.45% mean return
                z_score=0.85,
                close_at_signal=51.23,
                atm_at_signal=1.50,
                trailing_volume_30d=2850000,
                signal_source_link=(
                    "trading_journal/TradeOrderManagement/P300/2026-06-07_COHR.md"
                ),
            )

        if not success:
            print(f"✗ FAIL: {msg}")
            return False
        print("✓ PASS")
        print(f"   → {msg}")

        # Step 3: Verify vault interface was called with SIGNAL_V2
        print("[3] Verifying write_to_vault captured SIGNAL_V2 packet...", end=" ")
        if captured.get("schema") != "SIGNAL_V2":
            print(f"✗ FAIL: schema={captured.get('schema')!r}, expected 'SIGNAL_V2'")
            return False
        if not isinstance(captured.get("data"), dict):
            print("✗ FAIL: no packet dict captured")
            return False
        json_data = captured["data"]
        # Persist to temp for inspection (not the live vault)
        dump_path = temp_vault_path / "2026-06-07_COHR_signal_v2.json"
        dump_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")
        print("✓ PASS")
        print(f"   → captured schema=SIGNAL_V2, dump={dump_path}")

        # Step 4: Load dump and re-parse JSON
        print("[4] Loading JSON and parsing...", end=" ")
        try:
            with open(dump_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            print("✓ PASS")
        except Exception as e:
            print(f"✗ FAIL: {e}")
            return False

        # Step 5: Validate against SignalV2 schema (shared_resources)
        print("[5] Validating against SignalV2 schema...", end=" ")
        try:
            packet = SignalV2.model_validate(json_data)
            print("✓ PASS")
        except Exception as e:
            print(f"✗ FAIL: {e}")
            return False

        # Step 6: Check key fields
        print("[6] Checking required fields...", end=" ")
        checks = [
            ("signal_id", packet.signal_id == "P300-2026-06-07-COHR-001"),
            ("symbol", packet.symbol == "COHR"),
            ("signal_source", packet.signal_source == "P_300"),
            ("strategy", packet.strategy == "pattern_analog"),
            ("confidence_level", packet.confidence_level == "HIGH"),  # wr=75 -> HIGH
            ("n_matches in rationale", "15 matches" in packet.context.signal_rationale),
            (
                "signal_source_link",
                packet.signal_metadata.signal_source_link
                == "trading_journal/TradeOrderManagement/P300/2026-06-07_COHR.md",
            ),
        ]

        all_ok = True
        for field, check in checks:
            if not check:
                print(f"\n   ✗ {field}: FAILED")
                all_ok = False

        if not all_ok:
            print("✗ FAIL")
            return False
        print("✓ PASS")

        # Step 7: Display JSON for inspection
        print("\n[7] JSON output (for inspection):")
        print("-" * 70)
        print(json.dumps(json_data, indent=2))
        print("-" * 70)

    print("\n" + "=" * 70)
    print("RESULT: ✓ ALL TESTS PASSED")
    print("=" * 70)
    print("\nNext: Run live test on actual XLSX via P_300_DailyEval_v2.bat")
    print("      Check: trading_journal/TradeOrderManagement/signals/ for JSON files")
    return True


if __name__ == "__main__":
    success = test_signal_emitter_dry_run()
    sys.exit(0 if success else 1)
