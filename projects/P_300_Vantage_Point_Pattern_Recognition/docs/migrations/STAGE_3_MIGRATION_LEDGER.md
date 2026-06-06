# Stage 3 Migration Ledger

**File:** `docs/migrations/STAGE_3_MIGRATION_LEDGER.md`
**Stage:** 3 — File System Cleanup + Empty New Schema
**Executed:** 2026-05-13 through 2026-05-14
**Status:** SEALED 2026-05-14
**Maintained By:** Anthony Zoppi + Claude
**Pairs With:** `tasks/todo.md` §3, architecture v2.1 §7 Stage 3 enhancements, `tasks/lessons.md` M-007 through M-012

---

## Purpose

Forensic record of every file moved, created, edited, or deleted during the Stage 3 rebuild migration. Enables future debugging ("where did `intelliscan.py` go?") and verifies cleanup completeness. Every section lists exact source → destination paths so the original location of any archived artifact is recoverable.

---

## Stage Summary

| Step | Mechanism | Action | Result |
| :---- | :---- | :---- | :---- |
| 3.1 | Manual write | Foundation files | `python/config.py` v1.0 + `python/schemas.py` v1.0 |
| 3a | `stage_3a_folder_setup.py` v1.1 | Created Hub-standard layer packages + plain dirs | 5 packages, 3 plain dirs |
| 3b | `stage_3b_archive_cruft.py` v1.0 | Archived all legacy artifacts | 10 dir moves + 29 file moves + 47 utility-sweep + 2 cache-delete (88 ops) |
| 3c | `stage_3c_init_new_catalog.py` v1.0 | Created empty 7-table catalog | `models/051426catalog.db` |
| 3.3 | Manual edit | db_utils.py glob update | `db_utils.py` v1.14 → v1.15 |
| 3.3+ (bonus) | Manual edit + new file | `db_utils.py` refactor; `db_connect.py` v1.0 created | M-012 enforcement point established |
| 3.4 | Manual write | This ledger | `STAGE_3_MIGRATION_LEDGER.md` |

---

## Stage 3a — Folder Setup

Script: `python/migrations/stage_3a_folder_setup.py` v1.1
Run date: 2026-05-13

### Python packages created (with `__init__.py` markers)

| Path | Status before | Status after |
| :---- | :---- | :---- |
| `python/domain/` | absent | created |
| `python/infrastructure/` | absent | created |
| `python/application/` | absent | created |
| `python/migrations/` | absent (pre-created by setup PowerShell before script run) | `__init__.py` added |
| `python/utilities/` | pre-existed | `__init__.py` added |

### Plain dirs (with `.gitkeep` markers)

| Path | Status before | Status after |
| :---- | :---- | :---- |
| `tests/` (project root) | pre-existed | `.gitkeep` added |
| `data/archive/` | pre-existed | `.gitkeep` added |
| `models/archive/` | pre-existed | `.gitkeep` added |

---

## Stage 3b — Archive Manifest

Script: `python/migrations/stage_3b_archive_cruft.py` v1.0
Run date: 2026-05-14
Dry-run preview executed first; commit run executed after operator approval.
All operations idempotent under re-execution.

### Whole-directory moves (10)

| Source | Destination |
| :---- | :---- |
| `python/ingest/` | `python/archive/legacy_layers/ingest/` |
| `python/labeling/` | `python/archive/legacy_layers/labeling/` |
| `python/feature_engineering/` | `python/archive/legacy_layers/feature_engineering/` |
| `python/parsers/` | `python/archive/legacy_layers/parsers/` |
| `python/input/` | `python/archive/legacy_layers/input/` |
| `python/output/` | `python/archive/legacy_layers/output/` |
| `python/matching/` | `python/archive/legacy_layers/matching/` |
| `python/reporting/` | `python/archive/legacy_layers/reporting/` |
| `python/tests/` | `python/archive/legacy_tests/` |
| `models/schema/` | `models/archive/schema/` |

### Python root legacy file moves (11)

| Source | Destination | Reason |
| :---- | :---- | :---- |
| `python/old_P_300_vantagepoint_batch_convert_v6.py` | `python/archive/legacy_root/...` | Converter v6 pre-rebuild (EC-060) |
| `python/P_300_Intraday_VPCheck_v2.6.py` | `python/archive/legacy_root/...` | Posture script moved to P_010 |
| `python/P_300_Posture_V2.4.py` | `python/archive/legacy_root/...` | Posture script superseded by P_010 |
| `python/P_300_Posture_V2.5.py` | `python/archive/legacy_root/...` | Posture script superseded by P_010 |
| `python/P_300_Posture_v2.6.py` | `python/archive/legacy_root/...` | Posture script superseded by P_010 |
| `python/P_300_vantagepoint_batch_convert_v1.py` | `python/archive/legacy_root/...` | Converter v1 (legacy version) |
| `python/P_300_vantagepoint_batch_convert_v2.py` | `python/archive/legacy_root/...` | Converter v2 (legacy version) |
| `python/P_300_vantagepoint_batch_convert_v3.py` | `python/archive/legacy_root/...` | Converter v3 (legacy version) |
| `python/P_300_vantagepoint_batch_convert_v4.py` | `python/archive/legacy_root/...` | Converter v4 (legacy version) |
| `python/P_300_vantagepoint_batch_convert_v5.py` | `python/archive/legacy_root/...` | Converter v5 (legacy version) |
| `python/risk_config.json` | `python/archive/legacy_root/...` | Legacy duplicate, superseded by P_010 |

### models/ database file moves (7)

| Source | Destination |
| :---- | :---- |
| `models/051026geminicatalog.db` | `models/archive/databases/051026geminicatalog.db` |
| `models/051126geminicatalog.db` | `models/archive/databases/051126geminicatalog.db` |
| `models/anothercorrupted_051126geminicatalog.db` | `models/archive/databases/anothercorrupted_051126geminicatalog.db` |
| `models/corrupted_051126geminicatalog.db` | `models/archive/databases/corrupted_051126geminicatalog.db` |
| `models/empty_ catalog.db` | `models/archive/databases/empty_ catalog.db` (Perplexity 7-table schema; archival only per O-004) |
| `models/pre_051126geminicatalog - Copy.db` | `models/archive/databases/pre_051126geminicatalog - Copy.db` |
| `models/Archivegeminicatalog.zip` | `models/archive/databases/Archivegeminicatalog.zip` |

### models/ loose .py moves (10)

| Source | Destination |
| :---- | :---- |
| `models/check_rows.py` | `models/archive/loose/check_rows.py` |
| `models/debug_db.py` | `models/archive/loose/debug_db.py` |
| `models/hydrate.py` | `models/archive/loose/hydrate.py` |
| `models/intelliscan.py` | `models/archive/loose/intelliscan.py` |
| `models/pattern_instance.py` | `models/archive/loose/pattern_instance.py` |
| `models/performance_dashboard.py` | `models/archive/loose/performance_dashboard.py` |
| `models/sanitize_db.py` | `models/archive/loose/sanitize_db.py` |
| `models/seed_data.py` | `models/archive/loose/seed_data.py` |
| `models/sync_catalog.py` | `models/archive/loose/sync_catalog.py` |
| `models/validate_catalog.py` | `models/archive/loose/validate_catalog.py` |

### Project root legacy (1)

| Source | Destination |
| :---- | :---- |
| `risk_config.json` (project root) | `data/archive/legacy_root/risk_config.json` |

### python/utilities/ sweep — KEEP list

These four entries were preserved in `python/utilities/`:
- `db_utils.py` (current catalog-path resolver; refactored v1.16 — see Stage 3.3+ Bonus)
- `__init__.py` (package marker, added by Stage 3a)
- `.vscode/` (VS Code launch config)
- `__pycache__/` (handled separately by cache cleanup)

### python/utilities/ sweep — moved to `python/archive/legacy_utilities/` (47)

`audit_missing_labels.py`, `catalog_summary.py`, `check_catalog.py`, `clean_database_dates.py`, `db_cleanup.py`, `delete_ghost.py`, `diagnostic_intelliscan.py`, `dump_catalog_fast.py`, `ingest_data.py`, `init_catalog.py`, `inspect_catalog.py`, `inspect_labels.py`, `inspect_schema.py`, `list_tables.py`, `migrate_schema.py`, `migrate_schema_py.py`, `p300_bridge.py`, `P_300_00_AddPatternLauncher.ps1`, `P_300_00_ingest.ps1`, `P_300_00_WorkflowLauncher_old.ps1`, `P_300_05_ingest.ps1`, `P_300_06_LabelMath.ps1`, `P_300_10_ArchiveCSV.ps1`, `P_300_20_PatternMatch.ps1`, `P_300_50_ConReport.ps1`, `P_300_AddPattern.bat`, `P_300_Audit_Symbols.py`, `P_300_DailyWorkflow.bat`, `P_300_EvaluateTrade.py`, `P_300_EvaluateTrade.v0.py`, `P_300_EvaluateTradev14.py`, `P_300_EvaluateTradev2.py`, `P_300_EvaluateTradev3.py`, `P_300_Final_Validator.py`, `P_300_vantagepoint_batch_convert_v6.py`, `parameter_sweep.py`, `patch_database.py`, `performance_dashboard.py`, `price_bar_columns.py`, `purge_zombies.py`, `repair_orphans.py`, `resolve_catalog.ps1`, `sample_pattern.py`, `truthcheck_Audit.py`, `undo_eval.py`, `vantage_point_health.log`, `verify_ingestion.py`.

### Cache deletions (2)

Stale `__pycache__/` directories deleted because they held `.pyc` files referencing moved scripts. Python regenerates as needed on next import.

| Path | Action |
| :---- | :---- |
| `python/__pycache__/` | Deleted |
| `python/utilities/__pycache__/` | Deleted |

---

## Stage 3c — New Catalog

Script: `python/migrations/stage_3c_init_new_catalog.py` v1.0
Run date: 2026-05-14
Target: `models/051426catalog.db` (mmddyy = 05/14/26)

### Schema created (7 tables, 4 indexes)

| Table | Purpose |
| :---- | :---- |
| `symbols` | Ticker identity |
| `source_files` | Provenance — every ingested CSV recorded |
| `feature_sets` | Versioned feature engineering definitions |
| `pattern_instances` | One row per historical setup observation |
| `pattern_bars` | Per-bar data; raw VP columns + normalized columns |
| `pattern_features` | Derived window-level features |
| `forward_labels` | Outcome at 5/7/10/15/20-day horizons |

| Index | Target |
| :---- | :---- |
| `idx_pattern_instances_symbol_anchor` | `(symbol_id, anchor_date)` |
| `idx_pattern_bars_pattern_offset` | `(pattern_instance_id, bar_offset)` |
| `idx_forward_labels_pattern_horizon` | `(pattern_instance_id, horizon_days)` |
| `idx_pattern_instances_origin` | `(data_origin_type)` |

### Bootstrap row inserted

| Table | Row |
| :---- | :---- |
| `feature_sets` | `feature_version='baseline_v1'`, description per `config.DEFAULT_FEATURE_DESCRIPTION`, `created_at=<utc-now-iso>` |

### Naming note

Architecture v2.1 §2.5 claims an "8-table schema" but §9.2 defines only 7 tables. The 8-table claim is stale wording from earlier planning, propagated through §2.5, §7 enhancement log, and `tasks/todo.md` 3.2. Pending architecture doc cleanup will canonicalize the wording to "7-table".

---

## Stage 3.3 — db_utils.py Surgical Edit

| Item | Before (v1.14) | After (v1.15) |
| :---- | :---- | :---- |
| Glob pattern | `*geminicatalog.db` | `*catalog.db` |
| Header | Missing AUTHOR / LAYER / CHANGELOG | Full §8.4.1 standard |
| Path | Hardcoded MODELS_DIR | (Same as v1.14 — refactored later in Bonus to import from config) |

---

## Stage 3.3+ Bonus (out of original scope; added during stage closeout)

### db_utils.py v1.15 → v1.16

| Item | v1.15 | v1.16 |
| :---- | :---- | :---- |
| `MODELS_DIR` | Hardcoded `Path(r"C:\Users\Trader\...\models")` | Imported from `config.MODELS_DIR` |
| `CATALOG_GLOB_PATTERN` | Hardcoded literal `'*catalog.db'` | Imported from `config.CATALOG_GLOB_PATTERN` |
| sys.path bootstrap | Absent | Added — `sys.path.insert(0, parents[1])` so standalone runs find `config.py` |

Rationale: architecture §2.4 single-source-of-truth rule was violated by the hardcoded path in v1.15. Closed in v1.16.

### db_connect.py v1.0 (new file)

Path: `python/utilities/db_connect.py`

Purpose: M-012 enforcement point — every catalog connection in the project flows through this factory, which sets `PRAGMA foreign_keys = ON` before returning the connection. Prevents EC-027-class hollow rows by structurally enforcing FK constraints.

Public surface:
- `get_connection(catalog_path=None) -> sqlite3.Connection` — manual lifecycle
- `connection_context(catalog_path=None)` — context manager (auto commit/rollback/close)

Smoke-test entry point in `__main__`: opens active catalog, verifies pragma is 1, reads `baseline_v1` feature_sets row.

### lessons.md additions

| ID | Topic | Identified |
| :---- | :---- | :---- |
| M-011 | Route Python logging to stdout in PowerShell-invoked scripts | 2026-05-13 (Stage 3a verification) |
| M-012 | `PRAGMA foreign_keys = ON` on every sqlite3 connection | 2026-05-14 (Stage 3c verification) |

---

## Verification Checklist

- [x] `python/` contains only: `application/`, `archive/`, `config.py`, `domain/`, `infrastructure/`, `migrations/`, `requirements.txt`, `schemas.py`, `utilities/`
- [x] `python/utilities/` contains only: `.vscode/`, `__init__.py`, `db_utils.py`, `db_connect.py`
- [x] `models/` contains only: `archive/`, `configs/`, `trained/`, `051426catalog.db`
- [x] `db_utils.get_latest_catalog()` resolves to `models/051426catalog.db`
- [x] `models/051426catalog.db` opens with 7 tables, 4 indexes, 1 bootstrap `feature_sets` row
- [x] `db_connect.py` smoke test reports `foreign_keys = 1, feature_sets row = baseline_v1` (verified 2026-05-14)
- [x] Architecture doc "8-table" → "7-table" canonical-text cleanup (completed in v2.2, 2026-05-14)

---

## Outstanding (Stage 4 Inheritance)

1. `infrastructure/catalog_writer.py` MUST import connections from `utilities.db_connect.connection_context()` — no direct `sqlite3.connect()`.
2. `infrastructure/catalog_reader.py` — same constraint.
3. Every migration script in Stage 4+ — same constraint.
4. Lock + Temp-DB + Atomic Move write pattern (architecture §2.6) is unimplemented; build in Stage 4 alongside Pipeline A.
5. `verify_ingestion.py` (Pipeline A health check) — wraps Verify Temp + Atomic Move + Log steps; unimplemented (ID-004).
6. Architecture doc v2.2 cleanup: patch "8-table" wording in §2.5, §7, and Stage 3 todo.md; reflect db_connect.py addition.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** Reopen if any Stage 3 artifact is moved, edited, or deleted post-closeout. Otherwise frozen as historical record.
- **Promotion:** Migration ledgers are stage-scoped; this document closes when Stage 3 closes.

---

**End of Stage 3 Migration Ledger**
