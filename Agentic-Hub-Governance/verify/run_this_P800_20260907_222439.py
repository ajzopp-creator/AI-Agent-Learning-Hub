"""
run_this_P800_20260907_222439.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 11 of 18,
part 2+3 of 3: infrastructure\\p020_reader.py, domain\\note_merger.py,
application\\regenerate_command.py).

No real P_020 database connection (infrastructure.db_client.
get_connection is monkeypatched to a scratch in-memory DB) and no real
vault write anywhere (write_to_vault is monkeypatched throughout).

IMPORTANT: regenerate_command.py imports get_closed_p400_orders,
find_note_by_order_id, and write_to_vault at MODULE TOP LEVEL (unlike
some other files this session that import lazily per-call) -- learned
the hard way in the file-10 handoff that patching the ORIGIN modules
for a top-level import doesn't reach the caller. This script patches
all three directly on the regenerate_command module object.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sqlite3
import sys
import warnings
from datetime import date, datetime
from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
P800_PYTHON_DIR = HUB_ROOT / "projects" / "P_800_Automation_Note_Taking" / "python"
P_020_DATABASE_DIR = (
    HUB_ROOT / "projects" / "P_020_AJZStrategies_PerformanceAnalysisSystem"
    / "python" / "database"
)

FILES = {
    "p020_reader.py": P800_PYTHON_DIR / "p400_regenerate" / "infrastructure" / "p020_reader.py",
    "note_merger.py": P800_PYTHON_DIR / "p400_regenerate" / "domain" / "note_merger.py",
    "regenerate_command.py": P800_PYTHON_DIR / "p400_regenerate" / "application" / "regenerate_command.py",
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


def main() -> None:
    _compile_all()

    sys.path.insert(0, str(P800_PYTHON_DIR))
    sys.path.insert(0, str(HUB_ROOT))

    # ---- p020_reader.py: mock P_020's get_connection, scratch DB ----
    sys.path.insert(0, str(P_020_DATABASE_DIR))
    import infrastructure.db_client as p020_db_client_mod  # noqa: E402
    import infrastructure.migration_add_orders_table as migration_mod  # noqa: E402

    scratch = sqlite3.connect(":memory:")
    scratch.row_factory = sqlite3.Row
    scratch.execute(migration_mod.ORDERS_TABLE_SQL)
    # 4 rows covering every filter branch of get_closed_p400_orders().
    scratch.executemany(
        "INSERT INTO orders (account_id, symbol, side, qty, submitted_ts, "
        "schwab_order_id, status, source_project, entry_date, close_date, "
        "realized_pnl) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("AJZ6348", "AAPL", "long", 100, "2026-09-01T09:00:00", "7001",
             "closed", "P400", "2026-09-01", "2026-09-03", 525.00),   # match
            ("AJZ6348", "MSFT", "long", 50, "2026-08-20T10:00:00", "3002",
             "closed", "P020", "2026-08-20", "2026-08-25", 500.00),   # wrong source_project
            ("AJZ6348", "NVDA", "long", 10, "2026-09-05T09:00:00", "7003",
             "working", "P400", None, None, None),                    # not closed
            ("AJZ6348", "TSLA", "long", 5, "2026-09-06T09:00:00", None,
             "closed", "P400", "2026-09-06", "2026-09-07", 100.00),   # no schwab_order_id
        ],
    )
    scratch.commit()

    class _KeepAliveConn:
        """Proxy so get_closed_p400_orders()'s finally: conn.close()
        is a no-op. sqlite3.Connection is an immutable C type --
        instance attributes (close_orig) cannot be assigned.
        """

        def __init__(self, conn):
            self._conn = conn

        def close(self):
            return None

        def __getattr__(self, name):
            return getattr(self._conn, name)

    p020_db_client_mod.get_connection = lambda: _KeepAliveConn(scratch)

    import p400_regenerate.infrastructure.p020_reader as reader_mod  # noqa: E402

    orders = reader_mod.get_closed_p400_orders()
    if len(orders) != 1:
        _fail(f"expected exactly 1 closed P400 order, got {len(orders)}: {orders}")
    if orders[0]["schwab_order_id"] != "7001" or orders[0]["realized_pnl"] != 525.00:
        _fail(f"wrong order returned: {orders[0]}")
    print("p020_reader.py filter check: PASS (1 of 4 rows correctly matched)")
    scratch.close()

    # ---- note_merger.py: pure logic, no I/O ----
    import p400_regenerate.domain.note_merger as merger_mod  # noqa: E402

    existing = {
        "signal_date": "2026-09-01", "ticker": "AAPL",
        "council_verdict": "APPROVED", "lifecycle_status": "SUBMITTED",
        "order_id": "7001", "entry_price": "150.00",
        # P_800-injected keys that must be stripped before re-submission:
        "note_version": "1", "write_route": "BUY",
        "write_route_history": "[...]", "source": "P_400/cli_evaluate",
        # scanner bookkeeping keys, also must be stripped:
        "_note_path": r"C:\fake\path\2026-09-01_AAPL.md", "_schema": "P400",
    }
    fake_order = {
        "order_id": 1, "schwab_order_id": "7001",
        "entry_date": date(2026, 9, 1), "close_date": date(2026, 9, 3),
        "realized_pnl": 525.00,
    }
    merged = merger_mod.merge_reconciled_order(existing, fake_order)

    if merged.get("lifecycle_status") != "CLOSED":
        _fail(f"lifecycle_status wrong: {merged.get('lifecycle_status')!r}")
    if merged.get("entry_date") != "2026-09-01" or merged.get("close_date") != "2026-09-03":
        _fail(f"entry_date/close_date wrong: {merged.get('entry_date')!r}, {merged.get('close_date')!r}")
    if merged.get("realized_pnl") != 525.00:
        _fail(f"realized_pnl wrong: {merged.get('realized_pnl')!r}")
    if merged.get("ticker") != "AAPL" or merged.get("signal_date") != "2026-09-01":
        _fail(f"original fields not preserved: ticker={merged.get('ticker')!r}, signal_date={merged.get('signal_date')!r}")
    for stripped in ("note_version", "write_route", "write_route_history", "source", "_note_path", "_schema"):
        if stripped in merged:
            _fail(f"P_800-internal/scanner key '{stripped}' should have been stripped, but is present: {merged[stripped]!r}")
    print("note_merger.py check: PASS (reconciled fields merged, originals preserved, internal keys stripped)")

    # ---- regenerate_command.py: orchestration, all 3 deps mocked ----
    import p400_regenerate.application.regenerate_command as rc_mod  # noqa: E402

    write_calls = []

    def fake_write_to_vault(schema, data):
        write_calls.append((schema, data))
        return True

    # Scenario A: normal sync.
    rc_mod.get_closed_p400_orders = lambda: [fake_order]
    rc_mod.find_note_by_order_id = lambda oid: dict(existing) if oid == "7001" else None
    rc_mod.write_to_vault = fake_write_to_vault

    counts_a = rc_mod.run_regenerate()
    if counts_a != {"synced": 1, "already_synced": 0, "no_note_found": 0}:
        _fail(f"Scenario A counts wrong: {counts_a}")
    if len(write_calls) != 1 or write_calls[0][0] != "P400":
        _fail(f"Scenario A: write_to_vault not called correctly: {write_calls}")
    print("regenerate_command.py Scenario A (normal sync) check: PASS")

    # Scenario B: already synced (note's lifecycle_status already CLOSED).
    write_calls.clear()
    already_closed = {**existing, "lifecycle_status": "CLOSED"}
    rc_mod.find_note_by_order_id = lambda oid: dict(already_closed)
    counts_b = rc_mod.run_regenerate()
    if counts_b != {"synced": 0, "already_synced": 1, "no_note_found": 0}:
        _fail(f"Scenario B counts wrong: {counts_b}")
    if write_calls:
        _fail(f"Scenario B: write_to_vault should NOT be called, but was: {write_calls}")
    print("regenerate_command.py Scenario B (already synced, no write) check: PASS")

    # Scenario C: no matching note found.
    rc_mod.find_note_by_order_id = lambda oid: None
    counts_c = rc_mod.run_regenerate()
    if counts_c != {"synced": 0, "already_synced": 0, "no_note_found": 1}:
        _fail(f"Scenario C counts wrong: {counts_c}")
    print("regenerate_command.py Scenario C (no note found) check: PASS")

    # Scenario D: write_to_vault raises -- must not crash, must not count as synced.
    rc_mod.find_note_by_order_id = lambda oid: dict(existing)
    rc_mod.write_to_vault = lambda schema, data: (_ for _ in ()).throw(RuntimeError("simulated vault write failure"))
    try:
        counts_d = rc_mod.run_regenerate()
    except Exception as exc:
        _fail(f"run_regenerate() must not raise on a write failure, but raised: {exc}")
    if counts_d["synced"] != 0:
        _fail(f"Scenario D: synced should stay 0 on write failure, got {counts_d}")
    print("regenerate_command.py Scenario D (write failure, no crash) check: PASS")

    print("PASS: p020_reader.py, note_merger.py, and regenerate_command.py all validated (no real DB/vault touched).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
