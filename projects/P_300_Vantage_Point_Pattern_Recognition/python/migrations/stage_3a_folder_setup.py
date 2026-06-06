"""
FILE: stage_3a_folder_setup.py
VERSION: 1.1
DATE: 2026-05-13
AUTHOR: Anthony Zoppi + Claude
LAYER: migration
DESCRIPTION: One-shot Stage 3a migration. Creates the Hub-standard folder
    structure for the P_300 project: python-layer packages (domain,
    infrastructure, application, migrations, utilities) with __init__.py
    markers, and project-root non-package dirs (tests, data/archive,
    models/archive) with .gitkeep markers. Idempotent — safe to re-run.
CHANGELOG:
    - 2026-05-13 v1.0: Initial migration for Stage 3 folder setup.
    - 2026-05-13 v1.1: Route logging to stdout (stream=sys.stdout) so
      PowerShell doesn't flag INFO output as NativeCommandError. Per M-011.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("stage_3a")

# Script lives at <project>/python/migrations/stage_3a_folder_setup.py
# parents[0] = migrations, parents[1] = python, parents[2] = project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTHON_PACKAGES = (
    "python/domain",
    "python/infrastructure",
    "python/application",
    "python/migrations",
    "python/utilities",
)

PLAIN_DIRS = (
    "tests",
    "data/archive",
    "models/archive",
)


def ensure_package(rel_path: str) -> None:
    """Create directory and __init__.py marker for a Python package."""
    target = PROJECT_ROOT / rel_path
    target.mkdir(parents=True, exist_ok=True)
    init_file = target / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""P_300 package."""\n', encoding="utf-8")
        log.info("CREATED  %s", init_file.relative_to(PROJECT_ROOT))
    else:
        log.info("EXISTS   %s", init_file.relative_to(PROJECT_ROOT))


def ensure_plain_dir(rel_path: str) -> None:
    """Create directory and .gitkeep marker for non-package dirs."""
    target = PROJECT_ROOT / rel_path
    target.mkdir(parents=True, exist_ok=True)
    keep_file = target / ".gitkeep"
    if not keep_file.exists():
        keep_file.write_text("", encoding="utf-8")
        log.info("CREATED  %s", keep_file.relative_to(PROJECT_ROOT))
    else:
        log.info("EXISTS   %s", keep_file.relative_to(PROJECT_ROOT))


def main() -> None:
    log.info("Stage 3a folder setup")
    log.info("Project root: %s", PROJECT_ROOT)
    for pkg in PYTHON_PACKAGES:
        ensure_package(pkg)
    for plain in PLAIN_DIRS:
        ensure_plain_dir(plain)
    log.info("Stage 3a complete.")


if __name__ == "__main__":
    main()
