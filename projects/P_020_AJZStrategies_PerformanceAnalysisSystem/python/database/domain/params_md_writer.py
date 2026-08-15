"""params_md_writer.py -- pure markdown edits for
P_000_Account_Parameters_Current.md (WO-P020-E1.009, extended by
WO-P020-E1.011). No file I/O here -- infrastructure/p000_params_writer.py
owns that. Growth Projections / Parameter History / Next Review live in
domain/params_history_writer.py -- kept separate to stay under the
project's file-size split threshold.
"""

from __future__ import annotations

from typing import Optional

ACTIVE_PARAMS_HEADER = "## Active Parameters"
CASH_NOTE_HEADER = "### Cash Balance (Separate Concept)"
CASH_NOTE_MARKER = "**Note (WO-P020-E1.009):**"
CASH_NOTE_TEXT = (
    f"{CASH_NOTE_MARKER} Buying Power and Cash Available for Trading in "
    "the table above are broker-reported reference numbers only. "
    "P_400's `--cash` flag stays a manual figure Tony types himself -- "
    "never auto-read from these fields."
)
RISK_MODE_HEADER = "## Risk Mode Adjustments (from P_010_RiskConfig.json)"
GATE_HEADER = "### Three-Gate Position Sizing"


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


def parse_last_written_balance(markdown: str) -> Optional[float]:
    """Read the current 'Account Balance' cell from the Active Parameters
    table and parse it to a float, for the WO-P020-E1.011 write-threshold
    comparison.

    Args:
        markdown: Full file content.

    Returns:
        Parsed balance, or None if the row/format is not found -- caller
        (account_params_calc.should_write) treats None as "always write"
        rather than silently blocking sync forever.
    """
    lines = markdown.split("\n")
    try:
        start = lines.index(ACTIVE_PARAMS_HEADER)
    except ValueError:
        return None

    for line in lines[start:]:
        if line.strip().startswith("| Account Balance"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2:
                raw = cells[1].replace("$", "").replace(",", "")
                try:
                    return float(raw)
                except ValueError:
                    return None
    return None


def upsert_risk_mode_table(
    markdown: str, mode_pairs: dict[str, tuple[str, str]]
) -> str:
    """Update Risk/Trade and Max Position cells in the Risk Mode
    Adjustments table. The Notes column (avg_posture ranges) is never
    touched -- WO-P020-E1.011 only keeps dollar values in sync, not the
    mode-selection thresholds themselves.

    Args:
        markdown: Full file content.
        mode_pairs: {mode_label: (risk_cell, max_cell)}.

    Returns:
        Updated markdown text.

    Raises:
        ValueError: If the table cannot be located.
    """
    lines = markdown.split("\n")
    try:
        start = lines.index(RISK_MODE_HEADER)
    except ValueError:
        raise ValueError(f"'{RISK_MODE_HEADER}' section not found")

    table_start = None
    for i in range(start, len(lines)):
        if lines[i].startswith("|-"):
            table_start = i + 1
            break
    if table_start is None:
        raise ValueError("Risk Mode Adjustments table header not found")

    table_end = table_start
    while table_end < len(lines) and lines[table_end].startswith("|"):
        table_end += 1

    remaining = dict(mode_pairs)
    for i in range(table_start, table_end):
        cells = [c.strip() for c in lines[i].strip("|").split("|")]
        if len(cells) >= 4 and cells[0] in remaining:
            risk_cell, max_cell = remaining.pop(cells[0])
            lines[i] = f"| {cells[0]} | {risk_cell} | {max_cell} | {cells[3]} |"

    return "\n".join(lines)


def upsert_gate_block(markdown: str, gate1_text: str, gate3_text: str) -> str:
    """Replace the Gate 1 and Gate 3 lines inside the fenced code block
    under '### Three-Gate Position Sizing'. Gate 2 and the Final Position
    line are static prose and untouched.

    Args:
        markdown: Full file content.
        gate1_text: Full replacement line, e.g.
            "Gate 1 (Risk-Based):    $470.23 / (Entry - Stop)".
        gate3_text: Full replacement line for Gate 3.

    Returns:
        Updated markdown text.

    Raises:
        ValueError: If the section cannot be located.
    """
    lines = markdown.split("\n")
    try:
        start = lines.index(GATE_HEADER)
    except ValueError:
        raise ValueError(f"'{GATE_HEADER}' section not found")

    for i in range(start, len(lines)):
        if lines[i].startswith("Gate 1"):
            lines[i] = gate1_text
        elif lines[i].startswith("Gate 3"):
            lines[i] = gate3_text
        elif lines[i].strip() == "```" and i > start + 1:
            break

    return "\n".join(lines)
