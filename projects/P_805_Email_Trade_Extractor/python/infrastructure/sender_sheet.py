"""Infrastructure: load and validate the approved-sender whitelist.

Reads data/sender_sheet.csv, validates each row through the
ApprovedSender Pydantic model, and returns the set of email addresses
where enabled=true (lowercased for case-insensitive matching).

Malformed rows are logged and skipped — they never crash the run.
"""

import csv
import logging

import config
from schemas import ApprovedSender

logger = logging.getLogger("p805")


def _coerce_optional_fields(row: dict) -> dict:
    """Convert empty CSV strings to None for optional schema fields.

    Pydantic v2 keeps '' as a literal empty string; we want None so
    sector reads cleanly downstream.
    """
    if not row.get("sector"):
        row["sector"] = None
    return row


def load_enabled_senders() -> set[str]:
    """Return the set of lowercased email addresses where enabled=true.

    Returns an empty set (and logs an error) if the CSV is missing.
    """
    addresses: set[str] = set()
    if not config.SENDER_SHEET.exists():
        logger.error(f"Sender sheet not found: {config.SENDER_SHEET}")
        return addresses

    with open(config.SENDER_SHEET, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    enabled_count = 0
    skipped = 0
    for row in rows:
        row = _coerce_optional_fields(row)
        try:
            sender = ApprovedSender(**row)
        except Exception as exc:
            logger.warning(f"Skipping malformed sender row: {row} ({exc})")
            skipped += 1
            continue
        if sender.enabled:
            addresses.add(sender.email_address.strip().lower())
            enabled_count += 1

    logger.info(
        f"sender_sheet.csv: {enabled_count} enabled, "
        f"{len(rows) - enabled_count - skipped} disabled, {skipped} skipped"
    )
    return addresses


def load_sender_sectors() -> dict[str, str]:
    """Return a lowercased email_address -> sector map for enabled senders.

    Senders with a blank/missing sector column are omitted from the map
    entirely (not mapped to 'unknown' here) — domain.ranker treats any
    address absent from this map as 'unknown' sector, so a blank CSV
    cell and a missing row behave the same way downstream.

    Returns an empty dict (and logs an error) if the CSV is missing.
    """
    sectors: dict[str, str] = {}
    if not config.SENDER_SHEET.exists():
        logger.error(f"Sender sheet not found: {config.SENDER_SHEET}")
        return sectors

    with open(config.SENDER_SHEET, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    for row in rows:
        row = _coerce_optional_fields(row)
        try:
            sender = ApprovedSender(**row)
        except Exception:
            continue  # already logged/counted in load_enabled_senders
        if sender.enabled and sender.sector:
            sectors[sender.email_address.strip().lower()] = sender.sector.strip().lower()

    return sectors
