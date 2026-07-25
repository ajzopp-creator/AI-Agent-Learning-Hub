"""
FILE: application/promote_topk.py
VERSION: 1.0
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Topk_cache population for the promote-to-live step (WO-P300-
    E4.006, decisions #6/#10). Split out of application/catalog_merge_
    pipeline.py rather than added inline there -- a real Process
    Boundary Standard reason to change, not just a line-count
    workaround: this logic applies to ANY promote regardless of which
    upstream pipeline produced the staging DB (catalog_merge_pipeline.
    py's bulk-research merges, or application/ingest_mined_pipeline.
    py's mined-candidate ingests), while catalog_merge_pipeline.py's
    own reason to change is specifically STRICT-tier bulk merge
    orchestration. (catalog_merge_pipeline.py was also at 312/300
    lines with this inlined -- the split fixes both concerns at once,
    but the boundary reasoning came first.)

    Runs domain/topk_cache.py's update_for_new_batch against a STAGING
    catalog copy and writes the results there, BEFORE the caller's
    verify_and_promote/atomic_move -- decision #6's one-cycle rule:
    schema creation, population, and the eventual atomic swap all
    happen on the private copy first, never in two separate cycles.

    Layer rules: application/ = orchestration only (calls domain +
    infrastructure in sequence), no raw logic of its own beyond
    assembling the expected_delta.

CHANGELOG:
    - 2026-07-19 v1.0: WO-P300-E4.006. Initial release.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain import topk_cache  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402
from infrastructure.topk_cache_io import (  # noqa: E402
    bulk_load_topk_cache,
    create_topk_cache_table,
    delete_topk_rows_for_pattern,
    insert_topk_rows_batch,
)
from utilities.db_connect import connection_context  # noqa: E402

logger = logging.getLogger(__name__)


def populate_topk_for_promote(
    staging_path: Path,
    new_pids: set[int],
) -> dict[str, int]:
    """Runs update_for_new_batch against the STAGING copy and writes
    the results there, before the caller's atomic_move (decision #6).

    Returns an expected_delta dict for topk_cache only, computed from
    the ACTUAL row counts update_for_new_batch produced -- not assumed
    as 20*len(new_pids), since patterns early in a symbol's history
    can have fewer than TOP_K_MATCHES corpus candidates, so a
    fixed-formula delta would be wrong for thin corpora.

    Raises:
        topk_cache.TopKTieError if update_for_new_batch finds an exact
        tie at the top-K boundary -- propagates uncaught, matching
        Finding 3's STOP-and-report rule; the caller's promote must
        halt before atomic_move, never partially promote.
    """
    staging_catalog_path, staging_meta, staging_win, _lab = load_full_catalog(staging_path)
    existing_pids = [pid for pid in staging_meta if pid not in new_pids]

    with connection_context(str(staging_path)) as conn:
        create_topk_cache_table(conn)
        existing_cache = bulk_load_topk_cache(conn, existing_pids)

    new_pid_topk, existing_must_check_topk = topk_cache.update_for_new_batch(
        new_pids, staging_meta, staging_win, existing_cache,
    )

    old_existing_total = sum(
        len(existing_cache.get(pid, [])) for pid in existing_must_check_topk
    )
    new_existing_total = sum(len(v) for v in existing_must_check_topk.values())
    new_pid_total = sum(len(v) for v in new_pid_topk.values())
    topk_delta = new_pid_total + (new_existing_total - old_existing_total)

    with connection_context(str(staging_path)) as conn:
        for pid in existing_must_check_topk:
            delete_topk_rows_for_pattern(conn, pid)
        all_rows = [
            row
            for rows in (*new_pid_topk.values(), *existing_must_check_topk.values())
            for row in rows
        ]
        insert_topk_rows_batch(conn, all_rows)
        conn.commit()

    logger.info(
        "topk_cache populated on staging: %d new pids, %d existing pids "
        "rechecked, net delta=%+d",
        len(new_pid_topk), len(existing_must_check_topk), topk_delta,
    )
    return {"topk_cache": topk_delta}
