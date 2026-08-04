"""
FILE: schemas_promote_gate.py
VERSION: 1.0
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic v2 models for the WO-P300-E5.005 auto-promote gate: the
    metrics parsed out of a walk-forward report, the thresholds the
    gate is judged against, and the verdict it produces.

    Pure data definitions. No IO, no decision logic -- parsing lives in
    infrastructure/walkforward_report_io.py, the decision in
    domain/promote_gate.py. This file is importable by both without
    pulling in either.

    TWO THINGS ENCODED HERE THAT WERE MEASURED, NOT ASSUMED
    (2026-07-28 PEH run against the real report pair):

    1. `correctness` has exactly five values, and they map per-class:
           BUY   -> correct_buy  / false_positive
           PASS  -> correct_pass / missed
           WATCH -> neutral (UNGRADED -- not right, not wrong)
       WATCH therefore carries NO accuracy field on WalkForwardMetrics,
       only a count. An earlier sketch scored correctness with
       startswith("correct_"), which silently produced WATCH=0.00%
       forever -- a permanently-zero metric that reads as a finding
       rather than a bug. Modelling WATCH without an accuracy field
       makes that error unrepresentable rather than merely discouraged.

    2. Real baseline magnitudes, for sanity-checking future parses:
           BUY  69.11% -> 69.05% (n 6983 -> 9260)
           PASS 61.29% -> 62.63% (n 6593 -> 7741)

    DELTAS ARE WHOLE-CORPUS, NOT COHORT. Adding patterns re-ranks top-K
    for pre-existing patterns too, so these compare two corpora -- they
    cannot be decomposed into "how did the new patterns do." That is the
    mechanism behind the WO-P300-E2.003 regression and is why the gate
    is built this way. Do not later "improve" it to score only the new
    cohort.

CHANGELOG:
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial. Thresholds default to
      the operator-confirmed 3pp bar and the n>=400 small-sample floor.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# The complete observed enum. The parser MUST reject any value outside
# this set rather than ignoring it -- an unrecognized value means the
# report format changed, and silently dropping it would understate a
# class's denominator and inflate its accuracy.
CORRECTNESS_VALUES: frozenset[str] = frozenset({
    "correct_buy", "false_positive",   # BUY   graded
    "correct_pass", "missed",          # PASS  graded
    "neutral",                         # WATCH ungraded
})

GRADED_BY_CLASS: dict[str, tuple[str, str]] = {
    "BUY": ("correct_buy", "false_positive"),
    "PASS": ("correct_pass", "missed"),
}


class GateThresholds(BaseModel):
    """Operator-confirmed decision bars. See WO-P300-E5.005."""

    model_config = ConfigDict(frozen=True)

    max_buy_precision_drop_pp: float = Field(
        default=3.0,
        description="Confirmed 2026-07-28. Sits below the only measured "
                    "regression this project has (E2.003, 5.2pp) with "
                    "margin, while tight enough to catch a repeat.",
    )
    max_pass_accuracy_drop_pp: float = Field(default=3.0)
    min_buy_n: int = Field(
        default=400,
        description="Small-sample floor on the COMPARISON, not the batch. "
                    "At p~0.69 the standard error is ~4.8pp at n=100 and "
                    "~2.4pp at n=400, so a 3pp bar is inside sampling "
                    "noise below this -- a spurious STOP would strand a "
                    "staged batch, the exact failure this WO prevents. "
                    "Below the floor the gate promotes and says why.",
    )
    buy_volume_flag_pct: float = Field(
        default=50.0,
        description="Informational only -- logged, never blocks.",
    )


class WalkForwardMetrics(BaseModel):
    """Aggregated from one walk-forward TSV report.

    Built ONLY from rows where is_chosen_horizon is true; those are the
    only rows carrying a `correctness` value.
    """

    model_config = ConfigDict(frozen=True)

    source_path: str
    source_mtime: datetime
    total_rows: int
    chosen_rows: int
    corpus_size: int

    buy_n: int
    buy_correct: int
    buy_precision_pct: float

    pass_n: int
    pass_correct: int
    pass_accuracy_pct: float

    # Ungraded by design -- see module docstring. Count only.
    watch_n: int


class PromoteGateVerdict(BaseModel):
    """Outcome of comparing a staging report against its baseline."""

    model_config = ConfigDict(frozen=True)

    decision: Literal["PROMOTE", "STOP"]
    reasons: list[str] = Field(
        description="Human-readable, always populated -- including on "
                    "PROMOTE, so the log records why it passed and not "
                    "merely that it did.",
    )

    pre: WalkForwardMetrics
    staging: WalkForwardMetrics
    thresholds: GateThresholds

    buy_delta_pp: float
    pass_delta_pp: float
    buy_volume_change_pct: float

    small_n_waived: bool = Field(
        description="True when staging BUY n fell below min_buy_n and the "
                    "comparison was skipped as untestable. A waived gate "
                    "is NOT a passed gate; the log must say so.",
    )
    evaluated_at: datetime


class PromoteStopMarker(BaseModel):
    """On-disk breadcrumb the INIT sequence surfaces at session start.

    Exists because the gate's STOP path recreates the very problem this
    WO was filed to solve. A blocked run leaves a staged batch on disk
    that the operator may walk away from -- the 2026-07-25 batch sat
    unpromoted for three days and was then silently overwritten by the
    next run's staging rebuild. A log file only helps someone who
    remembers to open it.

    INIT Step 0.6 reads this raw as JSON, so field names are chosen to
    be readable without the model.

    TWO SEVERITIES, deliberately distinct:
      STOP   -- action required. A staged batch is sitting unpromoted
                and WILL be destroyed by the next ingest run.
      WAIVED -- informational. The batch WAS promoted, but the sample
                was too small to test, so nothing was actually proven.
                Nothing is at risk; the operator should simply know.
    """

    model_config = ConfigDict(frozen=True)

    severity: Literal["STOP", "WAIVED"]
    created_at: datetime
    decision: Literal["PROMOTE", "STOP"]

    staging_db_path: str = Field(
        description="The staging DB at risk. On STOP this is the file "
                    "the next ingest run will overwrite.",
    )
    baseline_report: str
    staging_report: str

    buy_delta_pp: float
    pass_delta_pp: float
    small_n_waived: bool

    reasons: list[str]
    next_action: str = Field(
        description="Plain-language instruction, written for a reader "
                    "who has lost all context on the run that produced "
                    "this -- which is the expected case.",
    )
