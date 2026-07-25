"""Regression tests for infrastructure/imap_mover.py.

Per Hub-wide python-project-architecture Regression Test Governance: any
domain/infrastructure/application file with a real post-build bug fix
gets a permanent test here, one assertion per fix, never deleted.

Fix 1 (2026-07-14, Entry 010): dry-run mode was still calling conn.create()
to make the destination folder on iCloud — a real server mutation during
what was supposed to be a no-op dry run. _ensure_destination_folder() now
takes a dry_run flag and must never call create() when it's True.

Uses a fake IMAP connection object — no real network call, no real
credentials needed to run this test.
"""

import sys
import unittest

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

from infrastructure.imap_mover import _ensure_destination_folder
import config


class FakeConn:
    """Duck-typed stand-in for imaplib.IMAP4_SSL — tracks whether create() ran."""

    def __init__(self, folder_exists: bool):
        self._folder_exists = folder_exists
        self.create_called = False

    def list(self):
        if self._folder_exists:
            return "OK", [b'(\\HasNoChildren) "/" "ExtractedNewsletterFolder"']
        return "OK", [b'(\\HasNoChildren) "/" "INBOX"']

    def create(self, folder):
        self.create_called = True
        return "OK", [b"CREATE completed"]


class TestEnsureDestinationFolder(unittest.TestCase):
    def test_dry_run_never_calls_create_when_folder_missing(self):
        """Entry 010 fix: dry_run=True must not mutate the server, ever."""
        original_autocreate = config.EXTRACTED_FOLDER_AUTOCREATE
        config.EXTRACTED_FOLDER_AUTOCREATE = True
        try:
            conn = FakeConn(folder_exists=False)
            _ensure_destination_folder(conn, account="icloud", dry_run=True)
            self.assertFalse(
                conn.create_called,
                "dry_run=True must never call conn.create() — this is the exact "
                "bug fixed in Entry 010 (folder was created on iCloud during a dry run).",
            )
        finally:
            config.EXTRACTED_FOLDER_AUTOCREATE = original_autocreate

    def test_live_run_calls_create_when_folder_missing(self):
        """Sanity check: the real (non-dry-run) path still works after the fix."""
        original_autocreate = config.EXTRACTED_FOLDER_AUTOCREATE
        config.EXTRACTED_FOLDER_AUTOCREATE = True
        try:
            conn = FakeConn(folder_exists=False)
            _ensure_destination_folder(conn, account="icloud", dry_run=False)
            self.assertTrue(
                conn.create_called,
                "dry_run=False with folder missing should still call conn.create().",
            )
        finally:
            config.EXTRACTED_FOLDER_AUTOCREATE = original_autocreate


if __name__ == "__main__":
    unittest.main()
