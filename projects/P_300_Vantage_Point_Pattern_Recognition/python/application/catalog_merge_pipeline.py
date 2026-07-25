"""
FILE: application/catalog_merge_pipeline.py
VERSION: 1.3
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Orchestration for WO-P300-E2.003: reads STRICT-tier patterns from
    the research catalog (bulk_research.db), merges them into a STAGING
    COPY of the live catalog (never the real catalog.db directly -- see
    decision 2), and runs the Stage 6 walk-forward eval against both the
    untouched live catalog (baseline) and the staging copy (post-merge)
    so the comparison is a real result to review, not a mid-build gate.

    promote_staging_to_live() is a SEPARATE function, never called by
    build_staging_merge() -- promoting to the real catalog.db is an
    explicit, later action (cli.py's --promote flag), matching this
    project's established "ships off, flip explicitly" governance
    pattern (CE_GATE_ENABLED, NARRATOR_ENABLED).

    promote_staging_to_live() is GENERIC -- it promotes whatever
    validated staging DB is handed to it, regardless of source. Both
    this file's own build_staging_merge() (bulk_research.db merges)
    and application/ingest_mined_pipeline.py (mined-candidate CSV
    approvals) produce a staging DB and share this one go-live step.
    That genericity is why WO-P300-E4.006's new-batch topk population
    (decision #6/#10) DERIVES new_pids here by diffing staging against
    live, rather than receiving it as a parameter -- neither upstream
    caller's new_pids set is naturally available at this call site, and
    adding one would mean two different signatures for the two callers
    of a function whose whole point is being caller-agnostic.

CHANGELOG:
    - 2026-07-20 v1.3 (WO-P300-E4.002, M-095): both get_latest_catalog()
      call sites (build_staging_merge, promote_staging_to_live) migrated
      from the manually-wrapped Path(get_latest_catalog()) form to the new
      Path-typed get_latest_catalog_path() -- same behavior, no longer
      dependent on remembering the wrap by hand (that convention already
      failed here once, v1.1 above). Import updated accordingly.
    - 2026-07-19 v1.2 (WO-P300-E4.006, decisions #6/#7/#10): promote_
      staging_to_live() rewritten -- raw catalog_checkout/catalog_
      checkin replaced with verify_ingestion.verify_and_promote()
      (this was the E5.002 gap: zero per-table delta validation
      happened on any real promote before this). new_pids derived by
      diffing staging's pattern_instance_id set against live's (this
      function receives neither pipeline's new_pids directly -- see
      module docstring). New-pattern topk population and existing-pid
      cache updates happen on the STAGING copy before verify_and_
      promote's atomic_move, same Lock+Temp-DB+Atomic-Move cycle every
      other catalog write uses (decision #6). expected_delta's
      topk_cache count is computed from what update_for_new_batch
      ACTUALLY returned, not assumed as 20*len(new_pids) -- patterns
      early in a symbol's history can have fewer than 20 corpus
      candidates, so a fixed-formula delta would be wrong for thin
      corpora. check_topk_cache deliberately NOT passed to verify_and_
      promote (stays default False) -- the hollow-topk check has a
      false-positive edge case for genuinely degenerate-corpus
      patterns that the exact expected_delta check doesn't share.
      TopKTieError propagates uncaught if raised -- promote halts
      before atomic_move, never partially promotes (decision #9
      philosophy applied here too).
    - 2026-07-14 v1.1: Both get_latest_catalog() call sites (build_staging_merge
      line ~124, promote_staging_to_live line ~178) wrapped in Path() -- neither
      was, both are the M-089 str-vs-Path pattern recurring. Found live, during
      WO-P300-E3.002's first real production promote: promote_staging_to_live
      crashed ('str' object has no attribute 'exists') the first time it was ever
      called with no explicit --live-db, because atomic_move() calls .exists() on
      it and shutil.copy2/load_full_catalog (which tolerated the bug in
      build_staging_merge, masking it) don't. Real live catalog.db confirmed
      untouched (mtime unchanged) -- crash happened before any write.
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.003 file #5 of 7).
"""
from __future__ import annotations

import logging
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from application.promote_topk import populate_topk_for_promote  # noqa: E402
from config import BULK_FEATURE_VERSION, BULK_RESEARCH_DB, BULK_TIER_STRICT  # noqa: E402
from domain.eval_scoring import run_walk_forward  # noqa: E402
from infrastructure.catalog_merge_io import (  # noqa: E402
    MergeSummary,
    RawBulkBar,
    ensure_feature_set,
    merge_one_pattern,
)
from infrastructure.catalog_writer import catalog_checkout  # noqa: E402
from infrastructure.eval_io import load_full_catalog, write_walk_forward_report  # noqa: E402
from infrastructure.verify_ingestion import verify_and_promote  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog_path  # noqa: E402

logger = logging.getLogger(__name__)


@dataclass
class MergeResult:
    live_catalog_path: Path
    staging_path: Path
    merge: MergeSummary
    pre_report_path: Path
    post_report_path: Path


def _load_strict_bulk_patterns(research_conn: sqlite3.Connection) -> list[dict]:
    """One pass over the research catalog's STRICT-tier patterns,
    returning everything merge_one_pattern needs per pattern, already
    shaped. Read-only against bulk_research.db throughout."""
    rows = research_conn.execute(
        "SELECT pi.pattern_instance_id, s.ticker, sf.filename, sf.imported_at, "
        "sf.row_count, pi.anchor_date "
        "FROM pattern_instances pi "
        "JOIN symbols s ON s.symbol_id = pi.symbol_id "
        "JOIN source_files sf ON sf.source_file_id = pi.source_file_id "
        "WHERE pi.detection_tier = ?",
        (BULK_TIER_STRICT,),
    ).fetchall()

    patterns = []
    for pid, ticker, filename, imported_at, row_count, anchor_date in rows:
        bar_rows = research_conn.execute(
            "SELECT bar_date, open, high, low, close, volume, stdiff, mtdiff, "
            "ltdiff, pred_high, pred_low, pred_range, williams_emai, psi, "
            "neural_x_max FROM pattern_bars WHERE pattern_instance_id = ? "
            "ORDER BY bar_offset ASC",
            (pid,),
        ).fetchall()
        label_rows = research_conn.execute(
            "SELECT horizon_days, future_date, return_pct, is_profitable "
            "FROM forward_labels WHERE pattern_instance_id = ?",
            (pid,),
        ).fetchall()
        patterns.append({
            "ticker": ticker, "source_filename": filename,
            "source_imported_at": datetime.fromisoformat(imported_at),
            "source_row_count": row_count,
            "anchor_date": datetime.fromisoformat(anchor_date).date(),
            "raw_bars": [
                RawBulkBar(
                    bar_date=datetime.fromisoformat(r[0]).date(),
                    open=r[1], high=r[2], low=r[3], close=r[4], volume=r[5],
                    stdiff=r[6], mtdiff=r[7], ltdiff=r[8],
                    pred_high=r[9], pred_low=r[10], pred_range=r[11],
                    williams_emai=r[12], psi=r[13], neural_x_max=r[14],
                )
                for r in bar_rows
            ],
            "forward_labels": [
                (h, datetime.fromisoformat(fd).date(), rp, bool(ip))
                for h, fd, rp, ip in label_rows
            ],
        })
    return patterns


def build_staging_merge(
    staging_path: Path,
    live_catalog_path: Path | None = None,
    research_db_path: Path = BULK_RESEARCH_DB,
) -> MergeResult:
    """Copies the live catalog to staging_path, merges every STRICT bulk
    pattern into the copy, runs the walk-forward eval against BOTH the
    untouched live catalog (pre) and staging_path (post), writes both
    reports. Never writes to the real live catalog.db."""
    resolved_live_path = Path(live_catalog_path) if live_catalog_path else get_latest_catalog_path()
    shutil.copy2(resolved_live_path, staging_path)

    with sqlite3.connect(str(research_db_path)) as research_conn:
        patterns = _load_strict_bulk_patterns(research_conn)
    logger.info("Loaded %d STRICT bulk patterns from research catalog", len(patterns))

    summary = MergeSummary()
    with connection_context(str(staging_path)) as conn:
        feature_set_id = ensure_feature_set(
            conn, BULK_FEATURE_VERSION,
            "Bulk-scan features, merged from research_catalog.db (WO-P300-E2.003).",
        )
        for p in patterns:
            new_id = merge_one_pattern(
                conn, p["ticker"], p["source_filename"], p["source_imported_at"],
                p["source_row_count"], p["anchor_date"], p["raw_bars"],
                p["forward_labels"], feature_set_id,
            )
            if new_id is None:
                summary.skipped_duplicate_count += 1
            else:
                summary.inserted_count += 1
                summary.symbols_touched.add(p["ticker"])

    pre_catalog_path, pre_meta, pre_win, pre_lab = load_full_catalog(resolved_live_path)
    pre_batch = run_walk_forward(pre_catalog_path, pre_meta, pre_win, pre_lab)
    pre_report_path = write_walk_forward_report(pre_batch)

    post_catalog_path, post_meta, post_win, post_lab = load_full_catalog(staging_path)
    post_batch = run_walk_forward(post_catalog_path, post_meta, post_win, post_lab)
    post_report_path = write_walk_forward_report(post_batch)

    logger.info(
        "Merge complete: %d inserted, %d skipped (duplicate). "
        "Pre-merge n_patterns=%d, post-merge n_patterns=%d.",
        summary.inserted_count, summary.skipped_duplicate_count,
        pre_batch.n_patterns, post_batch.n_patterns,
    )
    return MergeResult(
        live_catalog_path=resolved_live_path, staging_path=staging_path,
        merge=summary, pre_report_path=pre_report_path,
        post_report_path=post_report_path,
    )


def promote_staging_to_live(
    staging_path: Path, live_catalog_path: Path | None = None,
) -> Path:
    """Explicit promotion of a validated staging copy to the real live
    catalog.db via verify_ingestion.verify_and_promote() -- the SAME
    Lock+Temp-DB+Atomic Move protocol every other catalog write in this
    project uses (decision #10: this function previously bypassed it,
    doing its own unchecked checkout/atomic_move/checkin with no
    expected_delta at all -- WO-P300-E5.002's gap, closed here).

    new_pids is derived by diffing staging's pattern_instance_id set
    against live's (see module docstring for why this isn't a
    parameter). If new_pids is non-empty, topk_cache gets populated on
    staging BEFORE the atomic_move (decision #6). check_topk_cache is
    deliberately NOT passed (stays verify_and_promote's default False)
    -- _check_no_hollow_topk can't distinguish a genuinely degenerate-
    corpus pattern (anchor_date earlier than everything else in the
    catalog, legitimately zero topk_cache rows) from a real population
    bug, so it has a false-positive edge case this promote path
    doesn't need: expected_delta's exact, actual-count-based check
    (populate_topk_for_promote) already catches real population
    failures without that risk. topk_cache.TopKTieError propagates
    uncaught if raised -- the promote halts before atomic_move, never
    partially promotes."""
    resolved_live_path = Path(live_catalog_path) if live_catalog_path else get_latest_catalog_path()

    with connection_context(str(resolved_live_path)) as conn:
        pre_counts = catalog_checkout(conn)
        live_pids = {
            r[0] for r in conn.execute("SELECT pattern_instance_id FROM pattern_instances")
        }
    with connection_context(str(staging_path)) as conn:
        staging_pids = {
            r[0] for r in conn.execute("SELECT pattern_instance_id FROM pattern_instances")
        }
    new_pids = staging_pids - live_pids

    expected_delta: dict[str, int] = {}
    if new_pids:
        expected_delta = populate_topk_for_promote(staging_path, new_pids)

    result = verify_and_promote(
        staging_path, resolved_live_path, expected_delta, pre_counts,
    )
    if not result.passed:
        raise RuntimeError(
            f"Promote verification failed for {staging_path} -> "
            f"{resolved_live_path}: {result.failures}"
        )
    logger.info(
        "Promoted staging -> live catalog. live=%s backup=%s post_counts=%s",
        resolved_live_path, result.backup_path, result.post_counts,
    )
    return resolved_live_path
