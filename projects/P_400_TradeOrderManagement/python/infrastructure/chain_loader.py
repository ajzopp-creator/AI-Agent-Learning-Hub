"""chain_loader.py -- Load and validate option chain data from chain_SYMBOL.json.

Infrastructure layer: I/O only. No business logic.
Reads the chain file, validates via OptionChainInput, returns typed object.

Source priority (Architecture v2.1 Section 3.9):
  TOS -> ChartExchange -> Yahoo Finance -> Barchart/Nasdaq -> manual
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from schemas import OptionChainInput

logger = logging.getLogger("p400.chain_loader")


def load_chain(chain_path: str) -> OptionChainInput:
    """Load and validate a chain_SYMBOL.json file.

    Args:
        chain_path: Full path to the chain JSON file.

    Returns:
        Validated OptionChainInput instance.

    Raises:
        FileNotFoundError: If the chain file does not exist.
        ValueError: If the file fails schema validation.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    path = Path(chain_path)
    if not path.exists():
        raise FileNotFoundError(f"Chain file not found: {chain_path}")

    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)

    try:
        chain = OptionChainInput(**data)
    except ValidationError as exc:
        raise ValueError(f"Chain file failed validation: {exc}") from exc

    _warn_liquidity(chain)
    logger.info(
        "Chain loaded: %s %s %.2f %s exp=%s OI=%d spread=%.1f%%",
        chain.symbol,
        chain.option_type,
        chain.strike,
        chain.expiration,
        chain.expiration,
        chain.open_interest,
        chain.spread_pct_of_mid,
    )
    return chain


def _warn_liquidity(chain: OptionChainInput) -> None:
    """Log warnings for liquidity concerns. Does not raise -- domain gates block.

    Liquidity thresholds (Architecture v2.1 Section 3.8):
      OI >= 150, spread <= 10% of mid.
    """
    if chain.open_interest < 150:
        logger.warning(
            "Chain %s OI=%d is below 150 minimum -- options_council will block.",
            chain.symbol, chain.open_interest,
        )
    if chain.spread_pct_of_mid > 10.0:
        logger.warning(
            "Chain %s spread=%.1f%% exceeds 10%% threshold -- options_council will block.",
            chain.symbol, chain.spread_pct_of_mid,
        )
