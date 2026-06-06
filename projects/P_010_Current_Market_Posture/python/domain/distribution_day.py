"""
P_010 Market Health -- domain/distribution_day.py

Pure detection functions for distribution days, stalling days,
and follow-through day candidates. No IO, no state -- given a row
(or pair of rows) return a boolean / value.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Section 4
"""

from datetime import date, timedelta
from typing import Optional

from market_health.config import (
    DISTRIBUTION_WINDOW_DAYS,
    FTD_DAY_MAX,
    FTD_DAY_MIN,
    FTD_MIN_GAIN_PCT,
    MIN_DISTRIBUTION_PCT,
    STALLING_CLOSE_IN_RANGE_MAX,
    STALLING_MAX_GAIN_PCT,
    STALLING_VOLUME_RATIO_MIN,
)
from market_health.schemas import VPDailyRow


# ---------------------------------------------------------------------------
# Distribution day
# ---------------------------------------------------------------------------

def is_distribution_day(today: VPDailyRow, prior: VPDailyRow) -> bool:
    """
    A distribution day requires ALL of:
      close[t]  <  close[t-1]
      volume[t] >  volume[t-1]
      abs(pct_change_close) >= MIN_DISTRIBUTION_PCT

    Caller is responsible for passing chronologically adjacent rows.
    """
    if today.close >= prior.close:
        return False
    if today.volume <= prior.volume:
        return False
    pct_change = ((today.close - prior.close) / prior.close) * 100.0
    if abs(pct_change) < MIN_DISTRIBUTION_PCT:
        return False
    return True


def count_distribution_days(
    rows: list[VPDailyRow],
    as_of: date,
    window_days: int = DISTRIBUTION_WINDOW_DAYS,
) -> tuple[int, list[date]]:
    """
    Walk rows in chronological order and count distribution days within
    the rolling window ending on as_of (inclusive of as_of).

    Returns: (count, list_of_distribution_dates)
    """
    if len(rows) < 2:
        return 0, []

    window_start = as_of - timedelta(days=window_days)
    dist_dates: list[date] = []

    for i in range(1, len(rows)):
        today = rows[i]
        prior = rows[i - 1]
        if today.trade_date < window_start or today.trade_date > as_of:
            continue
        if is_distribution_day(today, prior):
            dist_dates.append(today.trade_date)

    return len(dist_dates), dist_dates


# ---------------------------------------------------------------------------
# Stalling day (Phase 2 -- pre-calibration thresholds, not yet wired in)
# ---------------------------------------------------------------------------

def is_stalling_day(today: VPDailyRow, prior: VPDailyRow) -> bool:
    """
    A stalling day is an UP day where institutions are quietly distributing.
    Hallmarks: small gain, prior-day-or-better volume, close weak in range.

    Requires ALL of:
      close[t]  >  close[t-1]                     (up day, not down)
      pct_change_close <= STALLING_MAX_GAIN_PCT   (gain is small)
      volume[t] >= volume[t-1] * STALLING_VOLUME_RATIO_MIN
      (close - low) / (high - low) <= STALLING_CLOSE_IN_RANGE_MAX

    Note: thresholds are pre-calibration defaults. This function is
    not yet called by count_distribution_days() -- production behavior
    is unchanged until calibration is complete.

    Caller is responsible for passing chronologically adjacent rows.
    """
    if today.close <= prior.close:
        return False

    pct_change = ((today.close - prior.close) / prior.close) * 100.0
    if pct_change > STALLING_MAX_GAIN_PCT:
        return False

    if today.volume < prior.volume * STALLING_VOLUME_RATIO_MIN:
        return False

    day_range = today.high - today.low
    if day_range <= 0:
        return False
    close_in_range = (today.close - today.low) / day_range
    if close_in_range > STALLING_CLOSE_IN_RANGE_MAX:
        return False

    return True


# ---------------------------------------------------------------------------
# Follow-through day candidate
# ---------------------------------------------------------------------------

def is_follow_through_candidate(
    today: VPDailyRow,
    prior: VPDailyRow,
    rally_attempt_day: Optional[int],
) -> bool:
    """
    A follow-through day candidate requires ALL of:
      rally_attempt_day in [FTD_DAY_MIN, FTD_DAY_MAX]
      pct_change_close >= FTD_MIN_GAIN_PCT
      volume[t] > volume[t-1]

    rally_attempt_day is the 1-indexed day number within the current
    rally attempt (day 1 = first up-close after rally low). Pass None
    when no rally attempt is active -- function returns False.
    """
    if rally_attempt_day is None:
        return False
    if rally_attempt_day < FTD_DAY_MIN or rally_attempt_day > FTD_DAY_MAX:
        return False
    if today.volume <= prior.volume:
        return False
    pct_change = ((today.close - prior.close) / prior.close) * 100.0
    if pct_change < FTD_MIN_GAIN_PCT:
        return False
    return True
