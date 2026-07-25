"""P_400 CLI entry point.

Commands (run from python/ dir, p140 env):

    python cli.py                              -- reader summary (E1)
    python cli.py screen-all                   -- Tier-1 screen of whole inbox
    python cli.py evaluate SYMBOL --snapshot FILE --cash DOLLARS
    python cli.py evaluate SYMBOL --snapshot FILE --cash DOLLARS --drop-reason REASON
    python cli.py spec SYMBOL --snapshot FILE --cash DOLLARS
    python cli.py compare SYMBOL --snapshot FILE --chain FILE --cash DOLLARS
    python cli.py record SYMBOL --order-id ID   -- WO-P400-E3.006, after evaluate/spec APPROVED
    python cli.py record SYMBOL --decline       -- WO-P400-E3.006, Tony skipped an APPROVED signal
    python cli.py schwab-auth                   -- WO-P400-E4.001, re-run Schwab OAuth
    python cli.py fetch-snapshot SYMBOL         -- WO-P400-E4.002, live Schwab snapshot
    python cli.py fetch-chain SYMBOL --type call|put -- WO-P400-E4.002, auto-select or --strike/--expiration
    python cli.py dossier SYMBOL                -- WO-P400-E4.003, computed technical dossier (items 1-8)
    python cli.py audit-book                    -- book vs. real AJZ Schwab positions, Tony directive 2026-07-24

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

    p_rec = sub.add_parser("record")
    p_rec.add_argument("symbol")
    p_rec.add_argument("--order-id", dest="order_id", default=None)
    p_rec.add_argument("--decline", action="store_true", default=False)

    sub.add_parser("schwab-auth")

    p_fsnap = sub.add_parser("fetch-snapshot")
    p_fsnap.add_argument("symbol")
    p_fsnap.add_argument("--earnings-date", dest="earnings_date", default=None)
    p_fsnap.add_argument("--sector", default=None)
    p_fsnap.add_argument("--last-earnings-date", dest="last_earnings_date", default=None,
                          help="WO-P400-E2.023, most recent past earnings date, YYYY-MM-DD")

    p_fchain = sub.add_parser("fetch-chain")
    p_fchain.add_argument("symbol")
    p_fchain.add_argument("--type", dest="option_type", required=True, choices=["call", "put"])
    p_fchain.add_argument("--strike", type=float, default=None)
    p_fchain.add_argument("--expiration", default=None)

    p_dossier = sub.add_parser("dossier")
    p_dossier.add_argument("symbol")

    sub.add_parser("audit-book")

    return parser


def main() -> int:
    from application import commands

    _setup_logging()
    parser = _build_parser()
    args = parser.parse_args()
    session_paper = getattr(args, "paper_session", False)

    if args.cmd == "screen-all":
        mode = _resolve_mode(session_paper, False)
        return commands.cmd_screen_all(mode)
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
    if args.cmd == "record":
        return commands.cmd_record(args.symbol, order_id=args.order_id, decline=args.decline)
    if args.cmd == "schwab-auth":
        return commands.cmd_schwab_auth()
    if args.cmd == "fetch-snapshot":
        from application.fetch_snapshot import cmd_fetch_snapshot
        return cmd_fetch_snapshot(args.symbol, earnings_date=args.earnings_date, sector=args.sector,
                                   last_earnings_date=args.last_earnings_date)
    if args.cmd == "fetch-chain":
        from application.fetch_chain import cmd_fetch_chain
        return cmd_fetch_chain(args.symbol, args.option_type, strike=args.strike, expiration=args.expiration)
    if args.cmd == "dossier":
        from application.build_dossier import cmd_dossier
        return cmd_dossier(args.symbol)
    if args.cmd == "audit-book":
        from application.audit_book import cmd_audit_book
        return cmd_audit_book()
    return commands.cmd_reader()


if __name__ == "__main__":
    raise SystemExit(main())