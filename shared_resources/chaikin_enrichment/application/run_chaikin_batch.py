"""run_chaikin_batch.py -- CLI orchestrator for schema-driven Chaikin enrichment.

application/ -- calls domain + infrastructure in sequence; no raw logic or
direct I/O beyond what orchestration requires. Built against WO-P800-E4.001.

Usage (invoked by RunChaikinBatch.ps1 -Schema P300):
    python run_chaikin_batch.py --schema P300

Exit codes:
    0  No candidates found -- nothing to run (matches the prior
       log-parsing script's "nothing to run" message).
    1  Candidates found -- prompt written to disk; PowerShell wrapper
       should call `claude -p` against it.

CHANGELOG:
  v1.0  2026-07-24  Initial version.
  v1.1  2026-08-12  Wired in read_skip_list() -- a schema's permanent
                    skip list (P_300's WO-P300-E5.007) now excludes
                    symbols before they reach the prompt, and skipped-
                    but-otherwise-qualifying symbols print a [SKIP] line
                    with the reason, matching the visibility the prior
                    P_300-local PowerShell version gave Tony.
"""

import argparse
import sys
from pathlib import Path

from shared_resources.chaikin_enrichment.config import SCHEMAS_ENABLED
from shared_resources.chaikin_enrichment.domain.candidate_filter import (
    NoteCandidate,
    filter_candidates,
)
from shared_resources.chaikin_enrichment.infrastructure.skip_list_reader import (
    read_skip_list,
)
from shared_resources.chaikin_enrichment.infrastructure.vault_scanner import scan_schema

_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "chaikin_prompt_template.txt"
_PROMPT_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "_last_prompt.txt"


def build_prompt(
    candidates: list[NoteCandidate], template_path: Path = _TEMPLATE_PATH
) -> str:
    """Renders the Chaikin prompt from a resolved candidate list.

    Args:
        candidates: NoteCandidate list from the domain filter -- each one
            already resolved to an exact note path, no date-guessing.
        template_path: Path to chaikin_prompt_template.txt.

    Returns:
        Rendered prompt text, {NOTE_TABLE} replaced with one
        "SYMBOL -> path" line per candidate.
    """
    template = template_path.read_text(encoding="utf-8")
    table = "\n".join(f"{c.symbol} -> {c.note_path}" for c in candidates)
    return template.replace("{NOTE_TABLE}", table)


def run(schema_name: str) -> int:
    """Runs the scan -> filter -> prompt-build pipeline for one schema.

    Args:
        schema_name: A key in SCHEMAS_ENABLED (e.g. "P115", "P300").

    Returns:
        Candidate count found (0 = nothing to run).

    Raises:
        ValueError: If schema_name is not in SCHEMAS_ENABLED.
    """
    if schema_name not in SCHEMAS_ENABLED:
        raise ValueError(
            f"Schema '{schema_name}' is not enabled for Chaikin enrichment "
            f"(SCHEMAS_ENABLED={SCHEMAS_ENABLED})"
        )

    scanned = scan_schema(schema_name)
    skip_map = read_skip_list(schema_name)
    skip_symbols = frozenset(skip_map)

    candidates = filter_candidates(scanned, skip_symbols)

    # Report skips for visibility -- only symbols that would otherwise have
    # qualified (matches the prior P_300-local script's behavior of only
    # printing [SKIP] for real BUY/WATCH candidates, not the whole list).
    # Reuses filter_candidates itself (once with, once without the skip set)
    # rather than re-deriving qualification logic here (M-082).
    if skip_symbols:
        unfiltered = {c.symbol for c in filter_candidates(scanned)}
        filtered = {c.symbol for c in candidates}
        for symbol in sorted(unfiltered - filtered):
            reason = skip_map.get(symbol, "")
            print(f"[SKIP] {symbol} -- {reason}")

    if not candidates:
        print(f"No BUY/WATCH candidates found for {schema_name} -- nothing to run.")
        return 0

    prompt = build_prompt(candidates)
    _PROMPT_OUTPUT_PATH.write_text(prompt, encoding="utf-8")

    symbol_list = ", ".join(c.symbol for c in candidates)
    print(f"Chaikin batch for: {symbol_list}")
    print(f"Prompt written to: {_PROMPT_OUTPUT_PATH}")
    return len(candidates)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run schema-driven Chaikin enrichment scan."
    )
    parser.add_argument("--schema", required=True, help="Schema name, e.g. P115 or P300")
    args = parser.parse_args()

    count = run(args.schema)
    sys.exit(0 if count == 0 else 1)


if __name__ == "__main__":
    main()
