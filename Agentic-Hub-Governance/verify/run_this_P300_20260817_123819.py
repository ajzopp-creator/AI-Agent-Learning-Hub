"""
run_this_P300_20260817_123819.py
WO-P300-E5.008 -- PEH verification harness for the rewritten
test_eval_incremental.py (domain layer) and the new
test_incremental_post_batch.py (application layer, real sqlite fixture).

Runs both permanent test files as real subprocesses via the p140
interpreter (matching their own documented RUN instructions), captures
stdout/stderr + exit code, reports PASS only if both exit 0 with
"ALL CHECKS PASSED" in their output. Self-contained, does not modify
production files. Writes its own .done marker on completion.
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
PROJECT_ROOT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
)
TESTS_DIR = PROJECT_ROOT / "python" / "tests"
DONE_MARKER = Path(__file__).with_suffix(".py.done")

TEST_FILES = [
    "test_eval_incremental.py",
    "test_incremental_post_batch.py",
]


def _write_done(status: str, exit_code: int) -> None:
    DONE_MARKER.write_text(
        f"status={status}\nexit_code={exit_code}\ntimestamp={datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def main() -> int:
    overall_ok = True
    for name in TEST_FILES:
        path = TESTS_DIR / name
        print(f"\n{'=' * 70}\nRUNNING: {name}\n{'=' * 70}")
        result = subprocess.run(
            [PYTHON_EXE, str(path)],
            cwd=str(PROJECT_ROOT / "python"),
            capture_output=True, text=True,
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:\n" + result.stderr)
        passed = result.returncode == 0 and "ALL CHECKS PASSED" in result.stdout
        print(f"{name}: {'PASS' if passed else 'FAIL'} (exit={result.returncode})")
        overall_ok = overall_ok and passed

    if overall_ok:
        print("\nPASS")
        _write_done("PASS", 0)
        return 0
    print("\nFAIL: one or more test files did not pass")
    _write_done("FAIL", 1)
    return 1


if __name__ == "__main__":
    sys.exit(main())
