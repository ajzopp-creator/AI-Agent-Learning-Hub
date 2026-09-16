"""
run_this_P020_20260907_205600.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 8 of 18).
Validates cli.py's new 'reconcile' subcommand and
reconcile_command.py's new run_reconcile_command() CLI wrapper.

NO real Schwab API call, NO real database connection anywhere in this
script. schwab_positions.get_account_hash, infrastructure.db_client.
get_connection, and reconcile_command.reconcile_live_orders are all
monkeypatched with fakes before anything is invoked.

Do not change test assertions.
"""
from __future__ import annotations

import io
import py_compile
import sys
import warnings
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path

DATABASE_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
)

FILES = {
    "reconcile_command.py": DATABASE_DIR / "application" / "reconcile_command.py",
    "cli.py": DATABASE_DIR / "cli.py",
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

    sys.path.insert(0, str(DATABASE_DIR))
    import application.reconcile_command as recon_cmd  # noqa: E402
    import cli  # noqa: E402
    import infrastructure.db_client as db_client_mod  # noqa: E402
    import infrastructure.schwab_positions as positions_mod  # noqa: E402

    # ---- Mock every external dependency ----
    calls = {}

    def fake_get_account_hash(last4):
        calls["last4"] = last4
        return "FAKE_HASH_ABC"

    def fake_get_connection():
        import sqlite3
        calls["get_connection_called"] = True
        return sqlite3.connect(":memory:")

    def fake_reconcile_live_orders(conn, account_hash, from_entered_datetime, to_entered_datetime):
        calls["account_hash"] = account_hash
        calls["from"] = from_entered_datetime
        calls["to"] = to_entered_datetime
        return {"reconciled": 1, "still_open": 2, "not_in_pull": 0}

    positions_mod.get_account_hash = fake_get_account_hash
    db_client_mod.get_connection = fake_get_connection
    recon_cmd.reconcile_live_orders = fake_reconcile_live_orders

    # ---- Test 1: run_reconcile_command() directly, happy path ----
    buf = io.StringIO()
    with redirect_stdout(buf):
        recon_cmd.run_reconcile_command("AJZ", "2026-08-01", "2026-09-07")
    output = buf.getvalue()

    if calls.get("last4") != "6348":
        _fail(f"last4 resolution wrong: expected '6348' (from AJZ6348), got {calls.get('last4')!r}")
    if calls.get("account_hash") != "FAKE_HASH_ABC":
        _fail(f"account_hash not passed through: got {calls.get('account_hash')!r}")
    if calls.get("from") != "2026-08-01" or calls.get("to") != "2026-09-07":
        _fail(f"start/end not passed through: from={calls.get('from')!r}, to={calls.get('to')!r}")
    if not calls.get("get_connection_called"):
        _fail("get_connection() was never called")
    if "closed: 1" not in output or "still open: 2" not in output or "not in pull window: 0" not in output:
        _fail(f"printed summary missing expected counts, got: {output!r}")
    print("run_reconcile_command() happy-path check: PASS (account resolution, pass-through, output)")

    # ---- Test 2: account hash resolution failure -> sys.exit(1), no crash ----
    positions_mod.get_account_hash = lambda last4: None
    try:
        recon_cmd.run_reconcile_command("AJZ", "2026-08-01", "2026-09-07")
        _fail("expected SystemExit when account hash can't be resolved")
    except SystemExit as exc:
        if exc.code != 1:
            _fail(f"expected exit code 1, got {exc.code}")
    print("run_reconcile_command() hash-failure check: PASS (SystemExit(1), no crash)")

    positions_mod.get_account_hash = fake_get_account_hash  # restore for cli.py tests below

    # ---- Test 3: cli.py argparse wiring dispatches to run_reconcile_command ----
    dispatch_calls = {}

    def fake_run_reconcile_command(account, start, end):
        dispatch_calls["account"] = account
        dispatch_calls["start"] = start
        dispatch_calls["end"] = end

    recon_cmd.run_reconcile_command = fake_run_reconcile_command

    sys.argv = ["cli.py", "reconcile", "--account", "IRA", "--start", "2026-01-01", "--end", "2026-02-01"]
    exit_code = cli.main()
    if exit_code != 0:
        _fail(f"cli.py reconcile dispatch: expected return 0, got {exit_code}")
    if dispatch_calls != {"account": "IRA", "start": "2026-01-01", "end": "2026-02-01"}:
        _fail(f"cli.py reconcile dispatch: wrong args passed through, got {dispatch_calls}")
    print("cli.py reconcile dispatch check: PASS (args parsed and passed through correctly)")

    # ---- Test 4: --account defaults to AJZ when omitted ----
    dispatch_calls.clear()
    sys.argv = ["cli.py", "reconcile", "--start", "2026-01-01", "--end", "2026-02-01"]
    cli.main()
    if dispatch_calls.get("account") != "AJZ":
        _fail(f"--account default wrong: expected 'AJZ', got {dispatch_calls.get('account')!r}")
    print("cli.py --account default check: PASS")

    # ---- Test 5: --start/--end are required -- omitting one raises SystemExit ----
    sys.argv = ["cli.py", "reconcile", "--account", "AJZ"]
    try:
        cli.main()
        _fail("expected SystemExit when --start/--end are omitted (argparse required=True)")
    except SystemExit:
        pass
    print("cli.py required-args check: PASS (SystemExit when --start/--end missing)")

    # ---- Test 6: pre-existing 'auth' subcommand still dispatches (regression) ----
    import application.schwab_auth_commands as auth_mod  # noqa: E402
    auth_calls = {}
    auth_mod.cmd_auth_all = lambda: auth_calls.setdefault("all", True) or 0
    auth_mod.cmd_auth = lambda project: auth_calls.setdefault("project", project) or 0

    sys.argv = ["cli.py", "auth"]
    cli.main()
    if not auth_calls.get("all"):
        _fail("regression: 'auth' with no --project should default to ALL and call cmd_auth_all()")

    sys.argv = ["cli.py", "auth", "--project", "P_020"]
    cli.main()
    if auth_calls.get("project") != "P_020":
        _fail(f"regression: 'auth --project P_020' should call cmd_auth('P_020'), got {auth_calls.get('project')!r}")
    print("cli.py 'auth' regression check: PASS (pre-existing subcommand unaffected)")

    print("PASS: cli.py reconcile subcommand and run_reconcile_command() validated (no live calls made).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
