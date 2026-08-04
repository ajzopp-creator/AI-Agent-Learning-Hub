"""
FILE: topk_cache.py
VERSION: 1.1
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Admission logic for the top-K state cache (WO-P300-E4.006, lever
    #3). Replaces domain/eval_incremental.py's assemble_incremental_
    post_batch as the ONE incremental post-batch path (decision #1) --
    that module's IncrementalGuardrailError and its fallback are NOT
    used here; this file's failure mode is different (TopKTieError
    below) and is NOT a fallback trigger -- it propagates, per
    Finding 3's own rule (STOP, report back, no silent tiebreak fix).

    Two entry points:
      - seed_full_catalog(): ONE-TIME O(N^2) initial population, run
        by migrations/stage_4a_add_topk_cache.py against a full live
        catalog copy (decision #6). Also IS Finding 3's tie census --
        the same O(N^2) pass proves zero ties exist at the top-K
        boundary across the full catalog before the cache goes live.
      - update_for_new_batch(): the ongoing per-batch path, wired into
        application/catalog_merge_pipeline.py's promote_staging_to_
        live() (decision #10). Reuses domain/eval_incremental.py's
        _partition_unaffected() verbatim (M-082, not re-derived) to
        skip existing pids that provably can't be displaced, then
        applies a tighter per-pattern anchor_date filter (decision #3)
        before any distance computation.

    K is exact at TOP_K_MATCHES=20, no headroom (decision #4) -- a
    future TOP_K_MATCHES change requires re-running seed_full_catalog,
    not a headroom buffer here.

    Layer rules: no file/DB/network I/O, no logging (domain/ pure
    logic only -- infrastructure/topk_cache_io.py owns all SQLite
    reads/writes for this table).

CHANGELOG:
    - 2026-07-29 v1.1 (WO-P300-E5.005 item #1): update_for_new_batch
      gained an optional progress_callback param, invoked from two new
      private helpers (_compute_new_pid_topk, _compute_existing_
      recheck_topk -- split out of update_for_new_batch's own body to
      stay under the 50-line function cap). Domain stays I/O-free --
      the callback is caller-supplied; this file still does no logging
      of its own. Default None, so every existing caller (including
      seed_full_catalog, which is unaffected) behaves exactly as before.
    - 2026-07-19 v1.0: WO-P300-E4.006. Initial release.
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import TOP_K_MATCHES  # noqa: E402
from domain import similarity  # noqa: E402
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_eval import TopKMatch  # noqa: E402
from schemas_pipeline_b import NormalizedBar  # noqa: E402

# _partition_unaffected is imported LAZILY inside update_for_new_batch,
# not here at module level: domain/eval_incremental.py imports THIS
# module (topk_cache) for update_for_new_batch, so a top-level import
# in the other direction would be circular -- eval_incremental would
# fail to finish defining _partition_unaffected before this module's
# own top-level import tried to pull it in. Deferred import breaks the
# load-time cycle; by call time both modules are fully initialized.


class TopKTieError(Exception):
    """Exact composite_distance tie at the top-K boundary. Finding 3's
    rule: STOP and report, never silently resolved -- raised at both
    the one-time seed census (seed_full_catalog) and any later batch's
    displacement check (update_for_new_batch / _displace); same
    failure class, two call sites, always propagates."""


def _corpus_pids_before(
    pid: int,
    all_metadata: dict[int, PatternMetadata],
    candidate_pool: set[int] | None = None,
) -> list[int]:
    """Every pid with anchor_date strictly earlier than `pid`'s own,
    restricted to candidate_pool if given. Same date-strictness rule
    as domain/eval_scoring.py's _corpus_pids -- kept local rather than
    imported because that function has no pool-restriction parameter
    and adding one there would touch a file this WO doesn't otherwise
    need to modify.
    """
    target_date = all_metadata[pid].anchor_date
    pool = candidate_pool if candidate_pool is not None else set(all_metadata)
    return [
        other for other in pool
        if other != pid and all_metadata[other].anchor_date < target_date
    ]


def _rank_topk(
    pid: int,
    candidate_pids: list[int],
    historical_windows: dict[int, list[NormalizedBar]],
) -> list[TopKMatch]:
    """Score `pid` against candidate_pids via similarity.rank_by_
    distance (reused, not reimplemented), slice to TOP_K_MATCHES,
    raise TopKTieError if the Kth and (K+1)th distances are exactly
    equal (ambiguous boundary -- which one is "in" the top-20 is not
    well-defined)."""
    if not candidate_pids:
        return []
    windows = {p: historical_windows[p] for p in candidate_pids}
    ranked = similarity.rank_by_distance(historical_windows[pid], windows)
    if len(ranked) > TOP_K_MATCHES:
        boundary_dist = ranked[TOP_K_MATCHES - 1][1]
        next_dist = ranked[TOP_K_MATCHES][1]
        if boundary_dist == next_dist:
            raise TopKTieError(
                f"pid={pid}: exact tie at rank {TOP_K_MATCHES} boundary "
                f"(distance={boundary_dist})"
            )
    return [
        TopKMatch(
            pattern_instance_id=pid, rank=i + 1,
            matched_pid=matched_pid, composite_distance=dist,
        )
        for i, (matched_pid, dist, _per_feat) in enumerate(ranked[:TOP_K_MATCHES])
    ]


def seed_full_catalog(
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
) -> dict[int, list[TopKMatch]]:
    """ONE-TIME O(N^2) seed + Finding 3's tie census combined (decision
    #6 -- one pass gets both). Every pid's top-K computed against its
    full anchor_date-restricted corpus. Raises TopKTieError on the
    first tie found anywhere in the catalog -- migrations/stage_4a_
    add_topk_cache.py must not catch this; a tie here means the whole
    migration stops (Finding 3's rule), not a per-pattern skip."""
    result: dict[int, list[TopKMatch]] = {}
    for pid in all_metadata:
        corpus = _corpus_pids_before(pid, all_metadata)
        result[pid] = _rank_topk(pid, corpus, historical_windows)
    return result


def _displace(
    current: list[TopKMatch],
    pattern_instance_id: int,
    candidate_pid: int,
    candidate_dist: float,
) -> list[TopKMatch]:
    """O(K) admission check against the current worst (last) entry.
    current must already be sorted ascending by composite_distance,
    length <= TOP_K_MATCHES. Returns a new list -- current is not
    mutated. Raises TopKTieError on exact equality with the worst
    slot (ambiguous which one belongs in the top-20)."""
    if len(current) < TOP_K_MATCHES:
        updated = current + [TopKMatch(
            pattern_instance_id=pattern_instance_id, rank=len(current) + 1,
            matched_pid=candidate_pid, composite_distance=candidate_dist,
        )]
    else:
        worst = current[-1]
        if candidate_dist == worst.composite_distance:
            raise TopKTieError(
                f"pid={pattern_instance_id}: candidate {candidate_pid} ties "
                f"current worst slot at distance={candidate_dist}"
            )
        if candidate_dist >= worst.composite_distance:
            return current
        updated = current[:-1] + [TopKMatch(
            pattern_instance_id=pattern_instance_id, rank=TOP_K_MATCHES,
            matched_pid=candidate_pid, composite_distance=candidate_dist,
        )]
    updated.sort(key=lambda m: m.composite_distance)
    return [m.model_copy(update={"rank": i + 1}) for i, m in enumerate(updated)]


def _compute_new_pid_topk(
    new_pids: set[int],
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    progress_callback: Callable[[int, int, str], None] | None,
) -> dict[int, list[TopKMatch]]:
    """Top-K for every newly-added pid, against its full anchor_date-
    restricted corpus. Split out of update_for_new_batch to keep that
    function under the 50-line cap while adding progress_callback
    support (WO-P300-E5.005 item #1)."""
    new_pid_list = list(new_pids)
    result: dict[int, list[TopKMatch]] = {}
    for i, pid in enumerate(new_pid_list, start=1):
        result[pid] = _rank_topk(
            pid, _corpus_pids_before(pid, all_metadata), historical_windows,
        )
        if progress_callback is not None:
            progress_callback(i, len(new_pid_list), "new_pids")
    return result


def _compute_existing_recheck_topk(
    existing_must_check: list[int],
    new_pids: set[int],
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    existing_cache: dict[int, list[TopKMatch]],
    progress_callback: Callable[[int, int, str], None] | None,
) -> dict[int, list[TopKMatch]]:
    """Re-rank every existing pid whose corpus grew (must_check),
    displacing into its cached top-20 wherever a new pid scores
    better. Split out of update_for_new_batch for the same reason as
    _compute_new_pid_topk above -- this is the loop that actually
    takes over an hour on a large batch, so it's also the one that
    matters most for progress visibility."""
    result: dict[int, list[TopKMatch]] = {}
    for i, pid in enumerate(existing_must_check, start=1):
        pid_date = all_metadata[pid].anchor_date
        qualifying_new = [p for p in new_pids if all_metadata[p].anchor_date < pid_date]
        current = existing_cache.get(pid, [])
        windows = {p: historical_windows[p] for p in qualifying_new}
        ranked = similarity.rank_by_distance(historical_windows[pid], windows) if qualifying_new else []
        for matched_pid, dist, _per_feat in ranked:
            current = _displace(current, pid, matched_pid, dist)
        result[pid] = current
        if progress_callback is not None:
            progress_callback(i, len(existing_must_check), "existing_recheck")
    return result


def update_for_new_batch(
    new_pids: set[int],
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    existing_cache: dict[int, list[TopKMatch]],
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> tuple[dict[int, list[TopKMatch]], dict[int, list[TopKMatch]]]:
    """The ongoing per-batch path (decision #3). Returns (new_pid_
    topk, existing_must_check_topk).

    existing_must_check_topk covers EVERY existing pid in must_check --
    not just the ones whose cached top-20 actually changed. This is
    deliberate, not an efficiency miss: every must_check pid's corpus
    grew by at least the earliest new pid (must_check is exactly the
    set with anchor_date > min_new_date, and the earliest new pid is
    by construction strictly earlier than every such pid -- so
    qualifying_new below is never actually empty for a must_check
    pid). catalog_baseline_win_rates() runs over the FULL corpus, not
    the top-20, so it changes for every must_check pid regardless of
    whether displacement touched their cache -- a caller recomputing
    WalkForwardResult needs all of them, not just the displaced
    subset. (Infrastructure-layer writes may still diff against the
    prior cache to skip unchanged DB rows -- that's a write-efficiency
    concern for topk_cache_io.py, not a correctness concern here.)

    progress_callback: optional (completed, total, phase) -> None,
    invoked from the two private helpers above -- domain stays I/O-
    free, this only ever calls back into whatever the caller supplied,
    never logs or prints itself (WO-P300-E5.005 item #1; the caller,
    application/promote_topk.py, owns the actual logging cadence).
    Default None preserves every existing caller unchanged.
    """
    from domain.eval_incremental import _partition_unaffected  # deferred, breaks circular import (see module note above)

    min_new_date = min(all_metadata[p].anchor_date for p in new_pids)
    _safe, must_check = _partition_unaffected(all_metadata, new_pids, min_new_date)
    existing_must_check = [p for p in must_check if p not in new_pids]

    new_pid_topk = _compute_new_pid_topk(
        new_pids, all_metadata, historical_windows, progress_callback,
    )
    existing_must_check_topk = _compute_existing_recheck_topk(
        existing_must_check, new_pids, all_metadata, historical_windows,
        existing_cache, progress_callback,
    )

    return new_pid_topk, existing_must_check_topk
