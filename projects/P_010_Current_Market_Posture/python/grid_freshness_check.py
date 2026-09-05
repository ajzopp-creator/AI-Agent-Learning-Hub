"""
P_010 Grid Freshness Check
New module, WO-P010-E1.004 (2026-08-29). Detects VantagePoint History
Grid exports that are OLDER than expected, silently feeding stale data
into a clean-looking morning run -- on 2026-08-28, grid_date lagged the
calendar by 3 trading days (VP had not overwritten exports for two
nights); P_010_daily_posture_v5.py ran clean and wrote a fresh
RiskConfig.json off 3-day-old input. staleness_check.py deliberately
keys off the JSON "timestamp" (did the script run today), never
grid_date -- this module is the missing check that grid_date itself is
the age it should be.

Pure logic -- no I/O, no network calls. Same split-file pattern as
intraday_risk_logic.py / staleness_check.py.

HOLIDAY + WEEKEND-RUN AWARE (WO-P010-E1.005, 2026-08-30): the original
E1.004 scope (Tony's sign-off, 2026-08-29) was weekend-only lag logic
with no holiday calendar, accepting ~9 false positives/year the morning
after a US market holiday. Reopened the same week -- the very next
holiday, Labor Day (Mon 2026-09-07), would have false-positived on Tue
2026-09-08 within days of shipping. Separately, a manual Sunday run on
2026-08-30 exposed a second gap in the same function: the old
Monday-only special case had no concept of the check itself running on
a non-trading day, and mis-derived Saturday as "expected." Both are
fixed by the same generalized rule below -- see WO-P010-E1.005.
"""

from datetime import date, timedelta

MARKET_HOLIDAYS_2026 = {
    date(2026, 1, 1),   # New Year's Day
    date(2026, 1, 19),  # MLK Day
    date(2026, 2, 16),  # Washington's Birthday
    date(2026, 4, 3),   # Good Friday
    date(2026, 5, 25),  # Memorial Day
    date(2026, 6, 19),  # Juneteenth
    date(2026, 7, 3),   # Independence Day (observed -- July 4 is a Saturday)
    date(2026, 9, 7),   # Labor Day
    date(2026, 11, 26), # Thanksgiving
    date(2026, 12, 25), # Christmas Day
}


def expected_trading_day(today: date) -> date:
    """The grid_date VantagePoint SHOULD show for today's morning run.

    VP exports the night before for next-day use, so a normal weekday
    morning expects the prior trading day's date. Generalized (v2,
    WO-P010-E1.005): walk backward from today one day at a time,
    skipping weekends AND MARKET_HOLIDAYS_2026, and return the first
    date that clears both. This also correctly handles the check
    itself running on a non-trading day (e.g. a manual Saturday/Sunday
    run) -- it always resolves to the most recent real trading day
    before `today`, regardless of what `today` itself is.
    """
    d = today - timedelta(days=1)
    while d.weekday() >= 5 or d in MARKET_HOLIDAYS_2026:
        d -= timedelta(days=1)
    return d


def check_grid_freshness(
    grid_dates: dict[str, date], today: date
) -> tuple[bool, str]:
    """Compare each symbol's actual grid_date against the expected date.

    Args:
        grid_dates: symbol -> the grid_date currently on disk, e.g.
            {"SPY": date(...), "QQQ": date(...), "VXX": date(...)}.
            VXX may be omitted if that grid isn't available.
        today: the calendar date of this run.

    Returns:
        (stale, detail). stale is True if ANY symbol's grid_date is
        older than expected_trading_day(today). detail names which
        symbol(s) and by how many days when stale; "" when fresh.
    """
    expected = expected_trading_day(today)
    behind = {sym: d for sym, d in grid_dates.items() if d < expected}
    if not behind:
        return False, ""

    parts = [
        f"{sym} grid_date={d.isoformat()} "
        f"({(expected - d).days}d behind expected {expected.isoformat()})"
        for sym, d in sorted(behind.items())
    ]
    return True, "STALE GRID DATA -- " + "; ".join(parts)
