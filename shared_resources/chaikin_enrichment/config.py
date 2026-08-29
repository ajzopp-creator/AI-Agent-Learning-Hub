"""config.py -- Constants and paths for the chaikin_enrichment package.

Generalizes P_300's Chaikin Power Gauge batch enrichment into a schema-driven
capability shared across any project writing BUY/WATCH notes to the vault.
Imports vault paths and folder routing from obsidian_writers.config rather
than duplicating them (WO-P800-E4.001).

CHANGELOG:
  v1.0  2026-07-24  Initial version. Built against WO-P800-E4.001.
  v1.1  2026-08-12  Added SCHEMA_SKIP_LISTS -- P_300's chaikin_skip_list.csv
                    (WO-P300-E5.007, OTC/ETF symbols Chaikin structurally
                    can't rate) had no equivalent in this shared package.
                    Folding P_300's daily-eval script over to this scanner
                    without it would have silently reintroduced the exact
                    bug E5.007 fixed. Per-schema, empty default -- P_115
                    unaffected. Extends WO-P800-E4.001, not a new WO.
"""

from pathlib import Path

from obsidian_writers.config import HUB_ROOT, VAULT_FOLDER_MAP, VAULT_ROOT

# -- SCHEMAS ENABLED ----------------------------------------------------------
# Schemas eligible for Chaikin enrichment. Add a schema here only after its
# project has confirmed write_route frontmatter is live for its notes.
SCHEMAS_ENABLED: list[str] = ["P115", "P300"]

# -- WRITE_ROUTE VALUES THAT QUALIFY FOR ENRICHMENT --------------------------
# Matches P_300's existing threshold (BUY or WATCH). No per-project
# special-casing per the WO-P800-E4.001 assumption -- P_115's ASYM already
# normalizes to WATCH via obsidian_writers.config.VERDICT_MAP before it
# reaches this package.
CANDIDATE_WRITE_ROUTES: set[str] = {"BUY", "WATCH"}

# -- LOOKBACK WINDOW -----------------------------------------------------------
# Days back from today the vault_scanner globs when looking for candidate
# notes. Was 1 (2026-07-24) -- broken across any weekend: a Friday-anchored
# note (filename date = last trading day's close, not today) falls outside
# a 1-day window on a Saturday/Sunday/Monday run. Confirmed real 2026-08-23
# (Sunday): 7 real BUY/WATCH notes filed 2026-08-21_*.md, all silently
# missed -- "No BUY/WATCH candidates found" printed with 7 live candidates
# sitting in the folder. 3 is the minimum that covers Friday-anchor-on-Monday
# (the worst real gap in a standard trading week). Safe to raise: idempotency
# (ScannedNote.has_chaikin_section, candidate_filter.is_candidate) already
# excludes already-enriched notes regardless of window size -- a wider
# window only means scanning more files, not reprocessing them.
LOOKBACK_DAYS: int = 3

# -- IDEMPOTENCY MARKER ---------------------------------------------------------
# Section header note_reader.py checks for before treating a note as a
# candidate. Must match exactly what run_chaikin_batch.py writes back.
CHAIKIN_SECTION_HEADER: str = "## Chaikin Power Gauge"

# -- PER-SCHEMA SKIP LISTS ----------------------------------------------------
# Optional CSV per schema naming symbols that schema's own upstream work has
# confirmed Chaikin structurally cannot rate (ETFs, OTC mirrors of a non-US
# primary listing, etc. -- see each schema's own WO for the enumeration
# rationale; P_300's is WO-P300-E5.007). CSV must have a 'symbol' column and
# should have a 'reason' column (read_skip_list degrades gracefully without
# one). A schema absent from this dict, or whose file doesn't exist yet, gets
# no filtering -- read_skip_list returns an empty dict either way.
SCHEMA_SKIP_LISTS: dict[str, Path] = {
    "P300": (
        HUB_ROOT
        / "projects"
        / "P_300_Vantage_Point_Pattern_Recognition"
        / "data"
        / "reference"
        / "chaikin_skip_list.csv"
    ),
}

# -- RE-EXPORTED VAULT PATHS ----------------------------------------------------
# Re-exported (not re-defined) so every other chaikin_enrichment module
# imports from this config.py alone, never reaching into obsidian_writers
# directly. Keeps WO-P800-E3.003 (TradeManagement -> TradeOrderManagement
# rename), if it lands, to a one-file blast radius here.
__all__ = [
    "SCHEMAS_ENABLED",
    "CANDIDATE_WRITE_ROUTES",
    "LOOKBACK_DAYS",
    "CHAIKIN_SECTION_HEADER",
    "SCHEMA_SKIP_LISTS",
    "VAULT_FOLDER_MAP",
    "VAULT_ROOT",
]
