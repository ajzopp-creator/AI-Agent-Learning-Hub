"""CSV exporter — exports v_trade_summary to CSV files for Excel Power Query."""

import csv
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional

from config import (
    AI_REVIEW_DIR,
    EXPORTS_DIR,
    OPTIONS_EXPORT_FILE,
    STOCKS_EXPORT_FILE,
)

logger = logging.getLogger(__name__)

# v_trade_summary column names — used as fallback headers when DB has no trades yet
_SUMMARY_HEADERS = [
    "trade_id", "account_id", "system", "underlying_symbol", "asset_type",
    "direction", "open_date", "qty", "entry_price", "stop_price", "risk_amount",
    "total_commissions", "status", "tags", "notes", "source",
    "realized_pnl", "qty_closed", "qty_remaining", "last_exit_date", "max_hold_days",
    "exit_1_price", "exit_1_qty", "exit_1_date", "exit_1_hold_days",
    "exit_2_price", "exit_2_qty", "exit_2_date", "exit_2_hold_days",
    "exit_3_price", "exit_3_qty", "exit_3_date", "exit_3_hold_days",
    "realized_R", "outcome",
]


# ── Helpers ────────────────────────────────────────────────────────────────

def _rows_to_csv(
    rows: List[sqlite3.Row],
    output_path: Path,
    fallback_headers: Optional[List[str]] = None,
) -> int:
    """Write sqlite3.Row results to a CSV file.

    Always writes the file — even when rows is empty — so Power Query
    connections remain valid before trade data is ingested.

    Args:
        rows: List of sqlite3.Row objects from a query.
        output_path: Full path to write the CSV file.
        fallback_headers: Column names to write when rows is empty.

    Returns:
        Number of data rows written (excluding header).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if rows:
            writer.writerow(rows[0].keys())
            writer.writerows([tuple(r) for r in rows])
            logger.info(f"Exported {len(rows)} rows → {output_path.name}")
        elif fallback_headers:
            writer.writerow(fallback_headers)
            logger.info(f"No data — header-only CSV written → {output_path.name}")
        else:
            logger.warning(f"No rows and no fallback headers → {output_path.name} empty.")

    return len(rows)


# ── Main exports (Power Query sources) ────────────────────────────────────

def export_options(conn: sqlite3.Connection, account_id: Optional[str] = None) -> int:
    """Export options trades from v_trade_summary to CSV for Excel Power Query.

    Args:
        conn: Active SQLite connection.
        account_id: Optional account filter. Defaults to live account only.

    Returns:
        Number of rows exported.
    """
    sql    = """
        SELECT * FROM v_trade_summary
         WHERE asset_type IN ('call', 'put', 'spread')
    """
    params = []

    if account_id:
        sql += " AND account_id = ?"
        params.append(account_id)
    else:
        sql += (
            " AND account_id NOT IN "
            "(SELECT account_id FROM accounts WHERE account_type = 'invest')"
        )

    sql += " ORDER BY open_date DESC"
    rows = conn.execute(sql, params).fetchall()
    return _rows_to_csv(rows, OPTIONS_EXPORT_FILE, _SUMMARY_HEADERS)


def export_stocks(conn: sqlite3.Connection, account_id: Optional[str] = None) -> int:
    """Export stock/ETF trades from v_trade_summary to CSV for Excel Power Query.

    Args:
        conn: Active SQLite connection.
        account_id: Optional account filter. Defaults to live account only.

    Returns:
        Number of rows exported.
    """
    sql    = """
        SELECT * FROM v_trade_summary
         WHERE asset_type IN ('stock', 'etf')
    """
    params = []

    if account_id:
        sql += " AND account_id = ?"
        params.append(account_id)
    else:
        sql += (
            " AND account_id NOT IN "
            "(SELECT account_id FROM accounts WHERE account_type = 'invest')"
        )

    sql += " ORDER BY open_date DESC"
    rows = conn.execute(sql, params).fetchall()
    return _rows_to_csv(rows, STOCKS_EXPORT_FILE, _SUMMARY_HEADERS)


# ── AI review exports ──────────────────────────────────────────────────────

def export_open_positions(conn: sqlite3.Connection) -> int:
    """Export all open/partial trades to ai_review/open_positions.csv.

    Args:
        conn: Active SQLite connection.

    Returns:
        Number of rows exported.
    """
    rows = conn.execute("""
        SELECT * FROM v_trade_summary
         WHERE status IN ('open', 'partial')
         ORDER BY open_date
    """).fetchall()
    path = AI_REVIEW_DIR / "open_positions.csv"
    return _rows_to_csv(rows, path, _SUMMARY_HEADERS)


def export_all(conn: sqlite3.Connection, account_id: Optional[str] = None) -> None:
    """Run all standard exports — options, stocks, and open positions.

    Args:
        conn: Active SQLite connection.
        account_id: Optional account filter passed to options + stocks exports.
    """
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    AI_REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    options_count = export_options(conn, account_id)
    stocks_count  = export_stocks(conn, account_id)
    open_count    = export_open_positions(conn)

    logger.info(
        f"Export complete — options: {options_count} rows, "
        f"stocks: {stocks_count} rows, open positions: {open_count} rows."
    )
