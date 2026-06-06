"""
P_010 Market Health -- market_health/cli_backtest.py

Argparse entry point for the Workstream C backtest harness. Invoked as:
    python -m market_health.cli_backtest [args]

Exit codes:
  0 = success
  1 = VP input error (file missing, schema bad)
  2 = empty / unusable data (no overlapping dates, range too narrow)
  3 = unexpected error
"""

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

from market_health.config import LOG_DIR, PROJECT_ROOT
from application.backtest_runner import DEFAULT_WARMUP_DAYS, run_backtest


DEFAULT_OUTPUT = (
    PROJECT_ROOT / "data" / "backtests" / f"P_010_Backtest_{datetime.now():%Y%m%d_%H%M%S}.csv"
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    _configure_logging(args.verbose)
    log = logging.getLogger("market_health.backtest")

    try:
        output_path = Path(args.output) if args.output else DEFAULT_OUTPUT
        path, rows = run_backtest(
            output_csv=output_path,
            start=_parse_date(args.start) if args.start else None,
            end=_parse_date(args.end) if args.end else None,
            warmup_days=args.warmup_days,
        )
    except FileNotFoundError as e:
        log.error("VP file missing: %s", e)
        return 1
    except ValueError as e:
        log.error("Data error: %s", e)
        return 2
    except Exception as e:  # noqa: BLE001 -- last-resort catch
        log.exception("Unexpected error: %s", e)
        return 3

    log.info("Backtest complete: %d rows written to %s", rows, path)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="market_health.cli_backtest",
        description="P_010 Backtest Harness -- write daily phase classifications to CSV",
    )
    p.add_argument("--start", help="First backtest date YYYY-MM-DD (default: earliest after warmup)")
    p.add_argument("--end", help="Last backtest date YYYY-MM-DD (default: latest VP row)")
    p.add_argument(
        "--warmup-days",
        type=int,
        default=DEFAULT_WARMUP_DAYS,
        help=f"Days of warmup before first emit (default: {DEFAULT_WARMUP_DAYS})",
    )
    p.add_argument("--output", help="Output CSV path (default: data/backtests/P_010_Backtest_<timestamp>.csv)")
    p.add_argument("--verbose", action="store_true", help="Debug-level logging")
    return p.parse_args(argv)


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _configure_logging(verbose: bool) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"backtest_{datetime.now():%Y%m%d}.log"
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
