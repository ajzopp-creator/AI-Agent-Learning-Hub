"""
FILE: infrastructure/promote_marker_io.py
VERSION: 1.0
DATE: 2026-07-28
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Writes, reads, and clears the promote-gate marker at
    <project root>\\P_300_promote_marker.json -- the file INIT Step 0.6
    surfaces at session start.

    WHY THIS FILE EXISTS AT ALL. Auto-promote solves the clean case,
    which is most runs. It does NOT solve the STOP case: a blocked run
    leaves a staged batch on disk that the operator may walk away from,
    which is the exact failure WO-P300-E5.005 was filed to fix. The
    2026-07-25 batch staged at 16:15, sat unpromoted for three days,
    and was silently destroyed when the next run's staging rebuild
    (shutil.copy2 from live) overwrote it. A bundled log file does not
    help, because reading it depends on remembering there is something
    to read.

    INIT runs every session. A marker on disk announces itself the next
    morning instead of waiting to be discovered.

    ATOMIC WRITES. Written to a temp file then os.replace()'d into
    place, so INIT can never read a half-written marker. os.replace is
    atomic on Windows for same-volume moves.

    CLEARING IS THE CALLER'S JOB, and it matters: a stale STOP marker
    that outlives its staged batch trains the operator to ignore the
    warning. clear_marker() must be called after a successful promote.

CHANGELOG:
    - 2026-07-28 v1.0 (WO-P300-E5.005): initial.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from schemas_promote_gate import PromoteGateVerdict, PromoteStopMarker

MARKER_FILENAME = "P_300_promote_marker.json"

_STOP_ACTION = (
    "A staged batch was NOT promoted because the quality gate stopped it. "
    "The staging DB named above is still on disk and WILL BE DESTROYED by "
    "the next ingest-mined run, which rebuilds staging from live. Either "
    "review the deltas and promote deliberately with "
    "`python cli.py ingest-mined --promote <staging_db_path>`, or accept "
    "the batch is bad and delete the staging DB. Then clear this marker."
)

_WAIVED_ACTION = (
    "The batch WAS promoted, but the sample was too small to test at the "
    "configured threshold -- so quality was not verified, merely untested. "
    "Nothing is at risk and no action is required. Clear this marker once "
    "read."
)


def marker_path(project_root: Path) -> Path:
    return Path(project_root) / MARKER_FILENAME


def build_marker(
    verdict: PromoteGateVerdict,
    staging_db_path: Path | str,
) -> PromoteStopMarker | None:
    """Build a marker from a verdict, or None if nothing needs surfacing.

    A clean PROMOTE produces no marker. Only a STOP (batch stranded) or
    a waived PROMOTE (batch untested) is worth interrupting a session
    for -- surfacing every successful run would train the operator to
    skim past Step 0.6.
    """
    if verdict.decision == "STOP":
        severity, action = "STOP", _STOP_ACTION
    elif verdict.small_n_waived:
        severity, action = "WAIVED", _WAIVED_ACTION
    else:
        return None

    return PromoteStopMarker(
        severity=severity,
        created_at=datetime.now(),
        decision=verdict.decision,
        staging_db_path=str(staging_db_path),
        baseline_report=verdict.pre.source_path,
        staging_report=verdict.staging.source_path,
        buy_delta_pp=verdict.buy_delta_pp,
        pass_delta_pp=verdict.pass_delta_pp,
        small_n_waived=verdict.small_n_waived,
        reasons=list(verdict.reasons),
        next_action=action,
    )


def write_marker(project_root: Path, marker: PromoteStopMarker) -> Path:
    """Atomically write the marker. Returns the path written."""
    target = marker_path(project_root)
    tmp = target.with_suffix(".json.tmp")
    tmp.write_text(marker.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, target)
    return target


def read_marker(project_root: Path) -> PromoteStopMarker | None:
    """Read the marker, or None if absent.

    A malformed marker RAISES rather than returning None. None means
    'no problem outstanding', and a corrupt file must never be able to
    impersonate that.
    """
    target = marker_path(project_root)
    if not target.exists():
        return None
    raw = target.read_text(encoding="utf-8")
    try:
        return PromoteStopMarker.model_validate(json.loads(raw))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(
            f"{target} exists but could not be parsed: {exc}. Refusing to "
            f"treat an unreadable marker as 'no problem outstanding' -- "
            f"inspect or delete it deliberately."
        ) from exc


def clear_marker(project_root: Path) -> bool:
    """Remove the marker. Returns True if one was present.

    Call after a successful deliberate promote. A stale STOP marker
    that outlives its batch teaches the operator to ignore Step 0.6.
    """
    target = marker_path(project_root)
    if not target.exists():
        return False
    target.unlink()
    return True
