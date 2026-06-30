"""Infrastructure: load a daily signals CSV into TickerSignal objects.

I/O only — no ranking logic lives here.
"""

import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from schemas import TickerSignal

logger = logging.getLogger("p805")


def load_signals_csv(path: Path) -> list[TickerSignal]:
    """Read a Phase 3 signals CSV and return validated TickerSignal objects.

    Args:
        path: Full path to the signals CSV (e.g. data/daily/2026-06-14_signals.csv).

    Returns:
        List of TickerSignal objects. Rows that fail validation are skipped
        with a warning logged.
    """
    if not path.exists():
        logger.error(f"Signals CSV not found: {path}")
        return []

    signals: list[TickerSignal] = []
    skipped = 0

    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                # timestamp is stored as ISO string; parse back to datetime.
                ts_raw = row.get("timestamp", "")
                ts = datetime.fromisoformat(ts_raw)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                row["timestamp"] = ts
                signals.append(TickerSignal.model_validate(row))
            except Exception as exc:
                logger.warning(f"Skipping row (validation error): {exc} | row={row}")
                skipped += 1

    logger.info(f"Loaded {len(signals)} signals from {path.name} ({skipped} skipped)")
    return signals
