"""test_chain_selector.py -- WO-P400-E4.002. Permanent regression suite for
domain\chain_selector.py, per python-project-architecture skill's Regression
Test Governance (one assertion per fix/guarantee, never shrinks).
"""

from __future__ import annotations

from datetime import date

from domain.chain_selector import ChainCandidate, select_optimal_contract

AS_OF = date(2026, 7, 24)


def _candidate(strike, expiration, delta, iv=0.30, bid=1.0, ask=1.1, oi=200):
    return ChainCandidate(
        strike=strike, expiration=expiration, delta=delta, iv=iv,
        bid=bid, ask=ask, open_interest=oi,
    )


def test_picks_closest_to_target_delta_within_window():
    """30 DTE is inside the 21-45 window; delta 0.50 should win over 0.65."""
    candidates = [
        _candidate(100, "2026-08-23", delta=0.65),  # 30 DTE, off-target
        _candidate(105, "2026-08-23", delta=0.50),  # 30 DTE, on-target
        _candidate(110, "2026-08-23", delta=0.35),  # 30 DTE, off-target
    ]
    picked = select_optimal_contract(candidates, target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked.strike == 105


def test_excludes_candidates_outside_dte_window():
    """A perfect-delta match outside the DTE window must never be picked."""
    candidates = [
        _candidate(100, "2026-07-31", delta=0.50),  # 7 DTE -- too close, excluded
        _candidate(105, "2026-08-23", delta=0.55),  # 30 DTE -- in window, off-target but valid
    ]
    picked = select_optimal_contract(candidates, target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked.strike == 105


def test_no_candidates_in_window_returns_none():
    """Never fabricate a pick -- honest None when nothing qualifies."""
    candidates = [
        _candidate(100, "2026-07-31", delta=0.50),  # 7 DTE, outside window
    ]
    picked = select_optimal_contract(candidates, target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked is None


def test_empty_candidate_list_returns_none():
    picked = select_optimal_contract([], target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked is None


def test_tie_on_delta_broken_by_tighter_spread():
    """Two candidates equidistant from target delta -- tighter spread wins."""
    candidates = [
        _candidate(100, "2026-08-23", delta=0.45, bid=1.00, ask=1.20),  # wide spread
        _candidate(105, "2026-08-23", delta=0.55, bid=1.00, ask=1.05),  # tight spread
    ]
    picked = select_optimal_contract(candidates, target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked.strike == 105


def test_tie_on_delta_and_spread_broken_by_open_interest():
    candidates = [
        _candidate(100, "2026-08-23", delta=0.50, bid=1.00, ask=1.10, oi=150),
        _candidate(105, "2026-08-23", delta=0.50, bid=1.00, ask=1.10, oi=500),
    ]
    picked = select_optimal_contract(candidates, target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked.strike == 105


def test_boundary_dte_inclusive():
    """min_dte and max_dte are inclusive boundaries, not exclusive."""
    candidates = [
        _candidate(100, "2026-08-14", delta=0.50),  # exactly 21 DTE
        _candidate(105, "2026-09-07", delta=0.50),  # exactly 45 DTE
    ]
    picked_low = select_optimal_contract([candidates[0]], target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    picked_high = select_optimal_contract([candidates[1]], target_delta=0.50, min_dte=21, max_dte=45, as_of=AS_OF)
    assert picked_low is not None
    assert picked_high is not None