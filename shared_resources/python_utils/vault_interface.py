"""vault_interface.py — P_800 public vault API.

This is the ONLY file other projects need to import.
Pass a schema name and a data dict. P_800 handles everything else.

Usage (from any sending project):

    from shared_resources.python_utils.vault_interface import write_to_vault

    # Markdown note (P_115 evaluation)
    write_to_vault("P115", {
        "date": "2026-05-22",
        "symbol": "AAPL",
        "step1_verdict": "BUY",
        "setup_score": 5,
        "traded": "N",
    })

    # P_300 with narrative body
    write_to_vault("P300", signal_data, body=report_text)

    # Raw JSON signal packet (unified stock/option handoff to P_400)
    write_to_vault("SIGNAL_V2", packet_dict)

Schema names: P115 | P300 | P020 | P400 | KB (markdown notes),
              P400SIG | SIGNAL_V2 (raw JSON signal packets -> signals/).
P400SIG is the legacy v1.0 packet, retired at the SIGNAL_V2 cutover.
"""

from __future__ import annotations

from typing import Any

from obsidian_writers.application.write_handler import handle_write
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def write_to_vault(
    schema_name: str,
    data: dict[str, Any],
    body: str = "",
    overwrite: bool = True,
) -> bool:
    """Write a record to the Obsidian vault via the P_800 interface layer.

    The sending project passes field data. P_800 validates, builds the output
    (YAML frontmatter note or raw JSON packet), determines the correct vault
    folder, and writes the file.

    Args:
        schema_name: Target schema. Markdown notes: P115 | P300 | P020 | P400 |
              KB. JSON signal packets: P400SIG (legacy v1.0) | SIGNAL_V2 (unified
              stock/option). JSON packets route to TradeOrderManagement/signals/.
        data: Dict of field names and values to write. Unknown fields are
              ignored. Missing optional fields default to null.
        body: Optional markdown text appended below the frontmatter
              (md schemas only; ignored for JSON packets).
        overwrite: If False, existing files are skipped without error.

    Returns:
        True if the file was written, False if skipped.

    Raises:
        ValueError: If schema_name is unknown or required fields are missing.
        OSError: If the vault write fails (permissions, disk full, etc.).
    """
    try:
        return handle_write(schema_name, data, body=body, overwrite=overwrite)
    except (ValueError, OSError) as exc:
        log.error("write_to_vault failed: schema=%s error=%s", schema_name, exc)
        raise
