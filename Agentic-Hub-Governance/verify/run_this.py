"""run_this.py -- PEH verification script for WO-P400-E2.023 (backward-
looking post-earnings stabilization check, MACRO role).

Runs an import smoke check, then the full P_400 pytest suite from
python\, PYTHONPATH set to hub root (matches Tony's normal invocation
pattern). Self-contained; never modifies production files.

Ends with 'PASS' on success or 'FAIL: <reason>' + exit(1) on failure.
"""
import os
import subprocess
import sys

HUB_ROOT = r"C:\Users\Trader\AI-Agent-Learning-Hub"
P400_PYTHON_DIR = HUB_ROOT + r"\projects\P_400_TradeOrderManagement\python"
PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"

env = os.environ.copy()
env["PYTHONPATH"] = HUB_ROOT


def main() -> None:
    print("=== IMPORT SMOKE CHECK ===")
    smoke = subprocess.run(
        [PYTHON, "-c",
         "from domain.council import macro_vote; "
         "from application.evaluate_signal import _sessions_since_earnings; "
         "from config import POST_EARNINGS_STABILIZATION_SESSIONS; "
         "from schemas import SnapshotDict; "
         "print('IMPORTS OK')"],
        capture_output=True, text=True, cwd=P400_PYTHON_DIR, env=env,
    )
    print(smoke.stdout)
    print(smoke.stderr)
    if smoke.returncode != 0:
        print("FAIL: import smoke check failed -- see stderr above")
        sys.exit(1)

    print("=== PYTEST (full P_400 suite) ===")
    result = subprocess.run(
        [PYTHON, "-m", "pytest", ".", "-v"],
        capture_output=True, text=True, cwd=P400_PYTHON_DIR, env=env,
    )
    print(result.stdout[-10000:])
    print(result.stderr[-3000:])

    if result.returncode != 0:
        print("FAIL: pytest reported failures -- see output above")
        sys.exit(1)

    print("PASS")


if __name__ == "__main__":
    main()