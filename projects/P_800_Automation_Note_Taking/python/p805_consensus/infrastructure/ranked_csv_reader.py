"""ranked_csv_reader.py -- reads P_805 ranked.csv files into RankedCandidate records."""

from __future__ import annotations

import csv
import logging
from datetime import date
from pathlib import Path

from p805_consensus.config import RANKED_CSV_DIR, RANKED_CSV_SUFFIX
from p805_consensus.schemas import RankedCandidate

logger = logging.getLogger(__name__)


def _csv_files_in_range(start: date, end: date) -> list[Path]:
    """List ranked.csv files whose filename date falls within [start, end]."""
    matches: list[Path] = []
    for path in sorted(RANKED_CSV_DIR.glob(f"*{RANKED_CSV_SUFFIX}")):
        stem_date_str = path.name.replace(RANKED_CSV_SUFFIX, "")
        try:
            file_date = date.fromisoformat(stem_date_str)
        except ValueError:
            logger.warning("Skipping unparseable ranked.csv filename: %s", path.name)
            continue
        if start <= file_date <= end:
            matches.append(path)
    return matches


def _parse_row(row: dict[str, str]) -> RankedCandidate:
    """Convert one CSV row into a RankedCandidate.

    sector_count is absent on files written before that column existed;
    P_805's RankedCandidate defaults it to 1, so this reader does too.
    """
    return RankedCandidate(
        ticker=row["ticker"],
        source_count=int(row["source_count"]),
        sector_count=int(row.get("sector_count") or 1),
        sources=row["sources"].split("|"),
        direction=row["direction"],
        first_seen=row["first_seen"],
        last_seen=row["last_seen"],
    )


def read_candidates(start: date, end: date) -> list[RankedCandidate]:
    """Read and parse every ranked.csv row across [start, end], one file per day."""
    candidates: list[RankedCandidate] = []
    for path in _csv_files_in_range(start, end):
        # P_805 writes these as utf-8-sig; a plain utf-8 open leaves a BOM
        # on the first header and KeyError('ticker') on every row.
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    candidates.append(_parse_row(row))
                except (KeyError, ValueError) as exc:
                    logger.warning("Skipping bad row in %s: %s", path.name, exc)
    return candidates