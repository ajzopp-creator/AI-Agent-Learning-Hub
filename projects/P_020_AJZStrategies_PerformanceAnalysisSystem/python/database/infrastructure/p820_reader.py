"""p820_reader.py -- Infrastructure layer.

Reads P_820 (Order Signal Capture) vault notes -- the highest-priority
source in the resolver chain. Unlike ThinkLog, P_820 records are already
structured fields written directly by Claude at dictation time, so there
is no free-text tag parsing here -- just frontmatter read + lookup build.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\infrastructure\\p820_reader.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure
"""
from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from typing import Dict, Optional, Tuple, TypedDict

logger = logging.getLogger(__name__)

_SCALAR = re.compile(r"^([a-zA-Z0-9_]+):\s*(.*)$")


class P820Entry(TypedDict):
    symbol:       str
    signal_date:  date
    why_code:     Optional[str]
    sig_code:     Optional[str]
    entry_price:  Optional[float]
    stop_price:   Optional[float]
    target_price: Optional[float]
    notes:        Optional[str]


def resolve_p820_folder() -> Optional[Path]:
    """Resolve the P_820 vault folder via P_800's shared config.

    Returns:
        Path if the folder exists on disk, else None -- callers degrade
        to ThinkLog/tracker/default without P_820 in the chain.
    """
    try:
        from obsidian_writers.config import VAULT_FOLDER_MAP, VAULT_ROOT
    except Exception as e:
        logger.warning(f"Could not import P_800 vault config: {e}")
        return None

    rel = VAULT_FOLDER_MAP.get("P820")
    if not rel:
        logger.warning("No VAULT_FOLDER_MAP entry for schema: P820")
        return None

    path = Path(VAULT_ROOT) / rel
    if not path.is_dir():
        logger.info(f"P_820 vault folder not yet present: {path}")
        return None
    return path


def _parse_frontmatter(text: str) -> Dict[str, str]:
    """Extract flat scalar keys from a note's YAML frontmatter block.

    Same lightweight line-scanner as vault_system_reader.py -- P_820
    notes have no nested structures (no write_route_history entries with
    real content), so this covers every field.
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


def _build_entry(fields: Dict[str, str]) -> Optional[P820Entry]:
    """Assemble a P820Entry, or None when required fields are missing."""
    symbol = fields.get("symbol", "").strip().upper()
    signal_date_raw = fields.get("signal_date", "").strip()
    if not symbol or not signal_date_raw:
        return None
    try:
        signal_date = date.fromisoformat(signal_date_raw)
    except ValueError:
        return None

    def _f(key: str) -> Optional[float]:
        v = fields.get(key)
        try:
            return float(v) if v is not None else None
        except ValueError:
            return None

    return P820Entry(
        symbol=symbol,
        signal_date=signal_date,
        why_code=(fields.get("why_code", "").strip().upper() or None),
        sig_code=(fields.get("sig_code", "").strip().upper() or None),
        entry_price=_f("entry_price"),
        stop_price=_f("stop_price"),
        target_price=_f("target_price"),
        notes=fields.get("notes"),
    )


def load_p820_lookup() -> Dict[Tuple[str, date], P820Entry]:
    """Read all P_820 vault notes into a {(symbol, date): P820Entry} lookup.

    Returns an empty dict (not None) when the folder is absent or empty --
    callers look up against it unconditionally with no None-check.
    """
    folder = resolve_p820_folder()
    if folder is None:
        return {}

    lookup: Dict[Tuple[str, date], P820Entry] = {}
    count = 0
    for note in folder.glob("*.md"):
        try:
            text = note.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.warning(f"Could not read {note.name}: {e}")
            continue

        entry = _build_entry(_parse_frontmatter(text))
        if entry is None:
            continue
        lookup[(entry["symbol"], entry["signal_date"])] = entry
        count += 1

    logger.info(f"P_820 lookup: {count} entries from {folder}")
    return lookup
