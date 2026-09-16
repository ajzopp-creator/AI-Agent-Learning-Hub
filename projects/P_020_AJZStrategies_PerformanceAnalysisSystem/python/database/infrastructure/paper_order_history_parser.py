"""paper_order_history_parser.py -- parses the raw TOS/paperMoney Account
Statement CSV's "Account Order History" section into Schwab-shaped raw
order dicts, so domain/order_linkage.py and domain/order_reconciler.py
run UNCHANGED for paper orders too -- Tony's call (2026-09-07): the same
reconciliation logic applies to both paper and live, not a parallel
paper-only pipeline.

Section format (confirmed live against a real 2026-07-27 YTD paper
statement, D_020_2026-07-27_YTD_AccountStatement.csv): starts at a line
beginning "Account Order History", header row on the next line has two
UNLABELED columns (a leading blank, and the order type LMT/MKT/STP) --
this parser maps by FIXED POSITION, not by header name. Ends at the
first blank line.

TOS represents a bracket as multiple flat rows with linkage annotations
in the Spread column ("TRG BY #<id>", "OCO #<id>", "RE #<id>") instead
of Schwab's nested childOrderStrategies tree -- this parser reconstructs
an equivalent nested shape from "TRG BY #<id>" annotations (an order's
child points at its trigger parent by ID). Two or more children of the
same parent get orderStrategyType='TRIGGER' on the parent, matching
Schwab's vocabulary -- order_linkage.py doesn't branch on this value, it
only affects diagnostics.

Known v1 simplifications (Tony's call, 2026-09-07 -- go-ahead given "logic
should be the same for paper and schwab"):
  - Multi-leg combo orders (IRON CONDOR, VERTICAL, etc.) collapse to
    their primary leg only -- the row carrying the actual Order ID/Time
    Placed/Status. Continuation leg rows (blank Order ID, just
    Side/Qty/Pos Effect/Symbol/strike/type) aren't modeled as separate
    legs. Same simplification order_linkage.py already makes for Schwab
    spreads.
  - "RE #<id>" (order replaced/modified) rows are skipped, not
    chain-followed to the order they replaced.
  - No distinct fill timestamp exists in this section (only "Time
    Placed") -- closeTime is set equal to enteredTime as a best-effort
    approximation for FILLED orders. Paper data is inherently
    lower-fidelity than live; this is an accepted limitation, not a bug.
  - MKT orders show '~' instead of a price in this section (the actual
    fill price only appears in the separate Account Trade History
    section, out of scope here) -- avg_fill_price comes back None for
    these, and order_reconciler.py already handles a None fill price by
    returning no P&L rather than fabricating one.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   infrastructure (I/O + format translation)
"""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

_SECTION_START = "Account Order History"
_ORDER_ID_RE = re.compile(r'="?(\d+)"?')
_LEADING_COUNT_RE = re.compile(r'^\(\d+\)\s*')

# Fixed column positions in the Order History header row (two columns
# are unlabeled in the raw export: position 1 is always blank, position
# 12 is the order type LMT/MKT/STP -- mislabeled blank in the header).
_COL_TIME_PLACED = 2
_COL_SPREAD = 3
_COL_SIDE = 4
_COL_QTY = 5
_COL_POS_EFFECT = 6
_COL_SYMBOL = 7
_COL_TYPE = 10
_COL_PRICE = 11
_COL_STATUS = 14
_COL_ORDER_ID = 15


def _extract_order_id(raw: str) -> Optional[str]:
    """Strip TOS's Excel-formula wrapper: ="12345" -> "12345"."""
    if not raw:
        return None
    m = _ORDER_ID_RE.search(raw)
    return m.group(1) if m else None


def _find_section_rows(path: Path) -> List[List[str]]:
    """Return the raw CSV rows of the Account Order History section only.

    Args:
        path: Path to a raw TOS/paperMoney Account Statement CSV export.

    Returns:
        List of row field-lists, starting right after the section's own
        header row, up to (not including) the first blank line. Empty
        list if the section isn't found.
    """
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    start = None
    for i, row in enumerate(rows):
        if row and row[0].strip().startswith(_SECTION_START):
            start = i + 2  # skip the section title line AND its header row
            break
    if start is None:
        return []

    section_rows = []
    for row in rows[start:]:
        if not any(cell.strip() for cell in row):
            break
        section_rows.append(row)
    return section_rows


def _is_primary_order_row(row: List[str]) -> bool:
    """A real order's primary row has both a Time Placed and an Order ID.

    Multi-leg combo continuation rows and TRG BY/OCO/RE annotation rows
    both lack at least one of these.
    """
    return (
        len(row) > _COL_ORDER_ID
        and row[_COL_TIME_PLACED].strip() != ""
        and _extract_order_id(row[_COL_ORDER_ID]) is not None
    )


def _parse_trg_by(row: List[str]) -> Optional[str]:
    """Return the parent order_id from a 'TRG BY #<id>' annotation row,
    or None if this row isn't one (including OCO/RE rows, which carry no
    parent-linkage information themselves -- OCO siblings are already
    both children of the same TRG BY parent)."""
    if len(row) <= _COL_SPREAD:
        return None
    cell = row[_COL_SPREAD].strip()
    if cell.startswith("TRG BY #"):
        return cell[len("TRG BY #"):].strip()
    return None


def _to_iso_datetime(tos_ts: str) -> Optional[str]:
    """Convert TOS 'M/D/YY HH:MM:SS' to ISO 'YYYY-MM-DDTHH:MM:SS'.

    order_reconciler._to_date() reads the first 10 chars as an ISO date.
    TOS paper timestamps are not ISO -- convert here so the live-path
    _to_date() stays unchanged.
    """
    tos_ts = (tos_ts or "").strip()
    if not tos_ts:
        return None
    for fmt in ("%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.strptime(tos_ts, fmt).strftime("%Y-%m-%dT%H:%M:%S")
        except ValueError:
            continue
    return None


def _to_float(s: str) -> Optional[float]:
    """Best-effort float parse -- returns None for TOS's non-numeric
    price placeholders ('~' for MKT, 'BASE+X'/'BASE-X' relative stops,
    'DEBIT'/'CREDIT' combo net price)."""
    s = (s or "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def _clean_status(raw: str) -> str:
    """Strip a leading '(N) ' count prefix, e.g. '(0) EXPIRED' -> 'EXPIRED'."""
    return _LEADING_COUNT_RE.sub("", (raw or "").strip()) or "UNKNOWN"


def _build_order_dict(row: List[str]) -> dict:
    """Convert one primary order row into a Schwab-shaped raw order dict.

    Same field names domain/order_linkage.py's _parse_node() already
    reads: orderId, status, orderStrategyType, enteredTime, closeTime,
    orderLegCollection[0].{instrument.symbol/assetType/putCall,
    quantity}, top-level 'price' (fill-price fallback when no
    orderActivityCollection is present -- there never is one here).
    """
    order_id = _extract_order_id(row[_COL_ORDER_ID])
    qty_raw = row[_COL_QTY].strip()
    qty = abs(int(qty_raw)) if qty_raw.lstrip("+-").isdigit() else None
    instrument_type = row[_COL_TYPE].strip()
    asset_type = "OPTION" if instrument_type in ("CALL", "PUT") else "EQUITY"
    entered_time = _to_iso_datetime(row[_COL_TIME_PLACED])

    return {
        "orderId": int(order_id),
        "status": _clean_status(row[_COL_STATUS]),
        "orderStrategyType": "SINGLE",
        "enteredTime": entered_time,
        "closeTime": entered_time,  # no distinct fill time in this section
        "price": _to_float(row[_COL_PRICE]),
        "orderLegCollection": [{
            "instrument": {
                "symbol": row[_COL_SYMBOL].strip(),
                "assetType": asset_type,
                "putCall": instrument_type if asset_type == "OPTION" else None,
            },
            "quantity": qty,
        }],
        "childOrderStrategies": [],
    }


def parse_order_history(path: Path) -> List[dict]:
    """Parse the Account Order History section into Schwab-shaped raw
    order dicts, with brackets reassembled from TRG BY annotations into
    childOrderStrategies -- ready for
    domain.order_linkage.build_order_chain() unchanged.

    Args:
        path: Path to a raw TOS/paperMoney Account Statement CSV export.

    Returns:
        List of root-level order dicts (entries), each with its bracket
        children (if any) nested under childOrderStrategies. An order
        that is itself someone else's child is not also returned at the
        top level.
    """
    rows = _find_section_rows(path)

    orders: Dict[str, dict] = {}
    order_sequence: List[str] = []
    parent_by_order_id: Dict[str, str] = {}
    pending_parent: Optional[str] = None
    current_order_id: Optional[str] = None

    for row in rows:
        if _is_primary_order_row(row):
            if current_order_id is not None and pending_parent is not None:
                parent_by_order_id[current_order_id] = pending_parent
            order_dict = _build_order_dict(row)
            order_id = str(order_dict["orderId"])
            orders[order_id] = order_dict
            order_sequence.append(order_id)
            current_order_id = order_id
            pending_parent = None
        else:
            parent = _parse_trg_by(row)
            if parent:
                pending_parent = parent
    if current_order_id is not None and pending_parent is not None:
        parent_by_order_id[current_order_id] = pending_parent

    roots = []
    for order_id in order_sequence:
        order = orders[order_id]
        parent_id = parent_by_order_id.get(order_id)
        if parent_id and parent_id in orders:
            orders[parent_id]["childOrderStrategies"].append(order)
        else:
            roots.append(order)

    for order in orders.values():
        if len(order["childOrderStrategies"]) >= 1:
            order["orderStrategyType"] = "TRIGGER"

    return roots
