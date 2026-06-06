"""
FILE: inspect_pattern.py
VERSION: 1.0
DATE: 2026-05-16
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Read-only inspection of a single pattern_instance, sized for the Stage 5
    hand-compare regression check: operator picks one ingested pattern,
    computes forward labels by hand from the source XLSX, verifies pipeline
    output matches deterministically at all 5/7/10/15/20 horizons.

    Prints four sections:
        1. Pattern header — ticker, anchor_date, window_length, origin,
           feature_set, source_file (+ imported_at + source row count)
        2. Bars (raw OHLCV) — what the ingest captured from the XLSX
        3. Bars (normalized) — close_pct_from_anchor, range_pct, body_pct,
           volume_zscore (the columns Pipeline B cross-symbol matching reads)
        4. Forward labels — horizon, future_date, return_pct, implied
           future_close (= anchor_close * (1 + return_pct)), profitable.
           The implied future_close column is the hand-compare cheat: open
           the source XLSX, find the row at future_date, read close,
           compare against implied. Match to 4 decimals = pipeline OK.

    Read-only against the active catalog (resolved via
    db_utils.get_latest_catalog). No writes, no migrations, no risk.

    Usage:
        python cli.py inspect-pattern --id 1
        python python/utilities/inspect_pattern.py --id 1 [--catalog PATH]

CHANGELOG:
    - 2026-05-16 v1.0: Stage 5 hand-compare helper. Mirrors catalog_summary
      structure (utility layer, bare print(), connection_context, argparse).
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import LOG_FORMAT  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog  # noqa: E402

logger = logging.getLogger(__name__)

_BAR = "=" * 76
_SUB = "-" * 76


# ─────────────────────────────────────────────────────────────────────────────
# Fetch helpers
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_header(conn: sqlite3.Connection, pid: int) -> dict | None:
    """Single-row pattern header with all FK joins resolved.
    Returns None if pattern_instance_id is not in the catalog."""
    sql = """
        SELECT pi.pattern_instance_id, s.ticker, pi.anchor_date,
               pi.window_length, pi.data_origin_type,
               fs.feature_version, sf.filename, sf.imported_at, sf.row_count
          FROM pattern_instances pi
          JOIN symbols s        ON s.symbol_id        = pi.symbol_id
          JOIN feature_sets fs  ON fs.feature_set_id  = pi.feature_set_id
          JOIN source_files sf  ON sf.source_file_id  = pi.source_file_id
         WHERE pi.pattern_instance_id = ?
    """
    row = conn.execute(sql, (pid,)).fetchone()
    if row is None:
        return None
    keys = (
        "pattern_id", "ticker", "anchor_date", "window_length", "origin",
        "feature_version", "filename", "imported_at", "source_row_count",
    )
    return dict(zip(keys, row))


def _fetch_bars(conn: sqlite3.Connection, pid: int) -> list[sqlite3.Row]:
    """All bars for a pattern, ordered by bar_offset ascending (oldest first,
    anchor at offset 0 last). Uses sqlite3.Row so columns can be addressed by
    name in the print helpers."""
    conn.row_factory = sqlite3.Row
    sql = """
        SELECT bar_offset, bar_date,
               open, high, low, close, volume,
               close_pct_from_anchor, range_pct, body_pct, volume_zscore
          FROM pattern_bars
         WHERE pattern_instance_id = ?
         ORDER BY bar_offset ASC
    """
    return conn.execute(sql, (pid,)).fetchall()


def _fetch_labels(conn: sqlite3.Connection, pid: int) -> list[tuple]:
    """Forward labels ordered by horizon (5, 7, 10, 15, 20)."""
    sql = """
        SELECT horizon_days, future_date, return_pct, is_profitable
          FROM forward_labels
         WHERE pattern_instance_id = ?
         ORDER BY horizon_days ASC
    """
    return conn.execute(sql, (pid,)).fetchall()


# ─────────────────────────────────────────────────────────────────────────────
# Print helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_header(h: dict) -> None:
    """Section 1 — pattern identity + provenance."""
    print(f"Pattern ID:       {h['pattern_id']}")
    print(f"Ticker:           {h['ticker']}")
    print(f"Anchor date:      {h['anchor_date']}  (bar offset = 0)")
    print(f"Window length:    {h['window_length']} bars")
    print(f"Origin:           {h['origin']}")
    print(f"Feature set:      {h['feature_version']}")
    print(f"Source file:      {h['filename']}")
    print(
        f"Imported at:      {h['imported_at']}  "
        f"({h['source_row_count']} source rows)"
    )


def _print_bars_raw(bars: list[sqlite3.Row]) -> None:
    """Section 2 — raw OHLCV as captured from the XLSX."""
    print(_SUB)
    print("Bars (raw OHLCV)")
    print(_SUB)
    print(
        f"  {'offset':>6}  {'date':<10}  {'open':>10}  {'high':>10}  "
        f"{'low':>10}  {'close':>10}  {'volume':>14}"
    )
    for b in bars:
        print(
            f"  {b['bar_offset']:>6}  {b['bar_date']:<10}  "
            f"{b['open']:>10.4f}  {b['high']:>10.4f}  "
            f"{b['low']:>10.4f}  {b['close']:>10.4f}  "
            f"{b['volume']:>14,.0f}"
        )


def _print_bars_normalized(bars: list[sqlite3.Row]) -> None:
    """Section 3 — normalized columns Pipeline B reads for cross-symbol match."""
    print(_SUB)
    print("Bars (normalized — used by cross-symbol matching)")
    print(_SUB)
    print(
        f"  {'offset':>6}  {'close_pct':>10}  {'range_pct':>10}  "
        f"{'body_pct':>10}  {'vol_z':>10}"
    )
    for b in bars:
        print(
            f"  {b['bar_offset']:>6}  "
            f"{b['close_pct_from_anchor']:>10.5f}  "
            f"{b['range_pct']:>10.5f}  "
            f"{b['body_pct']:>10.5f}  "
            f"{b['volume_zscore']:>10.4f}"
        )


def _print_labels(labels: list[tuple], anchor_close: float | None) -> None:
    """Section 4 — forward labels with implied future_close for hand-compare."""
    print(_SUB)
    print("Forward labels (hand-compare these against the source XLSX)")
    print(_SUB)
    if not labels:
        print("  (no forward labels — ingest may be incomplete)")
        return
    if anchor_close is not None:
        print(f"  Anchor close: {anchor_close:.4f}")
        print("  Verify formula: return_pct = (future_close / anchor_close) - 1")
        print()
    print(
        f"  {'horizon':>8}  {'future_date':<12}  {'return_pct':>11}  "
        f"{'implied_future_close':>22}  {'profitable':>11}"
    )
    for horizon, future_date, return_pct, is_profitable in labels:
        if anchor_close is not None and return_pct is not None:
            implied_str = f"{anchor_close * (1 + return_pct):>22.4f}"
        else:
            implied_str = f"{'n/a':>22}"
        pct_str = (
            f"{return_pct * 100:>10.3f}%" if return_pct is not None else "n/a"
        )
        prof = "YES" if is_profitable else "no"
        print(
            f"  +{horizon:>5}d  {future_date:<12}  {pct_str:>11}  "
            f"{implied_str}  {prof:>11}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Public entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def run_inspect(pattern_id: int, catalog_path: Path | None = None) -> int:
    """Print full pattern detail for one pattern_instance_id.

    Returns 0 on success, 1 if pattern_id is not found or the catalog file
    can't be opened. No writes to the catalog — safe to run any time.
    """
    if catalog_path is None:
        catalog_path = Path(get_latest_catalog())
    if not catalog_path.exists():
        print(f"FATAL: catalog not found: {catalog_path}")
        return 1

    with connection_context(catalog_path=str(catalog_path)) as conn:
        header = _fetch_header(conn, pattern_id)
        if header is None:
            print(
                f"FATAL: pattern_instance_id={pattern_id} "
                f"not in {catalog_path.name}"
            )
            return 1
        bars = _fetch_bars(conn, pattern_id)
        labels = _fetch_labels(conn, pattern_id)

    anchor_close = None
    for b in bars:
        if b["bar_offset"] == 0:
            anchor_close = b["close"]
            break

    print()
    print(_BAR)
    print(f"P_300 Pattern Inspection — id {pattern_id}")
    print(_BAR)
    _print_header(header)
    _print_bars_raw(bars)
    _print_bars_normalized(bars)
    _print_labels(labels, anchor_close)
    print(_BAR)
    print()
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Inspect one pattern_instance for hand-compare regression."
    )
    parser.add_argument(
        "--id", type=int, required=True,
        help="pattern_instance_id to inspect (e.g., --id 1).",
    )
    parser.add_argument(
        "--catalog", default=None,
        help="Catalog path override; defaults to db_utils.get_latest_catalog().",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, stream=sys.stdout)
    catalog = Path(args.catalog) if args.catalog else None
    sys.exit(run_inspect(args.id, catalog))
