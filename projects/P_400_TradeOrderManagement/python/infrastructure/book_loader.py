"""P_400 infrastructure: load open-position book from P400 vault records.

Reads *.md files from BOOK_DIR, extracts YAML frontmatter, validates
against BookRecord schema. CLOSED records are included so portfolio.py can
compute today's realized losses. Malformed files are logged and skipped.

Architecture v2.0 Section 6.1, 6.3.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List

import yaml

from config import BOOK_DIR
from schemas import BookRecord

logger = logging.getLogger("p400.book_loader")

# YAML frontmatter is bounded by triple-dashes at the start of the file.
_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# Vault filenames are "YYYY-MM-DD_SYMBOL.md" -- date prefix used as order_date
# (WO-P000-E10.001; BookRecord itself has no created/order timestamp field).
_FILENAME_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")


def _parse_frontmatter(path: Path) -> dict:
    """Extract and parse YAML frontmatter from a markdown file.

    Returns empty dict if no frontmatter block is found.
    """
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        logger.warning("No frontmatter in %s -- skipping", path.name)
        return {}
    return yaml.safe_load(match.group(1)) or {}


def load_book(book_dir: Path = BOOK_DIR) -> List[BookRecord]:
    """Load all P400 position records from the book directory.

    Includes CLOSED records for daily-loss calculation in portfolio.py.
    Records that fail BookRecord validation are logged and skipped -- never repaired.

    Args:
        book_dir: Folder containing *.md files. Defaults to BOOK_DIR from config.

    Returns:
        List of BookRecord objects. Returns [] if folder absent or no matching files.
    """
    if not book_dir.exists():
        logger.info("Book dir %s does not exist -- returning empty book", book_dir)
        return []

    records: List[BookRecord] = []
    for path in sorted(book_dir.glob("*.md")):  # fixed WO-P400-E2.012
        try:
            fm = _parse_frontmatter(path)
            if not fm:
                continue
            fm["symbol"] = fm.pop("ticker", fm.get("symbol"))
            fm["status"] = fm.pop("lifecycle_status", fm.get("status"))
            date_match = _FILENAME_DATE_RE.match(path.name)
            if date_match and "order_date" not in fm:
                fm["order_date"] = date_match.group(1)
            rec = BookRecord(**fm)
            records.append(rec)
        except Exception as exc:
            logger.warning("Skipping %s: %s", path.name, exc)

    logger.debug("Loaded %d book records from %s", len(records), book_dir)
    return records
