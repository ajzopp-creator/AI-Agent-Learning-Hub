"""dashboard_section_writer.py -- patches Dashboard.md's P_805 Consensus section.

Writes UTF-8 no-BOM, LF-only, per the Hub file write standard.
"""

from __future__ import annotations

import logging

from p805_consensus.config import (
    DASHBOARD_PATH,
    SECTION_END_MARKER,
    SECTION_START_MARKER,
    TABLE_DIVIDER,
    TABLE_HEADER,
)
from p805_consensus.schemas import ConsensusRow

logger = logging.getLogger(__name__)


def _format_row(row: ConsensusRow) -> str:
    """One markdown table row for a ConsensusRow."""
    symbols = ", ".join(row.today_symbols) if row.today_symbols else "--"
    return (
        f"| {row.email_source} | {symbols} | {row.mtd_candidates} | "
        f"{row.ytd_candidates} | {row.mtd_buy_asym} | {row.ytd_buy_asym} |"
    )


def build_section_body(rows: list[ConsensusRow]) -> str:
    """Full markdown block for the section, markers included."""
    lines = [SECTION_START_MARKER, TABLE_HEADER, TABLE_DIVIDER]
    lines.extend(_format_row(r) for r in sorted(rows, key=lambda r: r.email_source))
    lines.append(SECTION_END_MARKER)
    return "\n".join(lines)


def write_section(rows: list[ConsensusRow]) -> None:
    """Replace the marker-delimited section of Dashboard.md in place.

    Raises ValueError if the markers are missing -- this writer never
    appends a new section on its own; marker insertion is a one-time
    manual step (see WO-P800-E6.001).
    """
    content = DASHBOARD_PATH.read_text(encoding="utf-8")
    if SECTION_START_MARKER not in content or SECTION_END_MARKER not in content:
        raise ValueError(
            f"Dashboard.md is missing {SECTION_START_MARKER} / "
            f"{SECTION_END_MARKER} -- insert them once before running this."
        )
    start = content.index(SECTION_START_MARKER)
    end = content.index(SECTION_END_MARKER) + len(SECTION_END_MARKER)
    new_content = content[:start] + build_section_body(rows) + content[end:]
    new_content = new_content.replace("\r\n", "\n")
    DASHBOARD_PATH.write_bytes(new_content.encode("utf-8"))
    logger.info("Dashboard.md P_805 Consensus section updated (%d rows)", len(rows))