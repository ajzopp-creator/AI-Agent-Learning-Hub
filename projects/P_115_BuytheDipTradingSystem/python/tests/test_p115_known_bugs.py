"""
test_p115_known_bugs.py -- Regression guard for the P_115 Bugs Already
Fixed table in .claude/skills/p115-project-context/SKILL.md.

Only WO-P115-E2.001 has real Python code behind it (the other bugs in
that table are ThinkScript/review-layer process fixes, not testable
here). One test per checkable behavior. Run after any edit to
signal_builder.py or emit_signal.py, before calling a fix "done."

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_115_BuytheDipTradingSystem\\python\\tests\\
           test_p115_known_bugs.py

Run with:
  C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe test_p115_known_bugs.py
"""
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_115_BuytheDipTradingSystem\python")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "domain"))

RESULTS = []


def check(name, kind, passed, detail=""):
    RESULTS.append((name, kind, passed, detail))


def test_stop_fields_present_when_supplied():
    """BEHAVIOR -- build_record() must include all three WO-P115-E2.001
    stop fields in its output dict when the caller supplies values."""
    import signal_builder as sb
    rec = sb.build_record(
        symbol="AMTM",
        session_date="2026-07-06",
        signal_timestamp="2026-07-06T14:30:00Z",
        strategy="dip_buy",
        guideline_entry=100.0,
        guideline_stop=95.0,
        guideline_target=110.0,
        signal_horizon="10-15 trading days",
        confidence_level="HIGH",
        close_at_signal=100.0,
        trailing_volume_30d=1_000_000.0,
        signal_rationale="test",
        chart_timeframe="1D",
        signal_source_link="test.md",
        seq=1,
        atm_at_signal=2.5,
        atr_adjusted_stop=97.5,
        intelliscan_support_1=96.0,
        intelliscan_support_2=94.0,
    )
    ok = (
        rec.get("atr_adjusted_stop") == 97.5
        and rec.get("intelliscan_support_1") == 96.0
        and rec.get("intelliscan_support_2") == 94.0
    )
    check("stop_fields_present_when_supplied", "BEHAVIOR", ok, f"got {rec}")


def test_stop_fields_none_not_omitted_or_zero():
    """BEHAVIOR -- when stop fields aren't supplied, they must serialize
    as None in the dict -- not absent (KeyError) and not 0. P_400 depends
    on the null/absent distinction (SKILL.md AI Behavioral Rules #4)."""
    import signal_builder as sb
    rec = sb.build_record(
        symbol="AMTM",
        session_date="2026-07-06",
        signal_timestamp="2026-07-06T14:30:00Z",
        strategy="dip_buy",
        guideline_entry=100.0,
        guideline_stop=95.0,
        guideline_target=110.0,
        signal_horizon="10-15 trading days",
        confidence_level="HIGH",
        close_at_signal=100.0,
        trailing_volume_30d=1_000_000.0,
        signal_rationale="test",
        chart_timeframe="1D",
        signal_source_link="test.md",
        seq=1,
    )
    ok = (
        "atr_adjusted_stop" in rec and rec["atr_adjusted_stop"] is None
        and "intelliscan_support_1" in rec and rec["intelliscan_support_1"] is None
        and "intelliscan_support_2" in rec and rec["intelliscan_support_2"] is None
    )
    check("stop_fields_none_not_omitted_or_zero", "BEHAVIOR", ok, f"got {rec}")


def test_emit_signal_computes_atr_adjusted_stop_formula():
    """SOURCE -- emit_signal.py must compute atr_adjusted_stop as
    entry - 1x ATR(14), guarded to None when atm_at_signal is None
    (WO-P115-E2.001 formula)."""
    src = (ROOT / "application" / "emit_signal.py").read_text(encoding="utf-8")
    ok = (
        "guideline_entry - atm_at_signal" in src
        and "if atm_at_signal is not None" in src
    )
    check("emit_signal_computes_atr_adjusted_stop_formula", "SOURCE", ok)


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


def test_cli_wires_intelliscan_supports_through_to_emit_signal():
    """BEHAVIOR -- WO-P115-E3.001 (2026-08-03).

    emit_signal() has accepted intelliscan_support_1/2 since v2.2
    (WO-P115-E2.001), but cli.py never defined the arguments or passed
    them at the call site. The enrichment was unreachable from the only
    entry point Tony actually uses, and WO-P115-E2.001 closed with its
    CLI half unwired. Discovered live on the ZION emission, 2026-08-03.

    Guarantee: the CLI must define --support-1/--support-2 AND forward
    them to emit_signal as intelliscan_support_1/intelliscan_support_2.
    """
    import cli

    captured = {}

    def fake_emit(**kwargs):
        captured.update(kwargs)
        return True

    real_emit = cli.emit_signal
    real_argv = sys.argv
    cli.emit_signal = fake_emit
    sys.argv = [
        "cli.py",
        "--symbol", "TEST",
        "--session-date", "2026-08-03",
        "--timestamp", "2026-08-03T14:00:00Z",
        "--strategy", "dip_buy",
        "--entry", "100.0",
        "--stop", "95.0",
        "--target", "110.0",
        "--horizon", "10-15 trading days",
        "--confidence", "HIGH",
        "--close", "100.5",
        "--volume", "1000000",
        "--rationale", "wiring test",
        "--timeframe", "1D",
        "--source-link", "x.md",
        "--atm", "2.0",
        "--support-1", "96.5",
        "--support-2", "92.0",
    ]
    try:
        cli.main()
    finally:
        cli.emit_signal = real_emit
        sys.argv = real_argv

    assert captured.get("intelliscan_support_1") == 96.5, (
        "cli.py did not forward --support-1 to emit_signal; got "
        f"{captured.get('intelliscan_support_1')!r}"
    )
    assert captured.get("intelliscan_support_2") == 92.0, (
        "cli.py did not forward --support-2 to emit_signal; got "
        f"{captured.get('intelliscan_support_2')!r}"
    )