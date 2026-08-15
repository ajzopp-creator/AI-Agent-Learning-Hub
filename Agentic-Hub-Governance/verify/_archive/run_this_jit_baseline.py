"""
WO-P300-E4.005 Phase 2a -- JIT baseline capture. Runs BEFORE any change
to domain/similarity.py. Captures ground-truth rank_by_distance output
(today's pure-Python DTW) for a spread of real candidate patterns from
the live catalog, serialized to JSON. The post-JIT regression script
(run_this_jit_regression.py, staged separately after the code change)
compares against this file for exact byte-identity -- same standard as
E4.003/E4.004.

Sample: N_CANDIDATES pids evenly spaced by anchor_date across the full
live catalog, so corpus_size coverage spans ~0 to the catalog's full
size. For each candidate, stores:
  - composites_sorted: [pid, composite_distance] for EVERY corpus
    member, in rank_by_distance's own sorted output order -- the
    strict, exhaustive check (every pair, not just the top-K), and
    captures today's real tie-order behavior as a side effect.
  - top_k_detail: full per-feature breakdown for the first
    TOP_K_MATCHES entries only, to bound file size.

_corpus_pids imported directly from domain/eval_scoring.py (private,
underscore-prefixed) rather than re-derived -- same real corpus
definition production code uses (M-082).

Sibling filename (not run_this.py): avoids clobbering the exit-1
diagnostic if it is still occupying the fixed peh-handoff path.
"""
import json
import sys
from pathlib import Path

_PYTHON_DIR = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python"
)
sys.path.insert(0, str(_PYTHON_DIR))

from config import TOP_K_MATCHES  # noqa: E402
from domain import similarity  # noqa: E402
from domain.eval_scoring import _corpus_pids  # noqa: E402
from infrastructure.eval_io import load_full_catalog  # noqa: E402

LIVE_CATALOG = (
    r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition"
    r"\models\071726catalog.db"
)
BASELINE_OUT = Path(
    r"C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\verify"
    r"\jit_baseline_20260718.json"
)
N_CANDIDATES = 40


def _select_evenly_spaced(meta, n):
    """N pids evenly spaced by anchor_date -- spans corpus_size ~0 to full."""
    pids_by_date = sorted(meta.keys(), key=lambda p: meta[p].anchor_date)
    total = len(pids_by_date)
    step = max(1, total // n)
    return pids_by_date[::step][:n]


def main() -> int:
    print(f"Live catalog: {LIVE_CATALOG}", flush=True)
    _, meta, windows, _ = load_full_catalog(LIVE_CATALOG)
    print(f"Loaded {len(meta)} patterns", flush=True)

    candidates = _select_evenly_spaced(meta, N_CANDIDATES)
    print(f"Baseline candidates: {len(candidates)}", flush=True)

    records = []
    for idx, pid in enumerate(candidates, 1):
        corpus_pids = _corpus_pids(pid, meta)
        if not corpus_pids:
            print(f"  [{idx}/{len(candidates)}] pid={pid} corpus_size=0 -- skipped")
            continue
        corpus_windows = {p: windows[p] for p in corpus_pids}
        ranked = similarity.rank_by_distance(windows[pid], corpus_windows)
        print(f"  [{idx}/{len(candidates)}] pid={pid} corpus_size={len(ranked)}",
              flush=True)
        records.append({
            "candidate_pid": pid,
            "corpus_size": len(ranked),
            "composites_sorted": [[p, c] for p, c, _f in ranked],
            "top_k_detail": [[p, c, f] for p, c, f in ranked[:TOP_K_MATCHES]],
        })

    with open(BASELINE_OUT, "w", encoding="utf-8") as fh:
        json.dump(records, fh)
    print(f"Baseline written: {BASELINE_OUT} ({len(records)} candidates)",
          flush=True)

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
