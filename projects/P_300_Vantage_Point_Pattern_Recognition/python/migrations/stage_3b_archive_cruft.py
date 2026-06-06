"""
FILE: stage_3b_archive_cruft.py
VERSION: 1.0
DATE: 2026-05-13
AUTHOR: Anthony Zoppi + Claude
LAYER: migration
DESCRIPTION: One-shot Stage 3b migration. Archives all Gemini-era /
    pre-rebuild legacy artifacts from python/ and models/ into archive
    folders, preserving relative paths inside the archive for forensic
    value. Supports --dry-run to preview without moving. Idempotent —
    missing sources and pre-existing destinations are logged and skipped.

    Strategy:
    1. Whole-directory moves for pre-rebuild layer dirs (ingest, labeling,
       feature_engineering, parsers, input, output, matching, reporting,
       python/tests, models/schema).
    2. Individual file moves for legacy scripts at python/ root, model
       database files, model loose .py files, and project-root risk_config.
    3. Sweep of python/utilities/ — keep only db_utils.py, __init__.py,
       .vscode/, __pycache__/. Everything else moves to archive.
    4. Delete stale __pycache__/ dirs that reference moved files.
CHANGELOG:
    - 2026-05-13 v1.0: Initial full-sweep cleanup for Stage 3.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("stage_3b")

# Script lives at <project>/python/migrations/stage_3b_archive_cruft.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRY_RUN = False

# ---------------------------------------------------------------------------
# Move manifests — relative to PROJECT_ROOT, forward slashes (Path handles it)
# ---------------------------------------------------------------------------

# Whole-directory moves: archived intact, preserving directory name.
DIRECTORY_MOVES = (
    ("python/ingest",              "python/archive/legacy_layers/ingest"),
    ("python/labeling",            "python/archive/legacy_layers/labeling"),
    ("python/feature_engineering", "python/archive/legacy_layers/feature_engineering"),
    ("python/parsers",             "python/archive/legacy_layers/parsers"),
    ("python/input",               "python/archive/legacy_layers/input"),
    ("python/output",              "python/archive/legacy_layers/output"),
    ("python/matching",            "python/archive/legacy_layers/matching"),
    ("python/reporting",           "python/archive/legacy_layers/reporting"),
    ("python/tests",               "python/archive/legacy_tests"),
    ("models/schema",              "models/archive/schema"),
)

# Individual file moves.
FILE_MOVES = (
    # python/ root legacy scripts
    ("python/old_P_300_vantagepoint_batch_convert_v6.py",
     "python/archive/legacy_root/old_P_300_vantagepoint_batch_convert_v6.py"),
    ("python/P_300_Intraday_VPCheck_v2.6.py",
     "python/archive/legacy_root/P_300_Intraday_VPCheck_v2.6.py"),
    ("python/P_300_Posture_V2.4.py",
     "python/archive/legacy_root/P_300_Posture_V2.4.py"),
    ("python/P_300_Posture_V2.5.py",
     "python/archive/legacy_root/P_300_Posture_V2.5.py"),
    ("python/P_300_Posture_v2.6.py",
     "python/archive/legacy_root/P_300_Posture_v2.6.py"),
    ("python/P_300_vantagepoint_batch_convert_v1.py",
     "python/archive/legacy_root/P_300_vantagepoint_batch_convert_v1.py"),
    ("python/P_300_vantagepoint_batch_convert_v2.py",
     "python/archive/legacy_root/P_300_vantagepoint_batch_convert_v2.py"),
    ("python/P_300_vantagepoint_batch_convert_v3.py",
     "python/archive/legacy_root/P_300_vantagepoint_batch_convert_v3.py"),
    ("python/P_300_vantagepoint_batch_convert_v4.py",
     "python/archive/legacy_root/P_300_vantagepoint_batch_convert_v4.py"),
    ("python/P_300_vantagepoint_batch_convert_v5.py",
     "python/archive/legacy_root/P_300_vantagepoint_batch_convert_v5.py"),
    ("python/risk_config.json",
     "python/archive/legacy_root/risk_config.json"),
    # models/ database files + zip
    ("models/051026geminicatalog.db",
     "models/archive/databases/051026geminicatalog.db"),
    ("models/051126geminicatalog.db",
     "models/archive/databases/051126geminicatalog.db"),
    ("models/anothercorrupted_051126geminicatalog.db",
     "models/archive/databases/anothercorrupted_051126geminicatalog.db"),
    ("models/corrupted_051126geminicatalog.db",
     "models/archive/databases/corrupted_051126geminicatalog.db"),
    ("models/empty_ catalog.db",
     "models/archive/databases/empty_ catalog.db"),
    ("models/pre_051126geminicatalog - Copy.db",
     "models/archive/databases/pre_051126geminicatalog - Copy.db"),
    ("models/Archivegeminicatalog.zip",
     "models/archive/databases/Archivegeminicatalog.zip"),
    # models/ loose .py files
    ("models/check_rows.py",           "models/archive/loose/check_rows.py"),
    ("models/debug_db.py",             "models/archive/loose/debug_db.py"),
    ("models/hydrate.py",              "models/archive/loose/hydrate.py"),
    ("models/intelliscan.py",          "models/archive/loose/intelliscan.py"),
    ("models/pattern_instance.py",     "models/archive/loose/pattern_instance.py"),
    ("models/performance_dashboard.py","models/archive/loose/performance_dashboard.py"),
    ("models/sanitize_db.py",          "models/archive/loose/sanitize_db.py"),
    ("models/seed_data.py",            "models/archive/loose/seed_data.py"),
    ("models/sync_catalog.py",         "models/archive/loose/sync_catalog.py"),
    ("models/validate_catalog.py",     "models/archive/loose/validate_catalog.py"),
    # project root legacy
    ("risk_config.json", "data/archive/legacy_root/risk_config.json"),
)

# python/utilities/ sweep — keep these names; archive everything else.
UTILITIES_KEEP = {"db_utils.py", "__init__.py", ".vscode", "__pycache__"}

# Stale __pycache__ dirs that reference soon-to-be-moved files. Safe to delete;
# Python regenerates as needed on next import.
CACHE_DIRS_TO_DELETE = (
    "python/__pycache__",
    "python/utilities/__pycache__",
)


def move_path(src_rel: str, dst_rel: str) -> None:
    """Move a file or directory from src to dst. Idempotent and dry-run aware."""
    src = PROJECT_ROOT / src_rel
    dst = PROJECT_ROOT / dst_rel
    if not src.exists():
        log.info("SKIP     %s (source missing — already moved?)", src_rel)
        return
    if dst.exists():
        log.warning("CONFLICT %s -> %s (destination exists; skipping)", src_rel, dst_rel)
        return
    if DRY_RUN:
        log.info("DRY      %s -> %s", src_rel, dst_rel)
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    log.info("MOVED    %s -> %s", src_rel, dst_rel)


def sweep_utilities() -> None:
    """Archive everything in python/utilities/ except items in UTILITIES_KEEP."""
    util_dir = PROJECT_ROOT / "python" / "utilities"
    if not util_dir.exists():
        log.warning("python/utilities/ not found — skipping sweep")
        return
    for item in sorted(util_dir.iterdir()):
        if item.name in UTILITIES_KEEP:
            log.info("KEEP     python/utilities/%s", item.name)
            continue
        rel_src = f"python/utilities/{item.name}"
        rel_dst = f"python/archive/legacy_utilities/{item.name}"
        move_path(rel_src, rel_dst)


def delete_cache(rel_path: str) -> None:
    """Delete a stale __pycache__ dir. Idempotent and dry-run aware."""
    target = PROJECT_ROOT / rel_path
    if not target.exists():
        log.info("SKIP     %s (already gone)", rel_path)
        return
    if DRY_RUN:
        log.info("DRY      delete %s", rel_path)
        return
    shutil.rmtree(target)
    log.info("DELETED  %s (stale cache)", rel_path)


def main() -> None:
    global DRY_RUN
    parser = argparse.ArgumentParser(description="Stage 3b — archive legacy cruft.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview moves without touching files.")
    args = parser.parse_args()
    DRY_RUN = args.dry_run

    log.info("Stage 3b cruft archive%s", " (DRY RUN)" if DRY_RUN else "")
    log.info("Project root: %s", PROJECT_ROOT)

    log.info("--- Directory moves ---")
    for src, dst in DIRECTORY_MOVES:
        move_path(src, dst)

    log.info("--- File moves ---")
    for src, dst in FILE_MOVES:
        move_path(src, dst)

    log.info("--- Utilities sweep ---")
    sweep_utilities()

    log.info("--- Cache cleanup ---")
    for cache in CACHE_DIRS_TO_DELETE:
        delete_cache(cache)

    log.info("Stage 3b %s.", "dry-run complete" if DRY_RUN else "complete")


if __name__ == "__main__":
    main()
