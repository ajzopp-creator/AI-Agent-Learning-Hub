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
        signal_horizon="3-5 days",
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
        signal_horizon="3-5 days",
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
