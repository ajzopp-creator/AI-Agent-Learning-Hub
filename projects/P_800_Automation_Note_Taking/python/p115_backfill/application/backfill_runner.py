"""backfill_runner.py — orchestrates the P_115 Excel → vault backfill.

Reads rows via excel_reader, maps them via row_mapper, writes each
note to the vault via write_to_vault(). Returns a BackfillResult
summary on completion.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from shared_resources.python_utils.vault_interface import write_to_vault

from p115_backfill.config import (
    EXCEL_TO_SCHEMA_MAP,
    HEADER_ROW,
    LOG_INTERVAL,
    REQUIRED_FIELDS,
    TRACKER_PATH,
    TRACKER_SHEET,
)
from p115_backfill.domain.row_mapper import map_row
from p115_backfill.infrastructure.excel_reader import read_rows

log = logging.getLogger(__name__)


@dataclass
class BackfillResult:
    """Summary of a completed backfill run."""
    total_read: int = 0
    written: int = 0
    skipped_missing: int = 0
    skipped_exists: int = 0
    errors: int = 0
    error_details: list[str] = field(default_factory=list)

    @property
    def total_skipped(self) -> int:
        return self.skipped_missing + self.skipped_exists


def run_backfill(
    dry_run: bool = False,
    overwrite: bool = False,
    limit: int | None = None,
) -> BackfillResult:
    """Run the full backfill from Excel tracker to Obsidian vault.

    Args:
        dry_run: Log what would be written without writing anything.
        overwrite: Overwrite existing vault notes when True.
        limit: Stop after N rows (for test runs). None = all rows.

    Returns:
        BackfillResult with counts for written, skipped, and errored rows.
    """
    result = BackfillResult()

    for raw_row in read_rows(TRACKER_PATH, TRACKER_SHEET, HEADER_ROW):
        result.total_read += 1

        if limit is not None and result.total_read > limit:
            log.info("Row limit of %d reached — stopping.", limit)
            break

        mapped: dict[str, Any] | None = map_row(
            raw_row, EXCEL_TO_SCHEMA_MAP, REQUIRED_FIELDS
        )
        if mapped is None:
            result.skipped_missing += 1
            continue

        label = f"{mapped.get('date')} / {mapped.get('symbol')}"

        if dry_run:
            log.info("[DRY RUN] Would write: %s", label)
            result.written += 1
            continue

        try:
            wrote = write_to_vault("P115", mapped, overwrite=overwrite)
            if wrote:
                result.written += 1
            else:
                result.skipped_exists += 1
                log.debug("Skipped existing note: %s", label)
        except Exception as exc:
            result.errors += 1
            msg = f"{label}: {exc}"
            result.error_details.append(msg)
            log.error("Write failed — %s", msg)

        if result.total_read % LOG_INTERVAL == 0:
            log.info(
                "Progress — read=%d written=%d skipped=%d errors=%d",
                result.total_read, result.written,
                result.total_skipped, result.errors,
            )

    log.info(
        "Backfill complete — read=%d written=%d skipped=%d errors=%d",
        result.total_read, result.written,
        result.total_skipped, result.errors,
    )
    return result
