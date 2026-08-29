"""thinklog_backfill.py -- Application layer.

Standalone command to retroactively apply ThinkLog tag overrides to
trades already in the DB. Companion to the live weekly ingest hook
(application/ingest_pipeline.py, which handles new trades only) --
this covers everything already sitting in the database, filtered by
date range and/or symbol so a run only ever touches what you point it at.

Reuses infrastructure/db_reader.get_trades_by_date_range() unchanged,
and the same domain/thinklog_override.get_override() the live hook
uses -- one override rule, two entry points.

Dry-run by default (Hub-wide rule: dry-run before any DB write, always).
UPDATEs only rows where the tag actually changes something.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\thinklog_backfill.py

Usage:
    python P_020_Trade_Manager.py thinklog --thinklog PATH \\
        --start YYYY-MM-DD --end YYYY-MM-DD [--symbols SYM,SYM] \\
        [--account AJZ6348] [--commit]

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from config import THINKLOG_MATCH_FORWARD_DAYS
from domain.thinklog_override import get_override
from infrastructure.db_client import get_connection
from infrastructure.db_reader import get_trades_by_date_range
from application.live_thinklog import load_live_thinklog_lookup

logger = logging.getLogger(__name__)


def _row_to_dict(row) -> Dict:
    """sqlite3.Row -> plain dict (get_override() needs .get(), Row has none)."""
    return dict(zip(row.keys(), row))


def find_backfill_candidates(
    conn,
    thinklog_lookup: Dict,
    date_from: str,
    date_to: str,
    account_id: Optional[str] = None,
    symbols: Optional[List[str]] = None,
) -> List[Dict]:
    """Find existing trades with a ThinkLog override available, unapplied.

    Args:
        conn: Active SQLite connection.
        thinklog_lookup: Lookup from load_live_thinklog_lookup().
        date_from: Start date 'YYYY-MM-DD', inclusive.
        date_to: End date 'YYYY-MM-DD', inclusive.
        account_id: Optional account filter, passed to db_reader unchanged.
        symbols: Optional symbol allow-list, filtered in Python (no SQL
                change needed in db_reader for this narrow case).

    Returns:
        List of dicts, one per matched trade:
        {trade_id, symbol, open_date, old_system, new_system, reason,
         signal_strength, tag_date, gap_days}. Trades where the tag
        resolves to the SAME system already stored are excluded --
        nothing to write.
    """
    rows = get_trades_by_date_range(conn, date_from, date_to, account_id)
    symbol_filter = {s.strip().upper() for s in symbols} if symbols else None

    candidates = []
    for row in rows:
        trade = _row_to_dict(row)
        symbol = trade["underlying_symbol"]
        if symbol_filter and symbol not in symbol_filter:
            continue

        override = get_override(
            symbol, trade["open_date"], thinklog_lookup, trade["system"],
            forward_days=THINKLOG_MATCH_FORWARD_DAYS,
        )
        if override is None or override.system == trade["system"]:
            continue

        candidates.append({
            "trade_id": trade["trade_id"],
            "symbol": symbol,
            "open_date": trade["open_date"],
            "old_system": trade["system"],
            "new_system": override.system,
            "reason": override.reason,
            "signal_strength": override.signal_strength,
            "tag_date": override.tag_date,
            "gap_days": override.gap_days,
        })
    return candidates


def print_preview(candidates: List[Dict]) -> None:
    """Print a preview table of pending backfill changes."""
    if not candidates:
        print("No trades match a ThinkLog tag in this range/symbol set.")
        return
    print(f"\n{'Trade':<8} {'Date':<11} {'Symbol':<8} {'Old':<10} {'New':<10} {'Reason':<8} {'Sig':<4} Tag")
    print("-" * 85)
    for c in candidates:
        gap = f" (-{c['gap_days']}d)" if c["gap_days"] else ""
        print(
            f"{c['trade_id']:<8} {c['open_date']:<11} {c['symbol']:<8} "
            f"{c['old_system']:<10} {c['new_system']:<10} "
            f"{(c['reason'] or '-'):<8} {(c['signal_strength'] or '-'):<4} "
            f"{c['tag_date']}{gap}"
        )
    print(f"\n{len(candidates)} trade(s) would be updated.")


def apply_backfill(conn, candidates: List[Dict]) -> int:
    """Write the backfill UPDATEs. Caller is responsible for the dry-run gate.

    Args:
        conn: Active SQLite connection.
        candidates: Output of find_backfill_candidates().

    Returns:
        Number of rows actually updated.
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
    for c in candidates:
        conn.execute(
            "UPDATE trades SET system=?, reason=?, signal_strength=?, "
            "updated_at=? WHERE trade_id=?",
            (c["new_system"], c["reason"], c["signal_strength"], now, c["trade_id"]),
        )
    conn.commit()
    logger.info(f"ThinkLog backfill: {len(candidates)} trade(s) updated.")
    return len(candidates)


def run_backfill(
    thinklog_path: str,
    date_from: str,
    date_to: str,
    account_id: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    commit: bool = False,
) -> int:
    """Entry point called by P_020_Trade_Manager.py's `thinklog` subcommand.

    Returns:
        Number of trades updated (0 on dry-run, always).
    """
    thinklog_lookup = load_live_thinklog_lookup(thinklog_path)
    if not thinklog_lookup:
        print(f"No usable ThinkLog data at: {thinklog_path}")
        return 0

    conn = get_connection()
    try:
        candidates = find_backfill_candidates(
            conn, thinklog_lookup, date_from, date_to, account_id, symbols,
        )
        print_preview(candidates)
        if not commit or not candidates:
            print("\nDry run — no DB writes. Add --commit to write.")
            return 0
        return apply_backfill(conn, candidates)
    finally:
        conn.close()
