"""schwab_commands.py -- `schwab-auth` CLI command (WO-P400-E4.001).

Split out from commands.py to keep it under the 300-line cap (was already
at 297 lines before this WO -- same pattern as spec_commands.py, WO-P400-E3.009).
"""

from __future__ import annotations

from config import SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH


def cmd_schwab_auth() -> int:
    """Run the Schwab OAuth flow for P_400's own config/token paths."""
    from shared_resources.python_utils.schwab_auth import run_auth

    run_auth(SCHWAB_CONFIG_PATH, SCHWAB_TOKEN_PATH)
    return 0