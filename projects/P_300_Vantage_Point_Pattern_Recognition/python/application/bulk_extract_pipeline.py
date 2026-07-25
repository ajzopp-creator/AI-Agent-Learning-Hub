"""
FILE: application/bulk_extract_pipeline.py
VERSION: 1.2
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Pipeline A-Bulk orchestrator (WO-P300-E2.001). Pure orchestration --
    calls infrastructure, domain, and config modules; no business logic
    of its own. Never touches the live *catalog.db or Pipeline A/B.

    Flow, per file in data/bulk/ matching BULK_INPUT_GLOB:
        1. Skip if filename already in checkpoint.completed_filenames.
        2. Parse via bulk_grid_reader.parse_bulk_file -> BulkPatternFileParse.
        3. find_predictive_boundary_index -- detection starts only where
           VP's backfilled predictive columns are real.
        4. run_detection_sweep + apply_spacing_rule -> list[BulkDetectionHit].
        5. Per surviving hit: application.bulk_hit_writer.write_bulk_hit
           handles slice -> label -> temp-DB -> insert -> promote.
        6. Update + persist checkpoint after the FILE completes (not
           per-hit) -- a crash mid-file re-parses that file next run,
           but never leaves a partially-committed file's hits half in
           the catalog (each hit's own promote is already atomic).

    Sector lookup: sector_map.csv is operator-maintained and optional --
    a missing file or missing symbol row means sector=None, non-blocking
    (mirrors intelliscan_reader.py's absent-file precedent in Pipeline B).

CHANGELOG:
    - 2026-07-08 v1.2: run_bulk_extraction() gained a checkpoint_path
      parameter (default still BULK_CHECKPOINT_FILE, so real CLI/`.bat`
      usage is unaffected). Previously the function always read/wrote
      the LIVE checkpoint regardless of what master_db/temp_db were
      passed -- a test run against scratch DB paths still polluted the
      real bulk_extract_checkpoint.json, writing a real filename in as
      "completed" with 0 detections after an unrelated bug (see
      bulk_hit_writer.py v1.1) rejected every hit. Every subsequent test
      run then silently skipped the file because the live checkpoint
      said it was already done -- no per-hit log lines, no visible
      symptom, looked like the sweep found nothing. Caught via a real
      end-to-end PEH run against 5_Pattern_SPY.xlsx; the polluted live
      checkpoint file was confirmed absent and did not need cleanup
      (no real bulk-extract run has ever happened -- cli.py's
      +bulk-extract subcommand and P_300_BulkExtract.bat don't exist
      yet). _load_or_init_checkpoint and _save_checkpoint now take
      path as a required positional arg (no more implicit default) so
      a future caller can't repeat this by omission.
    - 2026-07-08 v1.1: Split _process_one_hit out to bulk_hit_writer.py
      (write_bulk_hit) -- v1.0 landed at 309 lines, over the 300 hard
      limit (M-031: split at a natural boundary, don't compress
      docstrings). This file is now orchestration-only.
    - 2026-07-08 v1.0: Initial release (superseded same-day by the split
      above).
"""
from __future__ import annotations

import csv
import logging
import sys
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from application.bulk_hit_writer import write_bulk_hit  # noqa: E402
from config import (  # noqa: E402
    BULK_CHECKPOINT_FILE,
    BULK_INPUT_GLOB,
    BULK_RESEARCH_DB,
    BULK_TEMP_DB,
    DATA_BULK,
    SECTOR_MAP_CSV,
)
from domain.bulk_windowing import (  # noqa: E402
    apply_spacing_rule,
    find_predictive_boundary_index,
    run_detection_sweep,
)
from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402
from infrastructure.research_catalog_io import ensure_research_catalog_exists  # noqa: E402
from schemas_bulk import BulkCheckpoint  # noqa: E402

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Sector map / checkpoint I/O
# ─────────────────────────────────────────────────────────────────────────────

def _load_sector_map(path: Path = SECTOR_MAP_CSV) -> dict[str, str]:
    """Returns {} if the file is absent -- non-blocking by design, see
    module docstring."""
    if not path.exists():
        logger.warning("sector_map.csv not found at %s -- all symbols get sector=None", path)
        return {}
    mapping: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            mapping[row["symbol"].upper()] = row["sector"]
    return mapping


def _load_or_init_checkpoint(path: Path) -> BulkCheckpoint:
    if path.exists():
        return BulkCheckpoint.model_validate_json(path.read_text(encoding="utf-8"))
    now = datetime.now()
    return BulkCheckpoint(run_started_at=now, last_updated_at=now, total_files_queued=0)


def _save_checkpoint(checkpoint: BulkCheckpoint, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(checkpoint.model_dump_json(indent=2), encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Per-file orchestration
# ─────────────────────────────────────────────────────────────────────────────

def _process_one_file(
    xlsx_path: Path,
    sector_map: dict[str, str],
    master_db: Path,
    temp_db: Path,
) -> tuple[int, int]:
    """Returns (strict_count, relaxed_count) for this file."""
    parse = parse_bulk_file(xlsx_path)
    bars = parse.bars
    boundary_idx = find_predictive_boundary_index(bars)
    if boundary_idx is None:
        logger.warning("skip %s: no usable predictive window found", xlsx_path.name)
        return (0, 0)

    raw_hits = run_detection_sweep(bars, boundary_idx)
    survivors = apply_spacing_rule(bars, raw_hits)
    logger.info(
        "%s: %d raw hits -> %d after spacing", xlsx_path.name, len(raw_hits), len(survivors)
    )

    symbol = parse.metadata.symbol
    sector = sector_map.get(symbol)
    strict_count = relaxed_count = 0
    for hit in survivors:
        ok = write_bulk_hit(
            hit, bars, symbol, sector, parse.metadata.filename,
            parse.metadata.window_years, parse.metadata.is_intelliscan_export,
            master_db, temp_db,
        )
        if not ok:
            continue
        if hit.tier.value == "STRICT":
            strict_count += 1
        else:
            relaxed_count += 1
    return (strict_count, relaxed_count)


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def run_bulk_extraction(
    input_dir: Path = DATA_BULK,
    master_db: Path = BULK_RESEARCH_DB,
    temp_db: Path = BULK_TEMP_DB,
    checkpoint_path: Path = BULK_CHECKPOINT_FILE,
) -> BulkCheckpoint:
    """End-to-end bulk extraction run. Checkpoint-resumable: files already
    in completed_filenames are skipped. Returns the final checkpoint.
    checkpoint_path defaults to the live BULK_CHECKPOINT_FILE -- callers
    testing against scratch master_db/temp_db MUST also pass a scratch
    checkpoint_path, or a test run will pollute the live checkpoint
    (see v1.2 changelog)."""
    ensure_research_catalog_exists(master_db)
    sector_map = _load_sector_map()
    checkpoint = _load_or_init_checkpoint(checkpoint_path)

    all_files = sorted(input_dir.glob(BULK_INPUT_GLOB)) if input_dir.exists() else []
    pending = [f for f in all_files if f.name not in checkpoint.completed_filenames]
    checkpoint.total_files_queued = len(all_files)
    logger.info(
        "bulk extraction: %d files total, %d pending (%d already complete)",
        len(all_files), len(pending), len(all_files) - len(pending),
    )

    for xlsx_path in pending:
        try:
            strict_n, relaxed_n = _process_one_file(xlsx_path, sector_map, master_db, temp_db)
            checkpoint.strict_detections_total += strict_n
            checkpoint.relaxed_detections_total += relaxed_n
            checkpoint.completed_filenames.append(xlsx_path.name)
            checkpoint.last_error = None
        except Exception as e:
            logger.error("FAILED %s: %s", xlsx_path.name, e)
            checkpoint.last_error = f"{xlsx_path.name}: {e}"
            # File NOT added to completed_filenames -- next run retries it.
        checkpoint.last_updated_at = datetime.now()
        _save_checkpoint(checkpoint, checkpoint_path)

    logger.info(
        "bulk extraction run complete: %d STRICT, %d RELAXED total",
        checkpoint.strict_detections_total, checkpoint.relaxed_detections_total,
    )
    return checkpoint


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s: %(message)s")
    run_bulk_extraction()
