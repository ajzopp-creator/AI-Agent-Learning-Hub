"""commands.py -- P_400 CLI command implementations.

Application layer: orchestration only. Split out of cli.py (WO-P400-E2.015
follow-on) once cli.py crossed the 300-line cap -- cli.py is now argparse
wiring + main() dispatch only; this module holds the actual command bodies.
"""

from __future__ import annotations

import json
import logging

from config import (
    LOGGER_NAME,
    MAX_CONCURRENT_POSITIONS,
    PORTFOLIO_HEAT_MAX_PCT,
    SIGNALS_DIR,
    TradeMode,
)
from application.read_signals import read_signals


def _find_packet(symbol: str):
    result = read_signals()
    matches = [s for s in result.load.valid if s.symbol.upper() == symbol.upper()]
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# screen-all
# ---------------------------------------------------------------------------

def cmd_screen_all() -> int:
    from domain.screen import screen_all
    from infrastructure.book_loader import load_book
    from infrastructure.params_reader import read_params
    from infrastructure.posture_reader import read_posture
    from domain.portfolio import build_portfolio_state

    result = read_signals()
    posture = read_posture()
    params = read_params()
    port = build_portfolio_state(load_book())

    signals = [
        {"symbol": s.symbol, "signal_file": s.signal_id,
         "entry": s.guideline_entry, "stop": s.guideline_stop,
         "target": s.guideline_target, "signal_date_str": s.signal_timestamp}
        for s in result.load.valid
    ]
    context = {
        "risk_mode": posture.risk_mode,
        "base_risk_dollars": params.risk_per_trade,
        "current_heat_dollars": port.heat_dollars,
        "heat_cap_dollars": params.account_balance * (PORTFOLIO_HEAT_MAX_PCT / 100.0),
        "open_position_count": port.open_position_count,
        "max_positions": MAX_CONCURRENT_POSITIONS,
        "open_symbols": list(port.open_symbols),
    }
    results = screen_all(signals, context)
    print("=" * 70)
    print(f"TIER-1 SCREEN  |  posture={posture.risk_mode}  |  {len(signals)} packets")
    print("=" * 70)
    for r in results:
        print(" ", r.summary_line())
    print("=" * 70)
    return 0


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------

def cmd_evaluate(symbol: str, snapshot_path: str, cash: float, trade_mode: TradeMode,
                 target_override: float = None, pre_market: bool = False,
                 qty_override: int = None, drop_reason: str = None,
                 options: bool = False, chain_path: str = None,
                 spread: bool = False, chain_short_path: str = None) -> int:
    from application.evaluate_signal import evaluate_signal

    packet = _find_packet(symbol)
    if packet is None:
        print(f"[ERROR] No valid v2 packet found for {symbol} in {SIGNALS_DIR}")
        return 1

    if drop_reason is not None:
        from application.drop_signal import drop_signal
        ok = drop_signal(packet, drop_reason, trade_mode)
        print(f"REVIEWED_NO_TRADE: {symbol}  drop_reason={drop_reason}  "
              f"(archived={'OK' if ok else 'FAILED'}, record written)")
        return 0 if ok else 1

    if target_override is not None:
        packet = packet.model_copy(update={"guideline_target": target_override})
        print(f"[INFO] Target overridden to {target_override:.2f}")

    snapshot = json.loads(open(snapshot_path, encoding="utf-8").read())
    if pre_market:
        snapshot["market_open"] = True
        print("[INFO] --pre-market: market_open forced True")

    result = evaluate_signal(packet, snapshot, cash_available=cash,
                             trade_mode=trade_mode, qty_override=qty_override)
    print("=" * 60)
    print(f"EVALUATION: {result.symbol}  |  verdict={result.verdict}")
    print(f"  Mode:      {result.trade_mode.value}")
    print(f"  Posture:   {result.posture.risk_mode}")
    print(f"  Drift:     {result.drift_pct:+.2f}%")
    print(f"  R:R live:  {result.rr_after_drift:.2f}")
    if result.sizing:
        print(f"  Shares:    {result.sizing.shares}  (gate={result.sizing.winning_gate})")
        print(f"  $ risk:    ${result.sizing.dollar_risk:.2f}")
    print(result.council.summary())
    print("=" * 60)

    if spread:
        if not chain_path or not chain_short_path:
            print("[ERROR] --spread requires --chain (long leg) and --chain-short (short leg)")
            return 1
        from application.evaluate_spread import evaluate_spread
        spread_result = evaluate_spread(
            packet=packet, long_chain_path=chain_path,
            short_chain_path=chain_short_path, cash_available=cash,
        )
        print("=" * 60)
        print(f"SPREAD SIZING: {spread_result.symbol}  |  contracts={spread_result.sizing.contracts}"
              f"  rr={spread_result.sizing.rr_spread:.2f}  gate={spread_result.sizing.winning_gate}")
        if spread_result.sizing.warning:
            print(f"  WARNING: {spread_result.sizing.warning}")
        print("=" * 60)
        print(spread_result.spec_text)

        from infrastructure.record_writer import write_spread_eval_record
        written, sp_verdict = write_spread_eval_record(spread_result, result, packet, trade_mode.value)
        print(f"P400 record written: {spread_result.symbol}  verdict={sp_verdict}  "
              f"(vault_write={'OK' if written else 'FAILED'})")
    elif options:
        if not chain_path:
            print("[ERROR] --options requires --chain chain_SYMBOL.json")
            return 1
        from application.evaluate_options import evaluate_options
        opt_result = evaluate_options(
            packet=packet, snapshot_raw=snapshot, chain_path=chain_path,
            cash_available=cash, stock_rr=result.rr_after_drift,
        )
        print("=" * 60)
        print(f"OPTIONS COUNCIL: {opt_result.symbol}  |  verdict={opt_result.verdict}")
        for b in opt_result.council.blocks:
            print(f"  BLOCK: {b}")
        for c in opt_result.council.cautions:
            print(f"  CAUTION: {c}")
        print("=" * 60)
        if opt_result.spec_text:
            print(opt_result.spec_text)
        else:
            print(f"[NO SPEC -- {symbol}] Options council BLOCKED. No order spec generated.")

        from infrastructure.record_writer import write_options_eval_record
        written, opt_verdict = write_options_eval_record(opt_result, result, packet, trade_mode.value, symbol)
        print(f"P400 record written: {opt_result.symbol}  verdict={opt_verdict}  "
              f"(vault_write={'OK' if written else 'FAILED'})")

    if result.verdict == "BLOCKED":
        from infrastructure.record_writer import write_p400_record
        written = write_p400_record(
            symbol=result.symbol,
            verdict="BLOCKED",
            risk_mode=result.posture.risk_mode,
            entry_price=result.effective_entry,
            stop_price=result.effective_stop,
            target_1=packet.guideline_target,
            position_size=0,
            signal_source=packet.signal_source,
            trade_mode_value=trade_mode.value,
            signal_date=packet.signal_metadata.session_date,
        )
        print(f"BLOCKED record written: {result.symbol}  (vault_write={'OK' if written else 'FAILED'})")

    # Archive after the full pipeline completes (WO-P400-E2.015) -- was
    # previously called mid-evaluate_signal(), decoupled from whether any
    # downstream record write (BLOCKED/options/spread) actually finished.
    from infrastructure.signal_archiver import archive_packet
    archive_packet(packet.symbol, packet.signal_metadata.session_date)

    return 0


# ---------------------------------------------------------------------------
# spec
# ---------------------------------------------------------------------------

def cmd_spec(symbol: str, snapshot_path: str, cash: float, trade_mode: TradeMode,
             target_override: float = None, pre_market: bool = False,
             qty_override: int = None) -> int:
    from application.evaluate_signal import evaluate_signal
    from application.build_order_spec import build_spec

    packet = _find_packet(symbol)
    if packet is None:
        print(f"[ERROR] No valid v2 packet found for {symbol} in {SIGNALS_DIR}")
        return 1

    if target_override is not None:
        packet = packet.model_copy(update={"guideline_target": target_override})

    snapshot = json.loads(open(snapshot_path, encoding="utf-8").read())
    if pre_market:
        snapshot["market_open"] = True

    result = evaluate_signal(packet, snapshot, cash_available=cash,
                             trade_mode=trade_mode, qty_override=qty_override)
    print(build_spec(result, packet, snapshot))

    # Archive after spec is rendered (WO-P400-E2.015)
    from infrastructure.signal_archiver import archive_packet
    archive_packet(packet.symbol, packet.signal_metadata.session_date)

    return 0


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

def cmd_compare(symbol: str, snapshot_path: str, chain_path: str,
                cash: float) -> int:
    from application.compare_vehicles import run_comparison

    packet = _find_packet(symbol)
    if packet is None:
        print(f"[ERROR] No valid v2 packet found for {symbol} in {SIGNALS_DIR}")
        return 1

    print(run_comparison(packet, snapshot_path, chain_path, cash))
    return 0


# ---------------------------------------------------------------------------
# reader summary (E1)
# ---------------------------------------------------------------------------

def cmd_reader() -> int:
    logger = logging.getLogger(LOGGER_NAME)
    logger.info("Reading signals from: %s", SIGNALS_DIR)
    result = read_signals()
    print("=" * 60)
    print("P_400 SIGNAL READER -- summary")
    print("=" * 60)
    print(f"  Valid v2 packets:   {result.valid_count}")
    print(f"  Rejected packets:   {result.rejected_count}")
    print(f"  Legacy (tolerated): {result.legacy_count}")
    if result.load.rejected:
        print("-" * 60)
        print("  REJECTED:")
        for rej in result.load.rejected:
            print(f"    - {rej.path}\n        {rej.reason}")
    print("=" * 60)
    for sig in result.load.valid:
        print(f"  {sig.symbol:<6} {sig.asset_class:<6} "
              f"entry={sig.guideline_entry:.2f} stop={sig.guideline_stop:.2f} "
              f"src={sig.signal_source}")
    return 0