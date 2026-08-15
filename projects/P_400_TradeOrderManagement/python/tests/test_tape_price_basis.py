r"""Tests for domain/council.py::tape_vote() price_basis behavior -- WO-P400-E5.005.

Run: C:\Users\Trader\.conda\envs\p140\python.exe -m pytest tests\test_tape_price_basis.py -v

Split out of test_council.py (which was at the 300-line cap) rather than
added there. Covers the market-closed branch specifically: close-priced
data should CAUTION, not BLOCK; a still-live price_basis while closed
(shouldn't happen once fetch_snapshot is wired right, but defensive) must
still BLOCK.
"""

from domain.council import Decision, tape_vote
from domain.council_codes import RC_MARKET_CLOSED, RC_USING_CLOSE_DATA


def test_tape_caution_market_closed_with_close_data():
    # Market closed + price_basis="close" -> CAUTION, not PASS/BLOCK.
    # Tony is still told this is close data, just not stopped by it.
    v = tape_vote(price_delay_seconds=30, market_open=False, price_basis="close",
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.CAUTION
    assert v.reason_code == RC_USING_CLOSE_DATA


def test_tape_still_blocks_market_closed_if_price_basis_live():
    # Defensive path -- should never happen once fetch_snapshot is wired
    # correctly, but price_basis="live" while market is closed must still BLOCK.
    v = tape_vote(price_delay_seconds=30, market_open=False, price_basis="live",
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_MARKET_CLOSED


def test_tape_caution_close_data_ignores_stale_check_boundary():
    # price_delay_seconds is always 0 for close-priced snapshots (set in
    # fetch_snapshot.py), so the staleness BLOCK never fires ahead of the
    # market-closed check for this path -- confirm that ordering holds.
    v = tape_vote(price_delay_seconds=0, market_open=False, price_basis="close",
                  adverse_drift_pct=0.0, rr_after_drift=2.5)
    assert v.decision == Decision.CAUTION
    assert v.reason_code == RC_USING_CLOSE_DATA