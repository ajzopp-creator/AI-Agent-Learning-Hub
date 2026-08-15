"""
test_p400_known_bugs.py -- Regression guard for the P_400 Bugs Already
Fixed table in .claude/skills/p400-project-context/SKILL.md.

One test per CLOSED WO with a concrete, checkable fix. Run this after
ANY edit to the files it covers, and before calling a fix "done." Per
WO-P020-E1.003's Hub-wide rule (2026-07-06), any future bug fixed in
this project gets a matching test added here in the same session.

Two kinds of test, both labeled in each docstring:
  BEHAVIOR -- calls the real function against a tiny synthetic input and
              checks the actual output. Confirms the bug cannot recur.
  SOURCE   -- greps the file for the fix's signature. Cheaper, but only
              confirms the fix line is still there, not full behavior.

E2.017 (test_screen.py hardcoded absolute dates) is still OPEN as of
2026-07-06 -- not included here. Add its test when that WO closes.

SPLIT ACROSS FILES (WO-P400-E5.004, 2026-08-08): this file grows by design
(one test per future fix, forever) and will keep hitting the 300-line cap.
When it does, split -- do not just keep appending. Convention: this file
holds WO-P400-E2.xxx/E3.xxx; the E10.001 cluster moved to
test_p400_known_bugs_2.py at the same split. New entries go into whichever
split file is currently newest/smallest; when THAT one approaches 300
lines, start test_p400_known_bugs_3.py, and so on. No wiring needed --
pytest auto-discovers every test_*.py file under tests\\, so a new numbered
file requires no imports or registration anywhere else. Keep each file's
own module docstring current about which WO range it covers.

Converted from a standalone RESULTS/check() harness to plain pytest
assertions per WO-P000-E13.001 Phase 4 (2026-08-08) -- this file did not
previously run under a plain `pytest` invocation (Finding 5). ROOT is now
derived from this file's own location instead of hardcoded (Finding 4).
sys.path manipulation removed -- python\\conftest.py (WO-P000-E13.001
Phase 2) puts python\\ on sys.path Hub-wide, making it redundant here.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_400_TradeOrderManagement\\python\\tests\\
           test_p400_known_bugs.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_p400_known_bugs.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = ROOT / "domain"
APPLICATION = ROOT / "application"


def test_e2007_stop_exactly_1x_atr_passes():
    """BEHAVIOR -- stop at exactly 1x ATR must PASS, not false-BLOCK on
    float rounding (WO-P400-E2.007)."""
    from domain.council import quant_vote, Decision
    v = quant_vote(rr_at_t1=2.5, stop=49.0, entry=50.0, target=55.0, atr_14=1.0)
    assert v.decision == Decision.PASS, f"got {v.decision}"


def test_e2007_stop_below_tolerance_still_blocks():
    """BEHAVIOR -- stop genuinely tighter than 1x ATR (0.99x) must still
    BLOCK; the tolerance must not swallow real violations."""
    from domain.council import quant_vote, Decision
    from domain.council_codes import RC_STOP_TOO_TIGHT
    v = quant_vote(rr_at_t1=2.5, stop=49.01, entry=50.0, target=55.0, atr_14=1.0)
    assert v.decision == Decision.BLOCK and v.reason_code == RC_STOP_TOO_TIGHT, \
        f"got {v.decision}/{v.reason_code}"


def test_e2012_book_dir_not_dead_folder():
    """SOURCE -- BOOK_DIR must point at TradeOrderManagement\\P400 (post
    WO-P800-E3.003 vault rename), not the now-dead TradeManagement\\P400
    folder (WO-P400-E2.012 fix superseded by the rename)."""
    import config
    parts = config.BOOK_DIR.parts
    assert "TradeOrderManagement" in parts and "TradeManagement" not in parts, \
        f"got {config.BOOK_DIR}"


def test_e2012_book_loader_field_remap():
    """SOURCE -- book_loader.py must remap writer field names (ticker/
    lifecycle_status) to reader field names (symbol/status) at the read
    boundary (WO-P400-E2.012 second-layer fix)."""
    src = (ROOT / "infrastructure" / "book_loader.py").read_text(encoding="utf-8")
    assert 'fm.pop("ticker"' in src and 'fm.pop("lifecycle_status"' in src


def test_e2013_tape_adverse_drift_is_caution_not_block():
    """BEHAVIOR -- TAPE must CAUTION (not BLOCK) on adverse drift when
    R:R collapses; QUANT already owns the hard block for that same
    condition (WO-P400-E2.013)."""
    from domain.council import tape_vote, Decision
    from domain.council_codes import RC_ADVERSE_DRIFT
    v = tape_vote(price_delay_seconds=10, market_open=True, price_basis="live",
                   adverse_drift_pct=5.0, rr_after_drift=1.2)
    assert v.decision == Decision.CAUTION and v.reason_code == RC_ADVERSE_DRIFT, \
        f"got {v.decision}"


def test_e2014_gate3_scales_with_posture():
    """BEHAVIOR -- Gate 3 (Concentration) cap must scale with the live
    risk_mode posture multiplier, not stay pinned at the unreduced
    STANDARD/FULL value (WO-P400-E2.014)."""
    from domain.sizing import three_gate_size
    standard = three_gate_size(
        entry=100.0, stop=95.0, target=115.0, base_risk_dollars=500.0,
        cash_available=100000.0, max_position_dollars=1000.0, risk_mode="STANDARD",
    )
    half = three_gate_size(
        entry=100.0, stop=95.0, target=115.0, base_risk_dollars=500.0,
        cash_available=100000.0, max_position_dollars=1000.0, risk_mode="HALF",
    )
    assert half.adjusted_risk_dollars < standard.adjusted_risk_dollars, \
        f"standard={standard.adjusted_risk_dollars} half={half.adjusted_risk_dollars}"


def test_e2016_rr_below_min_detail_discloses_both_bases():
    """BEHAVIOR -- quant_vote()'s RC_RR_BELOW_MIN reason_detail must label
    both figures explicitly -- realistic-fill spread-adjusted R:R vs.
    clean/guideline target basis -- not state both on one line with no
    basis label, which read as self-contradictory even though the BLOCK
    itself was always correct (WO-P400-E2.016). Mirrors
    test_council.py::test_quant_blocks_rr_below_min."""
    from domain.council import quant_vote, Decision
    from domain.council_codes import RC_RR_BELOW_MIN
    v = quant_vote(rr_at_t1=1.8, stop=48.0, entry=50.0, target=53.6, atr_14=1.5)
    assert v.decision == Decision.BLOCK
    assert v.reason_code == RC_RR_BELOW_MIN
    assert "spread-adjusted" in v.reason_detail, f"got {v.reason_detail}"
    assert "clean/guideline basis" in v.reason_detail, f"got {v.reason_detail}"


def test_e2018_dispose_failed_wired_into_screen_all():
    """SOURCE -- cmd_screen_all() must call dispose_failed() automatically;
    FAIL packets must not require a manual batch-drop step
    (WO-P400-E2.018)."""
    src = (APPLICATION / "commands.py").read_text(encoding="utf-8")
    assert "dispose_failed" in src and "DISPOSAL SUMMARY" in src


def test_e3005_spread_council_blocks_wide_leg():
    """BEHAVIOR -- a spread with one leg's spread_pct_of_mid above the
    10% viability threshold must BLOCK, the exact ADBE 215C/225C
    regression case from WO-P400-E3.005."""
    from schemas import OptionChainInput
    from domain.spread_council import run_spread_council

    def _chain(strike, oi, spread_pct, bid, ask):
        mid = round((bid + ask) / 2, 2)
        return OptionChainInput(
            symbol="ADBE", underlying_price=220.0, expiration="2026-08-21",
            strike=strike, option_type="call", bid=bid, ask=ask, mid=mid,
            delta=0.5, iv=0.30, open_interest=oi, spread_pct_of_mid=spread_pct,
            data_source="tos", chain_timestamp="2026-07-04T10:00:00Z",
        )

    long_chain = _chain(215.0, 800, 3.5, 18.50, 18.90)
    short_chain = _chain(225.0, 300, 11.9, 9.20, 10.45)
    result = run_spread_council(long_chain, short_chain)
    assert result.verdict == "BLOCK" and any("SHORT_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks), \
        f"got {result.verdict}/{result.blocks}"


def test_e3010_spec_cacheable_verdicts_complete():
    """SOURCE -- SPEC_CACHEABLE_VERDICTS must include every verdict tier
    that reaches STEP 6 in the SIP (APPROVED, APPROVED_WITH_CAUTION,
    APPROVED_WITH_SEVERE_WARNING), so cmd_evaluate's spec-cache gate
    can't silently drop a tier again (WO-P400-E3.010)."""
    import config
    expected = {"APPROVED", "APPROVED_WITH_CAUTION", "APPROVED_WITH_SEVERE_WARNING"}
    assert expected.issubset(config.SPEC_CACHEABLE_VERDICTS), \
        f"got {config.SPEC_CACHEABLE_VERDICTS}"


def test_e3010_commands_uses_cacheable_verdicts_set():
    """SOURCE -- cmd_evaluate's stock-only branch must gate spec-caching
    on SPEC_CACHEABLE_VERDICTS, not a literal "APPROVED" string compare
    (regression of E3.009's exact-string gate, WO-P400-E3.010)."""
    src = (ROOT / "application" / "commands.py").read_text(encoding="utf-8")
    assert ("result.verdict in SPEC_CACHEABLE_VERDICTS" in src
            and 'if result.verdict == "APPROVED":' not in src)


def test_e4005_e4006_market_open_wall_clock_and_holiday_aware():
    """BEHAVIOR -- is_market_open_now() must return False on a real market
    holiday during normal trading hours (wall-clock alone would say open
    -- WO-P400-E4.006's holiday-aware upgrade over E4.005's original
    wall-clock-only check) and True on an ordinary weekday at the same
    time. Regression-guard mirror entry -- both WOs were genuinely tested
    at build time (test_market_hours.py, test_market_holidays.py) but
    neither added the separate guard-file entry this table is supposed to
    mirror (WO-P400-E5.004, found by WO-P000-E13.001 Phase 4's
    correspondence check)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from domain.market_hours import is_market_open_now

    eastern = ZoneInfo("America/New_York")
    labor_day_2026 = datetime(2026, 9, 7, 10, 0, tzinfo=eastern)     # Monday, market holiday
    ordinary_weekday = datetime(2026, 9, 8, 10, 0, tzinfo=eastern)   # Tuesday, normal session

    assert is_market_open_now(labor_day_2026) is False, "holiday must not report open"
    assert is_market_open_now(ordinary_weekday) is True, "ordinary weekday must report open"
