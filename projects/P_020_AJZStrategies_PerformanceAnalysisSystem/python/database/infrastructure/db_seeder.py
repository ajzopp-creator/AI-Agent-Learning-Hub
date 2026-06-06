"""Seed data loader for accounts and systems reference tables."""

import logging
import sqlite3
from typing import List, Tuple

logger = logging.getLogger(__name__)

# ── Account seed data ──────────────────────────────────────────────────────
# Format: (account_id, account_name, account_type, broker, distribution_years)

_ACCOUNTS: List[Tuple] = [
    ("AJZ6348", "AJZ Strategies LLC", "live",   "schwab", None),
    ("IRA9885", "AJZ Strategies IRA", "invest", "schwab", 10),
    ("PAPER",   "Paper Account",      "paper",  "schwab", None),
]

# ── System seed data ───────────────────────────────────────────────────────
# Format: (system_id, system_name, description, active)

_SYSTEMS: List[Tuple] = [
    ("P_115",      "Buy The Dip",
     "Buy The Dip entries",                           1),
    ("P_116",      "Options Income Launchpad",
     "Options income generation system",              1),
    ("P_117",      "External Recommendations",
     "External signal recommendations",               1),
    ("P_118",      "Eddie Z Breakouts",
     "Eddie Z breakout pattern system",               1),
    ("P_300",      "VantagePoint Pattern Recognition",
     "VantagePoint software signals",                 1),
    ("P_910",      "P_910 System",
     "Additional trading system",                     1),
    ("P_920",      "P_920 System",
     "Additional trading system",                     1),
    ("Day",        "Day Trading",
     "Intraday trades",                               1),
    ("SNT",        "Sunday Night Trader",
     "BigTrends email subscription - Sunday Night Trader",  1),
    ("TOS_Import", "TOS Import Default",
     "Default when no Tracker Dashboard match found", 1),
]


def seed_accounts(conn: sqlite3.Connection) -> None:
    """Insert account seed rows — skips any that already exist.

    Args:
        conn: Active SQLite connection.
    """
    conn.executemany("""
        INSERT OR IGNORE INTO accounts
            (account_id, account_name, account_type, broker, distribution_years)
        VALUES (?, ?, ?, ?, ?)
    """, _ACCOUNTS)
    conn.commit()
    logger.info(f"Accounts seeded: {len(_ACCOUNTS)} rows (duplicates skipped).")


def seed_systems(conn: sqlite3.Connection) -> None:
    """Insert trading system seed rows — skips any that already exist.

    Args:
        conn: Active SQLite connection.
    """
    conn.executemany("""
        INSERT OR IGNORE INTO systems
            (system_id, system_name, description, active)
        VALUES (?, ?, ?, ?)
    """, _SYSTEMS)
    conn.commit()
    logger.info(f"Systems seeded: {len(_SYSTEMS)} rows (duplicates skipped).")


def seed_all(conn: sqlite3.Connection) -> None:
    """Run all seed operations in dependency order.

    Args:
        conn: Active SQLite connection.
    """
    seed_accounts(conn)
    seed_systems(conn)
    logger.info("All seed data loaded.")
