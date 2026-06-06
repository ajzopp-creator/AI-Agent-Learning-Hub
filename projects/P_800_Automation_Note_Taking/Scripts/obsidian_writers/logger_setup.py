"""logger_setup.py — Shared logging configuration for obsidian_writers package."""

import logging
import sys
from pathlib import Path

LOG_DIR = Path(r"C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\logs")
LOG_FILE = LOG_DIR / "vault_interface.log"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name.

    Args:
        name: Typically __name__ from the calling module.

    Returns:
        Configured Logger instance.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured — avoid duplicate handlers

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — INFO and above
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler — DEBUG and above
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
