"""
PEH handoff script -- WO-P000-E10.001 item 3.3, P_805 ranker.py caller
propagation. Self-contained; writes its own .done marker on exit.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"
P805_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")


def write_done(status: str, exit_code: int) -> None:
    done_path = Path(__file__).with_suffix(".py.done")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    done_path.write_text(
        f"timestamp: {ts}\nstatus: {status}\nexit_code: {exit_code}\n",
        encoding="utf-8",
    )


def main() -> None:
    result = subprocess.run(
        [PYTHON, "-m", "unittest", "tests.test_ranker", "-v"],
        cwd=str(P805_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0:
        print("PASS")
        write_done("PASS", 0)
    else:
        print("FAIL:", "test_ranker.py returned nonzero -- see output above")
        write_done("FAIL", result.returncode)
        sys.exit(1)


if __name__ == "__main__":
    main()