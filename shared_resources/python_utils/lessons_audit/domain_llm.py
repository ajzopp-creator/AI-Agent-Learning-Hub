# domain_llm.py -- lessons_audit (WO-P000-E20.001, v1.4 addition 2026-09-04)
# Pure logic for the LM Studio classification path: candidate-evidence
# selection, prompt building, response parsing. No file/network I/O -- see
# infrastructure.py for the actual LM Studio call. Split out from domain.py
# rather than added to it: this is a different reason to change (prompt
# engineering) than domain.py's keyword-overlap scoring, and domain.py was
# already at 192 lines -- adding ~70 more would cross the 250-line
# split-warning threshold. domain.py's v1.1-v1.3 keyword scorer is
# untouched by this file; it's called from here only via score_overlap()
# for candidate ranking, reusing already-hardened logic rather than
# duplicating it.

from __future__ import annotations

import re

from shared_resources.python_utils.lessons_audit.domain import score_overlap

_CLASSIFICATION_LINE = re.compile(
    r"CLASSIFICATION:\s*(LIKELY_ENFORCED_ELSEWHERE|LIKELY_STILL_LIVE|UNCERTAIN)",
    re.IGNORECASE,
)


def select_top_candidate_chunks(
    lesson_keywords: set[str],
    chunk_records: list[tuple[str, str, str, set[str]]],
    top_n: int,
) -> list[tuple[str, str, str]]:
    """Select the top-N reference chunks by keyword overlap with a lesson,
    for use as LM Studio evidence -- reuses domain.score_overlap (the same
    machinery the keyword-overlap fallback scorer uses for its final
    verdict) here only for candidate ranking, not a classification.

    Args:
        lesson_keywords: Keywords extracted from the lesson body.
        chunk_records: (source_type, source_path, chunk_excerpt,
            chunk_keywords) records, same shape domain.classify_lesson
            consumes.
        top_n: Maximum number of chunks to return.

    Returns:
        Up to top_n (source_type, source_path, chunk_excerpt) triples,
        ranked by shared keyword count descending. Chunks with zero
        overlap are excluded even if fewer than top_n remain -- no
        overlap means no relevant evidence to show the model.
    """
    scored = []
    for source_type, source_path, chunk_excerpt, chunk_keywords in chunk_records:
        count, _shared = score_overlap(lesson_keywords, chunk_keywords)
        if count > 0:
            scored.append((count, source_type, source_path, chunk_excerpt))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [(s_type, s_path, excerpt) for _count, s_type, s_path, excerpt in scored[:top_n]]


def build_classification_prompt(
    lesson_id: str,
    lesson_title: str,
    lesson_body: str,
    candidate_chunks: list[tuple[str, str, str]],
    template: str,
) -> str:
    """Build the LM Studio prompt for one lesson's classification call.

    Args:
        lesson_id: e.g. "M-001".
        lesson_title: The entry's title text.
        lesson_body: The entry's full body text.
        candidate_chunks: (source_type, source_path, chunk_excerpt) triples
            from select_top_candidate_chunks -- never the full reference
            corpus pooled together.
        template: config.CLASSIFICATION_PROMPT_TEMPLATE.

    Returns:
        The filled prompt string, ready to send as a single user message.
    """
    if candidate_chunks:
        evidence_block = "\n".join(
            f"- [{source_type}] {chunk_excerpt}"
            for source_type, _source_path, chunk_excerpt in candidate_chunks
        )
    else:
        evidence_block = "(no keyword-matched candidates found)"

    return template.format(
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        lesson_body=lesson_body,
        evidence_block=evidence_block,
    )


def parse_llm_classification_response(response_text: str) -> str | None:
    """Extract the classification label from an LM Studio response.

    Args:
        response_text: Raw chat response text. May contain a reasoning
            model's (DeepSeek R1) preceding chain-of-thought -- this
            searches the whole text for the anchored "CLASSIFICATION:"
            line rather than assuming it's the first or only content.

    Returns:
        One of LIKELY_ENFORCED_ELSEWHERE / LIKELY_STILL_LIVE / UNCERTAIN,
        or None if no recognizable classification line was found -- the
        caller treats None the same as any other LM Studio failure and
        falls back to the keyword scorer.
    """
    match = _CLASSIFICATION_LINE.search(response_text)
    if not match:
        return None
    return match.group(1).upper()
