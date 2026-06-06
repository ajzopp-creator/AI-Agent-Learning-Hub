"""
FILE: narrator_prompt.py
VERSION: 1.0
DATE: 2026-05-19
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Builds the system + user prompts for the Stage 8 Post-Decision Narrator.
    Pure function — no I/O, no network, no DB. Same input always produces
    same output.

    The narrator runs AFTER classify_signal() emits the structured
    SignalReport. The decision path (BUY/WATCH/PASS) is fully deterministic
    Python; this module produces only the text input to the LLM, never
    consumes its output.

    NFR-1 hard rule: the LLM is NEVER in the decision path. This module's
    output is exclusively for human-readable summarization downstream.

    Per Stage 8 decision A2 (locked 2026-05-19): top 5 matches in the
    prompt, not full top 20 — the narrator's executive summary doesn't
    need the tail; the full top 20 lives in the structured report and the
    file output.

    Per M-020: forward_labels.return_pct is stored as decimal fraction
    (0.0672 represents 6.72%); display × 100 at this prompt-build boundary,
    same convention as report_writer.

LAYER SEPARATION:
    - This module exports NARRATOR_SYSTEM_PROMPT (constant) and
      build_narrator_user_prompt(report) -> str (pure function).
    - infrastructure/llm_client.py is generic — it accepts system + user
      strings and doesn't know about SignalReport.
    - application/daily_evaluate_pipeline.py glues both: builds the prompts
      here, hands them to llm_client, attaches narration to the report.

CHANGELOG:
    - 2026-05-19 v1.0: Initial Stage 8 release.
"""
from __future__ import annotations

from schemas_pipeline_b import SignalReport


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT — constant, same for every narration call
# ─────────────────────────────────────────────────────────────────────────────

NARRATOR_SYSTEM_PROMPT: str = (
    "You are the P_300 Post-Decision Narrator. You receive a structured "
    "Pipeline B signal report and produce a brief plain-prose summary for "
    "the trader. Your role is read-only on the decision output — you do "
    "not produce or alter BUY/WATCH/PASS classifications, only describe "
    "what the structured report says. Keep summaries to a single paragraph "
    "of 2-4 sentences. Factual and dry tone. No advice, no hedging, no "
    "markdown, no bullet points, no headers — plain prose only."
)


# ─────────────────────────────────────────────────────────────────────────────
# USER PROMPT — built per-report
# ─────────────────────────────────────────────────────────────────────────────

def build_narrator_user_prompt(report: SignalReport) -> str:
    """
    Build the user-content prompt from a SignalReport.

    Returns a single string containing the structured report data followed
    by a closing instruction line. Pure function — deterministic.

    Decimal-fraction returns multiplied by 100 at the display boundary
    (M-020): mean_return_pct, std_return_pct, and forward_labels[h].return_pct
    are all stored as decimals and rendered here as human-readable percentages.

    Top 5 matches included (Stage 8 decision A2); top 20 is intentionally
    not in the prompt — the executive summary doesn't need the tail.
    """
    lines: list[str] = [
        "P_300 Signal Report",
        "",
        f"Ticker: {report.ticker}",
        f"Anchor date: {report.anchor_date}",
        f"Final signal: {report.signal_class.value} at horizon {report.chosen_horizon}",
        f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M ET')}",
        "",
        "Per-horizon stats:",
    ]

    # Per-horizon stats lines, ordered by horizon ascending.
    for h in sorted(report.per_horizon_stats.keys()):
        stats = report.per_horizon_stats[h]
        mean_pct = stats.mean_return_pct * 100.0
        std_pct = stats.std_return_pct * 100.0
        lines.append(
            f"  h={h:<3} n={stats.n_matches:<3} "
            f"win_rate={stats.win_rate:.3f} "
            f"mean_ret={mean_pct:+.2f}% "
            f"std_ret={std_pct:.2f}% "
            f"z={stats.z_score:+.3f}"
        )

    lines.append("")
    lines.append("Top 5 closest historical analogs (sorted by composite distance ascending):")

    top_5 = report.top_matches[:5]
    for idx, match in enumerate(top_5, start=1):
        ret_5d = match.forward_labels.get(5)
        ret_20d = match.forward_labels.get(20)
        ret_5d_str = (
            f"{ret_5d.return_pct * 100.0:+.2f}%" if ret_5d is not None else "N/A"
        )
        ret_20d_str = (
            f"{ret_20d.return_pct * 100.0:+.2f}%" if ret_20d is not None else "N/A"
        )
        lines.append(
            f"  {idx}. {match.ticker:<5} anchor={match.anchor_date} "
            f"dist={match.composite_distance:.3f} "
            f"+5d={ret_5d_str} +20d={ret_20d_str}"
        )

    lines.append("")
    lines.append(
        "Write a single-paragraph plain-prose summary of this signal in 2-4 "
        "sentences. Be factual and dry. Note what the signal is and why "
        "(per-horizon stats plus the dispersion of top-5 analog outcomes). "
        "Do not give advice. Do not hedge. Do not use markdown or bullets."
    )

    return "\n".join(lines)
