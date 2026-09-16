"""
Diagnostic: dump P_020_trades.db `systems` table and compare against the
three hardcoded system-code lists found in the P_020 codebase (2026-09-13
session, Tony's question re: single canonical source for valid systems).

Never modifies production files. Read-only.
"""
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DB = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db")

HARDCODED_LISTS = {
    "generate_dashboard.py SYSTEM_ORDER": ["P_118", "P_115", "P_300", "P_117", "P_910", "SNT", "P_116"],
    "resolve_tos_imports.py VALID_SYSTEMS": {"P_115","P_116","P_117","P_118","P_300","P_910","P_920","SNT","Day","DAY","TOS_Import","P_105","P_110","P_120","P_210"},
    "tracker_reader.py _VALID_SYSTEMS": {"P_115","P_116","P_117","P_118","P_300","P_910","P_920","Day","SNT","TOS_Import","P_105","P_110","P_120","P_210"},
}

def main():
    if not DB.exists():
        print(f"FAIL: DB not found at {DB}")
        write_done("FAIL", 1)
        sys.exit(1)

    conn = sqlite3.connect(str(DB))
    try:
        rows = conn.execute(
            "SELECT system_id, system_name, active FROM systems ORDER BY system_id"
        ).fetchall()
    except sqlite3.Error as e:
        print(f"FAIL: query error: {e}")
        write_done("FAIL", 1)
        sys.exit(1)

    print("=== systems table ===")
    for r in rows:
        print(r)
    db_ids = {r[0] for r in rows}
    db_active_ids = {r[0] for r in rows if r[2] == 1}

    print()
    print("=== distinct system values actually used in trades table ===")
    try:
        trade_systems = conn.execute(
            "SELECT DISTINCT system, COUNT(*) FROM trades GROUP BY system ORDER BY system"
        ).fetchall()
        for r in trade_systems:
            print(r)
    except sqlite3.Error as e:
        print(f"NOTE: trades query error: {e}")

    print()
    print("=== comparison: hardcoded list vs systems table (active) ===")
    for name, lst in HARDCODED_LISTS.items():
        lst_set = set(lst)
        missing_from_list = db_active_ids - lst_set
        extra_in_list = lst_set - db_ids
        print(f"{name}:")
        print(f"  in DB.active but missing from list: {sorted(missing_from_list)}")
        print(f"  in list but not in DB at all:        {sorted(extra_in_list)}")

    conn.close()
    print()
    print("PASS")
    write_done("PASS", 0)

def write_done(status, exit_code):
    done_path = Path(__file__).with_suffix(".py.done")
    done_path.write_text(
        f"STATUS: {status}\nEXIT_CODE: {exit_code}\nTIMESTAMP: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
