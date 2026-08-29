"""Data schemas and Pydantic models for P_035 Local Vector RAG Engine.

Defines typed representations for raw documents, text chunks, embeddings,
similarity search queries, search results, and ingestion summaries.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RawDocument(BaseModel):
    """Represents an un-chunked source document loaded from disk."""

    doc_id: str = Field(..., description="Unique identifier or relative file path.")
    source_path: str = Field(..., description="Absolute path on disk.")
    content: str = Field(..., description="Full text content of the document.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="File metadata.")
    char_count: int = Field(0, description="Total characters in content.")
    loaded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of file loading.",
    )


class TextChunk(BaseModel):
    """Represents a split unit of text derived from a RawDocument."""

    chunk_id: str = Field(..., description="Composite key: {doc_id}::chunk_{index}")
    doc_id: str = Field(..., description="Parent document identifier.")
    chunk_index: int = Field(..., description="Zero-based sequence index.")
    text: str = Field(..., description="Text segment payload.")
    token_estimate: int = Field(..., description="Estimated word/token count.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata.")


class EmbeddedChunk(BaseModel):
    """Represents a text chunk paired with its vector embedding."""

    chunk_id: str
    doc_id: str
    text: str
    embedding: List[float] = Field(..., description="Dense float vector.")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchQuery(BaseModel):
    """Represents a retrieval query against the vector store."""

    query_text: str = Field(..., min_length=1, description="Natural language search query.")
    top_k: int = Field(default=4, ge=1, le=50, description="Max chunks to retrieve.")
    score_threshold: Optional[float] = Field(
        default=None, description="Max cosine distance allowed (lower = closer)."
    )
    filter_metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Key-value filters for metadata matching."
    )


class SearchResultItem(BaseModel):
    """A single retrieved chunk with its similarity score and distance."""

    chunk_id: str
    doc_id: str
    text: str
    score: float = Field(..., description="Similarity score (1.0 = identical).")
    distance: float = Field(..., description="Cosine distance metric.")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Aggregated response containing ranked retrieval results and context."""

    query: str
    total_results: int
    results: List[SearchResultItem] = Field(default_factory=list)
    formatted_context: str = Field(
        default="", description="Ready-to-inject LLM context block."
    )


class IngestionSummary(BaseModel):
    """Summary report produced after an indexing run."""

    files_discovered: int = 0
    files_processed: int = 0
    chunks_created: int = 0
    chunks_stored: int = 0
    failed_files: List[str] = Field(default_factory=list)
    duration_seconds: float = 0.0