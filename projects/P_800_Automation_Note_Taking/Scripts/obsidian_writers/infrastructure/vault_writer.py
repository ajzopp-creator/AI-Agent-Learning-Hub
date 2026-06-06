"""infrastructure/vault_writer.py — Write .md note files to the Obsidian vault.

I/O only — no business logic.
"""

from __future__ import annotations

from pathlib import Path

from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def write_note(file_path: Path, content: str, overwrite: bool = True) -> bool:
    """Write a markdown note to the vault.

    Creates any missing parent directories automatically.
    Skips the write if the file exists and overwrite=False.

    Args:
        file_path: Absolute path to the target .md file.
        content: Full note content including frontmatter.
        overwrite: If False, skip existing files without error.

    Returns:
        True if written, False if skipped.

    Raises:
        OSError: If the write fails due to permissions or disk error.
    """
    if file_path.exists() and not overwrite:
        log.info("Skipped (exists, overwrite=False): %s", file_path.name)
        return False

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        log.info("Written: %s", file_path.name)
        return True
    except OSError as exc:
        log.error("Failed to write %s: %s", file_path, exc)
        raise


def note_exists(file_path: Path) -> bool:
    """Check whether a vault note already exists.

    Args:
        file_path: Absolute path to the .md file.

    Returns:
        True if the file exists on disk.
    """
    return file_path.exists()
