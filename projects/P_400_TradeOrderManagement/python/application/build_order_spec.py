"""P_400 application: Schwab-grid order spec renderer.

Renders Pattern A (stock OCO bracket), Pattern B (single-leg option 1st-trgs-All),
or Pattern C stub (vertical spread -- requires full chain data, Phase 2).

Returns plain text Tony can type directly into Schwab.
Returns empty string with a message if the verdict is BLOCKED.

PAPER trades: identical spec output with [PAPER TRADE] banner prepended.
Record routing (PAPER_BOOK_DIR vs BOOK_DIR) is handled by record_writer, not here.

Architecture v2.0 Section 6.3, 3.10.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from application.evaluate_signal import EvaluationResult
from config import TradeMode
from schemas import SignalV2, SnapshotDict

logger = logging.getLogger("p400.build_order_spec")

_SEP = "=" * 60
_DIV = "-" * 60


def _stop_limit_price(stop: float, tick: float = 0.05) -> float:
    """Limit price for a stop-limit order: stop minus one tick."""
    return round(stop - tick, 2)


def _occ_symbol(symbol: str, expiry: str, option_type: str, strike: float) -> str:
    """Build OCC option symbol (underlying 6-char + YYMMDD + C/P + 8-digit strike)."""
    dt = datetime.strptime(expiry, "%Y-%m-%d")
    yymmdd = dt.strftime("%y%m%d")
    cp = "C" if option_type.lower() == "call" else "P"
    strike_int = int(round(strike * 1000))
    return f"{symbol:<6}{yymmdd}{cp}{strike_int:08d}"


def _paper_banner() -> str:
    return "\n".join([
        _SEP,
        "*** PAPER TRADE -- NOT FOR SUBMISSION TO SCHWAB ***",
        _SEP,
        "",
    ])


def _pattern_a(
    symbol: str,
    shares: int,
    entry: float,
    stop: float,
    target: float,
    dollar_risk: float,
    rr: float,
) -> str:
    """Pattern A: stock OCO bracket (1st-Triggers-OCO)."""
    lines = [
        _SEP,
        "PATTERN A -- Stock OCO Bracket  (1st-Triggers-OCO)",
        _SEP,
        "",
        f"  Symbol:      {symbol}",
        f"  Shares:      {shares}",
        f"  Dollar risk: ${dollar_risk:.2f}",
        f"  R:R at T1:   {rr:.2f}",
        "",
        _DIV,
        "  LEG 1 -- Entry  (triggers OCO on fill)",
        _DIV,
        f"  Action:  BUY",
        f"  Qty:     {shares}",
        f"  Symbol:  {symbol}",
        f"  Order:   LIMIT",
        f"  Price:   {entry:.2f}",
        f"  TIF:     DAY",
        "",
        _DIV,
        "  LEG 2 -- Take Profit (T1)",
        _DIV,
        f"  Action:  SELL",
        f"  Qty:     {shares}",
        f"  Symbol:  {symbol}",
        f"  Order:   LIMIT",
        f"  Price:   {target:.2f}",
        f"  TIF:     GTC",
        "",
        _DIV,
        "  LEG 3 -- Stop Loss  (cancels Leg 2 if triggered)",
        _DIV,
        f"  Action:  SELL",
        f"  Qty:     {shares}",
        f"  Symbol:  {symbol}",
        f"  Order:   STOP-LIMIT",
        f"  Stop:    {stop:.2f}",
        f"  Limit:   {_stop_limit_price(stop):.2f}",
        f"  TIF:     GTC",
        "",
        _SEP,
    ]
    return "\n".join(lines)


def _pattern_b(
    symbol: str,
    contracts: int,
    entry_premium: float,
    stop_underlying: float,
    target_underlying: float,
    option_symbol: str,
    dollar_risk: float,
    rr: float,
) -> str:
    """Pattern B: single-leg option 1st-Triggers-All."""
    lines = [
        _SEP,
        "PATTERN B -- Single-Leg Option  (1st-Triggers-All)",
        _SEP,
        "",
        f"  Underlying:  {symbol}",
        f"  Option:      {option_symbol}",
        f"  Contracts:   {contracts}",
        f"  Dollar risk: ${dollar_risk:.2f}",
        f"  R:R at T1:   {rr:.2f}",
        "",
        _DIV,
        "  LEG 1 -- Entry  (triggers exit legs on fill)",
        _DIV,
        f"  Action:  BUY TO OPEN",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_symbol}",
        f"  Order:   LIMIT",
        f"  Price:   {entry_premium:.2f}",
        f"  TIF:     DAY",
        "",
        _DIV,
        "  LEG 2 -- Stop Loss  (stock price trigger; see Options Rule)",
        _DIV,
        f"  Trigger: {symbol} MARK at or below {stop_underlying:.2f}",
        f"  Action:  SELL TO CLOSE",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_symbol}",
        f"  Order:   MARKET  (or LIMIT bid-aware if spread wide)",
        f"  TIF:     GTC",
        "",
        _DIV,
        "  LEG 3 -- Take Profit (underlying target reference)",
        _DIV,
        f"  Underlying target: {target_underlying:.2f}",
        f"  Action:  SELL TO CLOSE",
        f"  Qty:     {contracts}",
        f"  Symbol:  {option_symbol}",
        f"  Order:   LIMIT  (set at bid-aware premium at target)",
        f"  TIF:     GTC",
        "",
        _SEP,
    ]
    return "\n".join(lines)


def build_spec(
    result: EvaluationResult,
    packet: SignalV2,
    snapshot: dict,
) -> str:
    """Render Schwab-grid order spec from an approved evaluation result.

    Returns a BLOCKED notice (not an empty string) if the verdict is BLOCKED
    so the caller can always print the return value directly.

    PAPER trades receive an identical spec with a [PAPER TRADE] banner prepended.
    Record routing is handled by record_writer (PAPER_BOOK_DIR vs BOOK_DIR).

    Args:
        result: EvaluationResult from evaluate_signal().
        packet: The evaluated SignalV2 packet.
        snapshot: The same raw snapshot dict used in evaluate_signal().

    Returns:
        Multi-line string spec ready to display (PAPER banner if applicable).
    """
    if not result.is_approved():
        block = result.first_block() or "unknown"
        return (
            f"[BLOCKED -- {result.symbol}]\n"
            f"Verdict: {result.verdict}\n"
            f"First block: {block}\n"
            "No order spec generated."
        )

    snap = SnapshotDict(**snapshot)
    sizing = result.sizing
    if sizing is None or sizing.shares < 1:
        return f"[NO SPEC -- {result.symbol}] Sizing produced 0 shares."

    asset_class = getattr(packet.asset_class, "value", packet.asset_class)
    prefix = _paper_banner() if result.is_paper() else ""

    if asset_class == "stock":
        effective_stop = snap.guideline_stop_override or packet.guideline_stop
        body = _pattern_a(
            symbol=packet.symbol,
            shares=sizing.shares,
            entry=snap.price,
            stop=effective_stop,
            target=packet.guideline_target,
            dollar_risk=sizing.dollar_risk,
            rr=result.rr_after_drift,
        )
        return prefix + body

    if asset_class == "option":
        option_sym = _occ_symbol(
            symbol=packet.symbol,
            expiry=packet.expiration_date or "",
            option_type=packet.option_type or "call",
            strike=packet.strike_price or 0.0,
        )
        body = _pattern_b(
            symbol=packet.symbol,
            contracts=sizing.shares,
            entry_premium=snap.price,
            stop_underlying=packet.guideline_stop,
            target_underlying=packet.guideline_target,
            option_symbol=option_sym,
            dollar_risk=sizing.dollar_risk,
            rr=result.rr_after_drift,
        )
        return prefix + body

    return f"[NO SPEC -- {packet.symbol}] Unrecognised asset_class: {asset_class}"
