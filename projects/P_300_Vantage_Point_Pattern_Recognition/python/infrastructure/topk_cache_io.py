"""
FILE: topk_cache_io.py
VERSION: 1.0
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    SQLite I/O for the topk_cache table (WO-P300-E4.006, decision #2:
    a real 8th catalog table, single source of truth inside catalog.db
    itself -- no side file, no separate cache DB). Pure I/O, no
    business logic (layer rule, mirrors catalog_writer.py's own
    docstring convention) -- domain/topk_cache.py owns all admission
    logic; this file only reads/writes what that module produces.

    create_topk_cache_table() is idempotent (CREATE TABLE IF NOT
    EXISTS) -- safe to call on every migration run without a
    pre-existence check (decision #6).

    bulk_load_topk_cache() mirrors infrastructure/catalog_reader.py's
    bulk_load_* convention (same signature shape, same "absent pid =
    no rows" contract) so callers building domain/topk_cache.py's
    existing_cache argument don't need a different mental model for
    this table than any other bulk load in the project.

    Schema (decision #5, final): pattern_instance_id, rank,
    matched_pid, composite_distance. PRIMARY KEY (pattern_instance_id,
    rank) -- no surrogate key, the composite is already unique. Both
    pattern_instance_id and matched_pid FK-reference
    pattern_instances(pattern_instance_id).

CHANGELOG:
    - 2026-07-19 v1.0: WO-P300-E4.006. Initial release.
"""
from __future__ import annotations

import logging
import sqlite3
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from schemas_eval import TopKMatch  # noqa: E402

logger = logging.getLogger(__name__)


TOPK_CACHE_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS topk_cache (
    pattern_instance_id INTEGER NOT NULL,
    rank                 INTEGER NOT NULL,
    matched_pid          INTEGER NOT NULL,
    composite_distance   REAL NOT NULL,
    PRIMARY KEY (pattern_instance_id, rank),
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id),
    FOREIGN KEY (matched_pid) REFERENCES pattern_instances(pattern_instance_id)
);
"""


def _build_in_clause(n: int) -> str:
    """Same shape as catalog_reader._build_in_clause -- kept local
    rather than imported: infrastructure/ modules don't share private
    helpers with each other by established convention in this
    project (only domain/ has that pattern so far, via M-082); this
    is a 1-line string builder, not worth breaking that convention
    for."""
    return ", ".join("?" * n)


def create_topk_cache_table(conn: sqlite3.Connection) -> None:
    """Idempotent schema creation -- safe to call every migration run
    (decision #6). Does not commit; caller owns the transaction."""
    conn.execute(TOPK_CACHE_SCHEMA_DDL)


def insert_topk_rows_batch(
    conn: sqlite3.Connection,
    rows: list[TopKMatch],
) -> int:
    """Batch-insert TopKMatch rows. Returns row count inserted. Caller
    is responsible for deleting any prior rows for the same
    pattern_instance_id first if this is a re-write, not a fresh
    insert (see delete_topk_rows_for_pattern) -- this does a plain
    INSERT, not INSERT OR REPLACE, so a duplicate (pattern_instance_
    id, rank) pair raises sqlite3.IntegrityError rather than silently
    overwriting (fail loud, matches M-051)."""
    if not rows:
        return 0
    conn.executemany(
        "INSERT INTO topk_cache "
        "(pattern_instance_id, rank, matched_pid, composite_distance) "
        "VALUES (?, ?, ?, ?)",
        [
            (r.pattern_instance_id, r.rank, r.matched_pid, r.composite_distance)
            for r in rows
        ],
    )
    return len(rows)


def delete_topk_rows_for_pattern(
    conn: sqlite3.Connection,
    pattern_instance_id: int,
) -> int:
    """Delete all cached rows for one pattern (pre-step before
    re-inserting an updated top-K, since insert_topk_rows_batch does
    a plain INSERT, not an upsert). Returns row count deleted."""
    cur = conn.execute(
        "DELETE FROM topk_cache WHERE pattern_instance_id = ?",
        (pattern_instance_id,),
    )
    return cur.rowcount


def bulk_load_topk_cache(
    conn: sqlite3.Connection,
    pattern_ids: list[int],
) -> dict[int, list[TopKMatch]]:
    """Return cached top-K lists for many patterns in one round trip,
    keyed by pattern_instance_id, ranks ordered ascending. Mirrors
    catalog_reader.bulk_load_forward_labels's exact shape (same
    signature, same "absent pid = no rows" contract) -- callers
    building domain/topk_cache.py's existing_cache argument use the
    same mental model as every other bulk load in this project."""
    if not pattern_ids:
        return {}
    placeholders = _build_in_clause(len(pattern_ids))
    cur = conn.execute(
        f"SELECT pattern_instance_id, rank, matched_pid, composite_distance "
        f"FROM topk_cache "
        f"WHERE pattern_instance_id IN ({placeholders}) "
        f"ORDER BY pattern_instance_id, rank",
        tuple(pattern_ids),
    )
    out: dict[int, list[TopKMatch]] = {}
    for pid, rank, matched_pid, dist in cur.fetchall():
        out.setdefault(pid, []).append(TopKMatch(
            pattern_instance_id=pid, rank=rank,
            matched_pid=matched_pid, composite_distance=dist,
        ))
    logger.info(
        "Bulk-loaded topk_cache for %d patterns (%d requested)",
        len(out), len(pattern_ids),
    )
    return out


def topk_row_count(conn: sqlite3.Connection) -> int:
    """Total row count in topk_cache -- used by the migration's
    verify step (decision #6: must equal 20 * pattern count after
    seed_full_catalog)."""
    return conn.execute("SELECT COUNT(*) FROM topk_cache").fetchone()[0]
