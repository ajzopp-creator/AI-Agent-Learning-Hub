"""
PEH handoff script -- verify the datetime.utcnow() deprecation fix in
db_writer.py plus the two existing regression tests still pass. Self
-contained; writes its own .done marker on exit (peh-handoff v1.4).
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

DB_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database")
PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"


def write_done(status: str, exit_code: int) -> None:
    done_path = Path(__file__).with_suffix(".py.done")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    done_path.write_text(
        f"timestamp: {ts}\nstatus: {status}\nexit_code: {exit_code}\n",
        encoding="utf-8",
    )


def main() -> None:
    result = subprocess.run(
        [PYTHON, "-m", "pytest",
         "tests/test_db_writer.py", "tests/test_spread_matcher.py", "-v"],
        cwd=str(DB_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0:
        print("PASS")
        write_done("PASS", 0)
    else:
        print("FAIL:", "pytest returned nonzero -- see output above")
        write_done("FAIL", result.returncode)
        sys.exit(1)


if __name__ == "__main__":
    main()