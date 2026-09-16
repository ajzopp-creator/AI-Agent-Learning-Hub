"""
run_this_P300_20260910_211500.py
WO-P300-E5.001 step 2 -- the actual import-linter run. Installs
import-linter into the p140 env (if not already present), then runs
lint-imports against python/.importlinter for real, against the
now-cleaned tree (Batches 1+2 both verified PASS already).

This is the FIRST real audit -- the whole reason Batches 1+2 happened
first was so this run isn't drowned in known, already-fixed violations.
Whatever it finds now is either genuinely new or something the design
conversation missed. Does not modify any production file; only
installs a dev dependency and reads the tree.
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
PYTHON_DIR = PROJECT_ROOT / "python"
PY_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"

print("=== Step 1: ensure import-linter is installed ===")
result = subprocess.run(
    [PY_EXE, "-m", "pip", "install", "import-linter", "--break-system-packages", "--quiet"],
    capture_output=True, text=True, timeout=180,
)
print(result.stdout)
if result.returncode != 0:
    print("PIP INSTALL FAILED:")
    print(result.stderr)
    sys.exit(1)
print("  OK -- import-linter installed (or already present)")

print()
print("=== Step 2: python -m importlinter --version (sanity check) ===")
ver = subprocess.run(
    [PY_EXE, "-m", "importlinter", "--version"],
    capture_output=True, text=True, cwd=str(PYTHON_DIR), timeout=60,
)
print(ver.stdout.strip() or "(no stdout)")
if ver.returncode != 0:
    print("VERSION CHECK FAILED -- stderr:")
    print(ver.stderr)
    sys.exit(1)

print()
print("=== Step 3: lint-imports against python/.importlinter ===")
print("(this is the real, first audit -- print everything, no interpretation)")
print()
lint = subprocess.run(
    [PY_EXE, "-m", "importlinter", "lint-imports", "--config", str(PYTHON_DIR / ".importlinter")],
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
    print("CONTRACT BROKEN -- see violations printed above. This may be a real")
    print("finding (something Batches 1+2 and the design conversation missed)")
    print("or a config mistake (e.g. a layer/package name typo, or the")
    print("promote_gate.py case behaving differently than expected). Read the")
    print("violation chain before assuming either -- paste full output back")
    print("either way, do not try to fix the config yourself first.")

done_path = Path(__file__).with_suffix(".py.done")
import datetime
done_path.write_text(
    f"timestamp: {datetime.datetime.now().isoformat()}\n"
    f"lint_imports_exit_code: {lint.returncode}\n",
    encoding="utf-8",
)
sys.exit(0)  # this script's own success = "ran cleanly and reported", not "contract passed"
