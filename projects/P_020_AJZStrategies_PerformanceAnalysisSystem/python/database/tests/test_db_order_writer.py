"""Tests for infrastructure.db_order_writer -- the options-multiplier
back-solve fix (ref EC-010, WO-P400-E6.001 Gate 2: with realized_pnl
already multiplier-adjusted upstream in domain/order_reconciler.py,
_build_exit() must multiply qty by 100 for OPTION rows before dividing
back out, or exit_price comes out 100x too small -- live-verified
2026-09-08, SPY: $0.16 -> $3.13).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from infrastructure.db_order_writer import _build_exit


def _spy_option_data(realized_pnl: float) -> dict:
    return {
        "entry_fill_price": 3.16,
        "qty": 1,
        "asset_type": "OPTION",
        "side": "short",
        "realized_pnl": realized_pnl,
        "close_date": "2026-09-08",
        "entry_date": "2026-09-08",
    }


def test_build_exit_back_solves_option_price_with_multiplier():
    """Real 2026-09-08 SPY case: realized_pnl $3.00 must back-solve to
    exit_price $3.13, not $0.16 (the pre-fix bug: dividing by qty alone
    with no multiplier)."""
    exit_ = _build_exit(_spy_option_data(3.00), trade_id=1)
    assert exit_.exit_price == 3.13


def test_build_exit_stock_uses_1x_multiplier():
    data = {
        "entry_fill_price": 100.0,
        "qty": 10,
        "asset_type": "EQUITY",
        "side": "long",
        "realized_pnl": 10.00,
        "close_date": "2026-09-08",
        "entry_date": "2026-09-08",
    }
    exit_ = _build_exit(data, trade_id=1)
    assert exit_.exit_price == 101.0


def test_build_exit_returns_none_without_entry_fill_price():
    data = _spy_option_data(3.00)
    data["entry_fill_price"] = None
    assert _build_exit(data, trade_id=1) is None
