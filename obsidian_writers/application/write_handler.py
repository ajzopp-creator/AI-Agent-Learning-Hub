"""application/write_handler.py — Orchestrate validate → build → write pipeline.

Orchestration only — calls domain and infrastructure, no raw logic or I/O.

Two write paths, selected by OUTPUT_FORMAT (config.py):
  "md"   → frontmatter note via vault_writer. Injects run_date, run_ts,
           written_by, write_route; vault_writer handles note_version /
           write_route_history by reading the existing note on overwrite.
  "json" → raw signal packet via json_writer. No write_route normalization, no
           provenance, no frontmatter. Used by P400SIG (Enhancement 1).

CHANGELOG:
  v2.2  2026-07-10  Renamed the routing-only 'verdict' field to 'write_route'
                    everywhere it is produced (WO-P400-E2.020). Pure rename —
                    council_verdict (P_400's true disposition) and VERDICT_MAP's
                    mapping logic are unchanged. _inject_verdict renamed to
                    _inject_write_route.
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
      3. Map native classification to normalized write_route via VERDICT_MAP.
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
    _inject_write_route(schema_name, data)

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

    No write_route normalization, no run-timestamp injection, no provenance —
    a signal packet is an immutable handoff artifact validated against its
    locked schema and written verbatim.

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


def _inject_write_route(schema_name: str, data: dict[str, Any]) -> None:
    """Map the sending system's native classification to the normalized
    write_route field — routing-only, used to file the note into the right
    Obsidian folder. Not the true disposition (see council_verdict for P_400).

    Priority order:
      1. If 'write_route' already set and valid — leave it.
      2. Map from native field using VERDICT_MAP.
      3. Default to PASS if no mapping found.

    Native fields by schema:
      P115 → step1_verdict
      P300 → signal
      P400 → council_verdict
      P020 → outcome (TBD — left as null until P_020 is wired)
      KB   → no write_route (null)

    Args:
        schema_name: Schema identifier.
        data:        Data dict to mutate.
    """
    existing = data.get("write_route")
    if existing in ("BUY", "WATCH", "PASS"):
        return  # already normalized — nothing to do

    native_field_map = {
        "P115": "step1_verdict",
        "P300": "signal",
        "P400": "council_verdict",
        "P400_PAPER": "council_verdict",
        "P020": None,   # TBD
        "KB":   None,   # not applicable
    }
    native_field = native_field_map.get(schema_name)
    if not native_field:
        data["write_route"] = None
        return

    native_value = data.get(native_field)
    if native_value is None:
        data["write_route"] = None
        return

    mapped = VERDICT_MAP.get(native_value)
    if mapped is None:
        log.warning("No VERDICT_MAP entry for '%s' (schema=%s) — defaulting to PASS",
                    native_value, schema_name)
        mapped = "PASS"

    data["write_route"] = mapped
    log.debug("Write route mapped: %s.%s=%s → write_route=%s",
              schema_name, native_field, native_value, mapped)
