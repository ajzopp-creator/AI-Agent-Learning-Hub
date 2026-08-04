"""p000_params_writer.py -- writes broker balance fields into P_000's
Account Parameters file (WO-P020-E1.009). P_020 owns this write; the file
itself is P_000's, hand-maintained by Tony for Account Balance/Risk/Max.
"""

from __future__ import annotations

import logging
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
