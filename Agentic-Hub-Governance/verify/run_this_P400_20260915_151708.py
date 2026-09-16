"""run_this_P400_20260915_151708.py -- WO-P400-E8.003 post-code validation.

Compiles every touched/new file under p140 with -W error::SyntaxWarning,
then runs the full touched test suite.
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
    PROJECT_ROOT / "application" / "evaluate_options.py",
    PROJECT_ROOT / "application" / "commands.py",
    PROJECT_ROOT / "application" / "build_option_spec.py",
    PROJECT_ROOT / "application" / "build_option_spec_scaleout.py",
    PROJECT_ROOT / "application" / "size_option_standalone.py",
    PROJECT_ROOT / "cli.py",
    PROJECT_ROOT / "domain" / "options_sizer.py",
    PROJECT_ROOT / "tests" / "test_evaluate_options.py",
    PROJECT_ROOT / "tests" / "test_build_option_spec.py",
    PROJECT_ROOT / "tests" / "test_build_option_spec_scaleout.py",
    PROJECT_ROOT / "tests" / "test_size_option_standalone.py",
    PROJECT_ROOT / "tests" / "test_options_sizer.py",
]

TEST_FILES = [
    "tests\\test_evaluate_options.py",
    "tests\\test_build_option_spec.py",
    "tests\\test_build_option_spec_scaleout.py",
    "tests\\test_size_option_standalone.py",
    "tests\\test_options_sizer.py",
    "tests\\test_commands.py",
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
