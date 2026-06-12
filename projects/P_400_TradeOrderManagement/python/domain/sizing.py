"""P_400 domain: three-gate position sizing.

Pure logic only - no I/O, no network calls, no print statements.
Receives typed parameters; returns typed results.

Architecture v2.0 Section 3.3, 3.8, 6.2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from config import (
    MIN_ACCEPTABLE_RR,
    MIN_STOP_ATR_MULTIPLE,
    OPTION_IV_RANK_SPREAD_PREF,
    RISK_MODE_MULTIPLIERS,
)

logger = logging.getLogger("p400.sizing")


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SizingResult:
    """Output of three_gate_size()."""
    shares: int                    # final position size (smallest gate)
    gate1_shares: int              # risk gate raw
    gate2_shares: int              # cash gate raw
    gate3_shares: int              # concentration gate raw
    winning_gate: str              # "RISK" | "CASH" | "CONCENTRATION"
    dollar_risk: float             # shares * (entry - stop), posture-adjusted
    posture_multiplier: float      # 0.50 | 0.75 | 1.00
    adjusted_risk_dollars: float   # base_risk_dollars * posture_multiplier
    rr_at_t1: float                # (target - entry) / (entry - stop)
    rr_valid: bool                 # True if rr_at_t1 >= MIN_ACCEPTABLE_RR
    warning: Optional[str] = None


@dataclass
class OptionsSizingResult:
    """Output of options_size()."""
    contracts: int
    max_risk_dollars: float        # premium paid (capped at premium-at-risk)
    premium_per_contract: float
    delta_adjusted_risk: float
    theta_iv_haircut: float        # fraction applied (e.g. 0.20)
    haircut_applied_dollars: float
    warning: Optional[str] = None


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def posture_multiplier(risk_mode: str) -> float:
    """Return the risk-scaling multiplier for a given P_010 risk_mode.

    Args:
        risk_mode: String from P_010_RiskConfig.json 'risk_mode' field.

    Returns:
        Float multiplier (0.50, 0.75, or 1.00).
    """
    key = risk_mode.upper().strip()
    return RISK_MODE_MULTIPLIERS.get(key, 1.00)


def realistic_fill_rr(
    entry: float,
    stop: float,
    target: float,
    half_spread: float = 0.0,
) -> float:
    """Compute R:R on realistic fills (buy at ask, exit at bid).

    Realistic entry = entry + half_spread (paying the spread on buy).
    Realistic exit  = target - half_spread (receiving bid on sell).
    Stop is a stop-limit; conservative assumption: executed at stop price.

    Args:
        entry: Signal entry price.
        stop: Signal stop price.
        target: Signal T1 target price.
        half_spread: Half of bid-ask spread at entry (defaults to 0 if unknown).

    Returns:
        R:R ratio as float. Returns 0.0 if stop >= entry (invalid setup).
    """
    if stop >= entry:
        return 0.0
    real_entry = entry + half_spread
    real_target = target - half_spread
    risk_per_share = real_entry - stop
    reward_per_share = real_target - real_entry
    if risk_per_share <= 0:
        return 0.0
    return round(reward_per_share / risk_per_share, 3)


# ---------------------------------------------------------------------------
# Main sizing function
# ---------------------------------------------------------------------------

def three_gate_size(
    entry: float,
    stop: float,
    target: float,
    base_risk_dollars: float,
    cash_available: float,
    max_position_dollars: float,
    risk_mode: str,
    half_spread: float = 0.0,
) -> SizingResult:
    """Three-gate position sizer per Architecture v2.0 Section 3.3.

    Gate 1 (Risk):          posture_adjusted_risk / (entry - stop)
    Gate 2 (Cash):          cash_available / entry
    Gate 3 (Concentration): max_position_dollars / entry
    Final = SMALLEST of the three gates (floored to 0 shares minimum).

    Args:
        entry: Planned entry price.
        stop: Stop-loss price (must be < entry for long).
        target: T1 target price.
        base_risk_dollars: Dollar risk from P_000 Account Parameters (e.g. 490.04).
        cash_available: Per-trade buying power provided by Tony.
        max_position_dollars: P_000 max position dollar cap (e.g. 1633.47).
        risk_mode: P_010 risk_mode string (e.g. "OFF", "STANDARD").
        half_spread: Half of bid-ask spread; used for realistic-fill R:R only.

    Returns:
        SizingResult with shares and full audit trail.
    """
    mult = posture_multiplier(risk_mode)
    adj_risk = base_risk_dollars * mult

    risk_per_share = entry - stop
    if risk_per_share <= 0:
        logger.warning("stop >= entry: invalid setup, returning 0 shares")
        return SizingResult(
            shares=0, gate1_shares=0, gate2_shares=0, gate3_shares=0,
            winning_gate="INVALID", dollar_risk=0.0,
            posture_multiplier=mult, adjusted_risk_dollars=adj_risk,
            rr_at_t1=0.0, rr_valid=False,
            warning="stop >= entry",
        )

    gate1 = int(adj_risk / risk_per_share)
    gate2 = int(cash_available / entry)
    gate3 = int(max_position_dollars / entry)

    final = min(gate1, gate2, gate3)
    if gate1 <= gate2 and gate1 <= gate3:
        winning = "RISK"
    elif gate2 <= gate3:
        winning = "CASH"
    else:
        winning = "CONCENTRATION"

    rr = realistic_fill_rr(entry, stop, target, half_spread)

    return SizingResult(
        shares=max(0, final),
        gate1_shares=gate1,
        gate2_shares=gate2,
        gate3_shares=gate3,
        winning_gate=winning,
        dollar_risk=final * risk_per_share,
        posture_multiplier=mult,
        adjusted_risk_dollars=adj_risk,
        rr_at_t1=rr,
        rr_valid=(rr >= MIN_ACCEPTABLE_RR),
        warning=None if final > 0 else "sizing produced 0 shares",
    )


# ---------------------------------------------------------------------------
# Options sizing
# ---------------------------------------------------------------------------

def options_size(
    base_risk_dollars: float,
    risk_mode: str,
    premium_per_contract: float,
    option_delta: float,
    theta_iv_haircut: float = 0.20,
) -> OptionsSizingResult:
    """Options position sizing: risk capped at premium-at-risk with haircut.

    Dollar risk for an option position = premium paid, never (entry-stop) stock math.
    A theta/IV-crush haircut reduces the effective risk budget before sizing.

    Args:
        base_risk_dollars: From P_000 Account Parameters.
        risk_mode: P_010 risk_mode string.
        premium_per_contract: Option premium * 100 (full contract cost).
        option_delta: Absolute delta of the option (0.0 - 1.0).
        theta_iv_haircut: Fraction of budget reserved for theta/IV decay (default 0.20).

    Returns:
        OptionsSizingResult with contract count and risk breakdown.
    """
    mult = posture_multiplier(risk_mode)
    adj_risk = base_risk_dollars * mult
    haircut_dollars = adj_risk * theta_iv_haircut
    effective_budget = adj_risk - haircut_dollars

    contracts = 0
    warning = None
    if premium_per_contract > 0:
        contracts = int(effective_budget / premium_per_contract)
        if contracts == 0:
            warning = "budget insufficient for 1 contract after haircut"
    else:
        warning = "invalid premium_per_contract <= 0"

    delta_adj_risk = contracts * premium_per_contract * option_delta

    iv_flag = None
    if OPTION_IV_RANK_SPREAD_PREF > 0:
        iv_flag = f"IV rank >= {OPTION_IV_RANK_SPREAD_PREF} triggers spread preference"

    return OptionsSizingResult(
        contracts=max(0, contracts),
        max_risk_dollars=contracts * premium_per_contract,
        premium_per_contract=premium_per_contract,
        delta_adjusted_risk=round(delta_adj_risk, 2),
        theta_iv_haircut=theta_iv_haircut,
        haircut_applied_dollars=round(haircut_dollars, 2),
        warning=warning or iv_flag,
    )
