"""p400_regenerate/domain/note_merger.py -- merge a P_020 reconciled
order's outcome into an existing P_400 vault note's field dict.

Pure logic, no I/O. Takes what vault_note_scanner.py read (a flat
string-valued dict, straight from frontmatter) and what p020_reader.py
read (already-typed date/float values from SQLite), returns a new dict
ready for write_to_vault("P400", ...) -- signal_date/ticker/every other
untouched field preserved so the overwrite lands on the same note file.

Part of: P_800 Automation Note-Taking -- p400_regenerate sub-project
Layer:   domain (pure logic)
"""
from __future__ import annotations

from typing import Any, Dict

# P_800-internal bookkeeping keys: auto-injected/auto-managed by
# write_handler/vault_writer on every write (WO-P800-E2.005 design --
# see vault_schemas.py's P400Record docstring). The scanned note's
# frontmatter DOES contain these (they were written to disk even though
# the original caller's payload never supplied them), so they must be
# stripped before re-submitting, or we'd be feeding P_800's own injected
# values back in as if they were caller-supplied.
_STRIP_KEYS = ("note_version", "write_route", "write_route_history", "source")

# vault_note_scanner.py's own bookkeeping keys, not real frontmatter fields.
_SCANNER_KEYS = ("_note_path", "_schema")


def merge_reconciled_order(
    existing_fields: Dict[str, str], order: Dict[str, Any]
) -> Dict[str, Any]:
    """Build a write_to_vault() payload: existing note + reconciled outcome.

    Args:
        existing_fields: Full frontmatter dict from
            vault_note_scanner.find_note_by_order_id() (string values,
            plus its own _note_path/_schema bookkeeping keys).
        order: One row dict from p020_reader.get_closed_p400_orders() --
            entry_date/close_date are date objects, realized_pnl a float.

    Returns:
        A new dict with every real frontmatter field from existing_fields
        preserved, plus lifecycle_status/entry_date/close_date/
        realized_pnl overridden with the reconciled outcome.
    """
    merged = {
        k: v for k, v in existing_fields.items()
        if k not in _STRIP_KEYS and k not in _SCANNER_KEYS
    }

    merged["lifecycle_status"] = "CLOSED"
    merged["entry_date"] = str(order["entry_date"]) if order.get("entry_date") else None
    merged["close_date"] = str(order["close_date"]) if order.get("close_date") else None
    merged["realized_pnl"] = order.get("realized_pnl")

    return merged
