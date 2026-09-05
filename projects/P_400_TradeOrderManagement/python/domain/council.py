"""P_400 domain: Council deterministic block checks.

Pure logic only - no I/O, no network, no print.
Each role function returns a CouncilVote. Verdict assembled by council_verdict().

Architecture v2.0 Section 4.
Behavioral role annotates only (can_block = False).
RISK role annotates only as of 2026-07-20 (can_block = False; SEVERE_WARNING
ceiling, never BLOCK) -- see domain/risk_vote.py for the RISK role itself.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from config import (
    MIN_ACCEPTABLE_RR,
    MIN_STOP_ATR_MULTIPLE,
    STOP_ATR_TOLERANCE,
    PRICE_STALENESS_THRESHOLD_SEC,
    POST_EARNINGS_STABILIZATION_SESSIONS,
)
from domain.council_codes import (  # noqa: F401
    RC_ADVERSE_DRIFT,
    RC_ALL_CLEAR,
    RC_EARNINGS_IN_WINDOW,
    RC_MARKET_CLOSED,
    RC_OVERTRADING,
    RC_USING_CLOSE_DATA,
    RC_USING_EXTENDED_DATA,
    RC_POST_EARNINGS_STABILIZATION,
    RC_PRICE_STALE,
    RC_REVENGE_TRADE,
    RC_RR_BELOW_MIN,
    RC_STOP_BREAKS_RR,
    RC_STOP_TOO_TIGHT,
    RC_STREAK_CHASING,
)

logger = logging.getLogger("p400.council")


class Decision(str, Enum):
    PASS = "PASS"
    CAUTION = "CAUTION"
    SEVERE_WARNING = "SEVERE_WARNING"
    BLOCK = "BLOCK"


class Role(str, Enum):
    QUANT = "QUANT"
    RISK = "RISK"
    MACRO = "MACRO"
    TAPE = "TAPE"
    BEHAVIORAL = "BEHAVIORAL"


@dataclass
class CouncilVote:
    role: Role
    decision: Decision
    reason_code: str
    reason_detail: str
    can_block: bool = True


@dataclass
class CouncilResult:
    votes: List[CouncilVote] = field(default_factory=list)
    verdict: str = "PENDING"
    block_codes: List[str] = field(default_factory=list)
    caution_codes: List[str] = field(default_factory=list)
    severe_warning_codes: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [f"Council Verdict: {self.verdict}"]
        for v in self.votes:
            lines.append(f"  {v.role.value:12s} [{v.decision.value}] {v.reason_code}: {v.reason_detail}")
        return "\n".join(lines)


def quant_vote(
    rr_at_t1: float,
    stop: float,
    entry: float,
    target: float,
    atr_14: float,
) -> CouncilVote:
    """Quant blocks: R:R, stop tightness. Section 4.2."""
    risk_per_share = entry - stop
    reward_for_2x = risk_per_share * MIN_ACCEPTABLE_RR
    if rr_at_t1 < MIN_ACCEPTABLE_RR:
        return CouncilVote(
            role=Role.QUANT, decision=Decision.BLOCK,
            reason_code=RC_RR_BELOW_MIN,
            reason_detail=(
                f"R:R {rr_at_t1:.2f} (realistic-fill, spread-adjusted) below {MIN_ACCEPTABLE_RR:.1f}. "
                f"T1={target:.2f}, needs >= {entry + reward_for_2x:.2f} (clean/guideline basis)."
            ),
        )
    if atr_14 > 0 and risk_per_share < (atr_14 * MIN_STOP_ATR_MULTIPLE) - STOP_ATR_TOLERANCE:
        return CouncilVote(
            role=Role.QUANT, decision=Decision.BLOCK,
            reason_code=RC_STOP_TOO_TIGHT,
            reason_detail=(
                f"Stop {risk_per_share:.2f} tighter than {MIN_STOP_ATR_MULTIPLE}x "
                f"ATR ({atr_14:.2f}). Whipsaw risk."
            ),
        )
    if target > (entry + reward_for_2x) * 1.5:
        return CouncilVote(
            role=Role.QUANT, decision=Decision.BLOCK,
            reason_code=RC_STOP_BREAKS_RR,
            reason_detail=f"Target {target:.2f} disproportionate to risk. Fabrication check.",
        )
    return CouncilVote(
        role=Role.QUANT, decision=Decision.PASS,
        reason_code=RC_ALL_CLEAR,
        reason_detail=f"R:R {rr_at_t1:.2f} >= {MIN_ACCEPTABLE_RR}. Stop >= 1x ATR.",
    )


def macro_vote(
    earnings_in_window: bool,
    binary_events: Optional[List[str]] = None,
    defined_risk_confirmed: bool = False,
    sessions_since_earnings: Optional[int] = None,
) -> CouncilVote:
    """Earnings / binary event blocks. Section 4.4.

    sessions_since_earnings (WO-P400-E2.023): backward-looking stabilization
    check, CAUTION-only -- never escalates to BLOCK. Different kind of risk
    than the forward-looking earnings_in_window check above (gap-fade,
    spread/IV settling, invalidated structure vs. unknown future event),
    and Tony's call 2026-07-24 was CAUTION so he can eyeball the chart
    rather than get hard-stopped every time.
    """
    binary_events = binary_events or []
    has_binary = earnings_in_window or bool(binary_events)
    if has_binary:
        event_desc = "earnings" if earnings_in_window else binary_events[0]
        if not defined_risk_confirmed:
            return CouncilVote(
                role=Role.MACRO, decision=Decision.BLOCK,
                reason_code=RC_EARNINGS_IN_WINDOW,
                reason_detail=(
                    f"Binary event ({event_desc}) inside holding period. "
                    "Confirm defined-risk to convert to CAUTION."
                ),
            )
        return CouncilVote(
            role=Role.MACRO, decision=Decision.CAUTION,
            reason_code=RC_EARNINGS_IN_WINDOW,
            reason_detail=f"Binary event ({event_desc}) inside holding period. Defined-risk confirmed.",
        )
    if (
        sessions_since_earnings is not None
        and sessions_since_earnings <= POST_EARNINGS_STABILIZATION_SESSIONS
    ):
        return CouncilVote(
            role=Role.MACRO, decision=Decision.CAUTION,
            reason_code=RC_POST_EARNINGS_STABILIZATION,
            reason_detail=(
                f"Earnings {sessions_since_earnings} session(s) ago -- inside "
                f"{POST_EARNINGS_STABILIZATION_SESSIONS}-session stabilization "
                "window. Structure/ATR may be stale, spreads may still be elevated."
            ),
        )
    return CouncilVote(
        role=Role.MACRO, decision=Decision.PASS,
        reason_code=RC_ALL_CLEAR,
        reason_detail="No binary events inside holding period.",
    )


def tape_vote(
    price_delay_seconds: int,
    market_open: bool,
    price_basis: str,
    adverse_drift_pct: float,
    rr_after_drift: float,
) -> CouncilVote:
    """Tape / momentum blocks. Section 4.5.

    price_basis: "live" (regular-session quote), "extended" (pre-market/
    after-hours live quote, WO-P400-E7.001), or "close" (last completed
    daily bar, used by fetch_snapshot when the market is closed --
    WO-P400-E5.005).
    """
    if price_delay_seconds > PRICE_STALENESS_THRESHOLD_SEC:
        return CouncilVote(
            role=Role.TAPE, decision=Decision.BLOCK,
            reason_code=RC_PRICE_STALE,
            reason_detail=f"Price {price_delay_seconds}s old (threshold {PRICE_STALENESS_THRESHOLD_SEC}s).",
        )
    if not market_open:
        if price_basis == "extended":
            return CouncilVote(
                role=Role.TAPE, decision=Decision.CAUTION,
                reason_code=RC_USING_EXTENDED_DATA,
                reason_detail="Pre-market/after-hours -- priced off a live extended-hours quote, not the regular session.",
            )
        if price_basis == "close":
            return CouncilVote(
                role=Role.TAPE, decision=Decision.CAUTION,
                reason_code=RC_USING_CLOSE_DATA,
                reason_detail="Market closed -- priced off last regular-session close, not a live quote.",
            )
        return CouncilVote(
            role=Role.TAPE, decision=Decision.BLOCK,
            reason_code=RC_MARKET_CLOSED,
            reason_detail="Market closed and no close-priced data available.",
        )
    if adverse_drift_pct > 0 and rr_after_drift < MIN_ACCEPTABLE_RR:
        return CouncilVote(
            role=Role.TAPE, decision=Decision.CAUTION,
            reason_code=RC_ADVERSE_DRIFT,
            reason_detail=(
                f"Adverse drift {adverse_drift_pct:.1f}% collapsed R:R to "
                f"{rr_after_drift:.2f} (min {MIN_ACCEPTABLE_RR})."
            ),
        )
    return CouncilVote(
        role=Role.TAPE, decision=Decision.PASS,
        reason_code=RC_ALL_CLEAR,
        reason_detail=f"Price fresh ({price_delay_seconds}s). Drift OK.",
    )


def behavioral_vote(
    symbol: str,
    recently_stopped_out_symbols: Optional[List[str]] = None,
    orders_today: int = 0,
    daily_order_norm: int = 3,
    consecutive_wins: int = 0,
    win_streak_threshold: int = 3,
) -> CouncilVote:
    """Behavioral annotations only. Never blocks. Section 4.6."""
    recently_stopped = recently_stopped_out_symbols or []
    if symbol.upper() in [s.upper() for s in recently_stopped]:
        return CouncilVote(
            role=Role.BEHAVIORAL, decision=Decision.CAUTION,
            reason_code=RC_REVENGE_TRADE,
            reason_detail=f"{symbol} stopped out recently. Possible revenge-trade.",
            can_block=False,
        )
    if orders_today > daily_order_norm * 2:
        return CouncilVote(
            role=Role.BEHAVIORAL, decision=Decision.CAUTION,
            reason_code=RC_OVERTRADING,
            reason_detail=f"{orders_today} orders today vs norm {daily_order_norm}.",
            can_block=False,
        )
    if consecutive_wins >= win_streak_threshold:
        return CouncilVote(
            role=Role.BEHAVIORAL, decision=Decision.CAUTION,
            reason_code=RC_STREAK_CHASING,
            reason_detail=f"{consecutive_wins} consecutive wins. Watch size-creep.",
            can_block=False,
        )
    return CouncilVote(
        role=Role.BEHAVIORAL, decision=Decision.PASS,
        reason_code=RC_ALL_CLEAR,
        reason_detail="No behavioral flags.",
        can_block=False,
    )


def council_verdict(votes: List[CouncilVote]) -> CouncilResult:
    """Assemble final verdict per Section 4.8.

    Priority: BLOCKED > APPROVED_WITH_SEVERE_WARNING > APPROVED_WITH_CAUTION
    > APPROVED. RISK role never blocks (Tony directive 2026-07-20) -- its
    ceiling is SEVERE_WARNING, which outranks ordinary CAUTION but can never
    produce BLOCKED. Only QUANT/MACRO/TAPE retain block authority.
    """
    result = CouncilResult(votes=votes)
    blocks = [v for v in votes if v.decision == Decision.BLOCK and v.can_block]
    severe_warnings = [v for v in votes if v.decision == Decision.SEVERE_WARNING]
    cautions = [v for v in votes if v.decision == Decision.CAUTION]
    if blocks:
        result.verdict = "BLOCKED"
        result.block_codes = [v.reason_code for v in blocks]
    elif severe_warnings:
        result.verdict = "APPROVED_WITH_SEVERE_WARNING"
        result.severe_warning_codes = [v.reason_code for v in severe_warnings]
        result.caution_codes = [v.reason_code for v in cautions]
    elif cautions:
        result.verdict = "APPROVED_WITH_CAUTION"
        result.caution_codes = [v.reason_code for v in cautions]
    else:
        result.verdict = "APPROVED"
    return result