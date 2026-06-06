"""cli.py — command-line entry point for the P_115 backfill.

Run from the scripts\ folder with p140 conda env active:

    python -m p115_backfill.cli                  # full backfill
    python -m p115_backfill.cli --dry-run         # preview only
    python -m p115_backfill.cli --limit 10        # first 10 rows (test)
    python -m p115_backfill.cli --overwrite       # overwrite existing notes

Or double-click launch_backfill.bat.
"""

from __future__ import annotations

import argparse
import logging
import sys

# config import bootstraps sys.path for shared_resources
import p115_backfill.config  # noqa: F401
from p115_backfill.application.backfill_runner import run_backfill


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """Parse arguments and run the backfill."""
    parser = argparse.ArgumentParser(
        description="P_115 Excel → Obsidian vault one-time backfill"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Log what would be written without writing anything",
    )
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Overwrite existing vault notes (default: skip existing)",
    )
    parser.add_argument(
        "--limit", type=int, default=None, metavar="N",
        help="Process only the first N rows — use for test runs",
    )
    args = parser.parse_args()

    _setup_logging()

    if args.dry_run:
        logging.getLogger().info("DRY RUN — no files will be written")

    result = run_backfill(
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        limit=args.limit,
    )

    print(
        f"\nDone — read={result.total_read}  written={result.written}  "
        f"skipped={result.total_skipped}  errors={result.errors}"
    )

    if result.error_details:
        print("\nErrors:")
        for err in result.error_details:
            print(f"  {err}")

    sys.exit(1 if result.errors else 0)


if __name__ == "__main__":
    main()
