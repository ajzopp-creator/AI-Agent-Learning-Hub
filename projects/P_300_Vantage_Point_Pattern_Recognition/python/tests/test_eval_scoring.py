"""
FILE: tests/test_eval_scoring.py
VERSION: 1.2
DATE: 2026-07-17
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for WO-P300-E4.003 (M-096): proves
    domain/eval_scoring.py's v1.2 parallel path (run_walk_forward
    parallel=True) produces byte-identical results to the unchanged
    serial path, and that infrastructure/eval_io.py's pre-batch cache
    round-trips correctly, misses when catalog CONTENT changes (a real
    promote), and -- v1.5, M-099 -- still HITS when only the filename
    and mtime change but content doesn't (the daily dated-rollover
    copy). The cache fixture is now a minimal real SQLite db (a bare
    pattern_instances table), not a plain text file, since v1.5's
    fingerprint is a real COUNT/MAX query against it.

    Synthetic fixture only -- no real catalog dependency, matches the
    project's existing smoke-test convention (tests/smoke_*.py) rather
    than pytest; run directly via PEH. Windows requires ProcessPool
    Executor callers to guard top-level code behind
    `if __name__ == "__main__":` (spawn, not fork) -- all test logic
    lives in main() for that reason, not at module scope.

CHANGELOG:
    - 2026-07-23 v1.2 (WO-P300-E5.004): added
      _test_estimate_full_rescore_seconds() -- checks the new
      estimate_full_rescore_seconds() against WO-P300-E4.005's own
      measured reference point and confirms quadratic growth.
    - 2026-07-17 v1.1 (M-099): cache tests rewritten against a real
      minimal SQLite fixture (eval_io.py v1.5 fingerprints content,
      not mtime, so a plain-text fake catalog no longer works). Added
      _test_rollover_copy_still_hits() -- the case this fix exists for.
    - 2026-07-16 v1.0: WO-P300-E4.003. Initial release.

RUN (from project root, p140 active):
    python tests/test_eval_scoring.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import shutil
import sqlite3
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from domain.eval_scoring import (  # noqa: E402
    estimate_full_rescore_seconds, run_walk_forward,
)
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from infrastructure.eval_io import (  # noqa: E402
    read_cached_walk_forward, write_walk_forward_cache,
)
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _bar(close_pct: float) -> NormalizedBar:
    """One-bar synthetic window. Only close_pct_from_anchor varies
    across fixture patterns -- enough for DTW to rank them distinctly;
    every other field is a fixed, schema-valid placeholder."""
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


def _build_fixture(n: int = 10):
    """n synthetic patterns, one per day, alternating profitable
    labels across all FORWARD_HORIZONS -- enough to exercise a real
    corpus build, DTW rank, and AND-gate classification per pattern."""
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


def _make_fake_catalog(path: Path, n_rows: int = 3) -> None:
    """Minimal real SQLite catalog -- just enough schema for
    eval_io.py's _catalog_fingerprint() COUNT/MAX query to run for
    real (M-099: fingerprint replaced the old mtime-based key)."""
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE pattern_instances (pattern_instance_id INTEGER PRIMARY KEY)"
    )
    conn.executemany(
        "INSERT INTO pattern_instances (pattern_instance_id) VALUES (?)",
        [(i,) for i in range(1, n_rows + 1)],
    )
    conn.commit()
    conn.close()


def _test_parallel_matches_serial() -> None:
    """WO-P300-E4.003 acceptance criterion: parallel run_walk_forward
    is byte-identical to the serial path for the same input."""
    metadata, windows, labels = _build_fixture()
    serial = run_walk_forward("fixture", metadata, windows, labels)
    parallel = run_walk_forward(
        "fixture", metadata, windows, labels, parallel=True, max_workers=2,
    )
    if serial.model_dump_json() == parallel.model_dump_json():
        ok(f"parallel matches serial byte-for-byte ({serial.n_patterns} patterns)")
    else:
        fail("parallel output diverged from serial output")

    if serial.n_patterns == 10 and parallel.n_patterns == 10:
        ok("n_patterns == 10 for both paths")
    else:
        fail(f"n_patterns mismatch: serial={serial.n_patterns}, "
             f"parallel={parallel.n_patterns}")


def _test_cache_round_trip() -> None:
    """write_walk_forward_cache -> read_cached_walk_forward returns an
    equal batch for the same content fingerprint; a real content
    change (promote simulation: row count changes) must miss."""
    metadata, windows, labels = _build_fixture(n=3)
    batch = run_walk_forward("fixture", metadata, windows, labels)
    with tempfile.TemporaryDirectory() as tmp:
        fake_catalog = Path(tmp) / "071726catalog.db"
        _make_fake_catalog(fake_catalog, n_rows=3)

        write_walk_forward_cache(batch, fake_catalog)
        hit = read_cached_walk_forward(fake_catalog)
        if hit is not None and hit.model_dump_json() == batch.model_dump_json():
            ok("cache round-trip returns an identical batch")
        else:
            fail("cache round-trip did not return the written batch")

        conn = sqlite3.connect(fake_catalog)
        conn.execute("INSERT INTO pattern_instances VALUES (99)")
        conn.commit()
        conn.close()
        miss = read_cached_walk_forward(fake_catalog)
        if miss is None:
            ok("cache miss after catalog content changes (promote simulation)")
        else:
            fail("cache incorrectly hit after catalog content changed")


def _test_rollover_copy_still_hits() -> None:
    """M-099: a same-content copy under a NEW filename with a NEW
    mtime (the daily dated-rollover) must still HIT. This is the exact
    bug the old mtime-keyed cache had -- every morning's first
    ingest-mined run silently missed and paid the full ~31-minute
    re-score for no reason."""
    metadata, windows, labels = _build_fixture(n=3)
    batch = run_walk_forward("fixture", metadata, windows, labels)
    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "071626catalog.db"
        _make_fake_catalog(original, n_rows=3)
        write_walk_forward_cache(batch, original)

        rollover = Path(tmp) / "071726catalog.db"
        shutil.copy2(original, rollover)  # new filename, new mtime, same content

        hit = read_cached_walk_forward(rollover)
        if hit is not None and hit.model_dump_json() == batch.model_dump_json():
            ok("rollover copy (new filename+mtime, same content) hits cache")
        else:
            fail("rollover copy incorrectly missed the cache (M-099 regressed)")


def _test_estimate_full_rescore_seconds() -> None:
    """WO-P300-E5.004: pure-function check against WO-P300-E4.005's
    own measured reference points (~12.5h at N=10,738 -- see that
    WO's PHASE 2b RESULTS). Also checks the degenerate N<=1 case and
    that cost is monotonically increasing with corpus_size (quadratic
    growth -- doubling N should roughly quadruple the estimate, not
    just double it)."""
    if estimate_full_rescore_seconds(0) != 0.0:
        fail("N=0 should return exactly 0.0")
    else:
        ok("N=0 returns 0.0")

    if estimate_full_rescore_seconds(1) != 0.0:
        fail("N=1 should return exactly 0.0 (nothing to integrate)")
    else:
        ok("N=1 returns 0.0")

    hours_10738 = estimate_full_rescore_seconds(10738) / 3600.0
    if 11.0 <= hours_10738 <= 14.0:
        ok(f"N=10,738 estimates {hours_10738:.2f}h "
           f"(WO-P300-E4.005 measured ~12.5h)")
    else:
        fail(f"N=10,738 estimated {hours_10738:.2f}h, expected ~12.5h "
             f"(WO-P300-E4.005 reference point)")

    small = estimate_full_rescore_seconds(1000)
    double = estimate_full_rescore_seconds(2000)
    ratio = double / small
    if 3.5 <= ratio <= 4.5:
        ok(f"doubling N roughly quadruples cost (ratio={ratio:.2f}, "
           f"quadratic growth confirmed)")
    else:
        fail(f"doubling N gave ratio={ratio:.2f}, expected ~4.0 "
             f"(quadratic growth)")


def _test_threshold_overrides_reachable_via_cli() -> None:
    """WO-P000-E10.001 item 3.1: threshold_overrides must be reachable
    from a real caller, not just a dead default. run_eval_loop.py's
    --buy-min-z CLI flag builds ThresholdOverrides(buy_min_z_score=...)
    conditionally -- exactly the shape a keyword-arg-only AST scan
    misses, which is why an audit flagged this as "invoked by none."
    It isn't: confirmed here by source inspection, and separately by
    feature_ablation.py's (sealed) Stage 9 usage via a module constant,
    also invisible to a naive keyword scan.
    """
    src = (_PYTHON_DIR / "application" / "run_eval_loop.py").read_text(encoding="utf-8")
    if "ThresholdOverrides(buy_min_z_score=args.buy_min_z)" in src:
        ok("run_eval_loop.py --buy-min-z CLI flag builds a real ThresholdOverrides")
    else:
        fail("run_eval_loop.py no longer builds ThresholdOverrides from --buy-min-z -- "
             "re-check WO-P000-E10.001 item 3.1, this may have regressed to a true dead parameter")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== WO-P300-E4.003 -- parallel path vs serial ===")
    _test_parallel_matches_serial()

    print("\n=== WO-P300-E4.003 -- pre-batch cache round-trip ===")
    _test_cache_round_trip()

    print("\n=== M-099 -- rollover copy still hits cache ===")
    _test_rollover_copy_still_hits()

    print("\n=== WO-P300-E5.004 -- estimate_full_rescore_seconds() ===")
    _test_estimate_full_rescore_seconds()

    print("\n=== WO-P000-E10.001 item 3.1 -- threshold_overrides reachable via CLI ===")
    _test_threshold_overrides_reachable_via_cli()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
