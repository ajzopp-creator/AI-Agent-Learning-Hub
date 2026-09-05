"""
LM Studio Native API Configuration
Centralized constants, paths, model definitions, and LM Studio endpoint settings.
"""

from pathlib import Path
from typing import TypedDict

# ── LM STUDIO ENDPOINT ────────────────────────────────────────────────────────
# Native v1 API endpoints (required by architecture)
LM_STUDIO_HOST = "http://localhost"
LM_STUDIO_PORT = 1234
LM_STUDIO_API_BASE = f"{LM_STUDIO_HOST}:{LM_STUDIO_PORT}/api/v1"
LM_STUDIO_CHAT_ENDPOINT = f"{LM_STUDIO_API_BASE}/chat"
LM_STUDIO_MODELS_ENDPOINT = f"{LM_STUDIO_API_BASE}/models"
LM_STUDIO_LOAD_ENDPOINT = f"{LM_STUDIO_API_BASE}/models/load"
LM_STUDIO_UNLOAD_ENDPOINT = f"{LM_STUDIO_API_BASE}/models/unload"

# ── HUB ROOT & PROJECT PATHS ──────────────────────────────────────────────────
HUB_ROOT = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub")
INTEGRATIONS_DIR = HUB_ROOT / "integrations" / "lm_studio"
PROMPTS_DIR = INTEGRATIONS_DIR / "prompts"
OUTPUTS_DIR = INTEGRATIONS_DIR / "outputs"

# Create directories if they don't exist
PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# ── THREE-TIER MODEL STACK ────────────────────────────────────────────────────
class ModelConfig(TypedDict):
    """Type definition for model configuration."""
    id: str
    name: str
    vram_gb: int
    use_case: str


MODELS = {
    "primary": ModelConfig(
        id="deepseek-r1-distill-qwen-14b",
        name="DeepSeek R1 14B (Primary Daily Driver)",
        vram_gb=10,
        use_case="Real-time analysis, coding, trade setup evaluation",
    ),
    "batch": ModelConfig(
        id="qwen2.5-coder-32b-instruct-abliterated",
        name="Qwen 32B (Batch Processing)",
        vram_gb=20,
        use_case="Heavy code generation, trade journal analysis, document summarization",
    ),
    "long_context": ModelConfig(
        id="llama-4-scout-17b-16e-instruct",
        name="Llama 4 Scout 17B (Long Context Specialist)",
        vram_gb=14,
        use_case="Documents over 128K tokens, full architecture ingestion",
    ),
}

# ── API TIMEOUT & RETRY SETTINGS ──────────────────────────────────────────────
HTTP_TIMEOUT_SECONDS = 90  # was 30 -- raised 2026-09-04 (WO-P000-E20.001 rollout): DeepSeek R1's chain-of-thought on non-trivial prompts ran 32-110s in the same day's P_300 calls, but send_chat_request's HTTP_TIMEOUT_SECONDS*3 chat timeout (90s) killed all 3 lessons_audit classification calls at the client-disconnect mark with only 2-4 reasoning tokens generated. New chat timeout: 270s.
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# ── CHAT GENERATION PARAMETERS ────────────────────────────────────────────────
TEMPERATURE_SETTINGS = {
    "analysis": 0.7,
    "coding": 0.3,
    "creative": 0.9,
}

CONTEXT_LENGTH = {
    "primary": 16384,
    "batch": 8192,
    "long_context": 65536,
}

# ── TASK-TO-MODEL ROUTING TABLE ───────────────────────────────────────────────
TASK_ROUTING = {
    "market_analysis": "primary",
    "trade_setup_evaluation": "primary",
    "quick_coding": "primary",
    "python_debugging": "primary",
    "sql_schema_design": "primary",
    "vantagepoint_analysis": "primary",
    "lesson_classification": "primary",
    "trade_journal_analysis": "batch",
    "document_summarization": "batch",
    "code_generation_heavy": "batch",
    "pattern_analysis": "batch",
    "full_document_ingestion": "long_context",
    "architecture_review": "long_context",
    "large_codebase_analysis": "long_context",
}

# ── LOGGING ───────────────────────────────────────────────────────────────────
LOG_DIR = OUTPUTS_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "lm_studio_client.log"
# Diagnostic log for LM Studio server console output (overwrites each run)
LMS_DIAG_LOG = LOG_DIR / "lms_diag.log"
