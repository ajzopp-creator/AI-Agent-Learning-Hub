"""config.py -- Constants and paths for the chaikin_enrichment package.

Generalizes P_300's Chaikin Power Gauge batch enrichment into a schema-driven
capability shared across any project writing BUY/WATCH notes to the vault.
Imports vault paths and folder routing from obsidian_writers.config rather
than duplicating them (WO-P800-E4.001).

CHANGELOG:
  v1.0  2026-07-24  Initial version. Built against WO-P800-E4.001.
"""

from obsidian_writers.config import VAULT_FOLDER_MAP, VAULT_ROOT

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
# notes. 1 covers the standard nightly run; raise only to catch up after a
# missed run.
LOOKBACK_DAYS: int = 1

# -- IDEMPOTENCY MARKER ---------------------------------------------------------
# Section header note_reader.py checks for before treating a note as a
# candidate. Must match exactly what run_chaikin_batch.py writes back.
CHAIKIN_SECTION_HEADER: str = "## Chaikin Power Gauge"

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
    "VAULT_FOLDER_MAP",
    "VAULT_ROOT",
]
