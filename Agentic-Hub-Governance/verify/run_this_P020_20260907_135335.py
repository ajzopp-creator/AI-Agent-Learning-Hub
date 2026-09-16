"""
run_this_P020_20260907_135335.py

PEH verification script (WO-P400-E6.001 Scope item 2, files 1/2/3/5
revised + file 6 new). Validates the full chain end-to-end against an
in-memory scratch DB built from the REAL trades/exits/systems table
schemas (read via a read-only connection to the real DB, never written
to) plus the new orders table -- migration_add_orders_table.py,
schemas.py's extended Order model, order_linkage.py's put_call field,
order_reconciler.py's extended ReconciledOrder, and the new
db_order_writer.py (insert_order/update_order_status/
promote_order_to_trade).

The real P_020_trades.db is opened ONCE, in true read-only mode
(sqlite3 URI mode=ro), only to read its trades/exits/systems CREATE
TABLE statements -- no row is read or written in the real database at
any point in this script.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sqlite3
import sys
import warnings
from datetime import date, datetime
from pathlib import Path

DATABASE_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)
REAL_DB_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\data\database\P_020_trades.db"
)

FILES = {
    "migration_add_orders_table.py": DATABASE_DIR / "infrastructure" / "migration_add_orders_table.py",
    "schemas.py": DATABASE_DIR / "schemas.py",
    "order_linkage.py": DATABASE_DIR / "domain" / "order_linkage.py",
    "order_reconciler.py": DATABASE_DIR / "domain" / "order_reconciler.py",
    "db_order_writer.py": DATABASE_DIR / "infrastructure" / "db_order_writer.py",
}

DONE_MARKER = Path(__file__).with_suffix(".py.done")


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


def _compile_all() -> None:
    for label, path in FILES.items():
        if not path.exists():
            _fail(f"{label} not found on disk: {path}")
        with warnings.catch_warnings():
            warnings.simplefilter("error", SyntaxWarning)
            try:
                py_compile.compile(str(path), doraise=True)
            except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
                _fail(f"{label} compile error under warnings-as-errors: {exc}")
    print(f"Compile check: PASS ({len(FILES)} files, warnings-as-errors)")


def _build_scratch_db() -> sqlite3.Connection:
    """Read trades/exits/systems CREATE TABLE SQL from the REAL db
    read-only, then build an in-memory scratch DB with those tables plus
    the new orders table. Never writes to the real DB."""
    if not REAL_DB_PATH.exists():
        _fail(f"real DB not found (read-only lookup only): {REAL_DB_PATH}")

    ro_conn = sqlite3.connect(f"file:{REAL_DB_PATH}?mode=ro", uri=True)
    try:
        rows = ro_conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' "
            "AND name IN ('trades', 'exits', 'systems')"
        ).fetchall()
    finally:
        ro_conn.close()

    schema_by_name = {name: sql for name, sql in rows}
    for required in ("trades", "exits", "systems"):
        if required not in schema_by_name:
            _fail(f"real DB has no '{required}' table -- cannot build scratch DB")

    scratch = sqlite3.connect(":memory:")
    for sql in schema_by_name.values():
        scratch.execute(sql)

    sys.path.insert(0, str(DATABASE_DIR))
    import infrastructure.migration_add_orders_table as migration_mod  # noqa: E402
    scratch.execute(migration_mod.ORDERS_TABLE_SQL)
    scratch.commit()
    print("Scratch DB check: PASS (real trades/exits/systems schema + new orders table, in-memory only)")
    return scratch


def main() -> None:
    _compile_all()
    scratch = _build_scratch_db()

    import domain.order_linkage as linkage_mod  # noqa: E402
    import domain.order_reconciler as recon_mod  # noqa: E402
    import infrastructure.db_order_writer as writer_mod  # noqa: E402
    import schemas  # noqa: E402

    # ---- schemas.py: Order model accepts the 3 new fields ----
    order = schemas.Order(
        account_id="AJZ6348", symbol="AAPL", side="long", qty=100,
        submitted_ts=datetime(2026, 9, 1, 9, 30, 0),
        why_code="P_115", sig_code="BTD_SIGNAL", schwab_order_id="9001",
        planned_stop_price=145.00,
        entry_date=date(2026, 9, 1), close_date=date(2026, 9, 3),
        realized_pnl=525.00, entry_fill_price=150.25,
        asset_type="EQUITY", put_call=None,
    )
    if order.asset_type != "EQUITY":
        _fail(f"Order.asset_type wrong: got {order.asset_type}")
    print("schemas.py Order new-fields check: PASS")

    # ---- order_linkage.py: put_call extraction ----
    option_raw = {
        "orderId": 5001, "orderStrategyType": "SINGLE", "status": "FILLED",
        "enteredTime": "2026-09-01T10:00:00+0000",
        "closeTime": "2026-09-01T10:00:00+0000",
        "orderLegCollection": [
            {"instrument": {"symbol": "TSLA  260918C00250000", "assetType": "OPTION", "putCall": "CALL"}, "quantity": 1}
        ],
        "orderActivityCollection": [{"executionLegs": [{"quantity": 1, "price": 5.00}]}],
    }
    option_chain = linkage_mod.build_order_chain(option_raw)
    if option_chain.root.put_call != "CALL":
        _fail(f"put_call not extracted: got {option_chain.root.put_call}")
    print("order_linkage.py put_call check: PASS")

    # ---- order_reconciler.py: ReconciledOrder carries the new fields ----
    result = recon_mod.reconcile_order(side="long", entry_chain=option_chain)
    if result is not None:
        _fail("expected None (no filled exit for a standalone SINGLE with no children)")
    print("order_reconciler.py no-exit-yet check: PASS (None, no crash)")

    # ---- db_order_writer.py: full round trip, equity, via insert_order ----
    order_id_a = writer_mod.insert_order(scratch, order)
    if order_id_a is None:
        _fail("insert_order returned None for a fresh (non-duplicate) order")

    dup = writer_mod.insert_order(scratch, order)
    if dup is not None:
        _fail(f"insert_order should skip duplicate schwab_order_id, got {dup}")
    print(f"db_order_writer.py insert_order + dedup check: PASS (order_id={order_id_a})")

    trade_id_a = writer_mod.promote_order_to_trade(scratch, order_id_a)
    if trade_id_a is None:
        _fail("promote_order_to_trade returned None for a fully-reconciled order")

    trade_row = scratch.execute(
        "SELECT asset_type, entry_price, direction, system, reason FROM trades WHERE trade_id = ?",
        (trade_id_a,),
    ).fetchone()
    if trade_row is None:
        _fail("promoted trade not found in trades table")
    if trade_row[0] != "stock":
        _fail(f"asset_type mapping wrong: expected 'stock' (EQUITY+None), got {trade_row[0]}")
    if trade_row[1] != 150.25:
        _fail(f"entry_price wrong: expected 150.25, got {trade_row[1]}")
    if trade_row[3] != "P_115":
        _fail(f"system wrong: expected 'P_115' (why_code), got {trade_row[3]}")
    if trade_row[4] != "BTD_SIGNAL":
        _fail(f"reason wrong: expected 'BTD_SIGNAL' (sig_code), got {trade_row[4]}")

    exit_row = scratch.execute(
        "SELECT exit_price, exit_pnl, qty_exited FROM exits WHERE trade_id = ?",
        (trade_id_a,),
    ).fetchone()
    if exit_row is None:
        _fail("promoted exit leg not found in exits table")
    if exit_row[0] != 155.50:
        _fail(f"back-calculated exit_price wrong: expected 155.50, got {exit_row[0]}")
    if exit_row[1] != 525.00:
        _fail(f"exit_pnl wrong: expected 525.00, got {exit_row[1]}")
    print(
        f"db_order_writer.py promote_order_to_trade check: PASS "
        f"(trade_id={trade_id_a}, asset_type=stock, exit_price=155.50)"
    )

    # ---- db_order_writer.py: OPTION asset_type mapping, via COALESCE update path ----
    order_b = schemas.Order(
        account_id="AJZ6348", symbol="TSLA  260918C00250000", side="long", qty=1,
        submitted_ts=datetime(2026, 9, 1, 10, 0, 0),
        why_code="P_116", sig_code="OIL_SIGNAL", schwab_order_id="9002",
        status="pending",
    )
    order_id_b = writer_mod.insert_order(scratch, order_b)
    if order_id_b is None:
        _fail("insert_order returned None for order_b (fresh)")

    # Status-only transition -- reconciliation fields must stay untouched.
    writer_mod.update_order_status(scratch, order_id_b, status="working")
    row_after_status_only = scratch.execute(
        "SELECT status, close_date, realized_pnl FROM orders WHERE order_id = ?",
        (order_id_b,),
    ).fetchone()
    if row_after_status_only[0] != "working" or row_after_status_only[1] is not None:
        _fail(f"COALESCE status-only update wrong: got {row_after_status_only}")

    # Now the real reconciliation update.
    writer_mod.update_order_status(
        scratch, order_id_b, status="closed",
        entry_date="2026-09-01", close_date="2026-09-05",
        realized_pnl=2.50, entry_fill_price=5.00,
        asset_type="OPTION", put_call="CALL",
    )
    print("db_order_writer.py update_order_status COALESCE check: PASS")

    trade_id_b = writer_mod.promote_order_to_trade(scratch, order_id_b)
    if trade_id_b is None:
        _fail("promote_order_to_trade returned None for order_b after reconciliation update")
    trade_row_b = scratch.execute(
        "SELECT asset_type, entry_price FROM trades WHERE trade_id = ?", (trade_id_b,)
    ).fetchone()
    if trade_row_b[0] != "call":
        _fail(f"OPTION+CALL asset_type mapping wrong: expected 'call', got {trade_row_b[0]}")
    print(f"db_order_writer.py OPTION mapping check: PASS (trade_id={trade_id_b}, asset_type=call)")

    # ---- Not-yet-reconciled order -> promote returns None, no crash ----
    order_c = schemas.Order(
        account_id="AJZ6348", symbol="MSFT", side="long", qty=10,
        submitted_ts=datetime(2026, 9, 6, 9, 0, 0), status="working",
    )
    order_id_c = writer_mod.insert_order(scratch, order_c)
    result_c = writer_mod.promote_order_to_trade(scratch, order_id_c)
    if result_c is not None:
        _fail(f"expected None for an unreconciled order, got {result_c}")
    print("db_order_writer.py unreconciled-order check: PASS (None, no crash)")

    scratch.close()
    print("PASS: files 1/2/3/5 (revised) and file 6 all validated end-to-end.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
