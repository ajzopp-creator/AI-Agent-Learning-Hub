"""record_writer.py ? Write P400 lifecycle record to Obsidian vault after evaluate.

Infrastructure layer: I/O only. No business logic.
Called by cli.py cmd_evaluate() after every terminal disposition.
"""

from __future__ import annotations

import logging
from datetime import datetime, date
from typing import Optional

from shared_resources.python_utils.vault_interface import write_to_vault

logger = logging.getLogger("p400.record_writer")


def write_p400_record(
    symbol: str,
    verdict: str,
    risk_mode: str,
    entry_price: float,
    stop_price: float,
    target_1: float,
    position_size: int,
    signal_source: str,
    trade_mode_value: str,
    drop_reason: Optional[str] = None,
    signal_date: Optional[str] = None,
    # Options fields (all None for stock trades)
    option_method: Optional[str] = None,
    option_structure: Optional[str] = None,
    option_contract: Optional[str] = None,
    option_entry_premium: Optional[float] = None,
    option_stop_premium: Optional[float] = None,
    option_target_premium: Optional[float] = None,
    option_contracts: Optional[int] = None,
    option_override: Optional[bool] = None,
    option_override_justification: Optional[str] = None,
    iv_rank: Optional[float] = None,
    # Spread fields (all None for stock/single-leg trades)
    spread_long_strike: Optional[float] = None,
    spread_short_strike: Optional[float] = None,
    spread_debit: Optional[float] = None,
    spread_max_profit: Optional[float] = None,
    spread_max_loss: Optional[float] = None,
    spread_breakeven: Optional[float] = None,
) -> bool:
    """Write a P400 lifecycle record to the Obsidian vault.

    Never raises ? write failure logs a warning and returns False so
    the calling eval result is never blocked by a vault I/O error.

    Args:
        symbol:           Ticker symbol.
        verdict:          Council verdict string (APPROVED, BLOCKED, etc.).
        risk_mode:        Current P_010 risk mode string.
        entry_price:      Live snapshot price used as entry.
        stop_price:       Effective stop price.
        target_1:         T1 target price.
        position_size:    Final share count (post-override if applicable).
        signal_source:    P_115, P_300, etc. ? sets p115_linked / p300_linked.
        trade_mode_value: "REAL" or "PAPER".
        drop_reason:      ENTRY_MISSED | RR_INVALID | MANUAL_PASS | COUNCIL_BLOCK
        signal_date:      YYYY-MM-DD of the originating signal session.

    Returns:
        True if written successfully, False otherwise.
    """
    today = date.today().isoformat()
    run_ts = datetime.now().isoformat(timespec="seconds")
    sig_date = signal_date or today

    lifecycle_status = _resolve_lifecycle_status(verdict, trade_mode_value, drop_reason)

    data = {
        "signal_date": sig_date,
        "run_date": today,
        "run_ts": run_ts,
        "written_by": "P_400/cli_evaluate",
        "ticker": symbol,
        "council_verdict": verdict,
        "lifecycle_status": lifecycle_status,
        "risk_mode": risk_mode,
        "entry_price": entry_price,
        "stop_price": stop_price,
        "target_1": target_1,
        "position_size": position_size,
        "p115_linked": signal_source == "P_115",
        "p300_linked": signal_source == "P_300",
        "drop_reason": drop_reason,
        # Options fields -- None for stock trades; populated for options path
        "option_method": option_method,
        "option_structure": option_structure,
        "option_contract": option_contract,
        "option_entry_premium": option_entry_premium,
        "option_stop_premium": option_stop_premium,
        "option_target_premium": option_target_premium,
        "option_contracts": option_contracts,
        "option_override": option_override,
        "option_override_justification": option_override_justification,
        "iv_rank": iv_rank,
        "spread_long_strike": spread_long_strike,
        "spread_short_strike": spread_short_strike,
        "spread_debit": spread_debit,
        "spread_max_profit": spread_max_profit,
        "spread_max_loss": spread_max_loss,
        "spread_breakeven": spread_breakeven,
    }

    try:
        write_to_vault("P400", data)
        logger.info("P400 record written: %s verdict=%s status=%s",
                    symbol, verdict, lifecycle_status)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("record_writer: failed for %s ? %s. Record not written.", symbol, exc)
        return False


def _resolve_lifecycle_status(verdict: str, trade_mode: str, drop_reason: Optional[str]) -> str:
    """Map verdict + mode to lifecycle_status string."""
    if drop_reason or verdict in ("REVIEWED_NO_TRADE",):
        return "DROPPED"
    if verdict == "BLOCKED":
        return "DROPPED"
    if trade_mode == "PAPER":
        return "PAPER"
    return "PENDING"


def write_options_eval_record(opt_result, stock_result, packet, trade_mode_value: str,
                               symbol: str) -> bool:
    """Write a P400 record for a single-leg options evaluation (any verdict).

    Wraps write_p400_record() with the options field-mapping logic so
    cli.py stays a thin call site. Covers BLOCK/CAUTION/APPROVED -- full
    audit trail, not BLOCK-only.
    """
    verdict_map = {"PASS": "APPROVED", "CAUTION": "APPROVED_WITH_CAUTION", "BLOCK": "BLOCKED"}
    verdict = verdict_map.get(opt_result.verdict, opt_result.verdict)
    sizing = opt_result.sizing
    contracts = max(sizing.contracts, 1) if sizing.override_required else sizing.contracts
    drop_reason = "COUNCIL_BLOCK" if opt_result.verdict == "BLOCK" else None
    cp = opt_result.chain.expiration.replace("-", "")[2:]
    cp_type = "C" if opt_result.chain.option_type == "call" else "P"
    occ = f"{symbol}{cp}{cp_type}{opt_result.chain.strike:g}"

    written = write_p400_record(
        symbol=opt_result.symbol, verdict=verdict,
        risk_mode=stock_result.posture.risk_mode,
        entry_price=stock_result.effective_entry, stop_price=stock_result.effective_stop,
        target_1=packet.guideline_target, position_size=0,
        signal_source=packet.signal_source, trade_mode_value=trade_mode_value,
        drop_reason=drop_reason, signal_date=packet.signal_metadata.session_date,
        option_method=sizing.method, option_structure="single_leg", option_contract=occ,
        option_entry_premium=sizing.option_entry, option_stop_premium=sizing.option_stop,
        option_target_premium=sizing.option_target, option_contracts=contracts,
        option_override=sizing.override_required, iv_rank=opt_result.chain.iv,
    )
    return written, verdict


def write_spread_eval_record(spread_result, stock_result, packet, trade_mode_value: str) -> bool:
    """Write a P400 record for a vertical spread evaluation (any outcome).

    No council verdict exists for spreads yet (WO-P400-E3.005) -- maps
    override_required to APPROVED_WITH_CAUTION, otherwise APPROVED.
    """
    sp = spread_result.sizing
    verdict = "APPROVED_WITH_CAUTION" if sp.override_required else "APPROVED"
    contracts = max(sp.contracts, 1) if sp.override_required else sp.contracts

    written = write_p400_record(
        symbol=spread_result.symbol, verdict=verdict,
        risk_mode=stock_result.posture.risk_mode,
        entry_price=stock_result.effective_entry, stop_price=stock_result.effective_stop,
        target_1=packet.guideline_target, position_size=0,
        signal_source=packet.signal_source, trade_mode_value=trade_mode_value,
        signal_date=packet.signal_metadata.session_date,
        option_method="vertical_spread", option_structure="vertical_spread",
        option_contracts=contracts, option_override=sp.override_required,
        spread_long_strike=spread_result.long_chain.strike,
        spread_short_strike=spread_result.short_chain.strike,
        spread_debit=sp.debit_per_spread, spread_max_profit=sp.max_profit_per_spread,
        spread_max_loss=sp.max_loss_per_spread, spread_breakeven=sp.breakeven,
    )
    return written, verdict