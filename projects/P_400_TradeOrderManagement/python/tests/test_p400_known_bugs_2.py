"""
test_p400_known_bugs_2.py -- Regression guard for the P_400 Bugs Already
Fixed table in .claude/skills/p400-project-context/SKILL.md.

Split from test_p400_known_bugs.py at WO-P400-E5.004 (2026-08-08) when
that file approached the 300-line cap -- see that file's module docstring
for the split convention and why this file exists. This file holds the
WO-P000-E10.001 caller-propagation audit cluster. New entries after this
file also approaches 300 lines go into test_p400_known_bugs_3.py; no
wiring needed, pytest auto-discovers every test_*.py file under tests\\.

One test per CLOSED WO with a concrete, checkable fix. Run this after
ANY edit to the files it covers, and before calling a fix "done." Per
WO-P020-E1.003's Hub-wide rule (2026-07-06), any future bug fixed in
this project gets a matching test added here in the same session.

Two kinds of test, both labeled in each docstring:
  BEHAVIOR -- calls the real function against a tiny synthetic input and
              checks the actual output. Confirms the bug cannot recur.
  SOURCE   -- greps the file for the fix's signature. Cheaper, but only
              confirms the fix line is still there, not full behavior.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_400_TradeOrderManagement\\python\\tests\\
           test_p400_known_bugs_2.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe -m pytest test_p400_known_bugs_2.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = ROOT / "domain"
APPLICATION = ROOT / "application"

def test_e10001_compare_vehicles_passes_options_council_result():
    """SOURCE -- compare_vehicles.py call site must pass options_council_result
    positionally; the WO-P000-E10.001 caller-propagation audit's AST scan
    can't see positional args, so it flagged this as "never passed" -- false
    positive, confirmed by reading the actual call (item 2.3)."""
    src = (ROOT / "application" / "compare_vehicles.py").read_text(encoding="utf-8")
    call_block = src.split("comparison = compare_vehicles(")[1][:200]
    assert "options_council_result" in call_block


def test_e10001_cli_resolves_trade_mode_from_paper_flags():
    """SOURCE -- trade_mode must be resolvable from real --paper /
    --paper-session CLI flags via _resolve_mode(), not stuck at the REAL
    default forever (WO-P000-E10.001 item 2.5 -- audit false positive,
    this is genuinely wired end to end)."""
    src = (ROOT / "cli.py").read_text(encoding="utf-8")
    assert "_resolve_mode(" in src and "--paper" in src


def test_e10001_evaluate_options_passes_is_paper():
    """SOURCE -- evaluate_options() must thread is_paper into
    build_option_spec() so the PAPER TRADE banner renders on paper-mode
    option specs (WO-P000-E10.001 item 2.4 -- confirmed gap: paper and
    live option specs were byte-identical before this fix)."""
    src = (ROOT / "application" / "evaluate_options.py").read_text(encoding="utf-8")
    assert "is_paper: bool = False" in src and "is_paper=is_paper" in src


def test_e10001_evaluate_spread_passes_is_paper():
    """SOURCE -- same guarantee for the spread path (WO-P000-E10.001
    item 2.4)."""
    src = (ROOT / "application" / "evaluate_spread.py").read_text(encoding="utf-8")
    assert "is_paper: bool = False" in src and "is_paper=is_paper" in src


def test_e10001_commands_derives_is_paper_from_trade_mode():
    """SOURCE -- commands.py call sites must derive is_paper from the real
    trade_mode (not hardcode it) at both the spread and options evaluate
    call sites (WO-P000-E10.001 item 2.4)."""
    src = (ROOT / "application" / "commands.py").read_text(encoding="utf-8")
    count = src.count("is_paper=(trade_mode == TradeMode.PAPER)")
    assert count == 2, f"count={count}"


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
    assert result.orders_today == 2, f"got {result.orders_today}"


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
    assert result.consecutive_wins == 2, f"got {result.consecutive_wins}"


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
    assert result.recently_stopped_out_symbols == ["AAPL"], \
        f"got {result.recently_stopped_out_symbols}"


def test_e10001_evaluate_signal_wires_behavioral_inputs():
    """SOURCE -- evaluate_signal.py must pass the computed behavioral
    inputs into behavioral_vote(), not just symbol (WO-P000-E10.001 item
    2.1 -- confirmed gap, all 5 params were dead defaults, revenge-trade/
    overtrading/streak-chasing checks had never fired)."""
    src = (ROOT / "application" / "evaluate_signal.py").read_text(encoding="utf-8")
    assert ("compute_behavioral_inputs(records)" in src
            and "recently_stopped_out_symbols=behavioral.recently_stopped_out_symbols" in src
            and "orders_today=behavioral.orders_today" in src
            and "consecutive_wins=behavioral.consecutive_wins" in src)


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
    assert earnings_in_window(near_date) is True and earnings_in_window(far_date) is False


def test_e10001_evaluate_options_wires_macro_vote():
    """SOURCE -- evaluate_options() must call macro_vote() with
    defined_risk_confirmed=True and merge BLOCK/CAUTION into the options
    council verdict (WO-P000-E10.001 item 2.2 -- confirmed gap: options
    previously got zero earnings/binary-event check)."""
    src = (ROOT / "application" / "evaluate_options.py").read_text(encoding="utf-8")
    assert ("macro_vote(" in src
            and "defined_risk_confirmed=True" in src
            and "macro.decision == Decision.BLOCK" in src)


def test_e10001_evaluate_spread_wires_macro_vote():
    """SOURCE -- evaluate_spread() must call macro_vote() with
    defined_risk_confirmed=True and merge BLOCK into the spread council
    verdict (WO-P000-E10.001 item 2.2 -- confirmed gap: spreads previously
    got zero earnings/binary-event check, evaluate_spread() never called
    the main council at all)."""
    src = (ROOT / "application" / "evaluate_spread.py").read_text(encoding="utf-8")
    assert ("macro_vote(" in src
            and "defined_risk_confirmed=True" in src
            and "macro.decision == Decision.BLOCK" in src
            and "snapshot_raw: dict" in src)


def test_e10001_commands_passes_snapshot_to_evaluate_spread():
    """SOURCE -- commands.py must pass snapshot_raw=snapshot to
    evaluate_spread() so the new MACRO check has earnings data to work
    with (WO-P000-E10.001 item 2.2)."""
    src = (ROOT / "application" / "commands.py").read_text(encoding="utf-8")
    assert "snapshot_raw=snapshot, long_chain_path=chain_path" in src


def test_e10001_spread_council_result_has_cautions_field():
    """SOURCE -- SpreadCouncilResult must have a cautions list so MACRO
    CAUTION has somewhere to go without inventing a third verdict value
    for a field documented as PASS/BLOCK-only (WO-P000-E10.001 item 2.2)."""
    src = (ROOT / "domain" / "spread_council.py").read_text(encoding="utf-8")
    assert "cautions: list" in src
