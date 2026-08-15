"""
P_010 Staleness Check
New module, WO-P010-E1.003. Determines whether P_010_RiskConfig.json's morning
posture data is actually from today's run, or a stale carryover the intraday
script silently re-served (the root cause of WO-P010-E1.002's 4-day QQQ outage).

CRITICAL DESIGN CONSTRAINT (per Tony, 2026-08-10): this must key off the JSON's
internal "timestamp" field -- when the morning script itself last wrote the
file -- never off "grid_date". grid_date legitimately lags the calendar date
over weekends and holidays (VantagePoint doesn't export Sat/Sun; Monday's
morning run correctly shows Friday's grid_date until the next VP export runs
Monday 6:30 PM). Checking grid_date against "today" would false-positive as
stale every single Monday morning. Only "timestamp" not being from today's
actual run date is a real staleness signal.
"""

from datetime import date, datetime


def is_morning_data_stale(risk_config: dict, today: date) -> bool:
    """
    Returns True if P_010_RiskConfig.json's internal "timestamp" field is not
    from today -- meaning the morning script did not write fresh data today
    and this is a carryover from a prior (possibly failed) run.

    Does NOT check grid_date -- see module docstring. A missing or
    unparseable "timestamp" field is treated as stale (fail safe: when in
    doubt, flag it rather than silently trusting unknown data).
    """
    ts_raw = risk_config.get("timestamp")
    if not ts_raw:
        return True

    try:
        ts = datetime.fromisoformat(ts_raw)
    except (ValueError, TypeError):
        return True

    return ts.date() != today
