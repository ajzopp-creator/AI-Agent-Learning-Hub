"""build_option_spec.py -- Pattern B: single-leg option Schwab grid renderer.

Application layer: orchestration/render only -- no business logic, no I/O.
Receives an OptionSizingResult plus the OptionChainInput and the stock trio
(entry/stop/target); returns plain text Tony can type into Schwab.

Mirrors build_spread_spec.py (Pattern C). Shows BOTH stock and option prices
at entry/stop/T1 per Architecture v2.1 Section 3.8, with delta-derived option
estimates and the leverage multiple. The Leg 2 stop trigger is the UNDERLYING
stock price (P_000 Options Rule), never the option Mark.

Architecture v2.1 Section 7.3 (WO-P400-E3.001), Section 6.3 Pattern B, 3.8.
"""

from __future__ import annotations

import logging
from datetime import datetime

from domain.options_sizer import OptionSizingResult
from schemas import OptionChainInput

logger = logging.getLogger("p400.build_option_spec")

_SEP = "=" * 60
_DIV = "-" * 60


def _occ_symbol(symbol: str, expiry: str, option_type: str, strike: float) -> str:
    """Build OCC option symbol (6-char underlying + YYMMDD + C/P + 8-digit strike)."""
    dt = datetime.strptime(expiry, "%Y-%m-%d")
    yymmdd = dt.strftime("%y%m%d")
    cp = "C" if option_type.lower() == "call" else "P"
    strike_int = int(round(strike * 1000))
    return f"{symbol:<6}{yymmdd}{cp}{strike_int:08d}"


def _leverage_multiple(delta: float, stock_entry: float, option_mid: float) -> float:
    """Effective leverage: |delta| * stock_price / option premium."""
    if option_mid <= 0:
        return 0.0
    return round((abs(delta) * stock_entry) / option_mid, 1)


def _summary_block(
    underlying_symbol: str,
    option_sym: str,
    chain: OptionChainInput,
    sizing: OptionSizingResult,
    contracts: int,
    leverage: float,
) -> list:
    """Top summary lines for the spec."""
    return [
        _SEP,
        "PATTERN B -- Single-Leg Option  (1st-Triggers-All)",
        _SEP,
        "",
        f"  Underlying:   {underlying_symbol}",
        f"  Option:       {option_sym}",
        f"  Structure:    {chain.option_type.upper()}  strike {chain.strike:.2f}  exp {chain.expiration}",
        f"  Method:       {sizing.method}",
        f"  Contracts:    {contracts}",
        "",
        f"  Entry premium: ${sizing.option_entry:.2f}  (mid)",
        f"  Dollar risk:   ${sizing.risk_per_contract * contracts:.2f}  "
        f"(${sizing.risk_per_contract:.2f}/contract)",
        f"  R:R at T1:     {sizing.rr_option:.2f}",
        f"  Risk budget:   ${sizing.adjusted_risk_budget:.2f}",
        f"  Leverage:      {leverage:.1f}x  (delta {chain.delta:.2f})",
        "",
    ]


def _dual_price_block(
    underlying_symbol: str,
    sizing: OptionSizingResult,
    stock_entry: float,
    stock_stop: float,
    stock_target: float,
) -> list:
    """Stock -> option price display for entry, stop, T1 (Section 3.8)."""
    return [
        _DIV,
        "  STOCK -> OPTION  (delta-derived option estimates)",
        _DIV,
        f"  Entry:  {underlying_symbol} {stock_entry:.2f}  ->  option ${sizing.option_entry:.2f}",
        f"  Stop:   {underlying_symbol} {stock_stop:.2f}  ->  option ~${sizing.option_stop:.2f}",
        f"  T1:     {underlying_symbol} {stock_target:.2f}  ->  option ~${sizing.option_target:.2f}",
        "",
    ]


def _legs_block(
    underlying_symbol: str,
    option_sym: str,
    contracts: int,
    sizing: OptionSizingResult,
    stock_stop: float,
    stock_target: float,
) -> list:
    """Three-leg Schwab grid: entry, underlying-triggered stop, target."""
    return [
        _DIV,
        "  LEG 1 -- Entry  (triggers exit legs on fill)",
        _DIV,
        "  Action:  BUY TO OPEN",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_sym}",
        "  Order:   LIMIT",
        f"  Price:   {sizing.option_entry:.2f}  (mid; adjust bid-aware)",
        "  TIF:     DAY",
        "",
        _DIV,
        "  LEG 2 -- Stop Loss  (UNDERLYING trigger -- P_000 Options Rule)",
        _DIV,
        f"  Trigger: {underlying_symbol} stock at or below {stock_stop:.2f}",
        "  Action:  SELL TO CLOSE",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_sym}",
        f"  Order:   STOP-LIMIT  (limit bid-aware ~${sizing.option_stop:.2f})",
        "  TIF:     GTC",
        "",
        _DIV,
        "  LEG 3 -- Take Profit  (underlying target reference)",
        _DIV,
        f"  Trigger: {underlying_symbol} stock at or above {stock_target:.2f}",
        "  Action:  SELL TO CLOSE",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_sym}",
        f"  Order:   LIMIT  (bid-aware ~${sizing.option_target:.2f})",
        "  TIF:     GTC",
        "",
        _SEP,
    ]


def build_option_spec(
    underlying_symbol: str,
    chain: OptionChainInput,
    sizing: OptionSizingResult,
    stock_entry: float,
    stock_stop: float,
    stock_target: float,
    is_paper: bool = False,
) -> str:
    """Render Pattern B single-leg option spec for Schwab entry.

    Returns a [NO SPEC] notice if sizing produced 0 contracts with no override.
    When override_required, renders 1 contract with a loud override note.

    Args:
        underlying_symbol: Ticker (e.g. "ADBE").
        chain: Validated OptionChainInput (single leg).
        sizing: OptionSizingResult from options_sizer.
        stock_entry: Live underlying entry price.
        stock_stop: Underlying stop price (Section 3.8 display + Leg 2 trigger).
        stock_target: Underlying T1 target price.
        is_paper: If True, prepends PAPER TRADE banner.

    Returns:
        Multi-line string spec.
    """
    if sizing.contracts == 0 and not sizing.override_required:
        return (
            f"[NO SPEC -- {underlying_symbol}] "
            "Option sizing produced 0 contracts. Override required."
        )

    contracts = max(sizing.contracts, 1) if sizing.override_required else sizing.contracts

    override_note = ""
    if sizing.override_required:
        override_note = (
            "[OVERRIDE: gate math = 0 contracts -- trading 1 contract. "
            "Document justification per override protocol.]\n\n"
        )

    paper_banner = ""
    if is_paper:
        paper_banner = "\n".join([
            _SEP,
            "*** PAPER TRADE -- NOT FOR SUBMISSION TO SCHWAB ***",
            _SEP, "",
        ])

    option_sym = _occ_symbol(
        underlying_symbol, chain.expiration, chain.option_type, chain.strike,
    )
    leverage = _leverage_multiple(chain.delta, stock_entry, sizing.option_entry)

    lines = []
    lines += _summary_block(underlying_symbol, option_sym, chain, sizing,
                            contracts, leverage)
    lines += _dual_price_block(underlying_symbol, sizing,
                               stock_entry, stock_stop, stock_target)
    lines += _legs_block(underlying_symbol, option_sym, contracts, sizing,
                         stock_stop, stock_target)

    body = "\n".join(lines)
    return override_note + paper_banner + body