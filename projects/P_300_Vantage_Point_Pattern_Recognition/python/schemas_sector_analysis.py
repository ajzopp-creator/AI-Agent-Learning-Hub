"""
FILE: schemas_sector_analysis.py
VERSION: 1.1
DATE: 2026-07-10
AUTHOR: Anthony Zoppi + Claude
LAYER: schemas
DESCRIPTION:
    Pydantic models for WO-P300-E2.002 Phase 5 Sector-Stratified Result
    Analysis. Covers data/reference/sector_map.csv row shape and the
    sector_stats table row shape (research_catalog.db, additive table,
    Decision 3).

    SectorMapRow moved here from schemas_bulk.py v1.1 -> v1.2 (was
    unused/unimported there) and extended with asset_class + source_note
    per Decision 5 -- ETF rows carry sector=None, never a fabricated
    sector for a fund; STOCK rows carry a real GICS Level-1 sector,
    zero-tolerance per Decision 2 (no "Unclassified" resting state).

    SectorStatsRecord is the additive sector_stats table row -- one row
    per (sector_label x detection_tier x horizon_days) cell, where
    sector_label is either a real GICS sector (STOCK rows) or
    SECTOR_ETF_LABEL ("Index/Diversified", ETF rows -- never folded into
    a sector bucket). Computed fresh each analysis run: DELETE+INSERT
    snapshot semantics, not an ever-growing history table -- DB backups
    (established project pattern) cover historical snapshots instead of
    row-versioning. below_min_n flags cells under SECTOR_MIN_N_THRESHOLD
    (config.py, =30) per Decision 4 (flag, don't exclude).

CHANGELOG:
    - 2026-07-10 v1.1: source_note constraint relaxed min_length=1 ->
      default="" (file #3 revisited during file #5 drafting -- real
      sector_map.csv has ~87% empty source_note, would have rejected
      nearly every row on first real load. Caught via M-054 discipline,
      verifying against the actual file before building the next layer
      on top of an unverified assumption).
    - 2026-07-10 v1.0: Initial release (WO-P300-E2.002 file #3 of 11).
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from config import (
    ASSET_CLASS_ETF,
    ASSET_CLASS_STOCK,
    BULK_TIER_RELAXED,
    BULK_TIER_STRICT,
    FORWARD_HORIZONS,
)


# ---------------------------------------------------------------------------
# REFERENCE -- data/reference/sector_map.csv
# ---------------------------------------------------------------------------

class SectorMapRow(BaseModel):
    """
    One row of the operator-maintained symbol -> sector mapping.

    Moved from schemas_bulk.py (confirmed unimported there via
    Select-String across the active python/ tree, 2026-07-10) and
    extended for WO-P300-E2.002. asset_class distinguishes STOCK (real
    GICS sector required, Decision 2) from ETF (sector must be None,
    Decision 5). source_note is a free-text audit trail, populated only
    where worth documenting (GICS mismatch vs. an export-batch label,
    an unusual security like a REIT/MLP, an ETF's excluded status) --
    empty for the common case where a symbol's sector is unambiguous.
    Verified against the real sector_map.csv (2026-07-10, 127 rows):
    ~87% carry an empty source_note, confirming it must NOT be a
    required field.
    """
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(min_length=1, max_length=12)
    sector: Optional[str] = Field(default=None, min_length=1, max_length=64)
    asset_class: Literal[ASSET_CLASS_STOCK, ASSET_CLASS_ETF]
    source_note: str = Field(default="", max_length=256)

    @model_validator(mode="after")
    def _sector_matches_asset_class(self) -> "SectorMapRow":
        if self.asset_class == ASSET_CLASS_STOCK and self.sector is None:
            raise ValueError(
                f"{self.symbol}: STOCK rows must have a real sector "
                "(Decision 2 zero-tolerance -- no unclassified stocks)"
            )
        if self.asset_class == ASSET_CLASS_ETF and self.sector is not None:
            raise ValueError(
                f"{self.symbol}: ETF rows must have sector=None "
                "(Decision 5 -- never a fabricated sector for a fund)"
            )
        return self


# ---------------------------------------------------------------------------
# OUTPUT -- research_catalog.db sector_stats table (additive, Decision 3)
# ---------------------------------------------------------------------------

class SectorStatsRecord(BaseModel):
    """
    One sector_stats table row: n / win_rate / mean_return_pct /
    std_return_pct for one (sector_label x detection_tier x horizon_days)
    cell.

    Snapshot semantics: computed_at stamps each analysis run; the table
    is DELETE+INSERT per run, not accumulated. below_min_n flags cells
    under SECTOR_MIN_N_THRESHOLD (Decision 4 -- flag, don't exclude).

    Stats fields are None only when n=0 (that sector x tier x horizon
    combination has zero cataloged instances -- absent from the report
    per Decision 4's scope note, not an error). std_return_pct may also
    be None at n=1 (undefined for a single sample) even though win_rate
    and mean_return_pct are always computable for n>=1.
    """
    sector_stats_id: Optional[int] = None
    sector_label: str = Field(min_length=1, max_length=64)
    detection_tier: Literal[BULK_TIER_STRICT, BULK_TIER_RELAXED]
    horizon_days: int
    n: int = Field(ge=0)
    win_rate: Optional[float] = Field(default=None, ge=0, le=1)
    mean_return_pct: Optional[float] = None
    std_return_pct: Optional[float] = Field(default=None, ge=0)
    below_min_n: bool
    computed_at: datetime

    @field_validator("horizon_days")
    @classmethod
    def _horizon_in_allowed_set(cls, v: int) -> int:
        if v not in FORWARD_HORIZONS:
            raise ValueError(
                f"horizon_days {v} not in allowed set {FORWARD_HORIZONS}"
            )
        return v

    @model_validator(mode="after")
    def _stats_presence_matches_n(self) -> "SectorStatsRecord":
        if self.n == 0:
            if (
                self.win_rate is not None
                or self.mean_return_pct is not None
                or self.std_return_pct is not None
            ):
                raise ValueError("n=0 cells must have all stats fields None")
        else:
            if self.win_rate is None or self.mean_return_pct is None:
                raise ValueError(
                    "n>0 cells must have win_rate and mean_return_pct populated"
                )
        return self
