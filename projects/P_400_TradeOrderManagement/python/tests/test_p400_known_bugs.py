"""
test_p400_known_bugs.py -- Regression guard for the P_400 Bugs Already
Fixed table in .claude/skills/p400-project-context/SKILL.md.

One test per CLOSED WO with a concrete, checkable fix. Run this after
ANY edit to the files it covers, and before calling a fix "done." Per
WO-P020-E1.003's Hub-wide rule (2026-07-06), any future bug fixed in
this project gets a matching test added here in the same session.

Two kinds of test, both labeled below:
  BEHAVIOR -- calls the real function against a tiny synthetic input and
              checks the actual output. Confirms the bug cannot recur.
  SOURCE   -- greps the file for the fix's signature. Cheaper, but only
              confirms the fix line is still there, not full behavior.

E2.017 (test_screen.py hardcoded absolute dates) is still OPEN as of
2026-07-06 -- not included here. Add its test when that WO closes.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_400_TradeOrderManagement\\python\\tests\\
           test_p400_known_bugs.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_p400_known_bugs.py
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python")
DOMAIN = ROOT / "domain"
APPLICATION = ROOT / "application"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(DOMAIN))

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def test_e2007_stop_exactly_1x_atr_passes():
    """BEHAVIOR -- stop at exactly 1x ATR must PASS, not false-BLOCK on
    float rounding (WO-P400-E2.007)."""
    from domain.council import quant_vote, Decision
    v = quant_vote(rr_at_t1=2.5, stop=49.0, entry=50.0, target=55.0, atr_14=1.0)
    check("e2007_stop_exactly_1x_atr_passes", "BEHAVIOR", v.decision == Decision.PASS,
          f"got {v.decision}")


def test_e2007_stop_below_tolerance_still_blocks():
    """BEHAVIOR -- stop genuinely tighter than 1x ATR (0.99x) must still
    BLOCK; the tolerance must not swallow real violations."""
    from domain.council import quant_vote, Decision
    from domain.council_codes import RC_STOP_TOO_TIGHT
    v = quant_vote(rr_at_t1=2.5, stop=49.01, entry=50.0, target=55.0, atr_14=1.0)
    ok = v.decision == Decision.BLOCK and v.reason_code == RC_STOP_TOO_TIGHT
    check("e2007_stop_below_tolerance_still_blocks", "BEHAVIOR", ok, f"got {v.decision}/{v.reason_code}")


def test_e2012_book_dir_not_dead_folder():
    """SOURCE -- BOOK_DIR must point at TradeManagement\\P400, not the
    dead TradeOrderManagement\\P400 folder (WO-P400-E2.012)."""
    import config
    parts = config.BOOK_DIR.parts
    ok = "TradeManagement" in parts and not (
        "TradeOrderManagement" in parts and "TradeManagement" not in parts
    )
    check("e2012_book_dir_not_dead_folder", "SOURCE", ok, f"got {config.BOOK_DIR}")


def test_e2012_book_loader_field_remap():
    """SOURCE -- book_loader.py must remap writer field names (ticker/
    lifecycle_status) to reader field names (symbol/status) at the read
    boundary (WO-P400-E2.012 second-layer fix)."""
    src = (ROOT / "infrastructure" / "book_loader.py").read_text(encoding="utf-8")
    ok = 'fm.pop("ticker"' in src and 'fm.pop("lifecycle_status"' in src
    check("e2012_book_loader_field_remap", "SOURCE", ok)


def test_e2013_tape_adverse_drift_is_caution_not_block():
    """BEHAVIOR -- TAPE must CAUTION (not BLOCK) on adverse drift when
    R:R collapses; QUANT already owns the hard block for that same
    condition (WO-P400-E2.013)."""
    from domain.council import tape_vote, Decision
    from domain.council_codes import RC_ADVERSE_DRIFT
    v = tape_vote(price_delay_seconds=10, market_open=True, pre_market_flag=False,
                   adverse_drift_pct=5.0, rr_after_drift=1.2)
    ok = v.decision == Decision.CAUTION and v.reason_code == RC_ADVERSE_DRIFT
    check("e2013_tape_adverse_drift_is_caution_not_block", "BEHAVIOR", ok, f"got {v.decision}")


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
    ok = half.adjusted_risk_dollars < standard.adjusted_risk_dollars
    check("e2014_gate3_scales_with_posture", "BEHAVIOR", ok,
          f"standard={standard.adjusted_risk_dollars} half={half.adjusted_risk_dollars}")


def test_e2018_dispose_failed_wired_into_screen_all():
    """SOURCE -- cmd_screen_all() must call dispose_failed() automatically;
    FAIL packets must not require a manual batch-drop step
    (WO-P400-E2.018)."""
    src = (APPLICATION / "commands.py").read_text(encoding="utf-8")
    ok = "dispose_failed" in src and "DISPOSAL SUMMARY" in src
    check("e2018_dispose_failed_wired_into_screen_all", "SOURCE", ok)


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
    ok = result.verdict == "BLOCK" and any("SHORT_LEG_SPREAD_TOO_WIDE" in b for b in result.blocks)
    check("e3005_spread_council_blocks_wide_leg", "BEHAVIOR", ok, f"got {result.verdict}/{result.blocks}")


def main():
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
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
