"""One-time migration: add spread_group_id to trades table, rebuild
v_trade_summary to expose it, and add the new v_trade_summary_grouped view
(WO-P020-E1.021 -- nets a multi-leg spread's legs into one win/loss/R unit
for reporting; see that WO for the full incident this fixes).

Safe to re-run: ALTER TABLE is guarded by a column-exists check; both views
are DROPped and recreated from db_client.py's own SQL constants every run,
so this migration can never drift from what a fresh init-db produces.
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.db_client import _V_TRADE_SUMMARY_SQL, _V_TRADE_SUMMARY_GROUPED_SQL

DATABASE_FILE = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)


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
        if not _column_exists(conn, "trades", "spread_group_id"):
            conn.execute("ALTER TABLE trades ADD COLUMN spread_group_id TEXT")
            print("Added trades.spread_group_id")
        else:
            print("trades.spread_group_id already exists -- skipped")

        conn.execute("DROP VIEW IF EXISTS v_trade_summary_grouped")
        conn.execute("DROP VIEW IF EXISTS v_trade_summary")
        conn.execute(_V_TRADE_SUMMARY_SQL)
        conn.execute(_V_TRADE_SUMMARY_GROUPED_SQL)
        conn.commit()
        print("Rebuilt v_trade_summary + v_trade_summary_grouped")

        cols = [r[1] for r in conn.execute("PRAGMA table_info(trades)")]
        if "spread_group_id" not in cols:
            print("FAIL: spread_group_id still missing after ALTER TABLE")
            _write_done("FAIL", 1)
            return

        views = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view'"
        )]
        missing_views = [v for v in ("v_trade_summary", "v_trade_summary_grouped") if v not in views]
        if missing_views:
            print(f"FAIL: view(s) missing after rebuild: {missing_views}")
            _write_done("FAIL", 1)
            return

        # Smoke test -- both views must be queryable
        conn.execute("SELECT * FROM v_trade_summary LIMIT 1").fetchone()
        conn.execute("SELECT * FROM v_trade_summary_grouped LIMIT 1").fetchone()

    finally:
        conn.close()

    print("PASS")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
