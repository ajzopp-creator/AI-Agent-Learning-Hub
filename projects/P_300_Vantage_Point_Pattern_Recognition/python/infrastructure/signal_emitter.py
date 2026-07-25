"""
FILE: signal_emitter.py
VERSION: 2.3
DATE: 2026-07-04
AUTHOR: Anthony Zoppi + Claude
LAYER: infrastructure
DESCRIPTION:
    Emits a P_300 -> P_400 signal packet for an actionable (BUY/WATCH)
    evaluation. Hands a SIGNAL_V2 dict to the P_800 Hub interface
    (write_to_vault); P_800 validates, names the file, and writes it to
    trading_journal/TradeOrderManagement/signals/<date>_<SYMBOL>_v2.0.json.

    P_300 has ZERO knowledge of the vault location -- correctly, because
    P_800 owns the path. This module NEVER constructs a file path and NEVER
    writes to disk directly (M-038; Consumer Guide v1.2 rules 1 and 2).

    SIGNAL_V2 contract (P_800 Vault Interface Consumer Guide v1.2):
        - Unified stock/option schema; asset_class discriminates.
        - P_300 is a stock signal source: asset_class="stock"; the
          options-only fields (strike/underlying/option_type/expiration)
          are omitted and default null (validate clean).
        - position_size=0 sentinel: P_300 does NOT size positions. P_400
          owns sizing via its three-gate logic. Boundary stays clean --
          no coupling to P_000 account params. (WO-P800-E2; sentinel
          validated 2026-06-08: position_size=0 passes P_800 validation.)

    Best-effort, non-blocking: a rejected or failed write returns
    (False, msg) and is logged at WARNING (M-043) so the operator sees it;
    the signal still fires. A successful write logs at INFO (M-042). The
    vault_interface import is deferred into the call so P_800 import health
    never blocks Pipeline B startup.

CHANGELOG:
    - 2026-07-04 v2.3: WO-P300-E1.004. Added print() status lines
      ([OK]/[REJECTED]) alongside the existing logger.info/logger.warning
      calls. --clean's logging.disable(logging.WARNING) in
      daily_evaluate_pipeline.py main() spans the whole run, silently
      swallowing both success and failure logs from this function with no
      fallback -- same failure shape as the Obsidian writer's M-043 bug.
      Caught 2026-07-04: a real --clean batch produced 10 vault notes but
      only 3 signals/ packets with zero trace of what happened to the
      other 7 (PEH diagnostic later confirmed the emitter itself was fine
      -- write_to_vault succeeded on replay -- the only bug was visibility).
    - 2026-06-17 v2.2: Target generation now follows architecture 3.5
      (Target Selection Standard) -- WO-P300-E1.002. guideline_target was
      unconditionally entry + 2x ATR, ignoring any VP resistance level
      already present in the packet (caught via AG dossier 2026-06-17,
      where intelliscan_support_2=21.27 sat unused above entry=19.42).
      Now checks intelliscan_support_1/_support_2 for any level above
      close_at_signal; uses the nearer one as guideline_target
      (target_source="vp_resistance") when one exists, falling back to
      the existing 2x ATR extension (target_source="atr_extension") only
      for true price-discovery setups with no resistance above entry.
      target_source added to the packet for audit trail -- requires
      signal_schemas.py v2.2 (shared_resources) or the field is silently
      dropped at the P_800 vault-write validation step.
    - 2026-06-16 v2.1: Added atr_adjusted_stop, intelliscan_support_1,
      intelliscan_support_2 params (WO-P300-E1.001). All optional; passed
      through to the SIGNAL_V2 packet. P_400 uses atr_adjusted_stop as its
      primary Quant-gate stop input; falls back to guideline_stop when absent.
    - 2026-06-08 v2.0: Rerouted through the P_800 Hub interface
      (write_to_vault SIGNAL_V2). Removed schemas_signal_packet import,
      the output_filepath param, path construction, and the direct file
      open. Added chosen_horizon param (drives signal_horizon). Stock
      variant: asset_class="stock" + position_size=0 sentinel. Emits
      SIGNAL_V2 only (P_300 is a new producer; legacy P400SIG dual-emit
      not required). vault_interface import deferred into emit (lazy).
    - 2026-06-07 v1.1: Removed vault_root; took output_filepath (superseded).
    - 2026-06-07 v1.0: Initial. Local v1.0 SignalPacket written to disk.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# P_800 schema key for the unified JSON signal packet (Consumer Guide v1.2).
_SIGNAL_V2_KEY = "SIGNAL_V2"


def _confidence_level(wr: float) -> str:
    """Map win-rate (0-100) to the SIGNAL_V2 confidence enum."""
    if wr >= 70.0:
        return "HIGH"
    if wr >= 60.0:
        return "MEDIUM"
    return "LOW"


def _build_signal_v2_packet(
    symbol: str,
    signal_date: str,
    chosen_horizon: int,
    n_matches: int,
    wr: float,
    mean_ret: float,
    z_score: float,
    close_at_signal: float,
    atm_at_signal: float,
    trailing_volume_30d: float,
    signal_source_link: str,
    atr_adjusted_stop: float | None = None,
    intelliscan_support_1: float | None = None,
    intelliscan_support_2: float | None = None,
) -> dict:
    """Assemble a SIGNAL_V2 packet dict (stock variant). Pure -- no I/O."""
    signal_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rationale = (
        f"Pattern analog: {n_matches} matches @ {wr:.1f}% WR, "
        f"z={z_score:.2f}, mean return {mean_ret:+.2f}% at h={chosen_horizon}"
    )
    # Target selection per architecture 3.5 (Target Selection Standard,
    # WO-P300-E1.002). VP-derived resistance first: of whichever IntelliScan
    # level(s) sit above entry, take the nearer one as the target -- that's
    # the real structural ceiling. Field labels (support_1/support_2) aren't
    # reliably tied to above/below price, so both are checked rather than
    # assuming support_2 is always the one above entry. 2x ATR extension is
    # the Confluence-Based Target Framework fallback, reserved for true
    # price-discovery setups where neither level clears entry.
    _resistance_candidates = [
        lvl for lvl in (intelliscan_support_1, intelliscan_support_2)
        if lvl is not None and lvl > close_at_signal
    ]
    if _resistance_candidates:
        guideline_target = min(_resistance_candidates)
        target_source = "vp_resistance"
    else:
        guideline_target = close_at_signal + (2.0 * atm_at_signal)
        target_source = "atr_extension"
    return {
        "signal_id": f"P300-{signal_date}-{symbol}-001",
        "signal_timestamp": signal_timestamp,
        "signal_source": "P_300",
        "strategy": "pattern_analog",
        "symbol": symbol,
        "asset_class": "stock",
        "guideline_entry": close_at_signal,
        "guideline_stop": close_at_signal - atm_at_signal,
        "guideline_target": guideline_target,
        "target_source": target_source,
        "atr_adjusted_stop": atr_adjusted_stop,
        "intelliscan_support_1": intelliscan_support_1,
        "intelliscan_support_2": intelliscan_support_2,
        "signal_horizon": f"{chosen_horizon} trading days",
        "confidence_level": _confidence_level(wr),
        "position_size": 0,  # sentinel -- P_400 sizes via three gates
        "context": {
            "close_at_signal": close_at_signal,
            "trailing_volume_30d": trailing_volume_30d,
            "signal_rationale": rationale,
            "atm_at_signal": atm_at_signal,
        },
        "signal_metadata": {
            "session_date": signal_date,
            "chart_timeframe": "1D",
            "signal_source_link": signal_source_link,
        },
    }


def emit_signal_packet(
    symbol: str,
    signal_date: str,
    chosen_horizon: int,
    n_matches: int,
    wr: float,
    mean_ret: float,
    z_score: float,
    close_at_signal: float,
    atm_at_signal: float,
    trailing_volume_30d: float,
    signal_source_link: str,
    atr_adjusted_stop: float | None = None,
    intelliscan_support_1: float | None = None,
    intelliscan_support_2: float | None = None,
) -> tuple[bool, str]:
    """Build a SIGNAL_V2 packet and write it via the P_800 Hub interface.

    Args:
        symbol:                Uppercase ticker.
        signal_date:           Anchor date, ISO YYYY-MM-DD. Drives signal_id.
        chosen_horizon:        Classified horizon in trading days.
        n_matches:             Top-K analog count behind the signal.
        wr:                    Win rate as a percentage (0-100).
        mean_ret:              Mean return in percent (e.g. 4.81 for +4.81%).
        z_score:               Cluster z-score vs catalog baseline.
        close_at_signal:       Live close at eval; used as guideline entry.
        atm_at_signal:         ATR(14) Wilder; candidate/baseline stop/target -- P_400 resolves final.
        trailing_volume_30d:   Avg daily volume (audit context).
        signal_source_link:    Vault-relative path to the P_300 .md note.
        atr_adjusted_stop:     max(intelliscan_support_1, entry - 1x ATR).
                               P_400 primary Quant-gate stop input. None when
                               IntelliScan grid absent at eval time.
        intelliscan_support_1: Nearer VP structural support level. None when absent.
        intelliscan_support_2: Wider VP structural support level. None when absent.
                               P_400 may use this if support_1 exceeds risk params.

    Returns:
        (True, msg) on a successful vault write; (False, msg) on rejection
        or write failure. Never raises -- failures are non-blocking so the
        signal still fires (logged at WARNING for operator visibility).
    """
    try:
        # Lazy import: keeps P_800 import health out of Pipeline B startup.
        from shared_resources.python_utils.vault_interface import write_to_vault

        packet = _build_signal_v2_packet(
            symbol=symbol,
            signal_date=signal_date,
            chosen_horizon=chosen_horizon,
            n_matches=n_matches,
            wr=wr,
            mean_ret=mean_ret,
            z_score=z_score,
            close_at_signal=close_at_signal,
            atm_at_signal=atm_at_signal,
            trailing_volume_30d=trailing_volume_30d,
            signal_source_link=signal_source_link,
            atr_adjusted_stop=atr_adjusted_stop,
            intelliscan_support_1=intelliscan_support_1,
            intelliscan_support_2=intelliscan_support_2,
        )
        write_to_vault(_SIGNAL_V2_KEY, packet)
        msg = (
            f"SIGNAL_V2 packet emitted for {symbol} "
            f"({signal_date}, h={chosen_horizon}) -> P_400 signals/"
        )
        logger.info(msg)
        # M-043-pattern fix (WO-P300-E1.004): print(), not just logger.info,
        # so this survives --clean's logging.disable(logging.WARNING) for
        # the whole run. logger.info alone was silently swallowed under
        # --clean with no fallback -- identical failure shape to the
        # Obsidian writer bug M-043 already fixed elsewhere.
        print(f"[OK] {symbol}: SIGNAL_V2 emitted -> P_400 signals/")
        return True, msg

    except Exception as e:  # ValueError (reject) | OSError (disk) | import | other
        msg = (
            f"SIGNAL_V2 emit FAILED for {symbol} {signal_date}: "
            f"{type(e).__name__}: {e}"
        )
        logger.warning(msg)
        print(f"[REJECTED] {symbol}: {type(e).__name__}: {e}")
        return False, msg
