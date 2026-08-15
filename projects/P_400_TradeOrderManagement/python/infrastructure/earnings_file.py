"""earnings_file.py -- Read and validate the session-scoped earnings file.

Infrastructure layer: I/O and validation only, no business logic.

Bridge until WO-P400-E5.002 automates earnings/sector acquisition. Schwab's
market-data API carries no earnings calendar, so the data comes from a manual
web-search pass written once per session to earnings_YYYY-MM-DD.json in the
project python directory, alongside the snapshot files.

DESIGN RULE (WO-P400-E5.003 Scope 5): a symbol absent from the file is a hard,
named error. It is never a silent skip and never an assumed "no earnings".
Trading a stock through its earnings print because a lookup was missing is
exactly the failure the MACRO earnings gate exists to prevent, and defaulting
to "clear" on missing data would route around that gate rather than enforce it.
A present-but-null next_earnings_date is a DIFFERENT state -- it means the
lookup ran and found no confirmed date -- and is returned as-is for the caller
to weigh, not treated as clear either.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

from pydantic import ValidationError

from config import BATCH_EARNINGS_DIR, BATCH_EARNINGS_FILE_PATTERN
from schemas import EarningsEntry

logger = logging.getLogger("p400.earnings_file")


class EarningsDataMissing(Exception):
    """Raised when a symbol has no entry in the session earnings file."""


def earnings_file_path(session_date: str) -> Path:
    """Full path to the session-scoped earnings file.

    Args:
        session_date: ISO date, YYYY-MM-DD.
    """
    return BATCH_EARNINGS_DIR / BATCH_EARNINGS_FILE_PATTERN.format(date=session_date)


def load_earnings_file(session_date: str) -> Dict[str, EarningsEntry]:
    """Load and validate the session earnings file.

    Args:
        session_date: ISO date, YYYY-MM-DD.

    Returns:
        Mapping of uppercased symbol to validated EarningsEntry.

    Raises:
        FileNotFoundError: file absent -- the batch cannot proceed without it.
        ValueError: malformed JSON or a record failing schema validation.
    """
    path = earnings_file_path(session_date)
    if not path.exists():
        raise FileNotFoundError(
            f"Earnings file not found: {path}. Write it from this session's "
            "earnings lookup pass before running batch-2b."
        )

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Earnings file {path} is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(
            f"Earnings file {path} must be a JSON object keyed by symbol, "
            f"got {type(raw).__name__}."
        )

    entries: Dict[str, EarningsEntry] = {}
    for symbol, record in raw.items():
        try:
            entries[symbol.upper()] = EarningsEntry(**record)
        except ValidationError as exc:
            raise ValueError(f"Earnings entry for {symbol} failed validation: {exc}") from exc

    logger.info("Loaded %d earnings entries from %s", len(entries), path.name)
    return entries


def require_entry(entries: Dict[str, EarningsEntry], symbol: str) -> EarningsEntry:
    """Return the entry for symbol, or raise.

    Raises:
        EarningsDataMissing: symbol absent. Deliberately fatal for that symbol
            rather than defaulting to clear -- see module docstring.
    """
    entry = entries.get(symbol.upper())
    if entry is None:
        raise EarningsDataMissing(
            f"No earnings entry for {symbol}. Add it to the session earnings "
            "file; this symbol will not be evaluated without one."
        )
    return entry
