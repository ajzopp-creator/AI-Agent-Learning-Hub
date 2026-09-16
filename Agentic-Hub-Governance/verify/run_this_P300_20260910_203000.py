"""
run_this_P300_20260910_203000.py
WO-P300-E5.001 -- Batch 2 verification (utilities/ -> utilities/ + tools/
split). Read-only against production code: compiles every moved/edited
file under warnings-as-errors, then imports each one for real.

Modifies nothing. Safe to re-run.
"""
import sys
import traceback
import warnings
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
PYTHON_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))
sys.path.insert(0, str(PYTHON_DIR / "tests"))

warnings.simplefilter("error", SyntaxWarning)

MOVED_FILES = [
    "tools/catalog_summary.py",
    "tools/check_pattern.py",
    "tools/ledger_calibration.py",
    "tools/preflight_status.py",
    "tools/vp_export_integrity_check.py",
    "tools/loo_replay.py",
    "tools/feature_ablation.py",
    "tools/threshold_sweep.py",
    "tools/cap_sensitivity_audit.py",
    "tools/__init__.py",
]
EDITED_FILES = [
    "cli_commands/utility.py",
    "tests/smoke_loo_replay.py",
]
ALL_FILES = MOVED_FILES + EDITED_FILES

failures = []

print("=== Phase 1: compile check ===")
for rel in ALL_FILES:
    p = PYTHON_DIR / rel
    try:
        src = p.read_text(encoding="utf-8")
        compile(src, str(p), "exec", dont_inherit=True)
        print(f"  OK   compile: {rel}")
    except Exception as e:
        failures.append((rel, "compile", repr(e)))
        print(f"  FAIL compile: {rel} -- {e!r}")

print("=== Phase 2: import resolution (tools/ package + moved modules) ===")
import importlib

MODULES_TO_IMPORT = [
    "tools",
    "tools.catalog_summary",
    "tools.check_pattern",
    "tools.ledger_calibration",
    "tools.preflight_status",
    "tools.vp_export_integrity_check",
    "tools.loo_replay",
    "tools.feature_ablation",
    "tools.threshold_sweep",
    "tools.cap_sensitivity_audit",
    "cli_commands.utility",
]
for mod_name in MODULES_TO_IMPORT:
    try:
        importlib.import_module(mod_name)
        print(f"  OK   import: {mod_name}")
    except Exception as e:
        failures.append((mod_name, "import", repr(e)))
        print(f"  FAIL import: {mod_name} -- {e!r}")
        traceback.print_exc()

print("=== Phase 3: utilities/ no longer imports anything moved out ===")
UTILITIES_LEAVES = ["db_connect", "db_utils", "archive_live_file",
                     "archive_mined_file", "archive_pattern_file",
                     "archive_scanner_file", "intelliscan_reader",
                     "inspect_pattern"]
for mod_name in UTILITIES_LEAVES:
    try:
        importlib.import_module(f"utilities.{mod_name}")
        print(f"  OK   import: utilities.{mod_name}")
    except Exception as e:
        failures.append((f"utilities.{mod_name}", "import", repr(e)))
        print(f"  FAIL import: utilities.{mod_name} -- {e!r}")
        traceback.print_exc()

print("=== Phase 4: smoke_loo_replay's moved import target resolves ===")
try:
    from tools.loo_replay import _classify_per_horizon_overridable
    print("  OK   tools.loo_replay._classify_per_horizon_overridable resolves")
except Exception as e:
    failures.append(("smoke_loo_replay target", "import", repr(e)))
    print(f"  FAIL tools.loo_replay._classify_per_horizon_overridable -- {e!r}")
    traceback.print_exc()

print()
if failures:
    print(f"FAIL: {len(failures)} problem(s) found")
    for f in failures:
        print(f"  - {f}")
    result_line = f"FAIL: {len(failures)} problem(s)\n"
    exit_code = 1
else:
    print("PASS")
    result_line = "PASS\n"
    exit_code = 0

done_path = Path(__file__).with_suffix(".py.done")
import datetime
done_path.write_text(
    f"timestamp: {datetime.datetime.now().isoformat()}\n"
    f"status: {'PASS' if exit_code == 0 else 'FAIL'}\n"
    f"exit_code: {exit_code}\n",
    encoding="utf-8",
)
sys.exit(exit_code)
