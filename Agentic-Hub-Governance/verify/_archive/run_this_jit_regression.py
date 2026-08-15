"""
WO-P300-E4.005 Phase 2a -- JIT regression check. Run AFTER
domain/similarity.py has been modified to add the numba-jit DTW
kernel (test_similarity.py should already show PASS before this
runs). Recomputes rank_by_distance for the SAME candidates as the
baseline capture (same deterministic selection, same live catalog --
nothing about the catalog changed between the two runs) and asserts
exact float equality against jit_baseline_20260718.json.

Byte-identity standard: composites_sorted (every corpus member's
composite distance, in rank_by_distance's own sort order) AND
top_k_detail (full per-feature breakdown for the top TOP_K_MATCHES)
must match EXACTLY -- same standard as E4.003/E4.004, no tolerance,
no np.isclose. Any mismatch is a stop-and-review, not a close-enough
pass.

This is the M-079 gate PRECONDITION, not M-079 itself: it proves the
JIT change didn't alter DTW arithmetic. The separate walk-forward
BUY-precision/PASS-accuracy comparison (M-079 proper) still runs
before promoting this to the live signal path, per the WO's Finding 1
live-path flag.
"""
import json
import sys
from pathlib import Path

_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
)
sys.path.insert(0, str(_PYTHON_DIR))

from domain import similarity  # noqa: E402
from domain.eval_scoring import _corpus_pids  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402

LIVE_CATALOG = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\071726catalog.db"
)
BASELINE_PATH = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify"
    r"\jit_baseline_20260718.json"
)


def main() -> int:
    if not BASELINE_PATH.exists():
        print(f"FAIL: baseline not found at {BASELINE_PATH}")
        return 1
    with open(BASELINE_PATH, "r", encoding="utf-8") as fh:
        baseline_records = json.load(fh)
    print(f"Loaded baseline: {len(baseline_records)} candidates", flush=True)

    print(f"Live catalog: {LIVE_CATALOG}", flush=True)
    _, meta, windows, _ = load_full_catalog(LIVE_CATALOG)
    print(f"Loaded {len(meta)} patterns", flush=True)

    mismatches = 0
    for idx, record in enumerate(baseline_records, 1):
        pid = record["candidate_pid"]
        corpus_pids = _corpus_pids(pid, meta)
        corpus_windows = {p: windows[p] for p in corpus_pids}
        ranked = similarity.rank_by_distance(windows[pid], corpus_windows)

        if len(ranked) != record["corpus_size"]:
            print(f"  [{idx}] pid={pid} FAIL corpus_size {len(ranked)} != "
                  f"baseline {record['corpus_size']}")
            mismatches += 1
            continue

        actual_composites = [[p, c] for p, c, _f in ranked]
        if actual_composites != record["composites_sorted"]:
            print(f"  [{idx}] pid={pid} FAIL composites_sorted mismatch")
            mismatches += 1
            continue

        k = len(record["top_k_detail"])
        actual_top_k = [[p, c, f] for p, c, f in ranked[:k]]
        if actual_top_k != record["top_k_detail"]:
            print(f"  [{idx}] pid={pid} FAIL top_k_detail mismatch")
            mismatches += 1
            continue

        print(f"  [{idx}] pid={pid} OK (corpus_size={len(ranked)})", flush=True)

    if mismatches:
        print(f"\nFAIL: {mismatches}/{len(baseline_records)} candidates mismatched")
        return 1

    print(f"\nAll {len(baseline_records)} candidates byte-identical to baseline.")
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
