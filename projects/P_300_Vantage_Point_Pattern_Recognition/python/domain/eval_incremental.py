"""
FILE: eval_incremental.py
VERSION: 2.0
DATE: 2026-07-19
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    The ONE incremental post-batch path (WO-P300-E4.006, decision #1
    -- replaces v1.x's date-partition reuse outright, not alongside
    it). Walk-forward's corpus for any pattern X is still every
    pattern with a STRICTLY EARLIER anchor_date (domain/eval_scoring.
    py's _corpus_pids) -- that invariant is unchanged. What changed is
    HOW the top-K ranking for affected patterns gets computed: v1.x
    fully rescored every "must_rescore" pid via score_one() (a fresh
    O(corpus_size) similarity pass per pid); v2.0 delegates top-K
    ranking to domain/topk_cache.py's update_for_new_batch(), which
    reuses the SAME min-new-date partition (via _partition_unaffected,
    unchanged from v1.x) but only computes fresh distances for
    genuinely new candidate pairs, not a full corpus rescan for pids
    whose corpus merely grew without their top-20 changing.

    compute_reuse_fraction() and assemble_incremental_post_batch() are
    REMOVED, not left dormant (decision #9) -- both only made sense
    when there was a genuine "attempt incremental, or skip to full
    rescore" decision at the caller. That decision no longer exists:
    the cached path is unconditional (decision #1). IncrementalGuard-
    railError and _validated_pre_results() STAY -- they check that
    pre_batch is a valid superset of what this module marks "safe,"
    an invariant that's still real regardless of how the "must_check"
    set gets scored, and still propagates uncaught on failure (no
    automatic fallback swallows it, matching decision #9's guardrail
    philosophy).

    run_cached_post_batch()'s aggregator/classifier chain reuses
    domain/eval_scoring.py's private helpers directly (_corpus_pids,
    _classify_signal_overridable, _label_correctness) -- same
    cross-file private-function reuse this WO already established for
    _partition_unaffected (M-082): the logic those functions encode
    must not fork into a second copy that can silently drift.

    This file's edits were forced into this shape by a real
    constraint, not chosen freely: domain/eval_scoring.py is at the
    exact 300-line hard cap with zero headroom, so the new orchestration
    could not live there. eval_incremental.py shrinking (vestigial
    removal, decision #9) freed exactly the room needed -- and this is
    also the thematically correct home: it's still "the incremental
    post-batch file," just a different incremental strategy inside it.

    Layer rules: no file/DB/network I/O, no logging.

CHANGELOG:
    - 2026-07-19 v2.0 (WO-P300-E4.006, decisions #1/#3/#9): Removed
      compute_reuse_fraction() and assemble_incremental_post_batch()
      (vestigial once the cached path is unconditional). Added
      run_cached_post_batch() and _result_from_cached_topk() -- the
      new incremental path, delegating top-K ranking to domain/
      topk_cache.py instead of a full score_one() rescan per
      must_check pid. IncrementalGuardrailError, _partition_
      unaffected(), and _validated_pre_results() unchanged -- still
      the correctness backbone for both the min-new-date partition
      and the pre_batch-completeness check.
    - 2026-07-18 v1.2: Added compute_reuse_fraction().
    - 2026-07-17 v1.1 (M-100): min-new-date partition replaces the
      same-day-only guardrail.
    - 2026-07-17 v1.0: WO-P300-E4.004. Initial release.
"""
from __future__ import annotations

from domain import aggregator, topk_cache
from domain.eval_scoring import (
    _classify_signal_overridable, _corpus_pids, _label_correctness,
)
from infrastructure.catalog_reader import PatternMetadata
from schemas_eval import (
    ThresholdOverrides, TopKMatch, WalkForwardBatch, WalkForwardResult,
)
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar


class IncrementalGuardrailError(ValueError):
    """Raised only on a true internal-invariant break -- pre_batch
    doesn't actually contain a pid this module expected to find safe
    to reuse. Not expected in normal operation; propagates uncaught,
    no automatic fallback (decision #9)."""


def _partition_unaffected(
    all_metadata: dict[int, PatternMetadata],
    new_pids: set[int],
    min_new_date,
) -> tuple[list[int], list[int]]:
    """Splits existing (non-new) pids into safe-to-reuse (anchor_date
    <= min_new_date -- no new pid is earlier, corpus unchanged) and
    must-rescore (anchor_date > min_new_date -- at least one new pid
    could join the corpus). must_rescore_pids includes every new pid
    too (never cached)."""
    safe_pids: list[int] = []
    must_rescore_pids: list[int] = list(new_pids)
    for pid, meta in all_metadata.items():
        if pid in new_pids:
            continue
        if meta.anchor_date <= min_new_date:
            safe_pids.append(pid)
        else:
            must_rescore_pids.append(pid)
    return safe_pids, must_rescore_pids


def _validated_pre_results(
    pre_batch: WalkForwardBatch,
    safe_pids: list[int],
) -> dict[int, WalkForwardResult]:
    """pre_batch results keyed by pid. Raises IncrementalGuardrailError
    if any safe_pid is missing from pre_batch -- an internal-invariant
    break (pre_batch should always be a superset of anything this
    module marks safe), not an expected real-world outcome."""
    pre_results_by_pid = {r.pattern_instance_id: r for r in pre_batch.results}
    missing = [pid for pid in safe_pids if pid not in pre_results_by_pid]
    if missing:
        raise IncrementalGuardrailError(
            f"{len(missing)} safe pid(s) not present in pre_batch results "
            f"(e.g. {missing[0]}) -- pre_batch is not a superset of the "
            f"population this module marked safe to reuse"
        )
    return pre_results_by_pid


def _result_from_cached_topk(
    pid: int,
    topk: list[TopKMatch],
    all_metadata: dict[int, PatternMetadata],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    threshold_overrides: ThresholdOverrides | None,
) -> WalkForwardResult:
    """Builds one WalkForwardResult from an already-ranked top-K list
    (domain/topk_cache.py's output) instead of calling similarity.
    rank_by_distance directly. The aggregator/classifier chain is
    otherwise identical to score_one()'s -- including a fresh baseline
    over the pid's FULL corpus, not just its top-20 (corpus_size
    changes for every must_check pid regardless of whether
    displacement touched its cache; see topk_cache.update_for_new_
    batch's docstring)."""
    meta = all_metadata[pid]
    corpus_pids = _corpus_pids(pid, all_metadata)
    corpus_labels = {p: all_labels.get(p, {}) for p in corpus_pids}
    top_k_label_map = {
        m.matched_pid: all_labels.get(m.matched_pid, {}) for m in topk
    }
    baseline = aggregator.catalog_baseline_win_rates(corpus_labels)
    per_horizon_stats = aggregator.aggregate_top_k(top_k_label_map, baseline)
    final_signal, final_horizon = _classify_signal_overridable(
        per_horizon_stats, threshold_overrides,
    )
    actual = all_labels.get(pid, {}).get(final_horizon)
    return WalkForwardResult(
        pattern_instance_id=pid, symbol=meta.ticker, anchor_date=meta.anchor_date,
        corpus_size=len(corpus_pids), degenerate_corpus=len(corpus_pids) == 0,
        signal_class=final_signal, chosen_horizon=final_horizon,
        per_horizon=per_horizon_stats,
        actual_return_pct=actual.return_pct if actual else None,
        actual_is_profitable=actual.is_profitable if actual else None,
        correctness=(
            _label_correctness(final_signal, actual.is_profitable)
            if actual else None
        ),
    )


def run_cached_post_batch(
    catalog_path: str,
    all_metadata: dict[int, PatternMetadata],
    historical_windows: dict[int, list[NormalizedBar]],
    all_labels: dict[int, dict[int, ForwardLabelLite]],
    new_pids: set[int],
    pre_batch: WalkForwardBatch,
    existing_cache: dict[int, list[TopKMatch]],
    threshold_overrides: ThresholdOverrides | None = None,
) -> tuple[WalkForwardBatch, dict[int, list[TopKMatch]], dict[int, list[TopKMatch]]]:
    """The ONE incremental post-batch path (decision #1). Same
    assembly contract as v1.x's assemble_incremental_post_batch: safe
    pids (anchor_date <= min_new_date) reuse their WalkForwardResult
    from pre_batch verbatim; everything else (new pids + must_check
    existing pids) gets a freshly-derived WalkForwardResult. What
    changed is HOW "everything else" gets its top-K ranking -- see
    module docstring.

    Returns (batch, new_pid_topk, existing_must_check_topk) -- the
    latter two are the raw cache deltas for the caller to persist via
    infrastructure/topk_cache_io.py; this function does no DB I/O
    itself (domain/ layer rule).

    Raises:
        IncrementalGuardrailError if pre_batch is missing a safe pid
        (unchanged from v1.x).
        topk_cache.TopKTieError if a displacement or seed comparison
        finds an exact tie at the top-K boundary (Finding 3's rule --
        STOP and report, no silent tiebreak fix). Neither is caught
        here; both propagate to the caller (decision #9).
    """
    if not new_pids:
        return pre_batch, {}, {}

    min_new_date = min(all_metadata[pid].anchor_date for pid in new_pids)
    safe_pids, _must_rescore = _partition_unaffected(
        all_metadata, new_pids, min_new_date,
    )
    pre_results_by_pid = _validated_pre_results(pre_batch, safe_pids)

    new_pid_topk, existing_must_check_topk = topk_cache.update_for_new_batch(
        new_pids, all_metadata, historical_windows, existing_cache,
    )
    to_score = {**new_pid_topk, **existing_must_check_topk}
    fresh_results = [
        _result_from_cached_topk(
            pid, topk, all_metadata, all_labels, threshold_overrides,
        )
        for pid, topk in to_score.items()
    ]
    results_by_pid = {
        **pre_results_by_pid,
        **{r.pattern_instance_id: r for r in fresh_results},
    }
    ordered_pids = sorted(
        all_metadata.keys(), key=lambda pid: all_metadata[pid].anchor_date,
    )
    combined = [results_by_pid[pid] for pid in ordered_pids]
    batch = WalkForwardBatch(
        catalog_path=catalog_path,
        n_patterns=len(combined),
        n_degenerate=sum(1 for r in combined if r.degenerate_corpus),
        threshold_overrides=threshold_overrides,
        results=combined,
    )
    return batch, new_pid_topk, existing_must_check_topk
