"""market_holidays.py -- US stock-market (NYSE/Nasdaq) full-closure
holidays (WO-P400-E4.006).

Pure logic, no I/O, no external dependency, no per-year data to maintain.
Every NYSE full-closure holiday reduces to one of these rule shapes:
  - Nth weekday of a month (MLK, Presidents, Labor Day, Thanksgiving)
  - Last weekday of a month (Memorial Day)
  - A fixed calendar date, shifted to the nearest weekday if it falls on
    a weekend (New Year's, Juneteenth, Independence Day, Christmas) --
    New Year's Day has one documented exception: NYSE does not observe
    it at all if Jan 1 falls on a Saturday (confirmed for 2028).
  - Good Friday, the Friday before Easter Sunday (Anonymous Gregorian /
    Meeus-Jones-Butcher algorithm -- correct for any Gregorian year, no
    lookup table).

All rules verified 2026-07-27 against NYSE's published 2026-2028
calendars before this file was written (New Year's, MLK, Presidents,
Good Friday, Memorial Day, Juneteenth, Independence Day, Labor Day,
Thanksgiving, Christmas -- all ten 2026 dates matched; 2027 Juneteenth
weekend-shift and 2028 New Year's non-observance both matched).

Deliberately excludes early-close half-sessions (day after Thanksgiving,
Christmas Eve) -- out of scope, see WO-P400-E4.006 Out of Scope.
"""

from __future__ import annotations

from datetime import date, timedelta


def _nth_weekday_of_month(year: int, month: int, weekday: int, n: int) -> date:
    """The n-th occurrence of `weekday` (Monday=0) in `month`/`year`."""
    d = date(year, month, 1)
    offset = (weekday - d.weekday()) % 7
    d += timedelta(days=offset)
    d += timedelta(weeks=n - 1)
    return d


def _last_weekday_of_month(year: int, month: int, weekday: int) -> date:
    """The last occurrence of `weekday` (Monday=0) in `month`/`year`."""
    if month == 12:
        next_month_first = date(year + 1, 1, 1)
    else:
        next_month_first = date(year, month + 1, 1)
    d = next_month_first - timedelta(days=1)
    offset = (d.weekday() - weekday) % 7
    return d - timedelta(days=offset)


def _easter_sunday(year: int) -> date:
    """Easter Sunday via the Anonymous Gregorian algorithm (Meeus/Jones/
    Butcher). Correct for any Gregorian-calendar year -- no lookup table.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _observed_date(d: date, *, skip_if_saturday: bool = False) -> date | None:
    """Shift a fixed-date holiday to the nearest weekday.

    Saturday -> preceding Friday (or not observed at all if
    skip_if_saturday -- NYSE's documented New Year's Day exception).
    Sunday -> following Monday. Weekday -> unchanged.
    """
    if d.weekday() == 5:  # Saturday
        if skip_if_saturday:
            return None
        return d - timedelta(days=1)
    if d.weekday() == 6:  # Sunday
        return d + timedelta(days=1)
    return d


def market_holidays(year: int) -> set[date]:
    """All NYSE/Nasdaq full-closure holidays for `year` (WO-P400-E4.006).

    Ten holidays in a typical year. Excludes early-close half-sessions
    by design (see module docstring).
    """
    holidays: set[date] = set()

    new_years = _observed_date(date(year, 1, 1), skip_if_saturday=True)
    if new_years is not None:
        holidays.add(new_years)

    holidays.add(_nth_weekday_of_month(year, 1, 0, 3))   # MLK -- 3rd Mon Jan
    holidays.add(_nth_weekday_of_month(year, 2, 0, 3))   # Presidents -- 3rd Mon Feb
    holidays.add(_easter_sunday(year) - timedelta(days=2))  # Good Friday
    holidays.add(_last_weekday_of_month(year, 5, 0))     # Memorial -- last Mon May

    juneteenth = _observed_date(date(year, 6, 19))
    if juneteenth is not None:
        holidays.add(juneteenth)

    independence_day = _observed_date(date(year, 7, 4))
    if independence_day is not None:
        holidays.add(independence_day)

    holidays.add(_nth_weekday_of_month(year, 9, 0, 1))   # Labor -- 1st Mon Sept
    holidays.add(_nth_weekday_of_month(year, 11, 3, 4))  # Thanksgiving -- 4th Thu Nov

    christmas = _observed_date(date(year, 12, 25))
    if christmas is not None:
        holidays.add(christmas)

    return holidays


def is_market_holiday(d: date) -> bool:
    """True if `d` is a full NYSE/Nasdaq closure day."""
    return d in market_holidays(d.year)