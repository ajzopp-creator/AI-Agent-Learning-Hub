"""PEH verification: WO-P805-E2.001 Outlook OAuth2 support, Entry 014 fix.

Validates the corrected files compile under p140 with warnings-as-errors,
that msal + msal-extensions are importable, and runs the project's own
unittest suite (tests/test_imap_mover.py + tests/test_oauth2_outlook.py)
without touching any live keyring entry, real cache file, network call,
or browser.

Self-contained per peh-handoff convention. Never modifies production files.
"""

import subprocess
import sys
import warnings
from pathlib import Path

PROJECT_PYTHON = r"C:\Users\Trader\.conda\envs\p140\python.exe"
PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

CHANGED_FILES = [
    PROJECT_ROOT / "config.py",
    PROJECT_ROOT / "cli.py",
    PROJECT_ROOT / "infrastructure" / "oauth2_outlook.py",
    PROJECT_ROOT / "infrastructure" / "imap_mover.py",
    PROJECT_ROOT / "tests" / "test_imap_mover.py",
    PROJECT_ROOT / "tests" / "test_oauth2_outlook.py",
]


def compile_check() -> list[str]:
    """Compile each changed file with -W error::SyntaxWarning. Returns failures."""
    failures = []
    for f in CHANGED_FILES:
        result = subprocess.run(
            [PROJECT_PYTHON, "-W", "error::SyntaxWarning", "-m", "py_compile", str(f)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append(f"{f.name}: {result.stderr.strip()}")
    return failures


def import_check() -> list[str]:
    """Confirm msal and msal_extensions are installed and importable in p140."""
    failures = []
    for module in ["msal", "msal_extensions"]:
        result = subprocess.run(
            [PROJECT_PYTHON, "-c", f"import {module}; print({module}.__name__)"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append(f"{module} import failed: {result.stderr.strip()}")
    return failures


def run_tests() -> tuple[bool, str]:
    """Run the two relevant test files via unittest discover."""
    result = subprocess.run(
        [PROJECT_PYTHON, "-m", "unittest",
         "tests.test_imap_mover", "tests.test_oauth2_outlook", "-v"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
    )
    passed = result.returncode == 0
    return passed, result.stdout + result.stderr


def main() -> None:
    compile_failures = compile_check()
    if compile_failures:
        print("FAIL: compile errors")
        for f in compile_failures:
            print(f"  - {f}")
        write_done_marker("FAIL", 1)
        sys.exit(1)

    import_failures = import_check()
    if import_failures:
        print("FAIL: import errors")
        for f in import_failures:
            print(f"  - {f}")
        write_done_marker("FAIL", 1)
        sys.exit(1)

    tests_passed, test_output = run_tests()
    print(test_output)
    if not tests_passed:
        print("FAIL: unittest suite failed")
        write_done_marker("FAIL", 1)
        sys.exit(1)

    print("PASS")
    write_done_marker("PASS", 0)


def write_done_marker(status: str, exit_code: int) -> None:
    import datetime
    done_path = Path(__file__).with_suffix(".py.done")
    done_path.write_text(
        f"{status}\nexit_code={exit_code}\n{datetime.datetime.now().isoformat()}\n"
    )


if __name__ == "__main__":
    main()
