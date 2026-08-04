"""
PEH prep step (fast) -- WFG/PLTR/BOIL/RRC cleanup dry run, part 1 of 2.

Does NOT run the migration itself (that's a ~60 min step -- see the
printed command at the end, run it directly in your own terminal/
Claude Code, piped to a log file, not through this script).

This script:
  1. Runs tests/test_add_pattern_collision.py for real.
  2. Creates a FRESH disposable copy of the real live catalog
     (overwrites any stale DRYRUN_ file from a previous attempt).
  3. Prints the exact command to run the migration against that copy,
     with output piped to a log file per this project's own
     "long output -> pipe to file" convention.

Run:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this.py
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PYTHON_DIR = PROJECT_ROOT / "python"
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
sys.path.insert(0, str(PYTHON_DIR))

REMOVE_PIDS = {36, 405, 437, 487}

CHECKS_RUN = 0
CHECKS_PASSED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global CHECKS_RUN, CHECKS_PASSED
    CHECKS_RUN += 1
    if condition:
        CHECKS_PASSED += 1
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}  {detail}")
        sys.exit(1)


def main() -> int:
    print(f"Python: {sys.executable}")

    print("\n=== Step 1 regression test: tests/test_add_pattern_collision.py ===")
    result = subprocess.run(
        [PYTHON_EXE, "tests/test_add_pattern_collision.py"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=60,
    )
    check("test_add_pattern_collision.py exits 0", result.returncode == 0, result.stdout[-800:])
    print(result.stdout)

    print("\n=== creating a FRESH disposable copy (overwrites any stale one) ===")
    from utilities.db_utils import get_latest_catalog_path
    real_live = get_latest_catalog_path()
    dry_run_copy = real_live.with_name("DRYRUN_" + real_live.name)
    print(f"  REAL_LIVE_CATALOG (never written): {real_live}")
    print(f"  DISPOSABLE_COPY (fresh, about to be created): {dry_run_copy}")
    shutil.copy2(real_live, dry_run_copy)
    check("fresh disposable copy created", dry_run_copy.exists())

    conn = sqlite3.connect(str(dry_run_copy))
    remove_present = conn.execute(
        f"SELECT COUNT(*) FROM pattern_instances WHERE pattern_instance_id IN "
        f"({','.join('?' * len(REMOVE_PIDS))})", tuple(REMOVE_PIDS),
    ).fetchone()[0]
    conn.close()
    check("all 4 REMOVE_PIDS present in the fresh copy", remove_present == 4, f"found {remove_present}/4")

    log_path = HUB_ROOT / "Agentic-Hub-Governance" / "verify" / "dryrun_migration_output.txt"

    print(f"\n{CHECKS_PASSED}/{CHECKS_RUN} checks passed.")
    print("\nPREP COMPLETE. Now run this directly (NOT through a wrapper script --")
    print("this takes roughly an hour, mostly the topk_cache reseed):\n")
    print(f'cd "{PYTHON_DIR}"')
    print(
        f'& "{PYTHON_EXE}" migrations\\stage_4b_purge_four_pattern_ident_doubles.py '
        f'--live-db "{dry_run_copy}" 2>&1 | Tee-Object -FilePath "{log_path}"'
    )
    print(f"\n(Tee-Object shows output live AND writes it to {log_path.name} for the next step.)")
    print("\nWhen that finishes (look for 'Migration complete.' or an ERROR line),")
    print("run the second script (verify_purge_dryrun.py) to independently check the result.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
