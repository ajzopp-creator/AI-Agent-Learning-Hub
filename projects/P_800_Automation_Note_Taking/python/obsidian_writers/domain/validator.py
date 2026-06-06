"""domain/validator.py — Validate incoming data dict against P_800 schema registry.

Pure logic only — no I/O, no file reads, no network calls.
Raises ValueError on unknown schema or validation failure.
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from obsidian_writers.logger_setup import get_logger
from obsidian_writers.schemas import SCHEMA_REGISTRY

log = get_logger(__name__)


def validate(schema_name: str, data: dict[str, Any]) -> dict[str, Any]:
    """Validate data dict against the named schema.

    Args:
        schema_name: One of P115 | P300 | P020 | P400 | KB.
        data: Raw field dictionary from the sending project.

    Returns:
        Validated and normalized dict (None for missing optional fields).

    Raises:
        ValueError: If schema_name is unknown or data fails validation.
    """
    if schema_name not in SCHEMA_REGISTRY:
        known = ", ".join(SCHEMA_REGISTRY.keys())
        raise ValueError(
            f"Unknown schema '{schema_name}'. Known schemas: {known}"
        )

    model_class = SCHEMA_REGISTRY[schema_name]

    try:
        record = model_class(**data)
    except ValidationError as exc:
        errors = _format_errors(exc)
        log.error("Validation failed for schema=%s: %s", schema_name, errors)
        raise ValueError(
            f"Validation failed for schema '{schema_name}':\n{errors}"
        ) from exc

    log.debug("Validated schema=%s symbol/ticker=%s",
              schema_name, data.get("symbol") or data.get("ticker") or "?")

    return record.model_dump()


def _format_errors(exc: ValidationError) -> str:
    """Format pydantic ValidationError into a readable string.

    Args:
        exc: The ValidationError from pydantic.

    Returns:
        Human-readable error summary.
    """
    lines = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err["loc"])
        lines.append(f"  [{field}] {err['msg']}")
    return "\n".join(lines)
