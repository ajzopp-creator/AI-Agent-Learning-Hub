"""
P_010 Market Health -- infrastructure/trade_reader.py

Reads closed P_115/P_118 trades from the P_020 SQLite database.
Read-only. No writes to P_020.
"""
import logging
import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional

from market_health.config import BUCKET_SYSTEMS, P_020_DB_PATH
from market_health.schemas import TradeRecord

log = logging.getLogger(__name__)


def read_closed_trades(db_path: Path = P_020_DB_PATH) -> list[TradeRecord]:
    """
    Load all closed trades for BUCKET_SYSTEMS from P_020 database.
    Returns list sorted ascending by open_date.
    """
    if not db_path.exists():
        raise FileNotFoundError(f'P_020 database not found: {db_path}')

    systems_placeholder = ','.join('?' for _ in BUCKET_SYSTEMS)
    sql = f'''
        SELECT
            t.trade_id,
            t.system,
            t.underlying_symbol,
            t.open_date,
            e.exit_date,
            e.exit_pnl,
            t.risk_amount
        FROM trades t
        LEFT JOIN (
            SELECT trade_id,
                   MAX(exit_date) AS exit_date,
                   SUM(exit_pnl)  AS exit_pnl
            FROM exits
            GROUP BY trade_id
        ) e ON t.trade_id = e.trade_id
        WHERE t.status = 'closed'
          AND t.system IN ({systems_placeholder})
        ORDER BY t.open_date ASC
    '''

    records: list[TradeRecord] = []
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute(sql, BUCKET_SYSTEMS)
        for row in cur.fetchall():
            records.append(_row_to_record(row))
        conn.close()
    except sqlite3.Error as exc:
        log.error('SQLite error reading P_020 trades: %s', exc)
        raise

    log.info('Loaded %d closed trades from P_020', len(records))
    return records


def _row_to_record(row: tuple) -> TradeRecord:
    """Map a raw SQLite row to a TradeRecord."""
    trade_id, system, symbol, open_date, exit_date, exit_pnl, risk_amount = row
    return TradeRecord(
        trade_id=trade_id,
        system=system,
        underlying_symbol=symbol,
        open_date=_parse_date(open_date),
        exit_date=_parse_date(exit_date),
        exit_pnl=float(exit_pnl) if exit_pnl is not None else None,
        risk_amount=float(risk_amount) if risk_amount is not None else None,
    )


def _parse_date(value: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD string to date; returns None if blank."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None