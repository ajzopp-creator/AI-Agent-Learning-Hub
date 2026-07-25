"""Regression tests for domain/message_selector.py.

Per Hub-wide python-project-architecture Regression Test Governance: any
domain/infrastructure/application file with a real post-build behavior
fix/change gets a permanent test here, one assertion per fix.

Fix (2026-07-14, Entry 011): 'outlook' account excluded from Phase 5.3 move
entirely (Microsoft rejects Basic Auth / plain IMAP LOGIN for this OAuth2-only
account). select_candidates() gained a skip_accounts param; any signal whose
account is in skip_accounts must never produce a MoveCandidate, even if it
has a valid message_id and isn't in the moved log.
"""

import sys
import unittest
from datetime import datetime, timezone

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

from domain.message_selector import select_candidates
from schemas import TickerSignal


class TestSelectCandidatesSkipAccounts(unittest.TestCase):
    def test_skip_accounts_excluded_even_with_valid_message_id(self):
        """Entry 011 fix: an account in skip_accounts must never be a candidate."""
        now = datetime.now(timezone.utc)
        signals = [
            TickerSignal(ticker="MSFT", pattern="cashtag", source_address="a@b.com",
                         timestamp=now, subject="s", raw_context="ctx", account="outlook",
                         message_id="<msg-outlook@office365.com>"),
            TickerSignal(ticker="AAPL", pattern="cashtag", source_address="c@d.com",
                         timestamp=now, subject="s", raw_context="ctx", account="gmail",
                         message_id="<msg-gmail@gmail.com>"),
        ]
        candidates = select_candidates(signals, moved_log=[], skip_accounts=frozenset({"outlook"}))
        accounts = {c.account for c in candidates}

        self.assertNotIn(
            "outlook", accounts,
            "outlook is in skip_accounts (Microsoft OAuth2-only, Entry 011) — "
            "it must never appear as a move candidate regardless of message_id validity.",
        )
        self.assertIn("gmail", accounts, "gmail is not skipped and should still be a candidate.")


if __name__ == "__main__":
    unittest.main()
