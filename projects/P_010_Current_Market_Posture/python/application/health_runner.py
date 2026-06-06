"""
P_010 Market Health -- application/health_runner.py

Orchestration layer. Reads VP rows for SPY+QQQ, runs the rally state
machine, counts distribution days with both reset rules applied,
derives the market phase, and writes the JSON output.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Sections 4-7
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from market_health.config import DISTRIBUTION_WINDOW_DAYS, OUTPUT_JSON
from market_health.schemas import (
    IndexHealth,
    MarketHealthOutput,
    Ticker,
    VPDailyRow,
)
from domain.distribution_day import count_distribution_days
from domain.market_phase import derive_phase
from domain.rally_state import RallyTracker
from infrastructure.health_writer import write_health
from infrastructure.vp_reader import read_vp_history


def run_market_health(
    as_of: Optional[date] = None,
    dry_run: bool = False,
    target_path: Path = OUTPUT_JSON,
    lookback_days: Optional[int] = None,
) -> MarketHealthOutput:
    """
    Build the MarketHealthOutput and (unless dry_run) write it to disk.

    Returns the output object regardless. Caller can inspect fields.
    """
    if lookback_days is None:
        spy_rows = read_vp_history("SPY")
        qqq_rows = read_vp_history("QQQ")
    else:
        spy_rows = read_vp_history("SPY", lookback_days=lookback_days)
        qqq_rows = read_vp_history("QQQ", lookback_days=lookback_days)

    if not spy_rows or not qqq_rows:
        raise ValueError("VP reader returned empty row list")

    effective_as_of = as_of or max(spy_rows[-1].trade_date, qqq_rows[-1].trade_date)

    # Truncate to as_of so historical runs do not leak future rows into
    # the rally tracker / distribution counter. No-op when as_of equals
    # the latest row date (the production path).
    spy_rows_uptodate = [r for r in spy_rows if r.trade_date <= effective_as_of]
    qqq_rows_uptodate = [r for r in qqq_rows if r.trade_date <= effective_as_of]

    spy_health = _build_index_health("SPY", spy_rows_uptodate, effective_as_of)
    qqq_health = _build_index_health("QQQ", qqq_rows_uptodate, effective_as_of)

    max_dist = max(spy_health.dist_count, qqq_health.dist_count)
    phase, reason = derive_phase(spy_health, qqq_health)

    output = MarketHealthOutput(
        generated_at=datetime.now(),
        as_of_date=effective_as_of,
        spy=spy_health,
        qqq=qqq_health,
        max_dist_count=max_dist,
        market_phase=phase,
        phase_reason=reason,
    )

    if not dry_run:
        write_health(output, target=target_path)

    return output


# ---------------------------------------------------------------------------
# Per-index assembly
# ---------------------------------------------------------------------------

def _build_index_health(
    ticker: Ticker,
    rows: list[VPDailyRow],
    as_of: date,
) -> IndexHealth:
    tracker = RallyTracker()
    tracker.walk(rows)

    window_days = _effective_window_days(tracker.last_5pct_reset_date, as_of)
    dist_count, dist_dates = count_distribution_days(rows, as_of, window_days)

    # Apply external invalidation (must happen AFTER counting)
    tracker.invalidate_ftd_if_needed(dist_count)

    return IndexHealth(
        ticker=ticker,
        last_date=rows[-1].trade_date,
        last_close=rows[-1].close,
        dist_count=dist_count,
        dist_dates=dist_dates,
        rally_state=tracker.state,
        rally_low=tracker.rally_low,
        rally_low_date=tracker.rally_low_date,
        rally_attempt_day=tracker.attempt_day,
        follow_through_day=tracker.ftd_date,
        ftd_age_days=tracker.ftd_age_days(as_of),
    )


def _effective_window_days(
    last_5pct_reset_date: Optional[date],
    as_of: date,
) -> int:
    """
    Apply the 'either trigger applies independently' rule from Section 4.

    The effective window is the more restrictive (shorter) of:
      - rolling DISTRIBUTION_WINDOW_DAYS lookback
      - days since the most recent 5% rally reset, if any
    """
    if last_5pct_reset_date is None:
        return DISTRIBUTION_WINDOW_DAYS
    days_since_reset = (as_of - last_5pct_reset_date).days
    return min(DISTRIBUTION_WINDOW_DAYS, max(days_since_reset, 0))
