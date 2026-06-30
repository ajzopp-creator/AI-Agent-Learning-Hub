"""
FILE: eval_io.py
VERSION: 1.2
DATE: 2026-06-28
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    All I/O for the Stage 6 walk-forward eval loop. Two responsibilities:

      1. load_full_catalog() -- one round trip per bulk loader (M-012
         connection lifecycle via utilities/db_connect.py), returns
         every PATTERN_IDENT pattern's metadata/windows/labels keyed
         by pattern_instance_id. Read-only -- no catalog writes
         anywhere in this module.

      2. write_walk_forward_report() -- renders a WalkForwardBatch as
         a tab-delimited, Excel-ready table to outputs/reports/eval/
         (REPORTS_DIR/eval, created if absent). LONG format: one row
         per (pattern, horizon) -- all FORWARD_HORIZONS, not just
         chosen_horizon -- since this is a verification tool for the
         matching/classification chain, not a live trading report.
         is_chosen_horizon flags the row matching the pattern's
         actual emitted decision. Ground-truth columns are populated
         on the is_chosen_horizon row only (schemas_eval only stores
         ground truth at chosen_horizon).

         v1.2: filename now carries a threshold-override tag (e.g.
         "bz1.0" for a BUY_MIN_Z_SCORE=1.0 comparison run, "default"
         for an unmodified run) so two reports from different gate
         settings never collide or get confused on disk. No comment/
         header row injected into the table body itself -- that would
         break both Excel import and the project's existing tab-
         delimited PowerShell read pattern (Import-Csv -Delimiter
         "`t"); the tag lives in the filename only.

    No business logic here -- domain/eval_scoring.py owns the math.
    No orchestration -- application/run_eval_loop.py owns the call
    order. This module fetches and saves only.

CHANGELOG:
    - 2026-06-28 v1.2: Filename gains a threshold-override tag
      (_override_tag()) so default-gate and overridden-gate reports
      are distinguishable on disk without opening the file.
    - 2026-06-28 v1.1: Long-format report -- one row per (pattern,
      horizon) instead of one row per pattern. Adds is_chosen_horizon,
      std_return_pct, certainty_equivalent columns. Ground-truth
      columns now blank on non-chosen-horizon rows (data not carried
      per-horizon in schemas_eval.WalkForwardResult). No schema or
      domain changes -- per_horizon already held all 5 horizons.
    - 2026-06-28 v1.0: Initial release. Stage 6 eval loop file #3 of 5.
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

# sys.path bootstrap for direct invocation / smoke harness.
_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from config import FORWARD_HORIZONS, REPORTS_DIR  # noqa: E402
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

def load_full_catalog() -> tuple[
    str,
    dict[int, PatternMetadata],
    dict[int, list[NormalizedBar]],
    dict[int, dict[int, ForwardLabelLite]],
]:
    """Bulk-load every PATTERN_IDENT pattern's metadata, normalized
    bars, and forward labels from the active catalog.

    Returns:
        (catalog_path, metadata_by_pid, windows_by_pid, labels_by_pid)
        -- catalog_path as str (for WalkForwardBatch.catalog_path
        stamping). All three dicts keyed by pattern_instance_id.
    """
    catalog_path = get_latest_catalog()
    with connection_context(catalog_path) as conn:
        all_pids = catalog_reader.get_all_pattern_ids(conn)
        metadata = catalog_reader.bulk_load_pattern_metadata(conn, all_pids)
        windows = catalog_reader.bulk_load_normalized_windows(conn, all_pids)
        labels = catalog_reader.bulk_load_forward_labels(conn, all_pids)
    logger.info(
        "load_full_catalog: %d patterns loaded from %s",
        len(all_pids), catalog_path,
    )
    return str(catalog_path), metadata, windows, labels


# ─────────────────────────────────────────────────────────────────────────────
# Report write -- long format: one row per pattern per horizon
# ─────────────────────────────────────────────────────────────────────────────

def _override_tag(overrides: ThresholdOverrides | None) -> str:
    """Short filename tag for the threshold overrides used this run.

    "default" when overrides is None or every field is None. Otherwise
    one segment per non-None field, e.g. ThresholdOverrides(
    buy_min_z_score=1.0) -> "bz1.0".
    """
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

    Ground-truth fields (actual_return_pct, actual_is_profitable,
    correctness) are populated only when horizon == result.chosen_
    horizon -- that's the only horizon WalkForwardResult carries
    ground truth for. Other horizons render those three fields blank,
    not a fabricated value.
    """
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

    One row per (pattern, horizon) -- FORWARD_HORIZONS order within
    each pattern. Filename: walkforward_<catalog_stem>_<override_tag>_
    <YYYYMMDD_HHMMSS>.txt. Default target_dir is EVAL_REPORTS_DIR;
    caller may override.
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
