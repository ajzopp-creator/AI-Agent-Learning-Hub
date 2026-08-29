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

SCOPE (Tony's sign-off, 2026-08-29): weekend-only expected-lag logic,
no holiday calendar. A trading day the morning after a US market
holiday WILL false-positive here (~9x/year) -- accepted cost, cleared
by Tony in seconds each time rather than build/maintain a holiday
calendar. See WO-P010-E1.004 scoping decision.
"""

from datetime import date, timedelta


def expected_trading_day(today: date) -> date:
    """The grid_date VantagePoint SHOULD show for today's morning run.

    VP exports the night before for next-day use, so Tue-Fri mornings
    expect yesterday's date; Monday expects last Friday's. No holiday
    awareness -- see module docstring.
    """
    if today.weekday() == 0:  # Monday
        return today - timedelta(days=3)
    return today - timedelta(days=1)


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
