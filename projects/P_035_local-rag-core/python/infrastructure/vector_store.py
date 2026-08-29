"""Infrastructure wrapper for persistent ChromaDB vector store.

Manages local collection initialization, document chunk upserts, metadata
storage, and vector similarity queries.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings

from config import CHROMA_COLLECTION_NAME, DEFAULT_DB_DIR
from schemas import EmbeddedChunk, SearchResultItem

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Persistent local vector storage using ChromaDB."""

    def __init__(
        self,
        db_path: Path = DEFAULT_DB_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME,
    ) -> None:
        """Initializes persistent ChromaDB client and gets/creates collection.

        Args:
            db_path: Path to the local directory where Chroma stores data.
            collection_name: Name of the vector collection.
        """
        self._db_path = Path(db_path)
        self._db_path.mkdir(parents=True, exist_ok=True)
        self._collection_name = collection_name

        self._client = chromadb.PersistentClient(
            path=str(self._db_path),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "ChromaVectorStore initialized at %s with collection '%s'",
            self._db_path,
            self._collection_name,
        )

    def count(self) -> int:
        """Returns the total number of chunks currently indexed.

        Returns:
            Total integer count of records in the collection.
        """
        return self._collection.count()

    def upsert_chunks(self, chunks: List[EmbeddedChunk]) -> int:
        """Upserts embedded chunks into the persistent collection.

        Args:
            chunks: List of EmbeddedChunk objects containing IDs, embeddings, and text.

        Returns:
            Count of chunks successfully upserted.
        """
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        embeddings = [c.embedding for c in chunks]
        documents = [c.text for c in chunks]

        # Chroma metadata values must be str, int, float, or bool
        metadatas: List[Dict[str, Any]] = []
        for c in chunks:
            clean_meta = {}
            for k, v in c.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)
            clean_meta["doc_id"] = c.doc_id
            metadatas.append(clean_meta)

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("Successfully upserted %d chunks to ChromaDB", len(chunks))
        return len(chunks)

    def query_similarity(
        self,
        query_vector: List[float],
        top_k: int = 4,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResultItem]:
        """Queries the vector store using a dense vector embedding.

        Args:
            query_vector: Dense embedding vector for the search query.
            top_k: Number of nearest neighbors to retrieve.
            where_filter: Optional metadata filtering dictionary.

        Returns:
            List of SearchResultItem instances.
        """
        if self._collection.count() == 0:
            return []

        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self._collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        output: List[SearchResultItem] = []
        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
            doc_id = meta.get("doc_id", "unknown")
            output.append(
                SearchResultItem(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    text=doc_text,
                    score=round(max(0.0, 1.0 - (dist / 2.0)), 4),
                    distance=round(dist, 4),
                    metadata=meta,
                )
            )

        return output

    def clear_collection(self) -> None:
        """Deletes all items in the collection."""
        self._client.delete_collection(name=self._collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Cleared all records in collection '%s'", self._collection_name)