"""evaluate_spread.py -- Vertical debit spread evaluation orchestration.

Application layer: orchestration only -- no business logic, no direct I/O
beyond delegating to infrastructure readers/loaders.

No spread-specific viability council exists (WO-P400-E3.002 deliverable
list never included one) -- build_spread_spec.py already handles the
0-contract/no-override and debit-mismatch cases inline as text notices,
so this orchestrator just sizes, renders, and returns.

No vault write in this step -- same constraint as evaluate_options.py
(P400Record has no options/spread fields yet, WO-P400-E3.004 item 5).

Architecture v2.1 Section 7.3 (WO-P400-E3.002).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from application.build_spread_spec import build_spread_spec
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
    long_chain: OptionChainInput
    short_chain: OptionChainInput
    spec_text: str   # always populated -- build_spread_spec renders its own
                      # [NO SPEC] / [INVALID SPREAD] text inline


def evaluate_spread(
    packet: SignalV2,
    long_chain_path: str,
    short_chain_path: str,
    cash_available: float,
) -> SpreadEvalResult:
    """Run vertical debit spread sizing and render the Pattern C spec.

    Args:
        packet: Validated SignalV2 from the inbox (used for symbol only --
            spread sizing has no stock-trio dependency the way single-leg
            options sizing does; both legs are self-contained chain data).
        long_chain_path: Path to the long (ATM) leg chain_SYMBOL.json.
        short_chain_path: Path to the short (OTM) leg chain_SYMBOL.json.
        cash_available: Per-trade buying power.

    Returns:
        SpreadEvalResult. spec_text is always a string -- build_spread_spec
        renders its own notice text for 0-contract/invalid cases.
    """
    long_chain = load_chain(long_chain_path)
    short_chain = load_chain(short_chain_path)
    posture = read_posture()
    params = read_params()

    sizing = size_vertical_debit_spread(
        long_chain=long_chain,
        short_chain=short_chain,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash_available,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
    )

    spec_text = build_spread_spec(
        underlying_symbol=packet.symbol,
        long_chain=long_chain,
        short_chain=short_chain,
        sizing=sizing,
    )

    logger.info(
        "Spread evaluated %s: contracts=%d rr=%.2f warning=%s",
        packet.symbol, sizing.contracts, sizing.rr_spread, sizing.warning,
    )

    return SpreadEvalResult(
        symbol=packet.symbol,
        sizing=sizing,
        long_chain=long_chain,
        short_chain=short_chain,
        spec_text=spec_text,
    )