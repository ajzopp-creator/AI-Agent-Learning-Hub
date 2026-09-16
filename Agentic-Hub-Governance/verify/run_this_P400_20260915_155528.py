"""run_this_P400_20260915_155528.py -- target_2 vault-record fix, validation.

Compiles record_writer.py and size_option_standalone.py under p140
warnings-as-errors, then runs their test suites plus the full P_400 suite.
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
    PROJECT_ROOT / "infrastructure" / "record_writer.py",
    PROJECT_ROOT / "application" / "size_option_standalone.py",
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
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    print(result.stdout[-6000:])
    if result.stderr:
        print("--- stderr (tail) ---")
        print(result.stderr[-2000:])

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
