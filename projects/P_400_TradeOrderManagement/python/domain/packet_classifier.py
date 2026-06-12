"""Packet classification — pure logic, no I/O.

Decides what kind of signal packet a filename represents so the loader knows
whether to parse it (v2), count-and-skip it (legacy), or ignore it (unknown).
"""

from enum import Enum


class PacketKind(str, Enum):
    """Classification of a signal file by its name."""

    V2 = "v2"
    LEGACY = "legacy"
    UNKNOWN = "unknown"


def classify(filename: str) -> PacketKind:
    """Classify a signal filename.

    Args:
        filename: Bare file name (not a full path), e.g. "2026-06-08_BATRA_v2.0.json".

    Returns:
        PacketKind.V2 for *_v2.0.json, PacketKind.LEGACY for *_signal.json,
        PacketKind.UNKNOWN otherwise.
    """
    name = filename.lower()
    if name.endswith("_v2.0.json"):
        return PacketKind.V2
    if name.endswith("_signal.json"):
        return PacketKind.LEGACY
    return PacketKind.UNKNOWN
