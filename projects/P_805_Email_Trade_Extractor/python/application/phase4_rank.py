"""Application: Phase 4 — consensus ranking.

Workflow:
  1. Load today's signals CSV (Phase 3 / 3.5 output).
  2. Build ranked consensus signals via domain/ranker.py.
  3. Write ranked output to data/daily/YYYY-MM-DD_ranked.csv.
  4. Log summary: total signals in, consensus tickers out.
"""

import logging
from datetime import date
from pathlib import Path

import config
from domain.ranker import build_ranked_signals
from infrastructure.daily_csv_reader import load_signals_csv
from infrastructure.logging_setup import configure_logging
from infrastructure.ranked_csv_writer import write_ranked_csv
from infrastructure.sender_sheet import load_sender_sectors

logger = logging.getLogger("p805")


def run(signals_path: Path | None = None, ranked_path: Path | None = None) -> None:
    """Phase 4 entry point. Called from cli.py."""
    configure_logging()

    today = date.today().isoformat()

    if signals_path is None:
        filename = config.DAILY_OUTPUT_CSV.format(date=today)
        signals_path = config.DATA_DAILY_DIR / filename

    if ranked_path is None:
        ranked_filename = config.DAILY_RANKED_CSV.format(date=today)
        ranked_path = config.DATA_DAILY_DIR / ranked_filename

    logger.info(f"Phase 4: ranking signals from {signals_path.name}")
    signals = load_signals_csv(signals_path)

    if not signals:
        logger.error("No signals loaded — aborting Phase 4.")
        return

    logger.info(f"Loaded {len(signals)} signals — building consensus")
    logger.info(f"Consensus threshold: {config.CONSENSUS_THRESHOLD} sources")
    logger.info("-" * 72)

    sector_map = load_sender_sectors()
    logger.info(f"Sector map: {len(sector_map)} senders tagged")

    ranked = build_ranked_signals(signals, config.CONSENSUS_THRESHOLD, sector_map)

    direction_counts = {}
    for r in ranked:
        direction_counts[r.direction] = direction_counts.get(r.direction, 0) + 1

    logger.info(f"Consensus tickers: {len(ranked)}")
    for direction, count in sorted(direction_counts.items()):
        logger.info(f"  {direction}: {count}")
    logger.info("-" * 72)

    write_ranked_csv(ranked, ranked_path)
