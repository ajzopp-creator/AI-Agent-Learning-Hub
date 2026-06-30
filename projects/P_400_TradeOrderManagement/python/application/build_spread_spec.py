"""build_spread_spec.py -- Pattern C: vertical debit spread Schwab grid renderer.

Application layer: orchestration only -- no business logic, no direct I/O.
Receives a SpreadSizingResult and chain data; returns plain text spec.

Architecture v2.1 Section 7.3 (WO-P400-E3.002), Section 6.3 Pattern C.
"""

from __future__ import annotations

import logging
from datetime import datetime

from domain.spread_sizer import SpreadSizingResult
from schemas import OptionChainInput

logger = logging.getLogger("p400.build_spread_spec")

_SEP = "=" * 60
_DIV = "-" * 60


def _occ_symbol(symbol: str, expiry: str, option_type: str, strike: float) -> str:
    """Build OCC option symbol."""
    dt = datetime.strptime(expiry, "%Y-%m-%d")
    yymmdd = dt.strftime("%y%m%d")
    cp = "C" if option_type.lower() == "call" else "P"
    strike_int = int(round(strike * 1000))
    return f"{symbol:<6}{yymmdd}{cp}{strike_int:08d}"


def build_spread_spec(
    underlying_symbol: str,
    long_chain: OptionChainInput,
    short_chain: OptionChainInput,
    sizing: SpreadSizingResult,
    is_paper: bool = False,
) -> str:
    """Render Pattern C vertical debit spread spec for Schwab entry.

    Returns a blocked notice if sizing produced 0 contracts and no override.
    Returns the full Schwab grid otherwise.

    Args:
        underlying_symbol: Ticker (e.g. "MU").
        long_chain: Long leg OptionChainInput (ATM).
        short_chain: Short leg OptionChainInput (OTM).
        sizing: SpreadSizingResult from size_vertical_debit_spread().
        is_paper: If True, prepends PAPER TRADE banner.

    Returns:
        Multi-line string spec.
    """
    if sizing.contracts == 0 and not sizing.override_required:
        return (
            f"[NO SPEC -- {underlying_symbol}] "
            "Spread sizing produced 0 contracts. Override required."
        )

    if sizing.warning and "mismatch" in sizing.warning:
        return f"[INVALID SPREAD -- {underlying_symbol}] {sizing.warning}"

    long_sym = _occ_symbol(
        underlying_symbol, long_chain.expiration,
        long_chain.option_type, long_chain.strike,
    )
    short_sym = _occ_symbol(
        underlying_symbol, short_chain.expiration,
        short_chain.option_type, short_chain.strike,
    )

    contracts = max(sizing.contracts, 1) if sizing.override_required else sizing.contracts
    override_note = ""
    if sizing.override_required:
        override_note = (
            "[OVERRIDE: gate math = 0 contracts -- trading 1 spread. "
            "Document justification per override protocol.]\n\n"
        )

    paper_banner = ""
    if is_paper:
        paper_banner = "\n".join([
            _SEP,
            "*** PAPER TRADE -- NOT FOR SUBMISSION TO SCHWAB ***",
            _SEP, "",
        ])

    lines = [
        _SEP,
        "PATTERN C -- Vertical Debit Spread  (Net Debit Order)",
        _SEP,
        "",
        f"  Underlying:      {underlying_symbol}",
        f"  Structure:       {long_chain.option_type.upper()} DEBIT SPREAD",
        f"  Expiration:      {long_chain.expiration}",
        f"  Contracts:       {contracts}",
        "",
        f"  Debit paid:      ${sizing.debit_per_spread:.2f} per spread",
        f"  Max profit:      ${sizing.max_profit_per_spread:.2f} per spread  "
        f"(${sizing.max_profit_per_spread * contracts:.2f} total)",
        f"  Max loss:        ${sizing.max_loss_per_spread:.2f} per spread  "
        f"(${sizing.total_max_loss:.2f} total)",
        f"  Breakeven:       {sizing.breakeven:.2f}",
        f"  R:R:             {sizing.rr_spread:.2f}",
        f"  Risk budget:     ${sizing.adjusted_risk_budget:.2f}",
        "",
        _DIV,
        "  LONG LEG  (buy to open)",
        _DIV,
        f"  Action:  BUY TO OPEN",
        f"  Qty:     {contracts}",
        f"  Symbol:  {long_sym}",
        f"  Strike:  {long_chain.strike:.2f}  ({long_chain.option_type.upper()})",
        f"  Order:   LIMIT",
        f"  Price:   {long_chain.mid:.2f}  (mid; adjust to bid-aware fill)",
        f"  TIF:     DAY",
        "",
        _DIV,
        "  SHORT LEG  (sell to open -- same order as net debit)",
        _DIV,
        f"  Action:  SELL TO OPEN",
        f"  Qty:     {contracts}",
        f"  Symbol:  {short_sym}",
        f"  Strike:  {short_chain.strike:.2f}  ({short_chain.option_type.upper()})",
        f"  Order:   LIMIT",
        f"  Price:   {short_chain.mid:.2f}  (mid)",
        f"  TIF:     DAY",
        "",
        _DIV,
        "  NET DEBIT ORDER  (submit as single spread order in Schwab)",
        _DIV,
        f"  Net debit limit: {sizing.debit_per_spread:.2f}",
        f"  Qty:             {contracts}",
        f"  TIF:             DAY",
        "",
        "  EXIT MANAGEMENT:",
        "  - Stop: close spread if underlying hits stock stop level",
        "  - Target: close at 50-80% of max profit OR underlying hits T1",
        "  - Max loss is defined -- no stop-limit order required on short leg",
        "",
        _SEP,
    ]

    body = "\n".join(lines)
    return override_note + paper_banner + body