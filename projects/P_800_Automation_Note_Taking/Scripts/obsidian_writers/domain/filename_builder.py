"""domain/filename_builder.py — Generate vault file paths for each schema.

Pure logic only — no I/O.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from obsidian_writers.config import VAULT_FOLDER_MAP, VAULT_ROOT
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def build_filepath(schema_name: str, data: dict[str, Any]) -> Path:
    """Generate the full vault file path for a note.

    File naming convention per schema:
        P115 / P020  →  YYYY-MM-DD_SYMBOL.md
        P300 / P400  →  YYYY-MM-DD_TICKER.md
        KB           →  YYYY-MM-DD_SLUG.md  (slug from title)

    Args:
        schema_name: One of P115 | P300 | P020 | P400 | KB.
        data: Validated data dict containing at minimum 'date'.

    Returns:
        Absolute Path to the target .md file inside the vault.

    Raises:
        ValueError: If schema_name is not in VAULT_FOLDER_MAP.
    """
    if schema_name not in VAULT_FOLDER_MAP:
        raise ValueError(f"No folder mapping for schema '{schema_name}'")

    folder = VAULT_ROOT / VAULT_FOLDER_MAP[schema_name]
    date_str = _get_date_str(data)
    identifier = _get_identifier(schema_name, data)
    filename = f"{date_str}_{identifier}.md"

    path = folder / filename
    log.debug("Built filepath: %s", path)
    return path


def _get_date_str(data: dict[str, Any]) -> str:
    """Extract and format the primary date field.

    Args:
        data: Validated data dict.

    Returns:
        Date string in YYYY-MM-DD format.
    """
    date_val = data.get("date") or data.get("close_date") or data.get("anchor_date")
    if date_val is None:
        raise ValueError("Data dict must contain a 'date' field")
    return str(date_val)[:10]  # handles date objects and ISO strings


def _get_identifier(schema_name: str, data: dict[str, Any]) -> str:
    """Extract the secondary part of the filename (symbol, ticker, or slug).

    Args:
        schema_name: Schema identifier.
        data: Validated data dict.

    Returns:
        Clean identifier string safe for use in a filename.
    """
    if schema_name in ("P115", "P020"):
        raw = data.get("symbol") or "UNKNOWN"
    elif schema_name in ("P300", "P400"):
        raw = data.get("ticker") or "UNKNOWN"
    elif schema_name == "KB":
        title = data.get("title") or "untitled"
        raw = _slugify(title)[:40]
    else:
        raw = "UNKNOWN"
    return raw.upper().replace(" ", "_")


def _slugify(text: str) -> str:
    """Convert a title string to a filesystem-safe slug.

    Args:
        text: Raw title string.

    Returns:
        Lowercase hyphen-separated slug.
    """
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text
