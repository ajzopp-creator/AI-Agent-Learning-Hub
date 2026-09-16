"""One-time migration: add display_order to systems table, backfill values,
and rename P400 -> P_400 for naming consistency (Tony's call, 2026-09-13,
confirmed zero live trades reference 'P400').

Safe to re-run: ALTER TABLE is guarded by a column-exists check; the
UPDATEs are idempotent (re-running writes the same values); the rename
aborts instead of writing if any trade now references 'P400'.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DATABASE_FILE = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)

# Priority order kept from the pre-existing generate_dashboard.py
# SYSTEM_ORDER (first 7), then every other active system alphabetically,
# TOS_Import forced last.
DISPLAY_ORDER = [
    "P_118", "P_115", "P_300", "P_117", "P_910", "SNT", "P_116",
    "Day", "INV", "P_010", "P_105", "P_110", "P_120", "P_210", "P_400", "P_920",
    "TOS_Import",
]


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
    return column in cols


def _write_done(status: str, exit_code: int) -> None:
    done_path = Path(__file__).with_suffix(".py.done")
    done_path.write_text(
        f"STATUS: {status}\nEXIT_CODE: {exit_code}\n"
        f"TIMESTAMP: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )


def main() -> None:
    conn = sqlite3.connect(str(DATABASE_FILE))
    try:
        trade_count = conn.execute(
            "SELECT COUNT(*) FROM trades WHERE system = 'P400'"
        ).fetchone()[0]
        if trade_count != 0:
            print(f"FAIL: {trade_count} trades reference 'P400' -- not renaming, review first")
            _write_done("FAIL", 1)
            return
        conn.execute("UPDATE systems SET system_id = 'P_400' WHERE system_id = 'P400'")

        if not _column_exists(conn, "systems", "display_order"):
            conn.execute("ALTER TABLE systems ADD COLUMN display_order INTEGER")

        for i, system_id in enumerate(DISPLAY_ORDER):
            conn.execute(
                "UPDATE systems SET display_order = ? WHERE system_id = ?",
                (i, system_id),
            )
        conn.commit()

        rows = conn.execute(
            "SELECT system_id, display_order FROM systems ORDER BY display_order"
        ).fetchall()
        print("=== systems after migration ===")
        for r in rows:
            print(r)
        missing = [r[0] for r in rows if r[1] is None]
        if missing:
            print(f"FAIL: {len(missing)} systems with no display_order: {missing}")
            _write_done("FAIL", 1)
            return
    finally:
        conn.close()

    print("PASS")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
