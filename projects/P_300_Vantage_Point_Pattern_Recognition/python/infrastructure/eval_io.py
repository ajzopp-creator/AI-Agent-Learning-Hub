"""
FILE: eval_io.py
VERSION: 1.5
DATE: 2026-07-17
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    All I/O for the Stage 6 walk-forward eval loop.

    load_full_catalog() -- one round trip per bulk loader (M-012
    connection lifecycle via utilities/db_connect.py), returns every
    PATTERN_IDENT + BULK_SCAN pattern's metadata/windows/labels keyed
    by pattern_instance_id. Read-only -- no catalog writes anywhere in
    this module. catalog_path override (v1.3) supports staging-copy
    runs; BULK_SCAN inclusion is a no-op on the live catalog until a
    merge is promoted.

    write_walk_forward_report() -- renders a WalkForwardBatch as a
    tab-delimited, Excel-ready table to REPORTS_DIR/eval, created if
    absent. LONG format: one row per (pattern, horizon), not just
    chosen_horizon -- this is a verification tool for the matching/
    classification chain, not a live trading report. Ground-truth
    columns populate on the is_chosen_horizon row only. Filename
    carries a threshold-override tag (v1.2, e.g. "bz1.0") so reports
    from different gate settings never collide on disk.

    read_cached_walk_forward() / write_walk_forward_cache() (v1.4,
    E4.003) -- pre-batch memoization for run_ingest_mined's "pre"
    (live catalog) pass. Keyed on a content fingerprint (v1.5, M-099)
    -- row count + max pattern_instance_id + file size -- not mtime,
    so the daily dated-rollover copy (new filename, new mtime, same
    content) correctly hits instead of missing every morning. Cache
    is JSON via WalkForwardBatch's own Pydantic (de)serialization; a
    read failure is always a miss, never a crash -- callers always
    have the real run_walk_forward() fallback.

    No business logic here -- domain/eval_scoring.py owns the math.
    No orchestration -- application/ owns the call order, including
    the cache check itself.

CHANGELOG:
    - 2026-07-17 v1.5 (M-099): _cache_key() now fingerprints catalog
      content (row count + max pattern_instance_id + file size)
      instead of mtime -- the daily rollover copy (new filename, new
      mtime, byte-identical content) was defeating the cache every
      morning. Stem strips the <mmddyy> rollover prefix too, so the
      cache filename itself stays stable across the rename.
    - 2026-07-16 v1.4 (E4.003, M-096): pre-batch cache added.
    - Pre-v1.4: v1.3 catalog_path override + BULK_SCAN load, v1.1-1.2
      long-format report + threshold tag, v1.0 initial -- see
      tasks/lessons.md.
"""
from __future__ import annotations

import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import FORWARD_HORIZONS, MODELS_DIR, ORIGIN_BULK_SCAN, ORIGIN_PATTERN_IDENT, REPORTS_DIR  # noqa: E402
from infrastructure import catalog_reader  # noqa: E402
from infrastructure.catalog_reader import PatternMetadata  # noqa: E402
from schemas_eval import ThresholdOverrides, WalkForwardBatch  # noqa: E402
from schemas_pipeline_b import ForwardLabelLite, NormalizedBar  # noqa: E402
from utilities.db_connect import connection_context  # noqa: E402
from utilities.db_utils import get_latest_catalog  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s",
                     stream=sys.stdout)
logger = logging.getLogger(__name__)

EVAL_REPORTS_DIR: Path = REPORTS_DIR / "eval"
EVAL_CACHE_DIR: Path = MODELS_DIR / "eval_cache"

_REPORT_COLUMNS = (
    "pattern_instance_id", "symbol", "anchor_date", "corpus_size",
    "degenerate_corpus", "final_signal_class", "chosen_horizon",
    "horizon_days", "is_chosen_horizon", "n_matches", "win_rate",
    "z_score", "mean_return_pct", "std_return_pct",
    "certainty_equivalent", "actual_return_pct", "actual_is_profitable",
    "correctness",
)

# Override field -> short filename-tag prefix.
_TAG_PREFIXES = (
    ("buy_min_n", "bn"), ("buy_min_win_rate", "bwr"),
    ("buy_min_z_score", "bz"), ("watch_min_n", "wn"),
    ("watch_min_win_rate", "wwr"), ("watch_min_z_score", "wz"),
)


# ─────────────────────────────────────────────────────────────────────────────
# Catalog load
# ─────────────────────────────────────────────────────────────────────────────

def load_full_catalog(
    catalog_path: Path | str | None = None,
) -> tuple[
    str,
    dict[int, PatternMetadata],
    dict[int, list[NormalizedBar]],
    dict[int, dict[int, ForwardLabelLite]],
]:
    """Bulk-load every PATTERN_IDENT + BULK_SCAN pattern's metadata,
    normalized bars, and forward labels from the given catalog (or the
    active live catalog via get_latest_catalog() when None).

    catalog_path override + BULK_SCAN inclusion (WO-P300-E2.003) let
    this run against a staging merge copy and see merged rows; a
    no-op on the live catalog until a merge is promoted.

    Returns:
        (catalog_path, metadata_by_pid, windows_by_pid, labels_by_pid)
        -- catalog_path as str, all dicts keyed by pattern_instance_id.
    """
    resolved_path = Path(catalog_path) if catalog_path is not None else get_latest_catalog()
    with connection_context(resolved_path) as conn:
        all_pids = catalog_reader.get_all_pattern_ids(
            conn, origin_types=(ORIGIN_PATTERN_IDENT, ORIGIN_BULK_SCAN),
        )
        metadata = catalog_reader.bulk_load_pattern_metadata(conn, all_pids)
        windows = catalog_reader.bulk_load_normalized_windows(conn, all_pids)
        labels = catalog_reader.bulk_load_forward_labels(conn, all_pids)
    logger.info(
        "load_full_catalog: %d patterns loaded from %s",
        len(all_pids), resolved_path,
    )
    return str(resolved_path), metadata, windows, labels


# ─────────────────────────────────────────────────────────────────────────────
# Report write -- long format: one row per pattern per horizon
# ─────────────────────────────────────────────────────────────────────────────

def _override_tag(overrides: ThresholdOverrides | None) -> str:
    """Short filename tag for the threshold overrides used this run.
    "default" when overrides is None or every field is None; otherwise
    one segment per non-None field, e.g. ThresholdOverrides(
    buy_min_z_score=1.0) -> "bz1.0"."""
    if overrides is None:
        return "default"
    parts = [
        f"{prefix}{getattr(overrides, field)}"
        for field, prefix in _TAG_PREFIXES
        if getattr(overrides, field) is not None
    ]
    return "_".join(parts) if parts else "default"


def _row_for(result, horizon: int) -> str:
    """One tab-delimited row for one (pattern, horizon) pair.
    Ground-truth fields populate only on horizon == chosen_horizon
    (the only horizon with real ground truth); others render blank,
    not a fabricated value."""
    stats = result.per_horizon[horizon]
    is_chosen = horizon == result.chosen_horizon
    fields = [
        result.pattern_instance_id,
        result.symbol,
        result.anchor_date.isoformat(),
        result.corpus_size,
        result.degenerate_corpus,
        result.signal_class.value,
        result.chosen_horizon,
        horizon,
        is_chosen,
        stats.n_matches,
        f"{stats.win_rate:.4f}",
        f"{stats.z_score:.4f}",
        f"{stats.mean_return_pct:.4f}",
        f"{stats.std_return_pct:.4f}",
        "" if stats.certainty_equivalent is None else f"{stats.certainty_equivalent:.4f}",
        "" if not is_chosen or result.actual_return_pct is None else f"{result.actual_return_pct:.4f}",
        "" if not is_chosen or result.actual_is_profitable is None else result.actual_is_profitable,
        "" if not is_chosen or result.correctness is None else result.correctness,
    ]
    return "\t".join(str(f) for f in fields)


def write_walk_forward_report(
    batch: WalkForwardBatch,
    reports_dir: Path | None = None,
) -> Path:
    """Write batch as a long-format tab-delimited table; return path.
    One row per (pattern, horizon), FORWARD_HORIZONS order. Filename:
    walkforward_<stem>_<tag>_<timestamp>.txt in EVAL_REPORTS_DIR
    (override via reports_dir).
    """
    target_dir = reports_dir if reports_dir is not None else EVAL_REPORTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    catalog_stem = Path(batch.catalog_path).stem
    tag = _override_tag(batch.threshold_overrides)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = target_dir / f"walkforward_{catalog_stem}_{tag}_{stamp}.txt"

    lines = ["\t".join(_REPORT_COLUMNS)]
    for result in batch.results:
        for horizon in FORWARD_HORIZONS:
            if horizon in result.per_horizon:
                lines.append(_row_for(result, horizon))
    out_path.write_text("\n".join(lines), encoding="utf-8")

    logger.info(
        "write_walk_forward_report: %d patterns x %d horizons "
        "(%d degenerate_corpus, overrides=%s) -> %s",
        batch.n_patterns, len(FORWARD_HORIZONS), batch.n_degenerate, tag,
        out_path,
    )
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# Eval result cache -- WO-P300-E4.003 (M-096), pre-batch memoization
# ─────────────────────────────────────────────────────────────────────────────

def _stable_stem(path: Path) -> str:
    """Strips the daily <mmddyy> rollover prefix from a catalog
    filename stem ("071726catalog" -> "catalog") so a same-content
    rollover copy doesn't churn the cache filename. Non-dated stems
    (staging/test files) pass through unchanged."""
    return re.sub(r"^\d{6}(?=catalog$)", "", path.stem)


def _catalog_fingerprint(catalog_path: Path) -> str:
    """Content fingerprint: row count + max pattern_instance_id +
    file size. Identical across a verbatim rename/copy (the daily
    rollover) -- changes only when content actually changes (a real
    promote). One indexed COUNT/MAX query + a stat() call."""
    with connection_context(str(catalog_path)) as conn:
        count, max_id = conn.execute(
            "SELECT COUNT(*), COALESCE(MAX(pattern_instance_id), 0) "
            "FROM pattern_instances"
        ).fetchone()
    return f"{count}_{max_id}_{catalog_path.stat().st_size}"


def _cache_key(catalog_path: Path | str, overrides: ThresholdOverrides | None) -> str:
    """<stable_stem>_<content_fingerprint>_<override_tag>.json (v1.5,
    M-099). Fingerprint is the real invalidation signal, not mtime --
    a daily rollover copy now correctly HITS; only a real promote
    (row count/max_id change) invalidates. Raises FileNotFoundError if
    catalog_path doesn't exist (same precondition load_full_catalog
    relies on).
    """
    resolved = Path(catalog_path)
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    tag = _override_tag(overrides)
    return f"{_stable_stem(resolved)}_{_catalog_fingerprint(resolved)}_{tag}.json"


def read_cached_walk_forward(
    catalog_path: Path | str,
    overrides: ThresholdOverrides | None = None,
) -> WalkForwardBatch | None:
    """None on any miss -- absent, catalog changed, or unparseable.
    Never an error: a None always means "caller should run_walk_
    forward() for real."""
    try:
        cache_path = EVAL_CACHE_DIR / _cache_key(catalog_path, overrides)
    except FileNotFoundError:
        return None
    if not cache_path.exists():
        return None
    try:
        return WalkForwardBatch.model_validate_json(
            cache_path.read_text(encoding="utf-8")
        )
    except Exception as exc:  # noqa: BLE001 -- any parse failure is a miss
        logger.warning(
            "read_cached_walk_forward: %s unreadable (%s) -- treating as "
            "cache miss", cache_path, exc,
        )
        return None


def write_walk_forward_cache(
    batch: WalkForwardBatch,
    catalog_path: Path | str,
) -> Path:
    """Writes/refreshes the cache entry for this snapshot. catalog_path
    is separate from batch.catalog_path so the caller controls which
    file's fingerprint keys the entry (staging-copy case). Stale
    entries are not pruned -- cheap, one file per promote."""
    EVAL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = EVAL_CACHE_DIR / _cache_key(catalog_path, batch.threshold_overrides)
    cache_path.write_text(batch.model_dump_json(), encoding="utf-8")
    logger.info(
        "write_walk_forward_cache: %d patterns -> %s",
        batch.n_patterns, cache_path,
    )
    return cache_path
