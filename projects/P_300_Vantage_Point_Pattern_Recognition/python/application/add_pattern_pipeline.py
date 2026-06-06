"""
FILE: add_pattern_pipeline.py
VERSION: 1.0
DATE: 2026-05-15
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Pipeline A orchestrator. End-to-end ingest of one VantagePoint Pattern
    XLSX into the catalog. Pure orchestration — calls infrastructure,
    domain, and config modules; contains no business logic of its own.

    Flow (architecture §8.2):

        1. Parse XLSX via vp_xlsx_reader -> PatternFileParse
        2. Locate launch bar (filename's pattern_start_date)
        3. Slice setup window: window_length bars ending at launch
           (launch = offset 0 = anchor; oldest setup = offset -19)
        4. Normalize via domain.normalization (anchor defaults to bars[-1])
        5. Compute forward labels via domain.labeler at horizons (5/7/10/15/20)
        6. shutil.copy2(master, temp)  — temp now mirrors master
        7. Open temp via db_connect (FK PRAGMA on)
        8. catalog_checkout -> pre_counts
        9. Inserts in FK order (symbol, source_file, pattern_instance,
           pattern_bars batch, forward_labels batch)
       10. Context commits on clean exit; rolls back on exception
       11. verify_and_promote(temp, master, expected_delta, pre_counts)
           runs hollow-record scan + delta verification + atomic move

    Stage 4 POC scope:
        - One pattern per call
        - LAUNCH-anchor framing
        - data_origin_type = PATTERN_IDENT
        - pattern_features deferred (D2 scope trim)
        - Batch / Stage 5 multi-pattern orchestration comes later

CHANGELOG:
    - 2026-05-15 v1.0: Stage 4 file #9 of plan. End-to-end ingest entrypoint.
"""
from __future__ import annotations

import logging
import shutil
import sys
from datetime import date, datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    DEFAULT_FEATURE_VERSION,
    MAX_WINDOW_LENGTH,
    MIN_WINDOW_LENGTH,
    TEMP_WORKING_DB,
)
from domain.labeler import ForwardLabel, compute_forward_labels  # noqa: E402
from domain.normalization import NormalizedValues, normalize_window  # noqa: E402
from infrastructure.catalog_writer import (  # noqa: E402
    catalog_checkout,
    get_feature_set_id,
    get_or_create_symbol,
    insert_forward_labels_batch,
    insert_pattern_bars_batch,
    insert_pattern_instance,
    insert_source_file,
)
from infrastructure.verify_ingestion import VerificationResult, verify_and_promote  # noqa: E402
from infrastructure.vp_xlsx_reader import parse_pattern_file  # noqa: E402
from schemas import (  # noqa: E402
    DataOriginType,
    ForwardLabelRecord,
    PatternBarRecord,
    PatternInstanceRecord,
    SourceFileRecord,
    VPBarRaw,
)
from utilities.db_connect import connection_context  # noqa: E402

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Window slicing
# ─────────────────────────────────────────────────────────────────────────────

def _find_launch_index(bars: list[VPBarRaw], launch_date: date) -> int:
    """Locate launch_date in an ascending-sorted bar list."""
    for i, b in enumerate(bars):
        if b.bar_date == launch_date:
            return i
    raise ValueError(
        f"launch_date {launch_date} not found in bars "
        f"(range {bars[0].bar_date} to {bars[-1].bar_date}, n={len(bars)})"
    )


def _slice_setup_window(
    bars: list[VPBarRaw], launch_idx: int, window_length: int
) -> list[VPBarRaw]:
    """Return window_length bars ENDING at launch_idx (inclusive).
    setup_bars[-1] is the launch bar (offset 0); setup_bars[0] is offset
    -(window_length - 1). Raises if there's insufficient pre-launch history."""
    if launch_idx < window_length - 1:
        raise ValueError(
            f"insufficient setup history: need {window_length - 1} bars "
            f"before launch_idx={launch_idx}, have {launch_idx}"
        )
    return bars[launch_idx - (window_length - 1): launch_idx + 1]


# ─────────────────────────────────────────────────────────────────────────────
# Record builders (called after pattern_instance_id is known)
# ─────────────────────────────────────────────────────────────────────────────

def _build_pattern_bar_records(
    setup_bars: list[VPBarRaw],
    normalized: list[NormalizedValues],
    pattern_instance_id: int,
    window_length: int,
) -> list[PatternBarRecord]:
    """Zip raw bars + normalized values into PatternBarRecord list.
    Offsets: i=0 -> -(window_length-1) (oldest), i=window_length-1 -> 0 (launch)."""
    records: list[PatternBarRecord] = []
    for i, (bar, norm) in enumerate(zip(setup_bars, normalized)):
        offset = i - (window_length - 1)
        records.append(PatternBarRecord(
            pattern_instance_id=pattern_instance_id,
            bar_offset=offset,
            bar_date=bar.bar_date,
            open=bar.open, high=bar.high, low=bar.low, close=bar.close,
            volume=bar.volume,
            stdiff=bar.stdiff, mtdiff=bar.mtdiff, ltdiff=bar.ltdiff,
            pred_high=bar.pred_high, pred_low=bar.pred_low,
            pred_range=bar.pred_range,
            williams_emai=bar.williams_emai, psi=bar.psi,
            neural_index=bar.neural_index,
            triple_cross_short=bar.triple_cross_short,
            triple_cross_medium=bar.triple_cross_medium,
            triple_cross_long=bar.triple_cross_long,
            close_pct_from_anchor=norm.close_pct_from_anchor,
            range_pct=norm.range_pct,
            body_pct=norm.body_pct,
            volume_zscore=norm.volume_zscore,
            stdiff_pct=norm.stdiff_pct, mtdiff_pct=norm.mtdiff_pct,
            ltdiff_pct=norm.ltdiff_pct,
            pred_high_pct=norm.pred_high_pct,
            pred_low_pct=norm.pred_low_pct,
            pred_range_pct=norm.pred_range_pct,
        ))
    return records


def _build_forward_label_records(
    forward_labels: list[ForwardLabel], pattern_instance_id: int
) -> list[ForwardLabelRecord]:
    return [
        ForwardLabelRecord(
            pattern_instance_id=pattern_instance_id,
            horizon_days=fl.horizon_days,
            future_date=fl.future_date,
            return_pct=fl.return_pct,
            is_profitable=fl.is_profitable,
        )
        for fl in forward_labels
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers for delta-tracking
# ─────────────────────────────────────────────────────────────────────────────

def _check_symbol_is_new(conn, ticker: str) -> bool:
    """Pre-write probe: True if ticker is not yet in symbols table."""
    row = conn.execute(
        "SELECT 1 FROM symbols WHERE ticker = ?", (ticker,)
    ).fetchone()
    return row is None


def _compute_expected_delta(
    symbol_was_new: bool, window_length: int, n_labels: int
) -> dict[str, int]:
    """Per-table expected row delta for one Pipeline A ingest."""
    return {
        "symbols": 1 if symbol_was_new else 0,
        "source_files": 1,
        "feature_sets": 0,
        "pattern_instances": 1,
        "pattern_bars": window_length,
        "pattern_features": 0,
        "forward_labels": n_labels,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def ingest_pattern_file(
    xlsx_path: Path,
    master_db_path: Path,
    temp_db_path: Path = TEMP_WORKING_DB,
    window_length: int = MAX_WINDOW_LENGTH,
) -> VerificationResult:
    """End-to-end Pipeline A ingest of one VP Pattern XLSX. Returns the
    VerificationResult from verify_and_promote — `passed=True` means
    master was atomically replaced; `passed=False` means temp DB is in
    place for forensic inspection and master is untouched."""
    if not (MIN_WINDOW_LENGTH <= window_length <= MAX_WINDOW_LENGTH):
        raise ValueError(
            f"window_length must be in {MIN_WINDOW_LENGTH}..{MAX_WINDOW_LENGTH}"
        )

    logger.info("Ingesting %s", xlsx_path.name)
    parse = parse_pattern_file(xlsx_path)
    launch_date = parse.metadata.pattern_start_date
    launch_idx = _find_launch_index(parse.bars, launch_date)
    setup_bars = _slice_setup_window(parse.bars, launch_idx, window_length)
    logger.info(
        "launch=%s launch_idx=%d setup=[%s..%s] forward_horizon_max=%d",
        launch_date, launch_idx,
        setup_bars[0].bar_date, setup_bars[-1].bar_date, MAX_WINDOW_LENGTH,
    )

    normalized = normalize_window(setup_bars)
    forward_labels = compute_forward_labels(parse.bars, anchor_date=launch_date)
    logger.info(
        "normalized %d bars; computed %d forward labels",
        len(normalized), len(forward_labels),
    )

    shutil.copy2(master_db_path, temp_db_path)
    logger.info("temp DB seeded from master: %s", temp_db_path)

    with connection_context(catalog_path=str(temp_db_path)) as conn:
        pre_counts = catalog_checkout(conn)
        symbol_was_new = _check_symbol_is_new(conn, parse.metadata.symbol)

        symbol_id = get_or_create_symbol(conn, parse.metadata.symbol)
        feature_set_id = get_feature_set_id(conn, DEFAULT_FEATURE_VERSION)
        source_file_id = insert_source_file(conn, SourceFileRecord(
            filename=parse.metadata.filename,
            symbol_id=symbol_id,
            imported_at=datetime.now(),
            row_count=len(parse.bars),
        ))
        pattern_instance_id = insert_pattern_instance(conn, PatternInstanceRecord(
            symbol_id=symbol_id,
            source_file_id=source_file_id,
            feature_set_id=feature_set_id,
            anchor_date=launch_date,
            window_length=window_length,
            data_origin_type=DataOriginType.PATTERN_IDENT,
        ))

        bar_records = _build_pattern_bar_records(
            setup_bars, normalized, pattern_instance_id, window_length
        )
        label_records = _build_forward_label_records(
            forward_labels, pattern_instance_id
        )
        insert_pattern_bars_batch(conn, pattern_instance_id, bar_records)
        insert_forward_labels_batch(conn, pattern_instance_id, label_records)

        logger.info(
            "wrote pattern_instance_id=%d (symbol=%s symbol_id=%d, "
            "source_file_id=%d, %d bars, %d labels)",
            pattern_instance_id, parse.metadata.symbol, symbol_id,
            source_file_id, len(bar_records), len(label_records),
        )

    expected_delta = _compute_expected_delta(
        symbol_was_new, window_length, len(label_records)
    )
    return verify_and_promote(
        temp_db_path, master_db_path, expected_delta, pre_counts
    )
