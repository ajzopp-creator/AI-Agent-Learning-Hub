"""domain/filename_builder.py — Generate vault file paths for each schema.

Pure logic only — no I/O.

md schemas: filename key is signal_date + ticker (Note Standard v1.1 Decision 1):
  One canonical note per signal per symbol. Re-runs overwrite the same file;
  provenance is tracked via note_version and verdict_history in frontmatter.

json schemas (P400SIG, SIGNAL_V2): filename is signal date + symbol + a
  per-schema suffix + ".json", so legacy v1.0 and unified v2.0 packets coexist
  in the flat signals/ folder during the dual-emit window. Date is derived from
  signal_timestamp (packets carry no signal_date field).

CHANGELOG:
  v2.1  2026-06-07  Added JSON-schema branch: route P400SIG / SIGNAL_V2 to a
                    ".json" filename with a per-schema suffix; derive date from
                    signal_timestamp. md path unchanged. (WO-P800-E2.001)
  v2.0  2026-06-01  Use signal_date field for filename construction (was date).
                    Fallback to date field if signal_date absent (legacy callers).
  v1.0  2026-05-22  Initial version.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from obsidian_writers.config import (
    JSON_FILENAME_SUFFIX,
    OUTPUT_FORMAT,
    VAULT_FOLDER_MAP,
    VAULT_ROOT,
)
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def build_filepath(schema_name: str, data: dict[str, Any]) -> Path:
    """Generate the full vault file path for a record.

    md schemas:
        P115 / P020  →  YYYY-MM-DD_SYMBOL.md
        P300 / P400  →  YYYY-MM-DD_TICKER.md
        KB           →  YYYY-MM-DD_SLUG.md  (slug from title)
    json schemas:
        P400SIG      →  YYYY-MM-DD_SYMBOL_signal.json
        SIGNAL_V2    →  YYYY-MM-DD_SYMBOL_v2.0.json

    Args:
        schema_name: A key present in VAULT_FOLDER_MAP.
        data: Validated data dict. md schemas need signal_date (or fallback);
              json schemas need signal_timestamp (or signal_date) + symbol.

    Returns:
        Absolute Path to the target file inside the vault.

    Raises:
        ValueError: If schema_name is not in VAULT_FOLDER_MAP, or the required
            date field is absent.
    """
    if schema_name not in VAULT_FOLDER_MAP:
        raise ValueError(f"No folder mapping for schema '{schema_name}'")

    folder = VAULT_ROOT / VAULT_FOLDER_MAP[schema_name]

    if OUTPUT_FORMAT.get(schema_name) == "json":
        filename = _build_json_filename(schema_name, data)
    else:
        date_str = _get_date_str(data)
        identifier = _get_identifier(schema_name, data)
        filename = f"{date_str}_{identifier}.md"

    path = folder / filename
    log.debug("Built filepath: %s", path)
    return path


def _build_json_filename(schema_name: str, data: dict[str, Any]) -> str:
    """Build the filename for a raw JSON signal packet.

    Args:
        schema_name: A json-format schema ("P400SIG" | "SIGNAL_V2").
        data: Validated packet dict (signal_timestamp + symbol).

    Returns:
        Filename string, e.g. "2026-06-07_AAPL_v2.0.json".
    """
    date_str = _get_signal_date_str(data)
    symbol = str(data.get("symbol") or "UNKNOWN").upper().replace(" ", "_")
    suffix = JSON_FILENAME_SUFFIX.get(schema_name, "")
    return f"{date_str}_{symbol}{suffix}.json"


def _get_signal_date_str(data: dict[str, Any]) -> str:
    """Extract a YYYY-MM-DD date from a signal packet.

    Packets carry signal_timestamp (ISO 8601), not signal_date. signal_date is
    accepted as an override if a producer chooses to send one.

    Args:
        data: Validated packet dict.

    Returns:
        Date string in YYYY-MM-DD format.

    Raises:
        ValueError: If neither signal_timestamp nor signal_date is present.
    """
    raw = data.get("signal_date") or data.get("signal_timestamp")
    if raw is None:
        raise ValueError(
            "Signal packet must contain 'signal_timestamp' or 'signal_date'"
        )
    return str(raw)[:10]  # ISO 8601 datetime or date → YYYY-MM-DD


def _get_date_str(data: dict[str, Any]) -> str:
    """Extract date string from signal_date, falling back to date field.

    signal_date is the Note Standard v1.1 canonical field.
    date is retained as a deprecated fallback for legacy callers.

    Args:
        data: Validated data dict.

    Returns:
        Date string in YYYY-MM-DD format.

    Raises:
        ValueError: If neither signal_date nor date is present.
    """
    date_val = (
        data.get("signal_date")
        or data.get("date")
        or data.get("close_date")
        or data.get("anchor_date")
    )
    if date_val is None:
        raise ValueError("Data dict must contain a 'signal_date' field")
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
