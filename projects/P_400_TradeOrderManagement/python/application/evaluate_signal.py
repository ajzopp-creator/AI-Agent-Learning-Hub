"""P_400 application: full signal evaluation pipeline.

Orchestration: reads posture + params + book fresh, builds portfolio state,
runs reconciliation, sizes, runs Council, returns EvaluationResult.
No business logic -- calls domain and infra in sequence only.

Architecture v2.0 Section 2.1 (Tier-2 path), 2.2, 6.2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

from config import (
    ENTRY_DRIFT_THRESHOLD_PCT,
    MAX_CONCURRENT_POSITIONS,
    PORTFOLIO_HEAT_MAX_PCT,
    TradeMode,
    DEFAULT_TRADE_MODE,
)
from domain.council import (
    CouncilResult,
    behavioral_vote,
    council_verdict,
    macro_vote,
    quant_vote,
    risk_vote,
    tape_vote,
)
from domain.portfolio import PortfolioState, build_portfolio_state
from domain.sizing import SizingResult, realistic_fill_rr, three_gate_size
from infrastructure.book_loader import load_book
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from schemas import AccountParams, PostureSnapshot, SignalV2, SnapshotDict

logger = logging.getLogger("p400.evaluate")


@dataclass
class EvaluationResult:
    """Full pipeline output for one signal evaluation."""

    symbol: str
    verdict: str                  # APPROVED | APPROVED_WITH_CAUTION | BLOCKED
    council: CouncilResult
    sizing: Optional[SizingResult]
    portfolio_state: PortfolioState
    posture: PostureSnapshot
    params: AccountParams
    drift_pct: float              # (live_price - guideline_entry) / guideline_entry * 100
    rr_after_drift: float         # R:R at live price vs original stop/target
    snapshot_source: str          # from snapshot["data_source"]
    trade_mode: TradeMode = DEFAULT_TRADE_MODE

    def is_approved(self) -> bool:
        return self.verdict in ("APPROVED", "APPROVED_WITH_CAUTION")

    def first_block(self) -> Optional[str]:
        return self.council.block_codes[0] if self.council.block_codes else None

    def is_paper(self) -> bool:
        return self.trade_mode == TradeMode.PAPER


def _earnings_in_window(next_earnings_date: Optional[str]) -> bool:
    """Return True if earnings date is within 14 calendar days (conservative window)."""
    if not next_earnings_date:
        return False
    try:
        earnings = date.fromisoformat(next_earnings_date)
        return (earnings - date.today()).days <= 14
    except ValueError:
        return False


def evaluate_signal(
    packet: SignalV2,
    snapshot: dict,
    cash_available: float,
    trade_mode: TradeMode = DEFAULT_TRADE_MODE,
) -> EvaluationResult:
    """Run the full deterministic evaluation pipeline for one signal.

    Reads posture, params, and book from filesystem fresh (never cached).
    Raises ValueError (via Pydantic) if snapshot is missing required keys.

    Args:
        packet: Validated SignalV2 from the inbox.
        snapshot: Live-market data dict assembled by Claude (Section 6.2).
        cash_available: Per-trade buying power provided by Tony at eval time.
        trade_mode: REAL (default) or PAPER. Sizing rules identical for both.

    Returns:
        EvaluationResult with verdict, sizing, Council votes, and audit fields.
    """
    snap = SnapshotDict(**snapshot)
    effective_stop = snap.guideline_stop_override or packet.guideline_stop

    # -- Infra reads (always fresh) --
    posture = read_posture()
    params = read_params()
    records = load_book()
    port_state = build_portfolio_state(records)

    # -- Reconciliation: drift and live R:R --
    half_spread = (snap.ask - snap.bid) / 2.0 if snap.bid and snap.ask else 0.0
    drift_pct = round((snap.price - packet.guideline_entry) / packet.guideline_entry * 100, 3)
    rr_after_drift = realistic_fill_rr(
        entry=snap.price,
        stop=effective_stop,
        target=packet.guideline_target,
        half_spread=half_spread,
    )
    if abs(drift_pct) > ENTRY_DRIFT_THRESHOLD_PCT:
        logger.info(
            "%s: entry drift %.2f%% (threshold %.1f%%) -- using live price %.2f",
            packet.symbol, drift_pct, ENTRY_DRIFT_THRESHOLD_PCT, snap.price,
        )
    if snap.guideline_stop_override:
        logger.info(
            "%s: stop override %.2f (packet stop %.2f) -- P_400 drift reconciliation",
            packet.symbol, effective_stop, packet.guideline_stop,
        )

    # -- Three-gate sizing (using live price as entry) --
    sizing = three_gate_size(
        entry=snap.price,
        stop=effective_stop,
        target=packet.guideline_target,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash_available,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
        half_spread=half_spread,
    )

    # -- Council votes --
    heat_cap = params.account_balance * (PORTFOLIO_HEAT_MAX_PCT / 100.0)
    adverse_drift = max(0.0, -drift_pct)   # negative drift = adverse for a long
    votes = [
        quant_vote(
            rr_at_t1=rr_after_drift,
            stop=effective_stop,
            entry=snap.price,
            target=packet.guideline_target,
            atr_14=snap.atr_14,
        ),
        risk_vote(
            new_trade_risk_dollars=sizing.dollar_risk,
            current_heat_dollars=port_state.heat_dollars,
            account_balance=params.account_balance,
            open_position_count=port_state.open_position_count,
            realized_day_loss_dollars=port_state.realized_day_loss_dollars,
            new_sector=snap.sector,
            open_sector_counts=port_state.open_sector_counts,
        ),
        macro_vote(
            earnings_in_window=_earnings_in_window(snap.next_earnings_date),
            binary_events=snap.binary_events,
        ),
        tape_vote(
            price_delay_seconds=snap.price_delay_seconds,
            market_open=snap.market_open,
            pre_market_flag=False,
            adverse_drift_pct=adverse_drift,
            rr_after_drift=rr_after_drift,
        ),
        behavioral_vote(symbol=packet.symbol),
    ]
    council = council_verdict(votes)

    logger.info(
        "Evaluated %s: verdict=%s mode=%s drift=%.2f%% rr=%.2f src=%s",
        packet.symbol, council.verdict, trade_mode.value,
        drift_pct, rr_after_drift, snap.data_source,
    )
    return EvaluationResult(
        symbol=packet.symbol,
        verdict=council.verdict,
        council=council,
        sizing=sizing,
        portfolio_state=port_state,
        posture=posture,
        params=params,
        drift_pct=drift_pct,
        rr_after_drift=rr_after_drift,
        snapshot_source=snap.data_source,
        trade_mode=trade_mode,
    )
