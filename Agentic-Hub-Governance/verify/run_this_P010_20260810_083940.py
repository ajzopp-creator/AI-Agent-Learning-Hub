"""
peh verify script -- P_010, WO-P010-E1.003 failure-injection test
Generated: 2026-08-10 08:39:40

Reproduces WO-P010-E1.002's exact failure mode (QQQ grid filename broken --
missing closing paren) against the E1.003 halt/toast/staleness mechanism,
then restores and confirms clean recovery. Matches the WO's own VERIFY
section criteria.

SAFETY: renames the live QQQ grid export for the duration of the test only.
The restore is wrapped in try/finally so it runs even if a check fails or
the script errors -- the file is never left broken. A manifest is written
BEFORE the rename as a manual-recovery fallback if this script itself dies
uncaught (Ctrl+C, process kill, etc.).

Runs the REAL P_010_daily_posture.bat twice (once broken, once restored).
This touches live P_010_RiskConfig.json (creates a timestamped backup first,
same as normal operation) and will fire a real toast notification on the
broken run -- Tony has confirmed this is OK.
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture")
GRID_DIR = PROJECT_ROOT / "data" / "excel_exports"
GOOD_NAME = GRID_DIR / "History Grid (QQQ)_V3.xlsx"
BROKEN_NAME = GRID_DIR / "History Grid (QQQ_V3.xlsx"  # exact WO-P010-E1.002 bug: missing closing paren
BAT_PATH = PROJECT_ROOT / "P_010_daily_posture.bat"
FLAG_PATH = PROJECT_ROOT / "MORNING_RUN_FAILED.flag"
CONFIG_PATH = PROJECT_ROOT / "P_010_RiskConfig.json"
MANIFEST_PATH = PROJECT_ROOT / "_peh_test_restore_manifest.txt"

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label} -- {detail}")
        failures.append(label)


def run_bat():
    """Run the real morning batch, capture combined output, generous timeout
    for Excel reads + market_health (Protocol C sizing: Python+Excel=45s,
    batch=90s -- using 150s ceiling for the full 3-step chain)."""
    result = subprocess.run(
        ["cmd", "/c", str(BAT_PATH)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=150,
    )
    return result.stdout + result.stderr


print("=" * 70)
print("P_010 FAILURE-INJECTION TEST -- WO-P010-E1.003 VERIFY")
print("=" * 70)

# -- 0. Preconditions -----------------------------------------------------------
check("QQQ grid file exists at expected good name (precondition)", GOOD_NAME.exists())
check("No MORNING_RUN_FAILED.flag present before test starts (precondition)", not FLAG_PATH.exists())
if not GOOD_NAME.exists() or FLAG_PATH.exists():
    print("FAIL: preconditions not met, aborting before touching anything")
    Path(__file__).with_suffix(".py.done").write_text(
        f"STATUS: FAIL\nEXIT_CODE: 1\nTIMESTAMP: {datetime.now().isoformat()}\n", encoding="utf-8")
    sys.exit(1)

# -- Write manual-recovery manifest BEFORE any rename ---------------------------
MANIFEST_PATH.write_text(
    f"P_010 peh test in progress -- {datetime.now().isoformat()}\n"
    f"If this file still exists and the test script died, MANUALLY rename:\n"
    f"  FROM: {BROKEN_NAME}\n"
    f"  TO:   {GOOD_NAME}\n"
    f"Then delete this manifest.\n",
    encoding="utf-8"
)

try:
    # -- 1. BREAK: rename QQQ grid to the exact E1.002 bug pattern --------------
    GOOD_NAME.rename(BROKEN_NAME)
    print(f"  Renamed to broken filename: {BROKEN_NAME.name}")

    # -- 2. Run the real batch against broken data -------------------------------
    print("  Running P_010_daily_posture.bat (expect HALT)...")
    output_broken = run_bat()

    check("batch output shows [ERROR] on posture analysis", "[ERROR]" in output_broken)
    check("batch output shows [HALT] before STEP 2", "[HALT]" in output_broken)
    check("MORNING_RUN_FAILED.flag was written", FLAG_PATH.exists())
    if FLAG_PATH.exists():
        flag_content = FLAG_PATH.read_text(encoding="utf-8")
        check("flag content mentions today's date",
              datetime.now().strftime("%Y-%m-%d") in flag_content, flag_content[:100])
        check("flag content is non-empty (has error detail)", len(flag_content.strip()) > 20)

    print()
    print("  >>> Manual check: did a Windows toast/balloon pop up titled")
    print("      'P_010 Morning Run FAILED'? This script cannot verify that")
    print("      itself -- confirm visually and report back to Tony/Claude.")
    print()

finally:
    # -- 3. RESTORE: always runs, even if checks above failed or raised ---------
    if BROKEN_NAME.exists() and not GOOD_NAME.exists():
        BROKEN_NAME.rename(GOOD_NAME)
        print(f"  Restored filename: {GOOD_NAME.name}")
    check("QQQ grid filename restored to good name", GOOD_NAME.exists())
    if MANIFEST_PATH.exists():
        MANIFEST_PATH.unlink()

# -- 4. Re-run clean, confirm recovery -------------------------------------------
print("  Running P_010_daily_posture.bat again (expect clean pass)...")
ts_before_rerun = datetime.now()
output_clean = run_bat()

check("batch output shows [SUCCESS] on posture analysis (clean run)",
      "[SUCCESS] Posture analysis complete." in output_clean)
check("batch output does NOT show [HALT] on clean run", "[HALT]" not in output_clean)
check("MORNING_RUN_FAILED.flag cleared after clean run", not FLAG_PATH.exists())

if CONFIG_PATH.exists():
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cfg_ts = datetime.fromisoformat(cfg.get("timestamp", "1900-01-01T00:00:00"))
    check("P_010_RiskConfig.json timestamp advanced past the broken-run attempt",
          cfg_ts >= ts_before_rerun, f"cfg_ts={cfg_ts}, expected >= {ts_before_rerun}")
    check("qqq_grid_date populated on clean run (not null/error)",
          bool(cfg.get("qqq_grid_date")), str(cfg.get("qqq_grid_date")))
else:
    check("P_010_RiskConfig.json exists after clean run", False, "file missing")

print()
print("=" * 70)
status = "FAIL" if failures else "PASS"
exit_code = 1 if failures else 0
Path(__file__).with_suffix(".py.done").write_text(
    f"STATUS: {status}\nEXIT_CODE: {exit_code}\nTIMESTAMP: {datetime.now().isoformat()}\n",
    encoding="utf-8"
)
if failures:
    print(f"FAIL: {len(failures)} check(s) failed -- {failures}")
    sys.exit(1)
else:
    print("PASS (toast itself needs Tony's visual confirmation -- see note above)")
    sys.exit(0)
