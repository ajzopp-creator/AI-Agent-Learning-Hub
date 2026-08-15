"""params_history_writer.py -- pure markdown edits for the
"over time" sections of P_000_Account_Parameters_Current.md: Growth
Projections current row, Parameter History append, Next Review date
(WO-P020-E1.011). No file I/O here -- infrastructure/p000_params_writer.py
owns that. Split out from domain/params_md_writer.py to keep both files
comfortably under the project's 250-line split-warning threshold.
"""

from __future__ import annotations

GROWTH_HEADER = "## Growth Projections"
HISTORY_HEADER = "## Parameter History"
NEXT_REVIEW_PREFIX = "**Next Review:**"


def upsert_growth_current_row(markdown: str, current_row: str) -> str:
    """Replace the '(current)' row in the Growth Projections table. The
    fixed milestone rows ($35K/$40K/$50K/$75K/$100K) are static and
    excluded by NOT containing '(current)'.

    Args:
        markdown: Full file content.
        current_row: Full replacement row, e.g.
            "| $31,348.39 (current) | $470.23 | $1,567.42 |".

    Returns:
        Updated markdown text.

    Raises:
        ValueError: If the table cannot be located.
    """
    lines = markdown.split("\n")
    try:
        start = lines.index(GROWTH_HEADER)
    except ValueError:
        raise ValueError(f"'{GROWTH_HEADER}' section not found")

    for i in range(start, len(lines)):
        if lines[i].startswith("|") and "(current)" in lines[i]:
            lines[i] = current_row
            break

    return "\n".join(lines)


def append_history_row(markdown: str, row: str) -> str:
    """Append one row to the Parameter History table. Never edits or
    removes existing rows (WO-P020-E1.011 acceptance criterion).

    Args:
        markdown: Full file content.
        row: Full formatted row, e.g.
            "| Aug 9, 2026 | $30,502.00 | $457.53 | $1,525.10 | ... |".

    Returns:
        Updated markdown text.

    Raises:
        ValueError: If the table cannot be located.
    """
    lines = markdown.split("\n")
    try:
        start = lines.index(HISTORY_HEADER)
    except ValueError:
        raise ValueError(f"'{HISTORY_HEADER}' section not found")

    table_start = None
    for i in range(start, len(lines)):
        if lines[i].startswith("|-"):
            table_start = i + 1
            break
    if table_start is None:
        raise ValueError("Parameter History table header not found")

    table_end = table_start
    while table_end < len(lines) and lines[table_end].startswith("|"):
        table_end += 1

    lines.insert(table_end, row)
    return "\n".join(lines)


def update_next_review(markdown: str, new_text: str) -> str:
    """Replace the '**Next Review:**' line near the top of the file.

    Args:
        markdown: Full file content.
        new_text: Full replacement value after the label, e.g.
            "September 2026 (monthly) or when balance hits $35,000".

    Returns:
        Updated markdown text. No-op (returns unchanged) if the line
        cannot be found -- never guesses a new location.
    """
    lines = markdown.split("\n")
    for i, line in enumerate(lines):
        if line.startswith(NEXT_REVIEW_PREFIX):
            lines[i] = f"{NEXT_REVIEW_PREFIX} {new_text}"
            break
    return "\n".join(lines)
