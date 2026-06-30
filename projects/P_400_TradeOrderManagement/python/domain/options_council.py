"""options_council.py -- Options viability gates and verdict assembly.

Pure logic only -- no I/O, no network calls, no print.
Runs AFTER options_sizer produces an OptionSizingResult.
Architecture v2.1 Section 7.3 (WO-P400-E3.001).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from config import (
    MIN_ACCEPTABLE_RR,
    OPTION_IV_RANK_SPREAD_PREF,
    OPTION_OI_MINIMUM,
    OPTION_SPREAD_MAX_PCT,
    OPTION_RR_PARITY_MIN,
)
from domain.options_sizer import OptionSizingResult
from schemas import OptionChainInput

logger = logging.getLogger("p400.options_council")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class OptionsCouncilResult:
    """Viability verdict for an options trade."""

    verdict: str                        # "PASS" | "BLOCK" | "CAUTION"
    blocks: list = field(default_factory=list)
    cautions: list = field(default_factory=list)
    annotations: list = field(default_factory=list)
    spread_recommended: bool = False


# ---------------------------------------------------------------------------
# Individual gate checks
# ---------------------------------------------------------------------------

def _check_open_interest(chain: OptionChainInput, result: OptionsCouncilResult) -> None:
    """OI < 150 -> BLOCK (liquidity gate)."""
    if chain.open_interest < OPTION_OI_MINIMUM:
        result.blocks.append(
            f"OI_TOO_LOW: open_interest={chain.open_interest} < {OPTION_OI_MINIMUM} minimum"
        )


def _check_spread(chain: OptionChainInput, result: OptionsCouncilResult) -> None:
    """Spread > 10% of mid -> BLOCK (fill quality gate)."""
    if chain.spread_pct_of_mid > OPTION_SPREAD_MAX_PCT:
        result.blocks.append(
            f"SPREAD_TOO_WIDE: spread={chain.spread_pct_of_mid:.1f}% > {OPTION_SPREAD_MAX_PCT}% max"
        )


def _check_rr_parity(
    sizing: OptionSizingResult,
    stock_rr: float,
    result: OptionsCouncilResult,
) -> None:
    """Option R:R must be >= stock R:R * OPTION_RR_PARITY_MIN -> else BLOCK."""
    threshold = stock_rr * OPTION_RR_PARITY_MIN
    if sizing.rr_option < threshold:
        result.blocks.append(
            f"RR_PARITY_FAIL: option_rr={sizing.rr_option:.2f} < stock_rr={stock_rr:.2f} "
            f"(threshold={threshold:.2f})"
        )


def _check_rr_minimum(sizing: OptionSizingResult, result: OptionsCouncilResult) -> None:
    """Option R:R < 2.0 minimum -> BLOCK."""
    if not sizing.rr_valid:
        result.blocks.append(
            f"RR_BELOW_MIN: option_rr={sizing.rr_option:.2f} < {MIN_ACCEPTABLE_RR} minimum"
        )


def _check_iv_rank(chain: OptionChainInput, result: OptionsCouncilResult) -> None:
    """IV rank > 50 -> CAUTION + spread recommendation (not a block)."""
    iv_pct = (chain.iv or 0.0) * 100
    if iv_pct > OPTION_IV_RANK_SPREAD_PREF:
        result.cautions.append(
            f"IV_HIGH: iv_rank={iv_pct:.1f}% > {OPTION_IV_RANK_SPREAD_PREF} -- "
            "premium expensive, spread structure preferred"
        )
        result.spread_recommended = True


def _check_override_flag(sizing: OptionSizingResult, result: OptionsCouncilResult) -> None:
    """0 contracts after gate math -> CAUTION (override or reject)."""
    if sizing.override_required:
        result.cautions.append(
            "ZERO_CONTRACTS: gate math produced 0 contracts -- "
            "explicit override required to trade 1 contract (document justification)"
        )


# ---------------------------------------------------------------------------
# Main council function
# ---------------------------------------------------------------------------

def run_options_council(
    chain: OptionChainInput,
    sizing: OptionSizingResult,
    stock_rr: float,
) -> OptionsCouncilResult:
    """Run all viability gates and assemble options council verdict.

    Args:
        chain: Validated OptionChainInput.
        sizing: Output of size_option_chart_based() or size_option_risk_budget().
        stock_rr: Realistic-fill R:R of the underlying stock setup (for parity check).

    Returns:
        OptionsCouncilResult with verdict, blocks, cautions, annotations.
    """
    result = OptionsCouncilResult(verdict="PASS")

    _check_open_interest(chain, result)
    _check_spread(chain, result)
    _check_rr_minimum(sizing, result)
    _check_rr_parity(sizing, stock_rr, result)
    _check_iv_rank(chain, result)
    _check_override_flag(sizing, result)

    if result.blocks:
        result.verdict = "BLOCK"
        for b in result.blocks:
            logger.warning("Options council BLOCK: %s", b)
    elif result.cautions:
        result.verdict = "CAUTION"
        for c in result.cautions:
            logger.info("Options council CAUTION: %s", c)
    else:
        result.verdict = "PASS"
        logger.info("Options council PASS: %s %s strike=%.2f",
                    chain.symbol, chain.option_type, chain.strike)

    return result