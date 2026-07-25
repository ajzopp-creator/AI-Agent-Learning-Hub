"""
test_ingest_mined_pipeline.py -- Regression guard for
application/ingest_mined_pipeline.py (WO-P300-E3.002 file #6), per the
Hub-wide Regression Test Governance rule.

v1.0: M-093 -- MINE_MIN_ANCHOR_DATE only gates the ANCHOR bar in
pattern_miner.py's eligibility check. A BULK_WINDOW_LENGTH-bar window
behind an early-but-eligible anchor can still reach into the
pre-2021-07-14 backfill period, where pred_high/pred_low are 0.0
placeholders that fail PatternBarRecord's gt=0 validation downstream
(catalog_merge_io.py). Found 2026-07-14 during real-ADBE PEH: anchor
2021-08-04 is a valid, eligible anchor but its 20-bar window reaches
back to 2021-07-08.

Run this BEFORE any future rewrite of ingest_mined_pipeline.py, as its
own PEH step, separate from whatever the rewrite itself is validating.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_300_Vantage_Point_Pattern_Recognition\\python\\tests\\
           test_ingest_mined_pipeline.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_ingest_mined_pipeline.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")
sys.path.insert(0, str(ROOT))

from config import BULK_WINDOW_LENGTH, FORWARD_HORIZONS, MINE_MIN_ANCHOR_DATE  # noqa: E402
from schemas_bulk import BulkBarRaw  # noqa: E402
from application.ingest_mined_pipeline import _build_window_and_labels  # noqa: E402

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def make_bar(bar_date: date, close: float = 100.0) -> BulkBarRaw:
    """Minimal valid bar -- same convention as test_pattern_miner.py's
    fixture helper. pred_high/pred_low=0.0 mirrors real backfilled bars;
    _build_window_and_labels itself never validates them (RawBulkBar is
    a plain dataclass) -- only the boundary date matters for this test."""
    return BulkBarRaw(
        bar_date=bar_date, stdiff=0.0, mtdiff=0.0, ltdiff=0.0,
        open=close, high=close + 0.01, low=close - 0.01, close=close,
        pred_high=0.0, pred_low=0.0, volume=1000.0,
        williams_emai=0.0, psi=0.0, roc_pct=0.0,
        neural_index="unknown", neural_x_max=0.0,
        tc_short=0.0, tc_medium=0.0, tc_long=0.0,
        pred_high_diff=0.0, pred_low_diff=0.0, pred_range=0.0,
    )


def _daily_bars(base: date, n: int) -> list[BulkBarRaw]:
    """n consecutive daily bars starting at base -- enough after any
    anchor picked at offset 25 to satisfy FORWARD_HORIZONS' max lookahead."""
    return [make_bar(base + timedelta(days=i), 100.0 + i * 0.1) for i in range(n)]


def test_window_reaching_before_backfill_boundary_rejected():
    """BEHAVIOR (M-093) -- an anchor that is itself on/after
    MINE_MIN_ANCHOR_DATE but whose BULK_WINDOW_LENGTH-bar window reaches
    before it must be rejected with a ValueError naming the boundary,
    not silently passed through to a PatternBarRecord validation crash
    three layers downstream."""
    base = MINE_MIN_ANCHOR_DATE - timedelta(days=30)
    bars = _daily_bars(base, 80)
    anchor_idx = 25
    anchor_date = bars[anchor_idx].bar_date
    window_start_date = bars[anchor_idx - BULK_WINDOW_LENGTH + 1].bar_date
    assert window_start_date < MINE_MIN_ANCHOR_DATE, (
        "fixture bug: window_start_date must predate MINE_MIN_ANCHOR_DATE "
        "for this test to exercise the guard"
    )
    try:
        _build_window_and_labels(bars, anchor_date)
        check("window_reaching_before_backfill_boundary_rejected", "BEHAVIOR",
              False, "expected ValueError, none raised")
    except ValueError as exc:
        raised_right_reason = "MINE_MIN_ANCHOR_DATE" in str(exc) or "backfill" in str(exc)
        check("window_reaching_before_backfill_boundary_rejected", "BEHAVIOR",
              raised_right_reason, f"reason={exc}")


def test_window_fully_clear_of_backfill_boundary_accepted():
    """BEHAVIOR (M-093 boundary) -- widening the guard must not reject a
    window that stays entirely on/after MINE_MIN_ANCHOR_DATE -- the
    common, correct case must keep working."""
    base = MINE_MIN_ANCHOR_DATE + timedelta(days=10)
    bars = _daily_bars(base, 80)
    anchor_idx = 25
    anchor_date = bars[anchor_idx].bar_date
    window_start_date = bars[anchor_idx - BULK_WINDOW_LENGTH + 1].bar_date
    assert window_start_date >= MINE_MIN_ANCHOR_DATE, (
        "fixture bug: window_start_date must be on/after MINE_MIN_ANCHOR_DATE "
        "for this test to exercise the accept path"
    )
    try:
        raw_bars, label_tuples = _build_window_and_labels(bars, anchor_date)
        ok = len(raw_bars) == BULK_WINDOW_LENGTH and len(label_tuples) == len(FORWARD_HORIZONS)
        check("window_fully_clear_of_backfill_boundary_accepted", "BEHAVIOR",
              ok, f"raw_bars={len(raw_bars)} label_tuples={len(label_tuples)}")
    except ValueError as exc:
        check("window_fully_clear_of_backfill_boundary_accepted", "BEHAVIOR",
              False, f"unexpected reject: {exc}")


def main():
    test_window_reaching_before_backfill_boundary_rejected()
    test_window_fully_clear_of_backfill_boundary_accepted()

    print(f"{'NAME':<55} {'KIND':<10} RESULT")
    all_pass = True
    for name, kind, passed, detail in RESULTS:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"{name:<55} {kind:<10} {status}  {detail}")
    print()
    n_pass = sum(1 for _, _, p, _ in RESULTS if p)
    if all_pass:
        print(f"PASS ({n_pass}/{len(RESULTS)})")
    else:
        print(f"FAIL ({n_pass}/{len(RESULTS)})")
        sys.exit(1)


if __name__ == "__main__":
    main()
