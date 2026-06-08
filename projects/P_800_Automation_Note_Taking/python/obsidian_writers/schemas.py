"""schemas.py — Import facade for vault and signal schemas.

Root-level imports expose all schema classes for backward-compatible callers.
Actual schemas split into domain/{vault,signal}_schemas.py (WO-P800-E2 follow-up).

CHANGELOG:
  v2.4  2026-06-08  Split schemas.py (355 lines) into domain/{vault,signal}_schemas.py.
                    Root now imports + SCHEMA_REGISTRY facade. Maintains backward-compat.
  v2.3  2026-06-07  Fixed SignalV2 option-completeness validation (model_validator).
  v2.2  2026-06-07  Wired SIGNAL_V2 into registry; unified SignalContext/SignalMetadata.
  v2.1  2026-06-02  Added P400SignalRecord + registered "P400SIG".
  v2.0  2026-06-01  Note Standard v1.1 + verdict normalization.
"""

from pydantic import BaseModel

# ── VAULT SCHEMAS (Obsidian frontmatter records) ──────────────────────────────

from .domain.vault_schemas import (
    P115Record,
    P300Record,
    P020Record,
    P400Record,
    KBRecord,
)

# ── SIGNAL SCHEMAS (JSON packet models) ────────────────────────────────────────

from .domain.signal_schemas import (
    SignalContext,
    SignalMetadata,
    AssetClass,
    OptionType,
    P400SignalRecord,
    SignalV2,
)

# ── SCHEMA REGISTRY ───────────────────────────────────────────────────────────
# Single source of truth. Callers use: from obsidian_writers.schemas import SCHEMA_REGISTRY

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "P115":      P115Record,
    "P300":      P300Record,
    "P020":      P020Record,
    "P400":      P400Record,
    "P400SIG":   P400SignalRecord,
    "SIGNAL_V2": SignalV2,
    "KB":        KBRecord,
}

__all__ = [
    "P115Record",
    "P300Record",
    "P020Record",
    "P400Record",
    "KBRecord",
    "SignalContext",
    "SignalMetadata",
    "AssetClass",
    "OptionType",
    "P400SignalRecord",
    "SignalV2",
    "SCHEMA_REGISTRY",
]