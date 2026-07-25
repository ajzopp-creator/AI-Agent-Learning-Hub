"""
FILE: domain/mine_audit.py
VERSION: 1.1
DATE: 2026-07-13
AUTHOR: Anthony Zoppi + Claude
LAYER: domain
DESCRIPTION:
    Pre-ingest audit gate for WO-P300-E3.002 Phase 2 (file #5 of 9).
    Independently verifies operator-approved mine_candidates.csv rows
    before they're allowed into the staging insert path.

    Deliberately does NOT re-derive a second copy of the eligibility/
    outcome math -- that's exactly the trap M-082 already burned once
    (a fix silently diverging between two similar-but-not-identical
    implementations). Instead this re-runs pattern_miner.py's own
    mine_bars() -- 18/18 PASS, zero confirmed defects across eleven
    real-data diagnostic passes (2026-07-13 validation session) --
    against freshly re-read bars, then diffs the approved CSV row
    against what that real recompute actually produced.

    That single diff covers all of the WO's named checks in one move:
      - move clears MINE_MOVE_THRESHOLD at the claimed horizon
        (horizon_days/move_pct mismatch)
      - anchor is the launch, not a mid-run bar (the cursor-scan is
        sequence-dependent -- a mid-run bar simply never appears in
        mine_bars()'s output, so it fails as "not reproduced")
      - eligibility windows hold (setup/forward bars, enforced inside
        _is_eligible(), which the recompute calls)
      - post-backfill restriction holds (MINE_MIN_ANCHOR_DATE, same)
    Catalog collision is a separate, explicit check against a set of
    existing (symbol, anchor_date) keys passed in by the caller --
    this file stays domain-pure, no DB access of its own. Phase 2's
    orchestrator (file #6, not yet built) is responsible for reading
    that set from the live catalog and re-reading the source grid file.

    No I/O, no DB, no print -- strictly testable in isolation, same
    contract as pattern_miner.py.

CHANGELOG:
    - 2026-07-14 v1.1: _MOVE_PCT_EPSILON widened 1e-9 -> 1e-6 (M-092).
      Found during ingest_mined_pipeline.py (file #6) PEH against real
      ADBE data: every approved row failed audit on a move_pct
      "mismatch" that printed identical at 6 decimals -- root cause is
      mine_report_writer.py's CSV round-trip (:.6f write precision,
      by design, operator-readable), which can differ from the fresh
      recompute by up to ~5e-7 on a value that never actually changed.
      1e-9 was sized for float-arithmetic noise alone and never
      accounted for the CSV boundary it sits downstream of. CSV
      precision was deliberately NOT changed -- 6 decimals on a 15%+
      move is intentional operator-facing precision, not a bug.
    - 2026-07-13 v1.0: Initial release (WO-P300-E3.002 file #5 of 9).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

_PYTHON_DIR = Path(__file__).resolve().parent.parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from domain.pattern_miner import mine_bars  # noqa: E402
from infrastructure.mine_report_writer import MineCandidateRow  # noqa: E402
from schemas_bulk import BulkBarRaw  # noqa: E402

# Float-equality tolerance for move_pct comparison. Not a business
# threshold (MINE_MOVE_THRESHOLD stays the only one of those) -- this
# absorbs two independent noise sources: float arithmetic in the
# recompute itself (~1e-12, negligible) AND the candidates CSV's own
# :.6f write precision (mine_report_writer.py), which can round a
# genuinely-unchanged value by up to ~5e-7 (M-092). Stays local rather
# than in config.py -- implementation-level slack, not a business
# threshold.
_MOVE_PCT_EPSILON = 1e-6


@dataclass(frozen=True)
class AuditResult:
    """One approved row's audit outcome. passed=True iff reasons is
    empty. reasons is always populated when passed=False -- never a
    bare boolean with no explanation."""
    symbol: str
    anchor_date: date
    pattern_class: str
    passed: bool
    reasons: list[str] = field(default_factory=list)


def audit_symbol(
    symbol: str,
    bars: list[BulkBarRaw],
    claimed_rows: list[MineCandidateRow],
    existing_keys: set[tuple[str, date]],
) -> list[AuditResult]:
    """Audits one symbol's worth of approved rows against a fresh
    re-mine of its own freshly-read bars. mine_bars() runs exactly
    once per symbol regardless of how many rows are being audited --
    cheap, and matches Phase 1's proven code path exactly rather than
    re-deriving it per row.

    claimed_rows should all share this symbol -- the caller (Phase 2
    orchestrator) is responsible for grouping the approved CSV by
    symbol before calling this.
    """
    fresh = mine_bars(bars)
    fresh_lookup = {
        (c.anchor_date, c.pattern_class): c for c in fresh
    }

    results: list[AuditResult] = []
    for row in claimed_rows:
        reasons: list[str] = []
        match = fresh_lookup.get((row.anchor_date, row.pattern_class))

        if match is None:
            reasons.append(
                "not reproduced by independent re-mine -- stale export, "
                "hand-edited CSV row, or code drift since the CSV was "
                "generated"
            )
        else:
            if match.horizon_days != row.horizon_days:
                reasons.append(
                    f"horizon_days mismatch: claimed {row.horizon_days}, "
                    f"recomputed {match.horizon_days}"
                )
            if abs(match.move_pct - row.move_pct) > _MOVE_PCT_EPSILON:
                reasons.append(
                    f"move_pct mismatch: claimed {row.move_pct:.6f}, "
                    f"recomputed {match.move_pct:.6f}"
                )
            if match.standard_horizon != row.standard_horizon:
                reasons.append(
                    f"standard_horizon mismatch: claimed "
                    f"{row.standard_horizon}, recomputed "
                    f"{match.standard_horizon}"
                )
            if match.bars_since_crossover != row.bars_since_crossover:
                reasons.append(
                    "bars_since_crossover mismatch: claimed "
                    f"{row.bars_since_crossover}, recomputed "
                    f"{match.bars_since_crossover}"
                )
            if match.entry_tier != row.entry_tier:
                reasons.append(
                    f"entry_tier mismatch: claimed {row.entry_tier}, "
                    f"recomputed {match.entry_tier}"
                )

        if (symbol, row.anchor_date) in existing_keys:
            reasons.append(
                "catalog collision: (symbol, anchor_date) already "
                "present in the live catalog"
            )

        results.append(AuditResult(
            symbol=symbol,
            anchor_date=row.anchor_date,
            pattern_class=row.pattern_class,
            passed=not reasons,
            reasons=reasons,
        ))
    return results
