"""tape_block.py -- shared synthetic-TAPE-BLOCK early exit.

Extracted from evaluate_signal.py (WO-P400-E4.004) once that file crossed
the 300-line hard cap. Same pattern as WO-P400-E4.001's spec_commands.py
split off commands.py -- append would have exceeded the limit, so a new
file instead.
"""

from __future__ import annotations

from typing import Optional

from config import TradeMode
from domain.council import CouncilVote, Decision, Role, council_verdict
from domain.portfolio import build_portfolio_state
from infrastructure.book_loader import load_book
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from schemas import SignalV2, SnapshotDict


def _tape_block_result(
    packet: SignalV2,
    snap: SnapshotDict,
    trade_mode: TradeMode,
    qty_override: Optional[int],
    effective_stop: float,
    reason_code: str,
    reason_detail: str,
    drift_pct: float = 0.0,
    rr_value: float = 0.0,
):
    """Shared early-exit: synthetic TAPE BLOCK, skips sizing/full Council.

    Used by reconciliation-boundary checks (Section 6.5 ENTRY_MISSED, and
    WO-P400-E4.004 SPREAD_TOO_WIDE) that must stop the pipeline before
    R:R math runs on untrustworthy inputs. Caller writes REVIEWED_NO_TRADE.

    Returns an EvaluationResult -- imported locally to avoid a circular
    import (evaluate_signal.py imports this module).
    """
    from application.evaluate_signal import EvaluationResult

    block_vote = CouncilVote(
        role=Role.TAPE, decision=Decision.BLOCK,
        reason_code=reason_code, reason_detail=reason_detail,
    )
    dummy_council = council_verdict([block_vote])
    return EvaluationResult(
        symbol=packet.symbol, verdict=dummy_council.verdict,
        council=dummy_council, sizing=None,
        portfolio_state=build_portfolio_state(load_book()),
        posture=read_posture(), params=read_params(),
        drift_pct=drift_pct, rr_after_drift=rr_value,
        snapshot_source=snap.data_source, trade_mode=trade_mode,
        qty_override=qty_override,
        effective_entry=snap.price, effective_stop=effective_stop,
    )