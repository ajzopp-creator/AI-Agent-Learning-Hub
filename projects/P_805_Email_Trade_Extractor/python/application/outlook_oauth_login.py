"""Application: standalone Outlook OAuth2 interactive login.

Thin orchestration wrapper — configures logging, then delegates to
infrastructure.oauth2_outlook.interactive_login(). Mirrors the pattern
used by imap_auth_check.py so every cli.py entry point sets up logging
the same way before doing anything else.

Usage (via cli.py):
    python cli.py --outlook-oauth-login
"""

import logging

from infrastructure.logging_setup import configure_logging
from infrastructure.oauth2_outlook import interactive_login

logger = logging.getLogger("p805")


def run() -> None:
    """Configure logging, then run the one-time browser consent flow."""
    configure_logging()
    interactive_login()
