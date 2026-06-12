"""P_400 CLI entry point.

Commands (run from python/ dir, p140 env):

    python cli.py                              -- reader summary (E1)
    python cli.py screen-all                   -- Tier-1 screen of whole inbox
    python cli.py evaluate SYMBOL --snapshot FILE --cash DOLLARS [--paper]
    python cli.py spec SYMBOL --snapshot FILE --cash DOLLARS [--paper]

Session-level paper mode (all evaluate/spec calls in this session are PAPER):

    python cli.py --paper-session screen-all
    python cli.py --paper-session evaluate SYMBOL --snapshot FILE --cash DOLLARS

Per-trade --paper flag overrides session default if both are set.
"""

import argparse
import json
import logging
import sys

from config import (
    LOGGER_NAME,
    MAX_CONCURRENT_POSITIONS,
    PORTFOLIO_HEAT_MAX_PCT,
    SIGNALS_DIR,
    TradeMode,
    DEFAULT_TRADE_MODE,
)
from application.read_signals import read_signals


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _resolve_mode(session_paper: bool, trade_paper: bool) -> TradeMode:
    """Per-trade flag wins; falls back to session flag, then default."""
    if trade_paper or session_paper:
        return TradeMode.PAPER
    return TradeMode.REAL


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
        {
            "symbol": s.symbol,
            "signal_file": s.signal_id,
            "entry": s.guideline_entry,
            "stop": s.guideline_stop,
            "target": s.guideline_target,
            "signal_date_str": s.signal_timestamp,
        }
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
# evaluate / spec (shared packet lookup)
# ---------------------------------------------------------------------------

def _find_packet(symbol: str):
    """Load all inbox signals and return the first matching SignalV2 or None."""
    result = read_signals()
    matches = [s for s in result.load.valid if s.symbol.upper() == symbol.upper()]
    return matches[0] if matches else None


def cmd_evaluate(symbol: str, snapshot_path: str, cash: float, trade_mode: TradeMode) -> int:
    from application.evaluate_signal import evaluate_signal

    packet = _find_packet(symbol)
    if packet is None:
        print(f"[ERROR] No valid v2 packet found for {symbol} in {SIGNALS_DIR}")
        return 1

    snapshot = json.loads(open(snapshot_path, encoding="utf-8").read())
    result = evaluate_signal(packet, snapshot, cash_available=cash, trade_mode=trade_mode)

    mode_tag = f"  Mode:      {result.trade_mode.value}"
    print("=" * 60)
    print(f"EVALUATION: {result.symbol}  |  verdict={result.verdict}")
    print(mode_tag)
    print(f"  Posture:   {result.posture.risk_mode}")
    print(f"  Drift:     {result.drift_pct:+.2f}%")
    print(f"  R:R live:  {result.rr_after_drift:.2f}")
    if result.sizing:
        print(f"  Shares:    {result.sizing.shares}  (gate={result.sizing.winning_gate})")
        print(f"  $ risk:    ${result.sizing.dollar_risk:.2f}")
    print(result.council.summary())
    print("=" * 60)
    return 0


def cmd_spec(symbol: str, snapshot_path: str, cash: float, trade_mode: TradeMode) -> int:
    from application.evaluate_signal import evaluate_signal
    from application.build_order_spec import build_spec

    packet = _find_packet(symbol)
    if packet is None:
        print(f"[ERROR] No valid v2 packet found for {symbol} in {SIGNALS_DIR}")
        return 1

    snapshot = json.loads(open(snapshot_path, encoding="utf-8").read())
    result = evaluate_signal(packet, snapshot, cash_available=cash, trade_mode=trade_mode)
    print(build_spec(result, packet, snapshot))
    return 0


# ---------------------------------------------------------------------------
# Reader summary (original E1 command)
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
            print(f"    - {rej.path}")
            print(f"        {rej.reason}")
    print("=" * 60)
    for sig in result.load.valid:
        print(f"  {sig.symbol:<6} {sig.asset_class:<6} "
              f"entry={sig.guideline_entry:.2f} stop={sig.guideline_stop:.2f} "
              f"src={sig.signal_source}")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    _setup_logging()
    parser = argparse.ArgumentParser(prog="p400")
    parser.add_argument(
        "--paper-session",
        action="store_true",
        default=False,
        help="Mark all evaluate/spec calls this session as PAPER trades.",
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("screen-all", help="Tier-1 screen of whole inbox")

    p_eval = sub.add_parser("evaluate", help="Full evaluation for one symbol")
    p_eval.add_argument("symbol")
    p_eval.add_argument("--snapshot", required=True, help="Path to snapshot JSON file")
    p_eval.add_argument("--cash", type=float, required=True, help="Per-trade buying power")
    p_eval.add_argument(
        "--paper",
        action="store_true",
        default=False,
        help="Mark this trade as PAPER (overrides --paper-session).",
    )

    p_spec = sub.add_parser("spec", help="Evaluate and render Schwab order spec")
    p_spec.add_argument("symbol")
    p_spec.add_argument("--snapshot", required=True)
    p_spec.add_argument("--cash", type=float, required=True)
    p_spec.add_argument(
        "--paper",
        action="store_true",
        default=False,
        help="Mark this trade as PAPER (overrides --paper-session).",
    )

    args = parser.parse_args()
    session_paper = getattr(args, "paper_session", False)

    if args.cmd == "screen-all":
        return cmd_screen_all()
    if args.cmd == "evaluate":
        mode = _resolve_mode(session_paper, args.paper)
        return cmd_evaluate(args.symbol, args.snapshot, args.cash, mode)
    if args.cmd == "spec":
        mode = _resolve_mode(session_paper, args.paper)
        return cmd_spec(args.symbol, args.snapshot, args.cash, mode)

    # default: reader summary
    return cmd_reader()


if __name__ == "__main__":
    raise SystemExit(main())
