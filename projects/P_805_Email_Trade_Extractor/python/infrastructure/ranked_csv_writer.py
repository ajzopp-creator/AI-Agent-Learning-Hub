"""Infrastructure: write Phase 4 ranked signals to CSV.

I/O only — no ranking logic. Receives a list of RankedSignal objects
and writes them to the daily ranked output path.
"""

import csv
import logging
from pathlib import Path

from schemas import RankedSignal

logger = logging.getLogger("p805")


def write_ranked_csv(ranked: list[RankedSignal], output_path: Path) -> None:
    """Write ranked signals to a UTF-8 BOM CSV (Excel-safe).

    Args:
        ranked: Sorted list of RankedSignal objects.
        output_path: Full path for the output file.
    """
    if not ranked:
        logger.warning("write_ranked_csv: no signals to write — skipping")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    headers = list(RankedSignal.model_fields.keys())

    with open(output_path, "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()
        for sig in ranked:
            row = sig.model_dump()
            row["first_seen"] = sig.first_seen.isoformat()
            row["last_seen"] = sig.last_seen.isoformat()
            writer.writerow(row)

    logger.info(f"Ranked CSV written: {output_path} ({len(ranked)} rows)")
