"""paper_spread_reader.py -- reads raw TOS paper AccountStatement.csv and
extracts multi-leg CUSTOM combo fills (WO-P020-E1.002).

Header-detect + TRD-filter logic mirrors P_020_TOS_Parser_v2.4.py's
load_tos_csv(), scoped down to only what's needed here: rows the domain
parser recognizes as multi-leg combos. Single-leg rows are left entirely
alone -- they continue through the existing legacy pipeline unchanged.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd

from domain.spread_leg_parser import parse_multi_leg_description

logger = logging.getLogger(__name__)


def _find_header_row(filepath: Path) -> int:
    """Locate the line index where the real CSV header starts.

    Args:
        filepath: Path to the raw TOS AccountStatement.csv.

    Returns:
        Zero-based row index to pass as skiprows to pandas.

    Raises:
        ValueError: If no header row is found.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.startswith("DATE,TIME,TYPE"):
                return i
    raise ValueError(f"No 'DATE,TIME,TYPE' header found in {filepath}")


def read_spread_fills(filepath: Path) -> List[Dict]:
    """Read a raw paper AccountStatement.csv and extract multi-leg fills.

    Args:
        filepath: Path to the raw TOS AccountStatement.csv.

    Returns:
        List of fill dicts, each with ref, datetime, fees, and a "parsed"
        key (spread_leg_parser output). Rows that aren't recognized
        multi-leg CUSTOM combos are silently omitted -- they're not this
        function's concern.
    """
    header_row = _find_header_row(filepath)
    df = pd.read_csv(filepath, skiprows=header_row, on_bad_lines="skip", engine="python")

    total_rows = len(df)
    df = df[df["TYPE"] == "TRD"].copy()
    logger.info(f"Loaded {total_rows} total rows, {len(df)} TRD transactions")

    fills = []
    for _, row in df.iterrows():
        parsed = parse_multi_leg_description(row.get("DESCRIPTION", ""))
        if parsed is None:
            continue

        date_str = str(row["DATE"]).strip()
        time_str = str(row.get("TIME", "00:00:00")).strip()
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %H:%M:%S")
        except ValueError:
            dt = datetime.strptime(date_str, "%m/%d/%y")

        misc_fees = abs(pd.to_numeric(row.get("Misc Fees", 0), errors="coerce") or 0)
        comm_fees = abs(pd.to_numeric(row.get("Commissions & Fees", 0), errors="coerce") or 0)

        fills.append({
            "ref": str(row.get("REF #", "")).strip().strip("=\""),
            "date": date_str,
            "datetime": dt,
            "fees": round(misc_fees + comm_fees, 2),
            "parsed": parsed,
        })

    logger.info(f"Found {len(fills)} multi-leg spread fill(s)")
    return fills
