"""application/write_handler.py — Orchestrate validate → build → write pipeline.

Orchestration only — calls domain and infrastructure, no raw logic or I/O.
"""

from __future__ import annotations

from typing import Any

from obsidian_writers.domain.filename_builder import build_filepath
from obsidian_writers.domain.frontmatter_builder import build_note
from obsidian_writers.domain.validator import validate
from obsidian_writers.infrastructure.vault_writer import write_note
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def handle_write(
    schema_name: str,
    data: dict[str, Any],
    body: str = "",
    overwrite: bool = True,
) -> bool:
    """Run the full validate → build frontmatter → write pipeline.

    This is the internal entry point called by vault_interface.write_to_vault().
    Sending projects never call this directly.

    Args:
        schema_name: One of P115 | P300 | P020 | P400 | KB.
        data: Raw field dict from the sending project.
        body: Optional note body text appended below frontmatter.
        overwrite: If False, skip notes that already exist in vault.

    Returns:
        True if the note was written, False if skipped.

    Raises:
        ValueError: On unknown schema or validation failure.
        OSError: On disk write failure.
    """
    log.debug("handle_write called: schema=%s", schema_name)

    # Step 1 — Validate and normalize
    validated = validate(schema_name, data)

    # Step 2 — Build file path
    file_path = build_filepath(schema_name, validated)

    # Step 3 — Build note content
    content = build_note(schema_name, validated, body=body)

    # Step 4 — Write to vault
    written = write_note(file_path, content, overwrite=overwrite)

    if written:
        log.info("OK schema=%s file=%s", schema_name, file_path.name)
    return written
