"""
run_this_P020_20260907_204856.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 7 of 18 +
db_reader.py extension). Validates infrastructure\\db_reader.py's new
get_open_real_orders() and application\\reconcile_command.py's
reconcile_live_orders() end-to-end, against an in-memory scratch DB built
from the REAL trades/exits/systems schema (read-only lookup, same
pattern as the prior handoff) plus the orders table. Schwab's live API
is mocked -- get_orders_for_account is monkeypatched to return canned
data, no real network call is made.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sqlite3
import sys
import warnings
from datetime import datetime
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
    "db_reader.py": DATABASE_DIR / "infrastructure" / "db_reader.py",
    "reconcile_command.py": DATABASE_DIR / "application" / "reconcile_command.py",
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
    """Same pattern as the prior handoff -- real trades/exits/systems
    schema read-only, orders table added, everything else in-memory."""
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
    scratch.row_factory = sqlite3.Row  # matches get_connection()'s real behavior
    for sql in schema_by_name.values():
        scratch.execute(sql)

    sys.path.insert(0, str(DATABASE_DIR))
    import infrastructure.migration_add_orders_table as migration_mod  # noqa: E402
    scratch.execute(migration_mod.ORDERS_TABLE_SQL)
    scratch.commit()
    print("Scratch DB check: PASS (real trades/exits/systems schema + orders table, row_factory=Row)")
    return scratch


# Same TIER1/TIER2 fixtures as the file-5 handoff, for consistency and
# easy cross-reference -- TIER1_ORDER resolves via chain linkage (Tier 1),
# TIER2_ENTRY_ORDER + TIER2_EXIT_ORDER are separate standalone orders
# resolved via the FIFO fallback (Tier 2).
TIER1_ORDER = {
    "orderId": 2001, "orderStrategyType": "TRIGGER", "status": "FILLED",
    "enteredTime": "2026-09-01T09:35:00+0000", "closeTime": "2026-09-01T09:35:05+0000",
    "orderLegCollection": [{"instrument": {"symbol": "AAPL", "assetType": "EQUITY"}, "quantity": 100}],
    "orderActivityCollection": [{"executionLegs": [{"quantity": 100, "price": 150.25}]}],
    "childOrderStrategies": [{
        "orderId": 2002, "orderStrategyType": "OCO", "status": "WORKING",
        "orderLegCollection": [],
        "childOrderStrategies": [
            {
                "orderId": 2003, "orderStrategyType": "SINGLE", "status": "FILLED",
                "enteredTime": "2026-09-01T09:35:10+0000", "closeTime": "2026-09-03T14:00:00+0000",
                "orderLegCollection": [{"instrument": {"symbol": "AAPL", "assetType": "EQUITY"}, "quantity": 100}],
                "orderActivityCollection": [{"executionLegs": [{"quantity": 100, "price": 155.50}]}],
            },
            {
                "orderId": 2004, "orderStrategyType": "SINGLE", "status": "CANCELED",
                "orderLegCollection": [{"instrument": {"symbol": "AAPL", "assetType": "EQUITY"}, "quantity": 100}],
            },
        ],
    }],
}
TIER2_ENTRY_ORDER = {
    "orderId": 3001, "orderStrategyType": "SINGLE", "status": "FILLED",
    "enteredTime": "2026-08-20T10:00:00+0000", "closeTime": "2026-08-20T10:00:00+0000",
    "orderLegCollection": [{"instrument": {"symbol": "MSFT", "assetType": "EQUITY"}, "quantity": 50}],
    "orderActivityCollection": [{"executionLegs": [{"quantity": 50, "price": 300.00}]}],
}
TIER2_EXIT_ORDER = {
    "orderId": 3002, "orderStrategyType": "SINGLE", "status": "FILLED",
    "enteredTime": "2026-08-25T11:00:00+0000", "closeTime": "2026-08-25T11:00:00+0000",
    "orderLegCollection": [{"instrument": {"symbol": "MSFT", "assetType": "EQUITY"}, "quantity": 50}],
    "orderActivityCollection": [{"executionLegs": [{"quantity": 50, "price": 310.00}]}],
}


def _fake_get_orders_for_account(account_hash, **kwargs):
    """Stand-in for the real Schwab call -- returns the 3 fixture orders
    regardless of the date window passed in. No network access."""
    return [TIER1_ORDER, TIER2_ENTRY_ORDER, TIER2_EXIT_ORDER]


def main() -> None:
    _compile_all()
    scratch = _build_scratch_db()

    import infrastructure.db_reader as reader_mod  # noqa: E402
    import infrastructure.schwab_order_puller as puller_mod  # noqa: E402
    import schemas  # noqa: E402
    from infrastructure.db_order_writer import insert_order

    # ---- Regression: db_reader.py's pre-existing functions still present ----
    for fn_name in (
        "get_all_trades", "get_trades_by_date_range", "get_open_trades",
        "get_open_trade_for_symbol", "get_trade_by_symbol_and_date",
        "get_exits_for_trade", "get_trade_summary",
    ):
        if not hasattr(reader_mod, fn_name):
            _fail(f"regression: db_reader.py lost function {fn_name}")
    print("db_reader.py regression check: PASS (7 pre-existing functions intact)")

    # ---- Set up 5 orders covering every filter branch of get_open_real_orders ----
    def _mk(symbol, side, schwab_id, trade_mode="REAL", status="working"):
        return schemas.Order(
            account_id="AJZ6348", symbol=symbol, side=side, qty=1,
            submitted_ts=datetime(2026, 9, 1, 9, 0, 0),
            schwab_order_id=schwab_id, trade_mode=trade_mode, status=status,
        )

    order_x = insert_order(scratch, _mk("AAPL", "long", "2001"))       # resolves Tier 1
    order_y = insert_order(scratch, _mk("MSFT", "long", "3001"))       # resolves Tier 2
    order_z = insert_order(scratch, _mk("NVDA", "long", "9999"))       # not in pull
    order_w = insert_order(scratch, _mk("TSLA", "long", None))         # no schwab_order_id -- excluded
    order_v = insert_order(scratch, _mk("GOOG", "long", "4001", trade_mode="PAPER"))  # PAPER -- excluded
    order_u = insert_order(scratch, _mk("META", "long", "5001", status="closed"))     # closed -- excluded

    candidates = reader_mod.get_open_real_orders(scratch)
    candidate_ids = {row["order_id"] for row in candidates}
    if candidate_ids != {order_x, order_y, order_z}:
        _fail(
            f"get_open_real_orders() wrong candidate set: expected "
            f"{{order_x, order_y, order_z}} = {{{order_x}, {order_y}, {order_z}}}, "
            f"got {candidate_ids}"
        )
    print(f"get_open_real_orders() filter check: PASS (correctly excluded no-id/PAPER/closed orders, {len(candidates)} candidates)")

    # ---- Mock the live Schwab call, run the real orchestrator ----
    puller_mod.get_orders_for_account = _fake_get_orders_for_account

    import application.reconcile_command as recon_cmd  # noqa: E402
    counts = recon_cmd.reconcile_live_orders(
        scratch, account_hash="FAKE_HASH",
        from_entered_datetime="2026-08-01T00:00:00+0000",
        to_entered_datetime="2026-09-07T00:00:00+0000",
    )

    if counts != {"reconciled": 2, "still_open": 0, "not_in_pull": 1}:
        _fail(f"reconcile_live_orders() counts wrong: {counts}")
    print(f"reconcile_live_orders() counts check: PASS ({counts})")

    row_x = scratch.execute("SELECT status, realized_pnl FROM orders WHERE order_id = ?", (order_x,)).fetchone()
    if row_x["status"] != "closed" or row_x["realized_pnl"] != 525.00:
        _fail(f"order_x (Tier 1) not updated correctly: {dict(row_x)}")

    row_y = scratch.execute("SELECT status, realized_pnl FROM orders WHERE order_id = ?", (order_y,)).fetchone()
    if row_y["status"] != "closed" or row_y["realized_pnl"] != 500.00:
        _fail(f"order_y (Tier 2) not updated correctly: {dict(row_y)}")

    row_z = scratch.execute("SELECT status FROM orders WHERE order_id = ?", (order_z,)).fetchone()
    if row_z["status"] == "closed":
        _fail(f"order_z should NOT have been reconciled (not in pull), but status={row_z['status']}")

    print("Per-order outcome check: PASS (order_x/y closed with correct P&L, order_z left alone)")

    trades_count = scratch.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    if trades_count != 2:
        _fail(f"expected exactly 2 promoted trades, found {trades_count}")
    print(f"Promotion count check: PASS ({trades_count} trades promoted)")

    scratch.close()
    print("PASS: db_reader.py extension and reconcile_command.py validated end-to-end.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
