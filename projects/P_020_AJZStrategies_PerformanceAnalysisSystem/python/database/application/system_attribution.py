"""System attribution orchestration (WO-P020-E1.007).

Runs each trade through the vault -> tracker -> default resolution chain
and tallies what the P_400 vault would have said. Split out of
ingest_pipeline.py, which hit 323 lines (over the 300 hard limit) when
this logic was added inline.

Orchestration only -- the chain itself is domain/system_resolver.py and
the vault read is infrastructure/vault_system_reader.py.

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\system_attribution.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""

import logging
from typing import Dict, List

from config import VAULT_MATCH_FORWARD_DAYS, VAULT_SHADOW_MODE
from domain.system_resolver import ShadowTally, resolve

logger = logging.getLogger(__name__)


def apply_system_names(
    trades: List[Dict],
    lookup,
    default: str,
    vault_lookup=None,
) -> ShadowTally:
    """Resolve each trade's system through the attribution chain.

    While VAULT_SHADOW_MODE is True the Tracker Dashboard stays
    authoritative -- the P_400 vault result is computed and tallied for
    comparison but never written to trade['system']. Modifies trade
    dicts in place.

    Args:
        trades: Trade dicts -- need 'underlying_symbol' and 'open_date'.
        lookup: TrackerLookup object or None.
        default: Fallback system name.
        vault_lookup: VaultLookup object or None.

    Returns:
        ShadowTally summarising vault coverage and agreement.
    """
    matched = 0
    tally = ShadowTally()

    for trade in trades:
        res = resolve(
            symbol=trade.get("underlying_symbol", ""),
            open_date=str(trade.get("open_date", "")),
            vault_lookup=vault_lookup,
            tracker_lookup=lookup,
            default=default,
            forward_days=VAULT_MATCH_FORWARD_DAYS,
            shadow_mode=VAULT_SHADOW_MODE,
        )
        trade["system"] = res.system
        tally.record(res)
        if res.system != default:
            matched += 1

    logger.info(
        f"System matching: {matched}/{len(trades)} matched, "
        f"{len(trades) - matched} defaulted to '{default}'."
    )
    logger.info(tally.summary())
    return tally
