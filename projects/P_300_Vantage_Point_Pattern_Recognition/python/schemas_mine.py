"""
FILE: schemas_mine.py
VERSION: 1.0
DATE: 2026-09-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    WO-P300-E3.002 pattern-mining output formatting contract. New file
    (WO-P300-E5.001) -- MineCandidateRow was previously defined in
    infrastructure/mine_report_writer.py; domain/mine_audit.py imported
    it directly from there, which the import-linter contract this WO
    adds forbids.

    Tried schemas_bulk.py first (closest existing file by subject-matter
    proximity -- both mining and bulk extraction are pre-catalog-
    insertion, historical-export-scanning concerns) but that file is
    already at 281 lines and the addition pushed it to 315, over the
    300-line cap this same WO is trying not to make worse elsewhere.
    A dedicated one-class file was the actual right call, not a
    compromise -- avoids growing an unrelated file's debt to solve this
    one.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MineCandidateRow:
    """One mined candidate with its symbol attached (pattern_miner.py's
    MinedCandidate is deliberately symbol-less -- the caller knows the
    symbol from the file being scanned). Formatting layer's own input
    contract, not a DB row model -- WO-P300-E3.002 persists nothing to
    any catalog in Phase 1.

    Moved here from infrastructure/mine_report_writer.py (WO-P300-E5.001).
    No field, no behavior changed by the move.
    """
    symbol: str
    anchor_date: date
    pattern_class: str
    horizon_days: int
    move_pct: float
    standard_horizon: bool
    bars_since_crossover: int
    entry_tier: str
    keep: str = "YES"
