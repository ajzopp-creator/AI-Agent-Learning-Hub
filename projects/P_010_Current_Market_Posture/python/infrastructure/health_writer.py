"""
P_010 Market Health -- infrastructure/health_writer.py

Atomic JSON write for P_010_MarketHealth.json. Backs up the prior
version before replacing so a bad write is always recoverable.

Spec reference: docs/P_010_MarketHealth_Spec_v1_1.md Section 6
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from market_health.config import OUTPUT_JSON, SNAPSHOT_DIR
from market_health.schemas import MarketHealthOutput


def write_health(
    output: MarketHealthOutput,
    target: Path = OUTPUT_JSON,
) -> Path:
    """
    Write the MarketHealthOutput to disk atomically.

    Steps:
      1. Serialize to .tmp sibling file
      2. If target exists, rename it to .backup_YYYYMMDD_HHMMSS
      3. os.replace(.tmp -> target) -- atomic on Windows for same volume

    Returns the final path written.
    """
    target.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = target.with_suffix(target.suffix + ".tmp")
    payload = output.model_dump_json(indent=2)
    tmp_path.write_text(payload, encoding="utf-8")

    if target.exists():
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = target.with_name(f"{target.stem}.backup_{stamp}{target.suffix}")
        shutil.copy2(target, backup_path)

    os.replace(tmp_path, target)

    # Phase 2 archive: dated snapshot for baseline accumulation
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_path = SNAPSHOT_DIR / f"{output.as_of_date:%Y%m%d}.json"
    shutil.copy2(target, snapshot_path)

    return target
