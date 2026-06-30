"""P_400 CLI entry point.

Commands (run from python/ dir, p140 env):

    python cli.py                              -- reader summary (E1)
    python cli.py screen-all                   -- Tier-1 screen of whole inbox
    python cli.py evaluate SYMBOL --snapshot FILE --cash DOLLARS
    python cli.py evaluate SYMBOL --snapshot FILE --cash DOLLARS --drop-reason REASON
    python cli.py spec SYMBOL --snapshot FILE --cash DOLLARS
    python cli.py compare SYMBOL --snapshot FILE --chain FILE --cash DOLLARS

Session paper mode: python cli.py --paper-session <subcommand>

Command implementations live in application/commands.py (WO-P400-E2.015
follow-on -- this file is argparse wiring + main() dispatch only, kept
under the 300-line cap).
"""

import argparse
import logging

from config import TradeMode


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _resolve_mode(session_paper: bool, trade_paper: bool) -> TradeMode:
    if trade_paper or session_paper:
        return TradeMode.PAPER
    return TradeMode.REAL


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="p400")
    parser.add_argument("--paper-session", action="store_true", default=False)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("screen-all")

    p_eval = sub.add_parser("evaluate")
    p_eval.add_argument("symbol")
    p_eval.add_argument("--snapshot", required=True)
    p_eval.add_argument("--cash", type=float, required=True)
    p_eval.add_argument("--target", type=float, default=None)
    p_eval.add_argument("--paper", action="store_true", default=False)
    p_eval.add_argument("--pre-market", action="store_true", default=False)
    p_eval.add_argument("--qty-override", type=int, default=None)
    p_eval.add_argument("--drop-reason", default=None)
    p_eval.add_argument("--options", action="store_true", default=False)
    p_eval.add_argument("--chain", default=None, help="Path to chain_SYMBOL.json (single-leg, or spread long leg)")
    p_eval.add_argument("--spread", action="store_true", default=False)
    p_eval.add_argument("--chain-short", dest="chain_short", default=None,
                        help="Path to chain_SYMBOL.json for spread short leg (required with --spread)")

    p_spec = sub.add_parser("spec")
    p_spec.add_argument("symbol")
    p_spec.add_argument("--snapshot", required=True)
    p_spec.add_argument("--cash", type=float, required=True)
    p_spec.add_argument("--target", type=float, default=None)
    p_spec.add_argument("--paper", action="store_true", default=False)
    p_spec.add_argument("--pre-market", action="store_true", default=False)
    p_spec.add_argument("--qty-override", type=int, default=None)

    p_cmp = sub.add_parser("compare")
    p_cmp.add_argument("symbol")
    p_cmp.add_argument("--snapshot", required=True)
    p_cmp.add_argument("--chain", required=True, help="Path to chain_SYMBOL.json")
    p_cmp.add_argument("--cash", type=float, required=True)

    return parser


def main() -> int:
    from application import commands

    _setup_logging()
    parser = _build_parser()
    args = parser.parse_args()
    session_paper = getattr(args, "paper_session", False)

    if args.cmd == "screen-all":
        return commands.cmd_screen_all()
    if args.cmd == "evaluate":
        mode = _resolve_mode(session_paper, args.paper)
        return commands.cmd_evaluate(
            args.symbol, args.snapshot, args.cash, mode,
            target_override=getattr(args, "target", None),
            pre_market=getattr(args, "pre_market", False),
            qty_override=getattr(args, "qty_override", None),
            drop_reason=getattr(args, "drop_reason", None),
            options=getattr(args, "options", False),
            chain_path=getattr(args, "chain", None),
            spread=getattr(args, "spread", False),
            chain_short_path=getattr(args, "chain_short", None))
    if args.cmd == "spec":
        mode = _resolve_mode(session_paper, args.paper)
        return commands.cmd_spec(
            args.symbol, args.snapshot, args.cash, mode,
            target_override=getattr(args, "target", None),
            pre_market=getattr(args, "pre_market", False),
            qty_override=getattr(args, "qty_override", None))
    if args.cmd == "compare":
        return commands.cmd_compare(args.symbol, args.snapshot, args.chain, args.cash)
    return commands.cmd_reader()


if __name__ == "__main__":
    raise SystemExit(main())