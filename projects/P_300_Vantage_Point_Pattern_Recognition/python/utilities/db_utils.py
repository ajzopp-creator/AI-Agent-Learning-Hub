"""
FILE: db_utils.py
VERSION: 1.16
DATE: 2026-05-14
AUTHOR: Anthony Zoppi + Claude
LAYER: utility
DESCRIPTION: Centralized utility for dynamic catalog DB path discovery.
    Strict numeric-prefix filter prevents lexicographical collisions with
    backup or renamed files.
CHANGELOG:
    - 2026-05-06 v1.14: Numeric-prefix filter added.
    - 2026-05-14 v1.15: Glob pattern updated `*geminicatalog.db` -> `*catalog.db`
      to match the v2.0 schema rebuild naming convention (Stage 3.3).
      Header brought to §8.4.1 standard.
    - 2026-05-14 v1.16: MODELS_DIR and CATALOG_GLOB_PATTERN imported from
      config.py per architecture §2.4 single-source-of-truth rule. Removed
      hardcoded path. Added sys.path bootstrap for standalone invocation.
"""
import sys
from pathlib import Path

# Bootstrap sys.path so we can import from python/config.py when this
# script is invoked standalone (e.g., `python python/utilities/db_utils.py`).
# Stage 4 entry points via cli.py won't need this — they'll set PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import MODELS_DIR, CATALOG_GLOB_PATTERN  # noqa: E402

def get_latest_catalog():
    """
    Scans MODELS_DIR for files matching CATALOG_GLOB_PATTERN.
    Filters out files not starting with a digit to prevent lexicographical 
    collisions with backup/renamed files (e.g., 'org_...').
    """
    # Strict filter: only include files starting with a digit
    catalog_files = [f for f in MODELS_DIR.glob(CATALOG_GLOB_PATTERN) if f.name[0].isdigit()]
    
    if not catalog_files:
        raise FileNotFoundError(f"No valid catalog databases found (must start with digit) in {MODELS_DIR}")
        
    # Sort files by name in descending order (newest date first)
    catalog_files.sort(key=lambda x: x.name, reverse=True)
    
    return str(catalog_files[0])

if __name__ == "__main__":
    try:
        latest = get_latest_catalog()
        print(f"Latest catalog found: {latest}")
    except Exception as e:
        print(f"Error: {e}")