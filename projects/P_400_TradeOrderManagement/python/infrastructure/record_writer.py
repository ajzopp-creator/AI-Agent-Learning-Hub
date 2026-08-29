"""record_writer.py ? Write P400 lifecycle record to Obsidian vault after evaluate.

Infrastructure layer: I/O only. No business logic.
Called by cli.py cmd_evaluate() after every terminal disposition, and by
application/record_commands.py for the submitted/declined dispositions
(WO-P400-E3.006).
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
    order_id: Optional[str] = None,
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

    drop_reason: ENTRY_MISSED | RR_INVALID | MANUAL_PASS | COUNCIL_BLOCK
                | MANUAL_DECLINE (WO-P400-E3.006 -- APPROVED signal, Tony
                chose not to execute)
    order_id:    Broker order id, present only on the submitted
                disposition (WO-P400-E3.006). None otherwise.

    Returns:
        True if written successfully, False otherwise.
    """
    today = date.today().isoformat()
    run_ts = datetime.now().isoformat(timespec="seconds")
    sig_date = signal_date or today

    lifecycle_status = _resolve_lifecycle_status(verdict, trade_mode_value, drop_reason, order_id)

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
        "order_id": order_id,
        # WO-P020-E1.007 Part 2 / WO-P400-E6.001: signal_source was already
        # being received here on every call (never optional) but was only
        # ever used to derive the two booleans below, then discarded --
        # why_code stayed null on every vault record ever written. P_800's
        # P400Record schema already defines why_code (obsidian_writers\
        # domain\vault_schemas.py); P_020's vault_system_reader.py already
        # reads why_code first. No schema change either side, one field add.
        "why_code": signal_source,
        "p115_linked": signal_source == "P_115",
        "p300_linked": signal_source == "P_300",
        "drop_reason": drop_reason,
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

    # WO-P400-E2.019: PAPER records route to the P400_PAPER schema, which
    # P_800's VAULT_FOLDER_MAP resolves to TradeManagement/P400/paper/ --
    # keeps paper trades out of book_loader.py's real-book read entirely.
    schema_name = "P400_PAPER" if trade_mode_value == "PAPER" else "P400"

    try:
        write_to_vault(schema_name, data)
        logger.info("P400 record written: %s verdict=%s status=%s",
                    symbol, verdict, lifecycle_status)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("record_writer: failed for %s ? %s. Record not written.", symbol, exc)
        return False


def _resolve_lifecycle_status(
    verdict: str, trade_mode: str, drop_reason: Optional[str], order_id: Optional[str] = None
) -> str:
    """Map verdict + mode + order_id to lifecycle_status string.

    An order_id present on an APPROVED/APPROVED_WITH_CAUTION verdict means
    Tony executed the trade -- SUBMITTED, checked ahead of drop_reason/
    BLOCKED (order_id only ever accompanies a real submission).
    """
    if order_id and verdict in ("APPROVED", "APPROVED_WITH_CAUTION", "APPROVED_WITH_SEVERE_WARNING"):
        return "SUBMITTED"
    if drop_reason or verdict in ("REVIEWED_NO_TRADE",):
        return "DROPPED"
    if verdict == "BLOCKED":
        return "DROPPED"
    if trade_mode == "PAPER":
        return "PAPER"
    return "PENDING"


def _build_options_fields(opt_result, stock_result, packet, trade_mode_value: str,
                           symbol: str) -> tuple[dict, str]:
    """Assemble the write_p400_record() kwargs for a single-leg options run.

    Shared by write_options_eval_record() (writes immediately) and
    commands.py (caches the same dict for the later `record` command,
    WO-P400-E3.006) -- single source of truth for the field mapping.

    WO-P400-E2.022: a stock-level Council BLOCK always wins over an
    independently-clean options council result -- the trade is blocked
    either way, and the vault record must say so. options_council never
    sees the stock-level result on its own, so that check belongs here.
    """
    stock_blocked = stock_result.verdict == "BLOCKED"
    verdict_map = {"PASS": "APPROVED", "CAUTION": "APPROVED_WITH_CAUTION", "BLOCK": "BLOCKED"}
    verdict = "BLOCKED" if stock_blocked else verdict_map.get(opt_result.verdict, opt_result.verdict)
    sizing = opt_result.sizing
    contracts = max(sizing.contracts, 1) if sizing.override_required else sizing.contracts
    drop_reason = "COUNCIL_BLOCK" if (stock_blocked or opt_result.verdict == "BLOCK") else None
    cp = opt_result.chain.expiration.replace("-", "")[2:]
    cp_type = "C" if opt_result.chain.option_type == "call" else "P"
    occ = f"{symbol}{cp}{cp_type}{opt_result.chain.strike:g}"

    fields = dict(
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
    return fields, verdict


def write_options_eval_record(opt_result, stock_result, packet, trade_mode_value: str,
                               symbol: str, order_id: Optional[str] = None):
    """Write a P400 record for a single-leg options evaluation (any verdict).

    Covers BLOCK/CAUTION/APPROVED -- full audit trail, not BLOCK-only.
    Returns (written, verdict, fields) -- fields is the exact kwargs dict
    passed to write_p400_record(), for commands.py to cache (WO-P400-E3.006).
    """
    fields, verdict = _build_options_fields(opt_result, stock_result, packet, trade_mode_value, symbol)
    written = write_p400_record(order_id=order_id, **fields)
    return written, verdict, fields


def _build_spread_fields(spread_result, stock_result, packet, trade_mode_value: str) -> tuple[dict, str]:
    """Assemble the write_p400_record() kwargs for a vertical spread run.

    Shared by write_spread_eval_record() and commands.py caching, same
    reasoning as _build_options_fields() above.

    WO-P400-E2.022: stock-level Council BLOCK always wins, same as the
    options path -- see _build_options_fields() docstring.
    """
    sp = spread_result.sizing
    stock_blocked = stock_result.verdict == "BLOCKED"
    drop_reason = None
    if stock_blocked or spread_result.council.verdict == "BLOCK":
        verdict = "BLOCKED"
        drop_reason = "COUNCIL_BLOCK"
    elif sp.override_required:
        verdict = "APPROVED_WITH_CAUTION"
    else:
        verdict = "APPROVED"
    contracts = max(sp.contracts, 1) if sp.override_required else sp.contracts

    fields = dict(
        symbol=spread_result.symbol, verdict=verdict,
        risk_mode=stock_result.posture.risk_mode,
        entry_price=stock_result.effective_entry, stop_price=stock_result.effective_stop,
        target_1=packet.guideline_target, position_size=0,
        signal_source=packet.signal_source, trade_mode_value=trade_mode_value,
        drop_reason=drop_reason, signal_date=packet.signal_metadata.session_date,
        option_method="vertical_spread", option_structure="vertical_spread",
        option_contracts=contracts, option_override=sp.override_required,
        spread_long_strike=spread_result.long_chain.strike,
        spread_short_strike=spread_result.short_chain.strike,
        spread_debit=sp.debit_per_spread, spread_max_profit=sp.max_profit_per_spread,
        spread_max_loss=sp.max_loss_per_spread, spread_breakeven=sp.breakeven,
    )
    return fields, verdict


def write_spread_eval_record(spread_result, stock_result, packet, trade_mode_value: str,
                              order_id: Optional[str] = None):
    """Write a P400 record for a vertical spread evaluation (any outcome).

    Returns (written, verdict, fields) -- see write_options_eval_record().
    """
    fields, verdict = _build_spread_fields(spread_result, stock_result, packet, trade_mode_value)
    written = write_p400_record(order_id=order_id, **fields)
    return written, verdict, fields
