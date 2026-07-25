"""
FILE: application/ingest_mined_pipeline.py
VERSION: 1.5
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: application
DESCRIPTION:
    Phase 2 orchestrator for WO-P300-E3.002: reads an operator-approved
    mine_candidates.csv, re-reads each symbol's source grid file fresh
    from disk, audits via domain/mine_audit.py, and inserts audit-
    passed rows into a STAGING COPY of the live catalog -- never a
    direct write to real catalog.db. Runs M-079's walk-forward eval
    before returning; promote_staging_to_live() (catalog_merge_
    pipeline.py) is a separate call. Density decision (2026-07-14):
    BOIL/ASTS/MSTR/ARDX/CRK rows NOT filtered -- document-only.

    M-079 pre/post eval: "pre" (live) hits infrastructure/eval_io.py's
    cache when unchanged since last promote (v1.3, E4.003); "post"
    (staging) scores ONLY newly-inserted pids, reusing the cached pre-
    batch for the rest (application/incremental_post_batch.py, v1.4,
    E4.004), falling back to a full re-score if the guardrail fires.

CHANGELOG:
    - 2026-07-20 v1.5 (E4.002, M-095): get_latest_catalog() call site -> get_latest_catalog_path().
    - 2026-07-17 v1.4 (E4.004): new_pattern_ids added; post-batch now
      incremental via run_incremental_post_batch(), not a full re-score.
    - 2026-07-16 v1.3 (E4.003, M-096): pre-batch cache + parallel flag.
    - Pre-v1.3: v1.2 (M-095 str-vs-Path), v1.1 (M-093), v1.0 -- see lessons.md.
"""
from __future__ import annotations

import logging
import shutil
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import (  # noqa: E402
    BULK_FEATURE_VERSION, BULK_WINDOW_LENGTH, DATA_BULK_MINE,
    EVAL_PARALLEL_ENABLED, EVAL_PARALLEL_WORKERS, MINE_MIN_ANCHOR_DATE,
)
from domain.bulk_labeler import compute_bulk_forward_labels, find_anchor_index  # noqa: E402
from domain.eval_scoring import (  # noqa: E402
    estimate_full_rescore_seconds, run_walk_forward,
)
from domain.mine_audit import AuditResult, audit_symbol  # noqa: E402
from infrastructure.bulk_grid_reader import parse_bulk_file  # noqa: E402
from infrastructure.catalog_merge_io import (  # noqa: E402
    RawBulkBar, ensure_feature_set, merge_one_pattern,
)
from application.incremental_post_batch import run_incremental_post_batch  # noqa: E402
from application.reconstruct_pre_batch import (  # noqa: E402
    TopkCacheReconstructionNotViable, reconstruct_pre_batch_from_topk_cache,
)
from infrastructure.eval_io import (  # noqa: E402
    load_full_catalog, read_cached_walk_forward, write_walk_forward_cache,
    write_walk_forward_report,
)
from infrastructure.mine_report_writer import (  # noqa: E402
    MineCandidateRow, read_approved_candidates_csv,
)
from schemas_bulk import BulkBarRaw  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog_path  # noqa: E402

logger = logging.getLogger(__name__)


class FullRescoreConfirmationRequired(Exception):
    """Raised by _run_pre_batch() on a cold M-079 pre-cache -- WO-P300-
    E5.004: a full serial rescore never runs automatically. Caller (cli.py)
    catches this, prints the estimate, and exits non-zero rather than
    proceeding -- re-invoke with --confirm-full-rescore once the wait is
    a conscious choice, not a surprise."""

    def __init__(
        self, corpus_size: int, estimated_seconds: float, catalog_path,
    ) -> None:
        self.corpus_size = corpus_size
        self.estimated_seconds = estimated_seconds
        self.catalog_path = catalog_path
        hours = estimated_seconds / 3600.0
        super().__init__(
            f"Cold M-079 pre-cache for {catalog_path}: a full serial "
            f"rescore of {corpus_size} patterns is required, estimated "
            f"{hours:.1f} hours (WO-P300-E5.004 estimate, see config.py "
            f"WALK_FORWARD_SERIAL_MS_PER_PAIR). This does not run "
            f"automatically. Re-run with --confirm-full-rescore once "
            f"you have decided to accept that wait."
        )


@dataclass
class IngestMinedResult:
    live_catalog_path: Path
    staging_path: Path
    inserted_count: int = 0
    skipped_duplicate_count: int = 0
    audit_failed: list[AuditResult] = field(default_factory=list)
    symbols_touched: set[str] = field(default_factory=set)
    new_pattern_ids: set[int] = field(default_factory=set)
    pre_report_path: Path | None = None
    post_report_path: Path | None = None


def _load_symbol_bars(input_dir: Path) -> dict[str, tuple[list[BulkBarRaw], str]]:
    """Re-reads every *.xlsx in input_dir fresh from disk -- symbol ->
    (bars, source filename). Phase 2 never trusts Phase 1's in-memory
    result, only what's on disk right now (closes the stale-export-
    between-phases risk)."""
    out: dict[str, tuple[list[BulkBarRaw], str]] = {}
    files = sorted(input_dir.glob("*.xlsx")) if input_dir.exists() else []
    for xlsx_path in files:
        try:
            parsed = parse_bulk_file(xlsx_path)
        except Exception as exc:
            logger.error("Re-read failed for %s: %s", xlsx_path.name, exc)
            continue
        out[parsed.metadata.symbol] = (parsed.bars, xlsx_path.name)
    return out


def _existing_keys_for_symbol(
    conn: sqlite3.Connection, ticker: str
) -> set[tuple[str, date]]:
    """Real catalog-collision keys for one symbol, read from the
    staging connection (equivalent to live at this point). Not
    exhaustive against in-batch inserts earlier in this run -- fine,
    merge_one_pattern's own check is the final guard at insert time."""
    rows = conn.execute(
        "SELECT pi.anchor_date FROM pattern_instances pi "
        "JOIN symbols s ON s.symbol_id = pi.symbol_id WHERE s.ticker = ?",
        (ticker,),
    ).fetchall()
    return {(ticker, datetime.fromisoformat(r[0]).date()) for r in rows}


def _build_window_and_labels(
    bars: list[BulkBarRaw], anchor_date: date,
) -> tuple[list[RawBulkBar], list[tuple[int, date, float, bool]]]:
    """BULK_WINDOW_LENGTH-bar window ending at anchor_date + forward
    labels via bulk_labeler.py. Raises ValueError on insufficient
    pre/post-anchor history, or a window reaching before
    MINE_MIN_ANCHOR_DATE (M-093, backfilled bars fail gt=0 validation)
    -- caller treats both as an audit-adjacent skip, not a crash.
    """
    anchor_idx = find_anchor_index(bars, anchor_date)
    window_start = anchor_idx - BULK_WINDOW_LENGTH + 1
    if window_start < 0:
        raise ValueError(f"insufficient pre-anchor history at {anchor_date}")
    window_bars = bars[window_start: anchor_idx + 1]
    if window_bars[0].bar_date < MINE_MIN_ANCHOR_DATE:
        raise ValueError(
            f"window for anchor {anchor_date} reaches back to "
            f"{window_bars[0].bar_date}, before MINE_MIN_ANCHOR_DATE "
            f"({MINE_MIN_ANCHOR_DATE}) -- backfilled bars have 0.0 "
            f"pred_high/pred_low placeholders"
        )

    raw_bars = [
        RawBulkBar(
            bar_date=b.bar_date, open=b.open, high=b.high, low=b.low,
            close=b.close, volume=b.volume, stdiff=b.stdiff, mtdiff=b.mtdiff,
            ltdiff=b.ltdiff, pred_high=b.pred_high, pred_low=b.pred_low,
            pred_range=b.pred_range, williams_emai=b.williams_emai,
            psi=b.psi, neural_x_max=b.neural_x_max,
        )
        for b in window_bars
    ]
    labels = compute_bulk_forward_labels(bars, anchor_date)
    label_tuples = [
        (lbl.horizon_days, lbl.future_date, lbl.return_pct, lbl.is_profitable)
        for lbl in labels
    ]
    return raw_bars, label_tuples


def _ingest_symbol(
    conn: sqlite3.Connection,
    symbol: str,
    bars: list[BulkBarRaw],
    source_filename: str,
    claimed_rows: list[MineCandidateRow],
    feature_set_id: int,
) -> tuple[int, int, list[AuditResult], set[int]]:
    """Audits then inserts one symbol's approved rows. Returns
    (inserted_count, skipped_duplicate_count, audit_failed, new_ids)."""
    existing_keys = _existing_keys_for_symbol(conn, symbol)
    results = audit_symbol(symbol, bars, claimed_rows, existing_keys)

    inserted = 0
    skipped_dup = 0
    failed: list[AuditResult] = []
    new_ids: set[int] = set()
    for result, row in zip(results, claimed_rows):
        if not result.passed:
            failed.append(result)
            continue
        try:
            raw_bars, label_tuples = _build_window_and_labels(bars, row.anchor_date)
        except ValueError as exc:
            failed.append(AuditResult(
                symbol=symbol, anchor_date=row.anchor_date,
                pattern_class=row.pattern_class, passed=False, reasons=[str(exc)],
            ))
            continue

        new_id = merge_one_pattern(
            conn, symbol, source_filename, datetime.now(), len(bars),
            row.anchor_date, raw_bars, label_tuples, feature_set_id,
        )
        if new_id is None:
            skipped_dup += 1
        else:
            inserted += 1
            new_ids.add(new_id)
    return inserted, skipped_dup, failed, new_ids


def _ingest_all_symbols(
    conn: sqlite3.Connection,
    by_symbol: dict[str, list[MineCandidateRow]],
    symbol_bars: dict[str, tuple[list[BulkBarRaw], str]],
    feature_set_id: int,
    result: IngestMinedResult,
) -> None:
    """Loops every approved symbol against the staging connection,
    mutating result in place (kept under the 50-line/function limit)."""
    for symbol, claimed_rows in by_symbol.items():
        if symbol not in symbol_bars:
            logger.error(
                "No source file re-read for approved symbol %s -- "
                "all %d row(s) skipped", symbol, len(claimed_rows),
            )
            result.audit_failed.extend(
                AuditResult(
                    symbol=symbol, anchor_date=r.anchor_date,
                    pattern_class=r.pattern_class, passed=False,
                    reasons=["source file not found in input_dir re-read"],
                )
                for r in claimed_rows
            )
            continue
        bars, filename = symbol_bars[symbol]
        ins, dup, failed, new_ids = _ingest_symbol(
            conn, symbol, bars, filename, claimed_rows, feature_set_id,
        )
        result.inserted_count += ins
        result.skipped_duplicate_count += dup
        result.audit_failed.extend(failed)
        result.new_pattern_ids |= new_ids
        if ins > 0:
            result.symbols_touched.add(symbol)


def _run_pre_batch(
    resolved_live_path: Path,
    confirm_full_rescore: bool = False,
):
    """M-079 "pre" batch. Cache hit skips straight to the stored
    WalkForwardBatch. A miss is a full, uncached, serial rescore --
    WO-P300-E5.004: never runs automatically. Estimates wall time via
    domain.eval_scoring.estimate_full_rescore_seconds() and requires
    confirm_full_rescore=True (threaded from --confirm-full-rescore,
    cli_commands/bulk_promote.py) before proceeding -- otherwise raises
    FullRescoreConfirmationRequired with the estimate in the message.
    """
    cached = read_cached_walk_forward(resolved_live_path)
    if cached is not None:
        logger.info(
            "M-079 pre-batch: cache hit for %s (%d patterns) -- skipping "
            "recompute", resolved_live_path, cached.n_patterns,
        )
        return cached

    # WO-P300-E5.004 Part A: try reconstructing from topk_cache first --
    # skips the expensive DTW pass entirely when topk_cache is viable.
    # Falls through to the full rescore below only if reconstruction
    # itself cannot proceed (topk_cache table missing entirely). Real
    # per-pattern gaps are handled inside reconstruct_pre_batch_from_
    # topk_cache() itself, not here.
    try:
        pre_batch = reconstruct_pre_batch_from_topk_cache(resolved_live_path)
        logger.info(
            "M-079 pre-batch: reconstructed from topk_cache for %s "
            "(%d patterns, WO-P300-E5.004 Part A) -- skipped full DTW "
            "rescore", resolved_live_path, pre_batch.n_patterns,
        )
        write_walk_forward_cache(pre_batch, resolved_live_path)
        return pre_batch
    except TopkCacheReconstructionNotViable as exc:
        logger.warning(
            "M-079 pre-batch: topk_cache reconstruction not viable for "
            "%s (%s) -- falling through to the confirm-gated full DTW "
            "rescore", resolved_live_path, exc,
        )
    pre_path, pre_meta, pre_win, pre_lab = load_full_catalog(resolved_live_path)
    corpus_size = len(pre_meta)
    estimated_seconds = estimate_full_rescore_seconds(corpus_size)
    if not confirm_full_rescore:
        raise FullRescoreConfirmationRequired(
            corpus_size=corpus_size,
            estimated_seconds=estimated_seconds,
            catalog_path=resolved_live_path,
        )
    logger.warning(
        "M-079 pre-batch: cache MISS for %s -- running full serial "
        "rescore, %d patterns, estimated %.1f hours (WO-P300-E5.004, "
        "confirmed by --confirm-full-rescore)",
        resolved_live_path, corpus_size, estimated_seconds / 3600.0,
    )
    pre_batch = run_walk_forward(
        pre_path, pre_meta, pre_win, pre_lab,
        parallel=EVAL_PARALLEL_ENABLED, max_workers=EVAL_PARALLEL_WORKERS,
    )
    write_walk_forward_cache(pre_batch, resolved_live_path)
    return pre_batch


def run_ingest_mined(
    csv_path: Path,
    staging_path: Path,
    live_catalog_path: Path | None = None,
    input_dir: Path = DATA_BULK_MINE,
    confirm_full_rescore: bool = False,
) -> IngestMinedResult:
    """Phase 2 end-to-end: approved CSV -> audit gate -> staging insert
    -> M-079 staging walk-forward eval. Never writes to the real live
    catalog.db -- promote_staging_to_live() (catalog_merge_pipeline.py)
    is a separate, explicit call.

    confirm_full_rescore: threaded to _run_pre_batch() -- WO-P300-E5.004.
    A cold M-079 pre-cache raises FullRescoreConfirmationRequired unless
    this is True; see that function's docstring.
    """
    resolved_live_path = (
        Path(live_catalog_path) if live_catalog_path else get_latest_catalog_path()
    )
    shutil.copy2(resolved_live_path, staging_path)

    approved = read_approved_candidates_csv(csv_path)
    by_symbol: dict[str, list[MineCandidateRow]] = {}
    for row in approved:
        by_symbol.setdefault(row.symbol, []).append(row)

    symbol_bars = _load_symbol_bars(input_dir)
    result = IngestMinedResult(
        live_catalog_path=resolved_live_path, staging_path=staging_path,
    )

    with connection_context(str(staging_path)) as conn:
        feature_set_id = ensure_feature_set(
            conn, BULK_FEATURE_VERSION,
            "Outcome-first mined patterns, merged via WO-P300-E3.002 Phase 2.",
        )
        _ingest_all_symbols(conn, by_symbol, symbol_bars, feature_set_id, result)

    pre_batch = _run_pre_batch(resolved_live_path, confirm_full_rescore)
    result.pre_report_path = write_walk_forward_report(pre_batch)

    post_path, post_meta, post_win, post_lab = load_full_catalog(staging_path)
    post_batch = run_incremental_post_batch(
        post_path, post_meta, post_win, post_lab,
        result.new_pattern_ids, pre_batch,
    )
    result.post_report_path = write_walk_forward_report(post_batch)
    logger.info(
        'Ingest-mined complete: %d inserted, %d skipped (duplicate), '
        '%d audit-failed. Pre n_patterns=%d, post n_patterns=%d.',
        result.inserted_count,
        result.skipped_duplicate_count,
        len(result.audit_failed),
        pre_batch.n_patterns,
        post_batch.n_patterns,
    )
    return result
