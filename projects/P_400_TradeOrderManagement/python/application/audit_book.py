"""P_400 application: audit open book vs. real Schwab positions.

Tony directive, 2026-07-24. Cross-references PENDING/SUBMITTED/FILLED/
T1_HIT/TRAILING book records against what's actually held in the AJZ
account. Read-only -- never edits book records; flags mismatches for
Tony to correct by hand, then re-run screen-all.

External-position handling (WO-P400-E6.003, 2026-08-20): records tagged
with source_label are positions from paid subscription services, never
P_400-managed. They get their own report section instead of being
flagged as generic untracked noise.
"""

from __future__ import annotations

from typing import Dict, List

from config import BOOK_DIR
from domain.portfolio import OPEN_STATUSES
from infrastructure.book_loader import load_book
from infrastructure.schwab_positions import get_real_positions
from schemas import BookRecord


def _audit_managed(records: List[BookRecord], real: Dict[str, float]) -> int:
    """Print MATCH/NO MATCH lines for P_400-managed records. Returns mismatch count."""
    mismatches = 0
    for r in records:
        sym = r.symbol.upper()
        if sym in real:
            print(f"  MATCH    {sym:<8} book={r.status:<10} broker_qty={real[sym]}")
        else:
            mismatches += 1
            print(f"  NO MATCH {sym:<8} book={r.status:<10} -- not held in AJZ "
                  f"(likely paper, mistagged)")
    return mismatches


def _audit_external(records: List[BookRecord], real: Dict[str, float]) -> None:
    """Print the known-external section -- confirmed held or possibly closed."""
    if not records:
        return
    print("-" * 62)
    print("  Known external, not P_400-managed:")
    for r in records:
        sym = r.symbol.upper()
        vehicle = r.vehicle or "?"
        if sym in real:
            print(f"    {sym:<8} source={r.source_label:<8} vehicle={vehicle:<24} "
                  f"qty={r.qty} -- confirmed held")
        else:
            print(f"    {sym:<8} source={r.source_label:<8} vehicle={vehicle:<24} "
                  f"qty={r.qty} -- NOT found in broker (closed? update book by hand)")


def cmd_audit_book() -> int:
    """Print book-vs-broker reconciliation for open-status records."""
    records = load_book(BOOK_DIR)
    open_records = [r for r in records if r.status.upper() in OPEN_STATUSES]
    managed = [r for r in open_records if not r.source_label]
    external = [r for r in open_records if r.source_label]

    try:
        real = get_real_positions()
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Could not fetch real positions: {exc}")
        return 1

    print("=" * 62)
    print(f"BOOK-VS-BROKER AUDIT  |  AJZ_Strategies  |  book has {len(open_records)} open "
          f"({len(managed)} managed, {len(external)} external)")
    print("=" * 62)

    mismatches = _audit_managed(managed, real)
    _audit_external(external, real)

    book_symbols = {r.symbol.upper() for r in open_records}
    extra = set(real) - book_symbols
    if extra:
        print("-" * 62)
        print("  Held in AJZ but not in P_400 open book (not P_400-managed, or book stale):")
        for sym in sorted(extra):
            print(f"    {sym:<8} broker_qty={real[sym]}")

    print("=" * 62)
    confirmed = len(managed) - mismatches
    print(f"  {confirmed}/{len(managed)} P_400-managed records confirmed real. "
          f"{mismatches} mismatch(es) -- correct lifecycle_status by hand, "
          f"then re-run screen-all.")
    return 0