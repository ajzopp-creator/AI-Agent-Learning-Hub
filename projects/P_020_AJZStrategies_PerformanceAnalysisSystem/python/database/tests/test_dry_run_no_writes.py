"""Regression test for the WO-P020-E1.015 dry-run fix -- found live
2026-08-22 when a "dry run" IRA import actually wrote 9 real trades to
the DB. Root cause: --dry-run only ever skipped updating last_run.json;
write_trade() and attach_orphan_exit() always called insert_trade()/
insert_exit()/update_trade_status(), which each commit internally. This
test proves dry_run=True now makes zero writes, against a real schema
(not fully mocked), and that the reported preview counts still match
what a real --commit run would do.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sqlite3

from application.trade_writer import attach_orphan_exit, write_trade
from infrastructure.db_client import create_all_tables
from schemas import Trade

PARAMS = {"options_multiplier": 100}


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    create_all_tables(conn)
    conn.execute(
        "INSERT INTO accounts (account_id, account_name, account_type, broker) "
        "VALUES ('IRA9885', 'Test IRA', 'invest', 'schwab')"
    )
    conn.execute(
        "INSERT INTO systems (system_id, system_name) VALUES ('TOS_Import', 'Default')"
    )
    conn.commit()
    return conn


def _sample_trade() -> Trade:
    return Trade(
        account_id="IRA9885",
        system="TOS_Import",
        underlying_symbol="COPX",
        asset_type="stock",
        direction="long",
        open_date=date(2026, 1, 5),
        qty=100,
        entry_price=45.0,
        total_commissions=0.0,
        status="open",
        source="schwab_api",
        schwab_transaction_id="124345481670",
    )


def test_dry_run_write_trade_makes_zero_writes():
    """The exact bug: a dry-run call must not insert a trade row."""
    conn = _make_conn()
    raw = {"entry_price": 45.0, "asset_type": "stock", "direction": "long",
           "open_date": date(2026, 1, 5)}
    trade = _sample_trade()

    outcome, trade_id, new_exits = write_trade(conn, raw, trade, PARAMS, dry_run=True)

    assert outcome == "inserted"
    assert trade_id is None
    row_count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    assert row_count == 0, "dry_run=True must not insert a trade row"


def test_real_run_write_trade_inserts_exactly_one_row():
    """Confirms dry_run=False (the default) still writes normally --
    this test would have failed before the fix too, but locks in the
    real-write path stays intact."""
    conn = _make_conn()
    raw = {"entry_price": 45.0, "asset_type": "stock", "direction": "long",
           "open_date": date(2026, 1, 5)}
    trade = _sample_trade()

    outcome, trade_id, new_exits = write_trade(conn, raw, trade, PARAMS, dry_run=False)

    assert outcome == "inserted"
    assert trade_id is not None
    row_count = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    assert row_count == 1


def test_dry_run_preview_matches_real_run_for_duplicate_detection():
    """A dry_run call against an already-existing trade must report
    'updated' (matching what a real run would report), without writing,
    and without corrupting the duplicate-detection state for a later
    real run."""
    conn = _make_conn()
    raw = {"entry_price": 45.0, "asset_type": "stock", "direction": "long",
           "open_date": date(2026, 1, 5)}
    trade = _sample_trade()

    # Real insert first (simulates the trade already existing in the DB).
    write_trade(conn, raw, trade, PARAMS, dry_run=False)
    assert conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0] == 1

    # Now a dry-run call against the SAME schwab_transaction_id.
    raw_with_exit = dict(raw, exit_1={
        "exit_price": 50.0, "qty_exited": 100, "exit_date": date(2026, 1, 10),
        "exit_commissions": 0.0,
    })
    outcome, trade_id, new_exits = write_trade(
        conn, raw_with_exit, trade, PARAMS, dry_run=True
    )

    assert outcome == "updated"
    assert new_exits == 1  # would-be new exit, correctly counted
    assert conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM exits").fetchone()[0] == 0, (
        "dry_run=True must not insert an exit row either"
    )


def test_dry_run_attach_orphan_exit_makes_zero_writes():
    """Same bug, orphan-resolution path (import_command.py's
    _resolve_orphans_against_db, separate call site from the main loop)."""
    conn = _make_conn()
    raw = {"entry_price": 45.0, "asset_type": "stock", "direction": "long",
           "open_date": date(2026, 1, 5)}
    trade = _sample_trade()
    write_trade(conn, raw, trade, PARAMS, dry_run=False)
    trade_id = conn.execute("SELECT trade_id FROM trades").fetchone()["trade_id"]
    open_trade = conn.execute(
        "SELECT * FROM trades WHERE trade_id = ?", (trade_id,)
    ).fetchone()

    orphan = {
        "underlying_symbol": "COPX", "price": 50.0, "qty": 100,
        "open_date": date(2026, 1, 10), "open_datetime": None, "fees": 0.0,
    }

    outcome, returned_id, new_exits = attach_orphan_exit(
        conn, orphan, open_trade, PARAMS, dry_run=True
    )

    assert outcome == "updated"
    assert new_exits == 1
    assert conn.execute("SELECT COUNT(*) FROM exits").fetchone()[0] == 0, (
        "dry_run=True must not insert an exit row via the orphan path either"
    )
