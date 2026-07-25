"""
FILE: application/bulk_hit_writer.py
VERSION: 1.1
DATE: 2026-07-08
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Single-detection persistence for WO-P300-E2.001 Pipeline A-Bulk.
    Split out of bulk_extract_pipeline.py (v1.0 landed at 309 lines,
    over the 300 hard limit) at a natural boundary: file-level
    orchestration (parse -> sweep -> spacing -> loop) vs. one detection's
    write path (slice -> label -> temp-DB -> insert -> promote). Pure
    orchestration -- no detection logic, no windowing (those stay in
    domain/), calls infrastructure directly.

    write_bulk_hit is the sole export. Slices the BULK_WINDOW_LENGTH
    window ending at the hit, computes forward labels via
    domain.bulk_labeler, and writes one pattern_instance end-to-end via
    the Lock + Temp-DB + Atomic Move protocol (research_catalog_io).

CHANGELOG:
    - 2026-07-08 v1.1: Fixed expected_delta hardcoding "symbols": 0 and
      "source_files": 0 -- against an empty or partially-populated
      catalog, the FIRST hit for a given symbol/source_file genuinely
      creates a new row (+1), and verify_and_promote_research rejected
      every such hit on the resulting delta mismatch. Fixed by checking
      row existence (SELECT ... WHERE ticker/filename = ?) BEFORE the
      insert calls and setting expected_delta from that, not a hardcoded
      assumption. Caught via a real end-to-end PEH run against
      5_Pattern_SPY.xlsx (28 real survivors, all silently rejected --
      the v1.0 docstring note "delta is computed loosely here (0
      assumed)... deferred as unnecessary precision" was wrong: it's
      not imprecise, it's incorrect for the first-hit-per-symbol/file
      case, which is every symbol's first hit by definition.
    - 2026-07-08 v1.0: Split from bulk_extract_pipeline.py v1.0's
      _process_one_hit (renamed write_bulk_hit, now public since it
      crosses a file boundary). No logic changed in the split.
"""
from __future__ import annotations

import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import BULK_WINDOW_LENGTH  # noqa: E402
from domain.bulk_labeler import compute_bulk_forward_labels  # noqa: E402
from domain.bulk_windowing import BulkDetectionHit  # noqa: E402
from infrastructure.research_catalog_io import (  # noqa: E402
    get_feature_set_id,
    get_or_create_symbol_with_sector,
    insert_forward_labels_batch,
    insert_pattern_bars_batch,
    insert_pattern_instance,
    insert_source_file,
    research_catalog_checkout,
    research_connection,
    verify_and_promote_research,
)
from schemas_bulk import (  # noqa: E402
    BulkDataOriginType,
    BulkForwardLabelRecord,
    BulkPatternInstanceRecord,
    BulkSourceFileRecord,
)

logger = logging.getLogger(__name__)

_FEATURE_VERSION = "bulk_scan_v1"


def write_bulk_hit(
    hit: BulkDetectionHit,
    bars: list,
    symbol: str,
    sector: str | None,
    source_filename: str,
    window_years: int,
    is_intelliscan_export: bool,
    master_db: Path,
    temp_db: Path,
) -> bool:
    """Slices the detection window ending at hit.bar_index, computes
    forward labels, and writes one pattern_instance end-to-end via the
    Lock + Temp-DB + Atomic Move protocol. Returns True on success."""
    window_start = hit.bar_index - BULK_WINDOW_LENGTH + 1
    if window_start < 0:
        logger.warning(
            "skip hit at %s: window_start %d < 0 (insufficient pre-history)",
            hit.anchor_date, window_start,
        )
        return False
    window_bars = bars[window_start: hit.bar_index + 1]

    try:
        labels = compute_bulk_forward_labels(bars, hit.anchor_date)
    except ValueError as e:
        logger.warning("skip hit at %s: %s", hit.anchor_date, e)
        return False

    shutil.copy2(master_db, temp_db)
    with research_connection(temp_db) as conn:
        pre_counts = research_catalog_checkout(conn)
        symbol_existed = conn.execute(
            "SELECT 1 FROM symbols WHERE ticker = ?", (symbol,)
        ).fetchone() is not None
        symbol_id = get_or_create_symbol_with_sector(conn, symbol, sector)
        feature_set_id = get_feature_set_id(conn, _FEATURE_VERSION)
        source_file_existed = conn.execute(
            "SELECT 1 FROM source_files WHERE filename = ?", (source_filename,)
        ).fetchone() is not None
        try:
            source_file_id = insert_source_file(conn, BulkSourceFileRecord(
                filename=source_filename,
                symbol_id=symbol_id,
                imported_at=datetime.now(),
                row_count=len(bars),
                window_years=window_years,
                is_intelliscan_export=is_intelliscan_export,
            ))
        except ValueError:
            # source_file already ingested from an earlier hit in this
            # same file -- reuse the existing row rather than treat as
            # an error (one file produces many hits, one source_file row).
            row = conn.execute(
                "SELECT source_file_id FROM source_files WHERE filename = ?",
                (source_filename,),
            ).fetchone()
            source_file_id = row[0]

        pattern_instance_id = insert_pattern_instance(conn, BulkPatternInstanceRecord(
            symbol_id=symbol_id,
            source_file_id=source_file_id,
            feature_set_id=feature_set_id,
            anchor_date=hit.anchor_date,
            window_length=len(window_bars),
            data_origin_type=BulkDataOriginType.BULK_SCAN,
            detection_tier=hit.tier,
        ))
        n_bars = insert_pattern_bars_batch(
            conn, pattern_instance_id, window_bars, hit.resistance_level
        )
        label_records = [
            BulkForwardLabelRecord(
                pattern_instance_id=pattern_instance_id,
                horizon_days=lbl.horizon_days,
                future_date=lbl.future_date,
                return_pct=lbl.return_pct,
                is_profitable=lbl.is_profitable,
                significant_move_15=lbl.significant_move_15,
            )
            for lbl in labels
        ]
        n_labels = insert_forward_labels_batch(conn, pattern_instance_id, label_records)

    expected_delta = {
        "symbols": 0 if symbol_existed else 1,
        "source_files": 0 if source_file_existed else 1,
        "feature_sets": 0,
        "pattern_instances": 1, "pattern_bars": n_bars,
        "pattern_features": 0, "forward_labels": n_labels,
    }
    result = verify_and_promote_research(temp_db, master_db, expected_delta, pre_counts)
    if not result.passed:
        logger.error("hit at %s REJECTED: %s", hit.anchor_date, result.failures)
        return False
    return True
