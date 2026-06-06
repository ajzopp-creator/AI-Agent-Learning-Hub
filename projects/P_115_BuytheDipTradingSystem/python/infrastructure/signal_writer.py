"""signal_writer.py — file I/O for signal packets.

Derives the next sequence number by counting existing same-day
same-symbol files, and writes validated packets to disk as JSON.
This is the only emitter module that touches the filesystem.
"""

from __future__ import annotations

import logging
from pathlib import Path

import config
from schemas import P400SignalRecord

log = logging.getLogger(__name__)


def next_sequence(session_date: str, symbol: str) -> int:
    """Return the next 1-based sequence for a symbol+date.

    Counts files in SIGNALS_DIR whose name starts with
    '<date>_<symbol>_signal'. Returns 1 when the directory is absent.
    """
    if not config.SIGNALS_DIR.exists():
        return 1
    prefix = config.FILENAME_BASE.format(date=session_date, symbol=symbol)
    existing = list(config.SIGNALS_DIR.glob(f"{prefix}*{config.FILENAME_EXT}"))
    return len(existing) + 1


def write_signal(record: P400SignalRecord, filename: str) -> Path:
    """Write a validated packet to SIGNALS_DIR/<filename>.

    Creates the signals directory if needed. Returns the written path.

    Raises:
        OSError: if the directory or file cannot be written.
    """
    try:
        config.SIGNALS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = config.SIGNALS_DIR / filename
        out_path.write_text(
            record.model_dump_json(indent=config.JSON_INDENT),
            encoding="utf-8",
        )
        log.info("signal written: %s", out_path)
        return out_path
    except OSError as exc:
        log.error("failed to write signal %s: %s", filename, exc)
        raise