"""consensus_dashboard_runner.py -- orchestrates the full consensus build.

Reads P_805 and Tracker history, joins them, writes Dashboard.md.
"""

from __future__ import annotations

import logging
from datetime import date

from p805_consensus.domain.consensus_join import (
    aggregate_by_source,
    month_to_date_start,
    year_to_date_start,
)
from p805_consensus.infrastructure.dashboard_section_writer import write_section
from p805_consensus.infrastructure.ranked_csv_reader import read_candidates
from p805_consensus.infrastructure.tracker_reader import read_tracker_rows

logger = logging.getLogger(__name__)


def run(as_of: date | None = None) -> int:
    """Build and write the consensus section for as_of (defaults to today).

    Returns the number of email-source rows written.
    """
    as_of = as_of or date.today()
    mtd_start = month_to_date_start(as_of)
    ytd_start = year_to_date_start(as_of)

    # Windowed by which file a row came from, not by its first_seen date --
    # P_805's first_seen routinely lags a day behind the file that reports
    # it, so filtering by first_seen undercounts "today" (WO-P800-E6.001,
    # live-verified 2026-09-08).
    today_candidates = read_candidates(as_of, as_of)
    mtd_candidates = read_candidates(mtd_start, as_of)
    ytd_candidates = read_candidates(ytd_start, as_of)

    tracker_rows = read_tracker_rows()

    rows = aggregate_by_source(
        today_candidates, mtd_candidates, ytd_candidates, tracker_rows
    )
    write_section(rows)
    logger.info("Consensus dashboard run complete: %d sources", len(rows))
    return len(rows)