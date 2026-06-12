"""P_400 domain: Tier-1 deterministic inbox screen.

Fast pass over all inbox signals - no web calls, no live data.
Receives pre-loaded data; returns a ranked list of ScreenResult objects.

Architecture v2.0 Section 2.1 (Tier-1 screen) and Section 2.3 (C1.5).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from config import (
    MIN_ACCEPTABLE_RR,
    RISK_MODE_MULTIPLIERS,
    SIGNAL_AGE_MAX_TRADING_DAYS,
)
from domain.council_codes import (
    RC_ADVERSE_DRIFT,
    RC_ALL_CLEAR,
    RC_HEAT_BREACH,
    RC_POSITION_COUNT,
    RC_RR_BELOW_MIN,
)
from domain.sizing import posture_multiplier

logger = logging.getLogger("p400.screen")

SCREEN_PASS = "PASS"
SCREEN_FAIL = "FAIL"
SCREEN_WARN = "WARN"

RC_SIGNAL_STALE = "SIGNAL_STALE"
RC_DUPLICATE = "DUPLICATE_OPEN"
RC_ZERO_SHARES = "SIZING_ZERO_SHARES"


@dataclass
class ScreenResult:
    """Result for a single signal after Tier-1 screening."""
    symbol: str
    signal_file: str
    outcome: str                      # PASS | FAIL | WARN
    reason_codes: List[str] = field(default_factory=list)
    reason_details: List[str] = field(default_factory=list)
    packet_rr: float = 0.0
    posture_gate_shares: int = 0      # Gate-1 shares at current risk_mode

    def is_pass(self) -> bool:
        return self.outcome == SCREEN_PASS

    def summary_line(self) -> str:
        codes = ", ".join(self.reason_codes) if self.reason_codes else RC_ALL_CLEAR
        return (
            f"{self.outcome:4s} | {self.symbol:6s} | RR={self.packet_rr:.2f} "
            f"| G1_shares={self.posture_gate_shares} | {codes}"
        )


def _packet_rr(entry: float, stop: float, target: float) -> float:
    """Compute simple (not realistic-fill) R:R for fast screen."""
    if stop >= entry or entry <= 0:
        return 0.0
    risk = entry - stop
    reward = target - entry
    return round(reward / risk, 3) if risk > 0 else 0.0


def _signal_age_trading_days(signal_date_str: Optional[str]) -> Optional[int]:
    """Return approximate trading days since signal was emitted.

    Uses calendar days / 1.4 as a rough proxy (no holiday calendar).
    Returns None if date cannot be parsed.
    """
    if not signal_date_str:
        return None
    try:
        signal_dt = datetime.fromisoformat(signal_date_str.replace("Z", "+00:00"))
        if signal_dt.tzinfo is None:
            signal_dt = signal_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        cal_days = max(0, (now - signal_dt).days)
        return int(cal_days / 1.4)
    except (ValueError, TypeError):
        return None


def screen_signal(
    symbol: str,
    signal_file: str,
    entry: float,
    stop: float,
    target: float,
    signal_date_str: Optional[str],
    risk_mode: str,
    base_risk_dollars: float,
    current_heat_dollars: float,
    heat_cap_dollars: float,
    open_position_count: int,
    max_positions: int,
    open_symbols: List[str],
) -> ScreenResult:
    """Screen a single signal packet. All inputs are pre-loaded by caller.

    Args:
        symbol: Ticker symbol.
        signal_file: Source filename for traceability.
        entry/stop/target: Signal price levels.
        signal_date_str: ISO-8601 string from signal metadata.
        risk_mode: Current P_010 risk_mode (re-read fresh by caller).
        base_risk_dollars: From P_000 Account Parameters.
        current_heat_dollars: Sum of open position dollar risks.
        heat_cap_dollars: 12% of account balance.
        open_position_count: Current open position count.
        max_positions: Maximum concurrent positions.
        open_symbols: List of symbols currently in the open-position book.

    Returns:
        ScreenResult with PASS/FAIL outcome and reason codes.
    """
    result = ScreenResult(symbol=symbol, signal_file=signal_file, outcome=SCREEN_PASS)

    # --- R:R check ---
    rr = _packet_rr(entry, stop, target)
    result.packet_rr = rr
    if rr < MIN_ACCEPTABLE_RR:
        result.outcome = SCREEN_FAIL
        result.reason_codes.append(RC_RR_BELOW_MIN)
        result.reason_details.append(
            f"Packet R:R {rr:.2f} < {MIN_ACCEPTABLE_RR:.1f} minimum."
        )

    # --- Duplicate check ---
    if symbol.upper() in [s.upper() for s in open_symbols]:
        result.outcome = SCREEN_FAIL
        result.reason_codes.append(RC_DUPLICATE)
        result.reason_details.append(f"{symbol} already open in position book.")

    # --- Heat headroom ---
    mult = posture_multiplier(risk_mode)
    adj_risk = base_risk_dollars * mult
    risk_per_share = entry - stop if entry > stop else 1.0
    gate1_shares = int(adj_risk / risk_per_share)
    result.posture_gate_shares = gate1_shares
    projected_heat = current_heat_dollars + (gate1_shares * risk_per_share)
    if projected_heat > heat_cap_dollars:
        result.outcome = SCREEN_FAIL
        result.reason_codes.append(RC_HEAT_BREACH)
        result.reason_details.append(
            f"Projected heat ${projected_heat:.2f} > cap ${heat_cap_dollars:.2f}."
        )

    # --- Position count headroom ---
    if open_position_count >= max_positions:
        result.outcome = SCREEN_FAIL
        result.reason_codes.append(RC_POSITION_COUNT)
        result.reason_details.append(
            f"Positions {open_position_count} >= max {max_positions}."
        )

    # --- Posture gate: would sizing produce >= 1 share? ---
    if gate1_shares < 1:
        result.outcome = SCREEN_FAIL
        result.reason_codes.append(RC_ZERO_SHARES)
        result.reason_details.append(
            f"Gate-1 produces 0 shares at {risk_mode} risk_mode."
        )

    # --- Signal age ---
    age_days = _signal_age_trading_days(signal_date_str)
    if age_days is not None and age_days > SIGNAL_AGE_MAX_TRADING_DAYS:
        if result.outcome == SCREEN_PASS:
            result.outcome = SCREEN_WARN
        result.reason_codes.append(RC_SIGNAL_STALE)
        result.reason_details.append(
            f"Signal ~{age_days} trading days old (max {SIGNAL_AGE_MAX_TRADING_DAYS})."
        )

    return result


def screen_all(signals: List[dict], context: dict) -> List[ScreenResult]:
    """Screen a list of pre-loaded signal dicts against shared context.

    Args:
        signals: List of dicts, each with keys:
            symbol, signal_file, entry, stop, target, signal_date_str
        context: Shared portfolio/posture context:
            risk_mode, base_risk_dollars, current_heat_dollars,
            heat_cap_dollars, open_position_count, max_positions, open_symbols

    Returns:
        List of ScreenResult, PASS first then WARN then FAIL; within each group
        sorted by packet_rr descending.
    """
    results = []
    for sig in signals:
        r = screen_signal(
            symbol=sig.get("symbol", "UNKNOWN"),
            signal_file=sig.get("signal_file", ""),
            entry=sig.get("entry", 0.0),
            stop=sig.get("stop", 0.0),
            target=sig.get("target", 0.0),
            signal_date_str=sig.get("signal_date_str"),
            risk_mode=context.get("risk_mode", "STANDARD"),
            base_risk_dollars=context.get("base_risk_dollars", 490.04),
            current_heat_dollars=context.get("current_heat_dollars", 0.0),
            heat_cap_dollars=context.get("heat_cap_dollars", 3920.0),
            open_position_count=context.get("open_position_count", 0),
            max_positions=context.get("max_positions", 8),
            open_symbols=context.get("open_symbols", []),
        )
        results.append(r)

    order = {SCREEN_PASS: 0, SCREEN_WARN: 1, SCREEN_FAIL: 2}
    results.sort(key=lambda x: (order.get(x.outcome, 3), -x.packet_rr))
    return results
