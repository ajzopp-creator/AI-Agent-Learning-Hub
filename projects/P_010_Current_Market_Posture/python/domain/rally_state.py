"""
P_010 Market Health -- domain/rally_state.py

State machine tracking rally attempts and follow-through days.
Walks a chronological VPDailyRow list, transitioning between
states defined in Section 5 of the spec.

States:
  NO_RALLY      -- default; tracking running low
  RALLY_LOW_SET -- candidate rally low exists; waiting for first up close
  RALLY_ATTEMPT -- day 1+ of a rally attempt (FTD valid on days 4-7)
  FTD_CONFIRMED -- valid FTD recorded; persists until dist_count >= threshold
  STALE_RALLY   -- attempt window expired without FTD

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Section 5
"""

from datetime import date
from typing import Optional

from market_health.config import (
    DIST_COUNT_INVALIDATES_FTD,
    FTD_DAY_MAX,
    RALLY_RESET_PCT,
)
from market_health.schemas import RallyState, VPDailyRow
from domain.distribution_day import is_follow_through_candidate


class RallyTracker:
    """Mutable state walker. Build one instance, feed rows via walk()."""

    def __init__(self) -> None:
        self.state: RallyState = "NO_RALLY"
        self.rally_low: Optional[float] = None
        self.rally_low_date: Optional[date] = None
        self.attempt_day: Optional[int] = None
        self.ftd_date: Optional[date] = None
        self.last_5pct_reset_date: Optional[date] = None

    # -----------------------------------------------------------------------
    # Public entry points
    # -----------------------------------------------------------------------

    def walk(self, rows: list[VPDailyRow]) -> None:
        """Process every row in chronological order, mutating state."""
        if len(rows) < 2:
            return
        # Seed initial low from row 0 so it isn't ignored by the loop
        self.rally_low = rows[0].low
        self.rally_low_date = rows[0].trade_date
        self.state = "RALLY_LOW_SET"
        for i in range(1, len(rows)):
            self._step(rows[i], rows[i - 1])

    def invalidate_ftd_if_needed(self, dist_count: int) -> None:
        """Runner calls this after computing dist_count. If FTD_CONFIRMED
        and dist count has hit the kill threshold, drop back to NO_RALLY."""
        if self.state != "FTD_CONFIRMED":
            return
        if dist_count >= DIST_COUNT_INVALIDATES_FTD:
            self.state = "NO_RALLY"
            self.ftd_date = None
            self.attempt_day = None

    def ftd_age_days(self, as_of: date) -> Optional[int]:
        if self.ftd_date is None:
            return None
        return max((as_of - self.ftd_date).days, 0)

    # -----------------------------------------------------------------------
    # Single-day transition dispatch
    # -----------------------------------------------------------------------

    def _step(self, today: VPDailyRow, prior: VPDailyRow) -> None:
        self._check_5pct_reset(today)
        if self.state == "FTD_CONFIRMED":
            return
        if self.state in ("NO_RALLY", "STALE_RALLY"):
            self._step_no_rally(today, prior)
        elif self.state == "RALLY_LOW_SET":
            self._step_rally_low_set(today, prior)
        elif self.state == "RALLY_ATTEMPT":
            self._step_rally_attempt(today, prior)

    # -----------------------------------------------------------------------
    # Per-state handlers
    # -----------------------------------------------------------------------

    def _step_no_rally(self, today: VPDailyRow, prior: VPDailyRow) -> None:
        if self.rally_low is None or today.low < self.rally_low:
            self.rally_low = today.low
            self.rally_low_date = today.trade_date
            self.state = "RALLY_LOW_SET"
            self.attempt_day = None
            return
        if today.close > prior.close:
            self.state = "RALLY_ATTEMPT"
            self.attempt_day = 1

    def _step_rally_low_set(self, today: VPDailyRow, prior: VPDailyRow) -> None:
        if self.rally_low is not None and today.low < self.rally_low:
            self.rally_low = today.low
            self.rally_low_date = today.trade_date
            return
        if today.close > prior.close:
            self.state = "RALLY_ATTEMPT"
            self.attempt_day = 1

    def _step_rally_attempt(self, today: VPDailyRow, prior: VPDailyRow) -> None:
        # Undercut of rally low fails the attempt
        if self.rally_low is not None and today.low < self.rally_low:
            self.rally_low = today.low
            self.rally_low_date = today.trade_date
            self.state = "RALLY_LOW_SET"
            self.attempt_day = None
            return
        new_day = (self.attempt_day or 0) + 1
        if is_follow_through_candidate(today, prior, new_day):
            self.attempt_day = new_day
            self.ftd_date = today.trade_date
            self.state = "FTD_CONFIRMED"
            return
        self.attempt_day = new_day
        if new_day > FTD_DAY_MAX:
            self.state = "STALE_RALLY"
            self.attempt_day = None

    # -----------------------------------------------------------------------
    # 5% reset detection
    # -----------------------------------------------------------------------

    def _check_5pct_reset(self, today: VPDailyRow) -> None:
        if self.rally_low is None:
            return
        gain_pct = ((today.close - self.rally_low) / self.rally_low) * 100.0
        if gain_pct >= RALLY_RESET_PCT:
            self.last_5pct_reset_date = today.trade_date
