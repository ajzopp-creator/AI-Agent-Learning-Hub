"""
PEH handoff script -- run P_400's known-bugs regression suite, which now
includes 5 new WO-P000-E10.001 Phase 2 checks (items 2.3, 2.4, 2.5).
Self-contained; writes its own .done marker on exit (peh-handoff v1.4).
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PY_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
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
        [PYTHON, "tests/test_p400_known_bugs.py"],
        cwd=str(PY_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0:
        print("PASS")
        write_done("PASS", 0)
    else:
        print("FAIL:", "test_p400_known_bugs.py returned nonzero -- see output above")
        write_done("FAIL", result.returncode)
        sys.exit(1)


if __name__ == "__main__":
    main()