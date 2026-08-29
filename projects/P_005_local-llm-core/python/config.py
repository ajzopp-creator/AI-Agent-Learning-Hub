"""Central configuration parameters and file paths for P_005."""

from pathlib import Path

# Base Paths
PYTHON_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PYTHON_DIR.parent
HUB_ROOT = PROJECT_ROOT.parent.parent

# Config & Doc Paths
CONFIGS_DIR = PROJECT_ROOT / "configs"
CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_CONFIG_PATH = CONFIGS_DIR / "model_config.json"

DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
BENCHMARK_LOG_PATH = DOCS_DIR / "BENCHMARKS.md"

# LM Studio Server Defaults
DEFAULT_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_API_KEY = "lm-studio"
DEFAULT_MODEL_ALIAS = "deepseek-r1-distill-qwen-14b"
DEFAULT_TIMEOUT_SECONDS = 90.0

# Inference Hyperparameters
DEFAULT_TEMPERATURE = 0.0
DEFAULT_TOP_P = 0.95
DEFAULT_MAX_TOKENS = 2048

# Guardrails & System Limits
MAX_CONTEXT_TOKENS = 8192
RESERVE_OUTPUT_TOKENS = 1024
MAX_TOOL_ITERATIONS = 5

# Benchmark Settings
DEFAULT_BENCHMARK_PROMPT = "Explain the difference between TCP and UDP in 3 concise bullet points."