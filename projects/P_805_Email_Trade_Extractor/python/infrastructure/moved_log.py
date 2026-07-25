"""Infrastructure: read/write the Phase 5.3 moved-message audit log.

data/moved_messages.csv — one row per message the mover has attempted,
whether dry-run or real, whether it succeeded or failed. Read before every
move run so domain.message_selector can skip already-moved messages.
"""

import csv
import logging
from pathlib import Path

from schemas import MovedMessage

logger = logging.getLogger("p805")


def load_moved_log(path: Path) -> list[MovedMessage]:
    """Load the moved-message log. Returns [] if the file doesn't exist yet."""
    if not path.exists():
        return []
    rows: list[MovedMessage] = []
    with open(path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            try:
                rows.append(MovedMessage(**raw))
            except Exception as e:
                logger.warning(f"Skipping malformed moved-log row: {e}")
    return rows


def append_moved_log(entries: list[MovedMessage], path: Path) -> None:
    """Append new entries to the moved-message log; create file+header if new."""
    if not entries:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists()
    headers = list(MovedMessage.model_fields.keys())
    with open(path, "a", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        for entry in entries:
            row = entry.model_dump()
            row["moved_at"] = entry.moved_at.isoformat()
            writer.writerow(row)
    logger.info(f"Appended {len(entries)} row(s) to moved log: {path}")
