"""batch_2b_scoring.py -- Per-symbol pipeline, vehicle comparison, and
ranking assembly for the Tier-2B batch runner.

Application layer: orchestration only. Split out of batch_2b.py (same WO)
to stay under the 300-line file cap -- docstrings ran the combined file to
442 lines, same overage pattern already noted in the WO build log for
every file shipped 2026-08-05.

Public interface for batch_2b.py: evaluate_pass_symbols(), assemble_report().
Everything else here is module-private.

WO-P400-E5.003.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

from pydantic import ValidationError

from config import PORTFOLIO_HEAT_MAX_PCT, TradeMode
from application.batch_2b_disposition import dispose_evaluation
from application.evaluate_signal import evaluate_signal
from application.fetch_chain import cmd_fetch_chain
from application.fetch_snapshot import cmd_fetch_snapshot
from domain.options_council import run_options_council
from domain.options_sizer import size_option_chart_based
from domain.ranking import order_by_score, score_candidate
from domain.vehicle_selector import compare_vehicles
from infrastructure.chain_loader import load_chain
from schemas import BatchReport, RankedCandidate

EASTERN = ZoneInfo("America/New_York")
PYTHON_DIR = Path(__file__).resolve().parents[1]  # snapshot_/chain_ artifacts live here


# ---------------------------------------------------------------------------
# Small pure/lookup helpers
# ---------------------------------------------------------------------------

def _find_packet(symbol: str, packets):
    matches = [p for p in packets if p.symbol.upper() == symbol.upper()]
    return matches[0] if matches else None


def _atr_headroom(effective_entry: float, effective_stop: float, atr_14: float) -> float:
    if not atr_14:
        return 0.0
    return round((effective_entry - effective_stop) / atr_14, 4)


def _spread_pct_of_price(snapshot: dict) -> float:
    """Same formula as evaluate_signal.py's spread-plausibility gate --
    half-spread as a percent of price."""
    bid, ask, price = snapshot.get("bid", 0.0), snapshot.get("ask", 0.0), snapshot.get("price", 0.0)
    if not price:
        return 0.0
    half_spread = (ask - bid) / 2.0 if (bid and ask) else 0.0
    return round(half_spread / price * 100, 4)


# ---------------------------------------------------------------------------
# Per-symbol pipeline
# ---------------------------------------------------------------------------

def _fetch_snapshot_dict(symbol: str, entry) -> Optional[dict]:
    """Call cmd_fetch_snapshot as-is (WO investigation note: it writes the
    same artifact a manual run produces, so the batch stays auditable and a
    follow-up `spec SYMBOL --snapshot ...` still works). It returns an int,
    not the SnapshotDict, so the written file is the only handle to the
    data -- read it back. Returns None if the fetch failed (cmd_fetch_snapshot
    already printed why)."""
    rc = cmd_fetch_snapshot(
        symbol,
        earnings_date=entry.next_earnings_date,
        sector=entry.sector,
        last_earnings_date=entry.last_earnings_date,
    )
    if rc != 0:
        return None
    safe_symbol = symbol.replace("/", "_")
    snap_path = PYTHON_DIR / f"snapshot_{safe_symbol}.json"
    return json.loads(snap_path.read_text(encoding="utf-8"))


def _vehicle_comparison(packet, eval_result, cash: float, params, posture) -> Tuple[str, float, int, float, str]:
    """Options-first vehicle selection (Scope 2). Calls
    domain.vehicle_selector.compare_vehicles() directly -- not
    application.compare_vehicles.run_comparison() -- reusing
    eval_result.sizing (already computed against the drift-resolved
    effective_entry/effective_stop) rather than a second three_gate_size()
    call against the raw packet stop the way run_comparison() does.

    Falls back to stock-only if the chain fetch itself fails (Schwab error,
    or no contract in the DTE window): a data hiccup on the options side
    must not cost an otherwise-APPROVED stock trade its ranked row.

    Returns:
        (vehicle, rr_at_t1, quantity, dollar_risk, reason) -- reason (added
        WO-P400-E6.006) is always populated, not just on the STOCK-fallback
        path, so the batch report never silently omits why a vehicle won.
    """
    symbol = packet.symbol
    if cmd_fetch_chain(symbol, "call") != 0:
        return ("STOCK", eval_result.rr_after_drift,
                eval_result.sizing.shares, eval_result.sizing.dollar_risk,
                "options chain fetch failed (Schwab error or no contract in "
                "DTE window) -- stock used")

    chain_path = PYTHON_DIR / f"chain_{symbol}.json"
    chain = load_chain(str(chain_path))
    option_sizing = size_option_chart_based(
        chain=chain,
        stock_entry=eval_result.effective_entry,
        stock_stop=eval_result.effective_stop,
        stock_target=packet.guideline_target,
        base_risk_dollars=params.risk_per_trade,
        cash_available=cash,
        max_position_dollars=params.max_position,
        risk_mode=posture.risk_mode,
    )
    council_result = run_options_council(
        chain=chain, sizing=option_sizing, stock_rr=eval_result.rr_after_drift,
    )
    comparison = compare_vehicles(symbol, eval_result.sizing, option_sizing, council_result)

    if comparison.recommended in ("OPTION", "SPREAD"):
        return (comparison.recommended, comparison.option_rr,
                comparison.option_contracts, comparison.option_dollar_risk,
                comparison.recommendation_reason)
    if comparison.recommended == "STOCK":
        return ("STOCK", comparison.stock_rr, comparison.stock_shares,
                comparison.stock_dollar_risk, comparison.recommendation_reason)
    # OPTION_OVERRIDE_ONLY / NEITHER -- no real quantity without an explicit override
    return (comparison.recommended, comparison.stock_rr, 0, 0.0, comparison.recommendation_reason)


def _build_candidate(packet, eval_result, snapshot: dict, vehicle: str,
                      rr_at_t1: float, quantity: int, dollar_risk: float,
                      vehicle_reason: str) -> dict:
    atr_headroom = _atr_headroom(
        eval_result.effective_entry, eval_result.effective_stop, snapshot.get("atr_14", 0.0),
    )
    spread_pct = _spread_pct_of_price(snapshot)
    score, components = score_candidate(
        rr_at_t1=rr_at_t1,
        atr_headroom=atr_headroom,
        spread_pct_of_price=spread_pct,
        avg_volume_20d=snapshot.get("avg_volume_20d", 0.0),
        drift_pct=eval_result.drift_pct,
    )
    return {
        "symbol": packet.symbol,
        "score": score,
        "score_components": components,
        "vehicle": vehicle,
        "vehicle_reason": vehicle_reason,
        "verdict": eval_result.verdict,
        "rr_at_t1": rr_at_t1,
        "atr_headroom": atr_headroom,
        "spread_pct_of_price": spread_pct,
        "drift_pct": eval_result.drift_pct,
        "dollar_risk": round(dollar_risk, 2),
        "quantity": quantity,
    }


def _process_symbol(packet, entries, cash: float, trade_mode: TradeMode,
                     params, posture, skipped: List[Dict[str, str]]) -> Optional[dict]:
    """Full per-symbol pipeline. Returns a scored candidate dict, or None
    (with a named entry appended to `skipped`) at any stage the symbol
    cannot proceed. Never a silent skip -- every non-candidate outcome is
    named in the report."""
    symbol = packet.symbol

    if packet.asset_class != "stock":
        skipped.append({"symbol": symbol,
                         "reason": f"asset_class={packet.asset_class} -- batch-2b vehicle "
                                   "selection only covers stock-based signals"})
        return None

    earnings_entry = entries.get(symbol.upper())
    if earnings_entry is None:
        skipped.append({"symbol": symbol,
                         "reason": f"no earnings calendar entry for {symbol} -- "
                                   "skipped, not batch-fatal (WO-P400-E6.004)"})
        return None

    snapshot = _fetch_snapshot_dict(symbol, earnings_entry)
    if snapshot is None:
        skipped.append({"symbol": symbol, "reason": "fetch-snapshot failed -- see console output above"})
        return None

    eval_result = evaluate_signal(packet, snapshot, cash_available=cash, trade_mode=trade_mode)
    dispose_evaluation(packet, eval_result, snapshot, trade_mode)
    if not eval_result.is_approved():
        skipped.append({"symbol": symbol,
                         "reason": f"verdict={eval_result.verdict} "
                                   f"({eval_result.first_block() or 'not approved'})"})
        return None

    vehicle, rr_at_t1, quantity, dollar_risk, vehicle_reason = _vehicle_comparison(
        packet, eval_result, cash, params, posture,
    )
    return _build_candidate(packet, eval_result, snapshot, vehicle, rr_at_t1,
                             quantity, dollar_risk, vehicle_reason)


def evaluate_pass_symbols(pass_symbols, packets, entries, cash, trade_mode,
                           params, posture) -> Tuple[List[dict], List[Dict[str, str]]]:
    """Public: called by batch_2b.run_batch_2b() after Tier-1 screening."""
    skipped: List[Dict[str, str]] = []
    scored: List[dict] = []
    for symbol in pass_symbols:
        packet = _find_packet(symbol, packets)
        if packet is None:
            skipped.append({"symbol": symbol, "reason": "packet not found post-screen (unexpected)"})
            continue
        candidate = _process_symbol(packet, entries, cash, trade_mode, params, posture, skipped)
        if candidate is not None:
            scored.append(candidate)
    return scored, skipped


# ---------------------------------------------------------------------------
# Ranking + report assembly
# ---------------------------------------------------------------------------

def _rank_candidates(scored: List[dict]) -> Tuple[List[RankedCandidate], List[Dict[str, str]]]:
    """Order and validate. A RankedCandidate ValidationError (e.g.
    atr_headroom landing just under 1.0 inside QUANT's STOP_ATR_TOLERANCE
    band -- a real, approved edge case, not a wiring bug) demotes that one
    symbol to skipped rather than crashing the whole batch."""
    ordered = order_by_score(scored)
    candidates: List[RankedCandidate] = []
    extra_skips: List[Dict[str, str]] = []
    for c in ordered:
        try:
            candidates.append(RankedCandidate(**c))
        except ValidationError as exc:
            extra_skips.append({"symbol": c["symbol"], "reason": f"ranking validation failed: {exc}"})
    return candidates, extra_skips


def assemble_report(cash, session_date, posture, screened_count, passed_tier1,
                     scored, skipped, params) -> BatchReport:
    """Public: called by batch_2b.run_batch_2b() to produce the final report."""
    candidates, extra_skips = _rank_candidates(scored)
    skipped = skipped + extra_skips

    heat_cap = params.account_balance * (PORTFOLIO_HEAT_MAX_PCT / 100.0)
    cumulative_risk = round(sum(c.dollar_risk for c in candidates), 2)
    heat_warning = None
    if len(candidates) >= 2:
        heat_warning = (
            f"{len(candidates)} APPROVED candidates -- cumulative risk if all taken "
            f"${cumulative_risk:.2f} vs heat cap ${heat_cap:.2f} "
            f"({'OVER' if cumulative_risk > heat_cap else 'within'} cap). "
            "Not enforced -- each evaluate sizes independently (SIP v2.4, RISK never blocks)."
        )

    return BatchReport(
        run_timestamp=datetime.now(timezone.utc).astimezone(EASTERN).isoformat(),
        session_date=session_date,
        cash_available=cash,
        posture=posture.risk_mode,
        screened_count=screened_count,
        passed_tier1=passed_tier1,
        evaluated=len(candidates) + len(skipped),
        candidates=candidates,
        skipped=skipped,
        cumulative_risk_if_all_taken=cumulative_risk,
        heat_cap=heat_cap,
        heat_warning=heat_warning,
    )
