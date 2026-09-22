"""Tests for domain.order_reconciler -- the options 100x-multiplier fix
(ref EC-010, WO-P400-E6.001 Gate 2, live-verified 2026-09-08 against a
real SPY option: realized_pnl came back $0.03 instead of $3.00 before
this fix routed the P&L calc through exit_builder.compute_exit_pnl()).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.order_linkage import LinkedOrder
from domain.order_reconciler import _compute_pnl


def _spy_option_node(order_id: int, avg_fill_price: float) -> LinkedOrder:
    return LinkedOrder(
        order_id=order_id,
        parent_order_id=None,
        order_strategy_type="SINGLE",
        status="FILLED",
        symbol="SPY",
        depth=0,
        quantity=1,
        asset_type="OPTION",
        put_call="CALL",
        avg_fill_price=avg_fill_price,
        entered_time="2026-09-08T14:00:00+0000",
        close_time="2026-09-08T14:05:00+0000",
    )


def test_compute_pnl_applies_100x_multiplier_for_short_option():
    """Real 2026-09-08 SPY case: short 1 call, entry 3.16, exit 3.13 ->
    realized_pnl must be $3.00, not $0.03 (the pre-fix bug)."""
    entry = _spy_option_node(1, 3.16)
    exit_node = _spy_option_node(2, 3.13)
    result = _compute_pnl("short", entry, exit_node)
    assert result == 3.00


def test_compute_pnl_stock_uses_1x_multiplier():
    """Non-option leg must NOT get the 100x multiplier."""
    entry = LinkedOrder(
        order_id=1, parent_order_id=None, order_strategy_type="SINGLE",
        status="FILLED", symbol="AAPL", depth=0, quantity=10,
        asset_type="EQUITY", put_call=None, avg_fill_price=100.0,
        entered_time="2026-09-08T14:00:00+0000",
        close_time="2026-09-08T14:00:00+0000",
    )
    exit_node = LinkedOrder(
        order_id=2, parent_order_id=None, order_strategy_type="SINGLE",
        status="FILLED", symbol="AAPL", depth=0, quantity=10,
        asset_type="EQUITY", put_call=None, avg_fill_price=101.0,
        entered_time="2026-09-08T14:05:00+0000",
        close_time="2026-09-08T14:05:00+0000",
    )
    result = _compute_pnl("long", entry, exit_node)
    assert result == 10.00
