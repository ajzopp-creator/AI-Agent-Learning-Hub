"""
FILE: tests/mine_ground_truth.py
VERSION: 1.0
DATE: 2026-07-13
AUTHOR: Anthony Zoppi + Claude
LAYER: tests (shared fixture/reference data, not a test itself)
DESCRIPTION:
    Real ground-truth anchors for validating domain/pattern_miner.py --
    Tony's actual manual AddPattern picks, extracted from archived
    source filenames (data/processed/2026-0[567].zip + "History Grid
    0526.zip", start-date token = anchor date).

    Rebuilt as a permanent, versioned file after being ad-hoc re-derived
    three times in one session (2026-07-13) via disposable PEH scripts
    -- 66 anchors/30 symbols (first extraction) -> 84 anchors/40 symbols
    (corrected, this version) after two real bugs were found and fixed
    in the extraction logic itself:

    (1) Filename regex required an 8-digit archive-date prefix
        (`20260615_Pattern_...`). Some real archived files are plain
        `Pattern_<start>_<end>_<SYMBOL>.xlsx` with no prefix -- found
        via a GOOGL anchor-date mismatch (see exclusion note below),
        confirmed to affect 19 symbols total: 10 with zero picks under
        the old regex (AMD/BAC/CAT/CVX/GS/META/NKE/SPY/WMT/XOM) and 9
        undercounted (AVGO/CRK/DE/GOOGL/HAL/LMT/MSTR/NVDA/UI).
    (2) None -- this file's extraction is filename-based only (symbol +
        start-date token); the "try opposite direction / adjacent bar"
        fix belongs in the VALIDATION script (matching logic), not
        here -- this file states raw picks, not resolved outcomes.

    KNOWN EXCLUSION -- GOOGL 2026-04-04 -> 2026-04-17 (+24.59%, 14 days):
    Tony's own live example (walked through on-chart, 2026-07-13) of
    his actual selection process (support-triggered entry, resistance-
    triggered exit) is NOT in this list. Confirmed with Tony: this pick
    was never run through AddPattern -- no archived file exists for it
    (checked directly: no filename anywhere in the 4 zips contains
    "20260404"). GOOGL's only archived anchor is 2026-03-18, which
    IS the real ground truth for this symbol, not a mis-extraction.

    Symbol coverage: 40 symbols targeted (30 from the original mine/
    staging + AMD/BAC/CAT/CVX/GS/META/NKE/SPY/WMT/XOM, recovered by
    fix (1) above) all confirmed present in data/bulk/mine/.

    Usage: `from mine_ground_truth import GROUND_TRUTH` -- a list of
    (symbol: str, anchor_date: date) tuples, deduplicated.

CHANGELOG:
    - 2026-07-13 v1.0: Initial permanent version. 84 anchors / 40
      symbols. Supersedes three ad-hoc PEH-script extractions this
      session (66/30 original, then intermediate GOOGL-specific and
      regex-gap-audit passes that were never materialized as a file).
"""
from __future__ import annotations

from datetime import date

GROUND_TRUTH: list[tuple[str, date]] = [
    ("ADBE", date(2026, 1, 2)),
    ("ADBE", date(2026, 2, 23)),
    ("ADBE", date(2026, 3, 12)),
    ("AMD", date(2025, 8, 18)),
    ("AME", date(2026, 3, 2)),
    ("AMZN", date(2026, 2, 3)),
    ("AMZN", date(2026, 3, 30)),
    ("ARDX", date(2026, 1, 5)),
    ("ARDX", date(2026, 2, 3)),
    ("ARDX", date(2026, 3, 5)),
    ("ARDX", date(2026, 4, 29)),
    ("ASTS", date(2025, 9, 29)),
    ("ASTS", date(2025, 10, 29)),
    ("ASTS", date(2025, 12, 1)),
    ("ASTS", date(2025, 12, 31)),
    ("ASTS", date(2026, 2, 9)),
    ("ASTS", date(2026, 5, 11)),
    ("AVGO", date(2025, 6, 13)),
    ("AVGO", date(2026, 4, 6)),
    ("BAC", date(2026, 1, 29)),
    ("BLK", date(2026, 2, 23)),
    ("BLK", date(2026, 4, 1)),
    ("BOIL", date(2026, 1, 16)),
    ("BOIL", date(2026, 2, 2)),
    ("BURL", date(2025, 12, 16)),
    ("CAT", date(2025, 6, 25)),
    ("CIEN", date(2026, 3, 6)),
    ("CIEN", date(2026, 4, 29)),
    ("CRK", date(2026, 1, 16)),
    ("CRK", date(2026, 1, 30)),
    ("CRK", date(2026, 2, 2)),
    ("CRK", date(2026, 3, 27)),
    ("CRK", date(2026, 3, 30)),
    ("CRM", date(2026, 1, 27)),
    ("CRM", date(2026, 5, 14)),
    ("CVX", date(2026, 2, 10)),
    ("DE", date(2025, 11, 20)),
    ("DE", date(2026, 2, 17)),
    ("DVN", date(2025, 10, 10)),
    ("DVN", date(2026, 4, 7)),
    ("GOOGL", date(2025, 12, 12)),
    ("GOOGL", date(2026, 3, 18)),
    ("GS", date(2026, 1, 22)),
    ("HAL", date(2025, 10, 9)),
    ("HAL", date(2026, 3, 17)),
    ("ICE", date(2026, 2, 6)),
    ("INTC", date(2025, 5, 14)),
    ("INTC", date(2025, 6, 13)),
    ("ITW", date(2026, 1, 29)),
    ("LEN", date(2026, 1, 8)),
    ("LMT", date(2025, 9, 2)),
    ("LMT", date(2026, 1, 2)),
    ("META", date(2025, 11, 5)),
    ("MOS", date(2026, 3, 17)),
    ("MSTR", date(2026, 1, 21)),
    ("MSTR", date(2026, 1, 28)),
    ("MSTR", date(2026, 4, 8)),
    ("MSTR", date(2026, 4, 13)),
    ("NKE", date(2025, 9, 15)),
    ("NVDA", date(2025, 10, 24)),
    ("NVDA", date(2025, 11, 3)),
    ("NVDA", date(2026, 1, 30)),
    ("NVDA", date(2026, 3, 30)),
    ("NVDA", date(2026, 5, 5)),
    ("PCAR", date(2026, 3, 30)),
    ("QCOM", date(2026, 1, 12)),
    ("SHW", date(2026, 4, 7)),
    ("SPY", date(2025, 6, 20)),
    ("TDC", date(2026, 1, 29)),
    ("TDC", date(2026, 2, 4)),
    ("TDC", date(2026, 2, 5)),
    ("TDC", date(2026, 3, 4)),
    ("TDC", date(2026, 3, 30)),
    ("TDC", date(2026, 4, 29)),
    ("TECK", date(2026, 2, 6)),
    ("TECK", date(2026, 3, 30)),
    ("TECK", date(2026, 5, 4)),
    ("TECK", date(2026, 5, 20)),
    ("UI", date(2026, 2, 2)),
    ("UI", date(2026, 2, 5)),
    ("UI", date(2026, 3, 31)),
    ("UI", date(2026, 5, 6)),
    ("WMT", date(2026, 2, 25)),
    ("XOM", date(2026, 1, 15)),
]
