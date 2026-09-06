"""
P_020 Weekly Update -- Steps 2-5 (Trade Pull, Import, Analyze, Dashboard)
Staged for Claude Code after windows-mcp relay stalled 4+ min on the
Schwab Trade Pull call (Step 2) with zero output produced -- see context.txt.

Mirrors P_020_Weekly_Update.bat exactly, minus the interactive `pause`
lines (which hang headless runs) and Step 0/1 (token check + balance),
both of which already completed successfully this session:
  - Token pre-flight: OK, 2 accounts found (...6348, ...9885)
  - Balance: saved. AJZ6348 total=$27,362.98 cash=$16,140.32 bp=$32,280.64

Run with: C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this_P020_20260905_105257.py
"""
import json
import subprocess
import sys
from pathlib import Path

PY = r"C:\Users\Trader\.conda\envs\p140\python.exe"
PROJ = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem")
DB_DIR = PROJ / "python" / "database"
LAST_RUN_FILE = PROJ / "data" / "api_pulls" / "P_020_last_run.json"
THINKLOG = str(Path("..") / ".." / "data" / "thinklog" / "live" / "P_020_ThinkLog_Live_Current.csv")


def run(step_name, args, cwd):
    print(f"\n=== {step_name} ===")
    print("CMD:", " ".join(args))
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    print("--- STDOUT ---")
    print(result.stdout)
    print("--- STDERR ---")
    print(result.stderr)
    print(f"--- EXIT CODE: {result.returncode} ---")
    return result.returncode


def main():
    last_run_date = json.loads(LAST_RUN_FILE.read_text()).get("last_run_date", "2026-01-01")
    print(f"LAST_RUN={last_run_date}")

    # Step 2: Fresh Schwab trade pull
    rc = run(
        "STEP 2/5: Schwab Trade Pull",
        [PY, str(DB_DIR / ".." / "api" / "P_020_Schwab_Trade_Pull.py"), "--account", "AJZ", "--from", last_run_date],
        DB_DIR,
    )
    if rc != 0:
        print("FAIL: Step 2 (Schwab Trade Pull) -- stopping. Check token / API error above.")
        sys.exit(1)

    # Step 3: Import
    rc = run(
        "STEP 3/5: Import",
        [PY, "P_020_Trade_Manager.py", "import", "--account", "AJZ", "--thinklog", THINKLOG],
        DB_DIR,
    )
    if rc != 0:
        print("FAIL: Step 3 (Import) -- stopping. Check import error above.")
        sys.exit(1)

    # Step 4: Analyze
    rc = run(
        "STEP 4/5: Analyze",
        [PY, "P_020_Trade_Manager.py", "analyze", "--account", "AJZ6348"],
        DB_DIR,
    )
    if rc != 0:
        print("FAIL: Step 4 (Analyze) -- stopping. Check analysis error above.")
        sys.exit(1)

    # Step 5: Dashboard (non-fatal on failure, matches .bat)
    rc = run(
        "STEP 5/5: Dashboard Regeneration",
        [PY, "application/generate_dashboard.py"],
        DB_DIR,
    )
    if rc != 0:
        print("WARNING: Step 5 (Dashboard) failed -- non-fatal, matches .bat behavior.")

    print("\nPASS: Weekly pipeline steps 2-5 complete.")
    print("Check audit_logs\\ for the new P_020_Weekly_Audit_*.txt entry.")


if __name__ == "__main__":
    main()
