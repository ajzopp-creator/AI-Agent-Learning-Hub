"""Infrastructure: Outlook OAuth2 token lifecycle via msal + msal-extensions.

Owns everything needed to get a valid access token for the outlook
account's IMAP XOAUTH2 login: the persisted MSAL token cache, silent
refresh, and the one-time interactive browser consent flow.

Storage (Entry 014, 2026-08-23 — supersedes an earlier keyring-based
design from Entry 013). Windows Credential Manager caps a stored
credential at ~1280 characters — hit live (WinError 1783, "The stub
received bad data") the first time Tony ran the login, because a full
MSAL token cache is several times larger than that. Fix: msal-extensions'
FilePersistenceWithDataProtection, which encrypts the cache file with
Windows DPAPI tied to Tony's Windows login — same security property as
Credential Manager, no size limit. This is Microsoft's own recommended
persistence pattern for MSAL Python desktop apps.

interactive_login() is meant to be run standalone by Tony himself (e.g.
`python cli.py --outlook-oauth-login`), never called from within the
move/check_auth code path — same principle as keyring credentials, Claude
never signs in on Tony's behalf.
"""

import logging

import msal
from msal_extensions import FilePersistenceWithDataProtection, PersistedTokenCache

import config

logger = logging.getLogger("p805")


class OAuthError(Exception):
    """Raised when a token cannot be obtained. Never raised outward
    silently — always tells the caller what to do next."""


def _build_cache() -> PersistedTokenCache:
    """Build the DPAPI-encrypted, file-backed token cache.

    Creates the parent directory if missing. Reads and writes happen
    automatically inside msal_extensions/msal on every token operation —
    there is no separate manual save step.
    """
    config.OAUTH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    persistence = FilePersistenceWithDataProtection(str(config.OAUTH_CACHE_PATH))
    return PersistedTokenCache(persistence)


def _build_app(cache: PersistedTokenCache) -> msal.PublicClientApplication:
    """Construct the MSAL public client app, bound to the given cache."""
    return msal.PublicClientApplication(
        client_id=config.OUTLOOK_OAUTH_CLIENT_ID,
        authority=config.OUTLOOK_OAUTH_AUTHORITY,
        token_cache=cache,
    )


def get_access_token() -> str:
    """Return a valid access token, refreshing silently if needed.

    Raises OAuthError if no cached account exists — meaning Tony needs to
    run interactive_login() once first. Never opens a browser itself.
    """
    cache = _build_cache()
    app = _build_app(cache)
    accounts = app.get_accounts()
    if not accounts:
        raise OAuthError(
            "No cached Outlook OAuth token. Run "
            "'python cli.py --outlook-oauth-login' once to sign in via browser."
        )

    result = app.acquire_token_silent(config.OUTLOOK_OAUTH_SCOPES, account=accounts[0])
    if not result or "access_token" not in result:
        error = (result or {}).get("error_description", "silent token refresh failed")
        raise OAuthError(
            f"Outlook OAuth token refresh failed: {error}. "
            "Run 'python cli.py --outlook-oauth-login' again to re-authenticate."
        )
    return result["access_token"]


def interactive_login() -> None:
    """One-time browser consent flow. Tony runs this himself, standalone.

    Opens the system browser via msal's loopback flow (redirect URI
    http://localhost, registered on the app), persists the resulting
    refresh token to the DPAPI-encrypted cache file, and prints a plain
    success/failure message.
    """
    cache = _build_cache()
    app = _build_app(cache)

    logger.info("Opening browser for Outlook OAuth2 sign-in...")
    result = app.acquire_token_interactive(scopes=config.OUTLOOK_OAUTH_SCOPES)

    if not result or "access_token" not in result:
        error = (result or {}).get("error_description", "interactive login failed")
        logger.error(f"Outlook OAuth2 login failed: {error}")
        return

    logger.info("Outlook OAuth2 login succeeded. Token cached — you're done.")
