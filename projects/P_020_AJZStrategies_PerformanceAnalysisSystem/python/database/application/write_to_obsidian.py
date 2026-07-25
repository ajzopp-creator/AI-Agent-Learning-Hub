"""
write_to_obsidian.py -- Application layer (orchestration only).

Reads closed/partial trades from v_trade_summary, maps each to a
P020Record payload, writes to the Obsidian vault via the P_800 Hub
interface. Implements WO-P020-E1.005.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\write_to_obsidian.py

Usage:
    python write_to_obsidian.py            # dry run -- lists what would write
    python write_to_obsidian.py --commit   # actually writes to the vault
    python write_to_obsidian.py --all-history --commit
                                            # include pre-2026 frozen backlog

Scope: defaults to open_date >= config.VAULT_EXPORT_START_DATE (2026-01-01)
per Tony's standing rule that the pre-2026 backlog (324 rows) stays frozen
unless explicitly requested. Pass --all-history to override.

Note: the vault filename is YYYY-MM-DD_SYMBOL.md (close_date + symbol) --
built into P_800's filename_builder.py, not a choice made here. Two closed
trades on the same symbol closing the same day will overwrite each other
(last write wins, no error). Rare edge case, not handled by this script.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import VAULT_EXPORT_START_DATE  # noqa: E402
from infrastructure.db_client import get_connection  # noqa: E402
from infrastructure.vault_reader import get_closed_trades  # noqa: E402
from domain.vault_mapper import build_vault_payload  # noqa: E402

from shared_resources.python_utils.vault_interface import write_to_vault  # noqa: E402


def run(commit: bool, min_open_date: Optional[str]) -> Dict[str, int]:
    """Export closed/partial trades to the Obsidian vault.

    Args:
        commit: If False, only print what would be written. If True,
            actually call write_to_vault for each trade.
        min_open_date: 'YYYY-MM-DD' floor on open_date, or None for all
            history (including the frozen pre-2026 backlog).

    Returns:
        Dict with counts: total, written, skipped, errors.
    """
    stats = {"total": 0, "written": 0, "skipped": 0, "errors": 0}
    conn = get_connection()
    try:
        rows = get_closed_trades(conn, min_open_date=min_open_date)
    finally:
        conn.close()

    stats["total"] = len(rows)
    scope = f"open_date >= {min_open_date}" if min_open_date else "all history"
    print(f"Found {len(rows)} closed/partial trades ({scope}).")

    for row in rows:
        try:
            payload = build_vault_payload(row)
        except ValueError as exc:
            print(f"  SKIP trade_id={row.get('trade_id')} -- {exc}")
            stats["skipped"] += 1
            continue

        label = f"{payload['close_date']}_{payload['symbol']}"
        if not commit:
            print(f"  [DRY RUN] would write: {label} "
                  f"(system={payload['system']}, outcome={payload['outcome']})")
            continue

        try:
            written = write_to_vault("P020", payload, overwrite=True)
            if written:
                print(f"  OK: {label}")
                stats["written"] += 1
            else:
                print(f"  SKIPPED (vault declined): {label}")
                stats["skipped"] += 1
        except (ValueError, OSError) as exc:
            print(f"  ERROR: {label} -- {exc}")
            stats["errors"] += 1

    return stats


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Export closed P_020 trades to the Obsidian vault."
    )
    parser.add_argument(
        "--commit", action="store_true",
        help="Actually write to the vault. Without this flag, dry-run only.",
    )
    parser.add_argument(
        "--all-history", action="store_true",
        help="Include the frozen pre-2026 backlog. Default excludes it.",
    )
    args = parser.parse_args()

    min_open_date = None if args.all_history else VAULT_EXPORT_START_DATE
    stats = run(commit=args.commit, min_open_date=min_open_date)

    print("\n--- Summary ---")
    print(f"Total:   {stats['total']}")
    print(f"Written: {stats['written']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors:  {stats['errors']}")
    if not args.commit:
        print("(dry run -- add --commit to write for real)")


if __name__ == "__main__":
    main()
