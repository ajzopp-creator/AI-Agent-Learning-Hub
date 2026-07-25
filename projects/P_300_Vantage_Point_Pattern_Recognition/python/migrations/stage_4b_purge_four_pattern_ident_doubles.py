"""
FILE: migrations/stage_4b_purge_four_pattern_ident_doubles.py
VERSION: 1.1
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: migration
DESCRIPTION:
    One-shot migration: purges 4 confirmed PATTERN_IDENT catalog
    doubles (WFG pid=437, PLTR pid=36, BOIL pid=487, RRC pid=405 --
    each a later VP re-export of an already-catalogued window under a
    different filename, byte-identical bars+labels to an earlier KEEP
    pid) and reseeds topk_cache. Same Lock+Temp-DB+Atomic-Move
    protocol as stage_4a_add_topk_cache.py -- copy -> purge+reseed the
    copy -> verify -> atomic_move, never in-place DELETE on the real
    file.

    Root cause (closed separately: add_pattern_pipeline.py +
    catalog_writer.pattern_exists_for_ticker_anchor): EC-023 only
    blocks an exact filename match, so a re-export under a different
    filename silently double-inserted. Found via a real TopKTieError
    on a live batch, 2026-07-20; catalog-wide scan confirmed exactly
    these 4 doubles.

    REMOVE_PIDS is a frozen 4-int set, not a "find and delete" loop.
    Preflight re-verifies every pair against LIVE data at run time and
    HALTs on mismatch. Also scans sqlite_master for any table outside
    the known 6-table delete scope with a pattern-id-shaped column, so
    "nothing else references these pids" is a real runtime check.

    topk_cache: full DROP + reseed via the proven seed_full_catalog()
    path (wiped before the per-pid delete loop -- v1.1 fix, see
    CHANGELOG), not a surgical fill (new ranking code = new risk). An
    uncaught TopKTieError during reseed means a real, different tie
    exists elsewhere -- propagates per Finding 3's rule; temp is left
    purged-but-topk-empty, live untouched either way.

CHANGELOG:
    - 2026-07-20 v1.1: topk_cache wipe moved before the per-pid delete
      loop -- real dry-run FK-constraint failure (topk_cache FK-
      references pattern_instances on both id columns).
    - 2026-07-20 v1.0: Initial release (WFG/PLTR/BOIL/RRC cleanup).

RUN (PEH): python migrations/stage_4b_purge_four_pattern_ident_doubles.py --live-db <path>
Dry run: point --live-db at a disposable COPY of live, never the real file.
"""
from __future__ import annotations
import argparse
import logging
import shutil
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout,
)
log = logging.getLogger("stage_4b")

_PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain import topk_cache  # noqa: E402
from infrastructure.catalog_writer import CATALOG_TABLES, catalog_checkout  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402
from infrastructure.topk_cache_io import (  # noqa: E402
    create_topk_cache_table, insert_topk_rows_batch,
)
from infrastructure.verify_ingestion import verify_and_promote  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog_path  # noqa: E402

# (ticker, anchor_date, keep_pid, remove_pid) -- hard-coded, confirmed
# via a real catalog-wide duplicate scan + full bar/label comparison,
# 2026-07-20. KEEP = earlier import (first-import-wins, approved plan).
DOUBLES: tuple[tuple[str, str, int, int], ...] = (
    ("WFG", "2026-01-08", 26, 437),
    ("PLTR", "2025-10-23", 17, 36),
    ("BOIL", "2026-01-16", 449, 487),
    ("RRC", "2026-03-30", 353, 405),
)
REMOVE_PIDS: frozenset[int] = frozenset(d[3] for d in DOUBLES)
KEEP_PIDS: frozenset[int] = frozenset(d[2] for d in DOUBLES)

EXPECTED_ID_TABLES: frozenset[str] = frozenset({
    "pattern_instances", "pattern_bars", "forward_labels",
    "pattern_features", "topk_cache", "source_files",
})
_NEVER_TOUCHED_TABLES: frozenset[str] = frozenset({"symbols", "feature_sets"})

def _scan_for_unknown_id_tables(conn) -> list[str]:
    """Flag any table outside EXPECTED_ID_TABLES with a pattern-id-shaped column -- confirms delete scope against ACTUAL schema."""
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'"
    ).fetchall()]
    unexpected = []
    for table in tables:
        if table in EXPECTED_ID_TABLES or table in _NEVER_TOUCHED_TABLES:
            continue
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if any(c in ("pattern_instance_id", "matched_pid", "pid") for c in cols):
            unexpected.append(table)
    return unexpected

def _verify_pair_identity(conn, ticker: str, anchor_date: str, keep_pid: int, remove_pid: int) -> None:
    """Confirms exactly 2 pattern_instances rows for (ticker, anchor_date), and both pids resolve to that combo."""
    count = conn.execute(
        "SELECT COUNT(*) FROM pattern_instances pi "
        "JOIN symbols s ON s.symbol_id = pi.symbol_id "
        "WHERE s.ticker = ? AND pi.anchor_date = ?", (ticker, anchor_date),
    ).fetchone()[0]
    if count != 2:
        raise RuntimeError(
            f"{ticker}@{anchor_date}: expected 2 pattern_instances rows, "
            f"found {count}. Catalog changed since planning -- HALT."
        )
    for pid in (keep_pid, remove_pid):
        row = conn.execute(
            "SELECT s.ticker, pi.anchor_date FROM pattern_instances pi "
            "JOIN symbols s ON s.symbol_id = pi.symbol_id "
            "WHERE pi.pattern_instance_id = ?", (pid,),
        ).fetchone()
        if row is None or row[0] != ticker or row[1] != anchor_date:
            raise RuntimeError(
                f"pid={pid}: expected {ticker}@{anchor_date}, found "
                f"{row!r} -- HALT."
            )

def _verify_pair_content_identical(conn, ticker: str, anchor_date: str, keep_pid: int, remove_pid: int) -> None:
    """Confirms bar-identical AND label-identical -- the actual proof of duplication, not just a ticker+date coincidence."""
    def _bars(pid: int):
        return conn.execute(
            "SELECT bar_offset, close, high, low, open, volume "
            "FROM pattern_bars WHERE pattern_instance_id = ? "
            "ORDER BY bar_offset", (pid,),
        ).fetchall()
    def _labels(pid: int):
        return conn.execute(
            "SELECT horizon_days, return_pct, is_profitable "
            "FROM forward_labels WHERE pattern_instance_id = ? "
            "ORDER BY horizon_days", (pid,),
        ).fetchall()

    if _bars(keep_pid) != _bars(remove_pid):
        raise RuntimeError(
            f"{ticker}@{anchor_date}: pid={keep_pid}/{remove_pid} NOT "
            f"bar-identical -- not a confirmed duplicate, HALT."
        )
    if _labels(keep_pid) != _labels(remove_pid):
        raise RuntimeError(
            f"{ticker}@{anchor_date}: pid={keep_pid}/{remove_pid} "
            f"forward_labels differ -- HALT."
        )
    log.info("Preflight OK: %s@%s keep=%d remove=%d", ticker, anchor_date, keep_pid, remove_pid)

def _source_file_exclusive(conn, pid: int) -> int | None:
    """pid's source_file_id if used by NO OTHER pattern_instances row (safe to delete too), else None (shared)."""
    row = conn.execute(
        "SELECT source_file_id FROM pattern_instances WHERE pattern_instance_id = ?",
        (pid,),
    ).fetchone()
    if row is None:
        return None
    source_file_id = row[0]
    count = conn.execute(
        "SELECT COUNT(*) FROM pattern_instances WHERE source_file_id = ?",
        (source_file_id,),
    ).fetchone()[0]
    return source_file_id if count == 1 else None

def _delete_pair_rows(conn, pid: int) -> tuple[int, int, int]:
    """Delete bars/labels/features/instance for one remove_pid. Returns (bars, labels, features) deleted counts."""
    cur = conn.execute("DELETE FROM pattern_bars WHERE pattern_instance_id = ?", (pid,))
    bars = cur.rowcount
    cur = conn.execute("DELETE FROM forward_labels WHERE pattern_instance_id = ?", (pid,))
    labels = cur.rowcount
    cur = conn.execute("DELETE FROM pattern_features WHERE pattern_instance_id = ?", (pid,))
    features = cur.rowcount
    conn.execute("DELETE FROM pattern_instances WHERE pattern_instance_id = ?", (pid,))
    return bars, labels, features

def _preflight_and_delete(temp_path: Path) -> tuple[dict[str, int], int, int, int, int]:
    """All read-only checks + all deletes on temp_path. Returns (pre_counts, bars, labels, features, source_files
    deleted). topk_cache reseed happens separately (_reseed_topk) after this transaction commits."""
    with connection_context(catalog_path=str(temp_path)) as conn:
        unexpected = _scan_for_unknown_id_tables(conn)
        if unexpected:
            raise RuntimeError(
                f"Table(s) with a pattern-id-shaped column outside this "
                f"migration's known scope: {unexpected}. HALT."
            )
        for ticker, anchor_date, keep_pid, remove_pid in DOUBLES:
            _verify_pair_identity(conn, ticker, anchor_date, keep_pid, remove_pid)
            _verify_pair_content_identical(conn, ticker, anchor_date, keep_pid, remove_pid)

        pre_counts = catalog_checkout(conn)

        # topk_cache FK-references pattern_instances (both id cols) -- wipe before any pattern_instances delete (v1.1 fix).
        conn.execute("DELETE FROM topk_cache")

        bars_deleted = labels_deleted = features_deleted = source_files_deleted = 0
        source_files_to_delete: list[int] = []
        for pid in sorted(REMOVE_PIDS):
            excl = _source_file_exclusive(conn, pid)
            if excl is not None:
                source_files_to_delete.append(excl)
            bars, labels, features = _delete_pair_rows(conn, pid)
            bars_deleted += bars
            labels_deleted += labels
            features_deleted += features

        for source_file_id in source_files_to_delete:
            cur = conn.execute(
                "DELETE FROM source_files WHERE source_file_id = ?", (source_file_id,)
            )
            source_files_deleted += cur.rowcount

        conn.commit()

    log.info(
        "Deletes committed: pattern_instances=-%d pattern_bars=-%d "
        "forward_labels=-%d pattern_features=-%d source_files=-%d",
        len(REMOVE_PIDS), bars_deleted, labels_deleted, features_deleted,
        source_files_deleted,
    )
    return pre_counts, bars_deleted, labels_deleted, features_deleted, source_files_deleted

def _reseed_topk(temp_path: Path, pre_topk_count: int) -> int:
    """Reload the purged temp catalog and reseed topk_cache. Uncaught TopKTieError means a real tie exists elsewhere --
    propagates per Finding 3's rule (see module docstring). Returns the topk_cache row-count delta."""
    _path, all_metadata, historical_windows, _labels = load_full_catalog(temp_path)
    log.info("Post-purge catalog: %d patterns (reseeding topk_cache)", len(all_metadata))
    seed_result = topk_cache.seed_full_catalog(all_metadata, historical_windows)
    all_rows = [row for rows in seed_result.values() for row in rows]

    with connection_context(catalog_path=str(temp_path)) as conn:
        create_topk_cache_table(conn)  # idempotent
        insert_topk_rows_batch(conn, all_rows)
        conn.commit()

    log.info(
        "Reseeded topk_cache: %d patterns, %d rows (was %d)",
        len(seed_result), len(all_rows), pre_topk_count,
    )
    return len(all_rows) - pre_topk_count

def run_migration(live_catalog_path: Path | None = None) -> Path:
    """Full cycle: copy -> purge+reseed the copy -> verify -> atomic_move. Point live_catalog_path at a disposable
    COPY for a PEH dry run -- no separate dry-run mode, --live-db pointed at a copy IS the dry run."""
    resolved_path = Path(live_catalog_path) if live_catalog_path else get_latest_catalog_path()
    temp_path = resolved_path.with_name(
        resolved_path.stem + ".purge4_migration_tmp" + resolved_path.suffix
    )
    log.info("Target catalog: %s", resolved_path)
    log.info("Temp copy:      %s", temp_path)
    log.info("REMOVE_PIDS: %s   KEEP_PIDS: %s", sorted(REMOVE_PIDS), sorted(KEEP_PIDS))
    shutil.copy2(resolved_path, temp_path)

    pre_counts, bars, labels, features, source_files = _preflight_and_delete(temp_path)
    topk_delta = _reseed_topk(temp_path, pre_counts["topk_cache"])

    expected_delta = {t: 0 for t in CATALOG_TABLES}
    expected_delta.update({
        "pattern_instances": -len(REMOVE_PIDS),
        "pattern_bars": -bars,
        "forward_labels": -labels,
        "pattern_features": -features,
        "source_files": -source_files,
        "topk_cache": topk_delta,
    })

    result = verify_and_promote(temp_path, resolved_path, expected_delta, pre_counts)
    if not result.passed:
        log.error("Migration verification FAILED: %s", result.failures)
        log.error("Temp copy left at %s. Target catalog untouched.", temp_path)
        sys.exit(2)

    log.info(
        "Migration complete. target=%s backup=%s post_counts=%s",
        resolved_path, result.backup_path, result.post_counts,
    )
    return resolved_path

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 4b -- purge 4 PATTERN_IDENT doubles + reseed topk_cache."
    )
    parser.add_argument(
        "--live-db", type=str, default=None,
        help="Catalog to modify. For a dry run, point at a disposable COPY "
             "of live -- never the real file until reviewed. Default: "
             "get_latest_catalog_path() (the REAL live catalog).",
    )
    args = parser.parse_args()
    log.info("Stage 4b: purge 4 PATTERN_IDENT doubles + topk_cache reseed")
    run_migration(Path(args.live_db) if args.live_db else None)

if __name__ == "__main__":
    main()
