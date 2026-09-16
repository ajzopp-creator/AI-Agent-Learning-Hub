"""
FILE: catalog_summary.py
VERSION: 1.0
DATE: 2026-05-15
AUTHOR: Anthony Zoppi + Claude
LAYER: utilities
DESCRIPTION:
    Operator-facing health check for the P_300 catalog. Reports:

        1. Catalog file location, size, last-modified
        2. Row counts on all 7 tables
        3. Symbol distribution (patterns per ticker)
        4. Ghost pattern scan (hollow pattern_instances per EC-057)
        5. Recent pattern_instances (last N, default 5)
        6. Forward-label statistics (win-rate + avg return per horizon)

    Read-only against the active catalog (resolved via
    db_utils.get_latest_catalog). No writes, no migrations, no risk.

    Run any time. Run after Pipeline A ingest as a Check-In sanity pass.
    Run when investigating a strange Pipeline B result. Run before
    Stage 5 multi-symbol re-ingest to baseline the starting state.

CHANGELOG:
    - 2026-05-15 v1.0: Stage 4 file #10 of plan. Stage 4 POC close-out.
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import LOG_FORMAT  # noqa: E402
from infrastructure.catalog_writer import CATALOG_TABLES  # noqa: E402
from infrastructure.verify_ingestion import _check_no_hollow_instances  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog  # noqa: E402

logger = logging.getLogger(__name__)

_BAR = "=" * 64
_SUB = "-" * 64


# ─────────────────────────────────────────────────────────────────────────────
# Section helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_file_stats(catalog_path: Path) -> None:
    """Section 1: catalog file location, size, last-modified."""
    stat = catalog_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Catalog:  {catalog_path}")
    print(f"Size:     {stat.st_size:,} bytes ({stat.st_size / 1024:.1f} KB)")
    print(f"Modified: {mtime}")


def _print_row_counts(conn: sqlite3.Connection) -> None:
    """Section 2: row count per catalog table."""
    print(_SUB)
    print("Row counts")
    print(_SUB)
    for t in CATALOG_TABLES:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        annotation = ""
        if t == "feature_sets":
            versions = [
                r[0] for r in conn.execute(
                    "SELECT feature_version FROM feature_sets ORDER BY feature_set_id"
                )
            ]
            annotation = f"  ({', '.join(versions)})" if versions else ""
        if t == "pattern_features":
            annotation = "  (deferred per D2 scope trim)"
        print(f"  {t:<18} {n:>6}{annotation}")


def _print_symbol_distribution(conn: sqlite3.Connection) -> None:
    """Section 3: count of pattern_instances per ticker."""
    print(_SUB)
    print("Symbol distribution")
    print(_SUB)
    rows = conn.execute(
        "SELECT s.ticker, COUNT(pi.pattern_instance_id) "
        "FROM symbols s LEFT JOIN pattern_instances pi "
        "  ON pi.symbol_id = s.symbol_id "
        "GROUP BY s.ticker ORDER BY 2 DESC, s.ticker"
    ).fetchall()
    if not rows:
        print("  (no symbols in catalog)")
        return
    for ticker, n in rows:
        plural = "pattern" if n == 1 else "patterns"
        print(f"  {ticker:<8} {n:>4} {plural}")


def _print_ghost_check(conn: sqlite3.Connection) -> None:
    """Section 4: ghost pattern_instances (missing bars or labels)."""
    print(_SUB)
    print("Ghost pattern check (hollow instances)")
    print(_SUB)
    count, ids = _check_no_hollow_instances(conn)
    if count == 0:
        print("  0 hollow records  [OK]")
    else:
        sample = ids[:10]
        more = f"  (+{count - 10} more)" if count > 10 else ""
        print(f"  {count} HOLLOW instances: {sample}{more}")
        print("  These violate the schema-as-protection contract (EC-027/EC-057).")


def _print_recent_patterns(conn: sqlite3.Connection, limit: int = 5) -> None:
    """Section 5: most recent pattern_instances with companion counts."""
    print(_SUB)
    print(f"Recent patterns (last {limit})")
    print(_SUB)
    sql = """
        SELECT pi.pattern_instance_id, s.ticker, pi.anchor_date,
               pi.window_length, pi.data_origin_type,
               (SELECT COUNT(*) FROM pattern_bars pb
                 WHERE pb.pattern_instance_id = pi.pattern_instance_id),
               (SELECT COUNT(*) FROM forward_labels fl
                 WHERE fl.pattern_instance_id = pi.pattern_instance_id)
          FROM pattern_instances pi
          JOIN symbols s ON s.symbol_id = pi.symbol_id
         ORDER BY pi.pattern_instance_id DESC
         LIMIT ?
    """
    rows = conn.execute(sql, (limit,)).fetchall()
    if not rows:
        print("  (catalog has no pattern_instances)")
        return
    for pid, ticker, anchor, wlen, origin, n_bars, n_labels in rows:
        print(
            f"  id={pid:<4} {ticker:<6} anchor={anchor}  "
            f"window={wlen}  origin={origin}  bars={n_bars}  labels={n_labels}"
        )


def _print_forward_label_stats(conn: sqlite3.Connection) -> None:
    """Section 6: win-rate + avg return per horizon across all patterns."""
    print(_SUB)
    print("Forward-label statistics (all symbols)")
    print(_SUB)
    sql = """
        SELECT horizon_days,
               COUNT(*) AS n,
               SUM(is_profitable) AS wins,
               AVG(return_pct) AS avg_return
          FROM forward_labels
         GROUP BY horizon_days
         ORDER BY horizon_days
    """
    rows = conn.execute(sql).fetchall()
    if not rows:
        print("  (no forward labels in catalog)")
        return
    for horizon, n, wins, avg in rows:
        win_pct = (wins / n) * 100 if n else 0
        sign = "+" if avg >= 0 else ""
        print(
            f"  +{horizon:>2}d  n={n:<4}  {wins}/{n} profitable "
            f"({win_pct:>5.1f}%)  avg return {sign}{avg * 100:.2f}%"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Public entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def run_summary(catalog_path: Path | None = None, recent_limit: int = 5) -> int:
    """Print full catalog summary. Returns 0 on success, 1 if catalog
    can't be opened or has any ghost records."""
    if catalog_path is None:
        catalog_path = Path(get_latest_catalog())
    if not catalog_path.exists():
        print(f"FATAL: catalog not found: {catalog_path}")
        return 1

    print()
    print(_BAR)
    print("P_300 Catalog Summary")
    print(_BAR)
    _print_file_stats(catalog_path)

    with connection_context(catalog_path=str(catalog_path)) as conn:
        _print_row_counts(conn)
        _print_symbol_distribution(conn)
        _print_ghost_check(conn)
        ghost_count, _ = _check_no_hollow_instances(conn)
        _print_recent_patterns(conn, limit=recent_limit)
        _print_forward_label_stats(conn)

    print(_BAR)
    overall = "HEALTHY" if ghost_count == 0 else "ATTENTION REQUIRED"
    print(f"OVERALL: {overall}")
    print(_BAR)
    print()
    return 0 if ghost_count == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Print a health summary of the active P_300 catalog."
    )
    parser.add_argument(
        "--catalog",
        default=None,
        help="Optional catalog path override; defaults to db_utils.get_latest_catalog().",
    )
    parser.add_argument(
        "--recent",
        type=int,
        default=5,
        help="Number of most-recent patterns to show (default: 5).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, stream=sys.stdout)
    catalog = Path(args.catalog) if args.catalog else None
    sys.exit(run_summary(catalog, recent_limit=args.recent))
