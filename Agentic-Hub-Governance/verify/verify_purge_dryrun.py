"""
PEH verify step (fast) -- WFG/PLTR/BOIL/RRC cleanup dry run, part 2 of 2.

Run this AFTER the manual migration command (from prep_dryrun.py's
output) has finished -- check the log file or your terminal for
"Migration complete." or an ERROR line first.

Does not run anything long -- just reads the log tail and queries the
resulting DISPOSABLE COPY directly to independently confirm the
result, not trusting the migration's own printed summary.

Run:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this.py
"""
from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
PYTHON_DIR = PROJECT_ROOT / "python"
PYTHON_EXE = r"C:\Users\Trader\.conda\envs\p140\python.exe"
LOG_PATH = HUB_ROOT / "Agentic-Hub-Governance" / "verify" / "dryrun_migration_output.txt"
sys.path.insert(0, str(PYTHON_DIR))

REMOVE_PIDS = {36, 405, 437, 487}
KEEP_PIDS = {17, 26, 353, 449}

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
        print(f"\n{CHECKS_PASSED}/{CHECKS_RUN} checks passed before this failure.")
        sys.exit(1)


def main() -> int:
    print(f"Python: {sys.executable}")

    print(f"\n=== reading migration log: {LOG_PATH} ===")
    if not LOG_PATH.exists():
        print(f"FAIL: log file not found. Did you run the migration command "
              f"with Tee-Object -FilePath yet? See prep_dryrun.py's printed instructions.")
        return 1
    log_text = LOG_PATH.read_text(encoding="utf-8", errors="replace")
    print(log_text[-2000:])
    check(
        "log shows 'Migration complete.' (not an error/exit)",
        "Migration complete." in log_text,
        "log does not contain the success line -- read the tail above for the real error",
    )

    from utilities.db_utils import get_latest_catalog_path
    real_live = get_latest_catalog_path()
    dry_run_copy = real_live.with_name("DRYRUN_" + real_live.name)
    print(f"\n  REAL_LIVE_CATALOG (never touched by any of this): {real_live}")
    print(f"  DISPOSABLE_COPY (independently verifying THIS): {dry_run_copy}")

    conn = sqlite3.connect(str(dry_run_copy))
    remove_still_present = conn.execute(
        f"SELECT pattern_instance_id FROM pattern_instances WHERE pattern_instance_id IN "
        f"({','.join('?' * len(REMOVE_PIDS))})", tuple(REMOVE_PIDS),
    ).fetchall()
    check("all 4 REMOVE_PIDS gone from pattern_instances", len(remove_still_present) == 0, str(remove_still_present))

    keep_present = conn.execute(
        f"SELECT COUNT(*) FROM pattern_instances WHERE pattern_instance_id IN "
        f"({','.join('?' * len(KEEP_PIDS))})", tuple(KEEP_PIDS),
    ).fetchone()[0]
    check("all 4 KEEP_PIDS still present", keep_present == 4, f"found {keep_present}/4")

    orphan_bars = conn.execute(
        f"SELECT COUNT(*) FROM pattern_bars WHERE pattern_instance_id IN "
        f"({','.join('?' * len(REMOVE_PIDS))})", tuple(REMOVE_PIDS),
    ).fetchone()[0]
    check("no orphaned pattern_bars for removed pids", orphan_bars == 0, f"found {orphan_bars}")

    orphan_labels = conn.execute(
        f"SELECT COUNT(*) FROM forward_labels WHERE pattern_instance_id IN "
        f"({','.join('?' * len(REMOVE_PIDS))})", tuple(REMOVE_PIDS),
    ).fetchone()[0]
    check("no orphaned forward_labels for removed pids", orphan_labels == 0, f"found {orphan_labels}")

    orphan_topk = conn.execute(
        f"SELECT COUNT(*) FROM topk_cache WHERE pattern_instance_id IN "
        f"({','.join('?' * len(REMOVE_PIDS))}) OR matched_pid IN "
        f"({','.join('?' * len(REMOVE_PIDS))})", tuple(REMOVE_PIDS) * 2,
    ).fetchone()[0]
    check("no topk_cache rows reference removed pids", orphan_topk == 0, f"found {orphan_topk}")

    dup_check = conn.execute(
        "SELECT s.ticker, pi.anchor_date, COUNT(*) c FROM pattern_instances pi "
        "JOIN symbols s ON s.symbol_id = pi.symbol_id "
        "GROUP BY s.ticker, pi.anchor_date HAVING c > 1"
    ).fetchall()
    check("zero remaining (ticker, anchor_date) duplicates anywhere", len(dup_check) == 0, str(dup_check))

    total_patterns = conn.execute("SELECT COUNT(*) FROM pattern_instances").fetchone()[0]
    total_topk = conn.execute("SELECT COUNT(*) FROM topk_cache").fetchone()[0]
    check(
        "pattern_instances count is 10761 - 4 = 10757",
        total_patterns == 10757, f"found {total_patterns}",
    )
    print(f"  (topk_cache row count after reseed: {total_topk})")
    conn.close()

    print("\n=== sanity check: catalog-summary runs against the purged copy ===")
    result = subprocess.run(
        [PYTHON_EXE, "cli.py", "catalog-summary", "--catalog", str(dry_run_copy), "--recent", "5"],
        cwd=str(PYTHON_DIR), capture_output=True, text=True, timeout=60,
    )
    print(result.stdout)
    check("catalog-summary exits 0 against the purged copy", result.returncode == 0, result.stderr[-500:])

    print(f"\n{CHECKS_PASSED}/{CHECKS_RUN} checks passed.")
    print("PASS (DRY RUN VERIFIED -- real live catalog was never touched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
