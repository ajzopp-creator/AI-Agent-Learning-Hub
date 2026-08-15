r"""conftest.py -- pytest configuration for P_020.

Puts this project's python\ directory on sys.path so tests import
domain.x / infrastructure.y / application.z regardless of the working
directory pytest is launched from.

Exists so test files never need their own sys.path.insert() calls or
hardcoded absolute paths -- both forbidden by WO_COMPLETION_GATE
(WO-P000-E13.001 Phase 2, same shape as P_400's conftest.py).

collect_ignore excludes api\test_schwab.py -- a manual Schwab-auth
diagnostic script, not a pytest test. It calls sys.exit(1) at module level
when schwab_credentials.py (live API credentials, not committed) is
missing, which crashes pytest's collection outright (INTERNALERROR) since
pytest imports every test_*.py it finds. Config-only exclusion per the
E13.001 unblock handoff (2026-08-07) -- the file itself is untouched.

This module docstring is a raw string because the Windows paths above
contain backslash sequences a normal docstring would read as escapes.
"""

import sys
from pathlib import Path

PROJECT_PYTHON_DIR = Path(__file__).parent.resolve()

if str(PROJECT_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON_DIR))

collect_ignore = ["api/test_schwab.py"]
