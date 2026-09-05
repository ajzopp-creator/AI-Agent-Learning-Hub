# test_infrastructure.py -- lessons_audit (WO-P000-E20.001, v1.4)
# Permanent per Regression Test Governance -- coverage for the LM
# Studio/keyword-fallback boundary added 2026-09-04 (Decision 3
# revision). This is the one behavior that must never silently break: a
# failure signal from LM Studio must always produce None, never a crash
# or a flag mis-tagged with the wrong classification_method.

import asyncio

from shared_resources.python_utils.lessons_audit import config
from shared_resources.python_utils.lessons_audit.infrastructure import classify_via_lm_studio


class _StubClient:
    """Minimal stand-in for LMStudioClient.chat() -- avoids depending on
    a real LM Studio instance or a mocking library for this test."""

    def __init__(self, response_text):
        self._response_text = response_text
        self.last_task_type = None

    async def chat(self, messages, task_type=None, **kwargs):
        self.last_task_type = task_type
        return self._response_text


class _RaisingClient:
    """Stand-in that raises, simulating a dropped connection mid-call."""

    async def chat(self, messages, task_type=None, **kwargs):
        raise ConnectionError("simulated LM Studio drop")


_LESSON_KEYWORDS = {"wrapper", "architecture"}
_CHUNK_RECORDS = [
    ("ec_log", "doc.md", "wrapper architecture enforced rule", {"wrapper", "architecture"})
]


def test_classify_via_lm_studio_returns_flag_on_valid_response():
    """A well-formed response must produce a LessonFlag tagged LM_STUDIO,
    not the keyword fallback tag."""
    client = _StubClient("CLASSIFICATION: LIKELY_ENFORCED_ELSEWHERE")

    flag = asyncio.run(classify_via_lm_studio(
        client, "M-001", "Test Lesson", "Lesson body.", _LESSON_KEYWORDS, _CHUNK_RECORDS,
    ))

    assert flag is not None, "expected a LessonFlag, got None"
    assert flag.classification == "LIKELY_ENFORCED_ELSEWHERE"
    assert flag.classification_method == config.METHOD_LM_STUDIO


def test_classify_via_lm_studio_returns_none_on_empty_response():
    """chat() returning None/empty (LM Studio unhealthy or no response)
    must produce None -- the caller's signal to fall back, never a crash
    or a flag built from nothing."""
    client = _StubClient(None)

    flag = asyncio.run(classify_via_lm_studio(
        client, "M-002", "Test Lesson", "Lesson body.", _LESSON_KEYWORDS, _CHUNK_RECORDS,
    ))

    assert flag is None, f"expected None on empty response, got {flag}"


def test_classify_via_lm_studio_returns_none_on_unparseable_response():
    """A response with no recognizable CLASSIFICATION: line must fall
    back too, not silently default to some guessed classification."""
    client = _StubClient("The model never actually answered the question.")

    flag = asyncio.run(classify_via_lm_studio(
        client, "M-003", "Test Lesson", "Lesson body.", _LESSON_KEYWORDS, _CHUNK_RECORDS,
    ))

    assert flag is None, f"expected None on unparseable response, got {flag}"


def test_classify_via_lm_studio_returns_none_on_exception():
    """A dropped connection mid-call (raised exception, not a clean
    None) must be caught and treated as a fallback signal, never let an
    unhandled exception crash the whole audit run over one lesson."""
    client = _RaisingClient()

    flag = asyncio.run(classify_via_lm_studio(
        client, "M-004", "Test Lesson", "Lesson body.", _LESSON_KEYWORDS, _CHUNK_RECORDS,
    ))

    assert flag is None, f"expected None on raised exception, got {flag}"


def test_classify_via_lm_studio_uses_configured_task_type():
    """The call must route through the lesson_classification task type
    (config.LM_STUDIO_TASK_TYPE), confirming the wiring to
    integrations\\lm_studio\\config.py TASK_ROUTING actually happened,
    not just that some model answered."""
    client = _StubClient("CLASSIFICATION: UNCERTAIN")

    asyncio.run(classify_via_lm_studio(
        client, "M-005", "Test Lesson", "Lesson body.", _LESSON_KEYWORDS, _CHUNK_RECORDS,
    ))

    assert client.last_task_type == config.LM_STUDIO_TASK_TYPE
