"""market_hours.py -- market-session detection (WO-P400-E4.005).

Pure logic, no I/O. Computed independently of Schwab's quote response --
Tony's call 2026-07-26: the API itself is documented (Schwab's own Extended
Hours Trading page) as returning wider/less-reliable quotes outside regular
hours, so session state should not be inferred from Schwab's own fields
either. Wall-clock only.

Holiday calendar added WO-P400-E4.006 (domain\\market_holidays.py) --
formerly the known limitation here (and in WO-P400-E2.023's
sessions_since_earnings, fixed in the same WO). No per-year data to
maintain -- see that module's docstring for the rule set.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from config import MARKET_OPEN_TIME_ET, MARKET_CLOSE_TIME_ET
from domain.market_holidays import is_market_holiday

EASTERN = ZoneInfo("America/New_York")


def is_market_open_now(now: Optional[datetime] = None) -> bool:
    """True if the regular US equity session is open right now.

    Args:
        now: Optional injected datetime (timezone-aware or naive-UTC) for
            testability. Defaults to actual current time.

    Returns:
        False on weekends, US market holidays (domain.market_holidays), or
        outside 9:30-16:00 Eastern.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    et_now = now.astimezone(EASTERN)

    if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    if is_market_holiday(et_now.date()):
        return False

    current_time = et_now.time()
    return MARKET_OPEN_TIME_ET <= current_time < MARKET_CLOSE_TIME_ET