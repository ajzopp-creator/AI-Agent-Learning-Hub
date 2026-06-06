"""
FILE: catalog_reader.py
VERSION: 1.0
DATE: 2026-05-17
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Read-only query API against the P_300 catalog DB for Pipeline B
    (Daily Evaluate). Mirrors catalog_writer.py's calling convention:
    every function takes an open sqlite3.Connection as its first
    argument, and the caller (typically application/daily_evaluate_
    pipeline.py) owns connection lifecycle via
    utilities.db_connect.connection_context() so one evaluation pass =
    one connection.

    Layer rules:
        - Pure I/O. No business logic. No similarity math. No
          classification.
        - Outputs are Pydantic records from schemas_pipeline_b.py
          (NormalizedBar, ForwardLabelLite) plus a local PatternMetadata
          dataclass that doesn't cross persistence boundary.
        - Reads only. No writes against any catalog table. Pipeline B's
          live candidates are transient in-memory only (Stage 6 decision
          E) and are never inserted, so this module deliberately exposes
          no INSERT/UPDATE/DELETE surface.

    Bulk loaders use a single `WHERE pattern_instance_id IN (?, ?, ...)`
    query with dynamic placeholders rather than N round trips. SQLite's
    default SQLITE_MAX_VARIABLE_NUMBER is 999, so call sites should
    chunk pattern_ids above that count. Not relevant at current catalog
    sizes (~5 patterns; broader 14-symbol set still well under).

CHANGELOG:
    - 2026-05-17 v1.0: Initial release. Stage 6 file #3 of 9.
"""
from __future__ import annotations

import logging
import sqlite3
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# sys.path bootstrap so `from schemas_pipeline_b import ...` and
# `from config import ...` resolve on direct invocation as well as via
# cli.py / daily_evaluate_pipeline.py. Mirrors the pattern used by
# catalog_writer.py and db_connect.py.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import ORIGIN_PATTERN_IDENT  # noqa: E402
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar  # noqa: E402

# M-011: route logging to stdout so PowerShell doesn't render INFO lines
# as red NativeCommandError on success runs.
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Module constants
# ─────────────────────────────────────────────────────────────────────────────

# pattern_bars columns required to construct a NormalizedBar (bar_offset
# + bar_date + 17 raw VP + 10 normalized = 29 columns). Order matches
# both the SQL SELECT below and the NormalizedBar field set; the zip in
# _row_to_normalized_bar relies on this alignment. Kept private —
# catalog_writer.py owns the canonical write-side list.
_BAR_SELECT_COLUMNS: tuple[str, ...] = (
    "bar_offset", "bar_date",
    "open", "high", "low", "close", "volume",
    "stdiff", "mtdiff", "ltdiff",
    "pred_high", "pred_low", "pred_range",
    "williams_emai", "psi", "neural_index",
    "triple_cross_short", "triple_cross_medium", "triple_cross_long",
    "close_pct_from_anchor", "range_pct", "body_pct", "volume_zscore",
    "stdiff_pct", "mtdiff_pct", "ltdiff_pct",
    "pred_high_pct", "pred_low_pct", "pred_range_pct",
)


@dataclass(frozen=True)
class PatternMetadata:
    """Identity + provenance fields joined from symbols + pattern_instances.

    Internal infrastructure type — doesn't cross the persistence
    boundary, so it lives here rather than in schemas_pipeline_b.py.
    Domain layers consume it to populate MatchResult.ticker and
    MatchResult.anchor_date when building match results.
    """
    pattern_instance_id: int
    ticker: str
    anchor_date: date
    window_length: int


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
# ─────────────────────────────────────────────────────────────────────────────

def _row_to_normalized_bar(row: tuple) -> NormalizedBar:
    """Build a NormalizedBar from a row matching _BAR_SELECT_COLUMNS order.

    Pydantic v2 coerces the bar_date TEXT into a date object; raw +
    normalized fields land directly. Field validation (high>=low,
    bar_offset bounds, etc.) fires inside the NormalizedBar constructor.
    """
    return NormalizedBar(**dict(zip(_BAR_SELECT_COLUMNS, row)))


def _build_in_clause(n: int) -> str:
    """Build a comma-separated `?, ?, ?` placeholder string of length n."""
    if n <= 0:
        raise ValueError("In-clause requires at least one placeholder")
    return ",".join("?" for _ in range(n))


# ─────────────────────────────────────────────────────────────────────────────
# Single-pattern readers
# ─────────────────────────────────────────────────────────────────────────────

def get_all_pattern_ids(
    conn: sqlite3.Connection,
    origin_type: str = ORIGIN_PATTERN_IDENT,
) -> list[int]:
    """Return every pattern_instance_id with matching data_origin_type.

    Default is PATTERN_IDENT — the historical training set. Pipeline B
    runs similarity against this set only; EVAL_SET would be transient
    candidates (none currently persisted, per Stage 6 decision E).
    """
    cur = conn.execute(
        "SELECT pattern_instance_id FROM pattern_instances "
        "WHERE data_origin_type = ? ORDER BY pattern_instance_id",
        (origin_type,),
    )
    ids = [row[0] for row in cur.fetchall()]
    logger.info(
        "Loaded %d pattern_instance_ids (origin_type=%s)",
        len(ids), origin_type,
    )
    return ids


def get_normalized_window(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
) -> list[NormalizedBar]:
    """Return all bars for a pattern, sorted ascending by bar_offset.

    Result length equals pattern_instances.window_length (5–20 bars).
    Empty result raises ValueError — Pipeline B treats a missing window
    as a fatal catalog integrity issue, not a recoverable case.
    """
    cols = ", ".join(_BAR_SELECT_COLUMNS)
    cur = conn.execute(
        f"SELECT {cols} FROM pattern_bars "
        f"WHERE pattern_instance_id = ? ORDER BY bar_offset",
        (pattern_instance_id,),
    )
    rows = cur.fetchall()
    if not rows:
        raise ValueError(
            f"No pattern_bars rows for pattern_instance_id="
            f"{pattern_instance_id}"
        )
    return [_row_to_normalized_bar(row) for row in rows]


def get_forward_labels_all(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
) -> dict[int, ForwardLabelLite]:
    """Return all forward labels for a pattern, keyed by horizon_days.

    Typically returns 5 entries (5/7/10/15/20). A pattern near the edge
    of capturable history may have fewer — caller checks dict length.
    Shape matches MatchResult.forward_labels in schemas_pipeline_b.
    """
    cur = conn.execute(
        "SELECT horizon_days, return_pct, is_profitable "
        "FROM forward_labels WHERE pattern_instance_id = ? "
        "ORDER BY horizon_days",
        (pattern_instance_id,),
    )
    return {
        row[0]: ForwardLabelLite(return_pct=row[1], is_profitable=row[2])
        for row in cur.fetchall()
    }


def get_pattern_metadata(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
) -> PatternMetadata:
    """Return ticker + anchor_date + window_length for a single pattern."""
    cur = conn.execute(
        "SELECT pi.pattern_instance_id, s.ticker, pi.anchor_date, "
        "       pi.window_length "
        "FROM pattern_instances pi "
        "JOIN symbols s ON pi.symbol_id = s.symbol_id "
        "WHERE pi.pattern_instance_id = ?",
        (pattern_instance_id,),
    )
    row = cur.fetchone()
    if row is None:
        raise ValueError(
            f"No pattern_instances row for pattern_instance_id="
            f"{pattern_instance_id}"
        )
    return PatternMetadata(
        pattern_instance_id=row[0],
        ticker=row[1],
        anchor_date=date.fromisoformat(row[2]),
        window_length=row[3],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Bulk loaders
# ─────────────────────────────────────────────────────────────────────────────

def bulk_load_normalized_windows(
    conn: sqlite3.Connection,
    pattern_ids: list[int],
) -> dict[int, list[NormalizedBar]]:
    """Return normalized windows for many patterns in one round trip.

    Outer dict keyed by pattern_instance_id; each value is the same
    shape as get_normalized_window's return — list of NormalizedBar
    sorted by bar_offset ascending. pattern_ids missing from the
    catalog are silently absent from the result (caller checks length).
    """
    if not pattern_ids:
        return {}
    cols = ", ".join(_BAR_SELECT_COLUMNS)
    placeholders = _build_in_clause(len(pattern_ids))
    cur = conn.execute(
        f"SELECT pattern_instance_id, {cols} FROM pattern_bars "
        f"WHERE pattern_instance_id IN ({placeholders}) "
        f"ORDER BY pattern_instance_id, bar_offset",
        tuple(pattern_ids),
    )
    out: dict[int, list[NormalizedBar]] = {}
    for row in cur.fetchall():
        pid = row[0]
        out.setdefault(pid, []).append(_row_to_normalized_bar(row[1:]))
    logger.info(
        "Bulk-loaded %d normalized windows (%d requested)",
        len(out), len(pattern_ids),
    )
    return out


def bulk_load_forward_labels(
    conn: sqlite3.Connection,
    pattern_ids: list[int],
) -> dict[int, dict[int, ForwardLabelLite]]:
    """Return forward labels for many patterns in one round trip.

    Outer dict keyed by pattern_instance_id; inner dict keyed by
    horizon_days. Patterns with no forward_labels rows are absent from
    the outer dict.
    """
    if not pattern_ids:
        return {}
    placeholders = _build_in_clause(len(pattern_ids))
    cur = conn.execute(
        f"SELECT pattern_instance_id, horizon_days, return_pct, "
        f"       is_profitable "
        f"FROM forward_labels "
        f"WHERE pattern_instance_id IN ({placeholders}) "
        f"ORDER BY pattern_instance_id, horizon_days",
        tuple(pattern_ids),
    )
    out: dict[int, dict[int, ForwardLabelLite]] = {}
    for pid, horizon, ret, is_prof in cur.fetchall():
        out.setdefault(pid, {})[horizon] = ForwardLabelLite(
            return_pct=ret, is_profitable=is_prof,
        )
    logger.info(
        "Bulk-loaded forward labels for %d patterns (%d requested)",
        len(out), len(pattern_ids),
    )
    return out


def bulk_load_pattern_metadata(
    conn: sqlite3.Connection,
    pattern_ids: list[int],
) -> dict[int, PatternMetadata]:
    """Return metadata for many patterns in one round trip, keyed by pid."""
    if not pattern_ids:
        return {}
    placeholders = _build_in_clause(len(pattern_ids))
    cur = conn.execute(
        f"SELECT pi.pattern_instance_id, s.ticker, pi.anchor_date, "
        f"       pi.window_length "
        f"FROM pattern_instances pi "
        f"JOIN symbols s ON pi.symbol_id = s.symbol_id "
        f"WHERE pi.pattern_instance_id IN ({placeholders})",
        tuple(pattern_ids),
    )
    out: dict[int, PatternMetadata] = {}
    for pid, ticker, anchor_iso, wlen in cur.fetchall():
        out[pid] = PatternMetadata(
            pattern_instance_id=pid,
            ticker=ticker,
            anchor_date=date.fromisoformat(anchor_iso),
            window_length=wlen,
        )
    logger.info(
        "Bulk-loaded metadata for %d patterns (%d requested)",
        len(out), len(pattern_ids),
    )
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Smoke harness — `python infrastructure/catalog_reader.py`
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utilities.db_connect import connection_context

    with connection_context() as conn:
        pids = get_all_pattern_ids(conn)
        print(f"PATTERN_IDENT ids: {pids}")
        if pids:
            first = pids[0]
            window = get_normalized_window(conn, first)
            labels = get_forward_labels_all(conn, first)
            meta = get_pattern_metadata(conn, first)
            print(
                f"  pid={first} ticker={meta.ticker} "
                f"anchor={meta.anchor_date} window_length={meta.window_length}"
            )
            print(
                f"  bars loaded: {len(window)}, "
                f"horizons: {sorted(labels.keys())}"
            )
            bulk_w = bulk_load_normalized_windows(conn, pids)
            bulk_l = bulk_load_forward_labels(conn, pids)
            bulk_m = bulk_load_pattern_metadata(conn, pids)
            print(
                f"  bulk loaded: {len(bulk_w)} windows, "
                f"{len(bulk_l)} label sets, {len(bulk_m)} metadata records"
            )
