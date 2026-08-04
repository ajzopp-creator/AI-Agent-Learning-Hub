"""
E4.006's outstanding follow-up, closed out for real: byte-identity
regression between the cached-path scoring mechanism (topk_cache ->
_result_from_cached_topk) and a from-scratch full rescore (score_one,
independent similarity.rank_by_distance call), for a diverse set of
real patterns using their REAL, current (post-reseed) topk_cache rows.

Does NOT run run_cached_post_batch's full orchestration (which would
need a genuine whole-catalog pre_batch -- no valid cache exists for
the post-purge catalog, so that would mean another ~60-min full
computation, the same cost class as tonight's topk_cache reseed).
Instead calls the two INNER functions directly for a handful of test
pids -- this is the exact comparison E4.006's follow-up asked for
(does the cached top-20 produce the same WalkForwardResult as an
independent from-scratch ranking?), without the cost of re-deriving
every other pattern's result too. Read-only throughout.

Run:
    C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe run_this.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition")
PYTHON_DIR = PROJECT_ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))

from domain.eval_incremental import _result_from_cached_topk  # noqa: E402
from domain.eval_scoring import score_one  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402
from infrastructure.topk_cache_io import bulk_load_topk_cache  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog_path  # noqa: E402

# Diverse spread: 4 of tonight's KEEP_PIDS (directly relevant, freshly
# reseeded), plus the 5 most recent TWST additions (largest corpus in
# the catalog -- the most expensive/most-likely-to-reveal-a-divergence
# case), plus a few mid-catalog pids for spread.
TEST_PIDS = [26, 17, 353, 449, 10757, 10756, 10755, 10754, 10753, 5000, 2500, 1000]

CHECKS_RUN = 0
CHECKS_PASSED = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global CHECKS_RUN, CHECKS_PASSED
    CHECKS_RUN += 1
    if condition:
        CHECKS_PASSED += 1
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}  {detail}")


def results_match(a, b) -> tuple[bool, list[str]]:
    """Field-by-field compare of two WalkForwardResult Pydantic v2
    models (schemas_eval.WalkForwardResult(BaseModel), not a stdlib
    dataclass -- model_dump() is the correct comparison surface).
    Returns (all_match, list_of_differing_field_names)."""
    da, db = a.model_dump(), b.model_dump()
    diffs = [
        f"{key}: cached={da[key]!r} vs full_rescore={db[key]!r}"
        for key in da
        if da[key] != db[key]
    ]
    return not diffs, diffs


def main() -> int:
    print(f"Python: {sys.executable}")
    live_catalog = get_latest_catalog_path()
    print(f"Live catalog: {live_catalog}")

    print("\n=== loading full catalog (metadata + windows + labels) ===")
    t0 = time.time()
    _path, all_metadata, historical_windows, all_labels = load_full_catalog(str(live_catalog))
    print(f"  {len(all_metadata)} patterns loaded in {time.time() - t0:.1f}s")

    test_pids = [pid for pid in TEST_PIDS if pid in all_metadata]
    missing = [pid for pid in TEST_PIDS if pid not in all_metadata]
    if missing:
        print(f"  (skipping {missing} -- not in current catalog)")

    print(f"\n=== loading REAL current topk_cache rows for {len(test_pids)} test pids ===")
    with connection_context(catalog_path=str(live_catalog)) as conn:
        real_cache = bulk_load_topk_cache(conn, test_pids)

    print(f"\n=== per-pattern comparison: cached path vs. from-scratch full rescore ===")
    total_diffs = 0
    for pid in test_pids:
        meta = all_metadata[pid]
        topk = real_cache.get(pid, [])
        if not topk:
            print(f"  pid={pid} ({meta.ticker} {meta.anchor_date}): SKIPPED -- no topk_cache row "
                  f"(degenerate_corpus pattern, no earlier-dated patterns exist)")
            continue

        t0 = time.time()
        cached_result = _result_from_cached_topk(pid, topk, all_metadata, all_labels, None)
        cached_time = time.time() - t0

        t0 = time.time()
        full_result = score_one(pid, all_metadata, historical_windows, all_labels, None)
        full_time = time.time() - t0

        match, diffs = results_match(cached_result, full_result)
        check(
            f"pid={pid} ({meta.ticker} {meta.anchor_date}, corpus={cached_result.corpus_size}): "
            f"cached ({cached_time*1000:.1f}ms) == full rescore ({full_time*1000:.0f}ms)",
            match, "; ".join(diffs),
        )
        total_diffs += len(diffs)

    print(f"\n{CHECKS_PASSED}/{CHECKS_RUN} patterns byte-identical between cached path and full rescore.")
    if total_diffs == 0 and CHECKS_RUN > 0:
        print("PASS -- E4.006's byte-identity regression check, closed out for real.")
        return 0
    else:
        print("FAIL -- see diffs above. Do not close E4.006's follow-up on this result.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
