"""
FILE: infrastructure/catalog_merge_io.py
VERSION: 1.1
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Per-pattern merge logic for WO-P300-E2.003: converts one STRICT-tier
    research-catalog (bulk_research.db) pattern into the live catalog's
    schema shape and inserts it, reusing catalog_writer.py's existing
    insert functions -- no new write primitives, only a new caller that
    feeds them bulk-sourced, reframed data.

    Three real field-shape conversions happen here (verified against the
    actual manifests + schemas before writing, not assumed):
      - Normalized columns (close_pct_from_anchor, range_pct, etc.) are
        computed via domain/normalization.normalize_window against the
        bulk window's raw bars -- duck-typed (normalize_bar only reads
        attributes VPBarRaw and BulkBarRaw both have: OHLCV, stdiff/
        mtdiff/ltdiff, pred_high/pred_low/pred_range).
      - bar_offset is reindexed from bulk's 0..len-1 ascending to the
        live convention (0 = anchor/last bar, negative = setup bars
        before it) -- bulk_hit_writer.py already slices the window
        ENDING at the detection day, so the anchor framing itself was
        already correct; only the stored offset numbering needed fixing.
      - neural_index is populated from bulk.neural_x_max, NOT bulk's own
        neural_index field -- confirmed via both ingest manifests that
        this is the SAME VP export column (NeuralXMax) under different
        field names in the two schemas, not a data gap.
      - triple_cross_short/medium/long are zero-filled (this project's
        established pre-backfill-zero convention, M-072/M-077 family) --
        WO-P300-E2.001 Phase 0 verified the bulk export renders this
        VP column as a price level while the live export renders the
        same-named column as a small signed diff; no safe conversion
        formula exists between the two, and neither field is read by
        SIMILARITY_FEATURES or any decision-path logic, so a documented
        zero-fill (not a guessed value) is the honest choice.

    Dedup (WO-P300-E2.003 decision 4): a bulk pattern is skipped, not
    inserted, if the destination connection already has a PATTERN_IDENT
    or BULK_SCAN row for the same ticker + anchor_date.

CHANGELOG:
    - 2026-07-20 v1.1 (WFG/PLTR/BOIL/RRC PATTERN_IDENT-doubles cleanup):
      _pattern_already_exists() now delegates to the shared catalog_
      writer.pattern_exists_for_ticker_anchor() instead of running its
      own copy of the query -- same behavior, single implementation.
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.003 file #4 of 7).
"""
from __future__ import annotations

import sqlite3
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain.normalization import normalize_window  # noqa: E402
from infrastructure.catalog_writer import (  # noqa: E402
    get_or_create_symbol,
    insert_forward_labels_batch,
    insert_pattern_bars_batch,
    insert_pattern_instance,
    insert_source_file,
    pattern_exists_for_ticker_anchor,
)
from schemas import (  # noqa: E402
    DataOriginType,
    ForwardLabelRecord,
    PatternBarRecord,
    PatternInstanceRecord,
    SourceFileRecord,
)

# Zero-fill for the one genuinely unconvertible field family -- see module
# docstring. Not read by any decision-path logic (confirmed absent from
# config.SIMILARITY_FEATURES).
_TRIPLE_CROSS_ZERO_FILL = 0.0


@dataclass(frozen=True)
class RawBulkBar:
    """Duck-typed bar shape for normalize_window -- exposes exactly the
    attributes normalize_bar() reads (OHLCV + stdiff/mtdiff/ltdiff +
    pred_high/pred_low/pred_range), regardless of which Pydantic model
    (VPBarRaw or BulkBarRaw) the caller's real data came from. Public --
    application/catalog_merge_pipeline.py constructs these directly from
    research-catalog rows before calling merge_one_pattern."""
    bar_date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    stdiff: float
    mtdiff: float
    ltdiff: float
    pred_high: float
    pred_low: float
    pred_range: float
    williams_emai: float
    psi: float
    neural_x_max: float


@dataclass
class MergeSummary:
    inserted_count: int = 0
    skipped_duplicate_count: int = 0
    symbols_touched: set[str] = None

    def __post_init__(self):
        if self.symbols_touched is None:
            self.symbols_touched = set()


def ensure_feature_set(
    conn: sqlite3.Connection, feature_version: str, description: str
) -> int:
    """Get-or-create against the live catalog's feature_sets table
    (WO-P300-E2.003 decision 5 -- bulk_scan_v1 gets its own row, never
    reuses baseline_v1). Public -- called once per pipeline run by
    application/catalog_merge_pipeline.py before the merge loop starts."""
    row = conn.execute(
        "SELECT feature_set_id FROM feature_sets WHERE feature_version = ?",
        (feature_version,),
    ).fetchone()
    if row is not None:
        return row[0]
    cursor = conn.execute(
        "INSERT INTO feature_sets (feature_version, description, created_at) "
        "VALUES (?, ?, datetime('now'))",
        (feature_version, description),
    )
    return cursor.lastrowid


def _get_or_create_bulk_source_file(
    conn: sqlite3.Connection, filename: str, symbol_id: int,
    imported_at: datetime, row_count: int,
) -> int:
    """Get-or-create against source_files. catalog_writer.insert_source_file
    raises on a duplicate filename by design (EC-023) -- correct for live
    Pipeline A ingest, wrong here, since multiple merged patterns from the
    same symbol legitimately share one bulk source file."""
    row = conn.execute(
        "SELECT source_file_id FROM source_files WHERE filename = ?", (filename,)
    ).fetchone()
    if row is not None:
        return row[0]
    return insert_source_file(conn, SourceFileRecord(
        filename=filename, symbol_id=symbol_id,
        imported_at=imported_at, row_count=row_count,
    ))


def _pattern_already_exists(
    conn: sqlite3.Connection, ticker: str, anchor_date: date
) -> bool:
    """WO-P300-E2.003 decision 4: exact symbol+anchor_date dedup. Thin
    wrapper around the shared catalog_writer.pattern_exists_for_ticker_
    anchor (lifted there 2026-07-20, same WFG/PLTR/BOIL/RRC cleanup that
    added the matching guard to Pipeline A) -- kept local so this file's
    own call site (merge_one_pattern) needs no change."""
    return pattern_exists_for_ticker_anchor(conn, ticker, anchor_date)


def _build_bar_records(
    pattern_instance_id: int, raw_bars: list[RawBulkBar],
) -> list[PatternBarRecord]:
    """Builds all PatternBarRecord rows for one pattern: normalizes the
    window, reindexes bar_offset to the live convention, maps
    neural_index from neural_x_max, zero-fills triple_cross. Split out
    of merge_one_pattern to stay under the 50-line/function guideline."""
    normalized = normalize_window(raw_bars)  # anchor defaults to raw_bars[-1]
    n = len(raw_bars)
    return [
        PatternBarRecord(
            pattern_instance_id=pattern_instance_id,
            bar_offset=i - (n - 1),  # reindex: last bar -> 0, first -> -(n-1)
            bar_date=raw_bars[i].bar_date,
            open=raw_bars[i].open, high=raw_bars[i].high,
            low=raw_bars[i].low, close=raw_bars[i].close,
            volume=raw_bars[i].volume,
            stdiff=raw_bars[i].stdiff, mtdiff=raw_bars[i].mtdiff,
            ltdiff=raw_bars[i].ltdiff,
            pred_high=raw_bars[i].pred_high, pred_low=raw_bars[i].pred_low,
            pred_range=raw_bars[i].pred_range,
            williams_emai=raw_bars[i].williams_emai, psi=raw_bars[i].psi,
            neural_index=raw_bars[i].neural_x_max,  # see module docstring
            triple_cross_short=_TRIPLE_CROSS_ZERO_FILL,
            triple_cross_medium=_TRIPLE_CROSS_ZERO_FILL,
            triple_cross_long=_TRIPLE_CROSS_ZERO_FILL,
            close_pct_from_anchor=normalized[i].close_pct_from_anchor,
            range_pct=normalized[i].range_pct, body_pct=normalized[i].body_pct,
            volume_zscore=normalized[i].volume_zscore,
            stdiff_pct=normalized[i].stdiff_pct, mtdiff_pct=normalized[i].mtdiff_pct,
            ltdiff_pct=normalized[i].ltdiff_pct,
            pred_high_pct=normalized[i].pred_high_pct,
            pred_low_pct=normalized[i].pred_low_pct,
            pred_range_pct=normalized[i].pred_range_pct,
        )
        for i in range(n)
    ]


def merge_one_pattern(
    live_conn: sqlite3.Connection,
    ticker: str,
    source_filename: str,
    source_imported_at: datetime,
    source_row_count: int,
    anchor_date: date,
    raw_bars: list[RawBulkBar],
    forward_labels: list[tuple[int, date, float, bool]],
    feature_set_id: int,
) -> int | None:
    """Merge one bulk STRICT pattern into live_conn. Returns the new
    pattern_instance_id, or None if skipped as a duplicate (decision 4).
    raw_bars must be sorted ascending (bulk convention); forward_labels
    is a list of (horizon_days, future_date, return_pct, is_profitable).
    """
    if _pattern_already_exists(live_conn, ticker, anchor_date):
        return None

    symbol_id = get_or_create_symbol(live_conn, ticker)
    source_file_id = _get_or_create_bulk_source_file(
        live_conn, source_filename, symbol_id, source_imported_at, source_row_count,
    )

    pattern_instance_id = insert_pattern_instance(live_conn, PatternInstanceRecord(
        symbol_id=symbol_id, source_file_id=source_file_id,
        feature_set_id=feature_set_id, anchor_date=anchor_date,
        window_length=len(raw_bars), data_origin_type=DataOriginType.BULK_SCAN,
    ))

    bar_records = _build_bar_records(pattern_instance_id, raw_bars)
    insert_pattern_bars_batch(live_conn, pattern_instance_id, bar_records)

    label_records = [
        ForwardLabelRecord(
            pattern_instance_id=pattern_instance_id,
            horizon_days=h, future_date=fd, return_pct=rp, is_profitable=ip,
        )
        for h, fd, rp, ip in forward_labels
    ]
    insert_forward_labels_batch(live_conn, pattern_instance_id, label_records)

    return pattern_instance_id
