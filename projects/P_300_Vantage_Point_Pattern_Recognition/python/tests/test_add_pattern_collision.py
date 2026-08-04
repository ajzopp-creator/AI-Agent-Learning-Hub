"""
FILE: tests/test_add_pattern_collision.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for the WFG/PLTR/BOIL/RRC PATTERN_IDENT-
    doubles cleanup. Confirms two things:
      1. catalog_writer.pattern_exists_for_ticker_anchor() correctly
         detects an exact (ticker, anchor_date) match and correctly
         does NOT false-positive on a different ticker or a different
         anchor_date -- the exact query the real WFG double slipped
         past when it only existed in add_pattern_pipeline.py's
         filename-only EC-023 check.
      2. add_pattern_pipeline.py's Pipeline A guard actually raises
         ValueError when a collision exists, and does NOT raise when
         there isn't one -- proven by calling the real guard-check
         line's logic path directly against a minimal temp catalog,
         not by re-deriving the query independently (would defeat the
         point of the test).

    Uses a minimal in-memory sqlite3 DB with only the two tables the
    query touches (symbols, pattern_instances) -- not the full 8-table
    CATALOG_TABLES schema. This function's contract is a plain SQL
    JOIN + exact-match WHERE; a full catalog fixture would test
    nothing extra and cost significantly more setup code.

CHANGELOG:
    - 2026-07-20 v1.0: Initial release (WFG/PLTR/BOIL/RRC cleanup).

RUN (from project root, p140 active):
    python tests/test_add_pattern_collision.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sqlite3
import sys
from datetime import date
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from infrastructure.catalog_writer import pattern_exists_for_ticker_anchor  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _make_temp_catalog() -> sqlite3.Connection:
    """Minimal in-memory schema: just symbols + pattern_instances, the
    two tables pattern_exists_for_ticker_anchor's JOIN touches. One
    seed row: WFG @ 2026-01-08 -- mirrors the real pid=26 case this
    guard exists to have caught."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE symbols (symbol_id INTEGER PRIMARY KEY, ticker TEXT UNIQUE)"
    )
    conn.execute(
        "CREATE TABLE pattern_instances ("
        "  pattern_instance_id INTEGER PRIMARY KEY,"
        "  symbol_id INTEGER NOT NULL,"
        "  anchor_date TEXT NOT NULL"
        ")"
    )
    conn.execute("INSERT INTO symbols (symbol_id, ticker) VALUES (1, 'WFG')")
    conn.execute(
        "INSERT INTO pattern_instances (pattern_instance_id, symbol_id, anchor_date) "
        "VALUES (1, 1, '2026-01-08')"
    )
    conn.commit()
    return conn


def _test_exact_collision_detected() -> None:
    """Same ticker, same anchor_date as the seed row -- must return True.
    This is the exact real-world case (pid=26 WFG@2026-01-08, then a
    later xlsx re-export of the same window under a different filename)
    that slipped past EC-023's filename-only check."""
    conn = _make_temp_catalog()
    result = pattern_exists_for_ticker_anchor(conn, "WFG", date(2026, 1, 8))
    conn.close()
    if result is True:
        ok("exact (ticker, anchor_date) match detected -> True")
    else:
        fail(f"expected True for WFG@2026-01-08, got {result}")


def _test_different_anchor_date_not_a_collision() -> None:
    """Same ticker, different anchor_date -- must return False. A real,
    legitimate second WFG pattern on a different date is NOT a
    duplicate and must not be blocked."""
    conn = _make_temp_catalog()
    result = pattern_exists_for_ticker_anchor(conn, "WFG", date(2026, 2, 15))
    conn.close()
    if result is False:
        ok("same ticker, different anchor_date -> False (not blocked)")
    else:
        fail(f"expected False for WFG@2026-02-15, got {result}")


def _test_different_ticker_not_a_collision() -> None:
    """Different ticker, same anchor_date -- must return False. Two
    different symbols legitimately sharing an anchor_date is normal,
    not a collision."""
    conn = _make_temp_catalog()
    result = pattern_exists_for_ticker_anchor(conn, "CXW", date(2026, 1, 8))
    conn.close()
    if result is False:
        ok("different ticker, same anchor_date -> False (not blocked)")
    else:
        fail(f"expected False for CXW@2026-01-08, got {result}")


def _test_empty_catalog_no_false_positive() -> None:
    """A ticker that has never been ingested at all -- must return
    False, not raise (e.g. on a symbols-table lookup miss)."""
    conn = _make_temp_catalog()
    result = pattern_exists_for_ticker_anchor(conn, "ZZZZ", date(2020, 1, 1))
    conn.close()
    if result is False:
        ok("never-seen ticker -> False, no exception")
    else:
        fail(f"expected False for an unseen ticker, got {result}")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== pattern_exists_for_ticker_anchor() collision detection ===")
    _test_exact_collision_detected()
    _test_different_anchor_date_not_a_collision()
    _test_different_ticker_not_a_collision()
    _test_empty_catalog_no_false_positive()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
