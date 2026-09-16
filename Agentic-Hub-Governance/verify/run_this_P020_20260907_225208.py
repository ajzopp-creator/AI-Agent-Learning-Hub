"""
run_this_P020_20260907_225208.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 13 of 18 --
FINAL file of this WO scope item: db_reader.py's get_open_paper_orders,
reconcile_command.py's paper wiring + run_reconcile_command() refactor,
cli.py's --paper/--statement flags).

No live Schwab call, no real production DB, no real vault -- everything
mocked/scratch as established throughout this session. The paper path
DOES exercise the real, unmocked paper_order_history_parser.py against
a synthetic statement file (same verbatim-real-row content as the
file-12 handoff), since that file has no external dependencies to mock.

Do not change test assertions.
"""
from __future__ import annotations

import io
import py_compile
import sqlite3
import sys
import tempfile
import warnings
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

DATABASE_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)

FILES = {
    "db_reader.py": DATABASE_DIR / "infrastructure" / "db_reader.py",
    "reconcile_command.py": DATABASE_DIR / "application" / "reconcile_command.py",
    "cli.py": DATABASE_DIR / "cli.py",
}

DONE_MARKER = Path(__file__).with_suffix(".py.done")

# Same verbatim-real-row synthetic statement as the file-12 handoff.
SYNTHETIC_CSV = """Account Statement for D-68748526 (ira) since 1/1/26 through 8/17/26

Account Order History
Notes,,Time Placed,Spread,Side,Qty,Pos Effect,Symbol,Exp,Strike,Type,PRICE,,TIF,Status,Order ID
,,7/24/26 10:31:28,STOCK,SELL,-10,TO CLOSE,MRCY,,,STOCK,~,MKT,GTC,FILLED,="5374526395"
,,,TRG BY #5374526392,,,,,,,,BASE-6.43,STP,STD,,
,,,OCO #5374526393,,,,,,,,99.83,STP,,,
,,7/24/26 10:31:28,STOCK,SELL,-10,TO CLOSE,MRCY,,,STOCK,BASE+1.00,LMT,GTC,CANCELED,="5374526394"
,,,TRG BY #5374526392,,,,,,,,107.26,LMT,,,
,,,OCO #5374526393,,,,,,,,,,,,
,,7/24/26 10:31:28,STOCK,BUY,+10,TO OPEN,MRCY,,,STOCK,106.26,LMT,DAY,FILLED,="5374526392"

Futures Statements
Trade Date,Exec Date,Exec Time,Type,Ref #,Description,Misc Fees,Commissions & Fees,Amount,Balance
"""


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


def main() -> None:
    _compile_all()

    sys.path.insert(0, str(DATABASE_DIR))
    import infrastructure.db_client as db_client_mod  # noqa: E402
    import infrastructure.db_reader as reader_mod  # noqa: E402
    import infrastructure.migration_add_orders_table as migration_mod  # noqa: E402
    import schemas  # noqa: E402
    from infrastructure.db_order_writer import insert_order

    # ---- db_reader.py: get_open_paper_orders filter + regression ----
    scratch = sqlite3.connect(":memory:")
    scratch.row_factory = sqlite3.Row
    scratch.execute(migration_mod.ORDERS_TABLE_SQL)
    scratch.commit()

    def _mk(symbol, schwab_id, trade_mode="PAPER", status="working"):
        return schemas.Order(
            account_id="AJZ6348", symbol=symbol, side="long", qty=10,
            submitted_ts=datetime(2026, 7, 24, 10, 0, 0),
            schwab_order_id=schwab_id, trade_mode=trade_mode, status=status,
        )

    order_paper = insert_order(scratch, _mk("MRCY", "5374526392"))
    insert_order(scratch, _mk("AAPL", "9001", trade_mode="REAL"))  # wrong mode
    insert_order(scratch, _mk("TSLA", None))  # no schwab_order_id

    for fn_name in ("get_all_trades", "get_open_real_orders"):
        if not hasattr(reader_mod, fn_name):
            _fail(f"regression: db_reader.py lost function {fn_name}")

    paper_orders = reader_mod.get_open_paper_orders(scratch)
    if len(paper_orders) != 1 or paper_orders[0]["order_id"] != order_paper:
        _fail(f"get_open_paper_orders() wrong result: {[dict(r) for r in paper_orders]}")
    print("db_reader.py get_open_paper_orders() filter check: PASS (regression intact)")

    # ---- reconcile_command.py: paper path, real unmocked parser ----
    class _KeepAliveConn:
        """Proxy so run_reconcile_command()'s finally: conn.close() is
        a no-op. sqlite3.Connection is an immutable C type -- instance
        attributes (close_orig) cannot be assigned.
        """

        def __init__(self, conn):
            self._conn = conn

        def close(self):
            return None

        def __getattr__(self, name):
            return getattr(self._conn, name)

    db_client_mod.get_connection = lambda: _KeepAliveConn(scratch)

    import application.reconcile_command as rc_mod  # noqa: E402

    tmp_dir = Path(tempfile.mkdtemp(prefix="reconcile_paper_test_"))
    stmt_path = tmp_dir / "synthetic_statement.csv"
    stmt_path.write_text(SYNTHETIC_CSV, encoding="utf-8")

    try:
        counts = rc_mod.reconcile_paper_orders(scratch, str(stmt_path))
        if counts["reconciled"] != 1:
            _fail(f"reconcile_paper_orders() counts wrong: {counts}")

        row = scratch.execute(
            "SELECT status, realized_pnl FROM orders WHERE order_id = ?", (order_paper,)
        ).fetchone()
        if row["status"] != "closed":
            _fail(f"paper order should be closed, got status={row['status']!r}")
        # MRCY's exit was a MKT order ('~' price) -- P&L correctly None,
        # not fabricated (same behavior proven directly in file 12).
        if row["realized_pnl"] is not None:
            _fail(f"expected realized_pnl=None (MKT exit, unrecoverable price), got {row['realized_pnl']}")
        print(f"reconcile_paper_orders() end-to-end check: PASS (counts={counts}, status=closed, pnl=None as expected)")

        # No open paper orders left -> should short-circuit cleanly.
        counts2 = rc_mod.reconcile_paper_orders(scratch, str(stmt_path))
        if counts2 != {"reconciled": 0, "still_open": 0, "not_in_pull": 0}:
            _fail(f"expected all-zero counts with no open paper orders left, got {counts2}")
        print("reconcile_paper_orders() no-open-orders short-circuit check: PASS")
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # ---- reconcile_command.py: live-path regression (file-8 style) ----
    calls = {}
    rc_mod.reconcile_live_orders = lambda conn, account_hash, s, e: calls.update(
        {"account_hash": account_hash, "s": s, "e": e}
    ) or {"reconciled": 2, "still_open": 1, "not_in_pull": 0}

    import infrastructure.schwab_positions as positions_mod  # noqa: E402
    positions_mod.get_account_hash = lambda last4: "FAKE_HASH"

    buf = io.StringIO()
    with redirect_stdout(buf):
        rc_mod.run_reconcile_command("AJZ", "2026-08-01", "2026-09-07")
    if "closed: 2" not in buf.getvalue():
        _fail(f"live-path regression: unexpected output: {buf.getvalue()!r}")
    print("run_reconcile_command() live-path regression check: PASS")

    # Missing --start/--end on the live path -> sys.exit(1), not a crash
    # (moved from argparse required=True to an internal check, since
    # --paper mode legitimately omits both).
    try:
        with redirect_stdout(io.StringIO()):
            rc_mod.run_reconcile_command("AJZ", None, None)
        _fail("expected SystemExit when --start/--end missing on the live path")
    except SystemExit as exc:
        if exc.code != 1:
            _fail(f"expected exit code 1, got {exc.code}")
    print("run_reconcile_command() missing-start/end check: PASS (SystemExit(1))")

    # --paper without --statement -> sys.exit(1).
    try:
        with redirect_stdout(io.StringIO()):
            rc_mod.run_reconcile_command("AJZ", paper=True, statement=None)
        _fail("expected SystemExit when --paper is set but --statement is missing")
    except SystemExit as exc:
        if exc.code != 1:
            _fail(f"expected exit code 1, got {exc.code}")
    print("run_reconcile_command() missing-statement check: PASS (SystemExit(1))")

    scratch.close()

    # ---- cli.py: --paper/--statement dispatch ----
    import cli  # noqa: E402

    dispatch_calls = {}
    rc_mod.run_reconcile_command = lambda account, start, end, paper=False, statement=None: (
        dispatch_calls.update(
            {"account": account, "start": start, "end": end, "paper": paper, "statement": statement}
        )
    )

    sys.argv = ["cli.py", "reconcile", "--paper", "--statement", "C:\\fake\\statement.csv"]
    exit_code = cli.main()
    if exit_code != 0:
        _fail(f"cli.py --paper dispatch: expected return 0, got {exit_code}")
    if not dispatch_calls.get("paper") or dispatch_calls.get("statement") != "C:\\fake\\statement.csv":
        _fail(f"cli.py --paper dispatch: wrong args passed through: {dispatch_calls}")
    if dispatch_calls.get("start") is not None or dispatch_calls.get("end") is not None:
        _fail(f"cli.py --paper dispatch: start/end should be None when omitted, got {dispatch_calls}")
    print("cli.py --paper/--statement dispatch check: PASS")

    print("PASS: db_reader.py, reconcile_command.py, and cli.py all validated -- WO-P400-E6.001 Scope item 2 build complete.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
