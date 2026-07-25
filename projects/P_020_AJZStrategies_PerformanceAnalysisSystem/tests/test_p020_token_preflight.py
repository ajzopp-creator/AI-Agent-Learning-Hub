"""Regression test -- WO-P020-E1.007.

Locks in the token pre-flight exit-code contract used by the weekly
update .bat files: P_020_Schwab_Token_Manager._main() must exit 1 on a
failed connection check and exit 0 on success. If this drifts, the .bat
Step 0 pre-flight check silently stops catching expired tokens.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

API_DIR = Path(__file__).resolve().parents[1] / "python" / "api"
sys.path.insert(0, str(API_DIR))

import P_020_Schwab_Token_Manager as token_manager  # noqa: E402


def test_main_exits_nonzero_on_failed_connection():
    """test_connection() returning (None, None) -- fail -- must sys.exit(1)."""
    with patch.object(token_manager, "test_connection", return_value=(None, None)):
        with pytest.raises(SystemExit) as exc_info:
            token_manager._main()
    assert exc_info.value.code == 1


def test_main_exits_zero_on_successful_connection():
    """test_connection() returning real accounts -- pass -- must sys.exit(0)."""
    fake_client = object()
    fake_accounts = [{"accountNumber": "123456348"}]
    with patch.object(
        token_manager, "test_connection", return_value=(fake_client, fake_accounts)
    ):
        with pytest.raises(SystemExit) as exc_info:
            token_manager._main()
    assert exc_info.value.code == 0