"""WO-P020-E1.016 verification -- compile check + pytest for the
cash_available fallback fix in schwab_balance_pull.py. Self-contained,
never modifies production files or touches the live Schwab API.
See _context.txt for what this checks.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DONE_MARKER = SCRIPT_DIR / (Path(__file__).name + ".done")

PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)
TARGET_FILE = PROJECT_ROOT / "infrastructure" / "schwab_balance_pull.py"
TEST_FILE = PROJECT_ROOT / "tests" / "test_schwab_balance_pull.py"
PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"


def write_done(status: str, exit_code: int) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    DONE_MARKER.write_text(
        f"status={status}\nexit_code={exit_code}\ntimestamp={ts}\n",
        encoding="utf-8",
    )


def main() -> None:
    # 1. Compile check, warnings-as-errors, on the edited production file.
    compile_result = subprocess.run(
        [PYTHON, "-W", "error::SyntaxWarning", "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True,
        text=True,
    )
    if compile_result.returncode != 0:
        print("FAIL: compile error in schwab_balance_pull.py")
        print(compile_result.stderr)
        write_done("FAIL", 1)
        sys.exit(1)
    print("Compile check: PASS")

    # 2. Run the new regression test file only. This does NOT touch the
    #    live Schwab API -- it tests the extraction expression directly
    #    against fake dicts, no network/auth involved.
    test_result = subprocess.run(
        [PYTHON, "-m", "pytest", str(TEST_FILE), "-v"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    print(test_result.stdout)
    print(test_result.stderr)

    if test_result.returncode != 0:
        print("FAIL: test_schwab_balance_pull.py did not pass")
        write_done("FAIL", test_result.returncode)
        sys.exit(1)

    print("PASS")
    write_done("PASS", 0)


if __name__ == "__main__":
    main()
