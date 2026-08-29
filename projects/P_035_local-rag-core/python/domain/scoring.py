"""Domain logic for similarity scoring, ranking, and context assembly.

Provides pure functions for filtering similarity results, converting distances
to normalized similarity scores, and formatting retrieved chunks into an LLM context block.
"""

from typing import List, Optional
from schemas import SearchResultItem


def distance_to_similarity_score(distance: float) -> float:
    """Converts cosine distance into a bounded similarity score [0.0, 1.0].

    For cosine distance in range [0, 2]:
    similarity = max(0.0, 1.0 - (distance / 2.0))

    Args:
        distance: Floating point cosine distance metric.

    Returns:
        Normalized similarity score where 1.0 is identical.
    """
    normalized = 1.0 - (distance / 2.0)
    return round(max(0.0, min(1.0, normalized)), 4)


def filter_and_rank_results(
    results: List[SearchResultItem],
    max_distance_threshold: Optional[float] = None,
    top_k: int = 4,
) -> List[SearchResultItem]:
    """Filters search results by distance threshold and sorts by highest score.

    Args:
        results: Unfiltered list of retrieved search items.
        max_distance_threshold: Maximum allowed cosine distance cutoff.
        top_k: Maximum number of top ranked items to retain.

    Returns:
        Sorted and filtered list of SearchResultItem instances.
    """
    filtered = results
    if max_distance_threshold is not None:
        filtered = [item for item in results if item.distance <= max_distance_threshold]

    # Sort descending by similarity score (ascending by distance)
    ranked = sorted(filtered, key=lambda x: x.distance)
    return ranked[:top_k]


def build_formatted_context(results: List[SearchResultItem]) -> str:
    """Assembles a structured text block suitable for injecting into LLM prompts.

    Args:
        results: Ranked list of SearchResultItem objects.

    Returns:
        Formatted context string with source citations.
    """
    if not results:
        return "No relevant context found in local knowledge base."

    context_blocks: List[str] = []
    for idx, item in enumerate(results, start=1):
        source = item.metadata.get("source_path", item.doc_id)
        header = f"--- Context Source [{idx}]: {source} (Score: {item.score:.3f}) ---"
        block = f"{header}\n{item.text.strip()}"
        context_blocks.append(block)

    return "\n\n".join(context_blocks)