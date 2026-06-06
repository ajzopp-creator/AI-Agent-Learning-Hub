#!/usr/bin/env python
"""One-shot backfill: re-write all existing P_300 vault notes via fixed parser.

FILE:        backfill_obsidian_notes.py
VERSION:     1.1
DATE:        2026-05-31
AUTHOR:      Anthony Zoppi / Claude
LAYER:       utility (one-shot -- not part of any pipeline)
DESCRIPTION: Scans outputs/reports/ for all report_*.txt files, selects the
             latest report per symbol, and re-writes the corresponding vault
             note using the fixed write_signal_to_obsidian.parse_report_and_write().

             Corrects existing notes with wrong h5_win_rate / h5_mean_ret
             frontmatter values caused by the double-division bug fixed in
             write_signal_to_obsidian.py v1.1.

             Safe to re-run -- idempotent (overwrite=True is the default).

             Run from project root with p140 active.
             IMPORTANT: Use Out-File -Encoding utf8 to capture output -- PowerShell
             default redirection (>) writes UTF-16 LE which produces garbled text
             in editors and is unreadable by Claude (M-019).

             Correct command:
                 python python\backfill_obsidian_notes.py 2>&1 | Out-File -Encoding utf8 backfill_output.txt
                 Get-Content backfill_output.txt | Select-String "COMPLETE|ERROR|Written|Skipped"

CHANGELOG:
  v1.1  2026-05-31  Updated run command in docstring to use Out-File -Encoding utf8
                    instead of > redirection. Added verification command. (M-019)
  v1.0  2026-05-31  Initial version.
"""

import sys
from pathlib import Path
from collections import defaultdict

# Resolve project root (this file is at python/ -- one level below project root)
_PROJ_ROOT = Path(__file__).resolve().parent.parent
_REPORTS_DIR = _PROJ_ROOT / "outputs" / "reports"

# Import the fixed parser from the same package
_PYTHON_DIR = Path(__file__).resolve().parent
if str(_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(_PYTHON_DIR))

from write_signal_to_obsidian import parse_report_and_write  # noqa: E402


def collect_latest_reports(reports_dir: Path) -> dict[str, Path]:
    """Find the latest report file for each symbol.

    Filenames follow: report_SYMBOL_SIGNALDATE_TIMESTAMP.txt
    Sorting descending by filename gives latest timestamp last char-by-char,
    which is equivalent to latest run since timestamps are ISO-formatted.

    Args:
        reports_dir: Directory containing report_*.txt files.

    Returns:
        Dict mapping symbol -> Path of latest report file.
    """
    by_symbol: dict[str, list[Path]] = defaultdict(list)

    for report in reports_dir.glob("report_*_*_*.txt"):
        parts = report.stem.split("_")
        # stem format: report_SYMBOL_SIGNALDATE_TIMESTAMP
        # SYMBOL may contain underscores (rare) -- take parts[1] as symbol
        if len(parts) >= 4:
            symbol = parts[1]
            by_symbol[symbol].append(report)

    latest: dict[str, Path] = {}
    for symbol, files in by_symbol.items():
        latest[symbol] = sorted(files, reverse=True)[0]

    return latest


def main() -> None:
    """Run backfill across all symbols with available reports."""

    if not _REPORTS_DIR.exists():
        print(f"[ERROR] Reports directory not found: {_REPORTS_DIR}")
        sys.exit(1)

    latest_reports = collect_latest_reports(_REPORTS_DIR)

    if not latest_reports:
        print("[SKIP] No report files found.")
        sys.exit(0)

    symbols = sorted(latest_reports.keys())
    total = len(symbols)
    written = 0
    skipped = 0
    errors = 0

    print(f"\n{'=' * 60}")
    print(f"P_300 OBSIDIAN BACKFILL")
    print(f"{'=' * 60}")
    print(f"Reports dir : {_REPORTS_DIR}")
    print(f"Symbols     : {total}")
    print(f"{'=' * 60}\n")

    for symbol in symbols:
        try:
            ok = parse_report_and_write(symbol, _REPORTS_DIR)
            if ok:
                written += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"[ERROR] {symbol}: {type(e).__name__}: {e}")
            errors += 1

    print(f"\n{'=' * 60}")
    print(f"BACKFILL COMPLETE")
    print(f"  Written : {written}")
    print(f"  Skipped : {skipped}")
    print(f"  Errors  : {errors}")
    print(f"  Total   : {total}")
    print(f"{'=' * 60}\n")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
