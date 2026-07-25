"""dispose_failed.py -- Auto-dispose Tier-1 FAIL packets after screen_all().

Application layer: orchestration only. Calls drop_signal() (existing
E2.011-era function) on every FAIL result from domain.screen.screen_all(),
using the FAIL's own reason codes as drop_reason. PASS and WARN results
are left untouched -- WARN-tier disposal (e.g. SIGNAL_STALE) is out of
scope for this WO.

WO-P400-E2.018.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from config import TradeMode
from domain.screen import SCREEN_FAIL, ScreenResult
from shared_resources.python_utils.signal_schemas import SignalV2

logger = logging.getLogger("p400.dispose_failed")


@dataclass
class DisposalOutcome:
    """Result of attempting to dispose one FAILed packet."""
    symbol: str
    drop_reason: str
    archived: bool
    written: bool

    def summary_line(self) -> str:
        status = "OK" if (self.archived and self.written) else "PARTIAL/FAILED"
        return (
            f"  DISPOSED | {self.symbol:6s} | drop_reason={self.drop_reason} "
            f"| archive={'OK' if self.archived else 'FAIL'} "
            f"| record={'OK' if self.written else 'FAIL'} | {status}"
        )


def _find_packet(symbol: str, packets: List[SignalV2]) -> SignalV2 | None:
    matches = [p for p in packets if p.symbol.upper() == symbol.upper()]
    return matches[0] if matches else None


def dispose_failed(
    results: List[ScreenResult],
    packets: List[SignalV2],
    trade_mode: TradeMode,
) -> List[DisposalOutcome]:
    """Auto-dispose every FAIL result from a screen_all() run.

    Args:
        results: Output of domain.screen.screen_all().
        packets: The same SignalV2 packets that were screened (result.load.valid).
        trade_mode: REAL or PAPER -- tags the vault record accordingly.

    Returns:
        List of DisposalOutcome, one per FAILed symbol actually disposed.
        Symbols with no matching packet are logged and skipped.
    """
    from application.drop_signal import drop_signal

    outcomes: List[DisposalOutcome] = []

    for r in results:
        if r.outcome != SCREEN_FAIL:
            continue

        packet = _find_packet(r.symbol, packets)
        if packet is None:
            logger.warning("dispose_failed: no packet found for FAIL symbol %s", r.symbol)
            continue

        drop_reason = "+".join(r.reason_codes) if r.reason_codes else "UNKNOWN"
        ok = drop_signal(packet, drop_reason, trade_mode)
        archived_and_written = ok  # drop_signal returns archived and written

        outcomes.append(
            DisposalOutcome(
                symbol=r.symbol,
                drop_reason=drop_reason,
                archived=archived_and_written,
                written=archived_and_written,
            )
        )
        logger.info(
            "dispose_failed: %s drop_reason=%s ok=%s", r.symbol, drop_reason, ok
        )

    return outcomes