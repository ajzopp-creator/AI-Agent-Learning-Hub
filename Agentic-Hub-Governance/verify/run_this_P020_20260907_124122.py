"""
run_this_P020_20260907_124122.py

PEH verification script (WO-P400-E6.001 Scope item 2, file 3 of 18).
Validates domain\order_linkage.py: compiles clean, and build_order_chain()
correctly parses a synthetic order tree shaped like the WO's confirmed
live example (TRIGGER -> OCO -> two SINGLEs, GE 260918C410 entry -> OCO
bracket -> filled target + canceled stop). Pure logic, no I/O, no network,
no file writes beyond this script's own .done marker.

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sys
import warnings
from datetime import datetime
from pathlib import Path

TARGET = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
    r"\domain\order_linkage.py"
)

DONE_MARKER = Path(__file__).with_suffix(".py.done")

EXPECTED_MIN_LINES = 90
EXPECTED_MAX_LINES = 150


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


# Synthetic order tree shaped like the WO's confirmed live example:
# TRIGGER (entry) -> OCO bracket -> two SINGLEs (target filled, stop canceled)
SAMPLE_ORDER = {
    "orderId": 1001,
    "orderStrategyType": "TRIGGER",
    "status": "FILLED",
    "orderLegCollection": [
        {"instrument": {"symbol": "GE  260918C00410000"}, "quantity": 1}
    ],
    "childOrderStrategies": [
        {
            "orderId": 1002,
            "orderStrategyType": "OCO",
            "status": "WORKING",
            "orderLegCollection": [],
            "childOrderStrategies": [
                {
                    "orderId": 1003,
                    "orderStrategyType": "SINGLE",
                    "status": "FILLED",
                    "orderLegCollection": [
                        {"instrument": {"symbol": "GE  260918C00410000"}, "quantity": 1}
                    ],
                },
                {
                    "orderId": 1004,
                    "orderStrategyType": "SINGLE",
                    "status": "CANCELED",
                    "orderLegCollection": [
                        {"instrument": {"symbol": "GE  260918C00410000"}, "quantity": 1}
                    ],
                },
            ],
        }
    ],
}


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

    sys.path.insert(0, str(TARGET.parent))
    import order_linkage as mod  # noqa: E402

    # 3. Build the chain from the synthetic tree.
    chain = mod.build_order_chain(SAMPLE_ORDER)

    if chain.root.order_id != 1001:
        _fail(f"root order_id wrong: expected 1001, got {chain.root.order_id}")
    if chain.root.order_strategy_type != "TRIGGER":
        _fail(f"root order_strategy_type wrong: got {chain.root.order_strategy_type}")
    if chain.root.parent_order_id is not None:
        _fail(f"root should have no parent, got {chain.root.parent_order_id}")
    if chain.root.symbol != "GE  260918C00410000":
        _fail(f"root symbol not extracted correctly: got {chain.root.symbol!r}")
    print("Root node check: PASS")

    if len(chain.descendants) != 3:
        _fail(f"expected 3 descendants (OCO + 2 SINGLEs), got {len(chain.descendants)}")

    by_id = {node.order_id: node for node in chain.descendants}
    if set(by_id) != {1002, 1003, 1004}:
        _fail(f"descendant order_ids wrong: got {sorted(by_id)}")

    if by_id[1002].order_strategy_type != "OCO" or by_id[1002].parent_order_id != 1001:
        _fail("OCO node (1002) has wrong type or parent linkage")
    if by_id[1002].depth != 1:
        _fail(f"OCO node depth wrong: expected 1, got {by_id[1002].depth}")

    if by_id[1003].parent_order_id != 1002 or by_id[1003].status != "FILLED":
        _fail("filled SINGLE (1003) has wrong parent or status")
    if by_id[1004].parent_order_id != 1002 or by_id[1004].status != "CANCELED":
        _fail("canceled SINGLE (1004) has wrong parent or status")
    if by_id[1003].depth != 2 or by_id[1004].depth != 2:
        _fail("nested SINGLEs should be depth 2 (TRIGGER=0 -> OCO=1 -> SINGLE=2)")
    print("Nested descendants check: PASS (TRIGGER -> OCO -> 2 SINGLEs, depths correct)")

    # 4. all_order_ids / find() helpers.
    if sorted(chain.all_order_ids) != [1001, 1002, 1003, 1004]:
        _fail(f"all_order_ids wrong: got {sorted(chain.all_order_ids)}")
    if chain.find(1003) is None or chain.find(1003).order_id != 1003:
        _fail("find(1003) did not return the correct node")
    if chain.find(9999) is not None:
        _fail("find() returned a node for an order_id not in the chain")
    print("Helper methods (all_order_ids, find) check: PASS")

    # 5. Missing orderId raises ValueError (domain layer raises, doesn't swallow).
    try:
        mod.build_order_chain({"orderStrategyType": "SINGLE"})
        _fail("build_order_chain accepted an order dict with no orderId")
    except ValueError:
        pass
    print("Missing-orderId raises ValueError check: PASS")

    print("PASS: order_linkage.py validated against synthetic TRIGGER->OCO->2xSINGLE tree.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
