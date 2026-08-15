r"""conftest.py -- pytest configuration for P_400.

Puts this project's python\ directory on sys.path so tests import
domain.x / infrastructure.y / application.z regardless of the working
directory pytest is launched from.

Exists so test files never need their own sys.path.insert() calls or
hardcoded absolute paths -- both forbidden by WO_COMPLETION_GATE and both
currently present in tests\test_p400_known_bugs.py (WO-P000-E13.001
Findings 3 and 4).

Prerequisite for WO-P400-E5.003: lets tests\test_ranking.py live in
tests\ rather than adding another top-level stray.

This module docstring is a raw string because the Windows paths above
contain backslash sequences a normal docstring would read as escapes.
"""

import sys
from pathlib import Path

PROJECT_PYTHON_DIR = Path(__file__).parent.resolve()

if str(PROJECT_PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_PYTHON_DIR))