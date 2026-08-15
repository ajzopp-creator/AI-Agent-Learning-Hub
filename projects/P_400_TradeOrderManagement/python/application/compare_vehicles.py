"""compare_vehicles.py -- Orchestrate stock vs option comparison for a signal.

Application layer: orchestration only -- no business logic, no direct I/O.
Loads packet, snapshot, chain; runs both sizing paths; runs options council
viability gates; calls vehicle_selector; returns formatted comparison table
string for CLI output.

Architecture v2.1 Section 7.3. Wired to options_council.py under
WO-P400-E3.004 (item 2) -- previously OI/spread/RR-parity/IV-rank gates
were built and unit-tested but never invoked on the live compare path.

NEITHER disposal (WO-P400-E5.006, 2026-08-11): when neither vehicle is
viable, the packet is archived and a REVIEWED_NO_TRADE record is written
immediately -- Tony's call: once a signal reaches P_400 it is either a
trade or it is not. P_400 does not hold a packet waiting to see if it
re-qualifies later; that is the trade-selector projects' job
(P_115/P_300/P_118), not Order Management's. Mirrors the existing
ENTRY_MISSED disposal pattern already used by cmd_evaluate()'s
--drop-reason path.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from config import TradeMode
from infrastructure.params_reader import read_params
from infrastructure.posture_reader import read_posture
from infrastructure.chain_loader import load_chain
from domain.sizing import three_gate_size
from domain.options_sizer import size_option_chart_based
from domain.options_council import run_options_council
from domain.vehicle_selector import compare_vehicles, VehicleComparison
from schemas import SnapshotDict
from shared_resources.python_utils.signal_schemas import SignalV2

logger = logging.getLogger("p400.compare_vehicles")

_SEP = "=" * 60
_DIV = "-" * 60


def run_comparison(
    packet: SignalV2,
    snapshot_path: str,
    chain_path: str,
    cash_available: float,
    trade_mode: TradeMode,
) -> str:
    """Run stock vs option comparison and return formatted table.

    Args:
        packet: Validated SignalV2 from inbox.
        snapshot_path: Path to snapshot_SYMBOL.json.
        chain_path: Path to chain_SYMBOL.json.
        cash_available: Per-trade buying power from Tony.
        trade_mode: REAL or PAPER -- used only by the NEITHER disposal
            path; sizing itself is mode-agnostic.

    Returns:
        Multi-line comparison table string. If the recommendation is
        NEITHER, a REVIEWED_NO_TRADE disposal line is appended.
    """
    snapshot_raw = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    snap = SnapshotDict(**snapshot_raw)
    chain = load_chain(chain_path)
    posture = read_posture()
    params = read_params()

    stock_sizing = three_gate_size(
        entry=snap.price,
        stop=packet.guideline_stop,
        target=packet.guideline_target,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash_available,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
        half_spread=round((snap.ask - snap.bid) / 2, 4),
    )

    option_sizing = size_option_chart_based(
        chain=chain,
        stock_entry=snap.price,
        stock_stop=packet.guideline_stop,
        stock_target=packet.guideline_target,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash_available,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
    )

    options_council_result = run_options_council(
        chain=chain,
        sizing=option_sizing,
        stock_rr=stock_sizing.rr_at_t1,
    )

    comparison = compare_vehicles(packet.symbol, stock_sizing, option_sizing,
                                   options_council_result)
    table = _format_comparison(comparison, snap, chain, posture.risk_mode)
    return table + _dispose_if_neither(packet, comparison, trade_mode)


def _dispose_if_neither(
    packet: SignalV2,
    comparison: VehicleComparison,
    trade_mode: TradeMode,
) -> str:
    """Archive + write REVIEWED_NO_TRADE when neither vehicle is viable.

    No-op (returns "") for every other recommendation -- STOCK/OPTION/
    SPREAD/OPTION_OVERRIDE_ONLY still proceed to evaluate per the SIP,
    unchanged.
    """
    if comparison.recommended != "NEITHER":
        return ""
    from application.drop_signal import drop_signal
    ok = drop_signal(packet, "RR_INVALID", trade_mode)
    logger.info("compare NEITHER -> drop_signal ok=%s", ok)
    return (
        f"\nREVIEWED_NO_TRADE: {packet.symbol}  drop_reason=RR_INVALID  "
        f"(archived={'OK' if ok else 'FAILED'}, record written)"
    )


def _format_comparison(
    c: VehicleComparison,
    snap: SnapshotDict,
    chain,
    risk_mode: str,
) -> str:
    """Format VehicleComparison as a readable side-by-side table."""

    def _viable(flag: bool) -> str:
        return "YES" if flag else "NO"

    def _size_cell(c: VehicleComparison) -> str:
        if c.option_contracts > 0:
            return f"{c.option_contracts}ct"
        if c.option_override_available:
            return "0ct (OVERRIDE AVAIL)"
        return "0ct"

    lines = [
        _SEP,
        f"VEHICLE COMPARISON: {c.symbol}  |  posture={risk_mode}",
        _SEP,
        "",
        f"  {'':20} {'STOCK':>15} {'OPTION':>15}",
        _DIV,
        f"  {'R:R at T1':20} {c.stock_rr:>15.2f} {c.option_rr:>15.2f}",
        f"  {'Viable':20} {_viable(c.stock_viable):>15} {_viable(c.option_viable):>15}",
        f"  {'Size':20} {str(c.stock_shares)+' shares':>15} {_size_cell(c):>22}",
        f"  {'Dollar risk':20} {'$'+str(round(c.stock_dollar_risk,2)):>15} "
        f"{'$'+str(round(c.option_dollar_risk,2)):>15}",
        f"  {'Method':20} {'three-gate':>15} {c.option_method:>15}",
        "",
        f"  Stock underlying:  {snap.price:.2f}  |  "
        f"Option: {chain.option_type} {chain.strike:.0f} exp={chain.expiration}",
        f"  Option mid: ${chain.mid:.2f}  delta={chain.delta:.2f}  "
        f"IV={chain.iv*100:.1f}%  OI={chain.open_interest}",
        "",
        _DIV,
        f"  Options Council: {c.option_council_verdict}",
    ]
    for b in c.option_council_blocks:
        lines.append(f"    BLOCK: {b}")
    for cn in c.option_council_cautions:
        lines.append(f"    CAUTION: {cn}")
    lines.append(_DIV)

    rec_prefix = "OVERRIDE REQUIRED -- " if c.recommended == "OPTION_OVERRIDE_ONLY" else ""
    lines.append(f"  RECOMMENDATION: {rec_prefix}{c.recommended}")
    lines.append(f"  Reason: {c.recommendation_reason}")
    lines.append(_SEP)

    if c.spread_recommended:
        lines.append("  ** IV > 50 -- if choosing options, use SPREAD (--spread flag)")
        lines.append(_SEP)

    return "\n".join(lines)