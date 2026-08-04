"""
FILE: Agentic-Hub-Governance/verify/run_this.py
PURPOSE: Independent-review re-run for WO-P300-E5.002 / WO-P300-E5.005
         closure. This session wrote none of the code or tests below --
         re-running them fresh is the WO_COMPLETION_GATE Independent
         Review Requirement, not a repeat of the 2026-07-29/07-30
         sessions' own claims (M-054: a claim is not evidence).

Runs all 5 test files relevant to these two WOs, each as a subprocess
via the p140 interpreter, and reports exit codes + tail output.
Read-only: none of these tests touch the real project catalog (all use
tempfile.TemporaryDirectory() or synthetic in-memory fixtures per their
own docstrings).

RUN:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PY = r"C:\Users\Trader\.conda\envs\p140\python.exe"
TESTS_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\tests"
)

TEST_FILES = [
    "test_verify_ingestion.py",       # WO-P300-E5.002/E5.005 shared completion-gate test
    "test_walkforward_report_io.py",  # WO-P300-E5.005
    "test_promote_gate.py",           # WO-P300-E5.005
    "test_promote_marker_io.py",      # WO-P300-E5.005
    "test_cli_registry_inventory.py", # WO-P300-E5.005 (18 commands / 6 modules)
]


def main() -> int:
    print(f"Python: {PY}")
    overall_ok = True
    for fname in TEST_FILES:
        fpath = TESTS_DIR / fname
        print(f"\n{'=' * 70}")
        print(f"RUNNING: {fname}")
        print("=" * 70)
        if not fpath.exists():
            print(f"  MISSING: {fpath}")
            overall_ok = False
            continue
        result = subprocess.run(
            [PY, str(fpath)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        print(result.stdout)
        if result.stderr:
            print("--- stderr ---")
            print(result.stderr)
        print(f"EXIT CODE: {result.returncode}")
        if result.returncode != 0:
            overall_ok = False

    print(f"\n{'=' * 70}")
    if overall_ok:
        print("ALL 5 TEST FILES PASSED (exit 0)")
    else:
        print("AT LEAST ONE TEST FILE FAILED -- see above")
    print("=" * 70)
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
