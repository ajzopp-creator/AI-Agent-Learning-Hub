"""Command Line Interface (CLI) for P_035 Local Vector RAG Engine.

Provides terminal commands to inspect vector store status, index local directories
(or Obsidian vaults), execute semantic similarity queries, and clear the database.
"""

import argparse
import logging
from pathlib import Path
import sys

# Ensure python directory is at the root of sys.path
_MODULE_DIR = Path(__file__).resolve().parent
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

from application.rag_service import RagService
from config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_INGEST_DIR,
    DEFAULT_SIMILARITY_TOP_K,
    LOG_DATE_FORMAT,
    LOG_FORMAT,
)
from schemas import SearchQuery

# Setup logging format
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger("P_035_CLI")


def handle_status(service: RagService) -> None:
    """Displays health and count metrics for the local RAG engine."""
    status = service.get_status()
    print("\n=== P_035 Local RAG Engine Status ===")
    print(f"Embedding Service Online : {status['embedding_service_online']}")
    print(f"Indexed Chunks Count     : {status['indexed_chunks_count']}")
    print("=====================================\n")


def handle_index(service: RagService, args: argparse.Namespace) -> None:
    """Executes directory ingestion and reports performance metrics."""
    target_path = Path(args.path) if args.path else DEFAULT_INGEST_DIR
    print(f"\n[Indexing] Scanning directory: {target_path}")
    print(f"[Indexing] Chunk size: {args.chunk_size}, Overlap: {args.chunk_overlap}")

    summary = service.index_directory(
        directory_path=target_path,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    print("\n=== Ingestion Summary ===")
    print(f"Files Discovered : {summary.files_discovered}")
    print(f"Files Processed  : {summary.files_processed}")
    print(f"Chunks Created   : {summary.chunks_created}")
    print(f"Chunks Stored    : {summary.chunks_stored}")
    print(f"Duration (sec)   : {summary.duration_seconds}s")
    if summary.failed_files:
        print(f"Failed Files ({len(summary.failed_files)}):")
        for fail in summary.failed_files:
            print(f"  - {fail}")
    print("=========================\n")


def handle_query(service: RagService, args: argparse.Namespace) -> None:
    """Executes a semantic similarity query and displays retrieved context."""
    query_text = " ".join(args.query_text)
    if not query_text.strip():
        print("Error: Query text cannot be empty.")
        sys.exit(1)

    print(f"\n[Query] Searching for: '{query_text}' (top_k={args.top_k})\n")

    search_req = SearchQuery(
        query_text=query_text,
        top_k=args.top_k,
        score_threshold=args.threshold,
    )

    response = service.query(search_req)

    print(f"Retrieved {response.total_results} matching chunks:\n")
    for idx, item in enumerate(response.results, start=1):
        source = item.metadata.get("source_path", item.doc_id)
        print(f"[{idx}] Source: {source}")
        print(f"    Score: {item.score:.4f} | Cosine Distance: {item.distance:.4f}")
        print(f"    Text Preview: {item.text[:200]}...")
        print("-" * 60)

    if args.show_context:
        print("\n=== Assembled Prompt Context Block ===")
        print(response.formatted_context)
        print("======================================\n")


def handle_clear(service: RagService) -> None:
    """Clears all records in the ChromaDB collection."""
    confirm = input("Are you sure you want to clear the entire vector database? (y/N): ")
    if confirm.lower() == "y":
        service.clear_index()
        print("Vector database cleared successfully.")
    else:
        print("Clear operation canceled.")


def main() -> None:
    """CLI argument parser setup and routing."""
    parser = argparse.ArgumentParser(
        description="P_035 Local Vector RAG Engine CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Status Command
    subparsers.add_parser("status", help="Check vector store status and embedder health")

    # Index Command
    index_parser = subparsers.add_parser("index", help="Index a directory of documents or Obsidian vault")
    index_parser.add_argument("--path", type=str, default=None, help="Directory path to scan")
    index_parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Tokens per chunk")
    index_parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP, help="Overlap tokens")

    # Query Command
    query_parser = subparsers.add_parser("query", help="Run semantic similarity query")
    query_parser.add_argument("query_text", nargs="+", help="Natural language query string")
    query_parser.add_argument("--top-k", type=int, default=DEFAULT_SIMILARITY_TOP_K, help="Number of chunks")
    query_parser.add_argument("--threshold", type=float, default=None, help="Distance cutoff filter")
    query_parser.add_argument("--show-context", action="store_true", help="Print formatted prompt context")

    # Clear Command
    subparsers.add_parser("clear", help="Clear all records in the Chroma collection")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    service = RagService()

    if args.command == "status":
        handle_status(service)
    elif args.command == "index":
        handle_index(service, args)
    elif args.command == "query":
        handle_query(service, args)
    elif args.command == "clear":
        handle_clear(service)


if __name__ == "__main__":
    main()