"""Local document and Obsidian vault file loader.

Discovers, filters, and parses disk files into normalized RawDocument models
while excluding build artifacts, vendor directories, and virtual environments.

Changelog:
----------
- v1.0.0 (2026-08-18) - Gemini (Authored) / Anthony J. Zoppi (Directed): Baseline file discovery and loader.
- v1.0.1 (2026-08-18) - Gemini (Authored) / Anthony J. Zoppi (Directed): Added directory exclusion set and sys.path fix.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterator, List, Optional, Set

from config import SUPPORTED_EXTENSIONS
from schemas import RawDocument

__version__ = "1.0.1"
__author__ = "Gemini"
__maintainer__ = "Anthony J. Zoppi"
__date__ = "2026-08-18"

logger = logging.getLogger(__name__)

DEFAULT_IGNORED_DIRS: Set[str] = {
    ".git",
    ".github",
    ".vscode",
    ".idea",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".conda",
    ".venv",
    "venv",
    "env",
    "chroma_db",
    "dist",
    "build",
    "site-packages",
}


class LocalFileLoader:
    """Discovers and loads plain text and markdown documents from local disk."""

    def __init__(
        self,
        supported_extensions: tuple[str, ...] = SUPPORTED_EXTENSIONS,
        ignored_dirs: Optional[Set[str]] = None,
        max_file_size_bytes: int = 10 * 1024 * 1024,  # 10 MB limit
    ) -> None:
        """Initializes the loader."""
        self._extensions = tuple(ext.lower() for ext in supported_extensions)
        self._ignored_dirs = ignored_dirs or DEFAULT_IGNORED_DIRS
        self._max_size = max_file_size_bytes

    def scan_directory(self, root_path: Path) -> List[Path]:
        """Recursively discovers matching files while filtering out ignored directories."""
        discovered: List[Path] = []
        target_dir = Path(root_path).resolve()

        if not target_dir.exists():
            logger.warning("Target directory does not exist: %s", target_dir)
            return discovered

        if target_dir.is_file():
            if target_dir.suffix.lower() in self._extensions:
                return [target_dir]
            return []

        for root, dirs, files in os.walk(target_dir):
            # Prune ignored directories in-place to avoid descending into them
            dirs[:] = [d for d in dirs if d.lower() not in self._ignored_dirs]

            for file_name in files:
                file_path = Path(root) / file_name
                if file_path.suffix.lower() in self._extensions:
                    try:
                        if file_path.stat().st_size <= self._max_size:
                            discovered.append(file_path)
                    except OSError as exc:
                        logger.debug("Skipping unreadable file %s: %s", file_path, exc)

        logger.info(
            "Discovered %d indexable files in %s (ignoring vendor/runtime folders)",
            len(discovered),
            target_dir,
        )
        return discovered

    def load_single_file(self, file_path: Path) -> Optional[RawDocument]:
        """Reads a single file from disk and parses it into a RawDocument."""
        target = Path(file_path).resolve()
        if not target.is_file():
            logger.error("File does not exist: %s", target)
            return None

        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

            stats = target.stat()
            metadata = {
                "file_name": target.name,
                "file_extension": target.suffix.lower(),
                "file_size_bytes": stats.st_size,
                "modified_timestamp": stats.st_mtime,
            }

            return RawDocument(
                doc_id=target.name,
                source_path=str(target),
                content=content,
                metadata=metadata,
                char_count=len(content),
            )
        except Exception as exc:
            logger.error("Failed to read file %s: %s", target, exc)
            return None

    def load_all_from_directory(self, root_path: Path) -> Iterator[RawDocument]:
        """Generator yielding RawDocument instances for all discovered files."""
        files = self.scan_directory(root_path)
        for f in files:
            doc = self.load_single_file(f)
            if doc is not None:
                yield doc