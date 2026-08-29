"""
FILE: tests/test_incremental_post_batch.py
VERSION: 1.1
DATE: 2026-08-17
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Permanent regression test for application/incremental_post_batch.py's
    run_incremental_post_batch() (WO-P300-E5.008). Split out of
    tests/test_eval_incremental.py (which stays domain-layer-only, no
    I/O) because this file's whole purpose is exercising the ONE thing
    the domain-layer tests structurally cannot: the real sqlite
    connection_context() + infrastructure/topk_cache_io.bulk_load_
    topk_cache() round trip that v1.x's fixtures (a bare "fixture"
    catalog_path string, never a real file) never modeled -- exactly
    the gap WO-P300-E5.008's SCOPE item #2 flagged.

    Two checks:
      1. A real temp sqlite catalog, seeded with the TRUE pre-batch
         top-K (via the same domain/topk_cache.seed_full_catalog()
         production code uses), proves run_incremental_post_batch()
         reads it back correctly and still matches a full re-score --
         the DB-wiring seam is proven, not just the domain logic in
         isolation (that's tests/test_eval_incremental.py's job).
      2. IncrementalGuardrailError now propagates UNCAUGHT through this
         function -- WO-P300-E4.006 decision #9 removed v1.x's catch-
         and-fall-back-to-full-rescore behavior entirely. This replaces
         v1.x's _test_application_layer_falls_back, which tested the
         opposite (now-removed) behavior.

    Minimal real sqlite fixture (pattern_instances stub + the real
    topk_cache DDL via topk_cache_io.create_topk_cache_table(), not
    hand-copied -- avoids schema drift), same convention as
    tests/test_verify_ingestion.py. Real files under
    tempfile.TemporaryDirectory(), never the live project catalog.

CHANGELOG:
    - 2026-08-17 v1.1 (WO-P300-E5.008): full_rescore now stamps the
      same real temp catalog_path as run_incremental_post_batch --
      WalkForwardBatch includes that field, so "fixture" vs the temp
      path made the JSON compare fail even when all 13 results
      matched. Scoring assertion unchanged.
    - 2026-08-17 v1.0 (WO-P300-E5.008): Initial release. Split from
      test_eval_incremental.py v1.2's _test_application_layer_falls_
      back (behavior it tested no longer exists in v2.0) plus a new
      real-DB-wiring check the old fixtures never covered.

RUN (from project root, p140 active):
    python tests/test_incremental_post_batch.py

Expected output: each check prefixed "OK"; final line "ALL CHECKS
PASSED". Exit code 0 = full pass, 1 = any failure.
"""
from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PYTHON_DIR = _HERE.parent
sys.path.insert(0, str(_PYTHON_DIR))

from application.incremental_post_batch import run_incremental_post_batch  # noqa: E402
from domain.eval_incremental import IncrementalGuardrailError  # noqa: E402
from domain.eval_scoring import run_walk_forward  # noqa: E402
from domain.topk_cache import seed_full_catalog  # noqa: E402
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from infrastructure.topk_cache_io import (  # noqa: E402
    create_topk_cache_table, insert_topk_rows_batch,
)
from schemas_eval import WalkForwardBatch  # noqa: E402
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar  # noqa: E402


def ok(msg: str) -> None:
    print(f"  OK   {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL {msg}")
    sys.exit(1)


def _bar(close_pct: float) -> NormalizedBar:
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


def _make_patterns_at(dates: list[date], start_pid: int):
    """One synthetic pattern per given date -- arbitrary anchor_date mix.
    Duplicated from test_eval_incremental.py deliberately -- self-
    contained test files, same convention as test_verify_ingestion.py
    (no cross-test-file imports in this project)."""
    metadata: dict[int, PatternMetadata] = {}
    windows: dict[int, list[NormalizedBar]] = {}
    labels: dict[int, dict[int, ForwardLabelLite]] = {}
    for i, d in enumerate(dates):
        pid = start_pid + i
        metadata[pid] = PatternMetadata(
            pattern_instance_id=pid, ticker="TEST", anchor_date=d, window_length=1,
        )
        windows[pid] = [_bar(close_pct=0.01 * pid)]
        profitable = pid % 2 == 0
        labels[pid] = {
            h: ForwardLabelLite(
                return_pct=0.03 if profitable else -0.02, is_profitable=profitable,
            )
            for h in (5, 7, 10, 15, 20)
        }
    return metadata, windows, labels


def _make_patterns(n: int, start: date, start_pid: int = 1):
    """n synthetic patterns from start date, one per day."""
    return _make_patterns_at([start + timedelta(days=i) for i in range(n)], start_pid)


def _merge(existing, new_):
    meta = {**existing[0], **new_[0]}
    win = {**existing[1], **new_[1]}
    lab = {**existing[2], **new_[2]}
    return meta, win, lab


def _create_temp_catalog(path: Path) -> None:
    """Minimal real sqlite fixture: pattern_instances stub (FK target)
    + the REAL topk_cache DDL via topk_cache_io.create_topk_cache_table
    (not hand-copied -- avoids schema drift). Mirrors test_verify_
    ingestion.py's minimal-schema convention."""
    conn = sqlite3.connect(str(path))
    conn.execute(
        "CREATE TABLE pattern_instances (pattern_instance_id INTEGER PRIMARY KEY)"
    )
    create_topk_cache_table(conn)
    conn.commit()
    conn.close()


def _seed_existing_topk_cache(
    path: Path, existing_meta: dict, existing_win: dict,
) -> None:
    """Seeds pattern_instances stubs + the REAL pre-batch top-K for
    every existing pid, via the same seed_full_catalog() production
    code migrations/stage_4a_add_topk_cache.py uses -- mirrors what a
    real staging-catalog copy carries into run_incremental_post_batch
    per that module's own docstring."""
    true_cache = seed_full_catalog(existing_meta, existing_win)
    conn = sqlite3.connect(str(path))
    conn.executemany(
        "INSERT INTO pattern_instances (pattern_instance_id) VALUES (?)",
        [(pid,) for pid in existing_meta],
    )
    rows = [m for matches in true_cache.values() for m in matches]
    insert_topk_rows_batch(conn, rows)
    conn.commit()
    conn.close()


def _test_real_db_wiring_matches_full_rescore() -> None:
    """Closes WO-P300-E5.008's real gap: the old fixtures used a bare
    "fixture" catalog_path string and never exercised connection_
    context() + bulk_load_topk_cache()'s actual DB round trip. Real
    temp sqlite file here, seeded with the true pre-batch top-K --
    result must still byte-match a full re-score."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns_at(
        [date(2026, 1, 5), date(2026, 1, 8), date(2026, 2, 1)], start_pid=101,
    )
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())
    existing_meta, existing_win, _existing_lab = existing

    pre_batch = run_walk_forward("fixture", *existing)

    with tempfile.TemporaryDirectory() as tmp:
        catalog_path = Path(tmp) / "staging.db"
        catalog_path_str = str(catalog_path)
        _create_temp_catalog(catalog_path)
        _seed_existing_topk_cache(catalog_path, existing_meta, existing_win)

        result = run_incremental_post_batch(
            catalog_path_str, full_meta, full_win, full_lab, new_pids, pre_batch,
        )
        # WalkForwardBatch stamps catalog_path; both sides must use the
        # real temp path or the JSON compare fails on the stamp alone.
        full_rescore = run_walk_forward(
            catalog_path_str, full_meta, full_win, full_lab,
        )

    if result.model_dump_json() == full_rescore.model_dump_json():
        ok("run_incremental_post_batch matches full re-score through a "
           "real sqlite topk_cache read (connection_context + "
           "bulk_load_topk_cache wiring proven, not just the domain "
           "logic in isolation)")
    else:
        fail("real-DB incremental result diverged from a full re-score")


def _test_guardrail_propagates_uncaught() -> None:
    """v2.0 dropped the v1.x fallback (WO-P300-E4.006 decision #9):
    IncrementalGuardrailError must now reach the caller, not be caught
    and swallowed into a silent full-rescore fallback. Empty topk_cache
    table is fine -- bulk_load_topk_cache's own "absent pid = no rows"
    contract returns {} gracefully, and the guardrail fires before
    existing_cache is ever consulted (see test_eval_incremental.py)."""
    existing = _make_patterns(10, date(2026, 1, 1), start_pid=1)
    new = _make_patterns(3, date(2026, 2, 1), start_pid=101)
    full_meta, full_win, full_lab = _merge(existing, new)
    new_pids = set(new[0].keys())

    real_pre_batch = run_walk_forward("fixture", *existing)
    truncated = [r for r in real_pre_batch.results if r.pattern_instance_id != 1]
    broken_pre_batch = WalkForwardBatch(
        catalog_path="fixture", n_patterns=len(truncated),
        n_degenerate=real_pre_batch.n_degenerate,
        threshold_overrides=None, results=truncated,
    )

    with tempfile.TemporaryDirectory() as tmp:
        catalog_path = Path(tmp) / "staging.db"
        _create_temp_catalog(catalog_path)  # empty topk_cache -- fine, see above

        try:
            run_incremental_post_batch(
                str(catalog_path), full_meta, full_win, full_lab, new_pids,
                broken_pre_batch,
            )
            fail("expected IncrementalGuardrailError to propagate, none raised")
        except IncrementalGuardrailError:
            ok("guardrail propagates uncaught through the application layer "
               "-- v1.x's fallback-and-swallow behavior is gone (decision #9)")


def main() -> int:
    print(f"Python: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    print("\n=== real sqlite topk_cache wiring -- matches full re-score ===")
    _test_real_db_wiring_matches_full_rescore()

    print("\n=== guardrail propagates uncaught (no v1.x fallback) ===")
    _test_guardrail_propagates_uncaught()

    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
