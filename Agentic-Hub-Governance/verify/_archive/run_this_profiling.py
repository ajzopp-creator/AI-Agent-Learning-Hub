"""
WO-P300-E4.005 Phase 1 profiling. Component-level split of where
per-pattern walk-forward cost goes, on a real staging catalog, bounded
subset (NOT the full 3-hour+ pass).

Measures, per must-rescore pattern in the subset:
  (a) DTW compute proper -- timing wrapper DELEGATING to the real
      similarity.dtw_distance (M-082: source function, not re-derived).
  (b) corpus dict-rebuild -- score_one's own corpus_windows/corpus_
      labels build, derived as the score_one residual after (a)+(c).
  (c) ranking + aggregation -- rank_by_distance's non-DTW time
      (composite_distance + sort) plus aggregator.catalog_baseline_win_
      rates + aggregator.aggregate_top_k.
  (d) parallel-path decomposition on a 50-pid sub-subset: pool-init wall
      time vs steady-state throughput vs the same 50 pids run serially.
  (e) tie census -- exact composite-distance ties at the top-K boundary.
  (f) per-pattern (pid, corpus_size, wall_ms) -- for joining against the
      exit-1 diagnostic's fsync'd log outside this script.

Subset selection: must-rescore pids for the current live-vs-staging
batch (same partition logic as the exit-1 diagnostic), stratified by
corpus_size into terciles, SUBSET_SIZE pids sampled evenly across
terciles so the cost-vs-N curve comes from one run.

Self-check: instrumented vs. uninstrumented pass on a small slice must
produce byte-identical score_one() results (model_dump_json) -- proves
the timing wrappers did not perturb behavior.

_partition_unaffected imported directly from domain/eval_incremental.py
(private, underscore-prefixed) rather than re-derived -- diagnostic
script only, not production code (M-082, same precedent as run_this.py).

Output: timing summary + CSV to stdout; operator pipes via Out-File
per the output-piping rule (more than one screen of output).
"""
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
)
sys.path.insert(0, str(_PYTHON_DIR))

from domain import aggregator, similarity  # noqa: E402
from domain.eval_incremental import _partition_unaffected  # noqa: E402
from domain.eval_scoring import _corpus_pids, score_one  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402

LIVE_CATALOG = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\071726catalog.db"
)
STAGING_CATALOG = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\staging_ingest_mined.db"
)

SUBSET_SIZE = 150
PARALLEL_SUBSET_SIZE = 50
SELF_CHECK_SIZE = 20
TOP_K_TIE_EPSILON = 1e-9  # exact-tie check; DTW is sum-of-abs-diffs, no float noise expected


# ─────────────────────────────────────────────────────────────────────────────
# Subset selection -- stratified by corpus_size
# ─────────────────────────────────────────────────────────────────────────────

def _select_stratified_subset(must_rescore_pids, meta, target_size):
    """Terciles of corpus_size (via _corpus_pids), even sample per tercile."""
    sized = [(pid, len(_corpus_pids(pid, meta))) for pid in must_rescore_pids]
    sized.sort(key=lambda t: t[1])
    n = len(sized)
    thirds = [sized[: n // 3], sized[n // 3 : 2 * n // 3], sized[2 * n // 3 :]]
    per_tercile = target_size // 3
    subset = []
    for group in thirds:
        step = max(1, len(group) // max(per_tercile, 1))
        subset.extend(group[::step][:per_tercile])
    return subset  # (pid, corpus_size) list, len ~= target_size


# ─────────────────────────────────────────────────────────────────────────────
# Component (a)/(c) instrumented re-implementation -- DELEGATES to real code
# ─────────────────────────────────────────────────────────────────────────────

def _timed_rank_by_distance(candidate_bars, historical_windows):
    """Mirrors similarity.rank_by_distance's control flow exactly, but
    times DTW-proper (per_feature_distances) separately from composite
    + sort. Calls the REAL similarity.per_feature_distances and
    similarity.composite_distance -- no DTW math re-derived here."""
    dtw_seconds = 0.0
    rank_seconds = 0.0
    scored = []
    for pid, hist_bars in historical_windows.items():
        if not hist_bars:
            continue
        t0 = time.perf_counter()
        per_feat = similarity.per_feature_distances(candidate_bars, hist_bars)
        t1 = time.perf_counter()
        composite = similarity.composite_distance(per_feat)
        t2 = time.perf_counter()
        dtw_seconds += t1 - t0
        rank_seconds += t2 - t1
        scored.append((pid, composite, per_feat))
    t3 = time.perf_counter()
    scored.sort(key=lambda triple: triple[1])
    rank_seconds += time.perf_counter() - t3
    return scored, dtw_seconds, rank_seconds


def _timed_score_one(pid, meta, windows, labels):
    """score_one's control flow, instrumented. Corpus dict-rebuild (b)
    is measured directly; ranking (c) via _timed_rank_by_distance;
    aggregation (c) timed around the real aggregator calls. Returns the
    real WalkForwardResult (for the self-check) plus a timing dict."""
    from config import TOP_K_MATCHES

    t0 = time.perf_counter()
    candidate_bars = windows[pid]
    corpus_pids = _corpus_pids(pid, meta)
    corpus_size = len(corpus_pids)
    corpus_windows = {p: windows[p] for p in corpus_pids}
    corpus_labels = {p: labels.get(p, {}) for p in corpus_pids}
    t1 = time.perf_counter()

    ranked, dtw_s, rank_s = _timed_rank_by_distance(candidate_bars, corpus_windows)
    top_k_pids = [p for p, _d, _f in ranked[:TOP_K_MATCHES]]
    top_k_label_map = {p: corpus_labels.get(p, {}) for p in top_k_pids}

    t2 = time.perf_counter()
    baseline = aggregator.catalog_baseline_win_rates(corpus_labels)
    per_horizon = aggregator.aggregate_top_k(top_k_label_map, baseline)
    t3 = time.perf_counter()

    result = score_one(pid, meta, windows, labels, None)  # real result, untimed 2nd call

    timing = {
        "pid": pid,
        "corpus_size": corpus_size,
        "dict_rebuild_s": t1 - t0,
        "dtw_s": dtw_s,
        "rank_s": rank_s,
        "aggregate_s": t3 - t2,
        "total_wall_s": (t1 - t0) + dtw_s + rank_s + (t3 - t2),
    }
    return result, ranked, timing


# ─────────────────────────────────────────────────────────────────────────────
# (e) tie census
# ─────────────────────────────────────────────────────────────────────────────

def _tie_census(ranked, top_k):
    """Exact ties at the top_k-th boundary (index top_k-1 vs top_k)."""
    if len(ranked) <= top_k:
        return False
    boundary_dist = ranked[top_k - 1][1]
    next_dist = ranked[top_k][1]
    return abs(boundary_dist - next_dist) < TOP_K_TIE_EPSILON


# ─────────────────────────────────────────────────────────────────────────────
# (d) parallel decomposition -- reuses real run_walk_forward machinery
# ─────────────────────────────────────────────────────────────────────────────

def _parallel_decomposition(pids, meta, windows, labels):
    from domain.eval_scoring import _init_worker, _score_one_worker

    t0 = time.perf_counter()
    serial_results = [score_one(p, meta, windows, labels, None) for p in pids]
    serial_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    with ProcessPoolExecutor(
        initializer=_init_worker, initargs=(meta, windows, labels, None)
    ) as executor:
        init_done_s = time.perf_counter() - t0
        t1 = time.perf_counter()
        parallel_results = list(executor.map(_score_one_worker, pids))
        map_s = time.perf_counter() - t1
    parallel_s = time.perf_counter() - t0

    identical = [r.model_dump_json() for r in serial_results] == [
        r.model_dump_json() for r in parallel_results
    ]
    return {
        "n_pids": len(pids),
        "serial_total_s": serial_s,
        "parallel_total_s": parallel_s,
        "pool_init_s": init_done_s,
        "map_s": map_s,
        "byte_identical": identical,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Self-check -- instrumented vs uninstrumented must match exactly
# ─────────────────────────────────────────────────────────────────────────────

def _self_check(pids, meta, windows, labels):
    for pid in pids:
        instrumented_result, _ranked, _timing = _timed_score_one(pid, meta, windows, labels)
        real_result = score_one(pid, meta, windows, labels, None)
        if instrumented_result.model_dump_json() != real_result.model_dump_json():
            print(f"FAIL: self-check mismatch at pid={pid}")
            sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    print(f"Live catalog: {LIVE_CATALOG}", flush=True)
    print(f"Staging catalog: {STAGING_CATALOG}", flush=True)

    _, live_meta, _, _ = load_full_catalog(LIVE_CATALOG)
    _, staging_meta, staging_win, staging_lab = load_full_catalog(STAGING_CATALOG)
    print(f"Loaded live={len(live_meta)} staging={len(staging_meta)}", flush=True)

    new_pids = set(staging_meta.keys()) - set(live_meta.keys())
    if not new_pids:
        print("No new pids -- nothing to profile.")
        print("FAIL: empty new_pids, cannot profile a must-rescore set")
        return 1

    min_new_date = min(staging_meta[p].anchor_date for p in new_pids)
    _safe_pids, must_rescore_pids = _partition_unaffected(staging_meta, new_pids, min_new_date)
    print(f"must_rescore_pids: {len(must_rescore_pids)}", flush=True)

    subset = _select_stratified_subset(must_rescore_pids, staging_meta, SUBSET_SIZE)
    subset_pids = [pid for pid, _cs in subset]
    print(f"Profiling subset: {len(subset_pids)} pids "
          f"(corpus_size range {subset[0][1]}-{subset[-1][1]})", flush=True)

    print("\n--- Self-check: instrumented vs real, byte-identical ---", flush=True)
    _self_check(subset_pids[:SELF_CHECK_SIZE], staging_meta, staging_win, staging_lab)
    print(f"Self-check PASS ({SELF_CHECK_SIZE} pids, model_dump_json identical)", flush=True)

    print("\n--- (a)/(b)/(c) component timing ---", flush=True)
    rows = []
    tie_count = 0
    from config import TOP_K_MATCHES

    for pid in subset_pids:
        _result, ranked, timing = _timed_score_one(pid, staging_meta, staging_win, staging_lab)
        if _tie_census(ranked, TOP_K_MATCHES):
            tie_count += 1
        rows.append(timing)

    dict_rebuild_ms = [r["dict_rebuild_s"] * 1000 for r in rows]
    dtw_ms = [r["dtw_s"] * 1000 for r in rows]
    rank_ms = [r["rank_s"] * 1000 for r in rows]
    agg_ms = [r["aggregate_s"] * 1000 for r in rows]
    total_ms = [r["total_wall_s"] * 1000 for r in rows]

    def _pct(part_list, whole_list):
        s_part, s_whole = sum(part_list), sum(whole_list)
        return 0.0 if s_whole == 0 else 100.0 * s_part / s_whole

    print(f"n={len(rows)}  mean_total_ms={statistics.mean(total_ms):.2f}  "
          f"median_total_ms={statistics.median(total_ms):.2f}", flush=True)
    print(f"  dict_rebuild: mean={statistics.mean(dict_rebuild_ms):.3f}ms "
          f"({_pct(dict_rebuild_ms, total_ms):.1f}%)", flush=True)
    print(f"  dtw_proper:   mean={statistics.mean(dtw_ms):.3f}ms "
          f"({_pct(dtw_ms, total_ms):.1f}%)", flush=True)
    print(f"  rank_sort:    mean={statistics.mean(rank_ms):.3f}ms "
          f"({_pct(rank_ms, total_ms):.1f}%)", flush=True)
    print(f"  aggregate:    mean={statistics.mean(agg_ms):.3f}ms "
          f"({_pct(agg_ms, total_ms):.1f}%)", flush=True)

    print(f"\n--- (e) tie census: top-{TOP_K_MATCHES} boundary ---", flush=True)
    print(f"exact ties at boundary: {tie_count}/{len(rows)} subset patterns", flush=True)

    print(f"\n--- (d) parallel decomposition ({PARALLEL_SUBSET_SIZE} pids) ---", flush=True)
    par_pids = subset_pids[:PARALLEL_SUBSET_SIZE]
    par = _parallel_decomposition(par_pids, staging_meta, staging_win, staging_lab)
    print(f"serial_total_s={par['serial_total_s']:.2f}  "
          f"parallel_total_s={par['parallel_total_s']:.2f}  "
          f"pool_init_s={par['pool_init_s']:.2f}  map_s={par['map_s']:.2f}  "
          f"byte_identical={par['byte_identical']}", flush=True)

    print("\n--- (f) per-pattern CSV (pid,corpus_size,wall_ms) ---", flush=True)
    print("pid,corpus_size,wall_ms")
    for r in rows:
        print(f"{r['pid']},{r['corpus_size']},{r['total_wall_s'] * 1000:.3f}")

    if not par["byte_identical"]:
        print("\nFAIL: parallel decomposition results not byte-identical to serial")
        return 1

    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
