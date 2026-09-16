"""
run_this_P020_20260907_214809.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 9 fix).
Validates p020_order_writer.py's sys.modules stash/restore fix for the
live bug Claude Code found and reported in the file-10 handoff: a
caller with its own top-level "infrastructure"/"domain" packages already
loaded (P_400 has both) previously made _load_p020()'s
"from infrastructure.db_client import ..." resolve against the CALLER's
cached package instead of P_020's, raising ModuleNotFoundError.

This script deliberately RECREATES the collision (loads P_400's real
infrastructure.eval_cache FIRST, exactly like a real P_400 process
would) before calling submit_order(), then confirms both that P_020's
side resolves correctly AND that P_400's own infrastructure package is
still intact and usable afterward.

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
P_400_PYTHON_DIR = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python"

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
    if not (80 <= line_count <= 180):
        _fail(f"line count {line_count} outside expected [80, 180]")

    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    # 2. Deliberately recreate the collision: load P_400's REAL
    #    infrastructure.eval_cache first, exactly like a real P_400
    #    process would before ever touching this bridge.
    sys.path.insert(0, str(P_400_PYTHON_DIR))
    import infrastructure.eval_cache as p400_eval_cache  # noqa: E402

    if "infrastructure" not in sys.modules:
        _fail("setup error: P_400's infrastructure package did not load as expected")
    p400_infra_id_before = id(sys.modules["infrastructure"])
    print("Collision setup: PASS (P_400's infrastructure.eval_cache loaded first, as in a real process)")

    # 3. Lazy-import check (same as file-9 handoff): bare import of the
    #    bridge module must not touch P_020's sys.path.
    sys.path.insert(0, str(HUB_ROOT))
    import shared_resources.python_utils.p020_order_writer as writer_mod  # noqa: E402

    if str(P_020_DATABASE_DIR) in sys.path:
        _fail("P_020's database dir already on sys.path after a bare import of the bridge module")
    print("Lazy-import check: PASS (regression from file-9 handoff)")

    # 4. Mock P_020's get_connection -- reached THROUGH the collision,
    #    proving the fix actually resolves P_020's infrastructure package.
    sys.path.insert(0, str(P_020_DATABASE_DIR))
    stashed_infra = sys.modules.pop("infrastructure", None)
    stashed_infra_submods = {
        k: sys.modules.pop(k) for k in list(sys.modules) if k.startswith("infrastructure.")
    }
    import infrastructure.db_client as p020_db_client_mod  # noqa: E402
    import infrastructure.migration_add_orders_table as migration_mod  # noqa: E402
    # Restore P_400's stash immediately -- we only needed a moment's access
    # to reach P_020's db_client module object itself, to monkeypatch it.
    del sys.modules["infrastructure"]
    for k in list(sys.modules):
        if k.startswith("infrastructure."):
            del sys.modules[k]
    if stashed_infra is not None:
        sys.modules["infrastructure"] = stashed_infra
    sys.modules.update(stashed_infra_submods)

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

    # _load_p020() re-imports db_client after wiping sys.modules, so a
    # patch on this setup-imported module object never reaches the
    # call. sqlite3.connect is what the freshly imported get_connection()
    # actually uses -- patch that instead.
    _orig_connect = sqlite3.connect
    sqlite3.connect = lambda *a, **k: _KeepAliveConn(scratch)

    # 5. Call submit_order() THROUGH the collision -- this is exactly the
    #    call that raised ModuleNotFoundError before the fix.
    order_id = writer_mod.submit_order(
        account_id="AJZ6348", symbol="AAPL", side="long", qty=100,
        why_code="P_115", schwab_order_id="8001",
    )
    if order_id is None:
        _fail("submit_order() returned None through the collision -- fix did not work")

    row = scratch.execute(
        "SELECT account_id, symbol FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    if row is None or row["account_id"] != "AJZ6348":
        _fail(f"order not correctly inserted through the collision: {dict(row) if row else None}")
    print(f"Collision fix check: PASS (submit_order() succeeded through the collision, order_id={order_id})")

    # 6. Confirm P_400's own infrastructure package is intact afterward --
    #    same object identity, not silently replaced by P_020's.
    if id(sys.modules["infrastructure"]) != p400_infra_id_before:
        _fail("P_400's infrastructure package identity changed after submit_order() -- restore didn't work")
    if not hasattr(p400_eval_cache, "read_eval_cache"):
        _fail("P_400's infrastructure.eval_cache lost its read_eval_cache function after submit_order()")
    print("Post-call restore check: PASS (P_400's own infrastructure package still intact and usable)")

    # 7. Call submit_order() a SECOND time -- confirms the stash/restore
    #    is repeatable, not a one-shot fix that breaks on reuse.
    order_id_2 = writer_mod.submit_order(
        account_id="AJZ6348", symbol="MSFT", side="long", qty=50,
        why_code="P_300", schwab_order_id="8002",
    )
    if order_id_2 is None or order_id_2 == order_id:
        _fail(f"second submit_order() call failed or returned same id: {order_id_2}")
    if id(sys.modules["infrastructure"]) != p400_infra_id_before:
        _fail("P_400's infrastructure package identity changed after the SECOND submit_order() call")
    print(f"Repeated-call check: PASS (second call succeeded, order_id={order_id_2}, P_400 infra still intact)")

    sqlite3.connect = _orig_connect
    scratch.close()
    print("PASS: p020_order_writer.py's sys.modules collision fix validated (P_400<->P_020 both intact).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
