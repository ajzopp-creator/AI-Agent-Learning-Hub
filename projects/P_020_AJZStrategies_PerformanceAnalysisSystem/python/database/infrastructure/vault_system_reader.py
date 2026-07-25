"""P_400 Obsidian vault reader for system attribution (WO-P020-E1.007).

Reads P_400 lifecycle records and builds a VaultLookup. I/O only -- the
resolution chain that consumes this lives in domain/system_resolver.py.

The vault folder is resolved through P_800's obsidian_writers config
(VAULT_ROOT + VAULT_FOLDER_MAP) rather than a literal path, so the
pending WO-P800-E3.003 rename (TradeManagement -> TradeOrderManagement)
does not break this reader.

Frontmatter is parsed with a line scanner rather than a YAML library:
P_400 records contain a write_route_history block of inline-flow
mappings, and only flat scalar keys are needed here.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\infrastructure\\vault_system_reader.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional

from config import (
    VAULT_ATTRIBUTION_FIELDS,
    VAULT_MATCHABLE_STATUSES,
    VAULT_P400_SCHEMAS,
)
from vault_schemas import VaultEntry, VaultLookup

logger = logging.getLogger(__name__)

_SCALAR = re.compile(r"^([a-zA-Z0-9_]+):\s*(.*)$")
_DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})_")


def resolve_vault_folders() -> List[tuple]:
    """Resolve P_400 vault folders via P_800's shared config.

    Returns:
        List of (schema_name, Path) pairs for folders that exist on disk.
        Empty list if P_800's config cannot be imported or no folder is
        present -- callers degrade to tracker-only matching.
    """
    try:
        from obsidian_writers.config import VAULT_FOLDER_MAP, VAULT_ROOT
    except Exception as e:
        logger.warning(f"Could not import P_800 vault config: {e}")
        return []

    folders = []
    for schema in VAULT_P400_SCHEMAS:
        rel = VAULT_FOLDER_MAP.get(schema)
        if not rel:
            logger.warning(f"No VAULT_FOLDER_MAP entry for schema: {schema}")
            continue
        path = Path(VAULT_ROOT) / rel
        if path.is_dir():
            folders.append((schema, path))
        else:
            logger.warning(f"Vault folder missing on disk: {path}")
    return folders


def _parse_frontmatter(text: str) -> Dict[str, str]:
    """Extract flat scalar keys from a note's YAML frontmatter block.

    Nested and inline-flow values (write_route_history entries) are
    skipped -- only top-level scalars are needed.

    Args:
        text: Full note contents.

    Returns:
        Dict of key -> raw string value. 'null' values are dropped.
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


def _extract_system(fields: Dict[str, str]) -> Optional[str]:
    """Return the attribution value from the first populated field.

    Checks VAULT_ATTRIBUTION_FIELDS in priority order. p115_linked and
    p300_linked are deliberately excluded -- 189 of 191 records carry
    p300_linked=true, a schema default rather than real attribution.
    """
    for key in VAULT_ATTRIBUTION_FIELDS:
        value = fields.get(key)
        if value:
            return value.strip().upper()
    return None


def _build_entry(
    path: Path, schema: str, fields: Dict[str, str]
) -> Optional[VaultEntry]:
    """Assemble a VaultEntry, or None when required fields are missing."""
    symbol = fields.get("ticker", "").strip().upper()
    signal_date = fields.get("signal_date", "").strip()
    if not signal_date:
        m = _DATE_PREFIX.match(path.name)
        signal_date = m.group(1) if m else ""
    if not symbol or not signal_date:
        return None

    return VaultEntry(
        symbol=symbol,
        signal_date=signal_date,
        system=_extract_system(fields),
        lifecycle_status=fields.get("lifecycle_status", "").strip().upper(),
        source_schema=schema,
        note_name=path.name,
    )


def load_vault_lookup() -> Optional[VaultLookup]:
    """Read all P_400 vault records into a VaultLookup.

    DROPPED records are excluded: a dropped signal means the trade was
    not taken, so matching it to a later fill of the same symbol would
    attribute a real trade to a signal that was passed on.

    Returns:
        Populated VaultLookup, or None if no vault folder resolved.
    """
    folders = resolve_vault_folders()
    if not folders:
        logger.warning("P_400 vault unavailable -- tracker-only matching.")
        return None

    lookup = VaultLookup(
        vault_folder=", ".join(str(p) for _, p in folders)
    )

    for schema, folder in folders:
        for note in folder.glob("*.md"):
            try:
                text = note.read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                logger.warning(f"Could not read {note.name}: {e}")
                continue

            entry = _build_entry(note, schema, _parse_frontmatter(text))
            if entry is None:
                continue

            lookup.total_records += 1
            if entry.lifecycle_status not in VAULT_MATCHABLE_STATUSES:
                lookup.skipped_status += 1
                continue

            lookup.covered.setdefault(entry.symbol, []).append(entry)
            if entry.system:
                lookup.attributed.setdefault(entry.symbol, []).append(entry)

    logger.info(lookup.summary())
    return lookup
