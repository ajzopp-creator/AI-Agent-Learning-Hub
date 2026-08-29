"""Infrastructure: IMAP connection and real server-side message move.

Moves a message from Inbox to config.EXTRACTED_FOLDER_NAME via IMAP
COPY + STORE \\Deleted + EXPUNGE (portable across iCloud/Gmail/Outlook/
Yahoo — does not depend on the optional IMAP MOVE extension). This is a
real mutation of the live mailbox on the server, not local mbox cache
editing (see config.py Phase 5.3 header comment for why that approach
was rejected).

Credentials come from keyring only. Never logged, never written to any
file, never present in config.py.

Respects config.MOVE_DRY_RUN: when True, connects and searches for the
message but does not COPY/STORE/EXPUNGE anything.
"""

import imaplib
import logging
from email.utils import quote

import keyring

import config
from infrastructure import oauth2_outlook

logger = logging.getLogger("p805")


class ImapMoveError(Exception):
    """Raised when a connection, search, or move step fails."""


def _xoauth2_string(username: str, access_token: str) -> str:
    """Build the raw XOAUTH2 SASL string per the Microsoft IMAP spec."""
    return f"user={username}\x01auth=Bearer {access_token}\x01\x01"


def _connect(account: str) -> imaplib.IMAP4_SSL:
    """Open and login an IMAP connection for one account. Raises ImapMoveError.

    OAuth2 accounts (config.OAUTH_ACCOUNTS, currently just 'outlook') use
    AUTHENTICATE XOAUTH2 via oauth2_outlook.get_access_token() instead of
    LOGIN — Entry 013 reverses Entry 011 (Basic Auth rejected server-side).
    All other accounts are unchanged: keyring app-password LOGIN.
    """
    server = config.IMAP_SERVERS.get(account)
    username = config.IMAP_USERNAMES.get(account)
    if not server or not username:
        raise ImapMoveError(f"No IMAP server/username configured for '{account}'")

    host, port = server
    try:
        conn = imaplib.IMAP4_SSL(host, port, timeout=config.IMAP_CONNECT_TIMEOUT)
        if account in config.OAUTH_ACCOUNTS:
            access_token = oauth2_outlook.get_access_token()
            auth_string = _xoauth2_string(username, access_token)
            conn.authenticate("XOAUTH2", lambda _: auth_string.encode())
        else:
            password = keyring.get_password(config.KEYRING_SERVICE_NAME, account)
            if not password:
                raise ImapMoveError(
                    f"No keyring credential for account '{account}' "
                    f"(service={config.KEYRING_SERVICE_NAME!r}). Run keyring.set_password() first."
                )
            conn.login(username, password)
    except ImapMoveError:
        raise
    except oauth2_outlook.OAuthError as e:
        raise ImapMoveError(f"[{account}] OAuth2 error: {e}") from e
    except Exception as e:
        raise ImapMoveError(f"[{account}] connect/login failed: {e}") from e
    return conn


def _ensure_destination_folder(conn: imaplib.IMAP4_SSL, account: str, dry_run: bool) -> None:
    """Create EXTRACTED_FOLDER_NAME if missing and autocreate is enabled.

    dry_run=True never calls conn.create() — a dry run must not mutate the
    server. It only logs what it would do (Entry 010: dry-run mode was
    still creating the destination folder on iCloud before this fix).
    """
    folder = config.EXTRACTED_FOLDER_NAME
    status, mailboxes = conn.list()
    if status != "OK":
        raise ImapMoveError(f"[{account}] could not list mailboxes")
    exists = any(folder.encode() in box for box in mailboxes if box)
    if exists:
        return
    if not config.EXTRACTED_FOLDER_AUTOCREATE:
        raise ImapMoveError(
            f"[{account}] folder '{folder}' missing and EXTRACTED_FOLDER_AUTOCREATE=False"
        )
    if dry_run:
        logger.info(f"[{account}] DRY RUN — would create folder '{folder}'")
        return
    status, _ = conn.create(folder)
    if status != "OK":
        raise ImapMoveError(f"[{account}] could not create folder '{folder}'")
    logger.info(f"[{account}] created folder '{folder}'")


def _find_uid(conn: imaplib.IMAP4_SSL, message_id: str, account: str) -> str | None:
    """Search Inbox for a message by Message-ID header; return UID or None."""
    criterion = f'(HEADER Message-ID "{quote(message_id)}")'
    status, data = conn.uid("search", None, criterion)
    if status != "OK" or not data or not data[0]:
        return None
    uids = data[0].split()
    if not uids:
        return None
    if len(uids) > 1:
        logger.warning(
            f"[{account}] {len(uids)} messages matched Message-ID {message_id!r}; using first"
        )
    return uids[0].decode()


def check_auth(account: str) -> tuple[bool, str]:
    """Connect and log in only — no search, no folder touch, no mail touch.

    For use by application/imap_auth_check.py so credentials can be
    verified any time (e.g. after generating a new app password) without
    going near the move/search logic at all.

    Returns:
        (True, "OK") on success, (False, error message) on failure. Never
        raises outward.
    """
    try:
        conn = _connect(account)
    except ImapMoveError as e:
        return False, str(e)
    try:
        conn.logout()
    except Exception:
        pass
    return True, "OK"


def move_message(account: str, message_id: str) -> str:
    """Move one message from Inbox to EXTRACTED_FOLDER_NAME on the server.

    Returns one of: 'moved', 'dry_run', 'not_found', 'failed'. Never raises
    outward — all exceptions are caught and mapped to 'failed'.
    """
    try:
        conn = _connect(account)
    except ImapMoveError as e:
        logger.error(str(e))
        return "failed"

    try:
        conn.select("INBOX")
        _ensure_destination_folder(conn, account, dry_run=config.MOVE_DRY_RUN)
        uid = _find_uid(conn, message_id, account)
        if uid is None:
            logger.warning(f"[{account}] Message-ID {message_id!r} not found in INBOX")
            return "not_found"

        if config.MOVE_DRY_RUN:
            logger.info(f"[{account}] DRY RUN — would move UID {uid} ({message_id!r})")
            return "dry_run"

        status, _ = conn.uid("copy", uid, config.EXTRACTED_FOLDER_NAME)
        if status != "OK":
            raise ImapMoveError(f"[{account}] COPY failed for UID {uid}")
        status, _ = conn.uid("store", uid, "+FLAGS", "(\\Deleted)")
        if status != "OK":
            raise ImapMoveError(f"[{account}] STORE \\Deleted failed for UID {uid}")
        conn.expunge()
        logger.info(f"[{account}] moved UID {uid} ({message_id!r}) → {config.EXTRACTED_FOLDER_NAME}")
        return "moved"
    except ImapMoveError as e:
        logger.error(str(e))
        return "failed"
    except Exception as e:
        logger.error(f"[{account}] unexpected error moving {message_id!r}: {e}")
        return "failed"
    finally:
        try:
            conn.logout()
        except Exception:
            pass
