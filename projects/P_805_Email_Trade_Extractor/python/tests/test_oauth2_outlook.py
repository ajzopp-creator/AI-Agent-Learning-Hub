"""Regression tests for infrastructure.oauth2_outlook.

Entry 013: original OAuth2 token lifecycle. Entry 014: storage moved from
keyring (hit a real live failure — Windows Credential Manager's ~1280
character cap, WinError 1783) to msal-extensions' DPAPI-encrypted file
cache. All tests mock _build_cache/_build_app — no real network call, no
browser, no real file written to disk, ever runs in CI/local test.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

from infrastructure import oauth2_outlook


class TestBuildCache(unittest.TestCase):
    """Entry 014 fix: cache must be backed by DPAPI file persistence, not
    keyring — and must create its parent directory if missing."""

    @patch("infrastructure.oauth2_outlook.PersistedTokenCache")
    @patch("infrastructure.oauth2_outlook.FilePersistenceWithDataProtection")
    def test_uses_configured_cache_path(self, mock_persistence_cls, mock_cache_cls):
        oauth2_outlook._build_cache()
        mock_persistence_cls.assert_called_once_with(str(oauth2_outlook.config.OAUTH_CACHE_PATH))

    @patch("infrastructure.oauth2_outlook.PersistedTokenCache")
    @patch("infrastructure.oauth2_outlook.FilePersistenceWithDataProtection")
    @patch("pathlib.Path.mkdir")
    def test_creates_parent_directory(self, mock_mkdir, mock_persistence_cls, mock_cache_cls):
        # Path objects use __slots__ — patch.object() on an instance's
        # mkdir fails with "attribute is read-only". Patch the class
        # method (pathlib.Path.mkdir) instead; affects every Path
        # instance for the duration of the test, then restores.
        oauth2_outlook._build_cache()
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestGetAccessToken(unittest.TestCase):
    """No cached account must fail loud and instructive, not silently
    return an empty/invalid token."""

    @patch("infrastructure.oauth2_outlook._build_app")
    @patch("infrastructure.oauth2_outlook._build_cache")
    def test_raises_when_no_cached_accounts(self, mock_build_cache, mock_build_app):
        mock_app = MagicMock()
        mock_app.get_accounts.return_value = []
        mock_build_app.return_value = mock_app

        with self.assertRaises(oauth2_outlook.OAuthError) as ctx:
            oauth2_outlook.get_access_token()
        self.assertIn("--outlook-oauth-login", str(ctx.exception))

    @patch("infrastructure.oauth2_outlook._build_app")
    @patch("infrastructure.oauth2_outlook._build_cache")
    def test_raises_when_silent_refresh_fails(self, mock_build_cache, mock_build_app):
        mock_app = MagicMock()
        mock_app.get_accounts.return_value = [{"username": "ajzopp@outlook.com"}]
        mock_app.acquire_token_silent.return_value = {"error_description": "token expired"}
        mock_build_app.return_value = mock_app

        with self.assertRaises(oauth2_outlook.OAuthError) as ctx:
            oauth2_outlook.get_access_token()
        self.assertIn("token expired", str(ctx.exception))

    @patch("infrastructure.oauth2_outlook._build_app")
    @patch("infrastructure.oauth2_outlook._build_cache")
    def test_returns_token_on_success(self, mock_build_cache, mock_build_app):
        mock_app = MagicMock()
        mock_app.get_accounts.return_value = [{"username": "ajzopp@outlook.com"}]
        mock_app.acquire_token_silent.return_value = {"access_token": "real-token-value"}
        mock_build_app.return_value = mock_app

        token = oauth2_outlook.get_access_token()
        self.assertEqual(token, "real-token-value")


class TestInteractiveLogin(unittest.TestCase):
    """Login flow must never raise outward on failure — logs and returns."""

    @patch("infrastructure.oauth2_outlook._build_app")
    @patch("infrastructure.oauth2_outlook._build_cache")
    def test_logs_error_on_failed_login_without_raising(self, mock_build_cache, mock_build_app):
        mock_app = MagicMock()
        mock_app.acquire_token_interactive.return_value = {"error_description": "user cancelled"}
        mock_build_app.return_value = mock_app

        try:
            oauth2_outlook.interactive_login()
        except Exception as e:
            self.fail(f"interactive_login() must never raise outward, got: {e}")


if __name__ == "__main__":
    unittest.main()
