"""Infrastructure client for local vector embedding generation.

Communicates with local OpenAI-compatible embedding endpoints (Ollama / LM Studio)
to convert text payloads into dense vector representations.
"""

import logging
from typing import List, Optional
import requests

from config import (
    EMBEDDING_API_URL,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """Client wrapper for local HTTP-based embedding endpoints."""

    def __init__(
        self,
        api_url: str = EMBEDDING_API_URL,
        model_name: str = EMBEDDING_MODEL_NAME,
        timeout: float = EMBEDDING_TIMEOUT_SECONDS,
    ) -> None:
        """Initializes the embedding client.

        Args:
            api_url: Full URL to the OpenAI-compatible /v1/embeddings endpoint.
            model_name: Name of the local embedding model (e.g. nomic-embed-text).
            timeout: Network request timeout in seconds.
        """
        self._api_url = api_url
        self._model_name = model_name
        self._timeout = timeout

    def check_health(self) -> bool:
        """Verifies if the embedding endpoint is reachable.

        Returns:
            True if endpoint responds successfully, False otherwise.
        """
        try:
            sample_res = self.get_single_embedding("health check")
            return len(sample_res) > 0
        except Exception as exc:
            logger.warning("Embedding service health check failed: %s", exc)
            return False

    def get_single_embedding(self, text: str) -> List[float]:
        """Generates a dense vector embedding for a single text string.

        Args:
            text: Input string to embed.

        Returns:
            List of float values representing the dense embedding vector.

        Raises:
            RuntimeError: If the remote endpoint returns an error or invalid format.
        """
        batch_res = self.get_batch_embeddings([text])
        if not batch_res:
            raise RuntimeError("Empty response received from embedding service.")
        return batch_res[0]

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of text strings.

        Args:
            texts: List of text strings to embed.

        Returns:
            List of embedding vectors matching the order of input texts.

        Raises:
            RuntimeError: If the request fails or status code is not 200.
        """
        if not texts:
            return []

        all_embeddings: List[List[float]] = []

        # Process in configured batch sizes
        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            chunk = texts[i : i + EMBEDDING_BATCH_SIZE]
            payload = {
                "model": self._model_name,
                "input": chunk,
            }

            try:
                response = requests.post(
                    self._api_url,
                    json=payload,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                data = response.json()

                # Extract embedding items sorted by index
                items = data.get("data", [])
                items_sorted = sorted(items, key=lambda x: x.get("index", 0))
                batch_vectors = [item["embedding"] for item in items_sorted]
                all_embeddings.extend(batch_vectors)

            except requests.RequestException as exc:
                logger.error("Embedding request failed for batch: %s", exc)
                raise RuntimeError(
                    f"Failed to generate embeddings from {self._api_url}: {exc}"
                ) from exc

        return all_embeddings