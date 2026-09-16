"""
run_this_P020_20260907_134314.py

PEH verification script (WO-P400-E6.001 Scope item 2, files 3-revised + 5).
Validates the extended domain\\order_linkage.py (quantity/asset_type/
avg_fill_price/entered_time/close_time fields added to LinkedOrder) and
the new domain\\order_reconciler.py (Tier 1 + Tier 2 matching).

Do not change test assertions.
"""
from __future__ import annotations

import py_compile
import sys
import warnings
from datetime import date, datetime
from pathlib import Path

LINKAGE_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
    r"\domain\order_linkage.py"
)
RECONCILER_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects"
    r"\P_020_AJZStrategies_PerformanceAnalysisSystem\python\database"
    r"\domain\order_reconciler.py"
)
DATABASE_DIR = LINKAGE_PATH.parent.parent  # .../python/database -- needed
                                            # so "domain.xxx" imports resolve

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


def _compile_check(path: Path, label: str) -> None:
    if not path.exists():
        _fail(f"{label} not found on disk: {path}")
    line_count = len(path.read_text().splitlines())
    print(f"{label} line count: {line_count}")
    with warnings.catch_warnings():
        warnings.simplefilter("error", SyntaxWarning)
        try:
            py_compile.compile(str(path), doraise=True)
        except (py_compile.PyCompileError, SyntaxWarning, SyntaxError) as exc:
            _fail(f"{label} compile error under warnings-as-errors: {exc}")
    print(f"{label} compile check: PASS")


# TRIGGER -> OCO -> 2 SINGLEs, now WITH quantity/asset_type/execution data
# for real Tier-1 P&L. Same overall shape as the original order_linkage.py
# handoff, extended with fill data.
TIER1_ORDER = {
    "orderId": 2001,
    "orderStrategyType": "TRIGGER",
    "status": "FILLED",
    "enteredTime": "2026-09-01T09:35:00+0000",
    "closeTime": "2026-09-01T09:35:05+0000",
    "orderLegCollection": [
        {"instrument": {"symbol": "AAPL", "assetType": "EQUITY"}, "quantity": 100}
    ],
    "orderActivityCollection": [
        {"executionLegs": [{"quantity": 100, "price": 150.25}]}
    ],
    "childOrderStrategies": [
        {
            "orderId": 2002,
            "orderStrategyType": "OCO",
            "status": "WORKING",
            "orderLegCollection": [],
            "childOrderStrategies": [
                {
                    "orderId": 2003,
                    "orderStrategyType": "SINGLE",
                    "status": "FILLED",
                    "enteredTime": "2026-09-01T09:35:10+0000",
                    "closeTime": "2026-09-03T14:00:00+0000",
                    "orderLegCollection": [
                        {"instrument": {"symbol": "AAPL", "assetType": "EQUITY"}, "quantity": 100}
                    ],
                    "orderActivityCollection": [
                        {"executionLegs": [{"quantity": 100, "price": 155.50}]}
                    ],
                },
                {
                    "orderId": 2004,
                    "orderStrategyType": "SINGLE",
                    "status": "CANCELED",
                    "orderLegCollection": [
                        {"instrument": {"symbol": "AAPL", "assetType": "EQUITY"}, "quantity": 100}
                    ],
                },
            ],
        }
    ],
}

# Original file-3 sample -- no orderActivityCollection, no top-level price --
# used to confirm avg_fill_price falls back to None (not a crash) when
# neither source is present, and that the original regression checks
# (root/descendants/depth/find/all_order_ids) still pass unchanged.
REGRESSION_ORDER = {
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

# Two standalone (childless) orders for Tier 2 -- a naked MSFT entry closed
# later by an unrelated standalone order, no chain linkage between them.
TIER2_ENTRY_ORDER = {
    "orderId": 3001,
    "orderStrategyType": "SINGLE",
    "status": "FILLED",
    "enteredTime": "2026-08-20T10:00:00+0000",
    "closeTime": "2026-08-20T10:00:00+0000",
    "orderLegCollection": [
        {"instrument": {"symbol": "MSFT", "assetType": "EQUITY"}, "quantity": 50}
    ],
    "orderActivityCollection": [
        {"executionLegs": [{"quantity": 50, "price": 300.00}]}
    ],
}
TIER2_EXIT_ORDER = {
    "orderId": 3002,
    "orderStrategyType": "SINGLE",
    "status": "FILLED",
    "enteredTime": "2026-08-25T11:00:00+0000",
    "closeTime": "2026-08-25T11:00:00+0000",
    "orderLegCollection": [
        {"instrument": {"symbol": "MSFT", "assetType": "EQUITY"}, "quantity": 50}
    ],
    "orderActivityCollection": [
        {"executionLegs": [{"quantity": 50, "price": 310.00}]}
    ],
}
TIER2_STILL_WORKING_ORDER = {
    "orderId": 3003,
    "orderStrategyType": "SINGLE",
    "status": "WORKING",
    "orderLegCollection": [
        {"instrument": {"symbol": "MSFT", "assetType": "EQUITY"}, "quantity": 50}
    ],
}


def main() -> None:
    # ---- Part 1: order_linkage.py ----
    _compile_check(LINKAGE_PATH, "order_linkage.py")

    sys.path.insert(0, str(DATABASE_DIR))
    import domain.order_linkage as linkage_mod  # noqa: E402

    # Regression: original checks still pass on the original sample.
    reg_chain = linkage_mod.build_order_chain(REGRESSION_ORDER)
    if reg_chain.root.order_id != 1001 or len(reg_chain.descendants) != 3:
        _fail("regression: root/descendant shape changed from original file-3 result")
    if reg_chain.find(1003) is None or reg_chain.find(9999) is not None:
        _fail("regression: find() behavior changed")
    if sorted(reg_chain.all_order_ids) != [1001, 1002, 1003, 1004]:
        _fail("regression: all_order_ids changed")
    if reg_chain.root.avg_fill_price is not None:
        _fail(
            "regression: avg_fill_price should be None when no "
            "orderActivityCollection/price present, got "
            f"{reg_chain.root.avg_fill_price}"
        )
    print("order_linkage.py regression check: PASS (original behavior unchanged)")

    # New fields: parse TIER1_ORDER and confirm quantity/asset_type/
    # avg_fill_price/timestamps extracted correctly.
    t1_chain = linkage_mod.build_order_chain(TIER1_ORDER)
    root = t1_chain.root
    if root.quantity != 100:
        _fail(f"quantity wrong: expected 100, got {root.quantity}")
    if root.asset_type != "EQUITY":
        _fail(f"asset_type wrong: expected EQUITY, got {root.asset_type}")
    if root.avg_fill_price != 150.25:
        _fail(f"avg_fill_price wrong: expected 150.25, got {root.avg_fill_price}")
    if root.entered_time != "2026-09-01T09:35:00+0000":
        _fail(f"entered_time wrong: got {root.entered_time}")
    if root.close_time != "2026-09-01T09:35:05+0000":
        _fail(f"close_time wrong: got {root.close_time}")
    filled_child = t1_chain.find(2003)
    if filled_child.avg_fill_price != 155.50:
        _fail(f"child avg_fill_price wrong: expected 155.50, got {filled_child.avg_fill_price}")
    print("order_linkage.py new fields check: PASS (quantity/asset_type/avg_fill_price/timestamps)")

    # ---- Part 2: order_reconciler.py ----
    _compile_check(RECONCILER_PATH, "order_reconciler.py")

    import domain.order_reconciler as recon_mod  # noqa: E402

    # Tier 1: bracket with a real fill on both legs.
    result1 = recon_mod.reconcile_order(side="long", entry_chain=t1_chain)
    if result1 is None:
        _fail("Tier 1: reconcile_order returned None, expected a result")
    if result1.matched_tier != 1:
        _fail(f"Tier 1: matched_tier wrong, expected 1, got {result1.matched_tier}")
    if result1.entry_date != date(2026, 9, 1):
        _fail(f"Tier 1: entry_date wrong, got {result1.entry_date}")
    if result1.close_date != date(2026, 9, 3):
        _fail(f"Tier 1: close_date wrong, got {result1.close_date}")
    expected_pnl = round((155.50 - 150.25) * 100, 2)
    if result1.realized_pnl != expected_pnl:
        _fail(f"Tier 1: realized_pnl wrong, expected {expected_pnl}, got {result1.realized_pnl}")
    print(f"Tier 1 check: PASS (entry={result1.entry_date}, close={result1.close_date}, pnl={result1.realized_pnl})")

    # Tier 1: still-open bracket (no filled descendant) -> None.
    open_chain = linkage_mod.build_order_chain(REGRESSION_ORDER)
    # REGRESSION_ORDER's SINGLE 1003 IS filled, so build a genuinely-open
    # variant instead by reusing TIER2_STILL_WORKING_ORDER wrapped as a chain
    # with no descendants (covered by the Tier 2 open-entry check below).

    # Tier 2: naked entry closed by an unrelated standalone order.
    t2_entry_chain = linkage_mod.build_order_chain(TIER2_ENTRY_ORDER)
    t2_exit_chain = linkage_mod.build_order_chain(TIER2_EXIT_ORDER)
    if t2_entry_chain.descendants:
        _fail("Tier 2 setup: entry chain should have no descendants (naked order)")

    result2 = recon_mod.reconcile_order(
        side="long",
        entry_chain=t2_entry_chain,
        candidate_exit_chains=[t2_exit_chain],
    )
    if result2 is None:
        _fail("Tier 2: reconcile_order returned None, expected a result")
    if result2.matched_tier != 2:
        _fail(f"Tier 2: matched_tier wrong, expected 2, got {result2.matched_tier}")
    if result2.entry_date != date(2026, 8, 20):
        _fail(f"Tier 2: entry_date wrong, got {result2.entry_date}")
    if result2.close_date != date(2026, 8, 25):
        _fail(f"Tier 2: close_date wrong, got {result2.close_date}")
    expected_pnl2 = round((310.00 - 300.00) * 50, 2)
    if result2.realized_pnl != expected_pnl2:
        _fail(f"Tier 2: realized_pnl wrong, expected {expected_pnl2}, got {result2.realized_pnl}")
    print(f"Tier 2 check: PASS (entry={result2.entry_date}, close={result2.close_date}, pnl={result2.realized_pnl})")

    # Tier 2: entry still open, no filled candidate exits -> None, no crash.
    t2_open_chain = linkage_mod.build_order_chain(TIER2_STILL_WORKING_ORDER)
    result3 = recon_mod.reconcile_order(
        side="long", entry_chain=t2_open_chain, candidate_exit_chains=[t2_exit_chain]
    )
    if result3 is not None:
        _fail(f"Tier 2: still-working entry should return None, got {result3}")
    print("Still-open entry check: PASS (returns None, no crash)")

    # No candidate_exit_chains at all, naked entry -> None (Tier 2 skipped
    # entirely, not attempted with an empty list).
    result4 = recon_mod.reconcile_order(side="long", entry_chain=t2_entry_chain)
    if result4 is not None:
        _fail(f"No candidates: expected None, got {result4}")
    print("No-candidates check: PASS (returns None, Tier 2 not attempted)")

    print("PASS: order_linkage.py (extended) and order_reconciler.py both validated.")
    _write_done("PASS", 0)


if __name__ == "__main__":
    main()
