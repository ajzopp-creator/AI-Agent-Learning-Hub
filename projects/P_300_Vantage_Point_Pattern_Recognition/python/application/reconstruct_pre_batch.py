"""
FILE: reconstruct_pre_batch.py
VERSION: 1.0
DATE: 2026-07-23
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    WO-P300-E5.004 Part A (candidate 2). Orchestrates reconstructing a
    full WalkForwardBatch for a catalog from topk_cache instead of a
    fresh O(N^2) serial DTW pass (domain.eval_scoring.run_walk_forward
    with a cold cache -- WO-P300-E5.004's original incident, ~24h at
    N=14,812). Reuses infrastructure.eval_io.load_full_catalog and
    infrastructure.topk_cache_io.bulk_load_topk_cache exactly as-is --
    the latter is already proven at full-catalog scale (this morning's
    real promote log: "Bulk-loaded topk_cache for 10751 patterns
    (10757 requested)").

    Real, unexpected gaps (domain.reconstruct_from_topk.classify_topk_
    gap() returns "gap", not "degenerate") get a fresh per-pattern DTW
    score via domain.eval_scoring.score_one() -- cheap for a handful of
    patterns, not a reason to fall back to the full rescore for the
    whole catalog. TopkCacheReconstructionNotViable is raised only when
    reconstruction genuinely cannot proceed (topk_cache table missing
    entirely) -- callers (application/ingest_mined_pipeline.py) catch
    this and fall through to the existing confirm-gated full rescore.

    Layer rules: application/ = orchestration only, calls domain +
    infrastructure in sequence, no raw logic of its own beyond
    assembling the WalkForwardBatch and sorting results back into
    anchor_date order (run_walk_forward's own ordering contract).

CHANGELOG:
    - 2026-07-23 v1.0: WO-P300-E5.004 Part A. Initial release.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain.eval_scoring import score_one  # noqa: E402
from domain.reconstruct_from_topk import (  # noqa: E402
    classify_topk_gap, score_one_from_topk_cache,
)
from infrastructure.eval_io import load_full_catalog  # noqa: E402
from infrastructure.topk_cache_io import bulk_load_topk_cache  # noqa: E402
from schemas_eval import ThresholdOverrides, WalkForwardBatch  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402

logger = logging.getLogger(__name__)


class TopkCacheReconstructionNotViable(Exception):
    """Raised when reconstruction cannot proceed at all -- topk_cache
    table missing entirely. Caller (ingest_mined_pipeline.py's
    _run_pre_batch) catches this and falls through to the existing
    confirm-gated full DTW rescore. NOT raised for real per-pattern
    gaps (see domain.reconstruct_from_topk.classify_topk_gap) -- those
    get a cheap per-pattern fresh score instead, handled inline here.
    """


def _topk_cache_table_exists(conn) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='topk_cache'"
    )
    return cur.fetchone() is not None


def reconstruct_pre_batch_from_topk_cache(
    catalog_path: str | Path,
    threshold_overrides: ThresholdOverrides | None = None,
) -> WalkForwardBatch:
    """Reconstructs a full WalkForwardBatch for catalog_path, reading
    topk_cache per pattern instead of running domain.eval_scoring.
    run_walk_forward()'s fresh DTW pass. Output shape matches
    run_walk_forward()'s exactly (same WalkForwardBatch/WalkForwardResult
    contract, same anchor_date ordering) so callers -- and the existing
    walk-forward JSON cache write/read path -- need no changes to accept
    a batch produced this way.

    Raises:
        TopkCacheReconstructionNotViable if the topk_cache table does
        not exist at all. Real per-pattern gaps (table exists, some
        pids missing rows despite a real corpus) are handled inline
        via a fresh domain.eval_scoring.score_one() call for just
        those pids -- not a reason to raise.
    """
    resolved_path, all_metadata, all_windows, all_labels = load_full_catalog(
        str(catalog_path)
    )
    all_pids = list(all_metadata.keys())

    with connection_context(str(catalog_path)) as conn:
        if not _topk_cache_table_exists(conn):
            raise TopkCacheReconstructionNotViable(
                f"topk_cache table does not exist in {catalog_path}"
            )
        topk_by_pid = bulk_load_topk_cache(conn, all_pids)

    # Precompute corpus_size for every pid in O(N log N), not the naive
    # O(N^2) nested-loop version -- at N=14,812 that would cost real
    # seconds in pure Python, undermining the entire point of this file.
    # Group by anchor_date, sort distinct dates once, cumulative count
    # strictly before each date.
    dates_seen: dict = {}
    for pid in all_pids:
        d = all_metadata[pid].anchor_date
        dates_seen[d] = dates_seen.get(d, 0) + 1
    cumulative_before: dict = {}
    running = 0
    for d in sorted(dates_seen):
        cumulative_before[d] = running
        running += dates_seen[d]

    results = []
    gap_pids: list[int] = []
    for pid in all_pids:
        corpus_size = cumulative_before[all_metadata[pid].anchor_date]
        matches = topk_by_pid.get(pid, [])
        status = classify_topk_gap(corpus_size, matches)
        if status == "gap":
            gap_pids.append(pid)
            continue
        results.append(
            score_one_from_topk_cache(
                pid, all_metadata, all_labels, matches, threshold_overrides,
            )
        )

    if gap_pids:
        logger.warning(
            "reconstruct_pre_batch_from_topk_cache: %d pid(s) had a real "
            "topk_cache gap (non-empty corpus, zero cached rows) -- "
            "scored fresh via domain.eval_scoring.score_one() instead of "
            "guessing: %s",
            len(gap_pids), gap_pids,
        )
        for pid in gap_pids:
            results.append(
                score_one(
                    pid, all_metadata, all_windows, all_labels,
                    threshold_overrides,
                )
            )

    results.sort(key=lambda r: all_metadata[r.pattern_instance_id].anchor_date)
    n_degenerate = sum(1 for r in results if r.degenerate_corpus)

    return WalkForwardBatch(
        catalog_path=resolved_path,
        n_patterns=len(results),
        n_degenerate=n_degenerate,
        threshold_overrides=threshold_overrides,
        results=results,
    )
