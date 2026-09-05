# schemas.py -- lessons_audit (WO-P000-E20.001)
# Pydantic models for the audit status output contract. Required before any
# non-temp file write, per Hub-wide schema rule.
#
# v1.1 (2026-09-01): MatchedSource gained chunk_excerpt -- fix for the
# first-run false-positive bug where scoring against a whole pooled
# document flagged all 3 real lessons as LIKELY_ENFORCED_ELSEWHERE.
# Chunk-level matching now lets a flagged entry show exactly which line
# matched, not just which file.

from datetime import datetime

from pydantic import BaseModel, Field


class MatchedSource(BaseModel):
    """One reference-source CHUNK (table row / checklist line / paragraph)
    whose keywords overlapped a lesson entry -- never a whole file pooled
    together (see domain.chunk_reference_text)."""

    source_type: str  # "completion_gate" | "ec_log" | "skill_file"
    source_path: str
    chunk_excerpt: str
    shared_terms: list[str]


class LessonFlag(BaseModel):
    """Audit result for a single M-series lesson entry."""

    lesson_id: str
    lesson_title: str
    classification: str  # LIKELY_ENFORCED_ELSEWHERE | UNCERTAIN | LIKELY_STILL_LIVE
    classification_method: str = "KEYWORD_FALLBACK"  # LM_STUDIO | KEYWORD_FALLBACK; defaults to KEYWORD_FALLBACK because domain.classify_lesson() (the keyword-only path) never sets this explicitly
    shared_term_count: int
    matched_sources: list[MatchedSource] = Field(default_factory=list)


class AuditStatus(BaseModel):
    """Top-level status file written by lessons_audit.py.

    INIT reads this file as a fact (per WO-P000-E20.001 design) rather
    than re-deriving the staleness judgment from memory each session.
    """

    project_id: str
    lessons_file: str
    generated_at: datetime
    min_shared_terms: int
    total_lessons: int
    flags: list[LessonFlag] = Field(default_factory=list)
