"""Tests for infrastructure.paper_order_history_parser -- the TOS
Account Order History CSV section parser (WO-P400-E6.001 paper-path
Tier 1). Fixed-position column parsing + TRG BY bracket reassembly are
the two riskiest, previously-unverified behaviors here.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from infrastructure.paper_order_history_parser import (
    _clean_status,
    _extract_order_id,
    _to_iso_datetime,
    parse_order_history,
)


def _row(time_placed="", spread="", status="", order_id="") -> list:
    """16-column row matching the section's fixed layout; only the
    fields a given test cares about are ever non-blank."""
    cols = [""] * 16
    cols[2] = time_placed
    cols[3] = spread
    cols[4] = "BUY"
    cols[5] = "+1"
    cols[6] = "TO OPEN"
    cols[7] = "SPY"
    cols[10] = "STOCK"
    cols[11] = "3.16"
    cols[14] = status
    cols[15] = order_id
    return cols


def test_extract_order_id_strips_excel_wrapper():
    assert _extract_order_id('="1000"') == "1000"


def test_clean_status_strips_count_prefix():
    assert _clean_status("(0) FILLED") == "FILLED"


def test_to_iso_datetime_converts_tos_format():
    assert _to_iso_datetime("9/8/26 09:30:00") == "2026-09-08T09:30:00"


def test_parse_order_history_reassembles_trg_by_bracket(tmp_path):
    """A TRG BY annotation row must nest the following order under its
    parent's childOrderStrategies and flip the parent to TRIGGER."""
    csv_path = tmp_path / "statement.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Account Order History"])
        writer.writerow(["header row -- content unused, skipped by position"])
        writer.writerow(_row("9/8/26 09:30:00", "", "(0) FILLED", '="1000"'))
        writer.writerow(_row("9/8/26 09:31:00", "", "(0) FILLED", '="1001"'))
        writer.writerow(_row("", "TRG BY #1000", "", ""))
        writer.writerow([])

    roots = parse_order_history(csv_path)

    assert len(roots) == 1
    parent = roots[0]
    assert parent["orderId"] == 1000
    assert parent["orderStrategyType"] == "TRIGGER"
    assert len(parent["childOrderStrategies"]) == 1
    assert parent["childOrderStrategies"][0]["orderId"] == 1001
