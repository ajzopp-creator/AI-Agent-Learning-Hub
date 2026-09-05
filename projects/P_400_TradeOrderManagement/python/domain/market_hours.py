"""market_hours.py -- market-session detection (WO-P400-E4.005).

Pure logic, no I/O. Computed independently of Schwab's quote response --
Tony's call 2026-07-26: the API itself is documented (Schwab's own Extended
Hours Trading page) as returning wider/less-reliable quotes outside regular
hours, so session state should not be inferred from Schwab's own fields
either. Wall-clock only.

Holiday calendar added WO-P400-E4.006 (domain\market_holidays.py) --
formerly the known limitation here (and in WO-P400-E2.023's
sessions_since_earnings, fixed in the same WO). No per-year data to
maintain -- see that module's docstring for the rule set.

WO-P400-E7.001: added get_session_state(), classifying "regular" /
"pre_market" / "after_hours" / "closed". is_market_open_now() is now a
thin wrapper (get_session_state(now) == "regular") -- same public
contract, same weekday/holiday/time logic, just no longer duplicated.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from config import (
    AFTER_HOURS_CLOSE_TIME_ET,
    MARKET_CLOSE_TIME_ET,
    MARKET_OPEN_TIME_ET,
    PRE_MARKET_OPEN_TIME_ET,
)
from domain.market_holidays import is_market_holiday

EASTERN = ZoneInfo("America/New_York")


def get_session_state(now: Optional[datetime] = None) -> str:
    """Classify the current moment into one of four trading sessions.

    Args:
        now: Optional injected datetime (timezone-aware or naive-UTC) for
            testability. Defaults to actual current time.

    Returns:
        "regular" | "pre_market" | "after_hours" | "closed" -- weekends and
        US market holidays are always "closed" regardless of clock time
        (extended sessions don't run on non-trading days either).
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    et_now = now.astimezone(EASTERN)

    if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
        return "closed"

    if is_market_holiday(et_now.date()):
        return "closed"

    current_time = et_now.time()
    if MARKET_OPEN_TIME_ET <= current_time < MARKET_CLOSE_TIME_ET:
        return "regular"
    if PRE_MARKET_OPEN_TIME_ET <= current_time < MARKET_OPEN_TIME_ET:
        return "pre_market"
    if MARKET_CLOSE_TIME_ET <= current_time < AFTER_HOURS_CLOSE_TIME_ET:
        return "after_hours"
    return "closed"


def is_market_open_now(now: Optional[datetime] = None) -> bool:
    """True if the regular US equity session is open right now.

    Args:
        now: Optional injected datetime (timezone-aware or naive-UTC) for
            testability. Defaults to actual current time.

    Returns:
        False on weekends, US market holidays, or outside 9:30-16:00 Eastern.
    """
    return get_session_state(now) == "regular"