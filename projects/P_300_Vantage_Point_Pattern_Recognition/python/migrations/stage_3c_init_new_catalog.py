"""
FILE: stage_3c_init_new_catalog.py
VERSION: 1.0
DATE: 2026-05-14
AUTHOR: Anthony Zoppi + Claude
LAYER: migration
DESCRIPTION: One-shot Stage 3c migration. Creates an empty SQLite catalog
    at models/<mmddyy>catalog.db with the canonical 7-table schema
    (symbols, source_files, feature_sets, pattern_instances, pattern_bars,
    pattern_features, forward_labels) and 4 indexes per architecture §9.2.
    Inserts one bootstrap row in feature_sets (feature_version='baseline_v1').
    Refuses to overwrite an existing catalog unless --force is passed.
    Idempotent under --force; otherwise fails loudly if the target exists.
CHANGELOG:
    - 2026-05-14 v1.0: Initial empty-schema catalog creator. Target file:
      051426catalog.db. 7 tables (not 8 — the "8-table" claim in earlier
      planning docs is stale and will be patched).
"""

from __future__ import annotations

import argparse
import datetime as dt
import logging
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("stage_3c")

# Script lives at <project>/python/migrations/stage_3c_init_new_catalog.py
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Catalog filename — mmddyy stamp locked at script-creation date.
# Subsequent rebuilds get their own dated file; db_utils.get_latest_catalog()
# picks newest-by-name at runtime.
CATALOG_DATE_STAMP = "051426"
CATALOG_PATH = PROJECT_ROOT / "models" / f"{CATALOG_DATE_STAMP}catalog.db"

# ---------------------------------------------------------------------------
# Canonical schema — verbatim from architecture v2.1 §9.2
# ---------------------------------------------------------------------------

SCHEMA_DDL = """
-- Identity & provenance
CREATE TABLE symbols (
    symbol_id   INTEGER PRIMARY KEY,
    ticker      TEXT UNIQUE NOT NULL
);

CREATE TABLE source_files (
    source_file_id INTEGER PRIMARY KEY,
    filename       TEXT UNIQUE NOT NULL,
    symbol_id      INTEGER NOT NULL,
    imported_at    TEXT NOT NULL,
    row_count      INTEGER NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id)
);

CREATE TABLE feature_sets (
    feature_set_id  INTEGER PRIMARY KEY,
    feature_version TEXT NOT NULL,
    description     TEXT,
    created_at      TEXT NOT NULL
);

-- Pattern core
CREATE TABLE pattern_instances (
    pattern_instance_id INTEGER PRIMARY KEY,
    symbol_id           INTEGER NOT NULL,
    source_file_id      INTEGER NOT NULL,
    feature_set_id      INTEGER NOT NULL,
    anchor_date         TEXT NOT NULL,
    window_length       INTEGER NOT NULL,
    data_origin_type    TEXT NOT NULL,
    FOREIGN KEY (symbol_id)       REFERENCES symbols(symbol_id),
    FOREIGN KEY (source_file_id)  REFERENCES source_files(source_file_id),
    FOREIGN KEY (feature_set_id)  REFERENCES feature_sets(feature_set_id)
);

-- Normalized window
CREATE TABLE pattern_bars (
    pattern_bar_id      INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    bar_offset          INTEGER NOT NULL,
    bar_date            TEXT NOT NULL,
    -- Raw VP data (audit trail)
    open REAL, high REAL, low REAL, close REAL,
    volume REAL,
    stdiff REAL, mtdiff REAL, ltdiff REAL,
    pred_high REAL, pred_low REAL, pred_range REAL,
    williams_emai REAL, psi REAL, neural_index REAL,
    triple_cross_short REAL, triple_cross_medium REAL, triple_cross_long REAL,
    -- Normalization layer (computed at ingest, used for matching)
    close_pct_from_anchor REAL,
    range_pct REAL,
    body_pct REAL,
    volume_zscore REAL,
    stdiff_pct REAL, mtdiff_pct REAL, ltdiff_pct REAL,
    pred_high_pct REAL, pred_low_pct REAL, pred_range_pct REAL,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id),
    UNIQUE (pattern_instance_id, bar_offset)
);

-- Derived features (computed, not raw VP data)
CREATE TABLE pattern_features (
    pattern_feature_id  INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    feature_name        TEXT NOT NULL,
    feature_value       REAL,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id)
);

-- Outcomes
CREATE TABLE forward_labels (
    forward_label_id    INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    horizon_days        INTEGER NOT NULL,
    future_date         TEXT,
    return_pct          REAL,
    is_profitable       INTEGER,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id)
);

-- Indexes
CREATE INDEX idx_pattern_instances_symbol_anchor
    ON pattern_instances(symbol_id, anchor_date);
CREATE INDEX idx_pattern_bars_pattern_offset
    ON pattern_bars(pattern_instance_id, bar_offset);
CREATE INDEX idx_forward_labels_pattern_horizon
    ON forward_labels(pattern_instance_id, horizon_days);
CREATE INDEX idx_pattern_instances_origin
    ON pattern_instances(data_origin_type);
"""

EXPECTED_TABLES = (
    "symbols",
    "source_files",
    "feature_sets",
    "pattern_instances",
    "pattern_bars",
    "pattern_features",
    "forward_labels",
)

EXPECTED_INDEXES = (
    "idx_pattern_instances_symbol_anchor",
    "idx_pattern_bars_pattern_offset",
    "idx_forward_labels_pattern_horizon",
    "idx_pattern_instances_origin",
)

BOOTSTRAP_FEATURE_VERSION = "baseline_v1"
BOOTSTRAP_DESCRIPTION = (
    "Initial baseline feature set. Variable pattern window 5-20 bars. "
    "Normalized columns pre-computed on pattern_bars. "
    "Forward horizons 5/7/10/15/20 days."
)


def utc_now_iso() -> str:
    """ISO-8601 UTC timestamp with seconds precision and Z suffix."""
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_catalog(force: bool) -> None:
    """Create the catalog file with the canonical schema and bootstrap row."""
    if CATALOG_PATH.exists():
        if not force:
            log.error("Catalog already exists: %s", CATALOG_PATH)
            log.error("Use --force to delete and recreate, or remove the file manually.")
            sys.exit(1)
        CATALOG_PATH.unlink()
        log.warning("DELETED existing catalog (--force): %s", CATALOG_PATH)

    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(CATALOG_PATH))
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SCHEMA_DDL)
        conn.execute(
            "INSERT INTO feature_sets (feature_version, description, created_at) "
            "VALUES (?, ?, ?);",
            (BOOTSTRAP_FEATURE_VERSION, BOOTSTRAP_DESCRIPTION, utc_now_iso()),
        )
        conn.commit()
    finally:
        conn.close()

    log.info("CREATED  %s", CATALOG_PATH)


def verify_catalog() -> bool:
    """Introspect the catalog and confirm all expected tables, indexes,
    and the bootstrap feature_set row are present. Returns True on success."""
    conn = sqlite3.connect(str(CATALOG_PATH))
    try:
        cur = conn.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        actual_tables = tuple(row[0] for row in cur.fetchall())
        for table in EXPECTED_TABLES:
            present = table in actual_tables
            log.info("TABLE    %-20s %s", table, "OK" if present else "MISSING")
            if not present:
                return False

        cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        actual_indexes = tuple(row[0] for row in cur.fetchall())
        for index in EXPECTED_INDEXES:
            present = index in actual_indexes
            log.info("INDEX    %-40s %s", index, "OK" if present else "MISSING")
            if not present:
                return False

        cur.execute("SELECT feature_version, description FROM feature_sets;")
        rows = cur.fetchall()
        if len(rows) != 1 or rows[0][0] != BOOTSTRAP_FEATURE_VERSION:
            log.error("BOOTSTRAP feature_set row missing or wrong: %s", rows)
            return False
        log.info("BOOTSTRAP feature_sets row: %s", rows[0][0])

        cur.execute("PRAGMA foreign_keys;")
        fk_enabled = cur.fetchone()[0]
        log.info("PRAGMA   foreign_keys = %s", fk_enabled)
    finally:
        conn.close()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 3c — initialize empty catalog.")
    parser.add_argument("--force", action="store_true",
                        help="Delete and recreate if catalog file already exists.")
    args = parser.parse_args()

    log.info("Stage 3c init new catalog")
    log.info("Project root: %s", PROJECT_ROOT)
    log.info("Target:       %s", CATALOG_PATH)

    log.info("--- Create ---")
    create_catalog(force=args.force)

    log.info("--- Verify ---")
    if verify_catalog():
        log.info("Stage 3c complete.")
    else:
        log.error("Stage 3c verification FAILED.")
        sys.exit(2)


if __name__ == "__main__":
    main()
