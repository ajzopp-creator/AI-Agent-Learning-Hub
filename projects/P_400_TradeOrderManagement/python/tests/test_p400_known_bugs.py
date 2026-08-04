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
    """SOURCE -- BOOK_DIR must point at TradeOrderManagement\\P400 (post
    WO-P800-E3.003 vault rename), not the now-dead TradeManagement\\P400
    folder (WO-P400-E2.012 fix superseded by the rename)."""
    import config
    parts = config.BOOK_DIR.parts
    ok = "TradeOrderManagement" in parts and "TradeManagement" not in parts
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


def test_e3010_spec_cacheable_verdicts_complete():
    """SOURCE -- SPEC_CACHEABLE_VERDICTS must include every verdict tier
    that reaches STEP 6 in the SIP (APPROVED, APPROVED_WITH_CAUTION,
    APPROVED_WITH_SEVERE_WARNING), so cmd_evaluate's spec-cache gate
    can't silently drop a tier again (WO-P400-E3.010)."""
    import config
    expected = {"APPROVED", "APPROVED_WITH_CAUTION", "APPROVED_WITH_SEVERE_WARNING"}
    ok = expected.issubset(config.SPEC_CACHEABLE_VERDICTS)
    check("e3010_spec_cacheable_verdicts_complete", "SOURCE", ok,
          f"got {config.SPEC_CACHEABLE_VERDICTS}")


def test_e3010_commands_uses_cacheable_verdicts_set():
    """SOURCE -- cmd_evaluate's stock-only branch must gate spec-caching
    on SPEC_CACHEABLE_VERDICTS, not a literal "APPROVED" string compare
    (regression of E3.009's exact-string gate, WO-P400-E3.010)."""
    src = (ROOT / "application" / "commands.py").read_text(encoding="utf-8")
    ok = ("result.verdict in SPEC_CACHEABLE_VERDICTS" in src
          and 'if result.verdict == "APPROVED":' not in src)
    check("e3010_commands_uses_cacheable_verdicts_set", "SOURCE", ok, "")


def test_e10001_compare_vehicles_passes_options_council_result():
    """SOURCE -- compare_vehicles.py call site must pass options_council_result
    positionally; the WO-P000-E10.001 caller-propagation audit's AST scan
    can't see positional args, so it flagged this as "never passed" -- false
    positive, confirmed by reading the actual call (item 2.3)."""
    src = (ROOT / "application" / "compare_vehicles.py").read_text(encoding="utf-8")
    call_block = src.split("comparison = compare_vehicles(")[1][:200]
    ok = "options_council_result" in call_block
    check("e10001_compare_vehicles_passes_options_council_result", "SOURCE", ok)


def test_e10001_cli_resolves_trade_mode_from_paper_flags():
    """SOURCE -- trade_mode must be resolvable from real --paper /
    --paper-session CLI flags via _resolve_mode(), not stuck at the REAL
    default forever (WO-P000-E10.001 item 2.5 -- audit false positive,
    this is genuinely wired end to end)."""
    src = (ROOT / "cli.py").read_text(encoding="utf-8")
    ok = "_resolve_mode(" in src and "--paper" in src
    check("e10001_cli_resolves_trade_mode_from_paper_flags", "SOURCE", ok)


def test_e10001_evaluate_options_passes_is_paper():
    """SOURCE -- evaluate_options() must thread is_paper into
    build_option_spec() so the PAPER TRADE banner renders on paper-mode
    option specs (WO-P000-E10.001 item 2.4 -- confirmed gap: paper and
    live option specs were byte-identical before this fix)."""
    src = (ROOT / "application" / "evaluate_options.py").read_text(encoding="utf-8")
    ok = "is_paper: bool = False" in src and "is_paper=is_paper" in src
    check("e10001_evaluate_options_passes_is_paper", "SOURCE", ok)


def test_e10001_evaluate_spread_passes_is_paper():
    """SOURCE -- same guarantee for the spread path (WO-P000-E10.001
    item 2.4)."""
    src = (ROOT / "application" / "evaluate_spread.py").read_text(encoding="utf-8")
    ok = "is_paper: bool = False" in src and "is_paper=is_paper" in src
    check("e10001_evaluate_spread_passes_is_paper", "SOURCE", ok)


def test_e10001_commands_derives_is_paper_from_trade_mode():
    """SOURCE -- commands.py call sites must derive is_paper from the real
    trade_mode (not hardcode it) at both the spread and options evaluate
    call sites (WO-P000-E10.001 item 2.4)."""
    src = (ROOT / "application" / "commands.py").read_text(encoding="utf-8")
    ok = src.count("is_paper=(trade_mode == TradeMode.PAPER)") == 2
    check("e10001_commands_derives_is_paper_from_trade_mode", "SOURCE", ok,
          f"count={src.count('is_paper=(trade_mode == TradeMode.PAPER)')}")

def test_e10001_behavioral_inputs_orders_today():
    """BEHAVIOR -- compute_behavioral_inputs must count only today's
    order_date, not yesterday's or a PENDING record dated today counted
    twice (WO-P000-E10.001 item 2.1)."""
    from datetime import date
    from domain.behavioral_history import compute_behavioral_inputs
    from schemas import BookRecord
    today = date(2026, 8, 4)
    records = [
        BookRecord(symbol="AAPL", status="FILLED", order_date="2026-08-04"),
        BookRecord(symbol="MSFT", status="FILLED", order_date="2026-08-03"),
        BookRecord(symbol="NVDA", status="PENDING", order_date="2026-08-04"),
    ]
    result = compute_behavioral_inputs(records, today=today)
    check("e10001_behavioral_inputs_orders_today", "BEHAVIOR", result.orders_today == 2,
          f"got {result.orders_today}")


def test_e10001_behavioral_inputs_consecutive_wins():
    """BEHAVIOR -- consecutive_wins counts from the most recent CLOSED
    record backward, stopping at the first non-win (WO-P000-E10.001 item 2.1)."""
    from datetime import date
    from domain.behavioral_history import compute_behavioral_inputs
    from schemas import BookRecord
    today = date(2026, 8, 4)
    records = [
        BookRecord(symbol="AAPL", status="CLOSED", close_date="2026-08-04", realized_pnl=100.0),
        BookRecord(symbol="MSFT", status="CLOSED", close_date="2026-08-03", realized_pnl=50.0),
        BookRecord(symbol="NVDA", status="CLOSED", close_date="2026-08-02", realized_pnl=-25.0),
        BookRecord(symbol="TSLA", status="CLOSED", close_date="2026-08-01", realized_pnl=75.0),
    ]
    result = compute_behavioral_inputs(records, today=today)
    check("e10001_behavioral_inputs_consecutive_wins", "BEHAVIOR", result.consecutive_wins == 2,
          f"got {result.consecutive_wins}")


def test_e10001_behavioral_inputs_recently_stopped_out():
    """BEHAVIOR -- recently_stopped_out_symbols includes losses within the
    window and excludes older losses and wins (WO-P000-E10.001 item 2.1)."""
    from datetime import date
    from domain.behavioral_history import compute_behavioral_inputs
    from schemas import BookRecord
    today = date(2026, 8, 4)
    records = [
        BookRecord(symbol="AAPL", status="CLOSED", close_date="2026-08-03", realized_pnl=-50.0),
        BookRecord(symbol="MSFT", status="CLOSED", close_date="2026-07-20", realized_pnl=-30.0),
        BookRecord(symbol="NVDA", status="CLOSED", close_date="2026-08-02", realized_pnl=40.0),
    ]
    result = compute_behavioral_inputs(records, today=today)
    ok = result.recently_stopped_out_symbols == ["AAPL"]
    check("e10001_behavioral_inputs_recently_stopped_out", "BEHAVIOR", ok,
          f"got {result.recently_stopped_out_symbols}")


def test_e10001_evaluate_signal_wires_behavioral_inputs():
    """SOURCE -- evaluate_signal.py must pass the computed behavioral
    inputs into behavioral_vote(), not just symbol (WO-P000-E10.001 item
    2.1 -- confirmed gap, all 5 params were dead defaults, revenge-trade/
    overtrading/streak-chasing checks had never fired)."""
    src = (ROOT / "application" / "evaluate_signal.py").read_text(encoding="utf-8")
    ok = ("compute_behavioral_inputs(records)" in src
          and "recently_stopped_out_symbols=behavioral.recently_stopped_out_symbols" in src
          and "orders_today=behavioral.orders_today" in src
          and "consecutive_wins=behavioral.consecutive_wins" in src)
    check("e10001_evaluate_signal_wires_behavioral_inputs", "SOURCE", ok)

def test_e10001_earnings_window_moved_behavior_preserved():
    """BEHAVIOR -- domain.earnings_window.earnings_in_window() must still
    return True for an earnings date inside the configured window, after
    being moved out of application/evaluate_signal.py (WO-P000-E10.001
    item 2.2 -- a move, not a rewrite)."""
    from datetime import date, timedelta
    from domain.earnings_window import earnings_in_window
    import config
    near_date = (date.today() + timedelta(days=config.EARNINGS_WINDOW_FORWARD_DAYS - 1)).isoformat()
    far_date = (date.today() + timedelta(days=config.EARNINGS_WINDOW_FORWARD_DAYS + 10)).isoformat()
    ok = earnings_in_window(near_date) is True and earnings_in_window(far_date) is False
    check("e10001_earnings_window_moved_behavior_preserved", "BEHAVIOR", ok)


def test_e10001_evaluate_options_wires_macro_vote():
    """SOURCE -- evaluate_options() must call macro_vote() with
    defined_risk_confirmed=True and merge BLOCK/CAUTION into the options
    council verdict (WO-P000-E10.001 item 2.2 -- confirmed gap: options
    previously got zero earnings/binary-event check)."""
    src = (ROOT / "application" / "evaluate_options.py").read_text(encoding="utf-8")
    ok = ("macro_vote(" in src
          and "defined_risk_confirmed=True" in src
          and "macro.decision == Decision.BLOCK" in src)
    check("e10001_evaluate_options_wires_macro_vote", "SOURCE", ok)


def test_e10001_evaluate_spread_wires_macro_vote():
    """SOURCE -- evaluate_spread() must call macro_vote() with
    defined_risk_confirmed=True and merge BLOCK into the spread council
    verdict (WO-P000-E10.001 item 2.2 -- confirmed gap: spreads previously
    got zero earnings/binary-event check, evaluate_spread() never called
    the main council at all)."""
    src = (ROOT / "application" / "evaluate_spread.py").read_text(encoding="utf-8")
    ok = ("macro_vote(" in src
          and "defined_risk_confirmed=True" in src
          and "macro.decision == Decision.BLOCK" in src
          and "snapshot_raw: dict" in src)
    check("e10001_evaluate_spread_wires_macro_vote", "SOURCE", ok)


def test_e10001_commands_passes_snapshot_to_evaluate_spread():
    """SOURCE -- commands.py must pass snapshot_raw=snapshot to
    evaluate_spread() so the new MACRO check has earnings data to work
    with (WO-P000-E10.001 item 2.2)."""
    src = (ROOT / "application" / "commands.py").read_text(encoding="utf-8")
    ok = "snapshot_raw=snapshot, long_chain_path=chain_path" in src
    check("e10001_commands_passes_snapshot_to_evaluate_spread", "SOURCE", ok)


def test_e10001_spread_council_result_has_cautions_field():
    """SOURCE -- SpreadCouncilResult must have a cautions list so MACRO
    CAUTION has somewhere to go without inventing a third verdict value
    for a field documented as PASS/BLOCK-only (WO-P000-E10.001 item 2.2)."""
    src = (ROOT / "domain" / "spread_council.py").read_text(encoding="utf-8")
    ok = "cautions: list" in src
    check("e10001_spread_council_result_has_cautions_field", "SOURCE", ok)

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
