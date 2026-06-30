"""infrastructure/vault_writer.py — Write .md note files to the Obsidian vault.

I/O only — no business logic.

On every overwrite, reads the existing frontmatter to extract the current
verdict and verdict_history, builds a new history entry, and passes the
updated list back through the data dict before writing. This ensures the
full verdict progression is preserved (Note Standard v1.1 Decision 6).

CHANGELOG:
  v2.0  2026-06-01  Added _read_existing_frontmatter() and _build_history_entry().
                    write_note() now reads prior verdict + history before overwrite
                    and increments note_version. Overwrite is always True by policy.
  v1.0  2026-05-22  Initial version.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from obsidian_writers.logger_setup import get_logger

log = get_logger(__name__)


def write_note(
    file_path: Path,
    content: str,
    data: dict[str, Any],
    overwrite: bool = True,
) -> bool:
    """Write a markdown note to the vault with provenance tracking.

    Before overwriting an existing note, reads the prior verdict and
    verdict_history from disk, appends a new history entry, and updates
    data in-place so frontmatter_builder emits the full history.

    Creates any missing parent directories automatically.

    Args:
        file_path: Absolute path to the target .md file.
        content:   Full note content including frontmatter (initial build).
        data:      Validated data dict — mutated in-place with updated
                   note_version and verdict_history before content is rebuilt.
        overwrite: If False, skip existing files without error (legacy param;
                   policy is always True per Note Standard v1.1 Decision 6).

    Returns:
        True if written, False if skipped.

    Raises:
        OSError: If the write fails due to permissions or disk error.
    """
    if file_path.exists() and not overwrite:
        log.info("Skipped (exists, overwrite=False): %s", file_path.name)
        return False

    if file_path.exists():
        _update_provenance(file_path, data)
        # content must be rebuilt by the caller after provenance update;
        # vault_writer signals the caller via the mutated data dict.
        # Re-import here avoids circular import at module level.
        from obsidian_writers.domain.frontmatter_builder import build_note
        schema_name = data.pop("_schema_name", data.get("source", "UNKNOWN"))
        body = data.pop("_body", "")
        content = build_note(schema_name, data, body=body)

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        log.info("Written: %s (version %s)", file_path.name, data.get("note_version", 1))
        return True
    except OSError as exc:
        log.error("Failed to write %s: %s", file_path, exc)
        raise


def note_exists(file_path: Path) -> bool:
    """Check whether a vault note already exists.

    Args:
        file_path: Absolute path to the .md file.

    Returns:
        True if the file exists on disk.
    """
    return file_path.exists()


def _update_provenance(file_path: Path, data: dict[str, Any]) -> None:
    """Read existing note, extract verdict + history, update data in-place.

    Reads the prior note_version, verdict, and verdict_history from disk.
    Appends the current verdict as a new history entry.
    Increments note_version by 1.
    Mutates data dict directly — caller rebuilds content after this call.

    Args:
        file_path: Path to the existing .md file.
        data:      Data dict to mutate with updated provenance fields.
    """
    existing = _read_existing_frontmatter(file_path)
    if not existing:
        return  # first write or unreadable — leave data as-is

    prior_verdict = existing.get("verdict", "PASS")
    prior_version = int(existing.get("note_version", 1))
    prior_history = existing.get("verdict_history", [])
    prior_run_date = existing.get("run_date", "")

    # Build new history entry from the note about to be replaced
    new_entry = _build_history_entry(prior_verdict, prior_run_date, prior_version)

    # Parse existing history if stored as string (YAML inline format from disk)
    parsed_history = _parse_history(prior_history)
    parsed_history.append(new_entry)

    data["note_version"] = prior_version + 1
    data["verdict_history"] = parsed_history
    log.debug(
        "Provenance updated: %s → version %s, history depth %s",
        file_path.name, data["note_version"], len(parsed_history)
    )


def _read_existing_frontmatter(file_path: Path) -> dict[str, Any]:
    """Parse key fields from the YAML frontmatter of an existing note.

    Reads only the fields needed for provenance tracking. Does not perform
    full YAML parsing — uses line-by-line extraction for reliability.

    Args:
        file_path: Path to the existing .md file.

    Returns:
        Dict with verdict, note_version, run_date, verdict_history keys.
        Returns empty dict if file cannot be read or has no frontmatter.
    """
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        log.warning("Could not read existing note: %s", file_path.name)
        return {}

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    result: dict[str, Any] = {}
    in_history = False
    history_entries: list[str] = []

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("verdict_history:"):
            val = line.split(":", 1)[1].strip()
            if val == "[]":
                result["verdict_history"] = []
            else:
                in_history = True
                history_entries = []
            continue
        if in_history:
            if line.startswith("  - "):
                history_entries.append(line.strip()[2:])  # strip "- "
            else:
                in_history = False
                result["verdict_history"] = history_entries
        stripped = line.strip()
        for key in ("verdict", "note_version", "run_date"):
            if stripped.startswith(f"{key}:"):
                result[key] = stripped.split(":", 1)[1].strip()

    if in_history:
        result["verdict_history"] = history_entries

    # Normalize note_version to int
    if "note_version" in result:
        try:
            result["note_version"] = int(result["note_version"])
        except (ValueError, TypeError):
            result["note_version"] = 1

    return result


def _build_history_entry(
    verdict: str, run_date: str, note_version: int
) -> dict[str, Any]:
    """Build a single verdict_history entry dict.

    Args:
        verdict:      The verdict value being replaced.
        run_date:     The run_date of the note being replaced.
        note_version: The note_version of the note being replaced.

    Returns:
        Dict with verdict, run_date, note_version keys.
    """
    return {"verdict": verdict, "run_date": run_date, "note_version": note_version}


def _parse_history(history: Any) -> list[dict[str, Any]]:
    """Normalize verdict_history to a list of dicts.

    Handles three cases:
      - Already a list of dicts (freshly built in memory).
      - List of inline YAML strings from disk read (e.g. '{verdict: BUY, ...}').
      - Empty list.

    Args:
        history: Raw verdict_history value from existing frontmatter.

    Returns:
        List of dicts with verdict, run_date, note_version keys.
    """
    if not history:
        return []
    result = []
    for entry in history:
        if isinstance(entry, dict):
            result.append(entry)
        elif isinstance(entry, str):
            # Parse inline YAML: {verdict: BUY, run_date: 2026-05-29, note_version: 1}
            import re
            parsed: dict[str, Any] = {}
            for match in re.finditer(r'(\w+):\s*([^,}]+)', entry):
                k, v = match.group(1).strip(), match.group(2).strip()
                parsed[k] = int(v) if k == "note_version" and v.isdigit() else v
            if parsed:
                result.append(parsed)
    return result