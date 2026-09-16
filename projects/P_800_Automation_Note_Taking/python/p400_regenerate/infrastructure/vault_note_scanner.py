"""p400_regenerate/infrastructure/vault_note_scanner.py -- find a P_400
vault note by its order_id.

I/O only. Reads P400/P400_PAPER note files directly from disk -- reading
vault content is not restricted to P_800 the way writing is (P_020's own
infrastructure/vault_system_reader.py already does the same kind of
direct read for system attribution). Frontmatter parsing mirrors that
file's proven line-scanner approach rather than a full YAML library,
since only flat scalar keys are needed here.

Part of: P_800 Automation Note-Taking -- p400_regenerate sub-project
Layer:   infrastructure (I/O)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional

_SCALAR = re.compile(r"^([a-zA-Z0-9_]+):\s*(.*)$")


def _parse_frontmatter(text: str) -> Dict[str, str]:
    """Extract flat scalar keys from a note's YAML frontmatter block.

    Same approach as P_020's vault_system_reader.py's proven scanner --
    nested/inline-flow values (write_route_history entries) are skipped,
    only top-level scalars are needed to rebuild a write_to_vault()
    payload.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}

    fields: Dict[str, str] = {}
    for line in text[3:end].splitlines():
        if not line or line.startswith((" ", "\t", "-", "#")):
            continue
        m = _SCALAR.match(line)
        if not m:
            continue
        value = m.group(2).strip().strip('"').strip("'")
        if value and value.lower() != "null":
            fields[m.group(1)] = value
    return fields


def find_note_by_order_id(order_id: str) -> Optional[Dict[str, str]]:
    """Find the P400/P400_PAPER vault note matching a broker order_id.

    Args:
        order_id: Broker order ID (matches P_020's schwab_order_id and
            the vault note's own order_id field).

    Returns:
        The note's full parsed frontmatter dict, plus '_note_path' (the
        absolute path as a string, needed by the caller to overwrite in
        place) and '_schema' (which vault schema it belongs to: 'P400'
        or 'P400_PAPER'), or None if no matching note is found.
    """
    try:
        from obsidian_writers.config import VAULT_FOLDER_MAP, VAULT_ROOT
    except Exception:
        return None

    for schema in ("P400", "P400_PAPER"):
        rel = VAULT_FOLDER_MAP.get(schema)
        if not rel:
            continue
        folder = Path(VAULT_ROOT) / rel
        if not folder.is_dir():
            continue
        for note_path in folder.glob("*.md"):
            try:
                text = note_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            fields = _parse_frontmatter(text)
            if fields.get("order_id") == str(order_id):
                fields["_note_path"] = str(note_path)
                fields["_schema"] = schema
                return fields
    return None
