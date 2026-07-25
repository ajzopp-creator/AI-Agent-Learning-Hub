"""
FILE: db_utils.py
VERSION: 1.17
DATE: 2026-07-20
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
    - 2026-07-20 v1.17 (WO-P300-E4.002, M-095): added get_latest_catalog_path(),
      a Path-typed sibling of get_latest_catalog(). Callers that need the
      catalog's filesystem PATH itself (shutil.copy2, atomic_move's .exists()
      check, a Path-typed field) should call this instead of manually wrapping
      get_latest_catalog() in Path() at every call site -- that manual-wrap
      convention has now failed 4 times (M-089 + 3 more in M-095, one of
      which crashed a real production promote). get_latest_catalog()'s own
      str contract is UNCHANGED -- sqlite3.connect()-style callers keep using
      it as-is; this is additive, not a breaking change.
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

    Returns the raw filesystem path as a `str` (deliberate -- see
    get_latest_catalog_path() below for the Path-typed sibling). Use this
    form for sqlite3.connect()-style callers, or callers that already
    wrap the result themselves; use get_latest_catalog_path() for anything
    that needs a real Path object.
    """
    # Strict filter: only include files starting with a digit
    catalog_files = [f for f in MODELS_DIR.glob(CATALOG_GLOB_PATTERN) if f.name[0].isdigit()]
    
    if not catalog_files:
        raise FileNotFoundError(f"No valid catalog databases found (must start with digit) in {MODELS_DIR}")
        
    # Sort files by name in descending order (newest date first)
    catalog_files.sort(key=lambda x: x.name, reverse=True)
    
    return str(catalog_files[0])


def get_latest_catalog_path() -> Path:
    """Path-typed sibling of get_latest_catalog() (WO-P300-E4.002, M-095).

    Use this when the caller needs the catalog's filesystem path itself
    (file copy, atomic move, a Path-typed dataclass field) -- use
    get_latest_catalog() (str) only for sqlite3.connect()-style
    DB-connection callers, or better, use db_connect.py's
    connection_context()/get_connection() directly and skip path
    resolution entirely.

    Correct-by-construction: callers that used to write
    `Path(get_latest_catalog())` by hand (a convention that has silently
    failed 4 times) call this instead and cannot forget the wrap.

    Raises:
        FileNotFoundError: propagated from get_latest_catalog() if no
            valid catalog file exists.
    """
    return Path(get_latest_catalog())


if __name__ == "__main__":
    try:
        latest = get_latest_catalog()
        print(f"Latest catalog found: {latest}")
        latest_path = get_latest_catalog_path()
        print(f"Latest catalog path (typed): {latest_path} (type={type(latest_path).__name__})")
    except Exception as e:
        print(f"Error: {e}")