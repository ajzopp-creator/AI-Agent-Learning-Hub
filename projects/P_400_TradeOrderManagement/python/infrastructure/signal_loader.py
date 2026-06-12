"""Signal loading — I/O only.

Scans the signals folder, reads JSON, validates each packet against the
canonical SignalV2 contract. Malformed packets are rejected (logged and
skipped) — never repaired, per locked E2 decision #3. One bad packet never
aborts the run.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from config import LOGGER_NAME, SIGNALS_DIR, V2_PATTERN
from schemas import SignalV2

logger = logging.getLogger(LOGGER_NAME)


@dataclass
class RejectedPacket:
    """A packet that failed to read or validate."""

    path: str
    reason: str


@dataclass
class LoadResult:
    """Outcome of a v2 load pass."""

    valid: list[SignalV2] = field(default_factory=list)
    rejected: list[RejectedPacket] = field(default_factory=list)


def list_v2_files(signals_dir: Path = SIGNALS_DIR) -> list[Path]:
    """Return all *_v2.0.json paths in the signals folder (sorted).

    Args:
        signals_dir: Folder to scan. Defaults to the configured signals dir.

    Returns:
        Sorted list of matching file paths. Empty if the folder is absent.
    """
    if not signals_dir.exists():
        logger.warning("Signals dir not found: %s", signals_dir)
        return []
    return sorted(signals_dir.glob(V2_PATTERN))


def _load_one(path: Path) -> tuple[SignalV2 | None, RejectedPacket | None]:
    """Read and validate a single packet. Returns (model, None) or (None, reject)."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, RejectedPacket(str(path), f"read error: {exc}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, RejectedPacket(str(path), f"invalid JSON: {exc}")
    try:
        return SignalV2(**data), None
    except ValidationError as exc:
        return None, RejectedPacket(str(path), f"schema validation failed: {exc.error_count()} error(s)")


def load_v2_signals(signals_dir: Path = SIGNALS_DIR) -> LoadResult:
    """Load and validate all v2 packets in the signals folder.

    Args:
        signals_dir: Folder to scan. Defaults to the configured signals dir.

    Returns:
        LoadResult with valid SignalV2 models and rejected packets.
    """
    result = LoadResult()
    for path in list_v2_files(signals_dir):
        model, reject = _load_one(path)
        if model is not None:
            result.valid.append(model)
        else:
            logger.warning("REJECTED %s -- %s", path.name, reject.reason)
            result.rejected.append(reject)
    return result
