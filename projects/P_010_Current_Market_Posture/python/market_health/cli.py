"""
P_010 Market Health -- market_health/cli.py

Argparse entry point. Invoked as:  python -m market_health.cli [args]
from the project's python/ folder (so the package roots resolve).

Exit codes:
  0 = success
  1 = VP input error (file missing, schema bad)
  2 = empty / unusable data
  3 = unexpected error
"""

import argparse
import logging
import sys
from datetime import date, datetime

from market_health.config import LOG_DIR
from application.health_runner import run_market_health


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    _configure_logging(args.verbose)
    log = logging.getLogger("market_health")

    try:
        as_of = _parse_date(args.date) if args.date else None
        output = run_market_health(as_of=as_of, dry_run=args.dry_run)
    except FileNotFoundError as e:
        log.error("VP file missing: %s", e)
        return 1
    except ValueError as e:
        log.error("Data error: %s", e)
        return 2
    except Exception as e:  # noqa: BLE001 -- last-resort catch
        log.exception("Unexpected error: %s", e)
        return 3

    log.info(
        "as_of=%s phase=%s max_dist=%d  spy_dist=%d qqq_dist=%d  "
        "spy_rally=%s qqq_rally=%s",
        output.as_of_date,
        output.market_phase,
        output.max_dist_count,
        output.spy.dist_count,
        output.qqq.dist_count,
        output.spy.rally_state,
        output.qqq.rally_state,
    )
    if args.dry_run:
        log.info("DRY RUN -- no JSON written")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="market_health",
        description="P_010 Distribution Day Tracker -- writes P_010_MarketHealth.json",
    )
    p.add_argument("--date", help="As-of date YYYY-MM-DD (default: latest VP row)")
    p.add_argument("--dry-run", action="store_true", help="Compute but skip JSON write")
    p.add_argument("--verbose", action="store_true", help="Debug-level logging")
    return p.parse_args(argv)


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _configure_logging(verbose: bool) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"market_health_{datetime.now():%Y%m%d}.log"
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


if __name__ == "__main__":
    raise SystemExit(main())
