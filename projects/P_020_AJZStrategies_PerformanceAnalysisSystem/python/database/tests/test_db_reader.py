"""Tests for database.infrastructure.db_reader -- get_all_trades()
system filter guarantee. Ref WO-P000-E10.001 Phase 3 (3.4).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sqlite3

from infrastructure.db_client import create_all_tables
from infrastructure.db_reader import get_all_trades


def _make_conn() -> sqlite3.Connection:
    """Build an in-memory DB with two trades on different systems."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    create_all_tables(conn)
    conn.execute(
        "INSERT INTO accounts (account_id, account_name, account_type, broker) "
        "VALUES ('acct1', 'Test Account', 'live', 'schwab')"
    )
    conn.execute("INSERT INTO systems (system_id, system_name) VALUES ('BT', 'Big Trends')")
    conn.execute("INSERT INTO systems (system_id, system_name) VALUES ('SNT', 'Sunday Night Trader')")
    conn.execute(
        "INSERT INTO trades (account_id, system, underlying_symbol, asset_type, "
        "direction, open_date, qty, entry_price) "
        "VALUES ('acct1', 'BT', 'AAPL', 'stock', 'long', '2026-08-01', 100, 50.0)"
    )
    conn.execute(
        "INSERT INTO trades (account_id, system, underlying_symbol, asset_type, "
        "direction, open_date, qty, entry_price) "
        "VALUES ('acct1', 'SNT', 'MSFT', 'stock', 'long', '2026-08-02', 50, 300.0)"
    )
    conn.commit()
    return conn


def test_system_none_returns_all_systems():
    """No caller currently passes system= -- confirming the None default
    (WO-P000-E10.001 item 3.4: correct default, not a caller-propagation
    gap) returns every system's trades, not an accidental filter."""
    conn = _make_conn()
    rows = get_all_trades(conn)
    assert len(rows) == 2


def test_system_filter_works_when_supplied():
    """The filter is functional when a caller does supply it -- confirms
    the parameter isn't dead code, just currently unused."""
    conn = _make_conn()
    rows = get_all_trades(conn, system="BT")
    assert len(rows) == 1
    assert rows[0]["underlying_symbol"] == "AAPL"