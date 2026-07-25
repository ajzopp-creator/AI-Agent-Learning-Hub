"""
test_pattern_miner.py -- Regression guard for domain/pattern_miner.py
(WO-P300-E3.002), per the Hub-wide Regression Test Governance rule.

v2.1: added _find_fresh_crossover() tests (the jump-strides-over-next-
crossover fix, confirmed 6/6 on the real 84-anchor ground truth --
tests/mine_ground_truth.py). v2.0: crossover-gated eligibility
replaced same-class re-arm (v1.6, confirmed via real-data gap analysis
to have reintroduced M-083). Backfills M-081 (extended search stays
uncapped) and M-082 (jump/consumption stays capped) against a
crossover-eligible fixture. Cross-class interruption (v1.5) tests kept
unchanged.

Run this BEFORE any future rewrite of pattern_miner.py, as its own
PEH step, separate from whatever the rewrite itself is validating.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_300_Vantage_Point_Pattern_Recognition\\python\\tests\\
           test_pattern_miner.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_pattern_miner.py
"""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python")
DOMAIN = ROOT / "domain"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DOMAIN))

from schemas_bulk import BulkBarRaw  # noqa: E402
import pattern_miner as pm  # noqa: E402

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def make_bar(day_offset: int, close: float, mtdiff: float = 0.0) -> BulkBarRaw:
    """Minimal valid bar: sequential date from 2022-01-03, high/low a
    tiny +-0.01 band around close, mtdiff caller-controlled (drives the
    v2.0 crossover gate), every other VP field zeroed."""
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


def _crossover_two_wave_bars():
    """M-081/M-082 fixture (v2.0): idx0-19 padding, mtdiff=-1.0, flat.
    idx20: crossover 1 (mtdiff -> +1.0), slow rise (0.21%/day) through
    idx41 -- reaches only ~104.4, forcing idx20's own outcome check
    through the extended search (M-081). idx41: single gap bar back to
    mtdiff=-1.0. idx42: crossover 2 (mtdiff -> +1.0 again), faster rise
    (0.6%/day) reaching idx42's own +15% target at h=25."""
    bars = [make_bar(i, 100.0, mtdiff=-1.0) for i in range(20)]
    for t in range(22):  # idx20..idx41
        bars.append(make_bar(20 + t, 100.0 * (1 + 0.0021 * t), mtdiff=1.0))
    bars[-1] = make_bar(41, bars[-1].close, mtdiff=-1.0)  # single gap bar
    base = bars[-1].close
    for t2 in range(60):  # idx42 onward, crossover 2
        bars.append(make_bar(42 + t2, base * (1 + 0.006 * t2), mtdiff=1.0))
    return bars


def test_extended_search_finds_beyond_standard_horizon():
    """BEHAVIOR (M-081) -- a move that only clears MINE_MOVE_THRESHOLD
    past the 20-day standard-horizon cap must still be found via the
    extended search, not silently dropped, even under crossover gating."""
    bars = _crossover_two_wave_bars()
    candidates = pm.mine_bars(bars)
    uptrend = [c for c in candidates if c.pattern_class == pm.UPTREND]
    hit = any(c.horizon_days > pm._MAX_STANDARD_HORIZON and not c.standard_horizon
              for c in uptrend)
    check("extended_search_finds_beyond_standard_horizon", "BEHAVIOR", hit,
          f"uptrend candidates: {[(c.horizon_days, c.standard_horizon) for c in uptrend]}")


def test_jump_capped_at_max_forward_horizon():
    """BEHAVIOR (M-082) -- the cursor jump after a match must be capped
    at _MAX_STANDARD_HORIZON regardless of search length. The fixture's
    second crossover (idx42) sits 22 bars after the first match's anchor
    (idx20) -- reachable only if jump is capped near 20."""
    bars = _crossover_two_wave_bars()
    candidates = pm.mine_bars(bars)
    uptrend = sorted(
        [c for c in candidates if c.pattern_class == pm.UPTREND],
        key=lambda c: c.anchor_date,
    )
    ok = False
    detail = f"found {len(uptrend)} uptrend candidates"
    if len(uptrend) >= 2:
        gap_days = (uptrend[1].anchor_date - uptrend[0].anchor_date).days
        ok = gap_days <= 25 and uptrend[1].bars_since_crossover == 0
        detail = (f"gap={gap_days} days, 2nd candidate bars_since_crossover="
                  f"{uptrend[1].bars_since_crossover}, entry_tier={uptrend[1].entry_tier}")
    check("jump_capped_at_max_forward_horizon", "BEHAVIOR", ok, detail)


def test_bars_since_crossover_walks_back_correctly():
    """BEHAVIOR -- direct unit test of _bars_since_crossover(): a clean
    mtdiff sign-run (down, down, down, up, up, up) must resolve to the
    correct distance from the first bar of the up-run."""
    bars = [make_bar(i, 100.0, mtdiff=-1.0) for i in range(5)] + \
           [make_bar(5 + i, 100.0, mtdiff=1.0) for i in range(5)]
    bs, direction = pm._bars_since_crossover(bars, 5)   # crossover bar itself
    bs2, direction2 = pm._bars_since_crossover(bars, 8)  # 3 bars later
    ok = (bs == 0 and direction == pm.UPTREND and bs2 == 3 and direction2 == pm.UPTREND)
    check("bars_since_crossover_walks_back_correctly", "BEHAVIOR", ok,
          f"at crossover: ({bs}, {direction}); 3 bars later: ({bs2}, {direction2})")


def test_bars_since_crossover_none_at_data_start():
    """BEHAVIOR (negative case) -- a same-sign run that reaches index 0
    (crossover not observable in available data) must return bars_since
    = None, not a wrong number."""
    bars = [make_bar(i, 100.0, mtdiff=1.0) for i in range(10)]
    bs, direction = pm._bars_since_crossover(bars, 5)
    check("bars_since_crossover_none_at_data_start", "BEHAVIOR",
          bs is None and direction == pm.UPTREND, f"got ({bs}, {direction})")


def test_eligible_within_xover_window():
    """BEHAVIOR -- a bar within MINE_XOVER_MAX_BARS of its own same-
    direction crossover, with matching class, must be eligible."""
    bars = _crossover_two_wave_bars()
    eligible, bars_since, tier = pm._is_eligible(bars, 25, pm.UPTREND)  # 5 bars after xover 1
    check("eligible_within_xover_window", "BEHAVIOR",
          eligible and bars_since == 5 and tier == pm.CONTINUATION,
          f"got eligible={eligible} bars_since={bars_since} tier={tier}")


def test_ineligible_beyond_xover_window():
    """BEHAVIOR -- a bar in the same trend but beyond MINE_XOVER_MAX_BARS
    of its crossover must NOT be eligible."""
    bars = [make_bar(i, 100.0, mtdiff=-1.0) for i in range(20)] + \
           [make_bar(20 + i, 100.0 + i, mtdiff=1.0) for i in range(40)]
    eligible, bars_since, tier = pm._is_eligible(bars, 45, pm.UPTREND)
    check("ineligible_beyond_xover_window", "BEHAVIOR", not eligible,
          f"got eligible={eligible} (expected False) bars_since={bars_since}")


def test_ineligible_direction_mismatch():
    """BEHAVIOR -- a bar sitting inside an UPTREND-direction crossover
    window must NOT be eligible for the BREAKDOWN class."""
    bars = _crossover_two_wave_bars()
    eligible, bars_since, tier = pm._is_eligible(bars, 25, pm.BREAKDOWN)
    check("ineligible_direction_mismatch", "BEHAVIOR", not eligible,
          f"got eligible={eligible} (expected False)")


def test_entry_tier_ignition_vs_continuation():
    """BEHAVIOR -- bars_since_crossover <= MINE_IGNITION_MAX_BARS tags
    IGNITION; beyond that (still within the xover window) tags
    CONTINUATION."""
    bars = _crossover_two_wave_bars()
    _, _, tier_at_xover = pm._is_eligible(bars, 20, pm.UPTREND)      # bars_since=0
    _, _, tier_far = pm._is_eligible(bars, 30, pm.UPTREND)           # bars_since=10
    ok = tier_at_xover == pm.IGNITION and tier_far == pm.CONTINUATION
    check("entry_tier_ignition_vs_continuation", "BEHAVIOR", ok,
          f"at crossover: {tier_at_xover}; 10 bars later: {tier_far}")


def test_find_interruption_returns_first_qualifying_bar():
    """BEHAVIOR (v1.5, kept unchanged in v2.x) -- _find_interruption()
    must return the FIRST interior bar where check_class independently
    qualifies at a standard horizon, and must NOT fire on bars whose own
    standard-horizon windows don't reach the qualifying move."""
    bars = [make_bar(i, 100.0) for i in range(22)] + [make_bar(22, 80.0)] \
        + [make_bar(i, 100.0) for i in range(23, 26)]
    interrupt_at = pm._find_interruption(bars, 0, 3, pm.BREAKDOWN)
    check("find_interruption_returns_first_qualifying_bar", "BEHAVIOR",
          interrupt_at == 2, f"got {interrupt_at!r}, expected 2")


def test_find_interruption_none_when_no_opposite_class_move():
    """BEHAVIOR (v1.5, negative case) -- no qualifying move anywhere in
    range must return None."""
    bars = [make_bar(i, 100.0) for i in range(30)]
    interrupt_at = pm._find_interruption(bars, 0, 20, pm.BREAKDOWN)
    check("find_interruption_none_when_no_opposite_class_move", "BEHAVIOR",
          interrupt_at is None, f"got {interrupt_at!r}, expected None")


def test_qualifies_for_class_allow_extended_flag():
    """BEHAVIOR (v1.5) -- allow_extended=False must suppress a match
    that ONLY resolves via the extended search."""
    bars = _crossover_two_wave_bars()
    extended_result = pm._qualifies_for_class(bars, 20, pm.UPTREND)
    standard_only_result = pm._qualifies_for_class(bars, 20, pm.UPTREND, allow_extended=False)
    ok = extended_result is not None and standard_only_result is None
    check("qualifies_for_class_allow_extended_flag", "BEHAVIOR", ok,
          f"extended={extended_result!r} standard_only={standard_only_result!r}")


def test_find_fresh_crossover_detects_new_ignition():
    """BEHAVIOR (v2.1) -- _find_fresh_crossover() must find a bar that
    is ITSELF a fresh same-direction crossover (bars_since_crossover
    == 0) inside a scanned range. Fixture: down-trend through idx19,
    up-trend idx20-40 (crossover 1), single down bar at idx41, fresh
    up-trend from idx42 (crossover 2) -- scanning [21, 45) must find
    idx42, not idx20 (outside the range) or nothing."""
    bars = _crossover_two_wave_bars()
    found = pm._find_fresh_crossover(bars, 21, 45, pm.UPTREND)
    check("find_fresh_crossover_detects_new_ignition", "BEHAVIOR",
          found == 42, f"got {found!r}, expected 42")


def test_find_fresh_crossover_none_when_no_new_crossover():
    """BEHAVIOR (v2.1, negative case) -- a range with no fresh same-
    direction crossover (still inside the FIRST crossover's own run)
    must return None."""
    bars = _crossover_two_wave_bars()
    found = pm._find_fresh_crossover(bars, 21, 40, pm.UPTREND)  # before the gap/2nd xover
    check("find_fresh_crossover_none_when_no_new_crossover", "BEHAVIOR",
          found is None, f"got {found!r}, expected None")


def test_window_stride_bug_fixed_end_to_end():
    """BEHAVIOR (v2.1) -- end-to-end proof of the actual bug fixed: with
    the fresh-crossover truncation in place, mine_bars() must find BOTH
    crossover 1 (idx20, extended search) AND crossover 2 (idx42) as
    separate uptrend candidates, even though crossover 1's raw
    horizon_days (~39) would, uncapped, jump the cursor straight past
    crossover 2 entirely. This is the same invariant
    jump_capped_at_max_forward_horizon checks, restated as the specific
    real-world failure mode (6/6 confirmed on real ground truth,
    2026-07-13) rather than just the cap arithmetic."""
    bars = _crossover_two_wave_bars()
    candidates = pm.mine_bars(bars)
    uptrend_anchors = {c.anchor_date for c in candidates if c.pattern_class == pm.UPTREND}
    xover1_date = bars[20].bar_date
    xover2_date = bars[42].bar_date
    ok = xover1_date in uptrend_anchors and xover2_date in uptrend_anchors
    check("window_stride_bug_fixed_end_to_end", "BEHAVIOR", ok,
          f"xover1 ({xover1_date}) found={xover1_date in uptrend_anchors}, "
          f"xover2 ({xover2_date}) found={xover2_date in uptrend_anchors}")


def test_same_class_rearm_removed():
    """SOURCE (v2.0) -- v1.6's same-class re-arm (confirmed via real-
    data gap analysis to reintroduce M-083) must be fully removed, not
    just unused."""
    src = (DOMAIN / "pattern_miner.py").read_text(encoding="utf-8")
    no_rearm_identifier = "same_class_rearm" not in src
    check("same_class_rearm_removed", "SOURCE", no_rearm_identifier,
          f"no_rearm_identifier={no_rearm_identifier}")


def test_scan_class_wires_crossover_eligibility():
    """SOURCE (v2.0) -- _is_eligible must take want_class and call
    _bars_since_crossover, gated on MINE_XOVER_MAX_BARS; _scan_class
    must pass want_class into _is_eligible."""
    src = (DOMAIN / "pattern_miner.py").read_text(encoding="utf-8")
    is_eligible_takes_class = "def _is_eligible(bars: list[BulkBarRaw], idx: int, want_class: str)" in src
    calls_bars_since_crossover = "_bars_since_crossover(bars, idx)" in src
    checks_xover_max = "bars_since > MINE_XOVER_MAX_BARS" in src
    scan_class_passes_class = "_is_eligible(bars, cursor, want_class)" in src
    ok = (is_eligible_takes_class and calls_bars_since_crossover
          and checks_xover_max and scan_class_passes_class)
    check("scan_class_wires_crossover_eligibility", "SOURCE", ok,
          f"is_eligible_takes_class={is_eligible_takes_class} "
          f"calls_bars_since_crossover={calls_bars_since_crossover} "
          f"checks_xover_max={checks_xover_max} "
          f"scan_class_passes_class={scan_class_passes_class}")


def test_scan_class_wires_fresh_crossover_truncation():
    """SOURCE (v2.1) -- _scan_class must call _find_fresh_crossover()
    with want_class (not opposite_class), and truncate at the min of
    that and the opposite-class interruption (not just the opposite-
    class one alone -- confirms the v2.1 fix is actually wired, not
    just present as a dead function)."""
    src = (DOMAIN / "pattern_miner.py").read_text(encoding="utf-8")
    calls_fresh_xover = "_find_fresh_crossover(\n            bars, cursor + 1, cursor + 1 + jump, want_class\n        )" in src
    truncates_at_min = "cursor = min(truncation_points) if truncation_points else cursor + jump + 1" in src
    ok = calls_fresh_xover and truncates_at_min
    check("scan_class_wires_fresh_crossover_truncation", "SOURCE", ok,
          f"calls_fresh_xover={calls_fresh_xover} truncates_at_min={truncates_at_min}")


def test_jump_cap_applied_at_jump_step_not_search():
    """SOURCE (M-082, structural guard, unchanged in v2.x) -- the jump
    must be min(horizon_days, _MAX_STANDARD_HORIZON), and the extended
    SEARCH loop (M-081) must remain uncapped."""
    src = (DOMAIN / "pattern_miner.py").read_text(encoding="utf-8")
    jump_capped = "jump = min(horizon_days, _MAX_STANDARD_HORIZON)" in src
    search_uncapped = "range(_MAX_STANDARD_HORIZON + 1, MINE_MAX_SCREEN_DAYS + 1)" in src
    ok = jump_capped and search_uncapped
    check("jump_cap_applied_at_jump_step_not_search", "SOURCE", ok,
          f"jump_capped={jump_capped} search_uncapped={search_uncapped}")


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        try:
            t()
        except Exception as e:
            check(t.__name__, "ERROR", False, repr(e))

    failed = [r for r in RESULTS if not r[2]]
    for name, kind, passed, detail in RESULTS:
        mark = "PASS" if passed else "FAIL"
        line = f"[{mark}] ({kind}) {name}"
        if detail and not passed:
            line += f" -- {detail}"
        print(line)

    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
