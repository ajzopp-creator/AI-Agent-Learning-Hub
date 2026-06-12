"""Signal reading orchestration.

Calls infrastructure (scan/load) and domain (classify) in sequence, assembles
a ReadResult. No raw logic, no direct I/O.
"""

from dataclasses import dataclass
from pathlib import Path

from config import LEGACY_PATTERN, SIGNALS_DIR, TOLERATE_LEGACY
from domain.packet_classifier import PacketKind, classify
from infrastructure.signal_loader import LoadResult, load_v2_signals


@dataclass
class ReadResult:
    """Summary of one read pass over the signals folder."""

    load: LoadResult
    legacy_count: int

    @property
    def valid_count(self) -> int:
        """Number of packets that parsed and validated."""
        return len(self.load.valid)

    @property
    def rejected_count(self) -> int:
        """Number of packets that failed read or validation."""
        return len(self.load.rejected)


def _count_legacy(signals_dir: Path) -> int:
    """Count legacy *_signal.json packets without parsing them."""
    if not TOLERATE_LEGACY or not signals_dir.exists():
        return 0
    return len(list(signals_dir.glob(LEGACY_PATTERN)))


def read_signals(signals_dir: Path = SIGNALS_DIR) -> ReadResult:
    """Read all signals: validate v2 packets, count tolerated legacy packets.

    Args:
        signals_dir: Folder to scan. Defaults to the configured signals dir.

    Returns:
        ReadResult bundling the v2 load outcome and the legacy count.
    """
    load = load_v2_signals(signals_dir)
    legacy = _count_legacy(signals_dir)
    return ReadResult(load=load, legacy_count=legacy)


def classify_kinds(filenames: list[str]) -> dict[PacketKind, int]:
    """Tally filenames by PacketKind (audit helper)."""
    tally: dict[PacketKind, int] = {k: 0 for k in PacketKind}
    for name in filenames:
        tally[classify(name)] += 1
    return tally
