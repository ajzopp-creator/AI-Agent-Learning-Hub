"""Domain logic for document chunking and token estimation.

Provides pure functions for splitting text and Markdown content into overlapping
segments optimized for embedding generation and semantic retrieval without any I/O.
"""

import re
from typing import List

from schemas import RawDocument, TextChunk


def estimate_token_count(text: str) -> int:
    """Estimates the token count of a given text string.

    Uses whitespace and punctuation segmentation as a fast local proxy
    for subword tokenizers (~1.3 words per token ratio).

    Args:
        text: Input string to measure.

    Returns:
        Estimated token count as an integer.
    """
    if not text:
        return 0
    words = len(text.split())
    return max(1, int(words * 1.3))


def split_text_by_paragraphs(text: str) -> List[str]:
    """Splits raw text into natural blocks based on double newlines and markdown headings.

    Args:
        text: Source document content.

    Returns:
        List of non-empty string segments.
    """
    normalized = text.replace("\r\n", "\n")
    # Split on double newlines or markdown headers (# H1, ## H2, etc.)
    raw_blocks = re.split(r"\n{2,}|(?=\n#{1,6}\s)", normalized)
    return [b.strip() for b in raw_blocks if b.strip()]


def create_sliding_window_chunks(
    blocks: List[str],
    chunk_size: int,
    chunk_overlap: int,
) -> List[str]:
    """Combines paragraph blocks into chunks within target token bounds with overlap.

    Args:
        blocks: List of paragraph or structural text segments.
        chunk_size: Maximum estimated token capacity per chunk.
        chunk_overlap: Number of tokens/words to overlap between adjacent chunks.

    Returns:
        List of formatted text chunk payloads.
    """
    if not blocks:
        return []

    chunks: List[str] = []
    current_segments: List[str] = []
    current_tokens = 0

    for block in blocks:
        block_tokens = estimate_token_count(block)

        # If a single block exceeds the max chunk size, break it into smaller lines/sentences
        if block_tokens > chunk_size:
            if current_segments:
                chunks.append("\n\n".join(current_segments))
                current_segments = []
                current_tokens = 0

            sub_words = block.split()
            for i in range(0, len(sub_words), chunk_size - chunk_overlap):
                segment = " ".join(sub_words[i : i + chunk_size])
                if segment:
                    chunks.append(segment)
            continue

        if current_tokens + block_tokens > chunk_size and current_segments:
            chunks.append("\n\n".join(current_segments))
            # Retain the last block if within overlap bounds
            if current_segments and estimate_token_count(current_segments[-1]) <= chunk_overlap:
                current_segments = [current_segments[-1], block]
                current_tokens = estimate_token_count("\n\n".join(current_segments))
            else:
                current_segments = [block]
                current_tokens = block_tokens
        else:
            current_segments.append(block)
            current_tokens += block_tokens

    if current_segments:
        chunks.append("\n\n".join(current_segments))

    return chunks


def chunk_document(
    document: RawDocument,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[TextChunk]:
    """Transforms a RawDocument into an ordered list of typed TextChunks.

    Args:
        document: The source raw document to chunk.
        chunk_size: Target token capacity per chunk.
        chunk_overlap: Token overlap between consecutive chunks.

    Returns:
        List of TextChunk instances ready for embedding.
    """
    blocks = split_text_by_paragraphs(document.content)
    raw_chunks = create_sliding_window_chunks(blocks, chunk_size, chunk_overlap)

    output: List[TextChunk] = []
    for idx, text_payload in enumerate(raw_chunks):
        chunk_id = f"{document.doc_id}::chunk_{idx:04d}"
        tokens = estimate_token_count(text_payload)
        chunk_metadata = {
            **document.metadata,
            "source_path": document.source_path,
            "chunk_index": idx,
            "total_chunks": len(raw_chunks),
        }

        output.append(
            TextChunk(
                chunk_id=chunk_id,
                doc_id=document.doc_id,
                chunk_index=idx,
                text=text_payload,
                token_estimate=tokens,
                metadata=chunk_metadata,
            )
        )

    return output