"""Tests for database.infrastructure.db_writer -- update_trade_status()
guarantees around total_commissions. Ref WO-P000-E10.001 Phase 1 (1.1).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sqlite3

from infrastructure.db_client import create_all_tables
from infrastructure.db_writer import update_trade_status


def _make_conn() -> sqlite3.Connection:
    """Build an in-memory DB with one account, one system, one open trade."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    create_all_tables(conn)
    conn.execute(
        "INSERT INTO accounts (account_id, account_name, account_type, broker) "
        "VALUES ('acct1', 'Test Account', 'live', 'schwab')"
    )
    conn.execute(
        "INSERT INTO systems (system_id, system_name) VALUES ('BT', 'Big Trends')"
    )
    conn.execute(
        "INSERT INTO trades (account_id, system, underlying_symbol, asset_type, "
        "direction, open_date, qty, entry_price, total_commissions) "
        "VALUES ('acct1', 'BT', 'AAPL', 'stock', 'long', '2026-08-01', 100, 50.0, 2.00)"
    )
    conn.commit()
    return conn


def test_commissions_supplied_by_caller_are_written():
    """A caller-supplied total_commissions value is written to the row."""
    conn = _make_conn()
    trade_id = conn.execute("SELECT trade_id FROM trades").fetchone()["trade_id"]

    update_trade_status(conn, trade_id, "closed", total_commissions=4.50)

    row = conn.execute(
        "SELECT status, total_commissions FROM trades WHERE trade_id = ?", (trade_id,)
    ).fetchone()
    assert row["status"] == "closed"
    assert row["total_commissions"] == 4.50


def test_commissions_omitted_leaves_prior_value_unchanged():
    """Omitting total_commissions (the None default) must not zero it out --
    both real callers (trade_writer.py) rely on this to avoid clobbering a
    value they intentionally didn't recompute this call.
    """
    conn = _make_conn()
    trade_id = conn.execute("SELECT trade_id FROM trades").fetchone()["trade_id"]

    update_trade_status(conn, trade_id, "partial")

    row = conn.execute(
        "SELECT status, total_commissions FROM trades WHERE trade_id = ?", (trade_id,)
    ).fetchone()
    assert row["status"] == "partial"
    assert row["total_commissions"] == 2.00


def test_updated_at_stays_naive_iso_format():
    """Fix for the deprecated datetime.utcnow() call (2026-08-04): the
    replacement must produce the exact same string shape as before --
    naive ISO 8601, 'T' separator, no timezone offset suffix -- so it stays
    consistent with existing rows and nothing downstream that reads this
    column has to change. A future edit re-introducing an offset (e.g. a
    bare datetime.now(timezone.utc).isoformat() without stripping tzinfo)
    would silently change the stored format -- this test catches that.
    """
    conn = _make_conn()
    trade_id = conn.execute("SELECT trade_id FROM trades").fetchone()["trade_id"]

    update_trade_status(conn, trade_id, "closed")

    row = conn.execute(
        "SELECT updated_at FROM trades WHERE trade_id = ?", (trade_id,)
    ).fetchone()
    updated_at = row["updated_at"]
    assert "T" in updated_at
    assert "+" not in updated_at
    assert "Z" not in updated_at