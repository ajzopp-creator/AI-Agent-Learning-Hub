"""P_400 infrastructure: signal JSON archiver.

After a signal is evaluated (any terminal disposition), the source JSON packet
is appended to the monthly processed zip and deleted from the inbox.

I/O only -- no business logic.
"""

from __future__ import annotations

import logging
import zipfile
from datetime import date
from pathlib import Path

from config import SIGNALS_DIR, SIGNALS_PROCESSED_DIR, V2_PATTERN

logger = logging.getLogger("p400.signal_archiver")


def _monthly_zip_path(ref_date: date | None = None) -> Path:
    """Return the path for this month's processed zip.

    Filename pattern: YYMM_ProcessedJson.zip  (e.g. 2606_ProcessedJson.zip)
    """
    d = ref_date or date.today()
    name = f"{d.strftime('%y%m')}_ProcessedJson.zip"
    return SIGNALS_PROCESSED_DIR / name


def _find_packet(symbol: str, signal_date: str) -> Path | None:
    """Locate the v2.0 JSON packet for a symbol+date in SIGNALS_DIR.

    Tries exact filename first, then falls back to glob on symbol name.

    Args:
        symbol: Ticker string (e.g. 'BEKE').
        signal_date: ISO date string matching the packet filename (e.g. '2026-06-15').

    Returns:
        Path to the packet, or None if not found.
    """
    exact = SIGNALS_DIR / f"{signal_date}_{symbol}_v2.0.json"
    if exact.exists():
        return exact
    matches = list(SIGNALS_DIR.glob(f"*_{symbol}_v2.0.json"))
    if matches:
        return matches[0]
    return None


def archive_packet(symbol: str, signal_date: str) -> bool:
    """Append the source JSON to the monthly zip and delete from inbox.

    Creates SIGNALS_PROCESSED_DIR if it does not exist.
    Appends to existing zip if present; creates new zip otherwise.
    Deletes the original only after a confirmed successful zip write.

    Args:
        symbol: Ticker string.
        signal_date: ISO date string from the packet (used to find the file).

    Returns:
        True if archived successfully, False if packet not found or error.
    """
    packet_path = _find_packet(symbol, signal_date)
    if packet_path is None:
        logger.warning("archive_packet: no packet found for %s %s -- skipping.", symbol, signal_date)
        return False

    SIGNALS_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = _monthly_zip_path()

    try:
        with zipfile.ZipFile(zip_path, mode="a", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(packet_path, arcname=packet_path.name)
        packet_path.unlink()
        logger.info("Archived %s -> %s", packet_path.name, zip_path.name)
        return True
    except Exception as exc:
        logger.error("archive_packet failed for %s: %s", packet_path.name, exc)
        return False
