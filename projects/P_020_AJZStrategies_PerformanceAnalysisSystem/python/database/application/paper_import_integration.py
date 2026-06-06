"""
paper_import_integration.py — REFERENCE SNIPPET

Shows how to wire thinklog_parser into paper_import.py ingestion.
Not a standalone runnable script — copy the relevant function and call site
into the actual paper_import.py.

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application (integration pattern)
"""
from __future__ import annotations

from typing import Optional

# Import path inside paper_import.py:
#     from domain.thinklog_parser import parse_thinklog_note
from domain.thinklog_parser import parse_thinklog_note


def enrich_trade_with_thinklog(
    trade: dict,
    thinklog_text: Optional[str],
) -> dict:
    """
    Mutate trade dict in place and return it. Adds reason, signal_strength,
    and appends free-text notes from a ThinkLog note.

    - Does not overwrite existing reason/signal_strength if already set
    - Appends free-text notes with ' | ' separator if trade already has notes
    - Safe to call with thinklog_text=None (no-op)
    """
    if not thinklog_text:
        return trade

    parsed = parse_thinklog_note(thinklog_text)

    if parsed["reason"] and not trade.get("reason"):
        trade["reason"] = parsed["reason"]

    if parsed["signal_strength"] and not trade.get("signal_strength"):
        trade["signal_strength"] = parsed["signal_strength"]

    if parsed["notes"]:
        existing = (trade.get("notes") or "").strip()
        if existing:
            trade["notes"] = f"{existing} | {parsed['notes']}"
        else:
            trade["notes"] = parsed["notes"]

    return trade


# ----------------------------------------------------------------------------
# CALL SITE inside paper_import.py — inside the per-trade loop, right before
# the DB write:
#
#     for trade in parsed_trades:
#         thinklog_text = thinklog_reader.get_note_for_date(trade["open_date"])
#         trade = enrich_trade_with_thinklog(trade, thinklog_text)
#         db_writer.insert_trade(trade)
#
# And update the INSERT statement in db_writer to include the new columns:
#
#     INSERT INTO trades (
#         account_id, system, underlying_symbol, ...,
#         reason, signal_strength, notes,
#         source, schwab_transaction_id
#     ) VALUES (?, ?, ?, ..., ?, ?, ?, ?, ?)
#
# Run migration_add_tag_columns.py FIRST to add the columns to the DB.
# ----------------------------------------------------------------------------
