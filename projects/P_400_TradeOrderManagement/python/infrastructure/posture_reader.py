"""P_400 infrastructure: read P_010 market posture.

Glob-discovers P_010_RiskConfig.json from Hub root -- folder path may drift.
Returns PostureSnapshot. No business logic.

Architecture v2.0 Section 3.4, 6.1.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from config import HUB_ROOT, P010_GLOB_PATTERN
from schemas import PostureSnapshot

logger = logging.getLogger("p400.posture_reader")

REQUIRED_FIELDS = {"risk_mode", "avg_posture", "timestamp"}


def read_posture(hub_root: Path = HUB_ROOT) -> PostureSnapshot:
    """Glob-discover and parse P_010_RiskConfig.json.

    Searches from hub_root using P010_GLOB_PATTERN. If multiple matches exist
    (should not happen in practice), the most recently modified file wins.

    Args:
        hub_root: Root to search from; defaults to HUB_ROOT from config.

    Returns:
        PostureSnapshot with risk_mode, avg_posture, and timestamp.

    Raises:
        FileNotFoundError: if no matching file is found.
        ValueError: if the file is missing required fields.
    """
    matches = sorted(
        hub_root.glob(P010_GLOB_PATTERN),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError(
            f"P_010_RiskConfig.json not found under {hub_root} "
            f"(pattern: {P010_GLOB_PATTERN})"
        )

    path = matches[0]
    if len(matches) > 1:
        logger.warning("Multiple posture files found; using %s", path)

    data = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        raise ValueError(f"P_010 posture file missing required fields: {missing}")

    logger.debug("Posture read from %s: risk_mode=%s", path.name, data["risk_mode"])
    return PostureSnapshot(
        risk_mode=data["risk_mode"],
        avg_posture=float(data["avg_posture"]),
        timestamp=data["timestamp"],
        source=str(path),
    )
