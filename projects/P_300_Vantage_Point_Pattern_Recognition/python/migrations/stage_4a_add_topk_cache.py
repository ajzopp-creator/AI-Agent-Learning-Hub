"""
FILE: stage_4a_add_topk_cache.py
VERSION: 1.0
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: migration
DESCRIPTION:
    One-shot migration for WO-P300-E4.006. ALTERs the real live
    catalog.db (adds the topk_cache table + seeds it for every existing
    pattern) via the SAME Lock+Temp-DB+Atomic Move protocol every other
    catalog write in this project uses -- unlike migrations/stage_3c_
    init_new_catalog.py, this does NOT write directly to a target path,
    because that script bootstraps a brand-new empty file with no
    existing data to protect; this one touches a live catalog with real
    trading-relevant data, so it goes through copy -> populate -> verify
    -> atomic_move, never an in-place ALTER (decision #6).

    Also IS Finding 3's tie census (WO-P300-E4.005): the same O(N^2)
    pass that seeds every pattern's initial top-20 also proves whether
    any exact tie exists at the top-K boundary anywhere in the live
    catalog. domain/topk_cache.py's seed_full_catalog() raises
    TopKTieError on the first tie found -- this script does NOT catch
    it. A tie means STOP, report back, no silent tiebreak fix (Finding
    3's own rule) -- the migration aborts before any write reaches the
    temp copy's insert step, and the real live catalog is untouched
    (verify_and_promote's atomic_move never runs).

    check_topk_cache is deliberately NOT used for this migration's
    verify_and_promote call (same reasoning as application/catalog_
    merge_pipeline.py's promote_staging_to_live -- the earliest
    pattern(s) in the whole catalog legitimately get zero topk_cache
    rows, degenerate_corpus=True, and the hollow-topk check can't tell
    that apart from a real population bug). The expected_delta check
    is exact and actual-count-based instead (decision #5's schema has
    no fixed row-per-pattern guarantee -- thin corpora get fewer than
    TOP_K_MATCHES rows).

CHANGELOG:
    - 2026-07-19 v1.0: WO-P300-E4.006. Initial release.
"""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("stage_4a")

_PYTHON_DIR = Path(__file__).resolve().parents[1]
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain import topk_cache  # noqa: E402
from infrastructure.catalog_writer import CATALOG_TABLES, catalog_checkout  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402
from infrastructure.topk_cache_io import (  # noqa: E402
    create_topk_cache_table,
    insert_topk_rows_batch,
)
from infrastructure.verify_ingestion import verify_and_promote  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog  # noqa: E402


def _seed_temp_copy(temp_path: Path) -> tuple[dict[str, int], dict[str, int]]:
    """Creates topk_cache on temp_path and populates it via seed_full_
    catalog (decision #6's tie census + seed, one pass). Returns
    (expected_delta, pre_counts) -- expected_delta covers every
    CATALOG_TABLES entry (zero for all 7 pre-existing tables, the real
    observed count for topk_cache); pre_counts is the checkout snapshot
    verify_and_promote needs. Raises topk_cache.TopKTieError uncaught
    if any tie is found."""
    with connection_context(str(temp_path)) as conn:
        create_topk_cache_table(conn)
        pre_counts = catalog_checkout(conn)

    _catalog_path, all_metadata, historical_windows, _labels = load_full_catalog(temp_path)
    log.info("Loaded %d patterns from temp copy for seeding", len(all_metadata))

    seed_result = topk_cache.seed_full_catalog(all_metadata, historical_windows)
    all_rows = [row for rows in seed_result.values() for row in rows]

    with connection_context(str(temp_path)) as conn:
        insert_topk_rows_batch(conn, all_rows)
        conn.commit()

    expected_delta = {t: 0 for t in CATALOG_TABLES if t != "topk_cache"}
    expected_delta["topk_cache"] = len(all_rows)
    log.info(
        "Seeded topk_cache: %d patterns, %d total rows (%.1f rows/pattern avg)",
        len(seed_result), len(all_rows),
        len(all_rows) / len(seed_result) if seed_result else 0.0,
    )
    return expected_delta, pre_counts


def run_migration(live_catalog_path: Path | None = None) -> Path:
    """Full decision #6 cycle: copy live -> seed the copy -> verify ->
    atomic_move. Returns the (unchanged-path) live catalog on success."""
    resolved_live_path = Path(live_catalog_path) if live_catalog_path else Path(get_latest_catalog())
    temp_path = resolved_live_path.with_name(
        resolved_live_path.stem + ".topk_migration_tmp" + resolved_live_path.suffix
    )
    log.info("Live catalog:  %s", resolved_live_path)
    log.info("Temp copy:     %s", temp_path)
    shutil.copy2(resolved_live_path, temp_path)

    expected_delta, pre_counts = _seed_temp_copy(temp_path)

    result = verify_and_promote(temp_path, resolved_live_path, expected_delta, pre_counts)
    if not result.passed:
        log.error("Migration verification FAILED: %s", result.failures)
        log.error("Temp copy left at %s for inspection. Live catalog untouched.", temp_path)
        sys.exit(2)

    log.info(
        "Migration complete. live=%s backup=%s post_counts=%s",
        resolved_live_path, result.backup_path, result.post_counts,
    )
    return resolved_live_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage 4a -- add topk_cache table to the live catalog."
    )
    parser.add_argument(
        "--live-db", type=str, default=None,
        help="Override the live catalog path (default: get_latest_catalog()).",
    )
    args = parser.parse_args()

    log.info("Stage 4a: add topk_cache (WO-P300-E4.006)")
    live_path = Path(args.live_db) if args.live_db else None
    run_migration(live_path)


if __name__ == "__main__":
    main()
