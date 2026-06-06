# P_300 Task Lessons & Development Protocols

## Project Overview
**Project:** P_300 Vantage Point Pattern Recognition
**Focus:** Data Pipeline, Normalization, and IntelliScan Reporting
**Last Review:** 2026-05-06

---

## 1. Data Integrity & Normalization
* **The Lesson:** "Garbage in, Garbage out" applies heavily to datetime fields. Mixing `MM/DD/YYYY` and `YYYY-MM-DD` strings creates a ticking time bomb for database queries.
* **The Resolution:** * **Source Normalization:** Always enforce `YYYY-MM-DD` at the ingestion/conversion gate. 
    * **In-Place Repair:** If the DB is corrupted, use a surgical Pandas script to `to_datetime(format='mixed')` and write back to the DB.
    * **Schema Safety:** Never rely on implicit date formatting in SQL queries; always parse to ISO-8601 standard before storage.

## 2. System Architecture & Imports
* **The Lesson:** Python's module resolution (`sys.path`) is sensitive to the execution directory. Running scripts from `P_301` while targeting `P_300` causes import failures because the local folder isn't in the Python path.
* **The Resolution:**
    * **Absolute Path Injection:** Use `sys.path.insert(0, <absolute_project_root>)` at the top of every module that relies on cross-package imports (e.g., `matching.intelliscan`).
    * **Package Definition:** Ensure every subdirectory (e.g., `matching/`) has an `__init__.py` file, even if empty. This is mandatory for Python to recognize it as a package.

## 3. Database Hygiene
* **The Lesson:** SQLite `rowid` vs. Pandas Index. Pandas often treats `rowid` as an index rather than a column, leading to `KeyError` during bulk updates.
* **The Resolution:**
    * Always use SQL aliasing (e.g., `SELECT rowid AS rid...`) to give the ID a unique name that won't conflict with Pandas' internal metadata.

## 4. Development Protocol (The "P_300 Handshake")
To maintain project stability, adhere to the following when switching environments or resuming work:
1.  **Version Headers:** Every file must contain a `FILE`, `VERSION`, `DATE`, `DESCRIPTION`, and `CHANGELOG` header.
2.  **Environment Check:** Verify the active database path (`db_utils.get_latest_catalog()`) before executing any aggregation or reporting scripts.
3.  **Dependency Check:** If a script fails, check `sys.path` first. Hardcoding absolute paths for internal project modules is preferred over relative imports for stability in complex folder structures.

## 5. Future Task Queue
* [ ] Implement a CI-style validation script that runs before `aggregator.py` to check for DB existence and date format consistency.
* [ ] Refactor `ingest_vp_catalog.py` to include a checksum validation for new patterns.
* [ ] Complete Phase 2: Statistical Aggregation of the full 394-pattern catalog.
