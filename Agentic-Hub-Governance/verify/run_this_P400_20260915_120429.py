"""run_this_P400_20260915_120429.py -- WO-P400-E8.002 validation.

Compiles every touched file under p140 with -W error::SyntaxWarning
(peh-handoff v1.5/v1.7: syntax-only checking is insufficient -- escape
sequences in docstrings and other silent-corruption classes only surface
under warnings-as-errors), then runs the full touched test suite.

Self-contained. Read-only against production files except for the
inevitable __pycache__ writes from compilation/import. Writes its own
<script>.py.done marker (peh_helper.py done_marker_format()) before exit.
"""

import py_compile
import subprocess
import sys
import warnings
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
DONE_PATH = Path(__file__).with_suffix(".py.done")

TOUCHED_FILES = [
    PROJECT_ROOT / "infrastructure" / "earnings_calendar_cache.py",
    PROJECT_ROOT / "application" / "earnings_lookup.py",
    PROJECT_ROOT / "application" / "batch_2b_scoring.py",
    PROJECT_ROOT / "tests" / "test_earnings_calendar_cache.py",
    PROJECT_ROOT / "tests" / "test_earnings_lookup.py",
    PROJECT_ROOT / "tests" / "test_batch_2b_scoring.py",
]

TEST_FILES = [
    "tests\\test_earnings_calendar_cache.py",
    "tests\\test_earnings_lookup.py",
    "tests\\test_batch_2b_scoring.py",
]


def _write_done(status: str, exit_code: int) -> None:
    content = (
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )
    DONE_PATH.write_text(content, encoding="utf-8")


def _compile_check() -> list:
    errors = []
    for f in TOUCHED_FILES:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", SyntaxWarning)
                py_compile.compile(str(f), doraise=True)
                source = f.read_text(encoding="utf-8")
                compile(source, str(f), "exec")
        except (SyntaxError, SyntaxWarning) as exc:
            errors.append(f"{f}: {exc}")
    return errors


def main() -> int:
    compile_errors = _compile_check()
    if compile_errors:
        print("COMPILE ERRORS:")
        for e in compile_errors:
            print(" ", e)
        print("FAIL: compile step")
        _write_done("FAIL", 1)
        return 1
    print(f"Compile OK: {len(TOUCHED_FILES)} files, warnings-as-errors clean.")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", *TEST_FILES, "-v"],
        cwd=str(PROJECT_ROOT),
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
