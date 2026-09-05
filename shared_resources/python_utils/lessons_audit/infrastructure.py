# infrastructure.py -- lessons_audit (WO-P000-E20.001)
# I/O only: reading lessons.md + reference sources, writing the status
# JSON, calling LM Studio. No business logic -- see domain.py/domain_llm.py.
#
# v1.4 (2026-09-04): added the LM Studio classification path. Split into
# classify_via_lm_studio() (orchestrator) + two helpers to keep every
# function under the 50-line hard limit -- the original single-function
# version was 68 lines.

from __future__ import annotations

import logging
from pathlib import Path

from integrations.lm_studio.application.lm_studio_client import LMStudioClient
from shared_resources.python_utils.lessons_audit import config, domain_llm
from shared_resources.python_utils.lessons_audit.schemas import AuditStatus, LessonFlag, MatchedSource

logger = logging.getLogger(__name__)


def read_text_file(path: Path) -> str:
    """Read a text file as UTF-8.

    Args:
        path: File to read.

    Returns:
        File contents, or "" if the file doesn't exist or can't be read.
        Missing reference sources are logged and skipped, not fatal --
        an audit run with fewer sources is still useful.
    """
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return ""


def gather_reference_texts(
    sources: list[tuple[str, Path]]
) -> list[tuple[str, str, str]]:
    """Read every configured reference source's raw text.

    Args:
        sources: (source_type, path) pairs, e.g. config.P000_REFERENCE_SOURCES.

    Returns:
        (source_type, path_as_str, text) triples. Sources that fail to
        read are omitted, not raised -- caller sees fewer sources, never
        a crash from one missing file.
    """
    results = []
    for source_type, path in sources:
        text = read_text_file(path)
        if text:
            results.append((source_type, str(path), text))
        else:
            logger.warning("Skipping empty/missing reference source: %s", path)
    return results


def write_status_json(status: AuditStatus, output_path: Path) -> None:
    """Write the audit status as UTF-8 JSON, no BOM.

    Args:
        status: Populated AuditStatus.
        output_path: Destination file (e.g. tasks\\lessons_audit_status.json).
    """
    output_path.write_text(
        status.model_dump_json(indent=2),
        encoding="utf-8",
    )
    logger.info("Wrote audit status: %s (%d flags)", output_path, len(status.flags))


async def _call_lm_studio_chat(
    client: LMStudioClient, prompt: str, lesson_id: str,
) -> str | None:
    """Send one classification prompt to LM Studio.

    Args:
        client: An already-started LMStudioClient.
        prompt: The filled classification prompt.
        lesson_id: Used only for the warning log line.

    Returns:
        Raw response text, or None on any failure (raised exception or
        empty/falsy response) -- caller treats None as a fallback signal.
    """
    try:
        response_text = await client.chat(
            messages=[{"role": "user", "content": prompt}],
            task_type=config.LM_STUDIO_TASK_TYPE,
        )
    except Exception as exc:
        logger.warning("LM Studio classification call failed for %s: %s", lesson_id, exc)
        return None

    if not response_text:
        logger.warning("LM Studio returned no response for %s -- falling back", lesson_id)
        return None
    return response_text


def _build_lm_studio_flag(
    lesson_id: str,
    lesson_title: str,
    classification: str,
    candidates: list[tuple[str, str, str]],
) -> LessonFlag:
    """Assemble the LessonFlag for a successful LM Studio classification,
    recording the candidate evidence shown to the model as matched_sources
    -- shared_terms is empty per source since this wasn't a keyword match,
    it's what the model was given to read.
    """
    matched_sources = [
        MatchedSource(
            source_type=s_type, source_path=s_path, chunk_excerpt=excerpt[:200], shared_terms=[]
        )
        for s_type, s_path, excerpt in candidates
    ]
    return LessonFlag(
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        classification=classification,
        classification_method=config.METHOD_LM_STUDIO,
        shared_term_count=0,
        matched_sources=matched_sources,
    )


async def classify_via_lm_studio(
    client: LMStudioClient,
    lesson_id: str,
    lesson_title: str,
    lesson_body: str,
    lesson_keywords: set[str],
    chunk_records: list[tuple[str, str, str, set[str]]],
) -> LessonFlag | None:
    """Classify one lesson via LM Studio inference.

    Args:
        client: An already-started (client.startup() called) LMStudioClient.
        lesson_id: e.g. "M-001".
        lesson_title: The entry's title text.
        lesson_body: The entry's full body text.
        lesson_keywords: Keywords extracted from the lesson body (used only
            to select candidate evidence chunks, not to classify).
        chunk_records: (source_type, source_path, chunk_excerpt,
            chunk_keywords) records, same shape the keyword fallback uses.

    Returns:
        A populated LessonFlag with classification_method=LM_STUDIO, or
        None on any failure (client unhealthy, no response, unparseable
        response) -- caller falls back to the keyword scorer on None.
    """
    candidates = domain_llm.select_top_candidate_chunks(
        lesson_keywords, chunk_records, config.LM_STUDIO_CANDIDATE_CHUNK_COUNT
    )
    prompt = domain_llm.build_classification_prompt(
        lesson_id, lesson_title, lesson_body, candidates, config.CLASSIFICATION_PROMPT_TEMPLATE
    )

    response_text = await _call_lm_studio_chat(client, prompt, lesson_id)
    if response_text is None:
        return None

    classification = domain_llm.parse_llm_classification_response(response_text)
    if classification is None:
        logger.warning(
            "LM Studio response for %s had no parseable CLASSIFICATION line -- falling back",
            lesson_id,
        )
        return None

    return _build_lm_studio_flag(lesson_id, lesson_title, classification, candidates)
