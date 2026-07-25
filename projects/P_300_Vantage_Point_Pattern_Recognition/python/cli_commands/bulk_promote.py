"""
FILE: cli_commands/bulk_promote.py
VERSION: 1.0
DATE: 2026-07-20
AUTHOR: Anthony Zoppi + Claude
LAYER: cli
DESCRIPTION:
    Staging-build + promote-to-live command handlers + argparse
    registration -- merge-research-catalog, ingest-mined, archive-
    mined. All three either build a staging copy meant to eventually
    promote to the real live catalog.db, or (archive-mined) are the
    paired post-ingest archive step for the ingest-mined flow. Split
    out of the former monolithic cli.py (WO-P300-E4.001, command-
    registry refactor) -- pure cut-and-paste, no behavior change.

    Real gap found and fixed during this WO's build (not a behavior
    change, an inventory correction): the WO's own category table
    (2026-07-14) never listed archive-mined at all -- it was added to
    cli.py the same day the WO was filed (v1.14) and the WO's "15
    subcommands" inventory undercounted by one. Placed here, paired
    with ingest-mined, matching its own docstring ("Run AFTER
    ingest-mined completes successfully -- part of the BulkAddPattern
    process").

    See cli_commands/bulk_research.py's docstring for why this WO
    splits the originally-planned single bulk.py into two files.

CHANGELOG:
    - 2026-07-20 v1.0 (WO-P300-E4.001): split from cli.py v1.14.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config import MODELS_DIR  # noqa: E402


def _cmd_archive_mined(args: argparse.Namespace) -> int:
    """Archive one mined-corpus XLSX to the monthly zip in MINE_ARCHIVE_DIR
    (E:\\ external drive). Run AFTER ingest-mined completes successfully --
    part of the "BulkAddPattern" process."""
    from utilities.archive_mined_file import run_archive as run_archive_mined
    return run_archive_mined(Path(args.xlsx))


def _cmd_merge_research_catalog(args: argparse.Namespace) -> int:
    """WO-P300-E2.003. Two modes based on --promote: build a staging
    merge + eval comparison (default), or promote an already-built
    staging copy to the real live catalog.db (explicit, separate)."""
    from application.catalog_merge_pipeline import (
        build_staging_merge, promote_staging_to_live,
    )

    live_db = Path(args.live_db) if args.live_db else None

    if args.promote:
        staging_path = Path(args.promote)
        if not staging_path.exists():
            print(f"Staging DB not found: {staging_path}", file=sys.stderr)
            return 1
        try:
            promoted_path = promote_staging_to_live(staging_path, live_db)
        except Exception as e:
            print(f"Promotion failed: {e}", file=sys.stderr)
            return 1
        print()
        print(f"PROMOTED -- staging={staging_path} -> live={promoted_path}")
        return 0

    staging_path = (
        Path(args.staging_db) if args.staging_db
        else MODELS_DIR / "staging_merge_catalog.db"
    )
    try:
        result = build_staging_merge(staging_path, live_db)
    except Exception as e:
        print(f"Merge build failed: {e}", file=sys.stderr)
        return 1

    print()
    print(f"STAGING MERGE COMPLETE -- staging={result.staging_path}")
    print(f"inserted={result.merge.inserted_count}  "
          f"skipped_duplicate={result.merge.skipped_duplicate_count}  "
          f"symbols_touched={len(result.merge.symbols_touched)}")
    print(f"pre-merge report:  {result.pre_report_path}")
    print(f"post-merge report: {result.post_report_path}")
    print("Review both reports, then promote with:")
    print(f"  python cli.py merge-research-catalog --promote \"{staging_path}\"")
    return 0


def _cmd_ingest_mined(args: argparse.Namespace) -> int:
    """WO-P300-E3.002 Phase 2 (file #7). Two modes based on --promote:
    build a staging insert of operator-approved mine_candidates.csv rows
    + M-079 eval comparison (default), or promote an already-built
    staging copy to the real live catalog.db (explicit, separate --
    reuses catalog_merge_pipeline.promote_staging_to_live unchanged,
    same promotion mechanics regardless of which pipeline built the
    staging copy)."""
    from application.catalog_merge_pipeline import promote_staging_to_live
    from application.ingest_mined_pipeline import (
        FullRescoreConfirmationRequired, run_ingest_mined,
    )
    from config import DATA_BULK_MINE, MINE_CANDIDATES_CSV, MINE_REPORTS_DIR

    live_db = Path(args.live_db) if args.live_db else None

    if args.promote:
        staging_path = Path(args.promote)
        if not staging_path.exists():
            print(f"Staging DB not found: {staging_path}", file=sys.stderr)
            return 1
        try:
            promoted_path = promote_staging_to_live(staging_path, live_db)
        except Exception as e:
            print(f"Promotion failed: {e}", file=sys.stderr)
            return 1
        print()
        print(f"PROMOTED -- staging={staging_path} -> live={promoted_path}")
        return 0

    csv_path = Path(args.csv) if args.csv else MINE_REPORTS_DIR / MINE_CANDIDATES_CSV
    if not csv_path.exists():
        print(f"Approved candidates CSV not found: {csv_path}", file=sys.stderr)
        return 1
    staging_path = (
        Path(args.staging_db) if args.staging_db
        else MODELS_DIR / "staging_ingest_mined.db"
    )
    input_dir = Path(args.input_dir) if args.input_dir else DATA_BULK_MINE

    try:
        result = run_ingest_mined(
            csv_path, staging_path, live_db, input_dir,
            confirm_full_rescore=args.confirm_full_rescore,
        )
    except FullRescoreConfirmationRequired as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Ingest-mined build failed: {e}", file=sys.stderr)
        return 1

    print()
    print(f"INGEST-MINED COMPLETE -- staging={result.staging_path}")
    print(f"inserted={result.inserted_count}  "
          f"skipped_duplicate={result.skipped_duplicate_count}  "
          f"audit_failed={len(result.audit_failed)}  "
          f"symbols_touched={len(result.symbols_touched)}")
    if result.audit_failed:
        print("audit failures (not inserted):")
        for r in result.audit_failed:
            print(f"  - {r.symbol} {r.anchor_date} ({r.pattern_class}): {r.reasons}")
    print(f"pre-ingest report:  {result.pre_report_path}")
    print(f"post-ingest report: {result.post_report_path}")
    print("Review both reports, then promote with:")
    print(f"  python cli.py ingest-mined --promote \"{staging_path}\"")
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Registers merge-research-catalog, ingest-mined, archive-mined."""
    p_merge = subparsers.add_parser(
        "merge-research-catalog",
        help="WO-P300-E2.003: staging merge of STRICT bulk patterns into "
             "the live catalog, or promote an already-built staging copy.",
    )
    p_merge.add_argument(
        "--staging-db", default=None,
        help="Staging DB output path (build mode); defaults to "
             "models/staging_merge_catalog.db.",
    )
    p_merge.add_argument(
        "--live-db", default=None,
        help="Live catalog path override; defaults to get_latest_catalog().",
    )
    p_merge.add_argument(
        "--promote", default=None, metavar="STAGING_DB_PATH",
        help="Promote this staging DB to the real live catalog.db instead "
             "of building a new staging merge. Separate, explicit action.",
    )
    p_merge.set_defaults(func=_cmd_merge_research_catalog)

    p_ingest_mined = subparsers.add_parser(
        "ingest-mined",
        help="WO-P300-E3.002 phase 2: audit-gate + staging-insert "
             "operator-approved mine_candidates.csv rows, or promote an "
             "already-built staging copy.",
    )
    p_ingest_mined.add_argument(
        "--csv", default=None,
        help="Approved candidates CSV path override; defaults to "
             "config.MINE_REPORTS_DIR / config.MINE_CANDIDATES_CSV.",
    )
    p_ingest_mined.add_argument(
        "--input-dir", default=None,
        help="Mine XLSX input dir override (re-read fresh from disk, "
             "never trusts Phase 1's in-memory result); defaults to "
             "config.DATA_BULK_MINE.",
    )
    p_ingest_mined.add_argument(
        "--staging-db", default=None,
        help="Staging DB output path (build mode); defaults to "
             "models/staging_ingest_mined.db.",
    )
    p_ingest_mined.add_argument(
        "--live-db", default=None,
        help="Live catalog path override; defaults to get_latest_catalog().",
    )
    p_ingest_mined.add_argument(
        "--promote", default=None, metavar="STAGING_DB_PATH",
        help="Promote this staging DB to the real live catalog.db instead "
             "of building a new staging ingest. Separate, explicit action.",
    )
    p_ingest_mined.add_argument(
        "--confirm-full-rescore", action="store_true",
        help="WO-P300-E5.004: required to proceed past a cold M-079 "
             "pre-cache full serial rescore (can take hours -- see the "
             "printed estimate). Without this flag, a cache miss refuses "
             "and exits rather than running automatically.",
    )
    p_ingest_mined.set_defaults(func=_cmd_ingest_mined)

    p_arch_mine = subparsers.add_parser(
        "archive-mined",
        help="Archive a mined-corpus XLSX to the monthly zip in "
             "config.MINE_ARCHIVE_DIR. Run AFTER ingest-mined.",
    )
    p_arch_mine.add_argument(
        "--xlsx", required=True,
        help="Path to the <years>[I]_Pattern_<SYMBOL>.xlsx to archive.",
    )
    p_arch_mine.set_defaults(func=_cmd_archive_mined)
