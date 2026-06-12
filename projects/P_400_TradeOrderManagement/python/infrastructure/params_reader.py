"""P_400 infrastructure: read P_000 account parameters.

Parses the 'Active Parameters' markdown table in P_000_Account_Parameters_Current.md.
Returns AccountParams. No business logic.

Architecture v2.0 Section 3.3, 6.1.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from config import PARAMS_PATH
from schemas import AccountParams

logger = logging.getLogger("p400.params_reader")

# Match table rows from the 'Active Parameters' section.
# Row format: | Parameter Name | $1,234.56 | or | Name | 1.5% = $490.04 |
_RE_BALANCE = re.compile(
    r"Account Balance\s*\|\s*\$([0-9,]+\.?[0-9]*)", re.IGNORECASE
)
_RE_RISK = re.compile(
    r"Risk per Trade\s*\|\s*[0-9.]+%\s*=\s*\$([0-9,]+\.?[0-9]*)", re.IGNORECASE
)
_RE_MAX_POS = re.compile(
    r"Max Position\s*\([0-9]+%\)\s*\|\s*\$([0-9,]+\.?[0-9]*)", re.IGNORECASE
)


def _to_float(m: re.Match) -> float:
    return float(m.group(1).replace(",", ""))


def read_params(path: Path = PARAMS_PATH) -> AccountParams:
    """Parse account_balance, risk_per_trade, and max_position from the params file.

    Reads the 'Active Parameters' table only — not history rows.

    Args:
        path: Path to P_000_Account_Parameters_Current.md. Defaults to PARAMS_PATH.

    Returns:
        AccountParams with all three values as floats.

    Raises:
        FileNotFoundError: if the params file does not exist.
        ValueError: if any of the three required values cannot be parsed.
    """
    if not path.exists():
        raise FileNotFoundError(f"Account params file not found: {path}")

    text = path.read_text(encoding="utf-8")

    m_balance = _RE_BALANCE.search(text)
    m_risk = _RE_RISK.search(text)
    m_max = _RE_MAX_POS.search(text)

    missing = []
    if not m_balance:
        missing.append("Account Balance")
    if not m_risk:
        missing.append("Risk per Trade")
    if not m_max:
        missing.append("Max Position")
    if missing:
        raise ValueError(f"Could not parse from params file: {missing}")

    params = AccountParams(
        account_balance=_to_float(m_balance),
        risk_per_trade=_to_float(m_risk),
        max_position=_to_float(m_max),
    )
    logger.debug(
        "Params read: balance=$%.2f risk=$%.2f max=$%.2f",
        params.account_balance, params.risk_per_trade, params.max_position,
    )
    return params
