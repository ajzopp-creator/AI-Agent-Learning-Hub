"""test_run_chaikin_batch.py -- Prompt rendering + schema gating
(WO-P800-E4.001).

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\shared_resources\\
           chaikin_enrichment\\test_run_chaikin_batch.py
"""
import pytest

from shared_resources.chaikin_enrichment.application.run_chaikin_batch import (
    build_prompt,
    run,
)
from shared_resources.chaikin_enrichment.domain.candidate_filter import NoteCandidate


def test_build_prompt_substitutes_note_table():
    candidates = [
        NoteCandidate("DNN", r"C:\vault\TradeManagement\P300\2026-07-23_DNN.md"),
        NoteCandidate("PH", r"C:\vault\TradeManagement\P115\2026-07-24_PH.md"),
    ]

    prompt = build_prompt(candidates)

    assert "{NOTE_TABLE}" not in prompt
    assert r"DNN -> C:\vault\TradeManagement\P300\2026-07-23_DNN.md" in prompt
    assert r"PH -> C:\vault\TradeManagement\P115\2026-07-24_PH.md" in prompt
    assert "## Chaikin Power Gauge" in prompt


def test_disabled_schema_raises():
    with pytest.raises(ValueError):
        run("P400")


def test_p300_run_against_real_vault_returns_int():
    """Real end-to-end scan+filter against the live P_300 vault folder --
    no mocking. Confirms the pipeline runs clean and returns an int; exact
    candidates change day to day so this doesn't assert a count."""
    count = run("P300")
    assert isinstance(count, int)
    assert count >= 0
