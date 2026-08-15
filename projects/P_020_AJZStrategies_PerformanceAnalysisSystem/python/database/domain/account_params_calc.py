"""account_params_calc.py -- pure calculations for P_000 Account Parameters
sync (WO-P020-E1.011). No file I/O, no markdown text -- infrastructure and
domain/params_md_writer.py + domain/params_history_writer.py own those.
Percentages sourced from P_020_Account_Params.json (config.load_params()),
never hardcoded fresh except the write-threshold, which IS this WO's own
named constant.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

# WO-P020-E1.011 decision 1: Tony did not specify X explicitly this
# session -- defaults to the same +/-10% concept already live in
# P_020_INIT.py's account threshold flag. Change this one constant to
# adjust the trigger sensitivity -- no code review needed (acceptance
# criterion).
WRITE_THRESHOLD_PCT = 0.10

MILESTONE_TEXT = "or when balance hits $35,000"


def should_write(new_balance: float, last_written_balance: Optional[float]) -> bool:
    """True if new_balance has moved >= WRITE_THRESHOLD_PCT from the last
    *written* baseline (not the last pull -- WO-P020-E1.011 decision 1).

    Args:
        new_balance: Latest balance from pull_balance().
        last_written_balance: Balance currently on disk in the Active
            Parameters table, or None if it could not be parsed (first
            run, or file format changed) -- treated as "always write" so
            a parse failure never silently blocks the sync forever.

    Returns:
        True if this pull should trigger a full param sync.
    """
    if last_written_balance is None or last_written_balance == 0:
        return True
    pct_change = abs(new_balance - last_written_balance) / last_written_balance
    return pct_change >= WRITE_THRESHOLD_PCT


def calculate_derived_params(balance: float, risk_pct: float, max_pct: float) -> dict:
    """Derive every dollar figure the 6 synced locations need from one
    balance number.

    Args:
        balance: New account balance (Net Liq per broker).
        risk_pct: Base risk-per-trade fraction (e.g. 0.015 = 1.5%).
        max_pct: Base max-position fraction (e.g. 0.05 = 5%).

    Returns:
        dict with every derived figure -- raw floats (for the History row)
        plus pre-formatted strings (for tables/blocks that mix dollars
        with fixed prose).
    """
    risk = balance * risk_pct
    max_pos = balance * max_pct

    return {
        "balance": balance,
        "risk_per_trade": risk,
        "max_position": max_pos,
        "active_params": {
            "Account Balance": f"${balance:,.2f}",
            "Risk per Trade": f"{risk_pct * 100:.1f}% = ${risk:,.2f}",
            "Max Position (5%)": f"${max_pos:,.2f}",
        },
        "risk_mode_rows": {
            "OFF / CORRECTION": (
                f"${risk * 0.5:,.2f} (50%)", f"${max_pos * 0.5:,.2f} (50%)"
            ),
            "HALF": (f"${risk * 0.75:,.2f} (75%)", f"${max_pos * 0.75:,.2f} (75%)"),
            "STANDARD": (f"${risk:,.2f}", f"${max_pos:,.2f}"),
            "FULL": (f"${risk:,.2f}", f"${max_pos:,.2f}"),
            # HOT is not a clean percentage of base -- Risk cell is fixed
            # prose in the source file, Max cell reuses the full base
            # figure with an "Up to" prefix. Never derive HOT's Risk cell
            # from a multiplier.
            "HOT": ("Tiered up to 5%", f"Up to ${max_pos:,.2f}"),
        },
        "gate1_text": f"Gate 1 (Risk-Based):    ${risk:,.2f} / (Entry - Stop)",
        "gate3_text": (
            f"Gate 3 (Concentration): ${max_pos:,.2f} max (or premium for options)"
        ),
        "growth_current_row": (
            f"| ${balance:,.2f} (current) | ${risk:,.2f} | ${max_pos:,.2f} |"
        ),
    }


def compute_next_review(today: date) -> str:
    """Roll 'Next Review' forward one month from today.

    WO-P020-E1.011 decision 3: auto-bump the date, leave the fixed
    milestone clause ("$35,000") as static text -- that number is a
    separate Update Triggers concept, not derived from this balance pull.

    Args:
        today: Current date (injected for testability).

    Returns:
        Formatted string, e.g. "September 2026 (monthly) or when balance
        hits $35,000".
    """
    month = today.month + 1
    year = today.year
    if month > 12:
        month = 1
        year += 1
    month_name = date(year, month, 1).strftime("%B")
    return f"{month_name} {year} (monthly) {MILESTONE_TEXT}"
