"""P_400 application: audit open book vs. real Schwab positions.

Tony directive, 2026-07-24. Cross-references PENDING/SUBMITTED/FILLED/
T1_HIT/TRAILING book records against what's actually held in the AJZ
account. Read-only -- never edits book records; flags mismatches for
Tony to correct by hand, then re-run screen-all.
"""

from __future__ import annotations

from config import BOOK_DIR
from domain.portfolio import OPEN_STATUSES
from infrastructure.book_loader import load_book
from infrastructure.schwab_positions import get_real_positions


def cmd_audit_book() -> int:
    """Print book-vs-broker reconciliation for open-status records."""
    records = load_book(BOOK_DIR)
    open_records = [r for r in records if r.status.upper() in OPEN_STATUSES]

    try:
        real = get_real_positions()
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Could not fetch real positions: {exc}")
        return 1

    print("=" * 62)
    print(f"BOOK-VS-BROKER AUDIT  |  AJZ_Strategies  |  book has {len(open_records)} open")
    print("=" * 62)

    book_symbols = {r.symbol.upper() for r in open_records}
    mismatches = 0

    for r in open_records:
        sym = r.symbol.upper()
        if sym in real:
            print(f"  MATCH    {sym:<8} book={r.status:<10} broker_qty={real[sym]}")
        else:
            mismatches += 1
            print(f"  NO MATCH {sym:<8} book={r.status:<10} -- not held in AJZ "
                  f"(likely paper, mistagged)")

    extra = set(real) - book_symbols
    if extra:
        print("-" * 62)
        print("  Held in AJZ but not in P_400 open book (not P_400-managed, or book stale):")
        for sym in sorted(extra):
            print(f"    {sym:<8} broker_qty={real[sym]}")

    print("=" * 62)
    confirmed = len(open_records) - mismatches
    print(f"  {confirmed}/{len(open_records)} book records confirmed real. "
          f"{mismatches} mismatch(es) -- correct lifecycle_status by hand, "
          f"then re-run screen-all.")
    return 0