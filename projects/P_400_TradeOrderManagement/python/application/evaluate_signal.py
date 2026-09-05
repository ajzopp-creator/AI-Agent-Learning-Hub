"""P_400 application: full signal evaluation pipeline.

Orchestration: reads posture + params + book fresh, builds portfolio state,
runs reconciliation, sizes, runs Council, returns EvaluationResult.
No business logic -- calls domain and infra in sequence only.

Architecture v2.0 Section 2.1 (Tier-2 path), 2.2, 6.2.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from config import (
    ENTRY_DRIFT_THRESHOLD_PCT,
    MAX_PLAUSIBLE_SPREAD_PCT,
    MAX_PLAUSIBLE_SPREAD_PCT_EXTENDED,
    MIN_ACCEPTABLE_RR,
    MAX_CONCURRENT_POSITIONS,
    PORTFOLIO_HEAT_MAX_PCT,
    TradeMode,
    DEFAULT_TRADE_MODE,
)
from application.tape_block import _tape_block_result
from domain.council import (
    CouncilResult,
    behavioral_vote,
    council_verdict,
    macro_vote,
    quant_vote,
    tape_vote,
)
from domain.council_codes import RC_ADVERSE_DRIFT, RC_SPREAD_TOO_WIDE
from domain.risk_vote import risk_vote
from domain.portfolio import PortfolioState, build_portfolio_state
from domain.behavioral_history import compute_behavioral_inputs
from domain.earnings_window import earnings_in_window, sessions_since_earnings
from domain.sizing import SizingResult, realistic_fill_rr, three_gate_size
from infrastructure.book_loader import load_book
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from schemas import AccountParams, PostureSnapshot, SignalV2, SnapshotDict
from pathlib import Path

logger = logging.getLogger("p400.evaluate")


@dataclass
class EvaluationResult:
    """Full pipeline output for one signal evaluation."""

    symbol: str
    verdict: str                  # APPROVED | APPROVED_WITH_CAUTION | APPROVED_WITH_SEVERE_WARNING | BLOCKED
    council: CouncilResult
    sizing: Optional[SizingResult]
    portfolio_state: PortfolioState
    posture: PostureSnapshot
    params: AccountParams
    drift_pct: float              # (live_price - guideline_entry) / guideline_entry * 100
    rr_after_drift: float         # R:R at live price vs original stop/target
    snapshot_source: str          # from snapshot["data_source"]
    trade_mode: TradeMode = DEFAULT_TRADE_MODE
    qty_override: Optional[int] = None  # trader override; bypasses concentration gate post-verdict
    effective_entry: float = 0.0  # live snapshot price actually used as entry
    effective_stop: float = 0.0   # guideline_stop or override, actually used in sizing/council

    def is_approved(self) -> bool:
        return self.verdict in (
            "APPROVED", "APPROVED_WITH_CAUTION", "APPROVED_WITH_SEVERE_WARNING",
        )

    def first_block(self) -> Optional[str]:
        return self.council.block_codes[0] if self.council.block_codes else None

    def is_paper(self) -> bool:
        return self.trade_mode == TradeMode.PAPER


def evaluate_signal(
    packet: SignalV2,
    snapshot: dict,
    cash_available: float,
    trade_mode: TradeMode = DEFAULT_TRADE_MODE,
    qty_override: Optional[int] = None,
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
    behavioral = compute_behavioral_inputs(records)

    # -- Reconciliation: entry resolution (Section 6.5) + live R:R --
    half_spread = (snap.ask - snap.bid) / 2.0 if snap.bid and snap.ask else 0.0

    # Spread plausibility gate (WO-P400-E4.004, extended threshold WO-P400-E7.001)
    # -- must run before any R:R math touches half_spread. A wide/bad spread
    # corrupts realistic-fill R:R silently (found live 2026-07-26: CAE
    # half_spread=$2.34 -> R:R computed as -1.00 on a setup that was actually
    # >2.0 by naive math). Extended-hours quotes get a wider, separate
    # ceiling -- genuinely thinner liquidity, not the same signal as a bad
    # regular-hours quote.
    spread_threshold = (
        MAX_PLAUSIBLE_SPREAD_PCT_EXTENDED if snap.price_basis == "extended"
        else MAX_PLAUSIBLE_SPREAD_PCT
    )
    spread_pct = (half_spread / snap.price * 100) if snap.price else 0.0
    if spread_pct > spread_threshold:
        logger.warning(
            '%s: spread %.1f%% of price exceeds %.1f%% plausibility threshold. SPREAD_TOO_WIDE.',
            packet.symbol, spread_pct, spread_threshold,
        )
        return _tape_block_result(
            packet, snap, trade_mode, qty_override, effective_stop,
            reason_code=RC_SPREAD_TOO_WIDE,
            reason_detail=f'Spread {spread_pct:.1f}% of price exceeds {spread_threshold}% plausibility threshold. Fill quality unacceptable.',
        )

    drift_pct = round((snap.price - packet.guideline_entry) / packet.guideline_entry * 100, 3)

    # Case 1: favorable pullback ? live below guideline, use live price (R:R improves)
    # Case 2: within threshold ? use live price (small adverse drift, still tradeable)
    # Case 3: entry missed ? adverse drift > threshold; check if R:R survives
    if drift_pct > ENTRY_DRIFT_THRESHOLD_PCT:
        rr_check = realistic_fill_rr(
            entry=snap.price,
            stop=effective_stop,
            target=packet.guideline_target,
            half_spread=half_spread,
        )
        if rr_check < MIN_ACCEPTABLE_RR:
            logger.warning(
                '%s: entry missed -- drift %.2f%% collapses R:R to %.2f (min %.1f). ENTRY_MISSED.',
                packet.symbol, drift_pct, rr_check, MIN_ACCEPTABLE_RR,
            )
            # archive_packet() moved to cli.py call sites (WO-P400-E2.015) --
            # archiving must happen after the full pipeline (incl. any
            # vault-record write) completes, not mid-evaluation.
            return _tape_block_result(
                packet, snap, trade_mode, qty_override, effective_stop,
                reason_code=RC_ADVERSE_DRIFT,
                reason_detail=f'Entry missed: drift {drift_pct:.2f}% collapses R:R to {rr_check:.2f}. drop_reason=ENTRY_MISSED.',
                drift_pct=drift_pct, rr_value=rr_check,
            )
        else:
            logger.info(
                '%s: adverse drift %.2f%% but R:R %.2f still clears minimum -- proceeding.',
                packet.symbol, drift_pct, rr_check,
            )

    rr_after_drift = realistic_fill_rr(
        entry=snap.price,
        stop=effective_stop,
        target=packet.guideline_target,
        half_spread=half_spread,
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

    # -- Qty override (post-sizing, pre-council; does not bypass council gates) --
    if qty_override is not None and qty_override > 0 and sizing.shares > 0:
        _risk_per_share = sizing.dollar_risk / sizing.shares
        import dataclasses
        sizing = dataclasses.replace(
            sizing,
            shares=qty_override,
            dollar_risk=round(_risk_per_share * qty_override, 2),
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
            cash_available=cash_available,
            adjusted_risk_dollars=sizing.adjusted_risk_dollars,
            open_symbols=sorted(port_state.open_symbols),
        ),
        macro_vote(
            earnings_in_window=earnings_in_window(snap.next_earnings_date),
            binary_events=snap.binary_events,
            sessions_since_earnings=sessions_since_earnings(snap.last_earnings_date),
        ),
        tape_vote(
            price_delay_seconds=snap.price_delay_seconds,
            market_open=snap.market_open,
            price_basis=snap.price_basis,
            adverse_drift_pct=adverse_drift,
            rr_after_drift=rr_after_drift,
        ),
        behavioral_vote(
            symbol=packet.symbol,
            recently_stopped_out_symbols=behavioral.recently_stopped_out_symbols,
            orders_today=behavioral.orders_today,
            consecutive_wins=behavioral.consecutive_wins,
        ),
    ]
    council = council_verdict(votes)
    # archive_packet() moved to cli.py call sites (WO-P400-E2.015)

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
        qty_override=qty_override,
        trade_mode=trade_mode,
        effective_entry=snap.price,
        effective_stop=effective_stop,
    )
