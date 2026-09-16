"""build_option_spec_scaleout.py -- Pattern B scale-out: two independent
OCO brackets sharing one stop (WO-P400-E8.003).

Application layer: orchestration/render only -- no business logic, no I/O.
Called by build_option_spec.py when stock_target_2 is given. Never called
directly by cli.py or any other caller -- build_option_spec() is the one
public entry point for Pattern B, single- or dual-target.

TOS cannot chain one entry into two separate OCO groups in a single order
ticket, so this renders 5 legs: one shared entry (full contracts, BUY TO
OPEN), then two independent stop/target OCO pairs, one per half. Leg 1's
note says so explicitly -- Tony enters both OCO pairs manually once the
entry fills, not as one ticket.

Contracts split floor/remainder-to-T2 (the further target gets the extra
contract on an odd count, since it's carrying more of the open risk for
longer). A target_1-only or target_2-only case never reaches this file --
build_option_spec.py only delegates here when both targets are set.
"""

from __future__ import annotations

from domain.options_sizer import OptionSizingResult, translate_target_premium
from schemas import OptionChainInput

_SEP = "=" * 60
_DIV = "-" * 60


def _split_contracts(contracts: int) -> tuple[int, int]:
    """Floor to T1, remainder to T2. (1, 0) on a single contract -- T2 gets
    nothing rather than a fractional/duplicate leg; not a real scale-out
    below 2 contracts."""
    half = contracts // 2
    return half, contracts - half


def _rr_at(option_entry: float, option_stop: float, option_target: float) -> float:
    risk = option_entry - option_stop
    if risk <= 0:
        return 0.0
    return round((option_target - option_entry) / risk, 2)


def _summary_block(
    underlying_symbol: str,
    option_sym: str,
    chain: OptionChainInput,
    sizing: OptionSizingResult,
    contracts_1: int,
    contracts_2: int,
    option_target_2: float,
    rr_2: float,
    leverage: float,
) -> list:
    return [
        _SEP,
        "PATTERN B -- Single-Leg Option, Scale-Out  (1 Entry -> 2 OCO groups)",
        _SEP,
        "",
        f"  Underlying:   {underlying_symbol}",
        f"  Option:       {option_sym}",
        f"  Structure:    {chain.option_type.upper()}  strike {chain.strike:.2f}  exp {chain.expiration}",
        f"  Method:       {sizing.method}",
        f"  Contracts:    {contracts_1 + contracts_2}  ({contracts_1} @ T1, {contracts_2} @ T2)",
        "",
        f"  Entry premium: ${sizing.option_entry:.2f}  (mid)",
        f"  Dollar risk:   ${sizing.risk_per_contract * (contracts_1 + contracts_2):.2f}  "
        f"(${sizing.risk_per_contract:.2f}/contract)",
        f"  R:R at T1:     {sizing.rr_option:.2f}",
        f"  R:R at T2:     {rr_2:.2f}",
        f"  Risk budget:   ${sizing.adjusted_risk_budget:.2f}",
        f"  Leverage:      {leverage:.1f}x  (delta {chain.delta:.2f})",
        "",
    ]


def _dual_price_block(
    underlying_symbol: str,
    sizing: OptionSizingResult,
    stock_entry: float,
    stock_stop: float,
    stock_target_1: float,
    stock_target_2: float,
    option_target_2: float,
) -> list:
    return [
        _DIV,
        "  STOCK -> OPTION  (delta-derived option estimates)",
        _DIV,
        f"  Entry:  {underlying_symbol} {stock_entry:.2f}  ->  option ${sizing.option_entry:.2f}",
        f"  Stop:   {underlying_symbol} {stock_stop:.2f}  ->  option ~${sizing.option_stop:.2f}",
        f"  T1:     {underlying_symbol} {stock_target_1:.2f}  ->  option ~${sizing.option_target:.2f}",
        f"  T2:     {underlying_symbol} {stock_target_2:.2f}  ->  option ~${option_target_2:.2f}",
        "",
    ]


def _bracket_legs(
    underlying_symbol: str,
    option_sym: str,
    bracket_label: str,
    contracts: int,
    stock_stop: float,
    option_stop: float,
    stock_target: float,
    option_target: float,
) -> list:
    """One OCO pair (stop + target) for one bracket's share of contracts."""
    return [
        _DIV,
        f"  {bracket_label} -- Stop Loss  (UNDERLYING trigger -- P_000 Options Rule)",
        _DIV,
        f"  Trigger: {underlying_symbol} stock at or below {stock_stop:.2f}",
        "  Action:  SELL TO CLOSE",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_sym}",
        f"  Order:   STOP-LIMIT  (limit bid-aware ~${option_stop:.2f})",
        "  TIF:     GTC",
        "",
        _DIV,
        f"  {bracket_label} -- Take Profit  (underlying target reference)",
        _DIV,
        f"  Trigger: {underlying_symbol} stock at or above {stock_target:.2f}",
        "  Action:  SELL TO CLOSE",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_sym}",
        f"  Order:   LIMIT  (bid-aware ~${option_target:.2f})",
        "  TIF:     GTC",
        "",
    ]


def _legs_block(
    underlying_symbol: str,
    option_sym: str,
    contracts_1: int,
    contracts_2: int,
    sizing: OptionSizingResult,
    stock_stop: float,
    stock_target_1: float,
    stock_target_2: float,
    option_target_2: float,
) -> list:
    lines = [
        _DIV,
        "  LEG 1 -- Entry  (fills once for the full quantity)",
        _DIV,
        "  Action:  BUY TO OPEN",
        f"  Qty:     {contracts_1 + contracts_2}",
        f"  Symbol:  {option_sym}",
        "  Order:   LIMIT",
        f"  Price:   {sizing.option_entry:.2f}  (mid; adjust bid-aware)",
        "  TIF:     DAY",
        "  NOTE:    TOS can't chain one entry into two OCO groups in one",
        "           ticket -- enter both OCO brackets below manually once",
        "           this fills.",
        "",
    ]
    if contracts_1 > 0:
        lines += _bracket_legs(
            underlying_symbol, option_sym, "BRACKET 1 (T1)", contracts_1,
            stock_stop, sizing.option_stop, stock_target_1, sizing.option_target,
        )
    if contracts_2 > 0:
        lines += _bracket_legs(
            underlying_symbol, option_sym, "BRACKET 2 (T2)", contracts_2,
            stock_stop, sizing.option_stop, stock_target_2, option_target_2,
        )
    lines.append(_SEP)
    return lines


def build_option_spec_scaleout(
    underlying_symbol: str,
    option_sym: str,
    chain: OptionChainInput,
    sizing: OptionSizingResult,
    contracts: int,
    leverage: float,
    stock_entry: float,
    stock_stop: float,
    stock_target_1: float,
    stock_target_2: float,
) -> str:
    """Render the scale-out body (no override_note/paper_banner -- the
    caller, build_option_spec(), prepends those; identical for both the
    single- and dual-target paths).

    Args:
        underlying_symbol, option_sym: Same as build_option_spec().
        chain, sizing: Same as build_option_spec() -- sizing was computed
            against stock_target_1 upstream (the near-term, sizing-gate
            target); this function derives T2's premium equivalent from
            the same chain.delta, it does not re-run the sizer.
        contracts: Already-resolved total contract count (override-adjusted
            by the caller, not raw sizing.contracts).
        leverage: Already-computed leverage multiple.
        stock_entry, stock_stop: Shared across both brackets.
        stock_target_1, stock_target_2: The two underlying targets.

    Returns:
        Multi-line string spec body.
    """
    contracts_1, contracts_2 = _split_contracts(contracts)
    option_target_2 = translate_target_premium(
        sizing.option_entry, chain.delta, stock_target_2 - stock_entry,
    )
    rr_2 = _rr_at(sizing.option_entry, sizing.option_stop, option_target_2)

    lines = []
    lines += _summary_block(underlying_symbol, option_sym, chain, sizing,
                            contracts_1, contracts_2, option_target_2, rr_2, leverage)
    lines += _dual_price_block(underlying_symbol, sizing, stock_entry, stock_stop,
                               stock_target_1, stock_target_2, option_target_2)
    lines += _legs_block(underlying_symbol, option_sym, contracts_1, contracts_2,
                         sizing, stock_stop, stock_target_1, stock_target_2, option_target_2)

    return "\n".join(lines)
