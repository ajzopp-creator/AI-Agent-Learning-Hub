"""
FILE: tests/test_reconstruct_from_topk.py
VERSION: 1.0
DATE: 2026-07-23
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E5.004 Part A (candidate 2):
    proves domain/reconstruct_from_topk.py's score_one_from_topk_cache()
    produces results IDENTICAL to domain/eval_scoring.py's score_one()
    (the real DTW-based path) for the same input. This is the whole
    point of the file existing -- reconstruction is only useful if it's
    provably equivalent to the real thing, not just plausible.

    topk_cache data for the fixture is generated via the REAL
    domain.topk_cache.seed_full_catalog() (pure in-memory, no DB
    needed), not hand-crafted -- so the test validates against genuine
    topk_cache semantics, the same function that seeds the real table.
    Ground truth comes from the REAL run_walk_forward() (DTW), not a
    simplified stand-in.

    Synthetic fixture only, matching test_eval_scoring.py's own
    convention (smoke-test style, run directly via PEH, not pytest).
    _build_fixture()/_bar() mirror test_eval_scoring.py's exact shape
    for consistency -- not re-derived independently (M-082); a real
    shared fixture module would be a reasonable future cleanup but
    isn't worth a new file for two call sites yet.

CHANGELOG:
    - 2026-07-23 v1.0: WO-P300-E5.004 Part A. Initial release.

RUN (from project root, p140 active):
    python tests/test_reconstruct_from_topk.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent / "python"
sys.path.insert(0, str(_PYTHON_DIR))

from domain import topk_cache  # noqa: E402
from domain.eval_scoring import run_walk_forward, score_one  # noqa: E402
from domain.reconstruct_from_topk import (  # noqa: E402
    classify_topk_gap, score_one_from_topk_cache,
)
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _bar(close_pct: float) -> NormalizedBar:
    """One-bar synthetic window -- mirrors test_eval_scoring.py's _bar()
    exactly (M-082: same fixture shape, not re-derived)."""
    return NormalizedBar(
        bar_offset=0, bar_date=date(2026, 1, 1),
        open=100.0, high=101.0, low=99.0, close=100.0, volume=1_000_000,
        stdiff=0.1, mtdiff=0.2, ltdiff=0.3,
        pred_high=102.0, pred_low=98.0, pred_range=4.0,
        williams_emai=-20.0, psi=60.0, neural_index=1.0,
        triple_cross_short=1.0, triple_cross_medium=1.0, triple_cross_long=1.0,
        close_pct_from_anchor=close_pct, range_pct=0.02, body_pct=0.01,
        volume_zscore=0.0, stdiff_pct=0.001, mtdiff_pct=0.002,
        ltdiff_pct=0.003, pred_high_pct=0.02, pred_low_pct=-0.02,
        pred_range_pct=0.04,
    )


def _build_fixture(n: int = 30):
    """n synthetic patterns, one per day -- mirrors test_eval_scoring.
    py's _build_fixture() shape, but larger (30 vs 10) so corpus sizes
    exceed TOP_K_MATCHES=20 for at least some patterns, exercising the
    real top-K truncation path, not just small-corpus degenerate cases.
    """
    metadata: dict[int, PatternMetadata] = {}
    windows: dict[int, list[NormalizedBar]] = {}
    labels: dict[int, dict[int, ForwardLabelLite]] = {}
    base = date(2026, 1, 1)
    for i in range(n):
        pid = i + 1
        metadata[pid] = PatternMetadata(
            pattern_instance_id=pid, ticker="TEST",
            anchor_date=base + timedelta(days=i), window_length=1,
        )
        windows[pid] = [_bar(close_pct=0.01 * i)]
        profitable = i % 2 == 0
        labels[pid] = {
            h: ForwardLabelLite(
                return_pct=0.03 if profitable else -0.02,
                is_profitable=profitable,
            )
            for h in (5, 7, 10, 15, 20)
        }
    return metadata, windows, labels


def _test_reconstruction_matches_real_dtw() -> None:
    """The core claim: for every pattern in the fixture, reconstructing
    from topk_cache (generated via the REAL seed_full_catalog(), not
    hand-crafted) produces a WalkForwardResult identical to the REAL
    run_walk_forward()'s DTW-based result for the same pattern."""
    metadata, windows, labels = _build_fixture(n=30)

    ground_truth = run_walk_forward("fixture", metadata, windows, labels)
    ground_truth_by_pid = {
        r.pattern_instance_id: r for r in ground_truth.results
    }

    real_topk_cache = topk_cache.seed_full_catalog(metadata, windows)

    mismatches = []
    for pid in metadata:
        matches = real_topk_cache.get(pid, [])
        reconstructed = score_one_from_topk_cache(
            pid, metadata, labels, matches,
        )
        truth = ground_truth_by_pid[pid]
        if reconstructed.model_dump_json() != truth.model_dump_json():
            mismatches.append(pid)

    if not mismatches:
        ok(f"all {len(metadata)} reconstructed results identical to "
           f"real DTW ground truth")
    else:
        fail(f"{len(mismatches)}/{len(metadata)} pids mismatched: "
             f"{mismatches}")

    n_top20_exercised = sum(
        1 for m in real_topk_cache.values() if len(m) == 20
    )
    if n_top20_exercised > 0:
        ok(f"{n_top20_exercised} patterns had a full 20-match corpus "
           f"(top-K truncation path genuinely exercised, not just "
           f"small-corpus degenerate cases)")
    else:
        fail("no pattern reached a full 20-match top-K -- fixture too "
             "small to exercise the truncation path meaningfully")


def _test_gap_classification() -> None:
    """classify_topk_gap(): the three real states, checked directly."""
    if classify_topk_gap(corpus_size=5, topk_matches=[1, 2, 3]) != "ok":  # type: ignore[arg-type]
        fail("non-empty topk_matches should classify as 'ok'")
    else:
        ok("non-empty topk_matches -> 'ok'")

    if classify_topk_gap(corpus_size=0, topk_matches=[]) != "degenerate":
        fail("empty topk_matches + corpus_size==0 should be 'degenerate'")
    else:
        ok("empty topk_matches + corpus_size==0 -> 'degenerate'")

    if classify_topk_gap(corpus_size=42, topk_matches=[]) != "gap":
        fail("empty topk_matches + corpus_size>0 should be 'gap'")
    else:
        ok("empty topk_matches + corpus_size>0 -> 'gap' (real gap, not "
           "silently treated as degenerate)")


def _test_degenerate_pattern_reconstructs_correctly() -> None:
    """The very first pattern (earliest anchor_date, corpus_size==0)
    must reconstruct with degenerate_corpus=True and match real
    run_walk_forward()'s own handling of the same case exactly."""
    metadata, windows, labels = _build_fixture(n=5)
    ground_truth = run_walk_forward("fixture", metadata, windows, labels)
    first_pid = min(metadata, key=lambda p: metadata[p].anchor_date)
    truth = next(
        r for r in ground_truth.results if r.pattern_instance_id == first_pid
    )
    if not truth.degenerate_corpus:
        fail("test assumption wrong -- earliest pattern should be "
             "degenerate_corpus=True in the real ground truth")
        return

    reconstructed = score_one_from_topk_cache(
        first_pid, metadata, labels, [],
    )
    if reconstructed.model_dump_json() == truth.model_dump_json():
        ok("degenerate-corpus pattern reconstructs identically with an "
           "empty topk_matches list")
    else:
        fail("degenerate-corpus reconstruction diverged from real "
             "ground truth")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== WO-P300-E5.004 Part A -- reconstruction matches real DTW ===")
    _test_reconstruction_matches_real_dtw()

    print("\n=== WO-P300-E5.004 Part A -- gap classification ===")
    _test_gap_classification()

    print("\n=== WO-P300-E5.004 Part A -- degenerate-corpus pattern ===")
    _test_degenerate_pattern_reconstructs_correctly()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
