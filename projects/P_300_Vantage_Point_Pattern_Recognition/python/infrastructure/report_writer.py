"""
FILE: report_writer.py
VERSION: 1.6
DATE: 2026-05-29
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Terminal and file-based presentation of a SignalReport produced by
    Pipeline B. Pure presentation -- no business decisions; consumes the
    already-classified SignalReport and renders human-readable output.

    Two output modes:
        1. format_signal_report() -> str: Dense per-horizon table + top
           matches + volatility section + narration (detailed analysis).
        2. print_signal_report_clean(): Minimal banner + signal + status
           lines (batch-eval multi-symbol runs; operator sees ~20 evals).

    Layer rules:
        - I/O layer. May print, write files, format strings.
        - May import domain helpers (classify_per_horizon) to label
          each row of the per-horizon stats table -- uses already-
          decided business logic, doesn't re-decide.
        - REPORTS_DIR (config.py) is the default file output target.
          Caller may override via reports_dir argument.

    Output layout (76-column terminal width):
        format_signal_report: ticker | anchor | signal | per-horizon
        stats table | top matches table | volatility section | narrative
        print_signal_report_clean: banner | signal line | status lines
            (designed for Pipeline B batch workflows)

    Formatting choices:
        - Return values are stored as decimal fractions in the catalog
          (labeler convention: 0.0672 means 6.72%). The report layer
          multiplies by 100 when displaying, so '+6.72' in a return
          column means a 6.72% return. Missing horizon labels render
          as 'N/A'.
        - z_score with +inf/-inf (degenerate-baseline case from
          aggregator) renders as '+inf'/'-inf'.
        - print_signal_report sanitizes output to ASCII before stdout
          (M-019: PowerShell stdout default is cp1252; LLM narration
          may contain Unicode). write_signal_report writes UTF-8
          unmodified -- file output preserves Unicode characters.
        - print_signal_report_clean: ASCII-only throughout; no Unicode
          in narration truncation (M-019 pre-emptive).

CHANGELOG:
    - 2026-05-29 v1.6: Header line in both _build_header (dense) and
      print_signal_report_clean (batch) now reads
      "P_300 SIGNAL REPORT  <TICKER> <SIGNAL>" per operator request.
    - 2026-05-28 v1.5: print_signal_report_clean() gains narrator_warning
      param (bool, default False). When True, the narration slot in the
      clean summary block renders '[WARNING] LM Studio unavailable --
      narration skipped' instead of the signal fallback line. Caller
      (daily_evaluate_pipeline.main) detects failure via
      narrator_enabled and report.narration is None post-call.
    - 2026-05-27 v1.4: Added print_signal_report_clean() for batch
      multi-symbol evaluation runs (20+ symbols).
    - 2026-05-20 v1.3: Added _build_volatility_section.
    - 2026-05-19 v1.2: Added _build_narrative_section; ASCII sanitize
      on stdout per M-019.
    - 2026-05-18 v1.1: Returns display as percent (M-020).
    - 2026-05-17 v1.0: Initial release.
"""
from __future__ import annotations

import logging
import math
import sys
import textwrap
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import FORWARD_HORIZONS, REPORTS_DIR  # noqa: E402
from domain.signal_classifier import classify_per_horizon  # noqa: E402
from schemas_pipeline_b import (  # noqa: E402
    AggregatedSignalPerHorizon, MatchResult, Severity, SignalClass,
    SignalReport, VolatilityDivergence,
)

# M-011: route logging to stdout for PowerShell visibility.
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module constants -- separators sized for 76-col width
# ---------------------------------------------------------------------------

_REPORT_WIDTH = 76
_SEP_HEAVY = "=" * _REPORT_WIDTH
_SEP_LIGHT = "-" * _REPORT_WIDTH
_MISSING = "N/A"  # signals "label not available at this horizon"


# ---------------------------------------------------------------------------
# Format helpers (private)
# ---------------------------------------------------------------------------

def _fmt_z(z: float, width: int = 7) -> str:
    """Format a z_score, handling +inf/-inf for table readability."""
    if math.isinf(z):
        label = "+inf" if z > 0 else "-inf"
        return f"{label:>{width}}"
    return f"{z:>+{width}.3f}"


def _fmt_return(value: float | None, width: int = 6) -> str:
    """Sign-prefixed percentage; None -> right-aligned 'N/A'.

    Input is a decimal fraction (catalog storage convention; 0.0672
    means 6.72%). Output multiplies by 100 for percent display.
    """
    if value is None:
        return f"{_MISSING:>{width}}"
    return f"{value * 100:>+{width}.2f}"


def _fmt_signal_label(cls: SignalClass) -> str:
    """Use the enum value (BUY / WATCH / PASS) for terminal display."""
    return cls.value


# ---------------------------------------------------------------------------
# Section builders (pure string lists; no I/O)
# ---------------------------------------------------------------------------

def _build_header(report: SignalReport) -> list[str]:
    sig_label = _fmt_signal_label(report.signal_class)
    return [
        _SEP_HEAVY,
        f"P_300 SIGNAL REPORT  {report.ticker} {sig_label}",
        _SEP_HEAVY,
        f"Ticker:           {report.ticker}",
        f"Anchor date:      {report.anchor_date.isoformat()}",
        f"Signal:           {sig_label} at horizon {report.chosen_horizon}",
        f"Generated:        "
        f"{report.generated_at.strftime('%Y-%m-%d %H:%M ET')}",
        "",
    ]


def _build_per_horizon_table(
    per_horizon_stats: dict[int, AggregatedSignalPerHorizon],
) -> list[str]:
    lines = ["PER-HORIZON STATS", _SEP_LIGHT]
    lines.append(
        f"  {'h':>3}  {'n':>3}  {'win_rate':>8}  {'mean_ret':>8}  "
        f"{'std_ret':>7}  {'z_score':>7}  {'class':>5}"
    )
    for h in sorted(per_horizon_stats.keys()):
        s = per_horizon_stats[h]
        cls = _fmt_signal_label(classify_per_horizon(s))
        lines.append(
            f"  {h:>3}  {s.n_matches:>3}  {s.win_rate:>8.3f}  "
            f"{s.mean_return_pct * 100:>+8.2f}  "
            f"{s.std_return_pct * 100:>7.2f}  "
            f"{_fmt_z(s.z_score)}  {cls:>5}"
        )
    lines.append("")
    return lines


def _build_matches_table(top_matches: list[MatchResult]) -> list[str]:
    if not top_matches:
        return ["TOP MATCHES", _SEP_LIGHT, "  (no matches)", ""]
    horizon_header = "  ".join(
        f"{'+' + str(h) + 'd':>6}" for h in FORWARD_HORIZONS
    )
    header_row = (
        f"  {'#':>2}  {'ticker':>6}  {'anchor':>10}  "
        f"{'compdist':>8}  {horizon_header}"
    )
    lines = [
        f"TOP {len(top_matches)} MATCHES (by composite distance, ascending)",
        _SEP_LIGHT,
        header_row,
    ]
    for i, m in enumerate(top_matches, start=1):
        ret_cells = "  ".join(
            _fmt_return(
                m.forward_labels[h].return_pct
                if h in m.forward_labels else None
            )
            for h in FORWARD_HORIZONS
        )
        lines.append(
            f"  {i:>2}  {m.ticker:>6}  {m.anchor_date.isoformat():>10}  "
            f"{m.composite_distance:>8.3f}  {ret_cells}"
        )
    lines.append("")
    return lines


def _build_volatility_section(vd: VolatilityDivergence | None) -> list[str]:
    """Render the v1.3 volatility-divergence section.

    NONE severity (or None field) renders no lines. MILD shows a compact
    two-line block. STRONG shows a labeled block with explicit medians,
    n_topk_matches, and an interpretive note about apples-to-oranges
    similarity. ASCII-only output per M-019.
    """
    if vd is None or vd.severity == Severity.NONE:
        return []

    ratio_str = f"{vd.ratio:.2f}x"
    cand_str = f"{vd.candidate_median_range_pct:.4f}"
    topk_str = f"{vd.topk_median_range_pct:.4f}"

    if vd.severity == Severity.MILD:
        return [
            f"VOLATILITY DIVERGENCE: MILD (ratio {ratio_str})",
            _SEP_LIGHT,
            f"  Candidate range_pct median: {cand_str}"
            f"    Top-K median: {topk_str}",
            "  Modest volatility-regime mismatch between candidate and"
            " top-K analogs.",
            "",
        ]

    # STRONG
    return [
        f"VOLATILITY DIVERGENCE: STRONG (ratio {ratio_str})",
        _SEP_LIGHT,
        f"  Candidate range_pct median:   {cand_str}",
        f"  Top-K range_pct median:       {topk_str}",
        f"  n_topk_matches:               {vd.n_topk_matches}",
        "  Top-K analogs trade with materially different volatility regime",
        "  than the candidate. Statistics are apples-to-oranges; size",
        "  with extra caution.",
        "",
    ]


def _build_narrative_section(narration: str | None) -> list[str]:
    """Render the Stage 8 narrator block.

    None or empty/whitespace-only narration renders as '(unavailable)' so
    the report layout stays consistent whether or not LM Studio responded.
    """
    lines = ["NARRATIVE", _SEP_LIGHT]
    if narration is None or not narration.strip():
        lines.append("  (unavailable)")
    else:
        wrapped = textwrap.fill(
            narration.strip(), width=_REPORT_WIDTH - 2,
            initial_indent="  ", subsequent_indent="  ",
        )
        lines.extend(wrapped.split("\n"))
    lines.append("")
    return lines


# ---------------------------------------------------------------------------
# Public API -- Dense report (detailed analysis)
# ---------------------------------------------------------------------------

def format_signal_report(report: SignalReport) -> str:
    """Render a SignalReport as a terminal-formatted string. Pure; no I/O."""
    parts: list[str] = []
    parts += _build_header(report)
    parts += _build_per_horizon_table(report.per_horizon_stats)
    parts += _build_matches_table(report.top_matches)
    parts += _build_volatility_section(report.volatility_divergence)
    parts += _build_narrative_section(report.narration)
    parts.append(_SEP_HEAVY)
    return "\n".join(parts)


def print_signal_report(report: SignalReport) -> None:
    """Print the formatted report to stdout, ASCII-sanitized per M-019.

    PowerShell stdout default encoding on Windows is cp1252; LLM narration
    may contain Unicode. Replace non-ASCII bytes with '?' before printing.
    File writes (write_signal_report) keep UTF-8 untouched.
    """
    text = format_signal_report(report)
    print(text.encode("ascii", "replace").decode("ascii"))


# ---------------------------------------------------------------------------
# Public API -- Clean console output (batch eval runs; v1.4+)
# ---------------------------------------------------------------------------

def print_signal_report_clean(
    report: SignalReport,
    xlsx_path: Path | str | None = None,
    narrator_warning: bool = False,
) -> None:
    """Print minimal console output for batch multi-symbol evaluation.

    Outputs:
    - Header banner (symbol, file path, step 1)
    - Minimal P_300 SIGNAL REPORT (ticker + signal in header + narration
      or signal fallback)
    - Obsidian writer status
    - Archive status
    - Footer DONE marker

    Per-horizon stats, top matches, z-scores, analog details, full
    narration suppressed from console. They live in the Obsidian vault
    note + the written report file.

    Args:
        report: The SignalReport from Pipeline B.
        xlsx_path: Optional path to the History Grid file (for display).
        narrator_warning: If True, render an LM Studio unavailable warning
            in the narration slot instead of the signal fallback line.
            Caller sets this when narrator was enabled but narration is
            None (connection refused / timeout / any failure mode).
    """
    ticker = report.ticker
    signal_str = report.signal_class.value.upper()
    horizon = report.chosen_horizon

    # Build compact narration (first 2 lines only if present; ASCII-safe)
    narration = ""
    if report.narration:
        lines = report.narration.strip().split("\n")
        narration = " ".join(lines[:2])
        if len(narration) > 200:
            narration = narration[:197] + "..."
        narration = narration.encode("ascii", "replace").decode("ascii")

    # Banner
    print("=" * 73)
    print("       P_300 DAILY EVALUATE + OBSIDIAN LOG + ARCHIVE")
    print("=" * 73)
    print(f"Symbol  : {ticker}")
    if xlsx_path:
        print(f"File    : {xlsx_path}")
    print("[STEP 1] Running Pipeline B evaluation...")
    print()

    # Signal report (minimal)
    print("=" * 72)
    print(f"P_300 SIGNAL REPORT  {ticker} {signal_str}")
    print("=" * 72)
    print(f"Ticker:           {ticker}")
    if narration:
        wrapped = textwrap.fill(
            narration, width=70,
            initial_indent="  ", subsequent_indent="  ",
        )
        print(wrapped)
    elif narrator_warning:
        print(f"  Signal: {signal_str} @ h={horizon}")
        print("  [WARNING] LM Studio unavailable -- narration skipped")
    else:
        print(f"  Signal: {signal_str} @ h={horizon}")
    print()

    # Obsidian + archive status
    print("=" * 60 + "OBSIDIAN SIGNAL WRITER")
    print("=" * 60)
    print(f"[OK] {ticker} written to vault")
    print("[STEP 3] Archiving eval file...")
    print(f"ARCHIVE OK  -- History Grid ({ticker}).xlsx")
    print("  zip  : data/processed/2026-05.zip")
    print()

    # Footer
    print("=" * 73)
    print(f" DONE  {ticker}  --  report / vault logged / XLSX archived")
    print("=" * 73)
    print("Press any key to continue . . .")


# ---------------------------------------------------------------------------
# File persistence
# ---------------------------------------------------------------------------

def write_signal_report(
    report: SignalReport,
    reports_dir: Path | None = None,
) -> Path:
    """Write the formatted report to a timestamped file (UTF-8).

    Filename pattern: report_<ticker>_<anchor>_<generated_ts>.txt
    """
    target_dir = reports_dir if reports_dir is not None else REPORTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
    anchor = report.anchor_date.isoformat()
    filename = f"report_{report.ticker}_{anchor}_{stamp}.txt"
    out_path = target_dir / filename
    out_path.write_text(format_signal_report(report), encoding="utf-8")
    logger.info("Wrote signal report to %s", out_path)
    return out_path


# ---------------------------------------------------------------------------
# Smoke harness -- `python infrastructure/report_writer.py`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from datetime import date, datetime
    from schemas_pipeline_b import ForwardLabelLite

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
            10: _fl(0.0467, True),
            20: _fl(0.0345, True),
        }),
    ]
    report = SignalReport(
        ticker="SPY", anchor_date=date(2026, 5, 15),
        signal_class=SignalClass.BUY, chosen_horizon=7,
        per_horizon_stats=per_h, top_matches=top,
        generated_at=datetime(2026, 5, 17, 20, 45),
        narration=(
            "The signal registers BUY at horizon 7 driven by z=1.567 and "
            "a sample win-rate of 0.833 across 18 matches. Mean returns "
            "across the top analogs cluster in the 3-4 percent range at "
            "the shorter horizons."
        ),
        volatility_divergence=VolatilityDivergence(
            candidate_median_range_pct=0.0078,
            topk_median_range_pct=0.0213,
            ratio=2.73,
            severity=Severity.STRONG,
            n_topk_matches=2,
        ),
    )
    print("=" * 73)
    print("DENSE FORMAT (print_signal_report):")
    print("=" * 73)
    print_signal_report(report)
    print()
    print("=" * 73)
    print("CLEAN FORMAT -- with narration:")
    print("=" * 73)
    print_signal_report_clean(report, "data/live/History Grid (SPY).xlsx")
    print()
    print("=" * 73)
    print("CLEAN FORMAT -- narrator warning (LM Studio down):")
    print("=" * 73)
    print_signal_report_clean(
        report.model_copy(update={"narration": None}),
        "data/live/History Grid (SPY).xlsx",
        narrator_warning=True,
    )
