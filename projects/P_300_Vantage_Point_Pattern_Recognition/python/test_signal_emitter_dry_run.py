"""
TEST: signal_emitter dry-run
Validates signal_emitter.emit_signal_packet() with mock data.
No XLSX required. Checks JSON creation and schema validity.

Run from project python/ dir:
  python test_signal_emitter_dry_run.py

Expected output: PASS or FAIL on each step.
"""
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

# Add python/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infrastructure.signal_emitter import emit_signal_packet
from schemas_signal_packet import SignalPacket

def test_signal_emitter_dry_run():
    """Test signal_emitter with mock data."""
    print("\n" + "=" * 70)
    print("TEST: signal_emitter dry-run")
    print("=" * 70)
    
    # Step 1: Create temp vault root
    print("\n[1] Creating temp vault root...", end=" ")
    with TemporaryDirectory() as temp_vault:
        temp_vault_path = Path(temp_vault)
        print("✓ PASS")
        
        # Step 2: Call emit_signal_packet with mock data
        print("[2] Calling emit_signal_packet(COHR, 2026-06-07, BUY mock)...", end=" ")
        success, msg = emit_signal_packet(
            symbol="COHR",
            signal_date="2026-06-07",
            n_matches=15,
            wr=75.0,  # 75% win rate
            mean_ret=3.45,  # +3.45% mean return
            z_score=0.85,
            close_at_signal=51.23,
            atm_at_signal=1.50,
            trailing_volume_30d=2850000,
            signal_source_link="trading_journal/TradeManagement/P300/2026-06-07_COHR.md",
            vault_root=temp_vault_path,
        )
        
        if not success:
            print(f"✗ FAIL: {msg}")
            return False
        print("✓ PASS")
        print(f"   → {msg}")
        
        # Step 3: Verify file exists
        print("[3] Verifying JSON file exists...", end=" ")
        expected_path = temp_vault_path / "TradeOrderManagement" / "signals" / "2026-06-07_COHR_signal.json"
        if not expected_path.exists():
            print(f"✗ FAIL: File not found at {expected_path}")
            return False
        print("✓ PASS")
        print(f"   → {expected_path}")
        
        # Step 4: Load and parse JSON
        print("[4] Loading JSON and parsing...", end=" ")
        try:
            with open(expected_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            print("✓ PASS")
        except Exception as e:
            print(f"✗ FAIL: {e}")
            return False
        
        # Step 5: Validate against SignalPacket schema
        print("[5] Validating against SignalPacket schema...", end=" ")
        try:
            packet = SignalPacket.model_validate(json_data)
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
    print("      Check: C:<vault>/TradeOrderManagement/signals/ for JSON files")
    return True

if __name__ == "__main__":
    success = test_signal_emitter_dry_run()
    sys.exit(0 if success else 1)
