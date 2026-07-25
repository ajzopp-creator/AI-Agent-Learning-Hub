"""
FILE: application/incremental_post_batch.py
VERSION: 2.0
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Orchestration seam for the post-batch walk-forward eval report.
    v1.x tried domain/eval_incremental.py's assemble_incremental_
    post_batch() behind a reuse-fraction "worth it" gate, falling back
    to a full domain/eval_scoring.py run_walk_forward() rescore either
    below that threshold or on IncrementalGuardrailError. WO-P300-
    E4.006 (decision #9) removes all of that: the top-K cache path
    (domain/eval_incremental.py's run_cached_post_batch(), v2.0 of
    that file) is unconditional -- there is no "worth it" decision
    left to gate, and no fallback swallowing IncrementalGuardrailError
    or topk_cache.TopKTieError. Both propagate uncaught; a WARNING is
    still logged first so neither is silent, but nothing here catches
    and retries with a different code path.

    Loads existing_cache from catalog_path itself (the STAGING
    catalog) rather than a separate query: staging is a file copy of
    the live catalog made before this batch's inserts (application/
    ingest_mined_pipeline.py's own flow), so it already carries the
    pre-insert topk_cache rows for every EXISTING pattern -- no
    separate live-catalog read needed.

    Kept out of application/ingest_mined_pipeline.py (that file is at
    the exact 300-line hard cap, decision #10's other finding) -- this
    remains the one seam that owns the incremental-path call, per
    Process Boundary Standard (application/ = orchestration only).

CHANGELOG:
    - 2026-07-19 v2.0 (WO-P300-E4.006, decision #9): Removed the
      reuse-fraction gate, INCREMENTAL_MIN_REUSE_FRACTION, the
      IncrementalGuardrailError try/except, and both run_walk_forward
      fallback call sites -- vestigial once the cached path is
      unconditional. Added existing_cache loading via infrastructure/
      topk_cache_io.py and the call to eval_incremental.run_cached_
      post_batch (v2.0) in place of assemble_incremental_post_batch.
      Net effect: this file shrank (~115 -> ~65 lines), not grew.
    - 2026-07-19 v1.3: reuse-fraction-skip log message fix (parallel
      vs serial flag reporting).
    - 2026-07-18 v1.2: Added the reuse-fraction "worth it" threshold.
    - 2026-07-17 v1.1 (M-100): docstring update for eval_incremental
      v1.1's min-new-date partition.
    - 2026-07-17 v1.0: WO-P300-E4.004. Initial release.
"""
from __future__ import annotations

import logging

from domain.eval_incremental import IncrementalGuardrailError, run_cached_post_batch
from domain.topk_cache import TopKTieError
from infrastructure.catalog_reader import PatternMetadata
from infrastructure.topk_cache_io import bulk_load_topk_cache
from schemas_eval import ThresholdOverrides, WalkForwardBatch
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar
from utilities.db_connect import connection_context

logger = logging.getLogger(__name__)


def run_incremental_post_batch(
    catalog_path: str,
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    new_pids: set[int],
    pre_batch: WalkForwardBatch,
    threshold_overrides: ThresholdOverrides | None = None,
) -> WalkForwardBatch:
    """The ONE post-batch path (decision #1/#9) -- unconditional, no
    reuse-fraction gate, no fallback. IncrementalGuardrailError and
    topk_cache.TopKTieError both propagate to the caller uncaught
    (logged at WARNING first so neither is silent); this function
    does not retry with a different code path on either.

    catalog_path is the STAGING catalog (post-insert, pre-promote) --
    existing_cache is loaded from it directly, since staging already
    carries every existing pattern's pre-insert topk_cache rows (a
    file copy of live made before this batch's inserts).
    """
    existing_pids = [pid for pid in all_metadata if pid not in new_pids]
    with connection_context(catalog_path=catalog_path) as conn:
        existing_cache = bulk_load_topk_cache(conn, existing_pids)

    try:
        batch, _new_topk, _existing_topk = run_cached_post_batch(
            catalog_path, all_metadata, historical_windows, all_labels,
            new_pids, pre_batch, existing_cache, threshold_overrides,
        )
    except (IncrementalGuardrailError, TopKTieError):
        logger.warning(
            "run_cached_post_batch raised for catalog_path=%s, "
            "new_pids=%d -- propagating, no fallback (decision #9).",
            catalog_path, len(new_pids),
        )
        raise
    return batch
