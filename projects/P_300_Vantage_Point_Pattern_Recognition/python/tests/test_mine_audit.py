"""
test_mine_audit.py -- Regression guard for domain/mine_audit.py
(WO-P300-E3.002), per the Hub-wide Regression Test Governance rule.

v1.1 backfill: M-092 (_MOVE_PCT_EPSILON widened 1e-9 -> 1e-6) -- a real
value that survives mine_report_writer.py's :.6f CSV round-trip must
still pass audit against a fresh recompute, while a genuinely different
move_pct must still fail it. Found 2026-07-14 during
ingest_mined_pipeline.py (file #6) PEH against real ADBE data -- every
approved row failed on a "mismatch" invisible at 6 decimals.

Run this BEFORE any future rewrite of mine_audit.py, as its own PEH
step, separate from whatever the rewrite itself is validating.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_300_Vantage_Point_Pattern_Recognition\\python\\tests\\
           test_mine_audit.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_mine_audit.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")
sys.path.insert(0, str(ROOT))

from schemas_bulk import BulkBarRaw  # noqa: E402
from domain.pattern_miner import mine_bars  # noqa: E402
from domain.mine_audit import audit_symbol  # noqa: E402
from infrastructure.mine_report_writer import MineCandidateRow  # noqa: E402

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def make_bar(day_offset: int, close: float, mtdiff: float = 0.0) -> BulkBarRaw:
    """Minimal valid bar -- same convention as test_pattern_miner.py's
    fixture helper."""
    return BulkBarRaw(
        bar_date=date(2022, 1, 3) + timedelta(days=day_offset),
        stdiff=0.0, mtdiff=mtdiff, ltdiff=0.0,
        open=close, high=close + 0.01, low=close - 0.01, close=close,
        pred_high=0.0, pred_low=0.0, volume=1000.0,
        williams_emai=0.0, psi=0.0, roc_pct=0.0,
        neural_index="unknown", neural_x_max=0.0,
        tc_short=0.0, tc_medium=0.0, tc_long=0.0,
        pred_high_diff=0.0, pred_low_diff=0.0, pred_range=0.0,
    )


def _single_candidate_bars():
    """20 bars of flat padding (mtdiff=-1.0, ineligible), then a fresh
    UPTREND crossover at idx20 (mtdiff -> +1.0) with a steady 1%/day
    rise -- clears MINE_MOVE_THRESHOLD (15%) at h=15, a standard
    horizon. Exactly one real candidate, real move_pct from real
    pattern_miner.py math -- not a hand-picked number."""
    bars = [make_bar(i, 100.0, mtdiff=-1.0) for i in range(20)]
    for t in range(30):
        bars.append(make_bar(20 + t, 100.0 * (1 + 0.01 * t), mtdiff=1.0))
    return bars


def _claim_from_candidate(c, keep_move_pct: float) -> MineCandidateRow:
    return MineCandidateRow(
        symbol="TEST", anchor_date=c.anchor_date, pattern_class=c.pattern_class,
        horizon_days=c.horizon_days, move_pct=keep_move_pct,
        standard_horizon=c.standard_horizon,
        bars_since_crossover=c.bars_since_crossover, entry_tier=c.entry_tier,
        keep="YES",
    )


def test_csv_rounded_move_pct_passes_audit():
    """BEHAVIOR (M-092) -- a move_pct rounded to mine_report_writer.py's
    real CSV precision (:.6f, simulating the write->read round-trip)
    must still pass audit against a fresh recompute of the SAME real
    candidate. This is the exact failure mode found 2026-07-14: real
    data, genuinely unchanged, rejected by a too-tight epsilon."""
    bars = _single_candidate_bars()
    candidates = mine_bars(bars)
    assert len(candidates) == 1, f"fixture must produce exactly 1 candidate, got {len(candidates)}"
    c = candidates[0]
    csv_rounded = float(f"{c.move_pct:.6f}")  # exact CSV round-trip simulation
    claim = _claim_from_candidate(c, csv_rounded)
    results = audit_symbol("TEST", bars, [claim], existing_keys=set())
    check("csv_rounded_move_pct_passes_audit", "BEHAVIOR", results[0].passed,
          f"real move_pct={c.move_pct!r} csv_rounded={csv_rounded!r} reasons={results[0].reasons}")


def test_genuinely_different_move_pct_still_fails_audit():
    """BEHAVIOR (M-092 boundary) -- widening the epsilon to absorb CSV
    truncation must NOT blind the audit to a real, material move_pct
    difference (e.g. a hand-edited or stale CSV row). 0.01 (1 full
    percentage point) is far outside CSV truncation noise (~5e-7)."""
    bars = _single_candidate_bars()
    candidates = mine_bars(bars)
    c = candidates[0]
    claim = _claim_from_candidate(c, c.move_pct + 0.01)
    results = audit_symbol("TEST", bars, [claim], existing_keys=set())
    failed_for_right_reason = (
        not results[0].passed
        and any("move_pct mismatch" in r for r in results[0].reasons)
    )
    check("genuinely_different_move_pct_still_fails_audit", "BEHAVIOR",
          failed_for_right_reason, f"reasons={results[0].reasons}")


def main():
    test_csv_rounded_move_pct_passes_audit()
    test_genuinely_different_move_pct_still_fails_audit()

    print(f"{'NAME':<45} {'KIND':<10} RESULT")
    all_pass = True
    for name, kind, passed, detail in RESULTS:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"{name:<45} {kind:<10} {status}  {detail}")
    print()
    n_pass = sum(1 for _, _, p, _ in RESULTS if p)
    if all_pass:
        print(f"PASS ({n_pass}/{len(RESULTS)})")
    else:
        print(f"FAIL ({n_pass}/{len(RESULTS)})")
        sys.exit(1)


if __name__ == "__main__":
    main()
