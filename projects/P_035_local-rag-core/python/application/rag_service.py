"""Application service layer orchestrating local vector RAG workflows.

Coordinates file loading, document chunking, embedding generation, vector storage,
and semantic query execution across domain and infrastructure modules.
"""

import logging
import time
from pathlib import Path
from typing import Optional

from config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_INGEST_DIR,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_SIMILARITY_TOP_K,
)
from domain.chunking import chunk_document
from domain.scoring import build_formatted_context, filter_and_rank_results
from infrastructure.embedding_client import EmbeddingClient
from infrastructure.file_loader import LocalFileLoader
from infrastructure.vector_store import ChromaVectorStore
from schemas import (
    EmbeddedChunk,
    IngestionSummary,
    SearchQuery,
    SearchResponse,
)

logger = logging.getLogger(__name__)


class RagService:
    """Service orchestrating RAG indexing and retrieval operations."""

    def __init__(
        self,
        vector_store: Optional[ChromaVectorStore] = None,
        embedding_client: Optional[EmbeddingClient] = None,
        file_loader: Optional[LocalFileLoader] = None,
    ) -> None:
        """Initializes the service with dependency injection."""
        self._store = vector_store or ChromaVectorStore()
        self._embedder = embedding_client or EmbeddingClient()
        self._loader = file_loader or LocalFileLoader()

    def get_status(self) -> dict:
        """Returns the health status and current index size.

        Returns:
            Dictionary with health and count metrics.
        """
        service_online = self._embedder.check_health()
        total_chunks = self._store.count()
        return {
            "embedding_service_online": service_online,
            "indexed_chunks_count": total_chunks,
        }

    def index_directory(
        self,
        directory_path: Optional[Path] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> IngestionSummary:
        """Ingests and indexes all supported documents from a directory.

        Args:
            directory_path: Target directory (e.g. Obsidian vault or docs folder).
            chunk_size: Target token capacity per chunk.
            chunk_overlap: Token overlap between chunks.

        Returns:
            IngestionSummary containing metrics of the run.
        """
        target_dir = directory_path or DEFAULT_INGEST_DIR
        summary = IngestionSummary()
        start_time = time.time()

        files = self._loader.scan_directory(target_dir)
        summary.files_discovered = len(files)

        all_embedded_chunks = []

        for file_path in files:
            doc = self._loader.load_single_file(file_path)
            if doc is None:
                summary.failed_files.append(str(file_path))
                continue

            summary.files_processed += 1
            chunks = chunk_document(
                document=doc,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
            summary.chunks_created += len(chunks)

            if not chunks:
                continue

            # Generate embeddings in batch for this file
            texts_to_embed = [c.text for c in chunks]
            try:
                embeddings = self._embedder.get_batch_embeddings(texts_to_embed)
                for c, emb in zip(chunks, embeddings):
                    all_embedded_chunks.append(
                        EmbeddedChunk(
                            chunk_id=c.chunk_id,
                            doc_id=c.doc_id,
                            text=c.text,
                            embedding=emb,
                            metadata=c.metadata,
                        )
                    )
            except Exception as exc:
                logger.error("Failed embedding file %s: %s", file_path, exc)
                summary.failed_files.append(str(file_path))

        # Store all batches into ChromaDB
        if all_embedded_chunks:
            stored_count = self._store.upsert_chunks(all_embedded_chunks)
            summary.chunks_stored = stored_count

        summary.duration_seconds = round(time.time() - start_time, 2)
        return summary

    def query(self, search_query: SearchQuery) -> SearchResponse:
        """Performs semantic search against indexed knowledge base.

        Args:
            search_query: Search parameters and query text.

        Returns:
            SearchResponse containing ranked items and formatted LLM context.
        """
        # Step 1: Embed query text
        query_vector = self._embedder.get_single_embedding(search_query.query_text)

        # Step 2: Query vector store
        raw_results = self._store.query_similarity(
            query_vector=query_vector,
            top_k=search_query.top_k,
            where_filter=search_query.filter_metadata,
        )

        # Step 3: Domain scoring and threshold filtering
        threshold = (
            search_query.score_threshold
            if search_query.score_threshold is not None
            else DEFAULT_SIMILARITY_THRESHOLD
        )
        ranked_results = filter_and_rank_results(
            results=raw_results,
            max_distance_threshold=threshold,
            top_k=search_query.top_k,
        )

        # Step 4: Build prompt-ready context block
        formatted_context = build_formatted_context(ranked_results)

        return SearchResponse(
            query=search_query.query_text,
            total_results=len(ranked_results),
            results=ranked_results,
            formatted_context=formatted_context,
        )

    def clear_index(self) -> None:
        """Wipes the existing Chroma vector collection."""
        self._store.clear_collection()