"""run_this_P400_20260915_155031.py -- target_2 vault-record fix, regression gate.

Confirms test_record_writer.py, test_record_writer_derived.py, and
test_size_option_standalone.py pass BEFORE adding target_2. Read-only.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_PYTHON_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
DONE_PATH = Path(__file__).with_suffix(".py.done")


def _write_done(status: str, exit_code: int) -> None:
    content = (
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )
    DONE_PATH.write_text(content, encoding="utf-8")


def main() -> int:
    test_files = [
        "tests\\test_record_writer.py",
        "tests\\test_record_writer_derived.py",
        "tests\\test_size_option_standalone.py",
    ]
    result = subprocess.run(
        [sys.executable, "-m", "pytest", *test_files, "-v"],
        cwd=str(PROJECT_PYTHON_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print("--- stderr ---")
        print(result.stderr)

    if result.returncode == 0:
        print("PASS")
        _write_done("PASS", 0)
        return 0
    else:
        print(f"FAIL: pytest exited {result.returncode}")
        _write_done("FAIL", result.returncode)
        return 1


if __name__ == "__main__":
    sys.exit(main())
