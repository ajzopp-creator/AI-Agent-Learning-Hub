# test_domain.py -- lessons_audit (WO-P000-E20.001)
# Permanent per Regression Test Governance (python-project-architecture
# SKILL.md) -- never deleted, only grows, one assertion per real fix.
#
# Fix under test: lessons_audit's first live run against P_000's real
# tasks\lessons.md flagged all 3 lessons LIKELY_ENFORCED_ELSEWHERE.
# Root cause: classify_lesson scored a lesson against each reference
# source's ENTIRE text pooled into one keyword set -- any technical
# lesson shares 3+ generic terms with a multi-thousand-word document
# somewhere across its whole length. Fix: chunk_reference_text splits a
# source into individual table rows / checklist items / paragraphs;
# classify_lesson now requires a SINGLE chunk to clear the threshold on
# its own, never an aggregate across a whole file.

from shared_resources.python_utils.lessons_audit import config
from shared_resources.python_utils.lessons_audit.domain import (
    chunk_reference_text,
    classify_lesson,
    compute_document_frequency,
    extract_keywords,
    filter_significant_keywords,
)

_LESSON_TEXT = (
    "The wrapper architecture uses native endpoints, never switching "
    "mid-development."
)
_LESSON_KEYWORDS = extract_keywords(_LESSON_TEXT, config.STOPWORDS, config.MIN_TOKEN_LEN)


def _chunk_records(reference_text: str) -> list[tuple[str, str, str, set[str]]]:
    records = []
    for chunk in chunk_reference_text(reference_text):
        chunk_keywords = extract_keywords(chunk, config.STOPWORDS, config.MIN_TOKEN_LEN)
        if chunk_keywords:
            records.append(("test", "test_doc.md", chunk, chunk_keywords))
    return records


def test_scattered_terms_across_many_chunks_do_not_flag_as_enforced():
    """Each of the lesson's real keywords appears in a SEPARATE paragraph
    (chunk), one keyword per chunk -- the old pooled-whole-document
    scoring would have summed all of them together and false-flagged
    this. Per-chunk scoring must not."""
    keywords_to_scatter = ["wrapper", "architecture", "native", "endpoints", "switching"]
    reference_doc = "\n\n".join(
        f"Paragraph about {kw} and other filler padding words unrelated content extra."
        for kw in keywords_to_scatter
    )

    flag = classify_lesson(
        "M-TEST-SCATTERED", "scattered test", _LESSON_KEYWORDS,
        _chunk_records(reference_doc), min_shared_terms=3,
    )

    assert flag.classification != "LIKELY_ENFORCED_ELSEWHERE", (
        f"expected UNCERTAIN or LIKELY_STILL_LIVE, got {flag.classification} "
        f"(max_shared={flag.shared_term_count}) -- scattered terms across "
        f"separate chunks must never sum together"
    )


def test_concentrated_terms_in_single_chunk_flags_as_enforced():
    """All of the lesson's real keywords appear together in ONE chunk
    (a single checklist line) -- this SHOULD flag. Confirms the v1.1 fix
    didn't also kill real detection, only the false-positive pooling."""
    reference_doc = (
        "[x] wrapper architecture native endpoints switching enforced automatically\n\n"
        "Unrelated paragraph about a completely different topic with different words."
    )

    flag = classify_lesson(
        "M-TEST-CONCENTRATED", "concentrated test", _LESSON_KEYWORDS,
        _chunk_records(reference_doc), min_shared_terms=3,
    )

    assert flag.classification == "LIKELY_ENFORCED_ELSEWHERE", (
        f"expected LIKELY_ENFORCED_ELSEWHERE, got {flag.classification} "
        f"(max_shared={flag.shared_term_count}) -- concentrated real overlap "
        f"in one chunk must still be detected"
    )


def test_consecutive_non_blank_lines_do_not_merge_into_one_chunk():
    """A block of consecutive non-blank lines with NO blank-line
    separator (e.g. a version-history footer) must chunk as separate
    lines, never glue together into one oversized chunk -- this was the
    v1.1 M-002/M-003 false positive (the whole changelog footer matched
    as a single chunk)."""
    reference_doc = (
        "*Version 1.0 -- wrapper architecture native endpoints notes.*\n"
        "*Version 1.1 -- switching development testing notes.*\n"
        "*Version 1.2 -- completely unrelated different vocabulary content.*"
    )

    chunks = chunk_reference_text(reference_doc)

    assert len(chunks) == 3, (
        f"expected 3 separate line chunks, got {len(chunks)}: {chunks}"
    )


def test_fenced_code_block_content_excluded_from_scoring():
    """Content inside triple-backtick fenced code blocks must never
    become a scorable chunk -- a directory-tree diagram or code snippet
    naming the same subsystem as a lesson is not an enforcement signal.
    This was the v1.1 M-001 false positive (a folder-tree diagram
    matched)."""
    reference_doc = (
        "Some prose before the code block mentions unrelated topics.\n"
        "```\n"
        "AI-Agent-Learning-Hub/\n"
        "|-- integrations/\n"
        "|   `-- lm_studio/    # wrapper architecture native endpoints\n"
        "```\n"
        "Some prose after the code block, also unrelated to the lesson."
    )

    chunks = chunk_reference_text(reference_doc)

    assert not any("lm_studio" in c or "wrapper" in c for c in chunks), (
        f"fenced code content leaked into chunks: {chunks}"
    )

def test_pervasive_corpus_words_do_not_count_toward_a_flag():
    """A word appearing in MANY chunks across the reference corpus (e.g.
    'check' used constantly throughout a governance document) must be
    filtered out before scoring, even though it is not in the English
    stopword list -- a fixed stopword list cannot catch corpus-specific
    noise. This was the v1.2 M-001/M-002/M-003 false positive: shared
    words were generic terms (check/status/rule/just/because), pervasive
    throughout the corpus, not real overlap."""
    chunk_keyword_sets = [
        {"pervasive", "wordone"},
        {"pervasive", "wordtwo"},
        {"pervasive", "wordthree"},
        {"pervasive", "wordfour"},
        {"pervasive", "wordfive"},
        {"pervasive", "distinctive"},
    ]
    doc_frequency = compute_document_frequency(chunk_keyword_sets)

    filtered = filter_significant_keywords(
        {"pervasive", "distinctive"}, doc_frequency, config.MAX_CHUNK_DOC_FREQUENCY
    )

    assert "pervasive" not in filtered, (
        f"word in {doc_frequency['pervasive']} chunks should be filtered "
        f"at max_frequency={config.MAX_CHUNK_DOC_FREQUENCY}, got {filtered}"
    )
    assert "distinctive" in filtered, (
        f"rare word (1 chunk) should survive filtering, got {filtered}"
    )


def test_rare_corpus_word_is_not_filtered():
    """A word appearing in only one chunk across the corpus must survive
    filtering -- confirms the v1.3 filter strips PERVASIVE words only,
    not every word below some arbitrary floor."""
    chunk_keyword_sets = [{"onlyhere"}, {"other", "words"}, {"more", "stuff"}]
    doc_frequency = compute_document_frequency(chunk_keyword_sets)

    filtered = filter_significant_keywords({"onlyhere"}, doc_frequency, max_frequency=1)

    assert "onlyhere" in filtered, (
        f"word in exactly 1 chunk must survive max_frequency=1, got {filtered}"
    )