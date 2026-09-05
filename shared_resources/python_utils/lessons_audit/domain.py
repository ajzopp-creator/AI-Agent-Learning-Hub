# domain.py -- lessons_audit (WO-P000-E20.001)
# Pure logic: parsing, chunking, keyword extraction, overlap scoring,
# classification. No file/network I/O -- see infrastructure.py for that.
#
# v1.1 (2026-09-01): fixed a post-build bug -- classify_lesson originally
# scored a lesson against each reference source's ENTIRE text pooled into
# one keyword set, so any technical lesson shared 3+ generic terms with a
# multi-thousand-word document somewhere across its whole length. Fix:
# chunk_reference_text() split a source into blank-line-delimited
# paragraphs, table rows, and checklist items, scored independently.
#
# v1.2 (2026-09-01): the v1.1 fix still false-flagged all 3 real lessons,
# smaller radius but same root cause. Two distinct sub-bugs found on
# re-run: (1) a fenced code block (a folder-tree diagram) has no blank
# lines, so the paragraph accumulator glued the whole diagram into one
# chunk -- any lesson naming the same subsystem as the diagram matched
# it; (2) the doc's version-history footer is consecutive non-blank
# lines with no blank-line separator, so it also glued into one giant
# chunk. Fix: chunking is now line-level (every non-blank, non-fenced
# line is its own chunk -- this subsumes table rows and checklist items
# for free, they were already single lines) and content inside triple-
# backtick fences is excluded entirely, not scored at all. Regression-
# tested: test_domain.py (4 tests total, 2 added that pass).
#
# v1.3 (2026-09-01): line-chunking + code-fence exclusion fixed the
# STRUCTURAL false positives, but the real run still flagged all 3
# lessons -- the matched words were generic corpus vocabulary (check,
# status, rule, just, because) that a fixed English STOPWORDS list
# doesn't catch, since these are ordinary words, just pervasive in THIS
# governance corpus specifically. Fix: compute_document_frequency() +
# filter_significant_keywords() drop any word appearing in more than
# config.MAX_CHUNK_DOC_FREQUENCY chunks across the reference corpus
# before scoring -- corpus-relative noise, not a fixed word list.

from __future__ import annotations

import re

from shared_resources.python_utils.lessons_audit.schemas import (
    LessonFlag,
    MatchedSource,
)

_LESSON_HEADER = re.compile(r"^###\s+(M-\d+):\s*(.+?)\s*$", re.MULTILINE)
_WORD = re.compile(r"[a-zA-Z]+")
_TABLE_SEPARATOR = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")
_CODE_FENCE = re.compile(r"^\s*```")


def parse_lesson_entries(lessons_md_text: str) -> list[dict]:
    """Split lessons.md text into individual M-series entries.

    Args:
        lessons_md_text: Full text of a tasks/lessons.md file.

    Returns:
        List of {"id": "M-001", "title": str, "body": str}, in file order.
        Entries with no recognizable "### M-NNN: Title" header are skipped
        -- this parser is deliberately narrow (M-series only), not a
        general markdown parser.
    """
    matches = list(_LESSON_HEADER.finditer(lessons_md_text))
    entries = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(lessons_md_text)
        entries.append({
            "id": match.group(1),
            "title": match.group(2).strip(),
            "body": lessons_md_text[start:end].strip(),
        })
    return entries


def chunk_reference_text(text: str) -> list[str]:
    """Split a reference-source document into individually scorable chunks.

    Line-level (v1.2): every non-blank, non-fenced, non-table-separator
    line becomes its own chunk. This subsumes table rows and checklist
    items for free (they're already single lines) and fixes two v1.1
    bugs -- consecutive non-blank lines with no blank-line separator no
    longer glue together (was: a changelog footer became one giant
    chunk), and content inside triple-backtick fenced code blocks is
    excluded entirely, never scored (was: a folder-tree diagram matched
    any lesson naming the same subsystem). See module docstring.

    Args:
        text: Raw text of a reference source (e.g. WO_COMPLETION_GATE.md).

    Returns:
        List of non-empty, non-fenced chunk strings, in file order.
    """
    chunks: list[str] = []
    in_code_fence = False

    for line in text.splitlines():
        stripped = line.strip()
        if _CODE_FENCE.match(stripped):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence or not stripped:
            continue
        if _TABLE_SEPARATOR.match(stripped):
            continue
        chunks.append(stripped)

    return chunks


def extract_keywords(text: str, stopwords: frozenset, min_len: int) -> set[str]:
    """Tokenize text into a lowercase keyword set for overlap scoring.

    Args:
        text: Raw text (lesson body or a single reference-source chunk).
        stopwords: Common words to exclude.
        min_len: Minimum token length to keep.

    Returns:
        Set of lowercase alphabetic tokens, filtered.
    """
    tokens = (t.lower() for t in _WORD.findall(text))
    return {t for t in tokens if len(t) >= min_len and t not in stopwords}


def compute_document_frequency(chunk_keyword_sets: list[set[str]]) -> dict[str, int]:
    """Count how many chunks each keyword appears in, across a reference
    corpus (v1.3). Words pervasive across many chunks are generic to
    THIS corpus even when absent from a fixed English stopword list --
    e.g. "check"/"status"/"rule" show up constantly in a governance
    document because it IS a document about checks, statuses, and rules.

    Args:
        chunk_keyword_sets: One keyword set per chunk -- reference-source
            chunks only, never lesson keywords.

    Returns:
        {word: number_of_chunks_containing_it}.
    """
    frequency: dict[str, int] = {}
    for keywords in chunk_keyword_sets:
        for word in keywords:
            frequency[word] = frequency.get(word, 0) + 1
    return frequency


def filter_significant_keywords(
    keywords: set[str], doc_frequency: dict[str, int], max_frequency: int
) -> set[str]:
    """Drop words appearing in more than max_frequency chunks across the
    reference corpus (v1.3) -- corpus-specific noise a fixed stopword
    list can't catch. See module docstring.

    Args:
        keywords: A chunk's raw keyword set.
        doc_frequency: Output of compute_document_frequency, over the
            SAME reference corpus this chunk came from.
        max_frequency: Chunks-containing-word threshold.

    Returns:
        Keywords with doc_frequency <= max_frequency. A word absent
        from doc_frequency (frequency 0) is always kept.
    """
    return {w for w in keywords if doc_frequency.get(w, 0) <= max_frequency}


def score_overlap(lesson_keywords: set[str], chunk_keywords: set[str]) -> tuple[int, list[str]]:
    """Count and list keywords shared between a lesson and one chunk.

    Returns:
        (shared_count, sorted list of shared terms).
    """
    shared = sorted(lesson_keywords & chunk_keywords)
    return len(shared), shared


def classify_lesson(
    lesson_id: str,
    lesson_title: str,
    lesson_keywords: set[str],
    chunk_records: list[tuple[str, str, str, set[str]]],
    min_shared_terms: int,
) -> LessonFlag:
    """Classify one lesson entry against individual reference-source chunks.

    Args:
        lesson_id: e.g. "M-001".
        lesson_title: The entry's title text.
        lesson_keywords: Keywords extracted from the lesson body.
        chunk_records: (source_type, source_path, chunk_excerpt,
            chunk_keywords) -- ONE record per LINE-level chunk (v1.2),
            never a whole file or multi-line block pooled together (see
            chunk_reference_text).
        min_shared_terms: threshold a SINGLE chunk must clear on its own.

    Returns:
        A populated LessonFlag. LIKELY_ENFORCED_ELSEWHERE requires at
        least one individual chunk to independently clear
        min_shared_terms -- overlap is never summed across chunks or
        across a whole source.
    """
    matched: list[MatchedSource] = []
    max_shared = 0
    for source_type, source_path, chunk_excerpt, chunk_keywords in chunk_records:
        count, shared = score_overlap(lesson_keywords, chunk_keywords)
        if count > 0:
            matched.append(MatchedSource(
                source_type=source_type,
                source_path=source_path,
                chunk_excerpt=chunk_excerpt[:200],
                shared_terms=shared,
            ))
            max_shared = max(max_shared, count)

    if max_shared >= min_shared_terms:
        classification = "LIKELY_ENFORCED_ELSEWHERE"
    elif max_shared >= 1:
        classification = "UNCERTAIN"
    else:
        classification = "LIKELY_STILL_LIVE"

    matched.sort(key=lambda m: len(m.shared_terms), reverse=True)

    return LessonFlag(
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        classification=classification,
        shared_term_count=max_shared,
        matched_sources=matched[:5],
    )
