"""
run_this_P020_20260907_210328.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 9 of 18).
Validates shared_resources\\python_utils\\p020_order_writer.py --
lazy sys.path insertion, submit_order() end-to-end against a scratch
orders table, and dedup behavior. This file lives outside any single
project (shared_resources\\), unlike files 1-8 which were all inside
P_020's own project folder.

No real P_020 database connection anywhere in this script --
infrastructure.db_client.get_connection is monkeypatched to return an
in-memory scratch DB before submit_order() is ever called.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sqlite3
import sys
import warnings
from datetime import datetime
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
TARGET = HUB_ROOT / "shared_resources" / "python_utils" / "p020_order_writer.py"
P_020_DATABASE_DIR = (
    HUB_ROOT / "projects" / "P_020_AJZStrategies_PerformanceAnalysisSystem"
    / "python" / "database"
)

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


def main() -> None:
    # 1. Durable signal + compile check.
    if not TARGET.exists():
        _fail(f"target file not found on disk: {TARGET}")
    line_count = len(TARGET.read_text().splitlines())
    print(f"Line count: {line_count}")
    if not (60 <= line_count <= 130):
        _fail(f"line count {line_count} outside expected [60, 130]")

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    # 2. Lazy-import check: importing the module alone must NOT touch
    #    P_020's sys.path yet.
    sys.path.insert(0, str(HUB_ROOT))
    import shared_resources.python_utils.p020_order_writer as writer_mod  # noqa: E402

    if str(P_020_DATABASE_DIR) in sys.path:
        _fail(
            "P_020's database dir is already on sys.path after a bare "
            "import -- _load_p020() must only run inside submit_order(), "
            "not at module import time"
        )
    print("Lazy-import check: PASS (P_020 sys.path untouched by import alone)")

    # 3. Now insert the path ourselves (separately from the module under
    #    test) so we can reach in and monkeypatch db_client.get_connection
    #    before submit_order() is ever called for real.
    sys.path.insert(0, str(P_020_DATABASE_DIR))
    import infrastructure.db_client as db_client_mod  # noqa: E402
    import infrastructure.migration_add_orders_table as migration_mod  # noqa: E402

    scratch = sqlite3.connect(":memory:")
    scratch.row_factory = sqlite3.Row
    scratch.execute(migration_mod.ORDERS_TABLE_SQL)
    scratch.commit()

    class _KeepAliveConn:
        """Proxy so submit_order()'s finally: conn.close() is a no-op.

        sqlite3.Connection is an immutable C type -- neither instance
        attributes nor Connection.close can be assigned -- so the
        original close_original/close monkeypatch cannot work.
        """

        def __init__(self, conn):
            self._conn = conn

        def close(self):
            return None

        def __getattr__(self, name):
            return getattr(self._conn, name)

    def fake_get_connection():
        return _KeepAliveConn(scratch)  # same DB; close() does not kill it

    db_client_mod.get_connection = fake_get_connection

    # 4. submit_order() happy path.
    order_id = writer_mod.submit_order(
        account_id="AJZ6348", symbol="AAPL", side="long", qty=100,
        why_code="P_115", sig_code="BTD_SIGNAL",
        planned_entry_price=150.00, planned_stop_price=145.00,
        planned_target_price=160.00, schwab_order_id="7001",
        council_verdict="APPROVED", source_project="P400",
    )
    if order_id is None:
        _fail("submit_order() returned None for a fresh (non-duplicate) order")

    row = scratch.execute(
        "SELECT account_id, symbol, side, qty, why_code, sig_code, "
        "planned_entry_price, schwab_order_id, source_project, trade_mode, "
        "confidence_tier FROM orders WHERE order_id = ?",
        (order_id,),
    ).fetchone()
    if row is None:
        _fail("submitted order not found in scratch orders table")
    if row["account_id"] != "AJZ6348" or row["symbol"] != "AAPL":
        _fail(f"submitted row has wrong account/symbol: {dict(row)}")
    if row["why_code"] != "P_115" or row["sig_code"] != "BTD_SIGNAL":
        _fail(f"submitted row has wrong attribution fields: {dict(row)}")
    if row["planned_entry_price"] != 150.00:
        _fail(f"planned_entry_price wrong: {row['planned_entry_price']}")
    if row["trade_mode"] != "REAL" or row["confidence_tier"] != "CONFIRMED":
        _fail(f"defaults wrong: trade_mode={row['trade_mode']}, confidence_tier={row['confidence_tier']}")
    print(f"submit_order() happy-path check: PASS (order_id={order_id})")

    # 5. Dedup: same schwab_order_id -> None, no second row inserted.
    dup = writer_mod.submit_order(
        account_id="AJZ6348", symbol="AAPL", side="long", qty=100,
        schwab_order_id="7001",
    )
    if dup is not None:
        _fail(f"submit_order() should skip duplicate schwab_order_id, got {dup}")
    count = scratch.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    if count != 1:
        _fail(f"expected exactly 1 order row after the duplicate attempt, found {count}")
    print("submit_order() dedup check: PASS (no duplicate row inserted)")

    scratch.close()
    print("PASS: p020_order_writer.py validated (no real P_020 database touched).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
