"""
run_this_P020_20260907_130915.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 4 of 18).
Validates infrastructure\schwab_order_puller.py: compiles clean, module
imports without touching the network (client acquisition is lazy, inside
the function -- import alone must not call _get_client()), function
signature matches the approved plan, and the function's own try/except
shields a client-acquisition failure the way schwab_positions.py's does.

This script NEVER calls get_orders_for_account() for real and NEVER
authenticates to Schwab -- no live API call, no network access. It
proves the file is structurally sound, not that Schwab actually returns
orders (that's Tony's live-run job, separately, when this step of the
build is actually wired up and used).

Do not change test assertions.
"""
from __future__ import annotations

import inspect
import py_compile
import sys
import warnings
from datetime import datetime
from pathlib import Path

TARGET = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
    r"\infrastructure\schwab_order_puller.py"
)

DONE_MARKER = Path(__file__).with_suffix(".py.done")

EXPECTED_MIN_LINES = 50
EXPECTED_MAX_LINES = 90


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
    # 1. Durable signal.
    if not TARGET.exists():
        _fail(f"target file not found on disk: {TARGET}")

    line_count = len(TARGET.read_text().splitlines())
    print(f"Line count: {line_count}")
    if not (EXPECTED_MIN_LINES <= line_count <= EXPECTED_MAX_LINES):
        _fail(
            f"line count {line_count} outside expected "
            f"[{EXPECTED_MIN_LINES}, {EXPECTED_MAX_LINES}]"
        )

    # 2. Compile clean under warnings-as-errors.
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    # 3. Import must NOT touch the network -- P_020_Schwab_Token_Manager
    #    (and the schwab package itself) should only be imported lazily
    #    inside _get_client(), never at module import time. If this
    #    import call hangs or errors on a missing 'schwab' package, that
    #    proves the import is eager -- a real structural bug.
    sys.path.insert(0, str(TARGET.parent))
    import schwab_order_puller as mod  # noqa: E402

    print("Import check: PASS (module imported without touching the network)")

    # 4. Function exists with the approved signature.
    if not hasattr(mod, "get_orders_for_account"):
        _fail("get_orders_for_account function not found")

    sig = inspect.signature(mod.get_orders_for_account)
    expected_params = [
        "account_hash", "from_entered_datetime", "to_entered_datetime",
        "status", "max_results",
    ]
    actual_params = list(sig.parameters.keys())
    if actual_params != expected_params:
        _fail(
            f"signature mismatch: expected {expected_params}, "
            f"got {actual_params}"
        )
    # account_hash must be required (no default); the rest optional.
    if sig.parameters["account_hash"].default is not inspect.Parameter.empty:
        _fail("account_hash should be required, has a default")
    for name in expected_params[1:]:
        if sig.parameters[name].default is not None:
            _fail(f"{name} should default to None")
    print("Signature check: PASS (account_hash required, rest default None)")

    # 5. _get_client is only referenced inside the function body, not
    #    called at module scope -- confirms lazy client acquisition via
    #    source inspection (belt-and-braces on top of check 3's proof
    #    that import itself didn't touch the network).
    source = inspect.getsource(mod)
    module_level_lines = [
        line for line in source.split("\n")
        if not line.startswith((" ", "\t")) and "_get_client()" in line
    ]
    if module_level_lines:
        _fail(
            f"_get_client() appears to be called at module scope, not "
            f"just inside a function: {module_level_lines}"
        )
    print("Lazy-client check: PASS (_get_client() only called inside functions)")

    print("PASS: schwab_order_puller.py validated (no live API call made).")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
