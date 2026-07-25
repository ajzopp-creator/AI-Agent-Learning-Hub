"""Application: standalone IMAP auth check for all 4 accounts.

Verifies keyring-stored credentials against each account's real IMAP
server: connect + login + logout only. No search, no folder touch, no
mail read/move/delete. Safe to run any time — after generating a new app
password, before a real (non-dry-run) move, or whenever something feels
off with an account.

Usage (via cli.py):
    python cli.py --check-imap-auth
    python cli.py --check-imap-auth --account gmail
"""

import logging

import config
from infrastructure.imap_mover import check_auth
from infrastructure.logging_setup import configure_logging

logger = logging.getLogger("p805")


def run(account: str | None = None) -> None:
    """Check IMAP auth for one account or all 4. Called from cli.py."""
    configure_logging()
    targets = [account] if account else list(config.IMAP_ACCOUNT_ORDER)

    logger.info(f"IMAP auth check: {len(targets)} account(s)")
    logger.info("-" * 72)

    results: dict[str, tuple[bool, str]] = {}
    for name in targets:
        ok, detail = check_auth(name)
        results[name] = (ok, detail)
        status = "PASS" if ok else "FAIL"
        logger.info(f"[{name:7s}] {status}  {detail}")

    logger.info("-" * 72)
    passed = sum(1 for ok, _ in results.values() if ok)
    logger.info(f"Auth check: {passed}/{len(targets)} accounts OK")
