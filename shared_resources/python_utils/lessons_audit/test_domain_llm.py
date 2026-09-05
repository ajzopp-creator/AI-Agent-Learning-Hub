# test_domain_llm.py -- lessons_audit (WO-P000-E20.001, v1.4)
# Permanent per Regression Test Governance (python-project-architecture
# SKILL.md) -- coverage for the new LM Studio classification path added
# 2026-09-04 (Decision 3 revision). New logic gets tests at build time,
# same discipline as a post-build fix.

from shared_resources.python_utils.lessons_audit import config
from shared_resources.python_utils.lessons_audit.domain_llm import (
    build_classification_prompt,
    parse_llm_classification_response,
    select_top_candidate_chunks,
)


def _chunk_record(source_type, source_path, excerpt, keywords):
    return (source_type, source_path, excerpt, set(keywords))


def test_select_top_candidate_chunks_ranks_by_overlap_descending():
    """A chunk sharing more keywords with the lesson must rank above one
    sharing fewer -- the model should see the strongest evidence first,
    not corpus order."""
    lesson_keywords = {"wrapper", "architecture", "native", "endpoints"}
    records = [
        _chunk_record("skill_file", "a.md", "weak match line", {"wrapper"}),
        _chunk_record("ec_log", "b.md", "strong match line", {"wrapper", "architecture", "native"}),
        _chunk_record("completion_gate", "c.md", "no match line", {"unrelated"}),
    ]

    top = select_top_candidate_chunks(lesson_keywords, records, top_n=5)

    assert top[0][2] == "strong match line", (
        f"expected the 3-keyword-overlap chunk ranked first, got {top}"
    )


def test_select_top_candidate_chunks_excludes_zero_overlap():
    """A chunk with no shared keywords is not relevant evidence and must
    never appear in the candidate list, even if top_n isn't filled."""
    lesson_keywords = {"wrapper", "architecture"}
    records = [
        _chunk_record("skill_file", "a.md", "match line", {"wrapper"}),
        _chunk_record("ec_log", "b.md", "no match line", {"completely", "unrelated"}),
    ]

    top = select_top_candidate_chunks(lesson_keywords, records, top_n=5)

    assert len(top) == 1, f"expected only the overlapping chunk, got {top}"
    assert top[0][2] == "match line"


def test_select_top_candidate_chunks_respects_top_n_limit():
    """More matching chunks than top_n exist -- only top_n are returned,
    keeping the LM Studio prompt small regardless of corpus size."""
    lesson_keywords = {"wrapper"}
    records = [
        _chunk_record("skill_file", f"doc{i}.md", f"line {i} wrapper", {"wrapper"})
        for i in range(10)
    ]

    top = select_top_candidate_chunks(lesson_keywords, records, top_n=3)

    assert len(top) == 3, f"expected exactly top_n=3 chunks, got {len(top)}"


def test_build_classification_prompt_includes_lesson_and_evidence():
    """The filled prompt must contain the lesson body and every candidate
    excerpt -- if a field silently drops, the model classifies blind."""
    candidates = [("ec_log", "doc.md", "the enforced rule text")]

    prompt = build_classification_prompt(
        "M-001", "Test Lesson", "This is the lesson body.",
        candidates, config.CLASSIFICATION_PROMPT_TEMPLATE,
    )

    assert "M-001" in prompt
    assert "Test Lesson" in prompt
    assert "This is the lesson body." in prompt
    assert "the enforced rule text" in prompt


def test_build_classification_prompt_handles_no_candidates():
    """Zero candidate chunks (nothing keyword-matched at all) must still
    produce a valid prompt, not a crash or an empty evidence section the
    model could misread as 'evidence exists but is blank'."""
    prompt = build_classification_prompt(
        "M-002", "No Evidence Lesson", "Body text.", [], config.CLASSIFICATION_PROMPT_TEMPLATE,
    )

    assert "no keyword-matched candidates found" in prompt


def test_parse_llm_classification_response_extracts_label_ignoring_preceding_text():
    """DeepSeek R1 is a reasoning model -- it emits chain-of-thought
    before the answer. The parser must find CLASSIFICATION: wherever it
    sits, not assume it's the first line."""
    response = (
        "Let me think through this carefully. The lesson discusses "
        "wrapper architecture. Looking at the evidence, this does appear "
        "covered elsewhere.\n\nCLASSIFICATION: LIKELY_ENFORCED_ELSEWHERE"
    )

    result = parse_llm_classification_response(response)

    assert result == "LIKELY_ENFORCED_ELSEWHERE"


def test_parse_llm_classification_response_returns_none_when_no_match():
    """No recognizable CLASSIFICATION: line at all -- caller must be able
    to treat this exactly like any other LM Studio failure and fall back,
    never crash trying to use a missing label."""
    result = parse_llm_classification_response("The model rambled without ever answering.")

    assert result is None


def test_parse_llm_classification_response_case_insensitive():
    """Model output casing isn't guaranteed -- lowercase or mixed-case
    labels must still parse correctly."""
    result = parse_llm_classification_response("classification: likely_still_live")

    assert result == "LIKELY_STILL_LIVE"
