"""Regression tests for domain/ranker.py.

Per Hub-wide python-project-architecture Regression Test Governance.

WO-P000-E10.001 item 3.3: build_ranked_signals()'s consensus_threshold and
sector_map both default to values suggesting they might never be supplied
by a real caller (consensus_threshold=2, sector_map=None). Confirmed FALSE
POSITIVE: application/phase4_rank.py:52 passes both positionally --
build_ranked_signals(signals, config.CONSENSUS_THRESHOLD, sector_map), with
sector_map freshly loaded from infrastructure.sender_sheet.load_sender_sectors()
on the line directly above. A keyword-arg-only AST scan can't see a
positional pass, which is why the audit flagged it -- same root cause as
8 other false positives found in this WO across P_020/P_300/P_400.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")

_PYTHON_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python")


class TestBuildRankedSignalsCallerPropagation(unittest.TestCase):
    def test_phase4_rank_passes_both_params(self):
        """phase4_rank.py must pass real consensus_threshold and sector_map
        values, not rely on build_ranked_signals()'s defaults -- confirms
        WO-P000-E10.001 item 3.3 stays a false positive if this file changes."""
        src = (_PYTHON_DIR / "application" / "phase4_rank.py").read_text(encoding="utf-8")
        self.assertIn("sector_map = load_sender_sectors()", src)
        self.assertIn(
            "build_ranked_signals(signals, config.CONSENSUS_THRESHOLD, sector_map)",
            src,
        )


if __name__ == "__main__":
    unittest.main()