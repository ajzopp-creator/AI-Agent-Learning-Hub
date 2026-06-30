"""evaluate_options.py -- Single-leg options evaluation orchestration.

Application layer: orchestration only -- no business logic, no direct I/O
beyond delegating to infrastructure readers/loaders.

Reuses the exact sizing+council sequence proven in compare_vehicles.py,
then renders a Pattern B spec (build_option_spec) gated on the options
council verdict. Chart-Based method only -- packet always carries a
guideline_stop, so the chart-based technical-stop path applies (P_115
Hybrid Methodology; Risk-Budget-First is for setups with no defensible
technical stop, not wired here).

No vault write on BLOCK in this step -- P400Record has no options fields
yet (WO-P400-E3.004 item 5). Verdict and spec print only.

Architecture v2.1 Section 7.3 (WO-P400-E3.001).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from application.build_option_spec import build_option_spec
from domain.options_council import OptionsCouncilResult, run_options_council
from domain.options_sizer import OptionSizingResult, size_option_chart_based
from infrastructure.chain_loader import load_chain
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from schemas import OptionChainInput, SignalV2, SnapshotDict

logger = logging.getLogger("p400.evaluate_options")


@dataclass
class OptionsEvalResult:
    """Output of evaluate_options()."""

    symbol: str
    verdict: str                          # PASS | CAUTION | BLOCK
    sizing: OptionSizingResult
    council: OptionsCouncilResult
    chain: OptionChainInput
    spec_text: Optional[str] = None       # None when verdict == BLOCK


def evaluate_options(
    packet: SignalV2,
    snapshot_raw: dict,
    chain_path: str,
    cash_available: float,
    stock_rr: float,
) -> OptionsEvalResult:
    """Run single-leg options sizing + viability gates, render spec if not BLOCKED.

    Args:
        packet: Validated SignalV2 from the inbox (provides guideline stop/target).
        snapshot_raw: Raw snapshot dict already used for the stock evaluation.
        chain_path: Path to chain_SYMBOL.json.
        cash_available: Per-trade buying power.
        stock_rr: Realistic-fill stock R:R (EvaluationResult.rr_after_drift) --
            required for the options-council R:R parity gate.

    Returns:
        OptionsEvalResult. spec_text is None when council verdict is BLOCK.
    """
    snap = SnapshotDict(**snapshot_raw)
    chain = load_chain(chain_path)
    posture = read_posture()
    params = read_params()

    sizing = size_option_chart_based(
        chain=chain,
        stock_entry=snap.price,
        stock_stop=packet.guideline_stop,
        stock_target=packet.guideline_target,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash_available,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
    )

    council = run_options_council(chain=chain, sizing=sizing, stock_rr=stock_rr)

    spec_text = None
    if council.verdict != "BLOCK":
        spec_text = build_option_spec(
            underlying_symbol=packet.symbol,
            chain=chain,
            sizing=sizing,
            stock_entry=snap.price,
            stock_stop=packet.guideline_stop,
            stock_target=packet.guideline_target,
        )

    logger.info(
        "Options evaluated %s: council=%s contracts=%d rr=%.2f",
        packet.symbol, council.verdict, sizing.contracts, sizing.rr_option,
    )

    return OptionsEvalResult(
        symbol=packet.symbol,
        verdict=council.verdict,
        sizing=sizing,
        council=council,
        chain=chain,
        spec_text=spec_text,
    )