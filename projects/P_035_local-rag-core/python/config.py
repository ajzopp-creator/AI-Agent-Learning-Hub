"""Configuration module for P_035 Local Vector RAG Engine.

Defines default paths, embedding endpoints, persistent store settings,
and text chunking parameters for local document indexing and retrieval.
"""

from pathlib import Path
from typing import Final

# ----------------------------------------------------------------------
# Base Paths
# ----------------------------------------------------------------------
MODULE_DIR: Final[Path] = Path(__file__).resolve().parent
PROJECT_ROOT: Final[Path] = MODULE_DIR.parent
DEFAULT_DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
DEFAULT_DB_DIR: Final[Path] = DEFAULT_DATA_DIR / "chroma_db"
DEFAULT_INGEST_DIR: Final[Path] = DEFAULT_DATA_DIR / "documents"

# Ensure runtime directories exist
DEFAULT_DATA_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_INGEST_DIR.mkdir(parents=True, exist_ok=True)

## ----------------------------------------------------------------------
# Embedding Service Configuration (Local LM Studio)
# ----------------------------------------------------------------------
EMBEDDING_API_URL: Final[str] = "http://127.0.0.1:1234/v1/embeddings"
EMBEDDING_MODEL_NAME: Final[str] = "text-embedding-nomic-embed-text-v1.5"
EMBEDDING_BATCH_SIZE: Final[int] = 32
EMBEDDING_TIMEOUT_SECONDS: Final[float] = 30.0
EMBEDDING_VECTOR_DIM: Final[int] = 768
# ----------------------------------------------------------------------
# Vector Store (ChromaDB) Configuration
# ----------------------------------------------------------------------
CHROMA_COLLECTION_NAME: Final[str] = "p035_knowledge_base"
DEFAULT_SIMILARITY_TOP_K: Final[int] = 4
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.35

# ----------------------------------------------------------------------
# Text Chunking Defaults (Optimized for Markdown / Obsidian / Notes)
# ----------------------------------------------------------------------
DEFAULT_CHUNK_SIZE: Final[int] = 500
DEFAULT_CHUNK_OVERLAP: Final[int] = 50
SUPPORTED_EXTENSIONS: Final[tuple[str, ...]] = (
    ".md",
    ".txt",
    ".markdown",
    ".py",
    ".json",
)

# ----------------------------------------------------------------------
# Logging & Telemetry
# ----------------------------------------------------------------------
LOG_FORMAT: Final[str] = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"