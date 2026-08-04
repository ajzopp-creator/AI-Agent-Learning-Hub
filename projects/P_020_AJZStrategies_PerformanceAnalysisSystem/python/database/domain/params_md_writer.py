"""params_md_writer.py -- pure markdown edits for
P_000_Account_Parameters_Current.md (WO-P020-E1.009). No file I/O here --
infrastructure/p000_params_writer.py owns that.
"""

from __future__ import annotations

ACTIVE_PARAMS_HEADER = "## Active Parameters"
CASH_NOTE_HEADER = "### Cash Balance (Separate Concept)"
CASH_NOTE_MARKER = "**Note (WO-P020-E1.009):**"
CASH_NOTE_TEXT = (
    f"{CASH_NOTE_MARKER} Buying Power and Cash Available for Trading in "
    "the table above are broker-reported reference numbers only. "
    "P_400's `--cash` flag stays a manual figure Tony types himself -- "
    "never auto-read from these fields."
)


def upsert_active_parameter_rows(markdown: str, updates: dict[str, str]) -> str:
    """Insert or update rows in the '## Active Parameters' table.

    Args:
        markdown: Full file content.
        updates: {parameter_label: formatted_value_cell}.

    Returns:
        Updated markdown text.

    Raises:
        ValueError: If the Active Parameters table cannot be located.
    """
    lines = markdown.split("\n")
    try:
        start = lines.index(ACTIVE_PARAMS_HEADER)
    except ValueError:
        raise ValueError(f"'{ACTIVE_PARAMS_HEADER}' section not found")

    table_start = None
    for i in range(start, len(lines)):
        if lines[i].startswith("|-"):
            table_start = i + 1
            break
    if table_start is None:
        raise ValueError("Active Parameters table header not found")

    table_end = table_start
    while table_end < len(lines) and lines[table_end].startswith("|"):
        table_end += 1

    remaining = dict(updates)
    for i in range(table_start, table_end):
        cells = [c.strip() for c in lines[i].strip("|").split("|")]
        if cells and cells[0] in remaining:
            lines[i] = f"| {cells[0]} | {remaining.pop(cells[0])} |"

    new_rows = [f"| {label} | {value} |" for label, value in remaining.items()]
    lines[table_end:table_end] = new_rows

    return "\n".join(lines)


def ensure_cash_note(markdown: str) -> str:
    """Idempotently add the WO-P020-E1.009 clarification note.

    Inserted as the first line under '### Cash Balance (Separate Concept)'.
    No-op if the note is already present anywhere in the file.

    Args:
        markdown: Full file content.

    Returns:
        Updated markdown text.
    """
    if CASH_NOTE_MARKER in markdown:
        return markdown

    lines = markdown.split("\n")
    try:
        idx = lines.index(CASH_NOTE_HEADER)
    except ValueError:
        return markdown  # section renamed/missing -- do not guess a new spot

    lines.insert(idx + 1, CASH_NOTE_TEXT)
    return "\n".join(lines)
