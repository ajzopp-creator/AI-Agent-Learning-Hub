"""
PEH handoff script -- WO-P000-E10.001 Phase 3. Runs P_300's two updated
test files (test_eval_scoring.py, test_promote_gate.py) and P_020's new
test_db_reader.py. Self-contained; writes its own .done marker on exit.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"
P300_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")
P020_DB_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database")


def write_done(status: str, exit_code: int) -> None:
    done_path = Path(__file__).with_suffix(".py.done")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    done_path.write_text(
        f"timestamp: {ts}\nstatus: {status}\nexit_code: {exit_code}\n",
        encoding="utf-8",
    )


def run(label, cmd, cwd):
    print(f"\n{'=' * 20} {label} {'=' * 20}")
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode


def main() -> None:
    rc1 = run("P_300 test_eval_scoring.py", [PYTHON, "tests/test_eval_scoring.py"], P300_DIR)
    rc2 = run("P_300 test_promote_gate.py", [PYTHON, "tests/test_promote_gate.py"], P300_DIR)
    rc3 = run("P_020 test_db_reader.py (pytest)", [PYTHON, "-m", "pytest", "tests/test_db_reader.py", "-v"], P020_DB_DIR)

    codes = {"P300_eval_scoring": rc1, "P300_promote_gate": rc2, "P020_db_reader": rc3}
    print("\n" + "=" * 20 + " SUMMARY " + "=" * 20)
    for name, rc in codes.items():
        print(f"{name}: {'PASS' if rc == 0 else 'FAIL'} (exit {rc})")

    if all(rc == 0 for rc in codes.values()):
        print("PASS")
        write_done("PASS", 0)
    else:
        print("FAIL:", "one or more suites returned nonzero -- see output above")
        write_done("FAIL", 1)
        sys.exit(1)


if __name__ == "__main__":
    main()