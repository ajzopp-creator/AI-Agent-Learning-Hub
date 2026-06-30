"""signal_schemas.py — Re-export shim (P_800 domain layer).

All model bodies now live in the neutral shared contract:
    shared_resources/python_utils/signal_schemas.py

This module is a thin re-export so the P_800 facade (obsidian_writers.schemas)
and SCHEMA_REGISTRY continue to import from domain.signal_schemas with zero
call-site changes inside P_800.

External consumers (P_400, P_115, P_300) must import from the shared location:
    from shared_resources.python_utils.signal_schemas import SignalV2

DO NOT add logic here. If a name is missing from __all__, the facade breaks.
Relocated in WO-P800-E2.002.
"""

from shared_resources.python_utils.signal_schemas import (  # noqa: F401
    AssetClass,
    OptionType,
    P400SignalRecord,
    SignalContext,
    SignalMetadata,
    SignalV2,
)

__all__ = [
    "AssetClass",
    "OptionType",
    "P400SignalRecord",
    "SignalContext",
    "SignalMetadata",
    "SignalV2",
]
