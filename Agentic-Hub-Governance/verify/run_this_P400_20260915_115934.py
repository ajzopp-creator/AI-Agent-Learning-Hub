"""run_this_P400_20260915_115934.py -- PEH regression-gate check.

WO-P400-E8.002, pre-code regression gate (python-project-architecture
Step 0 item 10): confirms the EXISTING test suites for the two files
about to be edited (infrastructure/earnings_calendar_cache.py,
application/earnings_lookup.py) pass BEFORE any change lands. A
pre-existing failure here means a past fix already broke -- stop, do
not build on top of it.

Self-contained. Read-only -- never modifies production files. Writes
its own <script>.py.done marker (peh_helper.py done_marker_format())
before exit.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJECT_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python"
)
sys.path.insert(0, str(PROJECT_PYTHON_DIR))  # self-contained convention, even though
                                              # the pytest subprocess below sets its own cwd

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
        "tests\\test_earnings_calendar_cache.py",
        "tests\\test_earnings_lookup.py",
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
