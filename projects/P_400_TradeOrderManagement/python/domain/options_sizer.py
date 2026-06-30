"""options_sizer.py -- Options position sizing using P_115 Hybrid Methodology.

Pure logic only -- no I/O, no network calls, no print.
Two methods: Chart-Based (primary) and Risk-Budget-First (secondary).
Architecture v2.1 Section 7.3 (WO-P400-E3.001).
Canonical reference: P_115 OPTIONS_RISK_METHODOLOGY.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from config import (
    MIN_ACCEPTABLE_RR,
    OPTION_ATR_FLOOR_MULTIPLE,
    OPTION_IV_RANK_SPREAD_PREF,
    RISK_MODE_MULTIPLIERS,
)
from schemas import OptionChainInput

logger = logging.getLogger("p400.options_sizer")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class OptionSizingResult:
    """Output of size_option_chart_based() or size_option_risk_budget()."""

    method: str                        # "chart_based" | "risk_budget_first"
    contracts: int                     # final contract count (may be 0 -- override required)
    option_entry: float                # entry premium (mid)
    option_stop: float                 # stop premium (delta-translated or budget-derived)
    option_target: float               # target premium (delta-translated)
    risk_per_contract: float           # (entry - stop) * 100
    total_risk_dollars: float          # contracts * risk_per_contract
    adjusted_risk_budget: float        # posture-adjusted risk dollars
    rr_option: float                   # (target - entry) / (entry - stop)
    rr_valid: bool                     # True if rr_option >= MIN_ACCEPTABLE_RR
    override_required: bool            # True if contracts == 0 after gate math
    spread_recommended: bool           # True if iv_rank > OPTION_IV_RANK_SPREAD_PREF
    gate1_contracts: int = 0
    gate2_contracts: int = 0
    gate3_contracts: int = 0
    winning_gate: str = ""
    warning: Optional[str] = None
    notes: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _posture_multiplier(risk_mode: str) -> float:
    return RISK_MODE_MULTIPLIERS.get(risk_mode.upper().strip(), 1.00)


def _translate_stop(entry_premium: float, delta: float, stock_risk: float) -> float:
    """Delta-translate a stock stop to option premium stop.

    option_stop = entry_premium + (delta * stock_price_move_to_stop)
    stock_price_move_to_stop is negative (price falling to stop).

    Args:
        entry_premium: Option entry premium (mid price).
        delta: Option delta (positive for calls, negative for puts use abs).
        stock_risk: entry_price - stop_price (positive dollars at risk per share).

    Returns:
        Option stop premium (floored at 0.01).
    """
    option_stop = entry_premium - (abs(delta) * stock_risk)
    return max(round(option_stop, 2), 0.01)


def _translate_target(entry_premium: float, delta: float, stock_reward: float) -> float:
    """Delta-translate a stock target to option premium target.

    Args:
        entry_premium: Option entry premium (mid price).
        delta: Option delta (absolute value).
        stock_reward: target_price - entry_price (positive dollars reward per share).

    Returns:
        Option target premium.
    """
    return round(entry_premium + (abs(delta) * stock_reward), 2)


def _three_gate_contracts(
    adj_risk: float,
    cash_available: float,
    max_position_dollars: float,
    premium_per_contract: float,
    risk_per_contract: float,
) -> tuple[int, int, int, int, str]:
    """Run three gates, return (final, g1, g2, g3, winning_gate)."""
    if risk_per_contract <= 0 or premium_per_contract <= 0:
        return 0, 0, 0, 0, "INVALID"

    g1 = int(adj_risk / risk_per_contract)
    g2 = int(cash_available / premium_per_contract)
    g3 = int(max_position_dollars / premium_per_contract)

    final = min(g1, g2, g3)
    if g1 <= g2 and g1 <= g3:
        winning = "RISK"
    elif g2 <= g3:
        winning = "CASH"
    else:
        winning = "CONCENTRATION"

    return max(0, final), g1, g2, g3, winning


# ---------------------------------------------------------------------------
# Chart-Based (PRIMARY method)
# ---------------------------------------------------------------------------

def size_option_chart_based(
    chain: OptionChainInput,
    stock_entry: float,
    stock_stop: float,
    stock_target: float,
    base_risk_dollars: float,
    cash_available: float,
    max_position_dollars: float,
    risk_mode: str,
) -> OptionSizingResult:
    """Chart-Based options sizing (PRIMARY per P_115 OPTIONS_RISK_METHODOLOGY.md).

    Uses stock chart stop translated to option premium via delta.
    Gate 3 uses premium paid (not notional).

    Args:
        chain: Validated OptionChainInput from chain_loader.
        stock_entry: Live stock entry price.
        stock_stop: Stock chart stop price (must be < stock_entry).
        stock_target: Stock T1 target price.
        base_risk_dollars: From P_000 Account Parameters.
        cash_available: Per-trade buying power.
        max_position_dollars: P_000 max position cap.
        risk_mode: P_010 risk_mode string.

    Returns:
        OptionSizingResult with full audit trail.
    """
    mult = _posture_multiplier(risk_mode)
    adj_risk = base_risk_dollars * mult

    stock_risk = stock_entry - stock_stop
    stock_reward = stock_target - stock_entry

    option_stop = _translate_stop(chain.mid, chain.delta, stock_risk)
    option_target = _translate_target(chain.mid, chain.delta, stock_reward)

    risk_per_contract = round((chain.mid - option_stop) * 100, 2)
    premium_per_contract = round(chain.mid * 100, 2)

    rr = round((option_target - chain.mid) / (chain.mid - option_stop), 3) if (chain.mid - option_stop) > 0 else 0.0

    final, g1, g2, g3, winning = _three_gate_contracts(
        adj_risk, cash_available, max_position_dollars,
        premium_per_contract, risk_per_contract,
    )

    spread_rec = (chain.iv * 100) > OPTION_IV_RANK_SPREAD_PREF if chain.iv else False
    notes = []
    if spread_rec:
        notes.append(f"IV rank {chain.iv*100:.1f} > {OPTION_IV_RANK_SPREAD_PREF} -- spread recommended")

    return OptionSizingResult(
        method="chart_based",
        contracts=final,
        option_entry=chain.mid,
        option_stop=option_stop,
        option_target=option_target,
        risk_per_contract=risk_per_contract,
        total_risk_dollars=round(final * risk_per_contract, 2),
        adjusted_risk_budget=round(adj_risk, 2),
        rr_option=rr,
        rr_valid=(rr >= MIN_ACCEPTABLE_RR),
        override_required=(final == 0),
        spread_recommended=spread_rec,
        gate1_contracts=g1, gate2_contracts=g2, gate3_contracts=g3,
        winning_gate=winning,
        warning="0 contracts -- override required to trade 1" if final == 0 else None,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Risk-Budget-First (SECONDARY method)
# ---------------------------------------------------------------------------

def size_option_risk_budget(
    chain: OptionChainInput,
    atr_14: float,
    base_risk_dollars: float,
    cash_available: float,
    max_position_dollars: float,
    risk_mode: str,
) -> OptionSizingResult:
    """Risk-Budget-First options sizing (SECONDARY per P_115 OPTIONS_RISK_METHODOLOGY.md).

    Use when no clear technical stop exists. Derives stop from risk budget
    and 2xATR floor; selects the tighter of the two.

    Args:
        chain: Validated OptionChainInput from chain_loader.
        atr_14: Stock ATR(14) from snapshot.
        base_risk_dollars: From P_000 Account Parameters.
        cash_available: Per-trade buying power.
        max_position_dollars: P_000 max position cap.
        risk_mode: P_010 risk_mode string.

    Returns:
        OptionSizingResult with full audit trail.
    """
    mult = _posture_multiplier(risk_mode)
    adj_risk = base_risk_dollars * mult

    # Risk-budget stop: entry - (budget / 100)
    budget_stop = round(chain.mid - (adj_risk / 100), 2)

    # 2xATR floor stop: entry - (delta * 2 * ATR)
    atr_stop = max(round(chain.mid - (abs(chain.delta) * OPTION_ATR_FLOOR_MULTIPLE * atr_14), 2), 0.01)

    # Use whichever stop is lower (wider protection); ATR floor caps the downside
    option_stop = min(budget_stop, atr_stop)
    stop_method = "budget" if budget_stop <= atr_stop else "2xATR_floor"

    risk_per_contract = round((chain.mid - option_stop) * 100, 2)
    premium_per_contract = round(chain.mid * 100, 2)

    # No stock target available in this method -- use 2x risk as proxy target
    proxy_reward = risk_per_contract / 100 * MIN_ACCEPTABLE_RR
    option_target = round(chain.mid + proxy_reward, 2)
    rr = MIN_ACCEPTABLE_RR  # by construction when proxy used

    final, g1, g2, g3, winning = _three_gate_contracts(
        adj_risk, cash_available, max_position_dollars,
        premium_per_contract, risk_per_contract,
    )

    spread_rec = (chain.iv * 100) > OPTION_IV_RANK_SPREAD_PREF if chain.iv else False
    notes = [f"Stop method: {stop_method} (budget_stop={budget_stop:.2f}, atr_stop={atr_stop:.2f})"]
    if spread_rec:
        notes.append(f"IV rank {chain.iv*100:.1f} > {OPTION_IV_RANK_SPREAD_PREF} -- spread recommended")

    return OptionSizingResult(
        method="risk_budget_first",
        contracts=final,
        option_entry=chain.mid,
        option_stop=option_stop,
        option_target=option_target,
        risk_per_contract=risk_per_contract,
        total_risk_dollars=round(final * risk_per_contract, 2),
        adjusted_risk_budget=round(adj_risk, 2),
        rr_option=rr,
        rr_valid=(rr >= MIN_ACCEPTABLE_RR),
        override_required=(final == 0),
        spread_recommended=spread_rec,
        gate1_contracts=g1, gate2_contracts=g2, gate3_contracts=g3,
        winning_gate=winning,
        warning="0 contracts -- override required to trade 1" if final == 0 else None,
        notes=notes,
    )