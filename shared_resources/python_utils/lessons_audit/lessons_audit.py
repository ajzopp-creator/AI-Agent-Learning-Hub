# lessons_audit.py -- lessons_audit (WO-P000-E20.001)
# Application/CLI entry point. Thin orchestration only: wires
# infrastructure (I/O) and domain (logic) together. No logic of its own.
#
# Usage:
#   C:\Users\Trader\.conda\envs\p140\python.exe -m
#       shared_resources.python_utils.lessons_audit.lessons_audit
#
# P_000 pilot only (WO-P000-E20.001 Rollout) -- reference sources are
# hardcoded to config.P000_REFERENCE_SOURCES for this first build.
# Extending to other projects is a follow-on, not in scope here.
#
# v1.1 (2026-09-01): each reference source is now chunked before scoring
# (domain.chunk_reference_text), not scored as one pooled whole-file
# keyword set -- fixes the first-run false-positive bug (all 3 real
# lessons flagged). See domain.py module docstring for root cause.
#
# v1.4 (2026-09-04, Decision 3 revision): run() tries LM Studio
# classification first per lesson; on None (LM Studio unhealthy, not
# running, or an unparseable response) falls back to the existing
# v1.1-v1.3 keyword scorer (domain.classify_lesson) unchanged. Every flag
# records which path produced it (LessonFlag.classification_method) so a
# degraded run is never presented at LM Studio's confidence level. If LM
# Studio startup() fails once at the top of the run, every lesson goes
# straight to the keyword path -- no per-lesson health re-check.
# Per-lesson logic split into _classify_one_lesson() to keep run() under
# the 50-line hard limit -- the original inline-loop version was 56 lines.

from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path

from integrations.lm_studio.application.lm_studio_client import LMStudioClient
from shared_resources.python_utils.lessons_audit import config, domain, infrastructure
from shared_resources.python_utils.lessons_audit.schemas import AuditStatus

DEFAULT_LESSONS_PATH = (
    config.HUB_ROOT / "projects" / "P_000_PythonClaudeLocalLLM" / "tasks" / "lessons.md"
)


def _build_chunk_records(
    raw_sources: list[tuple[str, str, str]]
) -> list[tuple[str, str, str, set[str]]]:
    """Chunk every reference source, extract keywords per chunk, then
    drop corpus-generic words before scoring (v1.3 -- see domain.py
    module docstring for why a fixed stopword list alone isn't enough).

    Args:
        raw_sources: (source_type, source_path, full_text) triples.

    Returns:
        Flat (source_type, source_path, chunk_excerpt, chunk_keywords)
        records, one per chunk, with keywords already filtered for
        corpus-wide significance. Chunks left with no significant
        keywords after filtering are dropped.
    """
    raw_records = []
    for source_type, source_path, source_text in raw_sources:
        for chunk in domain.chunk_reference_text(source_text):
            chunk_keywords = domain.extract_keywords(
                chunk, config.STOPWORDS, config.MIN_TOKEN_LEN
            )
            if chunk_keywords:
                raw_records.append((source_type, source_path, chunk, chunk_keywords))

    doc_frequency = domain.compute_document_frequency(
        [keywords for _, _, _, keywords in raw_records]
    )

    filtered_records = []
    for source_type, source_path, chunk_excerpt, keywords in raw_records:
        significant = domain.filter_significant_keywords(
            keywords, doc_frequency, config.MAX_CHUNK_DOC_FREQUENCY
        )
        if significant:
            filtered_records.append((source_type, source_path, chunk_excerpt, significant))
    return filtered_records


async def _classify_one_lesson(
    client: LMStudioClient,
    lm_studio_healthy: bool,
    entry: dict,
    chunk_records: list[tuple[str, str, str, set[str]]],
    min_shared_terms: int,
):
    """Classify one lesson entry, trying LM Studio first when healthy.

    Returns:
        (flag, used_fallback) -- used_fallback is True whenever the
        keyword scorer produced the flag, whether because LM Studio was
        never tried (unhealthy at startup) or because it returned None.
    """
    lesson_keywords = domain.extract_keywords(
        entry["body"], config.STOPWORDS, config.MIN_TOKEN_LEN
    )

    flag = None
    if lm_studio_healthy:
        flag = await infrastructure.classify_via_lm_studio(
            client, entry["id"], entry["title"], entry["body"],
            lesson_keywords, chunk_records,
        )

    if flag is None:
        flag = domain.classify_lesson(
            entry["id"], entry["title"], lesson_keywords,
            chunk_records, min_shared_terms,
        )
        return flag, True

    return flag, False


async def run(lessons_path: Path, min_shared_terms: int) -> AuditStatus:
    """Run one audit pass and return the populated status object.

    Tries LM Studio classification first per lesson (v1.4); falls back to
    the keyword scorer on any failure. Method used is recorded per flag.
    """
    lessons_text = infrastructure.read_text_file(lessons_path)
    entries = domain.parse_lesson_entries(lessons_text)

    raw_sources = infrastructure.gather_reference_texts(config.P000_REFERENCE_SOURCES)
    chunk_records = _build_chunk_records(raw_sources)

    client = LMStudioClient()
    lm_studio_healthy = await client.startup()
    if not lm_studio_healthy:
        logging.warning("LM Studio unavailable -- all lessons will use the keyword fallback")

    flags = []
    fallback_count = 0
    for entry in entries:
        flag, used_fallback = await _classify_one_lesson(
            client, lm_studio_healthy, entry, chunk_records, min_shared_terms,
        )
        flags.append(flag)
        if used_fallback:
            fallback_count += 1

    if fallback_count:
        logging.warning(
            "%d of %d lessons used the keyword fallback (LM Studio unavailable or unparseable)",
            fallback_count, len(entries),
        )

    return AuditStatus(
        project_id="P_000",
        lessons_file=str(lessons_path),
        generated_at=datetime.now(timezone.utc),
        min_shared_terms=min_shared_terms,
        total_lessons=len(entries),
        flags=flags,
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Audit tasks/lessons.md for likely-superseded entries.")
    parser.add_argument("--lessons-path", type=Path, default=DEFAULT_LESSONS_PATH)
    parser.add_argument("--min-shared-terms", type=int, default=config.DEFAULT_MIN_SHARED_TERMS)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    output_path = args.output or (args.lessons_path.parent / config.OUTPUT_FILENAME)

    status = asyncio.run(run(args.lessons_path, args.min_shared_terms))
    infrastructure.write_status_json(status, output_path)

    counts: dict[str, int] = {}
    method_counts: dict[str, int] = {}
    for flag in status.flags:
        counts[flag.classification] = counts.get(flag.classification, 0) + 1
        method_counts[flag.classification_method] = method_counts.get(flag.classification_method, 0) + 1
    logging.info("Total lessons: %d | %s | methods: %s", status.total_lessons, counts, method_counts)


if __name__ == "__main__":
    main()
