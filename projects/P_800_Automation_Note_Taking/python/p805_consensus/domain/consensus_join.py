"""consensus_join.py -- pure join/aggregation logic.

No file I/O here -- see infrastructure/ for readers and the writer.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from p805_consensus.config import COUNTED_VERDICTS, JOIN_WINDOW_TRADING_DAYS
from p805_consensus.schemas import ConsensusRow, RankedCandidate, TrackerRow


def add_trading_days(start: date, trading_days: int) -> date:
    """Return start plus N weekday-only trading days (holidays not modeled)."""
    current = start
    remaining = trading_days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5:
            remaining -= 1
    return current


def month_to_date_start(as_of: date) -> date:
    """First calendar day of as_of's month."""
    return as_of.replace(day=1)


def year_to_date_start(as_of: date) -> date:
    """First calendar day of as_of's year."""
    return as_of.replace(month=1, day=1)



def has_buy_asym_hit(
    ticker: str, first_seen: datetime, tracker_rows: list[TrackerRow]
) -> bool:
    """True if any Tracker row matches ticker within the forward join window
    from first_seen and carries a counted verdict."""
    window_end = add_trading_days(first_seen.date(), JOIN_WINDOW_TRADING_DAYS)
    for row in tracker_rows:
        if row.symbol != ticker:
            continue
        row_date = row.date.date()
        if first_seen.date() <= row_date <= window_end:
            if row.step1_verdict.upper() in COUNTED_VERDICTS:
                return True
    return False


def _earliest_first_seen_by_source_ticker(
    candidates: list[RankedCandidate],
) -> dict[tuple[str, str], datetime]:
    """Earliest first_seen per (source, ticker) pair across all appearances.

    A persisting ticker gets a fresh ranked.csv row every day it stays in
    consensus; collapsing those to one origin date per source counts
    distinct ideas instead of source-ticker-days (Tony, 2026-09-21).
    """
    earliest: dict[tuple[str, str], datetime] = {}
    for c in candidates:
        for src in c.sources:
            key = (src, c.ticker)
            if key not in earliest or c.first_seen < earliest[key]:
                earliest[key] = c.first_seen
    return earliest


def aggregate_by_source(
    today_candidates: list[RankedCandidate],
    mtd_candidates: list[RankedCandidate],
    ytd_candidates: list[RankedCandidate],
    tracker_rows: list[TrackerRow],
) -> list[ConsensusRow]:
    """Build one ConsensusRow per distinct email source across all windows.

    Today's symbols are shown as-is (one day, no persistence to collapse).
    MTD/YTD candidate and BUY/ASYM counts are deduped to one entry per
    distinct (source, ticker) pair -- see _earliest_first_seen_by_source_ticker.
    """
    sources: set[str] = set()
    for group in (today_candidates, mtd_candidates, ytd_candidates):
        for c in group:
            sources.update(c.sources)

    rows: dict[str, ConsensusRow] = {
        src: ConsensusRow(email_source=src) for src in sorted(sources)
    }

    for c in today_candidates:
        for src in c.sources:
            rows[src].today_symbols.append(c.ticker)

    mtd_first_seen = _earliest_first_seen_by_source_ticker(mtd_candidates)
    for (src, ticker), first_seen in mtd_first_seen.items():
        hit = has_buy_asym_hit(ticker, first_seen, tracker_rows)
        rows[src].mtd_candidates += 1
        if hit:
            rows[src].mtd_buy_asym += 1

    ytd_first_seen = _earliest_first_seen_by_source_ticker(ytd_candidates)
    for (src, ticker), first_seen in ytd_first_seen.items():
        hit = has_buy_asym_hit(ticker, first_seen, tracker_rows)
        rows[src].ytd_candidates += 1
        if hit:
            rows[src].ytd_buy_asym += 1

    return list(rows.values())