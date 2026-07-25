"""chain_selector.py -- pick the optimal option contract from a candidate
range (WO-P400-E4.002).

Pure logic, no I/O. Deliberately narrow scope: picks by DTE window +
closest-to-target-delta only. Does NOT duplicate R:R/OI/spread checks --
those need the delta-translated stop/target math that only happens after
a contract is chosen (domain\options_council.py's job, unchanged). This
module's pick then goes through the exact same downstream path a manually
typed --strike/--expiration contract already goes through today.

Selection parameters are Tony's explicit call (config.py,
OPTION_SELECTION_TARGET_DELTA/MIN_DTE/MAX_DTE), not hardcoded here.
"""

from __future__ import annotations

from datetime import date
from typing import NamedTuple, Optional, Sequence


class ChainCandidate(NamedTuple):
    """One strike/expiration pair from a fetched option chain range.

    Raw data as returned by schwab_market_data.get_chain_candidates() --
    not yet an OptionChainInput (that's built after selection, in
    application\fetch_chain.py).
    """

    strike: float
    expiration: str          # YYYY-MM-DD
    delta: float
    iv: float                # implied volatility, decimal (0.31 = 31%)
    bid: float
    ask: float
    open_interest: int


def _days_to_expiration(expiration: str, as_of: date) -> int:
    """Return calendar days between as_of and expiration (YYYY-MM-DD)."""
    exp_date = date.fromisoformat(expiration)
    return (exp_date - as_of).days


def select_optimal_contract(
    candidates: Sequence[ChainCandidate],
    target_delta: float,
    min_dte: int,
    max_dte: int,
    as_of: Optional[date] = None,
) -> Optional[ChainCandidate]:
    """Return the candidate closest to target_delta within [min_dte, max_dte].

    Never fabricates a pick -- returns None if no candidate's DTE falls in
    the window. Ties on delta distance broken by tightest bid/ask spread,
    then by highest open interest.

    Args:
        candidates: Raw chain rows from schwab_market_data.
        target_delta: Absolute delta to target (config.py, Tony's call).
        min_dte: Minimum days to expiration, inclusive.
        max_dte: Maximum days to expiration, inclusive.
        as_of: Date to compute DTE from. Defaults to today.

    Returns:
        The selected ChainCandidate, or None if nothing qualifies.
    """
    if as_of is None:
        as_of = date.today()

    in_window = [
        c for c in candidates
        if min_dte <= _days_to_expiration(c.expiration, as_of) <= max_dte
    ]
    if not in_window:
        return None

    def _spread_pct(c: ChainCandidate) -> float:
        mid = (c.bid + c.ask) / 2
        if mid <= 0:
            return float("inf")
        return (c.ask - c.bid) / mid * 100

    def _sort_key(c: ChainCandidate):
        # Round so float noise (e.g. 0.45 vs 0.55 vs target 0.50) still
        # counts as equidistant and falls through to spread / OI ties.
        delta_distance = round(abs(abs(c.delta) - target_delta), 6)
        return (delta_distance, _spread_pct(c), -c.open_interest)

    return min(in_window, key=_sort_key)