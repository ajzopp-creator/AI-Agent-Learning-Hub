"""application/write_handler.py — Orchestrate validate → build → write pipeline.

Orchestration only — calls domain and infrastructure, no raw logic or I/O.

Two write paths, selected by OUTPUT_FORMAT (config.py):
  "md"   → frontmatter note via vault_writer. Injects run_date, run_ts,
           written_by, verdict; vault_writer handles note_version /
           verdict_history by reading the existing note on overwrite.
  "json" → raw signal packet via json_writer. No verdict normalization, no
           provenance, no frontmatter. Used by P400SIG (Enhancement 1).

CHANGELOG:
  v2.1  2026-06-02  Branch on OUTPUT_FORMAT. Added _handle_json for the
                    P400SIG signal-packet path (validate → build path →
                    json_writer). md path unchanged. Enhancement 1.
  v2.0  2026-06-01  Inject run_date, run_ts into data before validate.
                    Apply VERDICT_MAP to normalize verdict field.
                    Pass data dict through to vault_writer for provenance tracking.
                    Stash body in data["_body"] for vault_writer rebuild on overwrite.
  v1.0  2026-05-22  Initial version.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from obsidian_writers.config import OUTPUT_FORMAT, VERDICT_MAP
from obsidian_writers.domain.filename_builder import build_filepath
from obsidian_writers.domain.frontmatter_builder import build_note
from obsidian_writers.domain.validator import validate
from obsidian_writers.infrastructure.json_writer import write_signal
from obsidian_writers.infrastructure.vault_writer import write_note
from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def handle_write(
    schema_name: str,
    data: dict[str, Any],
    body: str = "",
    overwrite: bool = True,
) -> bool:
    """Run the full pipeline for one record, dispatching by output format.

    This is the internal entry point called by vault_interface.write_to_vault().
    Sending projects never call this directly.

    Args:
        schema_name: One of P115 | P300 | P020 | P400 | P400SIG | KB.
        data:        Raw field dict from the sending project.
        body:        Optional note body text (md path only; ignored for json).
        overwrite:   If False, skip records that already exist in the vault.

    Returns:
        True if the record was written, False if skipped.

    Raises:
        ValueError: On unknown schema or validation failure.
        OSError:    On disk write failure.
    """
    log.debug("handle_write called: schema=%s", schema_name)

    fmt = OUTPUT_FORMAT.get(schema_name, "md")
    if fmt == "json":
        return _handle_json(schema_name, data, overwrite=overwrite)
    return _handle_md(schema_name, data, body=body, overwrite=overwrite)


def _handle_md(
    schema_name: str,
    data: dict[str, Any],
    body: str = "",
    overwrite: bool = True,
) -> bool:
    """Frontmatter-note path (md schemas).

    Steps:
      1. Inject run_date / run_ts (wall-clock time of this pipeline run).
      2. Inject source so vault_writer can reference it after rebuild.
      3. Map native classification to normalized verdict via VERDICT_MAP.
      4. Validate and normalize via Pydantic.
      5. Build file path.
      6. Build initial note content.
      7. Stash body + schema_name for vault_writer rebuild on overwrite.
      8. Write (vault_writer handles provenance).

    Args:
        schema_name: md schema identifier.
        data:        Raw field dict.
        body:        Optional note body.
        overwrite:   Skip existing notes if False.

    Returns:
        True if written, False if skipped.
    """
    now_utc = datetime.now(timezone.utc)
    data.setdefault("run_date", now_utc.strftime("%Y-%m-%d"))
    data.setdefault("run_ts", now_utc.strftime("%Y-%m-%dT%H:%M:%S"))

    data["source"] = schema_name
    _inject_verdict(schema_name, data)

    validated = validate(schema_name, data)
    file_path = build_filepath(schema_name, validated)
    content = build_note(schema_name, validated, body=body)

    validated["_body"] = body
    validated["_schema_name"] = schema_name

    written = write_note(file_path, content, data=validated, overwrite=overwrite)
    if written:
        log.info("OK schema=%s file=%s version=%s",
                 schema_name, file_path.name, validated.get("note_version", 1))
    return written


def _handle_json(
    schema_name: str,
    data: dict[str, Any],
    overwrite: bool = True,
) -> bool:
    """Raw signal-packet path (P400SIG).

    No verdict normalization, no run-timestamp injection, no provenance — a
    signal packet is an immutable handoff artifact validated against its locked
    schema and written verbatim.

    Steps:
      1. Validate against the packet model (P400SignalRecord).
      2. Build the JSON packet path.
      3. Write via json_writer.

    Args:
        schema_name: "P400SIG".
        data:        Raw packet dict (nested context / signal_metadata).
        overwrite:   Refuse to clobber an existing packet if False.

    Returns:
        True if written, False if skipped.
    """
    validated = validate(schema_name, data)
    file_path = build_filepath(schema_name, validated)
    written = write_signal(file_path, validated, overwrite=overwrite)
    if written:
        log.info("OK schema=%s packet=%s", schema_name, file_path.name)
    return written


def _inject_verdict(schema_name: str, data: dict[str, Any]) -> None:
    """Map the sending system's native classification to the normalized verdict.

    Priority order:
      1. If 'verdict' already set and valid — leave it.
      2. Map from native field using VERDICT_MAP.
      3. Default to PASS if no mapping found.

    Native fields by schema:
      P115 → step1_verdict
      P300 → signal
      P400 → council_verdict
      P020 → outcome (TBD — left as null until P_020 is wired)
      KB   → no verdict (null)

    Args:
        schema_name: Schema identifier.
        data:        Data dict to mutate.
    """
    existing = data.get("verdict")
    if existing in ("BUY", "WATCH", "PASS"):
        return  # already normalized — nothing to do

    native_field_map = {
        "P115": "step1_verdict",
        "P300": "signal",
        "P400": "council_verdict",
        "P020": None,   # TBD
        "KB":   None,   # not applicable
    }
    native_field = native_field_map.get(schema_name)
    if not native_field:
        data["verdict"] = None
        return

    native_value = data.get(native_field)
    if native_value is None:
        data["verdict"] = None
        return

    mapped = VERDICT_MAP.get(native_value)
    if mapped is None:
        log.warning("No VERDICT_MAP entry for '%s' (schema=%s) — defaulting to PASS",
                    native_value, schema_name)
        mapped = "PASS"

    data["verdict"] = mapped
    log.debug("Verdict mapped: %s.%s=%s → verdict=%s",
              schema_name, native_field, native_value, mapped)

import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from obsidian_writers.domain.schemas import SignalV2, AssetClass
from config import get_dual_emit_status, SIGNAL_FOLDER
from infrastructure.vault_writer import vault_writer
from logger_setup import logger

# ============================================================================
# v2.0 Signal Handlers — Dual-Emit & JSON Writers
# ============================================================================

def convert_v2_to_v1(signal: SignalV2) -> Dict[str, Any]:
    """Convert v2.0 signal to v1.0 format for dual-emit during compat window."""
    v1_signal = {
        "signal_id": signal.signal_id,
        "signal_timestamp": signal.signal_timestamp,
        "signal_source": signal.signal_source,
        "strategy": signal.strategy,
        "symbol": signal.symbol,
        "guideline_entry": signal.guideline_entry,
        "guideline_stop": signal.guideline_stop,
        "guideline_target": signal.guideline_target,
        "signal_horizon": signal.signal_horizon,
        "confidence_level": signal.confidence_level,
        "context": {
            "atm_at_signal": signal.context.atm_at_signal,
            "close_at_signal": signal.context.close_at_signal,
            "trailing_volume_30d": signal.context.trailing_volume_30d,
            "signal_rationale": signal.context.signal_rationale
        },
        "signal_metadata": {
            "p115_session_date": signal.signal_metadata.p115_session_date,
            "p115_chart_timeframe": signal.signal_metadata.p115_chart_timeframe,
            "signal_source_link": signal.signal_metadata.signal_source_link
        }
    }
    return v1_signal

def write_signal_v2(signal: SignalV2) -> str:
    """Write a v2.0 signal to vault with optional dual-emit."""
    v2_filename = f"{signal.signal_metadata.p115_session_date}_{signal.symbol}_v2.0.json"
    v2_path = f"{SIGNAL_FOLDER}/{v2_filename}"
    v2_data = signal.model_dump(exclude_none=True, mode="json")
    vault_writer.write_json(v2_path, v2_data)
    logger.info(f"Signal written (v2.0): {v2_filename} | source={signal.signal_source} | asset_class={signal.asset_class}")
    
    if get_dual_emit_status():
        v1_filename = f"{signal.signal_metadata.p115_session_date}_{signal.symbol}_signal.json"
        v1_path = f"{SIGNAL_FOLDER}/{v1_filename}"
        v1_data = convert_v2_to_v1(signal)
        vault_writer.write_json(v1_path, v1_data)
        logger.info(f"Signal written (v1.0 compat): {v1_filename} | dual-emit active")
    else:
        logger.info(f"Dual-emit disabled | cutover passed | v2.0 only")
    
    return v2_path

def write_signal(schema_name: str, data_dict: Dict[str, Any]) -> str:
    """Public API for writing signals."""
    if schema_name not in ["SIGNAL", "P400SIG"]:
        raise ValueError(f"schema_name must be ''SIGNAL'' or ''P400SIG'', got {schema_name}")
    
    try:
        signal = SignalV2(**data_dict)
    except Exception as e:
        logger.error(f"Signal validation failed: {e}")
        raise ValueError(f"Signal data validation failed: {e}")
    
    return write_signal_v2(signal)

def cleanup_v1_signals(vault_root: Path) -> int:
    """Remove all v1.0 signal files after cutover."""
    signals_dir = vault_root / SIGNAL_FOLDER
    if not signals_dir.exists():
        logger.warning(f"Signals directory not found: {signals_dir}")
        return 0
    
    v1_files = list(signals_dir.glob("*_signal.json"))
    count = 0
    
    for v1_file in v1_files:
        try:
            v1_file.unlink()
            logger.info(f"Deleted v1.0 signal: {v1_file.name}")
            count += 1
        except Exception as e:
            logger.error(f"Failed to delete {v1_file.name}: {e}")
    
    logger.info(f"Cleanup complete: {count} v1.0 signal files deleted")
    return count