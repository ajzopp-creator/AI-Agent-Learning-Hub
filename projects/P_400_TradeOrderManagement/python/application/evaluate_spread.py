"""evaluate_spread.py -- Vertical debit spread evaluation orchestration.

Application layer: orchestration only -- no business logic, no direct I/O
beyond delegating to infrastructure readers/loaders.

WO-P400-E3.005 added the liquidity viability council (domain.spread_council)
-- either leg failing OI/spread-pct thresholds BLOCKs before a spec is
rendered. Sizing is still computed on a BLOCK so the record write has a
full audit trail (position_size=0 either way).

No vault write in this step -- same constraint as evaluate_options.py
(P400Record has no options/spread fields yet, WO-P400-E3.004 item 5).

Architecture v2.1 Section 7.3 (WO-P400-E3.002, WO-P400-E3.005).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from application.build_spread_spec import build_spread_spec
from domain.spread_council import SpreadCouncilResult, run_spread_council
from domain.spread_sizer import SpreadSizingResult, size_vertical_debit_spread
from infrastructure.chain_loader import load_chain
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from schemas import OptionChainInput, SignalV2

logger = logging.getLogger("p400.evaluate_spread")


@dataclass
class SpreadEvalResult:
    """Output of evaluate_spread()."""

    symbol: str
    sizing: SpreadSizingResult
    council: SpreadCouncilResult
    long_chain: OptionChainInput
    short_chain: OptionChainInput
    spec_text: str   # [NO SPEC] notice when council.verdict == "BLOCK"


def evaluate_spread(
    packet: SignalV2,
    long_chain_path: str,
    short_chain_path: str,
    cash_available: float,
) -> SpreadEvalResult:
    """Run spread liquidity gates, sizing, and Pattern C spec rendering.

    Args:
        packet: Validated SignalV2 from the inbox (used for symbol only).
        long_chain_path: Path to the long (ATM) leg chain_SYMBOL.json.
        short_chain_path: Path to the short (OTM) leg chain_SYMBOL.json.
        cash_available: Per-trade buying power.

    Returns:
        SpreadEvalResult. spec_text is a [NO SPEC] notice when the
        liquidity council BLOCKs; otherwise the full Pattern C spec.
    """
    long_chain = load_chain(long_chain_path)
    short_chain = load_chain(short_chain_path)
    posture = read_posture()
    params = read_params()

    council = run_spread_council(long_chain, short_chain)

    sizing = size_vertical_debit_spread(
        long_chain=long_chain,
        short_chain=short_chain,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash_available,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
    )

    if council.verdict == "BLOCK":
        spec_text = (
            f"[NO SPEC -- {packet.symbol}] Spread council BLOCKED. "
            "No order spec generated."
        )
    else:
        spec_text = build_spread_spec(
            underlying_symbol=packet.symbol,
            long_chain=long_chain,
            short_chain=short_chain,
            sizing=sizing,
        )

    logger.info(
        "Spread evaluated %s: council=%s contracts=%d rr=%.2f warning=%s",
        packet.symbol, council.verdict, sizing.contracts, sizing.rr_spread, sizing.warning,
    )

    return SpreadEvalResult(
        symbol=packet.symbol,
        sizing=sizing,
        council=council,
        long_chain=long_chain,
        short_chain=short_chain,
        spec_text=spec_text,
    )