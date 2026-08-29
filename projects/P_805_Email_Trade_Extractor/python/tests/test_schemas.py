"""Regression tests for schemas.ApprovedSender.date_added flexible parsing.

Entry 016: sender_sheet.csv was opened in Excel on 2026-07-22, which
silently reformatted every date_added value from ISO to US format. The
strict `date` type field rejected every row identically for a month with
no loud failure — Phase 3 logged it but exited 0 either way (see
test_phase_exit_codes.py for that half of the fix). This file locks in
that both formats now parse correctly, and that garbage still fails
loudly.
"""

import sys
import unittest
from datetime import date

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

from pydantic import ValidationError
from schemas import ApprovedSender


def _make(date_added):
    return ApprovedSender(
        email_address="test@example.com",
        sender_name="Test Sender",
        date_added=date_added,
        sector=None,
        enabled=True,
    )


class TestApprovedSenderDateParsing(unittest.TestCase):
    """Entry 016 fix: date_added must accept both ISO and US formats."""

    def test_accepts_iso_format(self):
        sender = _make("2026-04-26")
        self.assertEqual(sender.date_added, date(2026, 4, 26))

    def test_accepts_us_format(self):
        """The exact format Excel silently converted every row to."""
        sender = _make("4/26/2026")
        self.assertEqual(sender.date_added, date(2026, 4, 26))

    def test_accepts_us_format_single_digit_day_and_month(self):
        sender = _make("4/1/2026")
        self.assertEqual(sender.date_added, date(2026, 4, 1))

    def test_accepts_real_date_object(self):
        """Non-str input (already a date) must pass through untouched."""
        sender = _make(date(2026, 4, 26))
        self.assertEqual(sender.date_added, date(2026, 4, 26))

    def test_rejects_garbage_with_clear_error(self):
        with self.assertRaises(ValidationError) as ctx:
            _make("not-a-date")
        self.assertIn("neither ISO", str(ctx.exception))

    def test_rejects_ambiguous_garbage_that_isnt_a_date_at_all(self):
        with self.assertRaises(ValidationError):
            _make("13/45/2026")  # invalid month/day in either format


if __name__ == "__main__":
    unittest.main()
