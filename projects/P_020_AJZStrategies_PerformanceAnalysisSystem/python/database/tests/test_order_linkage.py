"""Tests for domain.order_linkage -- the childOrderStrategies tree
walker (WO-P400-E6.001 Tier-1 reconciliation matching), confirmed live
2026-08-21 against 29 real orders (TRIGGER -> OCO -> two SINGLEs).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from domain.order_linkage import build_order_chain


def _single_order(order_id: int, symbol: str = "AAPL") -> dict:
    return {
        "orderId": order_id,
        "status": "FILLED",
        "orderStrategyType": "SINGLE",
        "enteredTime": "2026-08-21T14:00:00+0000",
        "closeTime": "2026-08-21T14:00:05+0000",
        "orderLegCollection": [{
            "instrument": {"symbol": symbol, "assetType": "EQUITY", "putCall": None},
            "quantity": 10,
        }],
        "orderActivityCollection": [{
            "executionLegs": [{"quantity": 10, "price": 150.0}]
        }],
        "childOrderStrategies": [],
    }


def test_build_order_chain_single_order_has_no_descendants():
    chain = build_order_chain(_single_order(1))
    assert chain.root.order_id == 1
    assert chain.descendants == []


def test_build_order_chain_walks_nested_bracket():
    """Real observed shape: TRIGGER -> OCO -> two SINGLEs, nested 2
    levels deep (GE 260918C410 case, 2026-08-21 diagnostic)."""
    target = _single_order(3, "GE")
    stop = _single_order(4, "GE")
    oco = _single_order(2, "GE")
    oco["orderStrategyType"] = "OCO"
    oco["childOrderStrategies"] = [target, stop]
    entry = _single_order(1, "GE")
    entry["orderStrategyType"] = "TRIGGER"
    entry["childOrderStrategies"] = [oco]

    chain = build_order_chain(entry)

    assert chain.root.order_id == 1
    ids = {n.order_id for n in chain.descendants}
    assert ids == {2, 3, 4}
    depths = {n.order_id: n.depth for n in chain.descendants}
    assert depths[2] == 1
    assert depths[3] == 2
    assert depths[4] == 2


def test_build_order_chain_raises_on_missing_order_id():
    with pytest.raises(ValueError):
        build_order_chain({"status": "FILLED"})


def test_avg_fill_price_from_execution_legs():
    chain = build_order_chain(_single_order(1))
    assert chain.root.avg_fill_price == 150.0


def test_avg_fill_price_falls_back_to_order_price_when_no_fills():
    order = _single_order(5)
    order["orderActivityCollection"] = []
    order["price"] = 149.5
    chain = build_order_chain(order)
    assert chain.root.avg_fill_price == 149.5
