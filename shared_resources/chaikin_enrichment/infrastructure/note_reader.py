"""note_reader.py -- Reads a vault note's frontmatter and body markers.

I/O only. Parses YAML frontmatter to extract write_route and checks the
note body for an existing Chaikin Power Gauge section. Built against
WO-P800-E4.001.

CHANGELOG:
  v1.0  2026-07-24  Initial version.
"""

from pathlib import Path
from typing import Optional

import yaml

from shared_resources.chaikin_enrichment.config import CHAIKIN_SECTION_HEADER
from shared_resources.chaikin_enrichment.domain.candidate_filter import ScannedNote


def read_note(note_path: Path, symbol: str) -> Optional[ScannedNote]:
    """Reads one vault note and builds a ScannedNote for the domain filter.

    Args:
        note_path: Absolute path to the .md note.
        symbol: Ticker symbol already parsed from the filename by
            vault_scanner.py (schema-agnostic -- avoids needing to know
            whether a schema's frontmatter field is 'symbol' or 'ticker').

    Returns:
        A ScannedNote, or None if the note can't be read, has no
        frontmatter block, or has no write_route (malformed / not yet
        written by write_handler).
    """
    try:
        text = note_path.read_text(encoding="utf-8")
    except OSError:
        return None

    write_route = _parse_write_route(text)
    if write_route is None:
        return None

    has_chaikin_section = CHAIKIN_SECTION_HEADER in text

    return ScannedNote(
        symbol=symbol,
        note_path=str(note_path),
        write_route=write_route,
        has_chaikin_section=has_chaikin_section,
    )


def _parse_write_route(text: str) -> Optional[str]:
    """Extracts write_route from a note's YAML frontmatter block.

    Args:
        text: Full note content, frontmatter delimited by '---' lines.

    Returns:
        The write_route value, or None if frontmatter is missing/malformed
        or write_route is absent/null.
    """
    if not text.startswith("---"):
        return None

    end = text.find("\n---", 3)
    if end == -1:
        return None

    frontmatter_block = text[3:end]
    try:
        parsed = yaml.safe_load(frontmatter_block)
    except yaml.YAMLError:
        return None

    if not isinstance(parsed, dict):
        return None

    return parsed.get("write_route")
