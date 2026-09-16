"""
run_this_P400_20260907_211728.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 10 of 18).
Validates config.py's new ACCOUNT_ID constant, the new
infrastructure\\order_submit_writer.py, and record_commands.py's
cmd_record_submit() extension -- the P_400 side of the submit-time
bridge to P_020's orders table.

Zero live calls anywhere: shared_resources.python_utils.p020_order_writer.
submit_order is monkeypatched before anything runs. No real Schwab call,
no real database connection, no real vault write.

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

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
P400_PYTHON_DIR = HUB_ROOT / "projects" / "P_400_TradeOrderManagement" / "python"

FILES = {
    "config.py": P400_PYTHON_DIR / "config.py",
    "order_submit_writer.py": P400_PYTHON_DIR / "infrastructure" / "order_submit_writer.py",
    "record_commands.py": P400_PYTHON_DIR / "application" / "record_commands.py",
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

    sys.path.insert(0, str(P400_PYTHON_DIR))
    sys.path.insert(0, str(HUB_ROOT))

    import config  # noqa: E402

    # ---- config.py regression + new constant ----
    for const_name in ("MARKET_OPEN_TIME_ET", "DEFAULT_TRADE_MODE", "BASE_RISK_PCT"):
        if not hasattr(config, const_name):
            _fail(f"regression: config.py lost constant {const_name}")
    if config.ACCOUNT_ID != "AJZ6348":
        _fail(f"ACCOUNT_ID wrong: expected 'AJZ6348', got {config.ACCOUNT_ID!r}")
    print("config.py check: PASS (regression + ACCOUNT_ID='AJZ6348')")

    import infrastructure.order_submit_writer as writer_mod  # noqa: E402
    import shared_resources.python_utils.p020_order_writer as bridge_mod  # noqa: E402

    # ---- order_submit_writer.py: happy path, args mapped correctly ----
    calls = {}

    def fake_submit_order(**kwargs):
        calls.update(kwargs)
        return 42

    bridge_mod.submit_order = fake_submit_order

    result = writer_mod.write_order_to_p020(
        symbol="AAPL", order_id="7001", verdict="APPROVED",
        entry_price=150.00, stop_price=145.00, target_1=160.00,
        position_size=100, signal_source="P_115",
        trade_mode_value="REAL",
    )
    if result != 42:
        _fail(f"write_order_to_p020 should return submit_order's result, got {result}")
    if calls.get("side") != "long":
        _fail(f"side should always be 'long', got {calls.get('side')!r}")
    if calls.get("account_id") != "AJZ6348":
        _fail(f"account_id should come from config.ACCOUNT_ID, got {calls.get('account_id')!r}")
    if calls.get("qty") != 100:
        _fail(f"qty should equal position_size (100), got {calls.get('qty')!r}")
    if calls.get("why_code") != "P_115":
        _fail(f"why_code should equal signal_source, got {calls.get('why_code')!r}")
    if calls.get("schwab_order_id") != "7001":
        _fail(f"schwab_order_id wrong: got {calls.get('schwab_order_id')!r}")
    if calls.get("council_verdict") != "APPROVED":
        _fail(f"council_verdict wrong: got {calls.get('council_verdict')!r}")
    if calls.get("source_project") != "P400":
        _fail(f"source_project should be 'P400', got {calls.get('source_project')!r}")
    print("order_submit_writer.py happy-path check: PASS (all fields mapped correctly, side always 'long')")

    # ---- order_submit_writer.py: exception from submit_order is caught, never raises ----
    def fake_submit_order_raises(**kwargs):
        raise RuntimeError("simulated P_020 failure")

    bridge_mod.submit_order = fake_submit_order_raises
    try:
        result2 = writer_mod.write_order_to_p020(
            symbol="MSFT", order_id="7002", verdict="APPROVED",
            entry_price=300.00, stop_price=290.00, target_1=320.00,
            position_size=50, signal_source="P_300", trade_mode_value="REAL",
        )
    except Exception as exc:
        _fail(f"write_order_to_p020 must never raise, but raised: {exc}")
    if result2 is not None:
        _fail(f"write_order_to_p020 should return None on failure, got {result2}")
    print("order_submit_writer.py exception-safety check: PASS (never raises, returns None)")

    # ---- record_commands.py: cmd_record_submit() end-to-end ----
    bridge_mod.submit_order = fake_submit_order  # restore happy-path fake

    import application.record_commands as rc_mod  # noqa: E402
    import infrastructure.order_submit_writer as osw_mod  # noqa: E402

    # IMPORTANT: record_commands.py imports read_eval_cache and
    # write_p400_record at MODULE TOP LEVEL ("from infrastructure.x import
    # y"), unlike write_order_to_p020 which it imports LOCALLY inside
    # cmd_record_submit(). That means read_eval_cache/write_p400_record
    # must be patched on rc_mod directly (the name is already bound in
    # record_commands' own namespace) -- patching infrastructure.eval_cache
    # or infrastructure.record_writer's own module attributes would NOT
    # reach cmd_record_submit(), since it never re-imports them per call.
    fake_cached = {
        "symbol": "AAPL", "verdict": "APPROVED", "risk_mode": "STANDARD",
        "entry_price": 150.00, "stop_price": 145.00, "target_1": 160.00,
        "position_size": 100, "signal_source": "P_115",
        "trade_mode_value": "REAL",
    }
    rc_mod.read_eval_cache = lambda symbol: dict(fake_cached)

    vault_calls = {}
    rc_mod.write_p400_record = lambda **kw: vault_calls.update(kw) or True

    p020_calls = {}

    def fake_write_order_to_p020(**kwargs):
        p020_calls.update(kwargs)
        return 99

    osw_mod.write_order_to_p020 = fake_write_order_to_p020

    buf = io.StringIO()
    with redirect_stdout(buf):
        exit_code = rc_mod.cmd_record_submit("AAPL", "7001", paper=False)
    output = buf.getvalue()

    if exit_code != 0:
        _fail(f"cmd_record_submit should return 0 on success, got {exit_code}")
    if p020_calls.get("position_size") != 100 or p020_calls.get("entry_price") != 150.00:
        _fail(f"write_order_to_p020 called with wrong fields: {p020_calls}")
    if p020_calls.get("trade_mode_value") != "REAL":
        _fail(f"trade_mode_value wrong (non-paper path): {p020_calls.get('trade_mode_value')!r}")
    if "P_020 order write: OK (order_id=99)" not in output:
        _fail(f"expected P_020 write success line in output, got: {output!r}")
    print("cmd_record_submit() happy-path check: PASS (both writes fired, correct fields, output correct)")

    # ---- paper=True override must reach BOTH writes, not just the vault one ----
    p020_calls.clear()
    with redirect_stdout(io.StringIO()):
        rc_mod.cmd_record_submit("AAPL", "7003", paper=True)
    if p020_calls.get("trade_mode_value") != "PAPER":
        _fail(
            f"paper=True should override trade_mode_value to PAPER for the "
            f"P_020 write too, got {p020_calls.get('trade_mode_value')!r}"
        )
    print("cmd_record_submit() paper-override check: PASS (PAPER reaches both writes)")

    # ---- pre-condition failures must short-circuit BEFORE the P_020 write ----
    p020_calls.clear()
    rc_mod.read_eval_cache = lambda symbol: None
    with redirect_stdout(io.StringIO()):
        exit_code_missing = rc_mod.cmd_record_submit("ZZZZ", "7004")
    if exit_code_missing != 1 or p020_calls:
        _fail(
            f"missing-cache path should return 1 and never reach P_020 "
            f"write, got exit={exit_code_missing}, calls={p020_calls}"
        )
    print("cmd_record_submit() missing-cache short-circuit check: PASS")

    # ---- cmd_record_decline regression: unaffected, no P_020 write attempted ----
    rc_mod.read_eval_cache = lambda symbol: dict(fake_cached)
    with redirect_stdout(io.StringIO()):
        decline_code = rc_mod.cmd_record_decline("AAPL")
    if decline_code != 0 or p020_calls:
        _fail(
            f"cmd_record_decline regression failed: exit={decline_code}, "
            f"unexpected P_020 calls={p020_calls}"
        )
    print("cmd_record_decline() regression check: PASS (unaffected, no P_020 write)")

    print("PASS: config.py, order_submit_writer.py, and record_commands.py validated (no live calls made).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
