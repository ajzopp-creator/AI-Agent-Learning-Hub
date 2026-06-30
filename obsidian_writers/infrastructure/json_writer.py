"""infrastructure/json_writer.py — Write raw signal packets as JSON files.

Used by JSON schemas (P400SIG, SIGNAL_V2): validate → build path → json_writer.
No verdict normalization, no provenance, no frontmatter — raw signal output.

CHANGELOG:
  v1.1  2026-06-07  Fixed signature to write_signal(output_path, data, overwrite)
                    to match write_handler's call; added overwrite skip; raise
                    OSError on write failure instead of swallowing it (matches the
                    write_to_vault contract). (WO-P800-E2.001)
  v1.0  2026-06-02  Initial version (Enhancement 1).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def write_signal(
    output_path: str | Path,
    data: dict[str, Any],
    overwrite: bool = True,
) -> bool:
    """Write a signal packet to disk as a raw JSON file.

    Args:
        output_path: Full path for the JSON output file.
        data: Validated signal packet dict.
        overwrite: If False, skip when the file already exists (returns False).

    Returns:
        True if the file was written, False if skipped because it existed.

    Raises:
        OSError: If the write fails (permissions, disk full, bad path, etc.).
    """
    output_path = Path(output_path)

    if output_path.exists() and not overwrite:
        log.info("skip (exists, overwrite=False): %s", output_path.name)
        return False

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    except OSError:
        log.exception("signal write failed: %s", output_path)
        raise

    log.info("signal written: %s", output_path.name)
    return True
