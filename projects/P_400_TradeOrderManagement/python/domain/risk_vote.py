"""P_400 domain: Portfolio-level risk checks (RISK role).

Pure logic only - no I/O, no network, no print.

RISK never blocks (Tony directive 2026-07-20). The four portfolio-composition
checks (heat, position count, daily loss, sector) plus the new cash-vs-risk
check all report at SEVERE_WARNING severity with can_block=False.
SEVERE_WARNING outranks ordinary CAUTION in council.council_verdict() but can
never produce BLOCKED -- only QUANT/MACRO/TAPE retain block authority.

Architecture v2.0 Section 4.3 (superseded 2026-07-20: block -> SEVERE_WARNING).
"""

from __future__ import annotations

import logging
from typing import List, Optional

from config import (
    DAILY_LOSS_CIRCUIT_BREAKER_PCT,
    MAX_CONCURRENT_POSITIONS,
    MAX_SECTOR_EXPOSURE,
    PORTFOLIO_HEAT_MAX_PCT,
)
from domain.council import CouncilVote, Decision, Role
from domain.council_codes import (
    RC_ALL_CLEAR,
    RC_CASH_BELOW_RISK,
    RC_DAILY_LOSS,
    RC_HEAT_BREACH,
    RC_POSITION_COUNT,
    RC_SECTOR_CONCENTRATION,
)

logger = logging.getLogger("p400.risk_vote")


def _positions_note(open_symbols: Optional[List[str]]) -> str:
    """Format the open-positions list for a reason_detail string."""
    if not open_symbols:
        return ""
    symbols = sorted(open_symbols)
    return f" Open ({len(symbols)}): {', '.join(symbols)}."


def _check_heat(
    current_heat: float, new_risk: float, balance: float, note: str
) -> Optional[CouncilVote]:
    """Heat cap check. Returns None if within cap."""
    heat_cap = balance * (PORTFOLIO_HEAT_MAX_PCT / 100.0)
    projected = current_heat + new_risk
    if projected <= heat_cap:
        return None
    return CouncilVote(
        role=Role.RISK, decision=Decision.SEVERE_WARNING, can_block=False,
        reason_code=RC_HEAT_BREACH,
        reason_detail=(
            f"Projected heat ${projected:.2f} > cap ${heat_cap:.2f} "
            f"({PORTFOLIO_HEAT_MAX_PCT}%).{note}"
        ),
    )


def _check_position_count(count: int, note: str) -> Optional[CouncilVote]:
    """Concurrent-position cap check. Returns None if under max."""
    if count < MAX_CONCURRENT_POSITIONS:
        return None
    return CouncilVote(
        role=Role.RISK, decision=Decision.SEVERE_WARNING, can_block=False,
        reason_code=RC_POSITION_COUNT,
        reason_detail=f"Positions {count} >= max {MAX_CONCURRENT_POSITIONS}.{note}",
    )


def _check_daily_loss(day_loss: float, balance: float, note: str) -> Optional[CouncilVote]:
    """Daily-loss circuit-breaker check. Returns None if under breaker."""
    breaker = balance * (DAILY_LOSS_CIRCUIT_BREAKER_PCT / 100.0)
    if day_loss < breaker:
        return None
    return CouncilVote(
        role=Role.RISK, decision=Decision.SEVERE_WARNING, can_block=False,
        reason_code=RC_DAILY_LOSS,
        reason_detail=f"Day loss ${day_loss:.2f} >= breaker ${breaker:.2f}.{note}",
    )


def _check_sector(
    new_sector: Optional[str], sector_counts: dict, note: str
) -> Optional[CouncilVote]:
    """Sector-concentration check. Returns None if under max or no sector given."""
    if not new_sector:
        return None
    sector_count = sector_counts.get(new_sector, 0)
    if sector_count < MAX_SECTOR_EXPOSURE:
        return None
    return CouncilVote(
        role=Role.RISK, decision=Decision.SEVERE_WARNING, can_block=False,
        reason_code=RC_SECTOR_CONCENTRATION,
        reason_detail=(
            f"Sector '{new_sector}' has {sector_count} open. "
            f"Max {MAX_SECTOR_EXPOSURE}.{note}"
        ),
    )


def _check_cash(cash_available: float, adjusted_risk_dollars: float, note: str) -> Optional[CouncilVote]:
    """Cash-vs-risk-per-trade check. Returns None if cash covers the risk. New 2026-07-20."""
    if cash_available >= adjusted_risk_dollars:
        return None
    return CouncilVote(
        role=Role.RISK, decision=Decision.SEVERE_WARNING, can_block=False,
        reason_code=RC_CASH_BELOW_RISK,
        reason_detail=(
            f"Cash ${cash_available:.2f} below risk-per-trade "
            f"${adjusted_risk_dollars:.2f} for this posture.{note}"
        ),
    )


def risk_vote(
    new_trade_risk_dollars: float,
    current_heat_dollars: float,
    account_balance: float,
    open_position_count: int,
    realized_day_loss_dollars: float,
    new_sector: Optional[str],
    open_sector_counts: dict,
    cash_available: float,
    adjusted_risk_dollars: float,
    open_symbols: Optional[List[str]] = None,
) -> CouncilVote:
    """Portfolio-level risk checks. Section 4.3.

    Never blocks -- highest severity is SEVERE_WARNING (can_block=False).
    Checks run in order; first hit wins.

    Args:
        new_trade_risk_dollars: Dollar risk of the trade being sized.
        current_heat_dollars: Sum of open_risk_dollars across open positions.
        account_balance: Live account balance from P_000 params.
        open_position_count: Count of OPEN_STATUSES records in the book.
        realized_day_loss_dollars: Today's realized losses (portfolio.py).
        new_sector: Sector of the symbol being evaluated, if known.
        open_sector_counts: Dict of sector -> open position count.
        cash_available: Tony-provided per-trade buying power (--cash).
        adjusted_risk_dollars: Posture-adjusted risk$ for one trade
            (sizing.adjusted_risk_dollars -- base_risk * posture_multiplier).
        open_symbols: Open position symbols, for the SEVERE_WARNING note.

    Returns:
        CouncilVote -- PASS if all five checks clear, else the first
        SEVERE_WARNING hit (can_block=False).
    """
    note = _positions_note(open_symbols)
    checks = [
        _check_heat(current_heat_dollars, new_trade_risk_dollars, account_balance, note),
        _check_position_count(open_position_count, note),
        _check_daily_loss(realized_day_loss_dollars, account_balance, note),
        _check_sector(new_sector, open_sector_counts, note),
        _check_cash(cash_available, adjusted_risk_dollars, note),
    ]
    for vote in checks:
        if vote is not None:
            return vote

    heat_cap = account_balance * (PORTFOLIO_HEAT_MAX_PCT / 100.0)
    projected_heat = current_heat_dollars + new_trade_risk_dollars
    return CouncilVote(
        role=Role.RISK, decision=Decision.PASS,
        reason_code=RC_ALL_CLEAR,
        reason_detail=(
            f"Heat ${projected_heat:.2f}/{heat_cap:.2f}. "
            f"Positions {open_position_count}/{MAX_CONCURRENT_POSITIONS}. "
            f"Cash ${cash_available:.2f} >= risk ${adjusted_risk_dollars:.2f}."
        ),
    )