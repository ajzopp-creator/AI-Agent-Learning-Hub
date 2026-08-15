r"""conftest.py -- pytest configuration for P_800.

Puts this project's python\ directory on sys.path so tests import
domain.x / infrastructure.y / application.z regardless of the working
directory pytest is launched from.

Exists so test files never need their own sys.path.insert() calls or
hardcoded absolute paths -- both forbidden by WO_COMPLETION_GATE
(WO-P000-E13.001 Phase 2, same shape as P_400's conftest.py).

collect_ignore excludes tests\test_signal_v2_e2e.py -- a Finding-5-style
harness (same shape as P_400's tests\test_p400_known_bugs.py before Phase 4
repair): its "test_*" functions are plain helper functions with positional
args, called manually from the file's own main(), meant to be run directly
via `python test_signal_v2_e2e.py` per its own header, not collected by
pytest. Config-only exclusion per the E13.001 unblock handoff (2026-08-07)
-- the file itself is untouched.

Does NOT exclude tests\test_p115_write.py -- real production/test drift
(P115Record now requires signal_date/written_by, sample data predates
that), left collected so it keeps failing visibly until a real fix lands.

This module docstring is a raw string because the Windows paths above
contain backslash sequences a normal docstring would read as escapes.
"""

import sys
from pathlib import Path

PROJECT_PYTHON_DIR = Path(__file__).parent.resolve()

if str(PROJECT_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON_DIR))

collect_ignore = ["tests/test_signal_v2_e2e.py"]
