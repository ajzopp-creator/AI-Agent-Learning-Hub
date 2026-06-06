"""domain/frontmatter_builder.py — Build YAML frontmatter and .md note content.

Pure logic only — no I/O.
"""

from __future__ import annotations

from typing import Any

from obsidian_writers.config import SCHEMA_VERSIONS
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)

_YAML_INDENT = ""


def build_frontmatter(schema_name: str, data: dict[str, Any]) -> str:
    """Convert validated data dict to YAML frontmatter string.

    Args:
        schema_name: Schema identifier — added as 'source' field.
        data: Validated dict from validator.validate().

    Returns:
        YAML frontmatter block including opening and closing --- delimiters.
    """
    lines = ["---"]
    lines.append(f"source: {schema_name}")
    lines.append(f"schema_version: \"{SCHEMA_VERSIONS.get(schema_name, '1.0')}\"")

    for key, value in data.items():
        lines.append(_format_field(key, value))

    lines.append("---")
    return "\n".join(lines)


def build_note(schema_name: str, data: dict[str, Any], body: str = "") -> str:
    """Assemble a complete .md note: frontmatter + optional body.

    Args:
        schema_name: Used for frontmatter source field.
        data: Validated data dict.
        body: Optional raw text appended below frontmatter (e.g. P_300 narrative).

    Returns:
        Complete markdown note content as a string.
    """
    fm = build_frontmatter(schema_name, data)
    if body:
        return f"{fm}\n\n{body.strip()}\n"
    return f"{fm}\n"


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
        # Quote strings containing special YAML characters
        if any(c in value for c in (':', '#', '{', '}', '[', ']', ',')):
            return f'{key}: "{value}"'
        return f"{key}: {value}"
    return f"{key}: {value}"
