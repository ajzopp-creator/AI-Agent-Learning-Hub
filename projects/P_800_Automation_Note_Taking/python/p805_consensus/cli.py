r"""cli.py -- command-line entry point for the P_805 Consensus Dashboard.

Run from the python\ folder with p140 conda env active:

    python -m p805_consensus.cli

Or double-click launch_consensus_dashboard.bat.
"""

from __future__ import annotations

import logging
import sys

from p805_consensus.application.consensus_dashboard_runner import run


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s -- %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> int:
    _setup_logging()
    logger = logging.getLogger(__name__)
    try:
        row_count = run()
    except Exception:
        logger.exception("Consensus dashboard run failed")
        return 1
    print(f"\nDone -- wrote {row_count} source rows to Dashboard.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())