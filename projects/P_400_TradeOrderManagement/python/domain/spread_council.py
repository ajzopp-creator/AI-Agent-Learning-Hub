"""spread_council.py -- Vertical debit spread liquidity viability gates.

Pure logic only -- no I/O, no network calls, no print.
Runs OI and spread-pct checks on BOTH legs of a vertical debit spread.
A spread is only as liquid as its worse leg -- either leg failing is a
hard BLOCK, no CAUTION tier (severity resolved 2026-07-04).

Architecture v2.1 Section 3.8, WO-P400-E3.005.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from config import OPTION_OI_MINIMUM, OPTION_SPREAD_MAX_PCT
from schemas import OptionChainInput

logger = logging.getLogger("p400.spread_council")


@dataclass
class SpreadCouncilResult:
    """Liquidity viability verdict for a vertical debit spread."""

    verdict: str                        # "PASS" | "BLOCK"
    blocks: list = field(default_factory=list)


def _check_leg(chain: OptionChainInput, leg_label: str, result: SpreadCouncilResult) -> None:
    """OI < 150 or spread > 10% of mid -> BLOCK for this leg."""
    if chain.open_interest < OPTION_OI_MINIMUM:
        result.blocks.append(
            f"{leg_label}_OI_TOO_LOW: open_interest={chain.open_interest} "
            f"< {OPTION_OI_MINIMUM} minimum"
        )
    if chain.spread_pct_of_mid > OPTION_SPREAD_MAX_PCT:
        result.blocks.append(
            f"{leg_label}_SPREAD_TOO_WIDE: spread={chain.spread_pct_of_mid:.1f}% "
            f"> {OPTION_SPREAD_MAX_PCT}% max"
        )


def run_spread_council(
    long_chain: OptionChainInput,
    short_chain: OptionChainInput,
) -> SpreadCouncilResult:
    """Run liquidity viability gates on both legs of a vertical debit spread.

    A spread is only as liquid as its worse leg -- either leg failing
    OI or spread-pct thresholds produces a BLOCK. No CAUTION tier
    (severity resolved 2026-07-04, WO-P400-E3.005).

    Args:
        long_chain: Validated OptionChainInput for the long (ATM) leg.
        short_chain: Validated OptionChainInput for the short (OTM) leg.

    Returns:
        SpreadCouncilResult with verdict and block reason codes.
    """
    result = SpreadCouncilResult(verdict="PASS")

    _check_leg(long_chain, "LONG_LEG", result)
    _check_leg(short_chain, "SHORT_LEG", result)

    if result.blocks:
        result.verdict = "BLOCK"
        for b in result.blocks:
            logger.warning("Spread council BLOCK: %s", b)
    else:
        result.verdict = "PASS"
        logger.info(
            "Spread council PASS: long=%.2f short=%.2f",
            long_chain.strike, short_chain.strike,
        )

    return result