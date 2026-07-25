"""P_400 vault attribution schemas (WO-P020-E1.007).

Split out of schemas.py rather than appended: schemas.py was already at
229 lines and these models pushed it to 330, over the 300-line hard limit
(python-project-architecture skill). Separate file also satisfies the
one-reason-to-change rule -- these models track P_400's frontmatter
shape, which evolves independently of P_020's own trade/exit schemas.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\vault_schemas.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   schema
"""

from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class VaultEntry(BaseModel):
    """One P_400 Obsidian record, reduced to the fields P_020 needs."""

    symbol:           str
    signal_date:      str                     # 'YYYY-MM-DD'
    system:           Optional[str] = None    # from why_code / signal_source
    lifecycle_status: str = ""
    source_schema:    str = ""                # 'P400' or 'P400_PAPER'
    note_name:        str = ""


class VaultLookup(BaseModel):
    """In-memory lookup built from P_400 vault records.

    Two parallel indexes keyed by symbol:
      - attributed: entries carrying a usable system value
      - covered:    every matchable entry, attributed or not

    The split exists because coverage is measurable today while
    attribution is not (why_code is null on all 191 current records).
    """

    attributed:     Dict[str, List[VaultEntry]] = Field(default_factory=dict)
    covered:        Dict[str, List[VaultEntry]] = Field(default_factory=dict)
    total_records:  int = 0
    skipped_status: int = 0
    vault_folder:   str = ""

    def get_system(
        self,
        symbol: str,
        open_date: str,
        forward_days: int,
    ) -> Optional[str]:
        """Return the system for a fill, or None if no attributed match.

        Args:
            symbol: Underlying symbol (case-insensitive).
            open_date: Fill date 'YYYY-MM-DD'.
            forward_days: Max days the fill may lag the signal.

        Returns:
            System string, or None when no attributed record matches.
        """
        hit = self._nearest(
            self.attributed, symbol, open_date, forward_days
        )
        return hit.system if hit else None

    def has_coverage(
        self,
        symbol: str,
        open_date: str,
        forward_days: int,
    ) -> bool:
        """Return True if any matchable P_400 record covers this fill."""
        return self._nearest(
            self.covered, symbol, open_date, forward_days
        ) is not None

    @staticmethod
    def _nearest(
        index: Dict[str, List[VaultEntry]],
        symbol: str,
        open_date: str,
        forward_days: int,
    ) -> Optional[VaultEntry]:
        """Closest signal_date at or before open_date, inside the window.

        Forward-only by design: a signal cannot post-date its own fill,
        so a negative gap is never a match.
        """
        candidates = index.get(symbol.strip().upper())
        if not candidates:
            return None
        try:
            fill = date.fromisoformat(open_date)
        except ValueError:
            return None

        best: Optional[VaultEntry] = None
        best_gap: Optional[int] = None
        for entry in candidates:
            try:
                sig = date.fromisoformat(entry.signal_date)
            except ValueError:
                continue
            gap = (fill - sig).days
            if 0 <= gap <= forward_days:
                if best_gap is None or gap < best_gap:
                    best, best_gap = entry, gap
        return best

    def summary(self) -> str:
        """Return a one-line summary for logging."""
        return (
            f"VaultLookup: {self.total_records} P_400 records "
            f"({len(self.attributed)} symbols attributed, "
            f"{len(self.covered)} covered, "
            f"{self.skipped_status} skipped on status) "
            f"from {self.vault_folder}"
        )
