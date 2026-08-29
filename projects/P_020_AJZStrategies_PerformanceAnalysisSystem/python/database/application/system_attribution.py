"""System attribution orchestration (WO-P020-E1.007).

Runs each trade through the full attribution chain (vault/tracker/default,
then ThinkLog, then P_820) and tallies what the P_400 vault would have
said. Split out of ingest_pipeline.py, which hit 315 lines (over the
300 hard limit) when the P_820 layer was added inline (2026-08-16).

Orchestration only -- each layer's own logic lives in its own module:
domain/system_resolver.py (vault/tracker/default), application/
live_thinklog.py (ThinkLog), application/p820_capture.py (P_820).

Save path: C:\\Users\\Trader\\AI-Agent-Learning-Hub\\projects\\
           P_020_AJZStrategies_PerformanceAnalysisSystem\\python\\
           database\\application\\system_attribution.py

Part of: P_020 AJZ Strategies Performance Analysis System
Layer:   application
"""

import logging
from typing import Dict, List, Optional

from application.live_thinklog import apply_thinklog_overrides
from application.p820_capture import apply_p820_overrides
from config import VAULT_MATCH_FORWARD_DAYS, VAULT_SHADOW_MODE
from domain.system_resolver import ShadowTally, resolve

logger = logging.getLogger(__name__)

IRA_ACCOUNT_ID = "IRA9885"


def apply_system_names(
    trades: List[Dict],
    lookup,
    default: str,
    vault_lookup=None,
) -> ShadowTally:
    """Resolve each trade's system through the vault/tracker/default chain.

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


def run_full_attribution(
    all_trades: List[Dict],
    lookup,
    vault_lookup,
    thinklog_lookup: Dict,
    p820_lookup: Dict,
    params: Dict,
    audit: List[str],
    account_id: str = "",
) -> None:
    """Run all attribution layers in priority order (lowest to highest).

    P_820 > ThinkLog > vault/Tracker/default -- each layer only overrides
    trades where it actually has a match; everything else passes through
    unchanged to the next layer. Extracted from ingest_pipeline.run_ingest()
    to keep that function under the 300-line limit (2026-08-16).

    IRA9885 bypasses the vault/Tracker/default layer entirely (WO-P020-E1.015
    Decision 1) -- same as paper. Tracker Dashboard has no meaningful IRA
    coverage and the P_400 vault is AJZ-only, so running that chain for IRA
    would only ever produce a TOS_Import default anyway; skipping it lets
    ThinkLog (INV or a real project code) be the sole system source, with
    no Tracker/vault detour that ThinkLog would just override regardless.

    Args:
        all_trades: Trade dicts, mutated in place through all three layers.
        lookup: TrackerLookup object or None.
        vault_lookup: VaultLookup object or None.
        thinklog_lookup: Lookup from application.live_thinklog.
                load_live_thinklog_lookup().
        p820_lookup: Lookup from infrastructure.p820_reader.load_p820_lookup().
        params: Loaded params dict -- needs 'default_system_name'.
        audit: Audit log line list -- appended to by each layer.
        account_id: Database account_id (e.g. 'AJZ6348', 'IRA9885'). Empty
                string preserves prior behavior (full vault/Tracker chain
                runs) -- only IRA9885 triggers the bypass.
    """
    if account_id == IRA_ACCOUNT_ID:
        audit.append(
            "System matching: IRA9885 bypasses vault/Tracker (WO-P020-E1.015) "
            "-- ThinkLog/P_820 only."
        )
    else:
        apply_system_names(
            all_trades, lookup, params["default_system_name"], vault_lookup=vault_lookup,
        )
    tl_count = apply_thinklog_overrides(all_trades, thinklog_lookup, audit)
    if tl_count:
        audit.append(f"ThinkLog overrides applied: {tl_count}")
    p820_count = apply_p820_overrides(all_trades, p820_lookup, audit)
    if p820_count:
        audit.append(f"P_820 overrides applied: {p820_count}")


def explain_default(raw: Dict, vault_lookup, default: str) -> Optional[str]:
    """Explain a TOS_Import default for the weekly audit log.

    Only meaningful for trades that defaulted. Looks at ANY P_400
    record (any status) via VaultLookup.nearest_any -- diagnostic
    only, does not affect attribution (that stays shadow-mode via
    apply_system_names above). Distinguishes "P_400 reviewed and
    passed" from "nobody ever ran P_400 evaluate on this," since
    evaluate is a manual per-symbol command, not gated to inbox
    signals from P_115/116/117/118/300.

    Args:
        raw: Trade dict, must carry 'system', 'underlying_symbol', 'open_date'.
        vault_lookup: VaultLookup instance, or None.
        default: The default system name (e.g. 'TOS_Import').

    Returns:
        A single indented audit line, or None if the trade didn't
        default or no vault lookup is available.
    """
    if raw.get("system") != default or vault_lookup is None:
        return None

    symbol = raw.get("underlying_symbol", "")
    open_date = str(raw.get("open_date", ""))
    hit = vault_lookup.nearest_any(symbol, open_date, VAULT_MATCH_FORWARD_DAYS)

    if hit is None:
        return "  -> P_400: no record (never evaluated, manual or auto)"
    if hit.lifecycle_status == "DROPPED":
        reason = hit.drop_reason or "no reason logged"
        return f"  -> P_400: DROPPED on {hit.signal_date} ({reason})"
    return (
        f"  -> P_400: record exists (status={hit.lifecycle_status}, "
        f"{hit.signal_date}), no usable attribution"
    )
