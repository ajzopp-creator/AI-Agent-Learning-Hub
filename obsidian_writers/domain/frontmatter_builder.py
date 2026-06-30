"""domain/frontmatter_builder.py — Build YAML frontmatter and .md note content.

Pure logic only — no I/O.

Required base fields are emitted first in a fixed order (Note Standard v1.1),
followed by system-specific fields. verdict_history is serialized as a YAML
block list.

CHANGELOG:
  v2.0  2026-06-01  Emit required base fields first in defined order.
                    Serialize verdict_history as YAML block list.
  v1.0  2026-05-22  Initial version.
"""

from __future__ import annotations

from typing import Any

from obsidian_writers.config import SCHEMA_VERSIONS
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)

# Required base fields emitted first, in this order (Note Standard v1.1 §3.2)
_BASE_FIELD_ORDER = [
    "source",
    "schema_version",
    "signal_date",
    "run_date",
    "run_ts",
    "ticker",
    "verdict",
    "written_by",
    "note_version",
    "verdict_history",
]

# Deprecated fields that should not be emitted if signal_date is present
_DEPRECATED_FIELDS = {"date", "anchor_date"}


def build_frontmatter(schema_name: str, data: dict[str, Any]) -> str:
    """Convert validated data dict to YAML frontmatter string.

    Required base fields are emitted first in defined order.
    System-specific fields follow in dict order.
    Deprecated fields (date, anchor_date) are suppressed when signal_date exists.

    Args:
        schema_name: Schema identifier — added as 'source' field.
        data: Validated dict from validator.validate(), enriched by write_handler.

    Returns:
        YAML frontmatter block including opening and closing --- delimiters.
    """
    lines = ["---"]

    # Emit required base fields first
    base_data = {
        "source": schema_name,
        "schema_version": SCHEMA_VERSIONS.get(schema_name, "2.0"),
        **{k: data[k] for k in _BASE_FIELD_ORDER[2:] if k in data},
    }
    for key in _BASE_FIELD_ORDER:
        if key == "source":
            lines.append(f"source: {schema_name}")
        elif key == "schema_version":
            lines.append(f'schema_version: "{SCHEMA_VERSIONS.get(schema_name, "2.0")}"')
        elif key == "verdict_history":
            lines.extend(_format_verdict_history(data.get("verdict_history", [])))
        elif key in data:
            lines.append(_format_field(key, data[key]))

    # Emit system-specific fields (skip base fields and deprecated fields)
    has_signal_date = "signal_date" in data and data["signal_date"] is not None
    skip = set(_BASE_FIELD_ORDER) | {"source", "schema_version"}
    if has_signal_date:
        skip |= _DEPRECATED_FIELDS

    for key, value in data.items():
        if key not in skip:
            lines.append(_format_field(key, value))

    lines.append("---")
    return "\n".join(lines)


def build_note(schema_name: str, data: dict[str, Any], body: str = "") -> str:
    """Assemble a complete .md note: frontmatter + body header + optional body.

    Body header format (Note Standard v1.1 §3.5):
        # TICKER - VERDICT (source)

    Args:
        schema_name: Used for frontmatter source field and body header.
        data: Validated data dict.
        body: Optional raw text appended below the header.

    Returns:
        Complete markdown note content as a string.
    """
    fm = build_frontmatter(schema_name, data)

    ticker = data.get("ticker") or data.get("symbol") or "UNKNOWN"
    verdict = data.get("verdict") or "PASS"
    header = f"# {ticker.upper()} - {verdict} ({schema_name})"

    if body:
        return f"{fm}\n\n{header}\n\n{body.strip()}\n"
    return f"{fm}\n\n{header}\n"


def _format_verdict_history(history: list) -> list[str]:
    """Serialize verdict_history as a YAML block list.

    Empty list → single line: verdict_history: []
    Non-empty  → block list with one entry per history item.

    Args:
        history: List of dicts, each with verdict, run_date, note_version keys.

    Returns:
        List of YAML lines (without trailing newline).
    """
    if not history:
        return ["verdict_history: []"]
    lines = ["verdict_history:"]
    for entry in history:
        v = entry.get("verdict", "")
        rd = entry.get("run_date", "")
        nv = entry.get("note_version", "")
        lines.append(f'  - {{verdict: {v}, run_date: {rd}, note_version: {nv}}}')
    return lines


def _format_field(key: str, value: Any) -> str:
    """Format a single YAML key-value pair.

    Args:
        key: Field name.
        value: Field value — handles None, bool, list, str, numeric, date.

    Returns:
        Formatted YAML line.
    """
    if value is None:
        return f"{key}: null"
    if isinstance(value, bool):
        return f"{key}: {str(value).lower()}"
    if isinstance(value, list):
        if not value:
            return f"{key}: []"
        items = ", ".join(f'"{v}"' for v in value)
        return f"{key}: [{items}]"
    if isinstance(value, str):
        if any(c in value for c in (':', '#', '{', '}', '[', ']', ',')):
            return f'{key}: "{value}"'
        return f"{key}: {value}"
    return f"{key}: {value}"