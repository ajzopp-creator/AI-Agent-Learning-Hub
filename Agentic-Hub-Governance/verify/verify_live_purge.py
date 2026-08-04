"""
PEH verify step -- WFG/PLTR/BOIL/RRC cleanup, LIVE run (real catalog).
Run this AFTER the live migration command finishes -- check
live_migration_output.txt or your terminal for "Migration complete."
or an ERROR/Traceback first.

Independently re-queries the REAL live catalog directly (not trusting
the migration's own printed summary) -- same checks as the dry run's
verify_purge_dryrun.py, pointed at the real file instead of the
disposable copy.

Run:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe verify_live_purge.py
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
LOG_PATH = HUB_ROOT / "Agentic-Hub-Governance" / "verify" / "live_migration_output.txt"
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
        print("FAIL: log file not found. Has the live migration command finished yet?")
        return 1
    log_text = LOG_PATH.read_text(encoding="utf-8", errors="replace")
    if "\x00" in log_text:
        # Windows PowerShell's Tee-Object/Out-File default to UTF-16LE,
        # not UTF-8 -- reading as UTF-8 produces null-byte-interspersed
        # garbage that still LOOKS clean when printed (terminals often
        # swallow the nulls) but breaks an exact substring match. Retry
        # with the actual likely encoding instead of trusting the first read.
        log_text = LOG_PATH.read_text(encoding="utf-16", errors="replace")
    print(log_text[-2000:])
    check(
        "log shows 'Migration complete.' (not an error/exit)",
        "Migration complete." in log_text,
        "log does not contain the success line -- read the tail above for the real error",
    )

    from utilities.db_utils import get_latest_catalog_path
    real_live = get_latest_catalog_path()
    print(f"\n  LIVE_CATALOG (verifying this -- the real file): {real_live}")

    bak_path = real_live.with_suffix(real_live.suffix + ".bak")
    check(
        f"pre-migration backup exists: {bak_path.name}",
        bak_path.exists(),
        "no .bak -- atomic_move may not have run against the real file",
    )

    conn = sqlite3.connect(str(real_live))
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
    check("pattern_instances count is 10761 - 4 = 10757", total_patterns == 10757, f"found {total_patterns}")
    print(f"  (topk_cache row count after reseed: {total_topk})")
    conn.close()

    print("\n=== sanity check: catalog-summary against the REAL live catalog ===")
    result = subprocess.run(
        [PYTHON_EXE, "cli.py", "catalog-summary", "--recent", "5"],
        cwd=str(PYTHON_DIR), capture_output=True, text=True, timeout=60,
    )
    print(result.stdout)
    check("catalog-summary exits 0 against the live catalog", result.returncode == 0, result.stderr[-500:])

    print(f"\n{CHECKS_PASSED}/{CHECKS_RUN} checks passed.")
    print("PASS -- live catalog cleanup verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
