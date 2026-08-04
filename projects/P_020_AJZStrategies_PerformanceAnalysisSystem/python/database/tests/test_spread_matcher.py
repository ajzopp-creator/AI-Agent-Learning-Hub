"""Tests for database.domain.spread_matcher -- compute_realized_pnl()
default multiplier guarantee. Ref WO-P000-E10.001 Phase 1 (1.2).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from domain.spread_matcher import compute_realized_pnl


def _fill(net_price: float, qty: int, action: str) -> dict:
    """Minimal fill dict shaped like the real parsed Schwab fill."""
    return {
        "parsed": {
            "net_price": net_price,
            "container_qty": qty,
            "container_action": action,
        }
    }


def test_default_multiplier_matches_explicit_100_long():
    """No caller currently passes multiplier -- the default must stay 100,
    the standard options contract multiplier, or every stored spread P&L
    is silently wrong by 100x (ref WO-P000-E10.001 risk framing).
    """
    open_fill = _fill(net_price=2.00, qty=1, action="BOT")
    close_fill = _fill(net_price=3.50, qty=1, action="SLD")

    default_pnl = compute_realized_pnl(open_fill, close_fill)
    explicit_pnl = compute_realized_pnl(open_fill, close_fill, multiplier=100)

    assert default_pnl == explicit_pnl == 150.00


def test_default_multiplier_matches_explicit_100_short():
    """Same guarantee, short direction (net credit profits on price decline)."""
    open_fill = _fill(net_price=3.50, qty=2, action="SLD")
    close_fill = _fill(net_price=2.00, qty=2, action="BOT")

    default_pnl = compute_realized_pnl(open_fill, close_fill)
    explicit_pnl = compute_realized_pnl(open_fill, close_fill, multiplier=100)

    assert default_pnl == explicit_pnl == 300.00