"""Regression tests: all four P_805 pipeline phases must exit non-zero on
their true failure precondition (Entry 016).

Before this fix, phase3/35/4/53's run() functions logged an ERROR and
did a bare `return` on their failure case — the Python process still
exited 0, so P_805_daily_pipeline.bat's `if %errorlevel% equ 0` abort
check never fired. Every phase logged [SUCCESS] and the chain continued
doing nothing, silently, for a month (2026-07-22 to 2026-08-23) before
anyone noticed. Task Scheduler reported success the entire time because
it genuinely was true from the OS's point of view — this is what makes
that failure mode dangerous: the bug is in what "success" means, not in
whether the process crashed.

These tests only check the exit behavior, not full phase logic (already
covered by test_ranker.py, test_message_selector.py, etc.). Legitimate
non-error early-returns (Phase 3.5's "no unknowns to enrich", Phase
5.3's "nothing to move") are explicitly NOT covered here — those must
stay a normal exit 0, and are asserted as such to guard against a
future overcorrection.
"""

import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

import application.phase3_extract as phase3
import application.phase35_enrich as phase35
import application.phase4_rank as phase4
import application.phase53_move as phase53


class TestPhase3ExitCode(unittest.TestCase):
    @patch("application.phase3_extract.load_enabled_senders", return_value=set())
    @patch("application.phase3_extract.configure_logging")
    def test_exits_nonzero_when_no_enabled_senders(self, mock_configure, mock_load):
        with self.assertRaises(SystemExit) as ctx:
            phase3.run()
        self.assertNotEqual(ctx.exception.code, 0)


class TestPhase35ExitCode(unittest.TestCase):
    @patch("application.phase35_enrich.load_signals_csv", return_value=[])
    @patch("application.phase35_enrich.configure_logging")
    def test_exits_nonzero_when_no_signals_loaded(self, mock_configure, mock_load):
        with self.assertRaises(SystemExit) as ctx:
            phase35.run()
        self.assertNotEqual(ctx.exception.code, 0)


class TestPhase4ExitCode(unittest.TestCase):
    @patch("application.phase4_rank.load_signals_csv", return_value=[])
    @patch("application.phase4_rank.configure_logging")
    def test_exits_nonzero_when_no_signals_loaded(self, mock_configure, mock_load):
        with self.assertRaises(SystemExit) as ctx:
            phase4.run()
        self.assertNotEqual(ctx.exception.code, 0)


class TestPhase53ExitCode(unittest.TestCase):
    @patch("application.phase53_move.load_signals_csv", return_value=[])
    @patch("application.phase53_move.configure_logging")
    def test_exits_nonzero_when_no_signals_loaded(self, mock_configure, mock_load):
        with self.assertRaises(SystemExit) as ctx:
            phase53.run()
        self.assertNotEqual(ctx.exception.code, 0)

    @patch("application.phase53_move.select_candidates", return_value=[])
    @patch("application.phase53_move.load_moved_log", return_value=[])
    @patch(
        "application.phase53_move.load_signals_csv",
        return_value=[object()],  # non-empty, just needs len() > 0
    )
    @patch("application.phase53_move.configure_logging")
    def test_does_not_exit_when_nothing_to_move(
        self, mock_configure, mock_load, mock_moved_log, mock_candidates
    ):
        """Guard against overcorrection: 'nothing to move' (everything
        already moved) is a legitimate normal exit, not a failure."""
        try:
            phase53.run()
        except SystemExit as e:
            self.fail(f"Phase 5.3 must not exit on an empty candidate list, got: {e}")


if __name__ == "__main__":
    unittest.main()
