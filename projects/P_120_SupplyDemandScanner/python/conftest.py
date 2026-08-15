r"""conftest.py -- pytest configuration for P_120.

Puts this project's python\ directory on sys.path so tests import
domain.x / infrastructure.y / application.z regardless of the working
directory pytest is launched from.

Exists so test files never need their own sys.path.insert() calls or
hardcoded absolute paths -- both forbidden by WO_COMPLETION_GATE
(WO-P000-E13.001 Phase 2, same shape as P_400's conftest.py).

This module docstring is a raw string because the Windows paths above
contain backslash sequences a normal docstring would read as escapes.
"""

import sys
from pathlib import Path

PROJECT_PYTHON_DIR = Path(__file__).parent.resolve()

if str(PROJECT_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON_DIR))
