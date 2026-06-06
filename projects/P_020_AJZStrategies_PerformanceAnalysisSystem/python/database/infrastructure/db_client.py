"""SQLite connection management and schema creation for P_020."""

import logging
import sqlite3

from config import DATABASE_DIR, DATABASE_FILE

logger = logging.getLogger(__name__)

# ── v_trade_summary view SQL ───────────────────────────────────────────────
_V_TRADE_SUMMARY_SQL = """
CREATE VIEW IF NOT EXISTS v_trade_summary AS
SELECT
    t.trade_id,
    t.account_id,
    t.system,
    t.underlying_symbol,
    t.asset_type,
    t.direction,
    t.open_date,
    t.qty,
    t.entry_price,
    t.stop_price,
    t.risk_amount,
    t.total_commissions,
    t.status,
    t.tags,
    t.notes,
    t.source,

    COALESCE(SUM(e.exit_pnl),   0.0) AS realized_pnl,
    COALESCE(SUM(e.qty_exited), 0)   AS qty_closed,
    t.qty - COALESCE(SUM(e.qty_exited), 0) AS qty_remaining,
    MAX(e.exit_date)                 AS last_exit_date,
    MAX(e.hold_days)                 AS max_hold_days,

    MAX(CASE WHEN e.exit_number = 1 THEN e.exit_price  END) AS exit_1_price,
    MAX(CASE WHEN e.exit_number = 1 THEN e.qty_exited  END) AS exit_1_qty,
    MAX(CASE WHEN e.exit_number = 1 THEN e.exit_date   END) AS exit_1_date,
    MAX(CASE WHEN e.exit_number = 1 THEN e.hold_days   END) AS exit_1_hold_days,
    MAX(CASE WHEN e.exit_number = 2 THEN e.exit_price  END) AS exit_2_price,
    MAX(CASE WHEN e.exit_number = 2 THEN e.qty_exited  END) AS exit_2_qty,
    MAX(CASE WHEN e.exit_number = 2 THEN e.exit_date   END) AS exit_2_date,
    MAX(CASE WHEN e.exit_number = 2 THEN e.hold_days   END) AS exit_2_hold_days,
    MAX(CASE WHEN e.exit_number = 3 THEN e.exit_price  END) AS exit_3_price,
    MAX(CASE WHEN e.exit_number = 3 THEN e.qty_exited  END) AS exit_3_qty,
    MAX(CASE WHEN e.exit_number = 3 THEN e.exit_date   END) AS exit_3_date,
    MAX(CASE WHEN e.exit_number = 3 THEN e.hold_days   END) AS exit_3_hold_days,

    CASE
        WHEN t.risk_amount IS NOT NULL AND t.risk_amount != 0
        THEN ROUND(COALESCE(SUM(e.exit_pnl), 0.0) / t.risk_amount, 2)
        ELSE NULL
    END AS realized_R,

    CASE
        WHEN t.status = 'open'                   THEN 'OPEN'
        WHEN COALESCE(SUM(e.exit_pnl), 0.0) > 0 THEN 'WIN'
        WHEN COALESCE(SUM(e.exit_pnl), 0.0) < 0 THEN 'LOSS'
        ELSE 'SCRATCH'
    END AS outcome

FROM trades t
LEFT JOIN exits e ON t.trade_id = e.trade_id
GROUP BY t.trade_id
"""


# ── Connection ─────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Open and return a SQLite connection with foreign keys enabled.

    Returns:
        sqlite3.Connection: Active database connection.
    """
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_FILE))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    logger.debug(f"Connected to: {DATABASE_FILE}")
    return conn


# ── Table creation ─────────────────────────────────────────────────────────

def _create_accounts_table(conn: sqlite3.Connection) -> None:
    """Create the accounts reference table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            account_id         TEXT     PRIMARY KEY,
            account_name       TEXT     NOT NULL,
            account_type       TEXT     NOT NULL
                                        CHECK(account_type IN ('live','invest','paper')),
            broker             TEXT     NOT NULL,
            distribution_years INTEGER,
            created_at         DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _create_systems_table(conn: sqlite3.Connection) -> None:
    """Create the trading systems reference table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS systems (
            system_id   TEXT    PRIMARY KEY,
            system_name TEXT    NOT NULL,
            description TEXT,
            active      INTEGER NOT NULL DEFAULT 1
        )
    """)


def _create_trades_table(conn: sqlite3.Connection) -> None:
    """Create the trades primary entity table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            trade_id               INTEGER  PRIMARY KEY AUTOINCREMENT,
            account_id             TEXT     NOT NULL REFERENCES accounts(account_id),
            system                 TEXT     NOT NULL REFERENCES systems(system_id),
            underlying_symbol      TEXT     NOT NULL,
            asset_type             TEXT     NOT NULL
                                            CHECK(asset_type IN
                                                  ('stock','etf','call','put','spread')),
            direction              TEXT     NOT NULL
                                            CHECK(direction IN ('long','short')),
            open_date              DATE     NOT NULL,
            open_datetime          DATETIME,
            qty                    REAL     NOT NULL,
            entry_price            REAL     NOT NULL,
            stop_price             REAL,
            risk_amount            REAL,
            total_commissions      REAL     NOT NULL DEFAULT 0.0,
            status                 TEXT     NOT NULL DEFAULT 'open'
                                            CHECK(status IN ('open','partial','closed')),
            tags                   TEXT,
            notes                  TEXT,
            source                 TEXT     NOT NULL DEFAULT 'schwab_api',
            schwab_transaction_id  TEXT     UNIQUE,
            created_at             DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at             DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _create_exits_table(conn: sqlite3.Connection) -> None:
    """Create the exits normalized child table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS exits (
            exit_id          INTEGER  PRIMARY KEY AUTOINCREMENT,
            trade_id         INTEGER  NOT NULL REFERENCES trades(trade_id),
            exit_number      INTEGER  NOT NULL CHECK(exit_number >= 1),
            exit_date        DATE     NOT NULL,
            exit_datetime    DATETIME,
            qty_exited       REAL     NOT NULL,
            exit_price       REAL     NOT NULL,
            exit_commissions REAL     NOT NULL DEFAULT 0.0,
            exit_pnl         REAL     NOT NULL,
            hold_days        INTEGER  NOT NULL,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(trade_id, exit_number)
        )
    """)


# ── Orchestration ──────────────────────────────────────────────────────────


def _create_account_balances_table(conn) -> None:
    """Create the account_balances snapshot table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS account_balances (
            balance_id       INTEGER  PRIMARY KEY AUTOINCREMENT,
            account_id       TEXT     NOT NULL REFERENCES accounts(account_id),
            snapshot_date    DATE     NOT NULL,
            total_value      REAL     NOT NULL,
            cash_available   REAL,
            buying_power     REAL,
            day_pnl          REAL,
            start_of_day_value REAL,
            source           TEXT     NOT NULL DEFAULT 'schwab_api',
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(account_id, snapshot_date)
        )
    """)


def create_all_tables(conn: sqlite3.Connection) -> None:
    """Create all tables in foreign-key dependency order.

    Args:
        conn: Active SQLite connection.
    """
    _create_accounts_table(conn)
    _create_systems_table(conn)
    _create_trades_table(conn)
    _create_exits_table(conn)
    _create_account_balances_table(conn)
    conn.commit()
    logger.info("All tables created.")


def create_views(conn: sqlite3.Connection) -> None:
    """Create the v_trade_summary view.

    Args:
        conn: Active SQLite connection.
    """
    conn.execute(_V_TRADE_SUMMARY_SQL)
    conn.commit()
    logger.info("v_trade_summary view created.")


def initialize_database() -> sqlite3.Connection:
    """Create DB file, all tables, and all views. Safe to re-run.

    Returns:
        sqlite3.Connection: Open connection to the initialized database.
    """
    conn = get_connection()
    create_all_tables(conn)
    create_views(conn)
    logger.info(f"Database initialized: {DATABASE_FILE}")
    return conn
