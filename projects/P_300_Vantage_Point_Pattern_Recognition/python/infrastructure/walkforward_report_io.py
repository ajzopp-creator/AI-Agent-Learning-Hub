"""
FILE: infrastructure/walkforward_report_io.py
VERSION: 1.0
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Reads walk-forward evaluation reports into WalkForwardMetrics, and
    locates the baseline/staging pair for a given run.

    FORMAT (verified 2026-07-28 against real reports -- not assumed):
    tab-separated .txt in outputs/reports/eval/, NO summary block, one
    row per (pattern x horizon). ~106k rows / ~10MB at a 21k corpus.
    `correctness` is populated ONLY on is_chosen_horizon rows; every
    other row has it blank. All aggregation happens here.

    FAIL LOUD, NEVER DEFAULT. Every validation below raises rather than
    substituting a zero or skipping a row. The reasoning is asymmetric:
    a parse that silently under-counts a class shrinks its denominator
    and INFLATES its accuracy, which makes the gate PASS a batch it
    should have STOPPED. A crash costs a re-run; a silent pass costs a
    degraded live catalog that nobody notices. There is no case where
    guessing beats stopping.

CHANGELOG:
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from schemas_promote_gate import (
    CORRECTNESS_VALUES, GRADED_BY_CLASS, WalkForwardMetrics,
)

REQUIRED_COLUMNS = frozenset({
    "corpus_size", "final_signal_class", "is_chosen_horizon", "correctness",
})

_STAGING_RE = re.compile(r"^walkforward_staging_.*\.txt$", re.IGNORECASE)
_BASELINE_RE = re.compile(r"^walkforward_\d+catalog_.*\.txt$", re.IGNORECASE)

# Generous: a real run legitimately spans hours (2026-07-28's pair was 91
# minutes apart, and the promote alone took 86). Tight enough to catch the
# failure this exists for -- a baseline run that failed, leaving a
# DAYS-old report that "newest match" globbing would happily pair up.
DEFAULT_MAX_PAIR_AGE_MINUTES = 720


def _load_chosen_rows(path: Path) -> tuple[pd.DataFrame, int, int]:
    """Read the TSV, validate it, return (chosen_rows, total_rows, corpus)."""
    df = pd.read_csv(path, sep="\t", low_memory=False)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"{path.name}: missing required column(s) {sorted(missing)}. "
            f"Report format changed; parser must be revisited, not patched."
        )

    mask = df["is_chosen_horizon"].astype(str).str.strip().str.lower() == "true"
    chosen = df[mask]
    if chosen.empty:
        raise ValueError(
            f"{path.name}: zero is_chosen_horizon rows. Either the report is "
            f"truncated or the column's encoding changed -- refusing to "
            f"report all-zero metrics from it."
        )

    values = set(chosen["correctness"].astype(str).str.strip())
    unknown = values - CORRECTNESS_VALUES
    if unknown:
        raise ValueError(
            f"{path.name}: unrecognized correctness value(s) {sorted(unknown)}. "
            f"Known: {sorted(CORRECTNESS_VALUES)}. Dropping unknowns would "
            f"understate a denominator and inflate accuracy -- refusing."
        )

    return chosen, len(df), int(df["corpus_size"].max())


def _tally(chosen: pd.DataFrame, signal_class: str) -> tuple[int, int, float]:
    """Return (n, correct, pct) for one graded class. WATCH is not graded."""
    correct_val, incorrect_val = GRADED_BY_CLASS[signal_class]
    sub = chosen[
        chosen["final_signal_class"].astype(str).str.strip() == signal_class
    ]
    n = len(sub)
    vals = sub["correctness"].astype(str).str.strip()
    correct = int((vals == correct_val).sum())
    incorrect = int((vals == incorrect_val).sum())

    if correct + incorrect != n:
        raise ValueError(
            f"{signal_class}: {correct} + {incorrect} != {n} rows. Class "
            f"carries a correctness value outside its own graded pair "
            f"({correct_val}/{incorrect_val}) -- class/value mapping is "
            f"wrong or the report changed."
        )

    return n, correct, (correct / n * 100.0) if n else 0.0


def parse_walkforward_report(path: Path) -> WalkForwardMetrics:
    """Aggregate one walk-forward report. Raises on any inconsistency."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"walk-forward report not found: {path}")

    chosen, total_rows, corpus = _load_chosen_rows(path)
    buy_n, buy_ok, buy_pct = _tally(chosen, "BUY")
    pass_n, pass_ok, pass_pct = _tally(chosen, "PASS")
    watch_n = len(
        chosen[chosen["final_signal_class"].astype(str).str.strip() == "WATCH"]
    )

    if buy_n + pass_n + watch_n != len(chosen):
        raise ValueError(
            f"{path.name}: BUY+PASS+WATCH ({buy_n + pass_n + watch_n}) != "
            f"{len(chosen)} chosen rows -- an unexpected signal class exists."
        )

    return WalkForwardMetrics(
        source_path=str(path),
        source_mtime=datetime.fromtimestamp(path.stat().st_mtime),
        total_rows=total_rows,
        chosen_rows=len(chosen),
        corpus_size=corpus,
        buy_n=buy_n, buy_correct=buy_ok, buy_precision_pct=buy_pct,
        pass_n=pass_n, pass_correct=pass_ok, pass_accuracy_pct=pass_pct,
        watch_n=watch_n,
    )


def find_report_pair(
    eval_dir: Path,
    max_age_minutes: int = DEFAULT_MAX_PAIR_AGE_MINUTES,
) -> tuple[Path, Path]:
    """Locate (baseline, staging) for the current run. Raises if unsafe.

    Newest-match globbing alone is NOT sufficient. On 2026-07-28 the
    baseline report was byte-identical to 2026-07-25's, because no promote
    landed between them -- so a failed baseline run would leave a stale
    file that pairs up silently and yields a meaningless delta.
    """
    eval_dir = Path(eval_dir)
    if not eval_dir.is_dir():
        raise NotADirectoryError(f"eval report dir not found: {eval_dir}")

    def newest(pattern: re.Pattern[str], label: str) -> Path:
        hits = [p for p in eval_dir.iterdir() if pattern.match(p.name)]
        if not hits:
            raise FileNotFoundError(
                f"no {label} walk-forward report in {eval_dir}"
            )
        return max(hits, key=lambda p: p.stat().st_mtime)

    baseline = newest(_BASELINE_RE, "baseline")
    staging = newest(_STAGING_RE, "staging")

    gap = abs(
        datetime.fromtimestamp(staging.stat().st_mtime)
        - datetime.fromtimestamp(baseline.stat().st_mtime)
    )
    if gap > timedelta(minutes=max_age_minutes):
        raise ValueError(
            f"report pair is {gap} apart, over the {max_age_minutes}-minute "
            f"limit -- these are probably not from the same run.\n"
            f"  baseline: {baseline.name}\n  staging:  {staging.name}\n"
            f"Re-run the baseline eval rather than comparing against a "
            f"stale report."
        )

    return baseline, staging
