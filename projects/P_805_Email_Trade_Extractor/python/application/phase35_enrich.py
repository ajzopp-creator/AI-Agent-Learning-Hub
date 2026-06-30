"""Application: Phase 3.5 — LLM direction enrichment.

Workflow:
  1. Configure logging.
  2. Load today's signals CSV (Phase 3 output).
  3. For each signal where direction=unknown, call classify_direction(ticker, context).
  4. Rewrite the signals CSV in-place with updated directions.
  5. Log a summary of how many unknowns were resolved.

LLM selection (Gemini primary, LM Studio fallback) is handled entirely
by infrastructure/lm_studio_caller.py. This layer passes no LLM params.
"""

import csv
import logging
from datetime import date
from pathlib import Path

import config
from infrastructure.daily_csv_reader import load_signals_csv
from infrastructure.lm_studio_caller import classify_direction
from infrastructure.logging_setup import configure_logging
from schemas import TickerSignal

logger = logging.getLogger("p805")


def enrich_signals(signals: list[TickerSignal]) -> tuple[list[TickerSignal], int, int]:
    """Classify direction for each unknown signal.

    Args:
        signals: All signals from today's CSV.

    Returns:
        Tuple of (enriched signal list, resolved count, still-unknown count).
    """
    resolved = 0
    still_unknown = 0
    enriched: list[TickerSignal] = []

    for sig in signals:
        if sig.direction != "unknown":
            enriched.append(sig)
            continue
        direction = classify_direction(ticker=sig.ticker, context=sig.raw_context)
        if direction != "unknown":
            resolved += 1
        else:
            still_unknown += 1
        enriched.append(sig.model_copy(update={"direction": direction}))

    return enriched, resolved, still_unknown


def write_enriched_csv(signals: list[TickerSignal], output_path: Path) -> None:
    """Overwrite the signals CSV with enriched direction values."""
    headers = list(TickerSignal.model_fields.keys())
    with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for sig in signals:
            row = sig.model_dump()
            row["timestamp"] = sig.timestamp.isoformat()
            writer.writerow(row)
    logger.info(f"Rewrote enriched signals CSV: {output_path}")


def run(signals_path: Path | None = None) -> None:
    """Phase 3.5 entry point. Called from cli.py."""
    configure_logging()

    if signals_path is None:
        filename = config.DAILY_OUTPUT_CSV.format(date=date.today().isoformat())
        signals_path = config.DATA_DAILY_DIR / filename

    logger.info(f"Phase 3.5: enriching directions in {signals_path.name}")
    signals = load_signals_csv(signals_path)
    if not signals:
        logger.error("No signals loaded — aborting Phase 3.5.")
        return

    unknown_count = sum(1 for s in signals if s.direction == "unknown")
    logger.info(f"Signals: {len(signals)} total, {unknown_count} unknown direction")

    if unknown_count == 0:
        logger.info("No unknowns to enrich — nothing to do.")
        return

    logger.info("-" * 72)
    enriched, resolved, still_unknown = enrich_signals(signals)
    logger.info("-" * 72)
    logger.info(f"Resolved: {resolved}  Still unknown: {still_unknown}")
    write_enriched_csv(enriched, signals_path)
