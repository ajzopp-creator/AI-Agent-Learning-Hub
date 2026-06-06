r"""P_805 KB Writer — scan data/inbox/, convert emails to KB notes via P_800.

Scans data\inbox\ for .eml files. Determines processing mode (full or
summarized) via CLI flag or filename patterns. Writes to KB via P_800's
handle_write() interface. Deletes .eml on success.
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from email import message_from_binary_file

import config
from domain.headers import decode_header_safe
from infrastructure.lm_studio_caller import summarize
from obsidian_writers.application.write_handler import handle_write

logger = logging.getLogger("p805")


def determine_mode(filename: str, cli_mode: str) -> str:
    """Determine processing mode for a single .eml file.

    Per-file patterns override CLI default:
    - *--full.eml     -> "full"
    - *--summarize.eml -> "summary"
    - *.eml           -> use cli_mode
    """
    if re.search(config.KB_MODE_PATTERN_FULL, filename):
        logger.debug(f"File {filename} matches --full pattern")
        return "full"
    if re.search(config.KB_MODE_PATTERN_SUMMARIZE, filename):
        logger.debug(f"File {filename} matches --summarize pattern")
        return "summary"
    return cli_mode


def extract_eml_body(eml_path: Path) -> str:
    """Extract plain-text body from .eml file.

    Returns the message's get_payload() if plain text, or decodes
    multipart/alternative for text/plain. Falls back to empty string
    if undecodable.
    """
    try:
        with open(eml_path, "rb") as f:
            msg = message_from_binary_file(f)

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        return payload.decode("utf-8", errors="ignore")
                    return payload
            return ""
        else:
            payload = msg.get_payload(decode=True)
            if isinstance(payload, bytes):
                return payload.decode("utf-8", errors="ignore")
            return payload or ""

    except Exception as e:
        logger.error(f"Failed to extract body from {eml_path.name}: {e}")
        return ""


def build_kb_record(eml_path: Path, email_subject: str, email_from: str, ai_summarized: bool) -> dict:
    """Build KBRecord dict for P_800 write handler."""
    mtime = datetime.fromtimestamp(eml_path.stat().st_mtime).date()
    return {
        "date": mtime,
        "title": email_subject or eml_path.stem,
        "kb_type": "Article",
        "origin": "Email",
        "from": email_from,
        "ai_summarized": ai_summarized,
        "tags": [],
        "ticker_relevance": [],
        "sector": None,
        "market_regime": None,
        "linked_trades": [],
    }


def write_and_cleanup(kb_data: dict, body: str, eml_path: Path) -> bool:
    """Write to KB via P_800 handler. Delete .eml on success."""
    try:
        success = handle_write(
            schema_name="KB",
            data=kb_data,
            body=body,
            overwrite=False,
        )

        if success:
            try:
                eml_path.unlink()
                logger.info(f"KB write succeeded and {eml_path.name} deleted")
                return True
            except Exception as e:
                logger.warning(f"KB write succeeded but failed to delete {eml_path.name}: {e}")
                return True  # Write succeeded even if delete failed
        else:
            logger.error(f"KB write failed for {eml_path.name}; file not deleted")
            return False

    except Exception as e:
        logger.error(f"Unexpected error in write_and_cleanup: {e}")
        return False


def scan_kb_inbox(kb_mode: str, kb_lookback_days: int) -> None:
    r"""Scan data\inbox\ for .eml files and process each one.

    Args:
        kb_mode: "full" or "summary"
        kb_lookback_days: ignored for now (included for future use)
    """
    inbox_dir = config.PROJECT_ROOT / "data" / "inbox"

    if not inbox_dir.exists():
        logger.info(f"KB inbox folder does not exist: {inbox_dir}")
        inbox_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created KB inbox folder: {inbox_dir}")
        return

    eml_files = list(inbox_dir.glob("*.eml"))
    if not eml_files:
        logger.info(f"No .eml files in {inbox_dir}")
        return

    logger.info(f"Found {len(eml_files)} .eml files in {inbox_dir}")
    written_count = 0
    summarized_count = 0

    for eml_path in eml_files:
        try:
            # Determine mode for this file
            mode = determine_mode(eml_path.name, kb_mode)
            is_summarized = (mode == "summary")

            # Extract email metadata and body
            with open(eml_path, "rb") as f:
                msg = message_from_binary_file(f)

            email_subject = decode_header_safe(msg.get("Subject"))
            email_from = decode_header_safe(msg.get("From"))
            body = extract_eml_body(eml_path)

            if not body.strip():
                logger.warning(f"Skipping {eml_path.name}: empty body")
                continue

            # Summarize if requested
            if is_summarized:
                summary = summarize(
                    body,
                    url=config.LM_STUDIO_URL,
                    model=config.LM_STUDIO_MODEL,
                    temperature=config.LM_STUDIO_TEMP,
                    max_tokens=config.LM_STUDIO_MAX_TOKENS,
                    timeout=config.LM_STUDIO_TIMEOUT,
                )
                if summary:
                    body = summary
                    summarized_count += 1
                    logger.debug(f"Summarized {eml_path.name}")
                else:
                    logger.info(f"LM Studio failed for {eml_path.name}; using full text")
                    is_summarized = False

            # Build KBRecord
            kb_data = build_kb_record(eml_path, email_subject, email_from, is_summarized)

            # Write to KB
            if write_and_cleanup(kb_data, body, eml_path):
                written_count += 1

        except Exception as e:
            logger.error(f"Error processing {eml_path.name}: {e}")

    logger.info(
        f"KB write complete: {written_count} notes written "
        f"({summarized_count} summarized, {written_count - summarized_count} full)"
    )
