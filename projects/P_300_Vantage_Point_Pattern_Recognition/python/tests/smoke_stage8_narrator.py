"""
FILE: smoke_stage8_narrator.py
VERSION: 1.0
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
LAYER: tests
DESCRIPTION:
    Stage 8 smoke harness for the Post-Decision Narrator path.

    Five checks:
      1. domain.narrator_prompt.build_narrator_user_prompt — pure logic,
         no I/O, structural assertions on the produced prompt string.
      2. infrastructure.llm_client.call_lm_studio — returns None against
         an unreachable endpoint (port 9999); never raises.
      3. infrastructure.report_writer.format_signal_report — renders
         cleanly with narration=None (the `(unavailable)` path).
      4. infrastructure.report_writer.format_signal_report — renders
         and wraps narration text at the 76-col report width.
      5. application.daily_evaluate_pipeline.run_daily_evaluate — two
         runs on the same live SPY XLSX, narrator_enabled=False vs
         narrator_enabled=True, produce IDENTICAL signal_class +
         chosen_horizon + per-horizon stats field-by-field. NFR-1
         verification: narrator presence/output must not affect the
         deterministic decision path. Test 5 auto-skips if the live
         SPY XLSX is not present or the catalog has no PATTERN_IDENT
         patterns; either case prints SKIP rather than failing.

    Invocation (from project root in ISE):
        python tests/smoke_stage8_narrator.py

    Exit code: 0 if all checks pass (skipped tests count as pass);
    1 if any assertion fails.

CHANGELOG:
    - 2026-05-19 v1.0: Initial Stage 8 release. Final file of Stage 8
      build (#8 of 8).
"""
from __future__ import annotations

import math
import sys
from datetime import date, datetime
from pathlib import Path

# sys.path bootstrap -- make python/ importable from python/tests/.
# _PROJECT_ROOT is also used below (line ~220) to locate data/live/ --
# kept as a real project-root variable, not collapsed into _PYTHON_DIR.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_PYTHON_DIR = _PROJECT_ROOT / "python"
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from application.daily_evaluate_pipeline import run_daily_evaluate  # noqa: E402
from domain.narrator_prompt import (  # noqa: E402
    NARRATOR_SYSTEM_PROMPT, build_narrator_user_prompt,
)
from infrastructure.llm_client import call_lm_studio  # noqa: E402
from infrastructure.report_writer import format_signal_report  # noqa: E402
from schemas_pipeline_b import (  # noqa: E402
    AggregatedSignalPerHorizon, ForwardLabelLite, MatchResult, SignalClass,
    SignalReport,
)


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic fixture helpers (compact constructors)
# ─────────────────────────────────────────────────────────────────────────────

def _h(h, n, wr, mr, sr, z):
    return AggregatedSignalPerHorizon(
        horizon_days=h, n_matches=n, win_rate=wr,
        mean_return_pct=mr, std_return_pct=sr, z_score=z,
    )


def _fl(r, p):
    return ForwardLabelLite(return_pct=r, is_profitable=p)


def _mr(pid, t, d, cd, labels):
    return MatchResult(
        pattern_instance_id=pid, ticker=t, anchor_date=d,
        composite_distance=cd, per_feature_distances={},
        forward_labels=labels,
    )


def _make_report(narration: str | None = None) -> SignalReport:
    """Build a synthetic SignalReport for tests 1, 3, 4."""
    per_h = {
        5: _h(5, 18, 0.778, 0.0342, 0.0215, 1.234),
        7: _h(7, 18, 0.833, 0.0418, 0.0283, 1.567),
        10: _h(10, 17, 0.706, 0.0305, 0.0291, 0.987),
        15: _h(15, 15, 0.667, 0.0289, 0.0312, 0.456),
        20: _h(20, 12, 0.583, 0.0214, 0.0345, 0.123),
    }
    top = [
        _mr(42, "SPY", date(2024, 11, 14), 0.234, {
            5: _fl(0.0581, True), 7: _fl(0.0642, True),
            10: _fl(0.0519, True), 15: _fl(0.0488, True),
            20: _fl(0.0421, True),
        }),
        _mr(83, "QQQ", date(2025, 3, 8), 0.281, {
            5: _fl(0.0412, True), 7: _fl(-0.0103, False),
            10: _fl(0.0467, True), 20: _fl(0.0345, True),
        }),
    ]
    return SignalReport(
        ticker="SPY", anchor_date=date(2026, 5, 15),
        signal_class=SignalClass.BUY, chosen_horizon=7,
        per_horizon_stats=per_h, top_matches=top,
        generated_at=datetime(2026, 5, 17, 20, 45),
        narration=narration,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — build_narrator_user_prompt produces structured non-empty text
# ─────────────────────────────────────────────────────────────────────────────

def test_1_build_narrator_user_prompt() -> None:
    report = _make_report()
    prompt = build_narrator_user_prompt(report)
    assert isinstance(prompt, str), "prompt must be a string"
    assert len(prompt) > 200, f"prompt too short ({len(prompt)} chars)"
    # Structural anchors
    assert "P_300 Signal Report" in prompt, "missing report header"
    assert "Ticker: SPY" in prompt, "missing ticker line"
    assert "2026-05-15" in prompt, "missing anchor date"
    assert "BUY at horizon 7" in prompt, "missing signal class + horizon"
    assert "Per-horizon stats:" in prompt, "missing per-horizon section"
    assert "Top 5 closest historical analogs" in prompt, "missing top-5 section"
    # M-020: percentages shown as %, not raw decimals (0.0418 -> +4.18%)
    assert "+4.18%" in prompt, "mean_return_pct not multiplied by 100"
    # System prompt constant should also be a non-empty string
    assert isinstance(NARRATOR_SYSTEM_PROMPT, str)
    assert len(NARRATOR_SYSTEM_PROMPT) > 100
    assert "P_300 Post-Decision Narrator" in NARRATOR_SYSTEM_PROMPT


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — llm_client returns None on unreachable endpoint
# ─────────────────────────────────────────────────────────────────────────────

def test_2_llm_client_returns_none_on_unreachable() -> None:
    # Port 9999 is almost never bound. Short timeout to keep the test fast.
    result = call_lm_studio(
        "test system", "test user",
        base_url="http://localhost:9999/v1",
        timeout_seconds=3,
    )
    assert result is None, f"expected None on unreachable; got {result!r}"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — report renders with narration=None
# ─────────────────────────────────────────────────────────────────────────────

def test_3_report_renders_with_no_narration() -> None:
    report = _make_report(narration=None)
    output = format_signal_report(report)
    assert "NARRATIVE" in output, "missing NARRATIVE section header"
    assert "(unavailable)" in output, "missing (unavailable) marker"
    # Other sections still intact
    assert "P_300 SIGNAL REPORT" in output
    assert "PER-HORIZON STATS" in output


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — report renders + wraps narration text at 76 cols
# ─────────────────────────────────────────────────────────────────────────────

def test_4_report_renders_with_narration_set() -> None:
    # Long narration that forces line wrapping.
    narration = (
        "The signal registers BUY at horizon 7 driven by z=1.567 and a "
        "sample win-rate of 0.833 across 18 matches. Mean returns across "
        "the top analogs cluster in the 3-4 percent range at the shorter "
        "horizons. Both surfaced matches are post-2024 SPY/QQQ patterns "
        "with broadly positive forward outcomes through the 20-day horizon."
    )
    report = _make_report(narration=narration)
    output = format_signal_report(report)
    assert "NARRATIVE" in output
    assert "(unavailable)" not in output, "narration set but unavailable rendered"
    # Some fragment of the narration must appear
    assert "registers BUY at horizon 7" in output, "narration fragment missing"
    # Every line in the rendered output must fit the 76-col width
    over_width = [
        line for line in output.split("\n") if len(line) > 76
    ]
    assert not over_width, (
        f"{len(over_width)} line(s) exceed 76 cols; first: {over_width[0]!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — NFR-1: narrator on/off produces identical signal + stats
# ─────────────────────────────────────────────────────────────────────────────

def _stats_identical(
    s1: AggregatedSignalPerHorizon, s2: AggregatedSignalPerHorizon,
) -> bool:
    """Field-by-field equality with inf-aware z_score handling."""
    if s1.n_matches != s2.n_matches:
        return False
    if s1.win_rate != s2.win_rate:
        return False
    if s1.mean_return_pct != s2.mean_return_pct:
        return False
    if s1.std_return_pct != s2.std_return_pct:
        return False
    # z_score may be +/- inf in degenerate-baseline cases
    if math.isinf(s1.z_score) or math.isinf(s2.z_score):
        return (
            math.isinf(s1.z_score) and math.isinf(s2.z_score)
            and (s1.z_score > 0) == (s2.z_score > 0)
        )
    return s1.z_score == s2.z_score


def test_5_signal_unaffected_by_narrator() -> None:
    xlsx = _PROJECT_ROOT / "data" / "live" / "History Grid (SPY).xlsx"
    if not xlsx.exists():
        print(f"  SKIP: {xlsx.name} not found at {xlsx.parent}")
        return

    try:
        r_off = run_daily_evaluate(
            xlsx, narrator_enabled=False, write_file=False,
        )
    except RuntimeError as e:
        if "no PATTERN_IDENT" in str(e):
            print(f"  SKIP: catalog empty -- {e}")
            return
        raise

    r_on = run_daily_evaluate(
        xlsx, narrator_enabled=True, write_file=False,
    )

    # Signal-side: identical in every observable way
    assert r_off.signal_class == r_on.signal_class, (
        f"signal_class drift: off={r_off.signal_class} on={r_on.signal_class}"
    )
    assert r_off.chosen_horizon == r_on.chosen_horizon, (
        f"chosen_horizon drift: off={r_off.chosen_horizon} on={r_on.chosen_horizon}"
    )
    assert set(r_off.per_horizon_stats.keys()) == set(
        r_on.per_horizon_stats.keys()
    ), "per_horizon_stats horizon set drift"
    for h, s_off in r_off.per_horizon_stats.items():
        s_on = r_on.per_horizon_stats[h]
        assert _stats_identical(s_off, s_on), (
            f"per-horizon stats drift at h={h}: off={s_off} on={s_on}"
        )

    # Narration: off must be None; on may be None or non-empty string
    assert r_off.narration is None, (
        f"narrator_enabled=False produced narration: {r_off.narration!r}"
    )
    if r_on.narration is None:
        print("  NOTE: LM Studio may be down or model not loaded "
              "-- r_on.narration is None (signal still emitted clean)")
    else:
        print(f"  NOTE: LM Studio returned narration "
              f"({len(r_on.narration)} chars)")


# ─────────────────────────────────────────────────────────────────────────────
# Test runner
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    tests = [
        test_1_build_narrator_user_prompt,
        test_2_llm_client_returns_none_on_unreachable,
        test_3_report_renders_with_no_narration,
        test_4_report_renders_with_narration_set,
        test_5_signal_unaffected_by_narrator,
    ]
    failed: list[str] = []
    print("=" * 76)
    print("P_300 STAGE 8 SMOKE -- Narrator path")
    print("=" * 76)
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
        except AssertionError as exc:
            failed.append(t.__name__)
            print(f"FAIL: {t.__name__}: {exc}")
    print("=" * 76)
    if failed:
        print(f"{len(failed)} test(s) failed: {', '.join(failed)}")
        return 1
    print(f"All {len(tests)} Stage 8 smoke tests PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
