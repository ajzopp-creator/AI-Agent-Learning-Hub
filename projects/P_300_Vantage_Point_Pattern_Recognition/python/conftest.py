r"""conftest.py -- pytest configuration for P_300.

Puts this project's python\ directory on sys.path so tests import
domain.x / infrastructure.y / application.z regardless of the working
directory pytest is launched from.

Exists so test files never need their own sys.path.insert() calls or
hardcoded absolute paths -- both forbidden by WO_COMPLETION_GATE
(WO-P000-E13.001 Phase 2, same shape as P_400's conftest.py).

collect_ignore excludes two dead files under archive\ -- legacy code from
before a refactor, each failing on a stale absolute import
(ModuleNotFoundError: 'python' / 'reporting') that has no live production
counterpart to fix against. Config-only exclusion per the E13.001 unblock
handoff (2026-08-07); the files themselves are untouched. NOT in the
handoff's explicit exclusion list (which named only the now-deleted backup
file) -- added here because leaving them in would still block collection
after the backup file's removal, and they are the same "dead code sitting
under archive\, not a real test" category the handoff authorizes excluding.
Flagged in the WO update, not silently decided.

Does NOT exclude tests\test_eval_incremental.py -- real production/test
drift (assemble_incremental_post_batch missing from domain.eval_incremental),
left collected so it keeps failing visibly until a real fix lands.

This module docstring is a raw string because the Windows paths above
contain backslash sequences a normal docstring would read as escapes.
"""

import sys
from pathlib import Path

PROJECT_PYTHON_DIR = Path(__file__).parent.resolve()

if str(PROJECT_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON_DIR))

collect_ignore = [
    "archive/legacy_layers/labeling/labeling_test.py",
    "archive/legacy_tests/test_zscore_regression.py",
]
