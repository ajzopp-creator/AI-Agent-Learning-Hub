"""p400_regenerate/application/regenerate_command.py -- sync P_020's
reconciled outcomes into P_400's existing vault notes.

Orchestration only: for each closed P_400-sourced order in P_020, find
the matching vault note by order_id, skip if already synced (note's own
lifecycle_status is already CLOSED), otherwise merge in the reconciled
outcome and re-write via write_to_vault() -- P_800's public API, the
only way any project is allowed to write vault content.

Part of: P_800 Automation Note-Taking -- p400_regenerate sub-project
Layer:   application (orchestration)
"""
from __future__ import annotations

import logging
from typing import Dict

from p400_regenerate.domain.note_merger import merge_reconciled_order
from p400_regenerate.infrastructure.p020_reader import get_closed_p400_orders
from p400_regenerate.infrastructure.vault_note_scanner import find_note_by_order_id
from shared_resources.python_utils.vault_interface import write_to_vault

logger = logging.getLogger("p800.p400_regenerate")


def run_regenerate() -> Dict[str, int]:
    """Sync every closed P_400-sourced P_020 order into its vault note.

    Returns:
        Dict with counts: {"synced": N, "already_synced": N,
        "no_note_found": N}.
    """
    orders = get_closed_p400_orders()
    counts = {"synced": 0, "already_synced": 0, "no_note_found": 0}

    for order in orders:
        schwab_order_id = order.get("schwab_order_id")
        existing = find_note_by_order_id(schwab_order_id)
        if existing is None:
            logger.warning(f"No vault note found for order_id={schwab_order_id}")
            counts["no_note_found"] += 1
            continue

        if existing.get("lifecycle_status", "").strip().upper() == "CLOSED":
            counts["already_synced"] += 1
            continue

        merged = merge_reconciled_order(existing, order)
        schema = existing.get("_schema", "P400")
        try:
            write_to_vault(schema, merged)
            counts["synced"] += 1
        except Exception as e:
            logger.warning(
                f"Vault regenerate write failed for order_id="
                f"{schwab_order_id}: {e}"
            )

    logger.info(
        f"Regenerate done: {counts['synced']} synced, "
        f"{counts['already_synced']} already synced, "
        f"{counts['no_note_found']} no note found."
    )
    return counts
