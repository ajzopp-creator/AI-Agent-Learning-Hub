"""Infrastructure: shared logging configuration.

Two loggers are configured:

  - 'p805'         → console (INFO+) + rotating file at config.LOG_FILE (DEBUG+)
  - 'p805.rejects' → rotating file at config.REJECT_LOG_FILE only (INFO+)

The reject logger has propagate=False so its lines do NOT also appear in
the main log or on the console. Call configure_logging() once at the top
of any application entry point. It is idempotent — safe to call again.
"""

import logging
from logging.handlers import RotatingFileHandler

import config


def _build_rotating_handler(path, level: int) -> RotatingFileHandler:
    """Create a 5 MB × 3-backup rotating file handler at the given path."""
    handler = RotatingFileHandler(
        path,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setLevel(level)
    return handler


def configure_logging() -> logging.Logger:
    """Configure the 'p805' and 'p805.rejects' loggers. Returns the main one."""
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    main = logging.getLogger("p805")
    if main.handlers:
        return main  # Already configured this run

    main.setLevel(logging.DEBUG)
    main.propagate = False

    # Console — concise format, INFO and above only.
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, config.LOG_LEVEL_CONSOLE))
    console.setFormatter(logging.Formatter("%(message)s"))
    main.addHandler(console)

    # File — full timestamped format, DEBUG and above.
    file_handler = _build_rotating_handler(
        config.LOG_FILE, getattr(logging, config.LOG_LEVEL_FILE)
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")
    )
    main.addHandler(file_handler)

    # Reject logger — separate file, no console, no propagation.
    rejects = logging.getLogger("p805.rejects")
    rejects.setLevel(logging.INFO)
    rejects.propagate = False
    if not rejects.handlers:
        reject_handler = _build_rotating_handler(config.REJECT_LOG_FILE, logging.INFO)
        reject_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
        rejects.addHandler(reject_handler)

    return main
