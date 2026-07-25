"""vault_scanner.py -- Globs a schema's vault folder for notes in the lookback window.

I/O only. Builds the file list note_reader.py reads, using the filename's
own date+symbol key (Note Standard v1.1) instead of re-deriving dates from
frontmatter or a log file. Built against WO-P800-E4.001.

CHANGELOG:
  v1.0  2026-07-24  Initial version.
"""

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from shared_resources.chaikin_enrichment.config import (
    LOOKBACK_DAYS,
    VAULT_FOLDER_MAP,
    VAULT_ROOT,
)
from shared_resources.chaikin_enrichment.domain.candidate_filter import ScannedNote
from shared_resources.chaikin_enrichment.infrastructure.note_reader import read_note

# Matches vault md filenames built by filename_builder.py's P115/P300 branch:
# YYYY-MM-DD_SYMBOL.md (symbol may contain letters, digits, dots, hyphens).
_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_([A-Za-z0-9._-]+)\.md$")


def scan_schema(schema_name: str, today: Optional[date] = None) -> list[ScannedNote]:
    """Scans one schema's vault folder for notes in the lookback window.

    Args:
        schema_name: A key present in VAULT_FOLDER_MAP (e.g. "P115", "P300").
        today: Override for the reference date -- used by tests against
            fixed real notes. Defaults to date.today() in production.

    Returns:
        ScannedNote list for every note in the window with a readable
        write_route. Malformed notes (no frontmatter, no write_route) are
        silently skipped -- note_reader.read_note() returns None for those.

    Raises:
        ValueError: If schema_name is not in VAULT_FOLDER_MAP.
    """
    if schema_name not in VAULT_FOLDER_MAP:
        raise ValueError(f"No folder mapping for schema '{schema_name}'")

    folder = VAULT_ROOT / VAULT_FOLDER_MAP[schema_name]
    if not folder.is_dir():
        return []

    reference_date = today or date.today()
    earliest = reference_date - timedelta(days=LOOKBACK_DAYS)

    notes: list[ScannedNote] = []
    for entry in folder.iterdir():
        match = _FILENAME_RE.match(entry.name)
        if not match:
            continue

        note_date = date.fromisoformat(match.group(1))
        if not (earliest <= note_date <= reference_date):
            continue

        symbol = match.group(2)
        scanned = read_note(entry, symbol)
        if scanned is not None:
            notes.append(scanned)

    return notes
