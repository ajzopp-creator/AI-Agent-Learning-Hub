"""p000_params_writer.py -- writes broker balance fields into P_000's
Account Parameters file (WO-P020-E1.009, extended by WO-P020-E1.011).
P_020 owns this write; the file itself is P_000's.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Optional

from config import P000_PARAMS_FILE
from domain.params_md_writer import ensure_cash_note, upsert_active_parameter_rows

logger = logging.getLogger(__name__)


def write_balance_to_p000_params(
    buying_power: Optional[float], cash_available: Optional[float]
) -> bool:
    """Surface Buying Power / Cash Available in P_000_Account_Parameters_Current.md.

    Either field may be None (Schwab omits cashAvailableForTrading for some
    margin accounts) -- writes "N/A" for whichever field is missing rather
    than skipping the whole update.

    Args:
        buying_power: Current buying power from pull_balance(), or None.
        cash_available: Current cash available for trading from pull_balance(), or None.

    Returns:
        True on success, False if the file is missing/locked (never raises).
    """
    try:
        markdown = P000_PARAMS_FILE.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not read P_000 params file: {e}")
        return False

    updates = {
        "Buying Power": (
            f"${buying_power:,.2f}" if buying_power is not None else "N/A"
        ),
        "Cash Available for Trading": (
            f"${cash_available:,.2f}" if cash_available is not None else "N/A"
        ),
    }
    try:
        markdown = upsert_active_parameter_rows(markdown, updates)
        markdown = ensure_cash_note(markdown)
        P000_PARAMS_FILE.write_text(markdown, encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not write P_000 params file: {e}")
        return False

    return True


def write_full_account_params(balance: float) -> bool:
    """Sync all 6 P_000 Account Parameters locations from one balance
    number (WO-P020-E1.011): Active Parameters (3 rows), Risk Mode
    Adjustments (5 rows), Three-Gate code block, Growth Projections
    current row, Next Review date, and one new Parameter History row.

    Gated by account_params_calc.should_write() -- the WO-P020-E1.011
    write threshold (default +/-10% vs. the last *written* baseline, not
    the last pull). No-op if not crossed: day-to-day balance noise never
    touches the file. Never raises -- logs and returns False on any
    read/parse/write failure so a bad pull can't corrupt the file
    mid-write.

    Args:
        balance: Latest total_value from pull_balance().

    Returns:
        True if a write happened, False if skipped (below threshold) or
        failed (see log).
    """
    from config import load_params
    from domain.account_params_calc import (
        calculate_derived_params,
        compute_next_review,
        should_write,
    )
    from domain.params_history_writer import (
        append_history_row,
        update_next_review,
        upsert_growth_current_row,
    )
    from domain.params_md_writer import (
        parse_last_written_balance,
        upsert_gate_block,
        upsert_risk_mode_table,
    )

    try:
        markdown = P000_PARAMS_FILE.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not read P_000 params file: {e}")
        return False

    last_balance = parse_last_written_balance(markdown)
    if not should_write(balance, last_balance):
        logger.info(
            f"Balance ${balance:,.2f} within threshold of last written "
            f"${last_balance if last_balance is not None else 'N/A'} -- "
            "no full param sync."
        )
        return False

    try:
        params = load_params()
        max_pct = params.get("max_position_pct", 0.05)
        derived = calculate_derived_params(
            balance, params["default_risk_pct"], max_pct
        )

        markdown = upsert_active_parameter_rows(markdown, derived["active_params"])
        markdown = upsert_risk_mode_table(markdown, derived["risk_mode_rows"])
        markdown = upsert_gate_block(
            markdown, derived["gate1_text"], derived["gate3_text"]
        )
        markdown = upsert_growth_current_row(markdown, derived["growth_current_row"])
        markdown = update_next_review(markdown, compute_next_review(date.today()))

        today = date.today()
        today_str = f"{today.strftime('%b')} {today.day}, {today.year}"
        history_row = (
            f"| {today_str} | ${balance:,.2f} | ${derived['risk_per_trade']:,.2f} | "
            f"${derived['max_position']:,.2f} | Auto-updated -- Net Liq per broker "
            "(threshold-triggered, WO-P020-E1.011) |"
        )
        markdown = append_history_row(markdown, history_row)

        P000_PARAMS_FILE.write_text(markdown, encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not write full P_000 params sync: {e}")
        return False

    return True
