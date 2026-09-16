"""
run_this_P020_20260907_122849.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 2 of 18).
Validates schemas.py after appending the new Order model: confirms the
file is intact, compiles clean under warnings-as-errors, that Order
instantiates correctly with valid data, and that every pre-existing
class in the file still imports fine (regression check -- the edit was
an append, this confirms nothing above it was disturbed).

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sys
import warnings
from datetime import date, datetime
from pathlib import Path

TARGET = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
    r"\schemas.py"
)

DONE_MARKER = Path(__file__).with_suffix(".py.done")

EXPECTED_MIN_LINES = 210
EXPECTED_MAX_LINES = 290


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

    # 2. Compile clean under warnings-as-errors.
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(TARGET), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"compile error under warnings-as-errors: {exc}")
    print("Compile check: PASS (warnings-as-errors)")

    # 3. Import the module, confirm pre-existing classes still resolve
    #    (regression check -- the append should not have disturbed them).
    sys.path.insert(0, str(TARGET.parent))
    import schemas as mod  # noqa: E402

    for cls_name in (
        "Account", "TradingSystem", "Trade", "Exit", "SpreadLeg",
        "TradeParams", "TrackerEntry", "TrackerLookup", "LastRunFile",
    ):
        if not hasattr(mod, cls_name):
            _fail(f"pre-existing class missing after edit: {cls_name}")
    print("Regression check: PASS (9 pre-existing classes still present)")

    # 4. Instantiate Order with valid data -- confirms field types/Literals
    #    are usable, not just syntactically present.
    try:
        order = mod.Order(
            account_id="AJZ6348",
            symbol="AAPL",
            side="long",
            qty=100,
            submitted_ts=datetime(2026, 9, 7, 12, 0, 0),
        )
    except Exception as exc:  # noqa: BLE001 -- want the real Pydantic error
        _fail(f"Order model failed to instantiate with minimal valid data: {exc}")

    if order.trade_mode != "REAL":
        _fail(f"trade_mode default wrong: expected REAL, got {order.trade_mode}")
    if order.status != "pending":
        _fail(f"status default wrong: expected pending, got {order.status}")
    if order.confidence_tier != "CONFIRMED":
        _fail(
            f"confidence_tier default wrong: expected CONFIRMED, "
            f"got {order.confidence_tier}"
        )
    if order.source_project != "P400":
        _fail(f"source_project default wrong: expected P400, got {order.source_project}")
    print("Order instantiation + defaults check: PASS")

    # 5. Confirm an invalid Literal value is correctly rejected (Pydantic
    #    validation actually wired, not just type hints as documentation).
    try:
        mod.Order(
            account_id="AJZ6348", symbol="AAPL", side="sideways", qty=100,
            submitted_ts=datetime(2026, 9, 7, 12, 0, 0),
        )
        _fail("Order accepted an invalid side='sideways' -- validation not wired")
    except Exception:
        pass
    print("Validation-rejects-bad-input check: PASS")

    print("PASS: schemas.py Order model validated, pre-existing classes intact.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
