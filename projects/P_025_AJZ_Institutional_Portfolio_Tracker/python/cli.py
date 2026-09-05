"""
P_025 AJZ Institutional Portfolio Tracker — CLI Entry Point

Usage
-----
    python cli.py build [--mode full|yearly|ytd]
    python cli.py update
    python cli.py quick
"""

from __future__ import annotations

import argparse
import logging
import sys

from config import ANALYSIS_MODE, LOG_FORMAT, LOG_LEVEL


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
        default=None,
        help=(
            "Analysis window for build: "
            "full=3y trailing (default), yearly=365d trailing, ytd=calendar year-to-date. "
            "Ignored for update/quick. Overrides P025_ANALYSIS_MODE env."
        ),
    )
    args = parser.parse_args(argv)

    if args.command == "build":
        from application.build_portfolio import run_full_build
        mode = args.mode or ANALYSIS_MODE
        logger.info("Running full build (mode=%s)…", mode)
        run_full_build(mode=mode)
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
