"""
FILE: db_connect.py
VERSION: 1.0
DATE: 2026-05-14
AUTHOR: Anthony Zoppi + Claude
LAYER: utility
DESCRIPTION:
    SQLite connection factory for the P_300 catalog. Sets PRAGMA
    foreign_keys = ON immediately on every connection (per M-012) so FK
    constraints are enforced — the structural protection against EC-027-class
    hollow rows. Resolves the active catalog path via
    db_utils.get_latest_catalog() unless an explicit path is supplied.

    Two callable forms:
      - get_connection(catalog_path=None) -> sqlite3.Connection
            Caller is responsible for commit/rollback/close.
      - connection_context(catalog_path=None) -> context manager
            Auto-commits on clean exit, rolls back on exception, always closes.

    No business logic. No domain decisions. Pure infrastructure helper.
CHANGELOG:
    - 2026-05-14 v1.0: Initial connection factory. Enforces M-012 (PRAGMA
      foreign_keys = ON on every connection). Single choke point for all
      catalog access; no direct sqlite3.connect() calls permitted elsewhere.
"""

import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Bootstrap sys.path: add python/ so `from utilities.db_utils` resolves whether
# this module is invoked standalone or imported from cli.py / infrastructure/.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utilities.db_utils import get_latest_catalog  # noqa: E402

# Pragmas applied to every connection in order. Adding journal_mode=WAL or
# similar is a Stage 4+ decision; keep minimal for now.
DEFAULT_PRAGMAS = (
    "PRAGMA foreign_keys = ON;",
)


def get_connection(catalog_path: Optional[str] = None) -> sqlite3.Connection:
    """Open a sqlite3 connection with all required PRAGMAs applied.

    Args:
        catalog_path: Optional explicit path to a catalog file. If None,
            resolves the active catalog via db_utils.get_latest_catalog().

    Returns:
        sqlite3.Connection ready for use. Caller owns lifecycle: must
        commit/rollback and close. Prefer connection_context() if you don't
        need manual control.
    """
    if catalog_path is None:
        catalog_path = get_latest_catalog()
    conn = sqlite3.connect(catalog_path)
    for pragma in DEFAULT_PRAGMAS:
        conn.execute(pragma)
    return conn


@contextmanager
def connection_context(catalog_path: Optional[str] = None):
    """Context-manager form of get_connection(). Auto-commits on clean exit,
    rolls back on exception, always closes.

    Usage:
        with connection_context() as conn:
            conn.execute("INSERT INTO ...", (...))
    """
    conn = get_connection(catalog_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    # Smoke test: open the active catalog, confirm PRAGMA fires, read the
    # bootstrap feature_set row that stage_3c inserted.
    with connection_context() as conn:
        fk = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
        catalog_row = conn.execute(
            "SELECT feature_version FROM feature_sets LIMIT 1;"
        ).fetchone()
    feature = catalog_row[0] if catalog_row else "<empty>"
    print(f"Connection OK. foreign_keys = {fk}, feature_sets row = {feature}")
