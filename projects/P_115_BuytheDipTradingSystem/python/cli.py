"""cli.py — command-line entry point for the P_115 signal emitter.

For manual and test runs. Parses thesis fields from the command line,
calls the application layer, and prints the written file path.

Run from this folder with the p140 interpreter:
    python.exe cli.py --symbol AMTM --session-date 2026-06-03
        --timestamp 2026-06-03T14:23:00Z --strategy dip_buy
        --entry 47.50 --stop 45.75 --target 52.00
        --horizon "10-15 trading days" --confidence HIGH --close 47.75
        --volume 1850000 --rationale "Dip into 20-day MA after earnings"
        --timeframe 1D --source-link "TradeOrderManagement/P_115/x.md"
        --atm 1.85 --support-1 45.20 --support-2 43.10
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import config  # noqa: E402
from application.emit_signal import emit_signal  # noqa: E402


def _parse_args() -> argparse.Namespace:
    """Define and parse command-line arguments."""
    p = argparse.ArgumentParser(description="Emit a P_115 -> P_400 signal packet.")
    p.add_argument("--symbol", required=True)
    p.add_argument("--session-date", required=True)
    p.add_argument("--timestamp", required=True)
    p.add_argument("--strategy", required=True)
    p.add_argument("--entry", type=float, required=True)
    p.add_argument("--stop", type=float, required=True)
    p.add_argument("--target", type=float, required=True)
    p.add_argument("--horizon", default=config.DEFAULT_SIGNAL_HORIZON)
    p.add_argument("--confidence", required=True)
    p.add_argument("--close", type=float, required=True)
    p.add_argument("--volume", type=float, required=True)
    p.add_argument("--rationale", required=True)
    p.add_argument("--timeframe", required=True)
    p.add_argument("--source-link", required=True)
    p.add_argument("--atm", type=float, default=None)
    p.add_argument("--support-1", type=float, default=None)
    p.add_argument("--support-2", type=float, default=None)
    p.add_argument("--source", default="P_115")
    return p.parse_args()


def main() -> None:
    """Parse args, emit one signal, print the resulting path."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    a = _parse_args()
    path = emit_signal(
        symbol=a.symbol,
        session_date=a.session_date,
        signal_timestamp=a.timestamp,
        strategy=a.strategy,
        guideline_entry=a.entry,
        guideline_stop=a.stop,
        guideline_target=a.target,
        signal_horizon=a.horizon,
        confidence_level=a.confidence,
        close_at_signal=a.close,
        trailing_volume_30d=a.volume,
        signal_rationale=a.rationale,
        chart_timeframe=a.timeframe,
        signal_source_link=a.source_link,
        atm_at_signal=a.atm,
        intelliscan_support_1=a.support_1,
        intelliscan_support_2=a.support_2,
        signal_source=a.source,
    )
    print(f"Signal written: {path}")


if __name__ == "__main__":
    main()