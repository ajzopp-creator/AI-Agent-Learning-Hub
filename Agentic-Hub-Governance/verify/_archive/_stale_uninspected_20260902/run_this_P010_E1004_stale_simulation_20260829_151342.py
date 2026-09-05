"""
FILE: run_this_P010_E1004_stale_simulation_20260829_151342.py
VERSION: 1.0
DATE: 2026-08-29
AUTHOR: Anthony Zoppi + Claude
LAYER: verify (PEH handoff, isolated integration test)
DESCRIPTION:
    WO-P010-E1.004 VERIFY item ("simulate a stale grid, confirm flag +
    toast fire and STEP 2 halts") -- completed properly this time: an
    isolated scratch copy of the real entry point, fabricated grid
    files, zero contact with any live P_010 file. This is owner
    verification work, not Independent Review's job (WO_COMPLETION_GATE.md
    -- review re-confirms evidence, it doesn't generate it).

    Copies the REAL P_010_daily_posture_v5.py / grid_freshness_check.py /
    toast_notify.py (unmodified) into a scratch project structure, writes
    two fabricated grid XLSX files dated 5 days old, runs the real script
    there (cwd = scratch python/, so Path(__file__).parent.parent resolves
    to the scratch root, never the live project), and inspects the
    scratch MORNING_RUN_FAILED.flag + P_010_RiskConfig.json it produces.

    NOTE: toast_notify.send_toast is NOT mocked -- this WILL fire a real
    Windows toast ("P_010 Morning Run FAILED"). That's the actual thing
    being verified, not a side effect to suppress.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

REAL_PROJECT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_010_Current_Market_Posture"
)
SCRATCH_ROOT = Path(__file__).parent / "e1004_stale_sim_20260829_151342"
SCRATCH_PYTHON = SCRATCH_ROOT / "python"
SCRATCH_DATA = SCRATCH_ROOT / "data" / "excel_exports"
PY_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"

FILES_TO_COPY = [
    "P_010_daily_posture_v5.py",
    "grid_freshness_check.py",
    "toast_notify.py",
]


def build_scratch_tree() -> None:
    SCRATCH_PYTHON.mkdir(parents=True, exist_ok=True)
    SCRATCH_DATA.mkdir(parents=True, exist_ok=True)
    for fname in FILES_TO_COPY:
        shutil.copy2(REAL_PROJECT / "python" / fname, SCRATCH_PYTHON / fname)
    print(f"scratch tree built: {SCRATCH_ROOT}")


def write_fake_grid(path: Path, stale_date: date) -> None:
    """Minimal fabricated grid matching read_grid_excel()'s expected
    columns, dated old on purpose. Not derived from any real VP export."""
    import pandas as pd

    df = pd.DataFrame([{
        "Date": pd.Timestamp(stale_date),
        "Close\nPrice": 100.0,
        "Predicted\nHigh\nPrice": 102.0,
        "Predicted\nLow\nPrice": 98.0,
        "Predicted\nRange": 4.0,
        "Medium\nTerm\nDifference": 0.5,
        "Long\nTerm\nDifference": 0.5,
        "Short\nTerm\nDifference": 0.5,
    }])
    df.to_excel(path, index=False)


def main() -> int:
    build_scratch_tree()

    today = date.today()
    stale_date = today - timedelta(days=5)
    write_fake_grid(SCRATCH_DATA / "History Grid (SPY)_v3.xlsx", stale_date)
    write_fake_grid(SCRATCH_DATA / "History Grid (QQQ)_v3.xlsx", stale_date)
    print(f"fabricated SPY/QQQ grids written, grid_date={stale_date} "
          f"(today={today}, deliberately 5 days old, no VXX grid --"
          f" script must handle that as it already does in production)")

    flag_path = SCRATCH_ROOT / "MORNING_RUN_FAILED.flag"
    config_path = SCRATCH_ROOT / "P_010_RiskConfig.json"
    if flag_path.exists():
        flag_path.unlink()

    result = subprocess.run(
        [PY_EXE, "P_010_daily_posture_v5.py"],
        cwd=str(SCRATCH_PYTHON),
        capture_output=True, text=True, timeout=120,
    )
    print("--- script stdout ---")
    print(result.stdout)
    if result.stderr:
        print("--- script stderr ---")
        print(result.stderr)
    print(f"--- exit code: {result.returncode} ---")

    flag_fired = flag_path.exists()
    flag_text = flag_path.read_text(encoding="utf-8") if flag_fired else ""
    config_written = config_path.exists()

    print(f"\nMORNING_RUN_FAILED.flag created: {flag_fired}")
    if flag_fired:
        print(f"flag content: {flag_text!r}")
    print(f"P_010_RiskConfig.json still written despite staleness: "
          f"{config_written}")

    ok = (
        flag_fired
        and "STALE GRID DATA" in flag_text
        and "SPY" in flag_text and "QQQ" in flag_text
        and config_written
    )
    print(f"\nVERDICT: {'PASS' if ok else 'FAIL'}")
    print("(toast_notify.send_toast ran live, unmocked -- check for the "
          "actual Windows toast as the other half of this verification)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
