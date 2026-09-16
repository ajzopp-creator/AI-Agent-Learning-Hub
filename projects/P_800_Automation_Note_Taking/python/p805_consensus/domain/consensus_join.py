"""consensus_join.py -- pure join/aggregation logic.

No file I/O here -- see infrastructure/ for readers and the writer.
"""

from __future__ import annotations

from datetime import date, timedelta

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
    candidate: RankedCandidate, tracker_rows: list[TrackerRow]
) -> bool:
    """True if any Tracker row matches this candidate's symbol within its
    forward join window and carries a counted verdict."""
    window_end = add_trading_days(
        candidate.first_seen.date(), JOIN_WINDOW_TRADING_DAYS
    )
    for row in tracker_rows:
        if row.symbol != candidate.ticker:
            continue
        row_date = row.date.date()
        if candidate.first_seen.date() <= row_date <= window_end:
            if row.step1_verdict.upper() in COUNTED_VERDICTS:
                return True
    return False


def aggregate_by_source(
    today_candidates: list[RankedCandidate],
    mtd_candidates: list[RankedCandidate],
    ytd_candidates: list[RankedCandidate],
    tracker_rows: list[TrackerRow],
) -> list[ConsensusRow]:
    """Build one ConsensusRow per distinct email source across all windows."""
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

    for c in mtd_candidates:
        hit = has_buy_asym_hit(c, tracker_rows)
        for src in c.sources:
            rows[src].mtd_candidates += 1
            if hit:
                rows[src].mtd_buy_asym += 1

    for c in ytd_candidates:
        hit = has_buy_asym_hit(c, tracker_rows)
        for src in c.sources:
            rows[src].ytd_candidates += 1
            if hit:
                rows[src].ytd_buy_asym += 1

    return list(rows.values())