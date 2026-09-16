"""
run_this_P020_20260907_121629.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 1 of 18).
Validates migration_add_orders_table.py: confirms the file landed on disk
intact, compiles clean under warnings-as-errors, and that its CREATE TABLE
SQL is syntactically valid -- WITHOUT touching the real P_020 production
database. Never modifies production files.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sqlite3
import sys
import warnings
from datetime import datetime
from pathlib import Path

TARGET = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
    r"\infrastructure\migration_add_orders_table.py"
)

DONE_MARKER = Path(__file__).with_suffix(".py.done")

EXPECTED_MIN_LINES = 100
EXPECTED_MAX_LINES = 140


def _write_done(status: str, exit_code: int) -> None:
    DONE_MARKER.write_text(
        f"timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"status: {status}\n"
        f"exit_code: {exit_code}\n"
    )


def _fail(reason: str) -> None:
    print(f"FAIL: {reason}")
    _write_done("FAIL", 1)
    sys.exit(1)


def main() -> None:
    # 1. Durable signal: file exists, plausible line count.
    if not TARGET.exists():
        _fail(f"target file not found on disk: {TARGET}")

    line_count = len(TARGET.read_text().splitlines())
    print(f"Line count: {line_count}")
    if not (EXPECTED_MIN_LINES <= line_count <= EXPECTED_MAX_LINES):
        _fail(
            f"line count {line_count} outside expected "
            f"[{EXPECTED_MIN_LINES}, {EXPECTED_MAX_LINES}] -- possible "
            f"chunk-boundary merge or truncated write"
        )

    # 2. Compile clean under warnings-as-errors (content-integrity check --
    #    catches invalid escape sequences in non-raw docstrings, etc.)
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    # 3. SQL validity check -- execute ORDERS_TABLE_SQL against an in-memory
    #    DB only. Never opens or touches the real P_020_trades.db.
    sys.path.insert(0, str(TARGET.parent))
    import migration_add_orders_table as mod  # noqa: E402

    conn = sqlite3.connect(":memory:")
    try:
        cur = conn.cursor()
        cur.execute(mod.ORDERS_TABLE_SQL)
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol)"
        )
        cur.execute("PRAGMA table_info(orders)")
        columns = [row[1] for row in cur.fetchall()]
        conn.commit()
    except sqlite3.Error as exc:
        _fail(f"ORDERS_TABLE_SQL invalid against in-memory DB: {exc}")
    finally:
        conn.close()
    print(f"SQL validity check: PASS ({len(columns)} columns created)")

    # 4. Sanity-check the column set matches the WO's BUILD PLAN spec.
    expected_columns = {
        "order_id", "account_id", "symbol", "side", "qty",
        "planned_entry_price", "planned_stop_price", "planned_target_price",
        "trade_mode", "submitted_ts", "schwab_order_id", "status",
        "council_verdict", "why_code", "sig_code", "source_project",
        "confidence_tier", "entry_date", "close_date", "realized_pnl",
    }
    missing = expected_columns - set(columns)
    extra = set(columns) - expected_columns
    if missing:
        _fail(f"missing expected columns: {sorted(missing)}")
    if extra:
        _fail(f"unexpected extra columns: {sorted(extra)}")
    print("Column set check: PASS (matches BUILD PLAN spec, 20 columns)")

    # 5. Confirm real DB_PATH constant is correct and untouched by this run.
    expected_db_path = (
        r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
        r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database"
        r"\P_020_trades.db"
    )
    if str(mod.DB_PATH) != expected_db_path:
        _fail(f"DB_PATH mismatch: {mod.DB_PATH} != {expected_db_path}")
    print("DB_PATH check: PASS (matches expected, not connected to)")

    print("PASS: migration_add_orders_table.py validated, production DB untouched.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
