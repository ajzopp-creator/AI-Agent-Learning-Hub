# config.py -- lessons_audit (WO-P000-E20.001)
# Constants, paths, thresholds. No logic, no I/O.

from pathlib import Path

HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")

# Conservative by default per Tony's 2026-09-01 decision: require multiple
# shared terms before flagging a lesson as likely-enforced-elsewhere, not
# a single shared keyword.
DEFAULT_MIN_SHARED_TERMS = 3

# v1.3 fix: a word appearing in more than this many chunks across the
# reference corpus is corpus-generic noise (e.g. "check"/"status"/"rule"
# in a governance document) even when it isn't in STOPWORDS -- a fixed
# English stopword list can't catch corpus-specific pervasiveness.
MAX_CHUNK_DOC_FREQUENCY = 5

# Tokens shorter than this are dropped before scoring (cuts noise from
# short common words that survive the stopword list).
MIN_TOKEN_LEN = 4

OUTPUT_FILENAME = "lessons_audit_status.json"

# P_000 pilot reference sources (WO-P000-E20.001 Rollout: pilot on P_000
# before Hub-wide adoption). Each entry is a (source_type, path) pair.
P000_REFERENCE_SOURCES = [
    ("completion_gate", HUB_ROOT / "Agentic-Hub-Governance" / "work_orders" / "WO_COMPLETION_GATE.md"),
    ("ec_log", HUB_ROOT / "projects" / "P_000_PythonClaudeLocalLLM" / "docs" / "P_000_SYSTEM_DOCUMENTATION.md"),
    ("skill_file", HUB_ROOT / ".claude" / "skills" / "system-doc-initializer" / "SKILL.md"),
]

# Generic English words common in lesson/rule prose that would otherwise
# inflate false-positive overlap. Not exhaustive -- tune after first run.
STOPWORDS = frozenset({
    "this", "that", "these", "those", "with", "from", "were", "have",
    "been", "which", "when", "then", "also", "into", "before", "after",
    "should", "would", "could", "never", "always", "must", "will", "does",
    "each", "same", "only", "such", "than", "over", "here", "there",
    "their", "about", "against", "while", "where", "what", "your", "session",
})

# ---------------------------------------------------------------------------
# LM Studio classification (v1.4, WO-P000-E20.001 Decision 3 revision,
# 2026-09-04). Keyword overlap above is retained as the fallback path, not
# the primary classifier -- see domain.py module docstring v1.3 note: the
# real run still false-flagged all 3 live lessons after three fix rounds.
# ---------------------------------------------------------------------------

# Must match a key added to integrations\lm_studio\config.py TASK_ROUTING.
LM_STUDIO_TASK_TYPE = "lesson_classification"

# Top-N keyword-scored candidate chunks handed to LM Studio as evidence per
# lesson. Keeps each call small and focused instead of pooling the whole
# reference corpus (WO_COMPLETION_GATE.md + P_000_SYSTEM_DOCUMENTATION.md +
# skill file) into every one of N lesson prompts.
LM_STUDIO_CANDIDATE_CHUNK_COUNT = 8

# Result-tagging constants -- every LessonFlag records which path produced
# it, so a degraded (fallback) run is never presented at LM Studio's
# confidence level.
METHOD_LM_STUDIO = "LM_STUDIO"
METHOD_KEYWORD_FALLBACK = "KEYWORD_FALLBACK"

# {lesson_id}/{lesson_title}/{lesson_body}/{evidence_block} are filled in by
# domain.build_classification_prompt(). Answer format is a single anchored
# line so parse_llm_classification_response() can find it even ahead of a
# reasoning model's (DeepSeek R1) preceding chain-of-thought text.
CLASSIFICATION_PROMPT_TEMPLATE = """You are auditing a lessons-learned log for a software project. Decide whether the LESSON below is already enforced elsewhere in the project's governance documents, or whether it is still the only place this rule lives.

LESSON ({lesson_id}): {lesson_title}
{lesson_body}

CANDIDATE EVIDENCE (top keyword-matched excerpts from governance docs):
{evidence_block}

Answer using exactly this format, with nothing else on that line:
CLASSIFICATION: LIKELY_ENFORCED_ELSEWHERE
or
CLASSIFICATION: LIKELY_STILL_LIVE
or
CLASSIFICATION: UNCERTAIN

LIKELY_ENFORCED_ELSEWHERE means the evidence above already states this exact rule as an enforced requirement, not just related vocabulary. LIKELY_STILL_LIVE means none of the evidence actually states this rule. UNCERTAIN means the evidence is related but does not clearly confirm or rule out enforcement.
"""
