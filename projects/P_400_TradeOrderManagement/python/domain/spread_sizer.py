"""spread_sizer.py -- Vertical debit spread sizing for P_400 Phase E3.

Pure logic only -- no I/O, no network calls, no print.
Triggered when: IV rank > 50, single-leg premium exceeds Gate 3,
or Tony explicitly requests spread via --spread flag.

Architecture v2.1 Section 7.3 (WO-P400-E3.002).
Canonical reference: P_115 OPTIONS_RISK_METHODOLOGY.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from config import (
    MIN_ACCEPTABLE_RR,
    OPTION_IV_RANK_SPREAD_PREF,
    RISK_MODE_MULTIPLIERS,
)
from schemas import OptionChainInput

logger = logging.getLogger("p400.spread_sizer")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class SpreadSizingResult:
    """Output of size_vertical_debit_spread()."""

    long_strike: float              # long leg strike (ATM)
    short_strike: float             # short leg strike (OTM at T1 or resistance)
    spread_width: float             # short_strike - long_strike (calls) or reverse (puts)
    debit_per_spread: float         # net premium paid (long mid - short mid)
    max_profit_per_spread: float    # (spread_width - debit) * 100
    max_loss_per_spread: float      # debit * 100
    breakeven: float                # long_strike + debit (calls) or long_strike - debit (puts)
    contracts: int                  # final contract count
    total_max_loss: float           # contracts * max_loss_per_spread
    adjusted_risk_budget: float     # posture-adjusted risk dollars
    rr_spread: float                # max_profit / max_loss per spread
    rr_valid: bool                  # True if rr_spread >= MIN_ACCEPTABLE_RR
    override_required: bool         # True if contracts == 0
    gate1_contracts: int = 0
    gate2_contracts: int = 0
    gate3_contracts: int = 0
    winning_gate: str = ""
    warning: Optional[str] = None
    notes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _posture_multiplier(risk_mode: str) -> float:
    return RISK_MODE_MULTIPLIERS.get(risk_mode.upper().strip(), 1.00)


def _spread_width(long_strike: float, short_strike: float, option_type: str) -> float:
    """Width is always positive regardless of option type."""
    if option_type.lower() == "call":
        return round(short_strike - long_strike, 2)
    return round(long_strike - short_strike, 2)


def _breakeven(long_strike: float, debit: float, option_type: str) -> float:
    """Breakeven at expiration."""
    if option_type.lower() == "call":
        return round(long_strike + debit, 2)
    return round(long_strike - debit, 2)


def _three_gate_contracts(
    adj_risk: float,
    cash_available: float,
    max_position_dollars: float,
    max_loss_per_spread: float,
    debit_cost: float,
) -> tuple[int, int, int, int, str]:
    """Run three gates for spread contracts.

    Gate 1: posture-adjusted risk / max_loss_per_spread
    Gate 2: cash_available / debit_cost
    Gate 3: max_position_dollars / max_loss_per_spread  (max loss, not notional)
    """
    if max_loss_per_spread <= 0 or debit_cost <= 0:
        return 0, 0, 0, 0, "INVALID"

    g1 = int(adj_risk / max_loss_per_spread)
    g2 = int(cash_available / debit_cost)
    g3 = int(max_position_dollars / max_loss_per_spread)

    final = min(g1, g2, g3)
    if g1 <= g2 and g1 <= g3:
        winning = "RISK"
    elif g2 <= g3:
        winning = "CASH"
    else:
        winning = "CONCENTRATION"

    return max(0, final), g1, g2, g3, winning


# ---------------------------------------------------------------------------
# Main sizing function
# ---------------------------------------------------------------------------

def size_vertical_debit_spread(
    long_chain: OptionChainInput,
    short_chain: OptionChainInput,
    base_risk_dollars: float,
    cash_available: float,
    max_position_dollars: float,
    risk_mode: str,
) -> SpreadSizingResult:
    """Size a vertical debit spread (call debit or put debit).

    Long leg: ATM strike (supplied as long_chain).
    Short leg: OTM strike at T1 or next resistance (supplied as short_chain).
    Max loss is capped at debit paid -- defined risk structure.
    Gate 3 uses max_loss (not notional) per Architecture v2.1 Section 3.8.

    Args:
        long_chain: OptionChainInput for the long (ATM) leg.
        short_chain: OptionChainInput for the short (OTM) leg.
        base_risk_dollars: From P_000 Account Parameters.
        cash_available: Per-trade buying power.
        max_position_dollars: P_000 max position cap.
        risk_mode: P_010 risk_mode string.

    Returns:
        SpreadSizingResult with full audit trail.
    """
    if long_chain.option_type != short_chain.option_type:
        return SpreadSizingResult(
            long_strike=long_chain.strike, short_strike=short_chain.strike,
            spread_width=0.0, debit_per_spread=0.0,
            max_profit_per_spread=0.0, max_loss_per_spread=0.0,
            breakeven=0.0, contracts=0, total_max_loss=0.0,
            adjusted_risk_budget=0.0, rr_spread=0.0, rr_valid=False,
            override_required=True, warning="option_type mismatch between legs",
        )

    mult = _posture_multiplier(risk_mode)
    adj_risk = base_risk_dollars * mult

    debit = round(long_chain.mid - short_chain.mid, 2)
    if debit <= 0:
        return SpreadSizingResult(
            long_strike=long_chain.strike, short_strike=short_chain.strike,
            spread_width=0.0, debit_per_spread=debit,
            max_profit_per_spread=0.0, max_loss_per_spread=0.0,
            breakeven=0.0, contracts=0, total_max_loss=0.0,
            adjusted_risk_budget=round(adj_risk, 2),
            rr_spread=0.0, rr_valid=False,
            override_required=True,
            warning=f"debit <= 0 ({debit:.2f}): short leg premium >= long leg -- invalid spread",
        )

    width = _spread_width(long_chain.strike, short_chain.strike, long_chain.option_type)
    max_profit = round((width - debit) * 100, 2)
    max_loss = round(debit * 100, 2)
    be = _breakeven(long_chain.strike, debit, long_chain.option_type)

    rr = round(max_profit / max_loss, 3) if max_loss > 0 else 0.0
    debit_cost = round(debit * 100, 2)

    final, g1, g2, g3, winning = _three_gate_contracts(
        adj_risk, cash_available, max_position_dollars, max_loss, debit_cost,
    )

    notes = []
    iv_pct = (long_chain.iv or 0.0) * 100
    if iv_pct > OPTION_IV_RANK_SPREAD_PREF:
        notes.append(f"IV rank {iv_pct:.1f}% -- spread is the preferred structure at this IV level")

    return SpreadSizingResult(
        long_strike=long_chain.strike,
        short_strike=short_chain.strike,
        spread_width=width,
        debit_per_spread=debit,
        max_profit_per_spread=max_profit,
        max_loss_per_spread=max_loss,
        breakeven=be,
        contracts=final,
        total_max_loss=round(final * max_loss, 2),
        adjusted_risk_budget=round(adj_risk, 2),
        rr_spread=rr,
        rr_valid=(rr >= MIN_ACCEPTABLE_RR),
        override_required=(final == 0),
        gate1_contracts=g1, gate2_contracts=g2, gate3_contracts=g3,
        winning_gate=winning,
        warning="0 contracts -- override required to trade 1 spread" if final == 0 else None,
        notes=notes,
    )