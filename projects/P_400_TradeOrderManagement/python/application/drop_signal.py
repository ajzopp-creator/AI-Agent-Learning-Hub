"""drop_signal.py -- Archive a signal as REVIEWED_NO_TRADE without evaluation.

Application layer: orchestration only -- no business logic, no direct I/O.
Called by cli.py cmd_evaluate() when --drop-reason flag is set.
"""

from __future__ import annotations

import logging
from config import TradeMode
from infrastructure.signal_archiver import archive_packet
from infrastructure.record_writer import write_p400_record
from infrastructure.posture_reader import read_posture
from shared_resources.python_utils.signal_schemas import SignalV2

logger = logging.getLogger("p400.drop_signal")


def drop_signal(packet: SignalV2, drop_reason: str, trade_mode: TradeMode) -> bool:
    """Archive packet and write REVIEWED_NO_TRADE record.

    Args:
        packet: The SignalV2 packet to drop.
        drop_reason: MANUAL_PASS | ENTRY_MISSED | RR_INVALID | COUNCIL_BLOCK
        trade_mode: REAL or PAPER.

    Returns:
        True if archive and record both succeeded.
    """
    symbol = packet.symbol
    signal_date = packet.signal_metadata.session_date
    posture = read_posture()

    archived = archive_packet(symbol, signal_date)
    if not archived:
        logger.warning("drop_signal: archive_packet failed for %s", symbol)

    written = write_p400_record(
        symbol=symbol,
        verdict="REVIEWED_NO_TRADE",
        risk_mode=posture.risk_mode,
        entry_price=packet.guideline_entry,
        stop_price=packet.guideline_stop,
        target_1=packet.guideline_target,
        position_size=0,
        signal_source=packet.signal_source,
        trade_mode_value=trade_mode.value,
        drop_reason=drop_reason,
        signal_date=signal_date,
    )

    logger.info("drop_signal: %s drop_reason=%s archived=%s written=%s",
                symbol, drop_reason, archived, written)
    return archived and written