"""
peh verify script -- P_010, WO-P010-E1.003 housekeeping (file split smoke test)
Generated: 2026-08-10 08:11:36
Tests: P_010_write_daily_note.py / P_010_intraday_vp_check_v4.py split into
       note_api_fetchers.py, note_content_builders.py, note_template_engine.py,
       intraday_risk_logic.py -- confirms identical behavior post-split.
Does NOT call main() on either script, does NOT hit yfinance, does NOT write to
P_010_RiskConfig.json, grid_snapshot_latest.json, or the Obsidian vault.
Read-only against today's real config/snapshot files for realistic input shape.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture")
PY_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PY_DIR))

failures = []

def check(label, condition, detail=""):
    if condition:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label} -- {detail}")
        failures.append(label)

print("=" * 70)
print("P_010 FILE-SPLIT SMOKE TEST")
print("=" * 70)

# -- 1. Import check (all 6 modules) -------------------------------------------
try:
    import note_api_fetchers
    import note_content_builders as ncb
    import note_template_engine as nte
    import P_010_write_daily_note as note_writer
    import intraday_risk_logic as irl
    import P_010_intraday_vp_check_v4 as intraday
    check("all 6 modules import cleanly", True)
except Exception as e:
    check("all 6 modules import cleanly", False, str(e))
    done_path = Path(__file__).with_suffix(".py.done")
    done_path.write_text(f"STATUS: FAIL\nEXIT_CODE: 1\nTIMESTAMP: {datetime.now().isoformat()}\n", encoding="utf-8")
    print("FAIL: import failure, cannot continue"); sys.exit(1)

# -- 2. note_content_builders logic (known inputs -> known outputs) -----------
r = ncb.suggest_risk_level("FULL", "NEUTRAL")
check("suggest_risk_level(FULL,NEUTRAL)", r == ("Low", "VP bullish, vol stable"), str(r))

r = ncb.suggest_bias(15.197128, "NEUTRAL")
check("suggest_bias(15.2,NEUTRAL) == Strongly Bullish", r == ("Strongly Bullish", "Strong positive posture"), str(r))

check("fp(1.5) formats as $1.50", ncb.fp(1.5) == "$1.50")
check("fp(None) formats as --", ncb.fp(None) == "--")
check("fc(1.23456) formats as 1.2346", ncb.fc(1.23456) == "1.2346")

# -- 3. note_content_builders against TODAY'S REAL config (read-only) ---------
cfg_path = PROJECT_ROOT / "P_010_RiskConfig.json"
snap_path = PROJECT_ROOT / "grid_snapshot_latest.json"
cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
snap = json.loads(snap_path.read_text(encoding="utf-8")) if snap_path.exists() else {}

try:
    sec5 = ncb.build_section5_block(cfg, datetime.now())
    check("build_section5_block runs on live config, no exception",
          cfg.get("risk_mode", "N/A") in sec5, "risk_mode not found in output")
except Exception as e:
    check("build_section5_block runs on live config, no exception", False, str(e))

try:
    ov = ncb.build_market_overview(cfg, snap)
    check("build_market_overview runs on live config, no exception", "SPY" in ov and "QQQ" in ov)
except Exception as e:
    check("build_market_overview runs on live config, no exception", False, str(e))

# -- 4. note_template_engine wiring (imports content builders correctly) ------
check("note_template_engine.TEMPLATES path resolves",
      str(nte.TEMPLATES).endswith(r"TradingJournal\Templates"), str(nte.TEMPLATES))
try:
    tpath, tver = nte.find_latest_template()
    check("find_latest_template runs, no exception", True)
except Exception as e:
    check("find_latest_template runs, no exception", False, str(e))

# -- 5. note_writer orchestration wiring ---------------------------------------
check("note_writer.RISK_CONFIG points at real project file",
      note_writer.RISK_CONFIG == cfg_path)
check("note_writer imported fetch_scripture from note_api_fetchers",
      note_writer.fetch_scripture is note_api_fetchers.fetch_scripture)
check("note_writer imported process_template from note_template_engine",
      note_writer.process_template is nte.process_template)

# -- 6. intraday_risk_logic (known inputs -> known outputs, PRANGE math) ------
val_above = irl.validate_against_prange(773.26, 780.00, 774.14, 768.87)
check("validate_against_prange: price above pred_high -> above_band",
      val_above["band_status"] == "above_band", val_above["band_status"])

val_in = irl.validate_against_prange(773.26, 771.00, 774.14, 768.87)
check("validate_against_prange: price inside range -> in_band",
      val_in["band_status"] == "in_band", val_in["band_status"])

val_below = irl.validate_against_prange(773.26, 760.00, 774.14, 768.87)
check("validate_against_prange: price below pred_low -> below_band",
      val_below["band_status"] == "below_band", val_below["band_status"])

fm, sig, reason = irl.determine_final_risk_mode("FULL", val_above, val_above)
check("determine_final_risk_mode: FULL + both above_band -> stays FULL, UPGRADE signal",
      fm == "FULL" and sig == "UPGRADE", f"{fm}, {sig}")

fm, sig, reason = irl.determine_final_risk_mode("HALF", val_below, val_below)
check("determine_final_risk_mode: HALF + both below_band -> OFF, DOWNGRADE signal",
      fm == "OFF" and sig == "DOWNGRADE", f"{fm}, {sig}")

fm, sig, reason = irl.determine_final_risk_mode("HALF", val_in, val_in)
check("determine_final_risk_mode: HALF + both in_band -> stays HALF, CONFIRM signal",
      fm == "HALF" and sig == "CONFIRM", f"{fm}, {sig}")

# -- 7. intraday orchestration wiring -------------------------------------------
check("intraday module imported validate_against_prange from intraday_risk_logic",
      intraday.validate_against_prange is irl.validate_against_prange)
check("intraday module imported determine_final_risk_mode from intraday_risk_logic",
      intraday.determine_final_risk_mode is irl.determine_final_risk_mode)

print()
print("=" * 70)

status = "FAIL" if failures else "PASS"
exit_code = 1 if failures else 0
done_path = Path(__file__).with_suffix(".py.done")
done_path.write_text(
    f"STATUS: {status}\n"
    f"EXIT_CODE: {exit_code}\n"
    f"TIMESTAMP: {datetime.now().isoformat()}\n",
    encoding="utf-8"
)

if failures:
    print(f"FAIL: {len(failures)} check(s) failed -- {failures}")
    sys.exit(1)
else:
    print("PASS")
    sys.exit(0)
