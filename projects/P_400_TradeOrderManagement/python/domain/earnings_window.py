"""P_400 domain: earnings-window and post-earnings-stabilization checks.

Pure logic only -- no I/O, no network, no print.

Extracted from application/evaluate_signal.py (WO-P000-E10.001 Phase 2,
item 2.2) so evaluate_options.py and evaluate_spread.py can share the exact
same earnings-window logic when wiring macro_vote() into those paths --
previously this lived as private (_-prefixed) functions in one application
module, which is also a pre-existing layer-rule violation (pure logic
belongs in domain/, not application/) that became worth fixing once a
second and third caller needed it.

Behavior is unchanged from the original evaluate_signal.py functions --
this is a move, not a rewrite.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from config import EARNINGS_WINDOW_BACKWARD_DAYS, EARNINGS_WINDOW_FORWARD_DAYS
from domain.market_holidays import is_market_holiday


def earnings_in_window(next_earnings_date: Optional[str]) -> bool:
    """Return True if earnings date falls inside the configured window around
    today: EARNINGS_WINDOW_FORWARD_DAYS ahead, EARNINGS_WINDOW_BACKWARD_DAYS
    behind (config.py, Tony's call 2026-07-28). Replaces the prior hardcoded
    14-day forward-only check, which also had no backward bound at all --
    a past earnings date never aged out of the old check.
    """
    if not next_earnings_date:
        return False
    try:
        earnings = date.fromisoformat(next_earnings_date)
        delta_days = (earnings - date.today()).days
        return -EARNINGS_WINDOW_BACKWARD_DAYS <= delta_days <= EARNINGS_WINDOW_FORWARD_DAYS
    except ValueError:
        return False


def sessions_since_earnings(last_earnings_date: Optional[str]) -> Optional[int]:
    """Weekday count from last_earnings_date to today (WO-P400-E2.023),
    holiday-aware since WO-P400-E4.006.

    Trading-session approximation -- skips weekends and NYSE full-closure
    holidays (domain\\market_holidays.py). Returns None if last_earnings_date
    is unknown or in the future (bad data, don't guess).
    """
    if not last_earnings_date:
        return None
    try:
        last_earn = date.fromisoformat(last_earnings_date)
    except ValueError:
        return None
    today = date.today()
    if last_earn > today:
        return None
    count = 0
    d = last_earn
    while d < today:
        d = date.fromordinal(d.toordinal() + 1)
        if d.weekday() < 5 and not is_market_holiday(d):
            count += 1
    return count