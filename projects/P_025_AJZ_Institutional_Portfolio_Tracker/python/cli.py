"""
P_025 AJZ Institutional Portfolio Tracker — CLI Entry Point

Usage
-----
    python cli.py build
    python cli.py update
    python cli.py quick
"""

from __future__ import annotations

import argparse
import logging
import sys

from config import LOG_FORMAT, LOG_LEVEL


def _configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    logger = logging.getLogger("p025.cli")

    parser = argparse.ArgumentParser(
        description="P_025 AJZ Institutional Portfolio Tracker",
    )
    parser.add_argument(
        "command",
        choices=["build", "update", "quick"],
        help="build = full rebuild | update = incremental | quick = prices only",
    )
    parser.add_argument(
        "--mode",
        choices=["full", "yearly", "ytd"],
        default="full",
        help="lookback window for build: full=3y | yearly=365d | ytd=Jan 1",
    )
    args = parser.parse_args(argv)

    if args.command == "build":
        from application.build_portfolio import run_full_build
        logger.info("Running full build (mode=%s)…", args.mode)
        run_full_build(mode=args.mode)
    elif args.command == "update":
        from application.update_portfolio import run_update
        logger.info("Running incremental update…")
        run_update(quick_prices_only=False)
    elif args.command == "quick":
        from application.update_portfolio import run_update
        logger.info("Running quick price refresh…")
        run_update(quick_prices_only=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
