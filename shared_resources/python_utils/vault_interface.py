"""vault_interface.py — P_800 public vault API.

This is the ONLY file other projects need to import.
Pass a schema name and a data dict. P_800 handles everything else.

Usage (from any sending project):

    from shared_resources.python_utils.vault_interface import write_to_vault

    write_to_vault("P115", {
        "date": "2026-05-22",
        "symbol": "AAPL",
        "step1_verdict": "BUY",
        "setup_score": 5,
        "traded": "N",
    })

    # P_300 with narrative body
    write_to_vault("P300", signal_data, body=report_text)
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import Any

# Add P_800 python folder to path (works from any Hub project)
p800_python_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../projects/P_800_Automation_Note_Taking/python")
)
if p800_python_path not in sys.path:
    sys.path.insert(0, p800_python_path)

from obsidian_writers.application.write_handler import handle_write

def write_to_vault(
    schema_name: str,
    data: dict[str, Any],
    body: str = "",
    overwrite: bool = True,
) -> bool:
    """Write a record to the Obsidian vault via the P_800 interface layer.

    The sending project passes field data. P_800 validates, builds the
    YAML frontmatter, determines the correct vault folder, and writes the note.

    Args:
        schema_name: Target schema — P115 | P300 | P020 | P400 | KB.
        data: Dict of field names and values to write. Unknown fields are
              ignored. Missing optional fields default to null.
        body: Optional markdown text appended below the frontmatter
              (e.g. the full P_300 narrative block).
        overwrite: If False, existing notes are skipped without error.

    Returns:
        True if the note was written, False if skipped.

    Raises:
        ValueError: If schema_name is unknown or required fields are missing.
        OSError: If the vault write fails (permissions, disk full, etc.).
    """
    try:
        return handle_write(schema_name, data, body=body, overwrite=overwrite)
    except (ValueError, OSError) as exc:
        log.error("write_to_vault failed: schema=%s error=%s", schema_name, exc)
        raise
