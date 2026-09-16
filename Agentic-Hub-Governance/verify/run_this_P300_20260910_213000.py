"""
run_this_P300_20260910_213000.py
WO-P300-E5.001 step 2 -- the actual import-linter run, take 2. First
attempt (run_this_P300_20260910_211500.py) died at the version check --
`python -m importlinter` isn't valid; import-linter installs as
standalone console-script exes (import-linter.exe, lint-imports.exe)
in the env's Scripts\ folder, not as a `python -m`-invokable module.
This version calls lint-imports.exe directly by full path instead.

import-linter is already installed (confirmed present, prior run's
pip install succeeded before the version-check step failed). Does not
modify any production file; reads the tree only.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
PYTHON_DIR = PROJECT_ROOT / "python"
LINT_IMPORTS_EXE = r"C:\Users\Trader\.conda\envs\p140\Scripts\lint-imports.exe"

print("=== Step 1: confirm lint-imports.exe is present ===")
if not Path(LINT_IMPORTS_EXE).exists():
    print(f"FAIL -- {LINT_IMPORTS_EXE} does not exist. Re-run the install step")
    print("from run_this_P300_20260910_211500.py first (pip install import-linter).")
    sys.exit(1)
print(f"  OK -- found {LINT_IMPORTS_EXE}")

print()
print("=== Step 2: lint-imports --version (sanity check) ===")
ver = subprocess.run(
    [LINT_IMPORTS_EXE, "--version"],
    capture_output=True, text=True, cwd=str(PYTHON_DIR), timeout=60,
)
print(ver.stdout.strip() or "(no stdout)")
if ver.stderr:
    print("stderr:", ver.stderr.strip())
if ver.returncode != 0:
    print("VERSION CHECK FAILED -- stopping before the real run.")
    sys.exit(1)

print()
print("=== Step 3: lint-imports against python/.importlinter -- the real, first audit ===")
print("(printing everything, no interpretation)")
print()
lint = subprocess.run(
    [LINT_IMPORTS_EXE, "--config", str(PYTHON_DIR / ".importlinter")],
    capture_output=True, text=True, cwd=str(PYTHON_DIR), timeout=180,
)
print(lint.stdout)
if lint.stderr:
    print("--- stderr ---")
    print(lint.stderr)

print()
print(f"lint-imports exit code: {lint.returncode}")
if lint.returncode == 0:
    print("PASS -- contract holds against the current tree")
else:
    print("CONTRACT BROKEN or CONFIG ERROR -- see output above.")
    print("Could be a real violation Batches 1+2 missed, or a mistake in")
    print(".importlinter itself (written from docs, never run before now).")
    print("Paste the full output back either way -- do not edit the config")
    print("or any production file first.")

done_path = Path(__file__).with_suffix(".py.done")
import datetime
done_path.write_text(
    f"timestamp: {datetime.datetime.now().isoformat()}\n"
    f"lint_imports_exit_code: {lint.returncode}\n",
    encoding="utf-8",
)
sys.exit(0)
