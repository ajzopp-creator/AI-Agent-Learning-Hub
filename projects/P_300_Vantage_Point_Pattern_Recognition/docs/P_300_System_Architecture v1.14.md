### **P_300 PRE-FLIGHT AUDIT**

* [x] **Artifact Complete:** YES (Entire, un-truncated merged architecture document provided)
* [x] **Path Resolved:** YES (Document standard applies)
* [x] **Finality:** YES (No user audit requested)
* [x] **Schema Parity:** YES (Canonical schema declared in Section 9.1; ID-003 resolved)
* [x] **Context Sync:** YES (References to `*geminicatalog.db` resolved)


**P_300 - VantagePoint Pattern Recognition System Architecture Document**

**Project ID:** P_300

**Version:** 1.15

**Last Updated:** 2026-05-07

**Maintained By:** Anthony Zoppi

**Status:** Active / In Development

## ---

**Documentation Decision Protocol**

This document is the **master architecture reference** for the P_300 project. New P_300 documentation should be added here first unless the content is long-form, frequently updated, reused across projects, or requires separate version history. If a separate file is created, it should be referenced back inside this document and named using the project convention.

**Golden rule:** Start every new P_300 AI session by reading this document first, summarizing current status, confirming the current milestone, and identifying the next action before doing any task work.

## ---

**Table of Contents**

1. Project Overview
2. System Architecture
3. AI Tools & Platforms
4. Requirements
5. Change Log
6. Error Corrections Log
7. Enhancement Log
8. AI Workflows & Processes
9. Data Design
10. Testing & Validation
11. Daily Operations & Session Management
12. Troubleshooting & Support
13. Appendices

# ---

**1. Project Overview**

## **1.1 Purpose**

P_300_Vantage_Point_Pattern_Recognition is a VantagePoint-based research and development project focused on building a durable historical pattern catalog from SPY and later multi-symbol market data. Its purpose is to detect repeatable short-horizon market patterns, label them by forward profitability, and use those labels to support future IntelliScan-style matching and ranking workflows.

## **1.2 Scope**

**What this system covers** - Historical pattern extraction from VantagePoint / history-grid style data

* Pattern catalog creation using structured historical records
* Profitability labeling for 5-day to 10-day holding windows
* Future matching of current IntelliScan candidates to historical analog patterns
* AI-assisted research, planning, architecture, and workflow control

**What this system does not cover** - Automated live brokerage execution

* Full enterprise data engineering infrastructure
* Long-horizon portfolio optimization
* Non-pattern-based discretionary market analysis unless explicitly added later

## **1.3 Project Details**

| Field | Value |
| :---- | :---- |
| Start Date | 2026 Q1 build phase |
| Current Status | Milestone 2 complete; Direction A complete (981 real forward labels generated from 391 pattern instances); Daily Pattern Analysis Workflow operational; Milestone 3 (IntelliScan refinement / Direction B) in progress; Milestone 5 (Trade Management) scoped |
| Primary AI Engine | Claude (Architect) -> Gemini -> Grok -> Local LLM (Final Destination) |
| Primary Platform | Python, VantagePoint exports, local documentation workflow |
| Project Location | AI-Agent-Learning-Hub / P_300_Vantage_Point_Pattern_Recognition |
| Related Projects | P_000, P_010, P_020, P_115 |

## **1.4 Reference Materials**

| Document | Location | Notes |
| :---- | :---- | :---- |
| README.md | P_000 foundation project | Master hub architecture reference |
| P300_Pipeline_Flow_V2 | docs/validation/ | Visual representation of pipeline flow |
| UNIVERSAL_PROJECT_TEMPLATE_v1_1.md | Project documentation template | Source template for this architecture doc |
| P300 carryover summary | Session content / working notes | Current milestone state |
| Trading_Projects_Folder_Architecture.md | Hub root | Environment and architecture standards |
| Daily Pattern Analysis Workflow | Section 2.6 of this document | Operational standard for incoming CSV processing |
| Catalog DB Check-In / Check-Out Protocol | Section 2.7 of this document | Required bracketing rule for all DB operations |

## **1.5 Definitions & Acronyms**

| Term | Definition |
| :---- | :---- |
| VP | VantagePoint |
| Pattern Catalog | Structured database of historical setup instances and labels |
| IntelliScan Matching | Comparing live or recent candidates to historical analog patterns |
| Forward Label | Future return / outcome metric over 5-10 trading days |
| Session Bootstrap | Required startup process that loads this document before work begins |
| Daily Pattern Analysis Workflow | The four-step operational pipeline (Ingest, Archive, Match, Report) executed each time new VantagePoint CSVs arrive |
| Catalog Check-Out | Pre-operation read/inspection step that verifies the SQLite catalog state before any read or write |
| Catalog Check-In | Post-operation validation step that confirms row counts, schema parity, and data integrity after any write |
| Direction A | Replacement of dummy data with real VantagePoint forward labels in the catalog (Complete) |
| Direction B | Upgrade of the IntelliScan similarity matching algorithm (In Progress) |

# ---

**2. System Architecture**

## **2.1 High-Level Flow**

*Refer to P300_Pipeline_Flow_V2 for the updated visual architecture.*

```
Historical Market Data / VP History Grid
                |
                v
      Data Cleaning / Standardization
                |
                v
      Feature Extraction / Pattern Encoding
                |
                v
    Pattern Instance Catalog in SQLite DB
                |
                v
  Forward Return Labeling (5d / 7d / 10d)
                |
                v
   Historical Match Query / Similarity Engine
                |
                v
 IntelliScan Candidate Matching and Ranking
```

## **2.2 P_300 Data Parity Flowboard (Mandatory Workflow)**

This visual model defines the immutable path data takes from the Sandbox "Truth" to the Local Environment to prevent drift.

```
+-----------------------+      +-----------------------+      +-----------------------+
|    SANDBOX TRUTH      |      |   PARITY VERIFICATION |      |  LOCAL ENVIRONMENT    |
+-----------------------+      +-----------------------+      +-----------------------+
|                       |      |                       |      |                       |
|  [Source Master Data] |----->|  [Handshake Protocol] |----->|   [models/catalog.db] |
|                       |      |  - Checksum Verification    |      |                       |
|  [Validated Schema]   |      |  - Row Count Check    |      |   [Injection Scripts] |
|                       |      |                       |      |    (seed_data.py)     |
+-----------------------+      +-----------------------+      +-----------------------+
           ^                                                            |
           |________________________Validation Loop_____________________|
```

### **Protocol Steps:**

1. **State Identification:** Define if the task is a *Schema Update* or *Data Hydration*.
2. **Serialization (The Handshake):** Perform row-count checks on the Sandbox source and Local destination.
3. **Secure Transmission:** Use verified Python injection scripts (seed_data.py, sync_catalog.py) to move data. Never rely on manual file copies for database state.
4. **Local Injection:** The data must land directly in the models\ directory.
5. **Validation Loop:** Run validate_catalog.py immediately post-sync. If Row Counts do not match, trigger a Rollback to the previous stable state.

## **2.3 Core Components**

### **Component 1 — Data Input Layer**

* **Responsibility:** Load SPY and future multi-symbol historical data from VantagePoint exports, spreadsheets, CSV, or transformed files.
* **Inputs:** History-grid exports, CSV files, Excel files, manually validated pattern examples.
* **Outputs:** Clean bar-level records and normalized data tables.
* **Tools Used:** Python, CSV/XLSX processing, hub folder structure.
* **Dependencies:** Consistent source files, file naming discipline, project folder conventions.

### **Component 2 — Pattern Engineering Layer**

* **Responsibility:** Transform cleaned market records into comparable pattern feature vectors.
* **Inputs:** Clean historical OHLCV-style records and derived indicators.
* **Outputs:** Pattern signatures, window encodings, feature hashes, and similarity-ready representations.
* **Tools Used:** Python scripts, reusable utilities from hub architecture.
* **Dependencies:** Stable feature definitions and version-controlled logic.

### **Component 3 — Catalog & Labeling Layer**

* **Responsibility:** Persist pattern instances in SQLite and attach future profitability labels for defined hold periods.
* **Inputs:** Pattern vectors plus future return windows.
* **Outputs:** SQLite catalog tables, forward-return labels, win/loss classifications, hit-rate-ready records.
* **Tools Used:** Python, SQLite.
* **Dependencies:** Historical completeness, label definitions, schema control.

### **Component 4 — Matching & Decision Support Layer**

* **Responsibility:** Query historical analogs for current patterns and rank likely outcomes.
* **Inputs:** Current candidate pattern, pattern catalog, match criteria.
* **Outputs:** Ranked analogs, expected return tendencies, confidence context.
* **Tools Used:** Python, AI reasoning workflow, future IntelliScan integration.
* **Dependencies:** Pattern database quality, similarity rules, clean session context.

### **Component 5 — AI Session Control Layer**

* **Responsibility:** Maintain consistency across sessions using architecture documents, startup prompts, and documented rules.
* **Inputs:** This architecture document, project summaries, thread startup instructions.
* **Outputs:** Context continuity, reduced drift, more consistent task execution.
* **Tools Used:** Claude/Gemini/Grok/LLM project workflows, markdown documentation.
* **Dependencies:** User discipline to load architecture first every session.

## **2.4 System Decomposition**

```   Latest directory Map   "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\P_300_Directory_map.txt"
P_300_Vantage_Point_Pattern_Recognition/
|
+-- python/
|   +-- ingest/
|   +-- feature_engineering/
|   +-- matching/
|   +-- labeling/
|   +-- reporting/
|   +-- utilities/
|
+-- data/
|   +-- live/
|   +-- raw/
|   +-- processed/
|   +-- historical/
|   +-- reference/
|
+-- outputs/
|   +-- reports/
|   +-- charts/
|   +-- exports/
|
+-- docs/
|   +-- architecture/
|   +-- prompts/
|   +-- notes/
|   +-- validation/
|
+-- models/
|   +-- catalog.db
|   +-- 050326geminicatalog.db
|   +-- temp_working.db
|   +-- schema/
```

## **2.5 Design Rationale**

* **Simplicity:** Start with SPY only, one repeatable pipeline, and a clean SQLite catalog before adding more assets.
* **AI-centric control:** The AI is used for planning, schema design, workflow enforcement, and research support rather than replacing deterministic computation.
* **Maintainability:** Documentation-first architecture reduces thread drift and creates a stable project memory anchor.
* **Independence:** P_300 follows hub standards from P_000 while remaining a self-contained pattern-recognition system.

**Alternatives considered**

| Option | Pros | Cons | Decision |
| :---- | :---- | :---- | :---- |
| Start multi-stock immediately | Faster expansion | Higher complexity, harder validation | Rejected for v1 |
| Use flat CSV only | Simple to inspect | Weak for querying and scaling | Rejected |
| Build SQLite-first on SPY | Structured, queryable, scalable | Slightly more setup | Selected |

## **2.6 Daily Pattern Analysis Workflow (Operational Standard)**

This is the official operational pipeline for processing every batch of incoming VantagePoint CSV exports. It replaces ad-hoc command sequences with a four-step pipeline anchored to PowerShell wrappers stored in `python/utilities/`. The workflow supports both single-file and batch (one-to-many) processing modes.

### **Workflow Steps**

**Step 1 — Ingest:** Read incoming CSVs from `data/live/` and write pattern instances into the catalog.

```powershell
python C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\ingest\ingest_vp_catalog.py --type EVAL_SET --db-path C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db
```

**Step 2 — Archive:** Move processed CSVs from `data/live/` to `data/processed/` so the live folder stays clean for the next batch.

```powershell
Move-Item -Path "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\live\*.csv" -Destination "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\data\processed\"
```

**Step 3 — Pattern Match:** Run the IntelliScan engine against the newly ingested patterns.

```powershell
python C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\matching\intelliscan.py
```

**Step 4 — Confidence Report:** Generate the aggregated confidence report. The smart aggregator auto-detects the most recently ingested pattern IDs (no manual ID entry required).

```powershell
python C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\reporting\aggregator.py
```

### **PowerShell Wrappers (Utilities)**

Five wrapper scripts live in `python/utilities/` so the daily sequence can be executed without retyping long paths.

Wrapper	Wraps	Purpose
P_300_00_WorkflowLauncher.ps1	Orchestrator	Master launcher for the daily pattern analysis pipeline.
P_300_05_ingest.ps1	Step 1	Run ingest with EVAL_SET type against 050326geminicatalog.db.
P_300_10_ArchiveCSV.ps1	Step 2	Move all CSVs from data\live to data\processed.
P_300_20_PatternMatch.ps1	Step 3	Run intelliscan.py similarity engine.
P_300_50_ConReport.ps1	Step 4	Run aggregator.py (smart, auto-ID-detection
### **Sequential Execution Pattern**

```powershell
& "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\P_300-00_ingest.ps1"
& "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\P_300_10_ArchiveCSV.ps1"
& "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\P_300_20_PatternMatch.ps1"
& "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\P_300_50_ConReport.ps1"
```

### **Batch Mode (One-to-Many CSVs)**

When multiple CSVs arrive together (e.g., 10 symbols on a Friday batch), drop all of them into `data/live/` and run the standard sequence. The ingest script iterates every `.csv` in the folder; the smart aggregator queries the database for the most recently inserted `pattern_instance_id` values and reports on every one of them automatically.

### **Folder Roles (Code vs. Data)**

The `python/reporting/` folder holds reporting code (the aggregator). The `data/processed/` folder holds archived CSV data files. They are intentionally separate — code logic stays under `python/`, data archives stay under `data/`.

| Folder | Role |
| :---- | :---- |
| `data/live/` | Drop incoming CSVs here |
| `data/processed/` | Archived CSVs after ingest |
| `python/ingest/` | Source of truth for data entry |
| `python/feature_engineering/` | Indicator calculation |
| `python/matching/` | IntelliScan engine |
| `python/reporting/` | Final decision support (Aggregator) |
| `python/utilities/` | PowerShell wrappers and inspection scripts |
| `models/` | SQLite catalog databases |

## **2.7 Catalog DB Check-In / Check-Out Protocol (Mandatory)**

Every operation that reads or writes the SQLite catalog must be bracketed by an explicit **Check-Out** before the operation and an explicit **Check-In** after. This rule prevents silent corruption, schema drift, and unverified data states. Tony's standing requirement: no work proceeds against the catalog without first verifying its current state, and no session ends without confirming the post-operation state.

### **Check-Out (Pre-Operation Verification)**

Performed at session start and before any operation that modifies the catalog. Confirms the database file exists at the immutable path, opens cleanly, and contains the expected tables and row counts.

**Required actions:**

1. Confirm file exists at `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db`.
2. Open via SQLite and run a row-count probe on each core table (`pattern_instances`, `forward_labels`).
3. Inspect the most recent rows to verify schema integrity and data sanity.
4. Record the pre-operation row counts in working notes for later comparison.

**Visual route:** Open `mmddyygeminicatalog.db` in **DB Browser for SQLite** (free, open-source). Use the *Browse Data* tab to inspect `pattern_instances` and `forward_labels`.  Where mmddyygeminicatalog is the moset recent catalog.db  Example:050326geminicatalog.db

**Script route:** `python\utilities\inspect_catalog.py` prints the contents of `pattern_instances` to the terminal.

```powershell
python C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\inspect_catalog.py
```

### **Check-In (Post-Operation Validation)**

Performed immediately after any ingest, label generation, or schema change. Confirms the operation produced the expected delta and did not corrupt existing data.

**Required actions:**

1. Re-run a row-count probe on each modified table.
2. Confirm the delta matches the expected number of new rows (e.g., 391 new patterns → 981 new forward labels at 5d/7d/10d horizons, allowing for edge-of-dataset truncation).
3. Run `python\utilities\inspect_labels.py` to view the 15 most recent forward labels joined to their pattern instances.
4. Verify `return_pct` and `is_profitable` columns look mathematically correct on spot-check rows.
5. Record the post-operation row counts and the schema version in the session log.

```powershell
python C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\python\utilities\inspect_labels.py
```

### **Check-In / Check-Out Bracketing Rule**

| Phase | Required Steps |
| :---- | :---- |
| Session Start | Check-Out (verify catalog state before work) |
| Before Ingest / Label / Schema Op | Check-Out (record pre-op row counts) |
| After Ingest / Label / Schema Op | Check-In (verify delta, inspect new rows, log row count + schema version) |
| Session End | Final Check-In (confirm catalog is in expected stable state) |

### **Write-Operation Transaction Safety (Lock + Temp-DB + Atomic Move)**

For any operation that writes to the canonical DB (ingest, label generation, schema change), the basic Check-Out / Check-In bracketing is escalated with a temp-DB transaction pattern. This prevents partial writes, mid-operation crashes, and concurrent-writer corruption from damaging the master.

1. **Lock Verify:** Confirm no other process is currently writing to `mmddyygeminicatalog.db`. If a writer is active, halt and wait.
2. **Copy to Temp:** Copy the master to `models/temp_working.db`. All write operations target the temp file, never the master.
3. **Verify Temp:** After the operation completes, run integrity checks against `temp_working.db` — row-count delta matches expectation, schema matches the canonical schema in Section 9.1, and spot-check inspections pass (`inspect_labels.py` against the temp path).
4. **Atomic Move:** Only after verification succeeds, atomically replace the master file with the verified temp file. On any failure, discard the temp file and leave the master untouched.
5. **Log:** Record the post-operation row count and schema version in the session log immediately after Check-In.

The dedicated `verify_ingestion.py` utility that wraps steps 3–5 is planned and tracked in the Enhancement Log; until it ships, perform the verification manually using `inspect_catalog.py` and `inspect_labels.py` pointed at the temp path.

### **Failure Mode Response**

If any Check-Out reveals an unexpected state (missing tables, row count regression, schema mismatch), halt all work and trigger the Rollback step from the Data Parity Flowboard (Section 2.2). Do not attempt to "patch forward" through an unverified catalog. If a temp-DB verification fails, discard `temp_working.db` and leave the master untouched.

# ---

**3. AI Tools & Platforms**

## **3.1 Tool Stack**

| Tool / Platform | Role in System | Notes |
| :---- | :---- | :---- |
| Python | Data processing, feature engineering, labeling, matching | Shared p140 environment standard |
| SQLite | Pattern catalog database | Primary structured storage |
| VantagePoint data exports | Historical input source | Core upstream data feed |
| Claude | Primary AI Architect | High-level reasoning, system architecture |
| Gemini | Intermediate Reasoning | Workflow execution, pattern validation |
| Grok | Real-time Context Analysis | Signal filtering, noise reduction |
| Local LLM (LM Studio) | Final Execution / Research | Localized pattern analysis (Final Destination) |
| Perplexity | Research | Deprecated from workflow, research only |
| DB Browser for SQLite | Visual catalog inspection | Used for the visual route of Catalog Check-Out |
| PowerShell | Workflow automation | Hosts the four `.ps1` wrappers in `python/utilities/` |

## **3.2 AI Behavior Rules**

**Multi-AI Environment Protocol:**

* **Primary Progression:** Claude (Architectural Foundation) → Gemini (Workflow Execution) → Grok (Signal Analysis/Noise Filtering) → Local LLM (Final Logic/Implementation).
* **Claude** is designated as the **Primary AI Architect**. Architectural changes must be reviewed by Claude.
* **Logging:** All AI interactions and tool usages should be noted in the Error/Enhancement logs when relevant.

**AI must**

* Read this architecture document at the start of every new P_300 thread.
* Summarize current status before starting new work.
* Use documented milestone state, not assumptions.
* Distinguish confirmed project facts from proposed next steps.
* Keep outputs aligned to project folder and naming conventions.
* Execute Catalog Check-Out before any DB-touching operation and Check-In after.
* Apply the Lock + Temp-DB + Atomic Move pattern for all write operations against the canonical DB.

**AI must not**

* Invent project status that is not documented.
* Skip architecture loading on a new thread.
* Change schema or folder conventions without documenting the change.
* Treat thread memory as authoritative when the architecture document says otherwise.
* Introduce a new parser, schema, workflow, or generalized implementation path when the approved task is to clone the validated POC exactly.
* Skip the Check-Out / Check-In bracketing on any catalog operation.
* Write directly to the master DB without going through `temp_working.db` first.

**POC Drift Guardrail**

The default rule for P_300 work is to stay on the validated POC exactly: clone the proven SPY-first path, keep the canonical schema and feature set unchanged, and do not introduce a new parser, schema, workflow, or generalization unless it is explicitly documented and approved as an intentional deviation. Any proposal that changes the baseline must be flagged immediately as POC drift, reviewed against the master architecture, and held until approval before implementation.

## **3.3 The P_300 Bootstrap Handshake (Session Initialization Rule)**

At the start of every new thread, the AI must execute the **P_300 Bootstrap Handshake** before accepting any task.

**The Handshake Prompt:** Read P300_System_Architecture.md first. Next, explicitly review **Section 6 (Error Corrections Log)** to understand past failures and ensure you do not repeat errors that cause hallucination or drift. Perform the **Catalog Check-Out** (Section 2.7) to confirm the current state of `050326geminicatalog.db`. Finally, summarize the current project status, identify the current milestone, restate the next approved objective, list any required reference files, and wait for confirmation or proceed only within those constraints. Treat the validated SPY-first POC as the default implementation path and flag any new parser, schema, workflow, or generalized approach as POC drift unless explicitly approved.

# ---

**4. Requirements**

## **4.1 Functional Requirements**

* **FR-1:** The system must ingest historical SPY data into a structured processing pipeline.
* **FR-2:** The system must compute repeatable pattern features for historical windows.
* **FR-3:** The system must create a SQLite pattern catalog database.
* **FR-4:** The system must attach forward profitability labels for 5-day, 7-day, and 10-day holds.
* **FR-5:** The system must support later extension to multi-stock IntelliScan matching.
* **FR-6:** The system must begin every new AI thread with the P_300 Bootstrap Handshake.
* **FR-7:** The system must support batch (one-to-many) CSV processing through the Daily Pattern Analysis Workflow.
* **FR-8:** The system must enforce Catalog Check-In / Check-Out bracketing on every database operation.
* **FR-9:** The system must apply Lock + Temp-DB + Atomic Move on every write operation against the canonical DB.

## **4.2 Non-Functional Requirements**

* **NFR-1 Accuracy:** No fabricated pattern statistics or milestone claims.
* **NFR-2 Consistency:** Same startup process every new session.
* **NFR-3 Auditability:** Schema, rules, and milestone changes must be documented.
* **NFR-4 Maintainability:** Folder conventions and master-document links must remain stable.
* **NFR-5 Scalability:** SPY-first design must support later multi-symbol expansion.

## **4.3 Requirements Matrix**

| ID | Description | Component | Status |
| :---- | :---- | :---- | :---- |
| FR-1 | Historical ingest | Data Input Layer | Complete |
| FR-2 | Feature engineering | Pattern Engineering Layer | Complete |
| FR-3 | SQLite catalog | Catalog & Labeling Layer | Complete |
| FR-4 | 5-10 day labels | Catalog & Labeling Layer | Complete |
| FR-5 | Multi-stock readiness | Matching Layer | Planned |
| FR-6 | Session bootstrap | AI Session Control Layer | Complete |
| FR-7 | Batch CSV processing | Daily Pattern Analysis Workflow | Complete |
| FR-8 | Check-In / Check-Out enforcement | Catalog & Labeling Layer | Complete |
| FR-9 | Lock + Temp-DB + Atomic Move on writes | Catalog & Labeling Layer | Procedural; awaiting `verify_ingestion.py` for full automation |

# ---

**5. Change Log**

## **5.1 Version History**
* **v1.15 — 2026-05-07**
  *  Successfully navigated complex mathematical scaling issues, enforced strict data integrity rules, and completed Milestone 4. The P_300 system is now equipped with a statistically validated, config-driven engine capable of filtering market noise from true signals.
  * EC-043 ... EC-047
* **v1.14 — 2026-05-06**
  *  Refactored `db_utils.py` to enforce numeric prefix filtering, preventing selection of 'org_' or invalid database backups. |
  *  `ingest_vp_catalog.py` | **CRITICAL LOGIC FIX (Anchor Date Extraction):** Changed chronological sorting extraction from `.tail(1)` to `.head(1)`. VantagePoint CSVs list newest dates at the top and oldest dates at the bottom. To correctly identify the "Anchor Date" (Day 0 / Pattern Trigger Day) and allow the labeling script to calculate future returns, the ingestion script must isolate the *oldest* date in the file, not the newest.
  * EC-038 ... EC-042
**v1.13 — 2026-05-06**
  * Added python\utilities\Dbutils. Utility to obtain LAtest catalog    
  * Added Section 8.4   Coding standards
 
* **v1.12 — 2026-05-05**
  * Added resaolution of Friction by distinuishing between Sandbox (Development) and Deployment Environments (AJZStrategies Laptop)
  * Moved Pattern recogniion from Sandbox to Deployment .  Naming convention of catalog.db on Deployment Evironment.
  * Added EC029 ..EX033
* **v1.11 — 2026-05-03**
  * Added P_300_00_WorkflowLauncher.ps1
  * Added EC-016 ... EC-028 
* **v1.10 — 2026-05-03**
  * Added Section 2.6: Daily Pattern Analysis Workflow (4-step pipeline with PowerShell wrappers in `python/utilities/`).
  * Added Section 2.7: Catalog DB Check-In / Check-Out Protocol (mandatory bracketing rule for all DB operations).
  * Section 2.7 expanded with Write-Operation Transaction Safety subsection: Lock Verify, Copy-to-Temp (`temp_working.db`), Verify Temp, Atomic Move, Schema-Version Logging. Sourced from Gemini's Database Integrity Protocol restatement.
  * Section 9 Data Design rewritten: canonical schema declared as `models/050326geminicatalog.db`. Legacy baseline_5bar_v1 schema and production-variant subsection removed. ID-003 Resolved.
  * Added Section 11.5: Daily Pattern Analysis Workflow operational reference.
  * Added FR-7 (batch CSV processing), FR-8 (Check-In / Check-Out enforcement), and FR-9 (Lock + Temp-DB + Atomic Move) to requirements matrix.
  * Added EC-015: PowerShell ExecutionPolicy block on unsigned `.ps1` scripts.
  * Recorded Direction A complete: 981 real forward labels generated from 391 pattern instances.
  * Updated Session Bootstrap Handshake to include Catalog Check-Out as a required step.
  * Working Folder Map updated with `data/live/`, `data/processed/`, `python/reporting/`, `temp_working.db`, and the four `.ps1` wrappers.
  * Added EC-016 Hallucination
* **v1.9 — 2026-05-03**
  * Formalization of Mandatory Pre-Flight Audit protocol (Section 11.4).
* **v1.8 — 2026-05-03**
  * Expanded Session Initialization Rule to formalize the **"P_300 Bootstrap Handshake"**.
  * Mandated explicit review of Section 6 (Error Log) during startup to prevent hallucination and systemic drift.
* **v1.7 — 2026-05-03**
  * Consolidated full history, fixed missing log entries (EC-001 through EC-014).
  * Added Data Parity Flowboard mapping the immutable local environment path.
* **v1.6 — 2026-05-03**
  * Enforced "Full Artifact" delivery rule (all scripts/docs delivered in full).
* **v1.5 — 2026-05-02**
  * Updated AI stack to Claude (Architect) -> Gemini -> Grok -> Local LLM pipeline.
* **v1.4 — 2026-05-02**
  * Completed Milestone 2.
* **v1.3 — 2026-04-30**
  * Schema baseline (baseline_5bar_v1) validated.
* **v1.2 — 2026-04-25**
  * Pipeline Flow V2 visual added.
* **v1.1 — 2026-04-20**
  * Master architecture document established.
* **v1.0 — 2026-04-15**
  * Initial project documentation.

# ---

**6. Error Corrections Log**

| ID | Description | Status | Resolution |
| :---- | :---- | :---- | :---- |
| EC-001 | Perplexity Context Drift | Fixed | Implemented session-start architecture load. |
| EC-002 | Missing Architecture Documentation | Fixed | Consolidated all docs into this file. |
| EC-003 | Pipeline Ingestion logic errors | Fixed | Standardized `initialize_db.py` schema. |
| EC-004 | Incorrect Path Mapping | Fixed | Absolute paths enforced. |
| EC-005 | Environment Path Drift | Fixed | Locked `C:\Users\Trader\...` as System of Record. |
| EC-006 | Missing Table (pattern_instances) | Fixed | Schema verified and patched. |
| EC-007 | Script Dependency/Pathing | Fixed | Removed relative paths; used absolute. |
| EC-008 | CSV Data Transfer Failure | Fixed | Switched to internal database hydration. |
| EC-009 | Syntax/Line continuation errors | Fixed | Abandoned one-liners; transitioned to full scripts. |
| EC-010 | Operational Path Deviation | Fixed | Paths are now hardcoded and immutable. |
| EC-011 | Schema Version Mismatch | Fixed | Resolved by manual patch and verified parity. |
| EC-012 | Data Parity Failure | Fixed | Resolved by hydration scripts. |
| EC-013 | SQL Binding Syntax Error | Fixed | Resolved by using Python `timedelta` logic. |
| EC-014 | Partial Code Delivery | Fixed | Full Artifact Rule enforced. |
| EC-015 | PowerShell ExecutionPolicy block on unsigned `.ps1` scripts | Fixed | Resolved per session with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. Long-term: sign scripts or keep the bypass scoped to the session. |
| EC-016 |  AI hallucinated a requirement to upload an IntelliScan file to the chat "Sandbox" for ingestion, breaking the      established local execution workflow. |Fixed | Resolution: AI must trust the user's local directory structure (data/raw/intelliscan/) and immediately provide the correct PowerShell/Python command to run the evaluation locally, assuming the data is already perfectly validated.|
ID,Description,Status,Resolution
|EC-017|,Rigid Lookback Horizon: Engine failing to scale similarity matching beyond 5-day windows.| Fixed | Implemented get_dynamic_normalized_close to scale DTW lookback up to 20 days automatically.
|EC-018|,"Time-Series Anchoring: Multi-day time-series files (e.g., 21-day) creating redundant/duplicate pattern_instances for every row." | Fixed |"Enforced ""Single Anchor"" policy; script now sorts chronologically and anchors only on the final date (tail(1))."
|EC-019|,Polluted Stream Reporting: Aggregator mixing historical training patterns with current EVAL_SET candidates. | Fixed |Enforced strict filtering in aggregator.py using data_origin_type = 'EVAL_SET' for all query operations.
|EC-020|,"Signal Interpretation Failure: ""No Matches Found"" output misinterpreted as code bug rather than system-defined ""No Trade"" signal." | Fixed | "Formally defined ""No Match"" as an explicit ""Stay in Cash"" signal; ceased debugging/code modification on this output."
|EC-021|DB-001	AI hallucinated column names for catalog.db instead of requesting exact DDL/schema or the physical database file.	| Fixed |Resolved	AI must explicitly request the current schema or the physical catalog.db file before drafting or modifying any SQL queries or database-interacting code.
|EC-022|	Pipeline Drift: Matching engine defaulting to legacy SPY records and returning false 0.0 distances for IVR.	| Open | Unresolved	Audit ingestion pipeline to ensure features are actually written to pattern_features
|EC-023|	Ingestion lacks idempotency (duplicate check).	| Fixed |	Added SELECT 1 pre-check in ingest_logic.py. Pipeline now aborts (sys.exit(1)) on duplicates.
|EC-024|	Pipeline lacks "Fail-Fast" mechanism.	| Fixed | Resolved	Added $LASTEXITCODE checking in WorkflowLauncher.ps1. Pipeline now terminates on any non-zero exit.
|EC-025|	AI bypassed established .ps1 wrappers in WorkflowLauncher.ps1 and hallucinated a non-existent ArchiveCSV.py file.	| Fixed |Resolved	Revert WorkflowLauncher.ps1 to strictly call the user's defined .ps1 scripts, injecting only the $LASTEXITCODE Fail-Fast logic.
|EC-026|	Empty inbox does not trigger Fail-Fast, leading to ghost reporting on stale/empty IDs.| Fixed |	Resolved	Added sys.exit(1) in ingest_logic.py if no files are found to halt the pipeline immediately.
|EC-027|	AI rewrote ingest_logic.py without discussing, accidentally deleting the core feature extraction logic. This caused hollow database records.	| Open |	AI must request the original ingestion logic to safely merge deduplication/batching without destroying the core engine.
|EC-028|	AI created unauthorized directory structures (inbox) without architectural approval, breaking the user's existing workflow. | Fixed | Resolved	AI must adapt code to the user's established directory paths; no new folders will be created without explicit permission.
|EC-029|	AI conflated Sandbox development with Local Deployment.	| Fixed | Resolved	Established "Local-Verification Gate": No task marked complete without local execution.
|EC-030|	AI provided code snippets instead of full files, forcing manual user splicing.	| Fixed | Resolved	Hard Rule Established: Any code modification beyond a trivial 1-2 line change MUST be output as a complete, fully integrated file ready for copy/download
|EC-031|	AI assumed the database file was located in the root directory instead of the correct models subdirectory. | Fixed |	Resolved	Hard-coded DB_DIR path to target ...\models\ specifically for the auto-discovery scan.
|EC-032| NEVER ask to advance to the next phase until the Operator explicitly confirms the local deployment script has run successfully on their machine. | Fixed |
|EC-033|	AI attempted to dynamically map missing columns, violating canonical schema enforcement and masking upstream vendor data drift. | Fixed |	Resolved	Removed dynamic fallbacks. Implemented strict schema validation that fatally halts and alerts the Operator if exact column headers are missing.
|EC-034|	AI falsely attributed a KeyError to upstream vendor schema drift, ignoring the logical constraint that the vendor software had not been updated.| Fixed |
Resolved	Re-focused diagnostics on the internal mapping layer (ingest_manifest.json).
|EC-035|	AI failed to apply historical schema mapping lessons from the Evaluation phase to the Pattern Ingestion phase, causing redundant crashes.	| Fixed |Resolved	Re-establishing the global translation layer. Generating the exact ingest_manifest.json to bridge raw VantagePoint headers to the canonical database schema.
|EC-036|	AI experienced "Code Regression." A functional data-cleaning solution from Phase 2 was dropped when generating Phase 3 scripts from scratch, causing the user to troubleshoot a previously solved problem.	| Fixed |Resolved	Acknowledged LLM stateless limitation. The "Pre-Wash" layer is now permanently hardcoded into the Phase 3 architecture to ensure this specific regression cannot happen again.
|EC-037|	Script failed to apply manifest mapping despite correct logic; likely due to MANIFEST_PATH resolution mismatch.	Resolved	Implemented explicit MANIFEST_PATH verification in the script output. It will now print the absolute path it is attempting to load and the status of that file.
|EC-038| UPDATE: DATA INTEGRITY ENFORCEMENT |Rule: Aggregator must strictly isolate NaN outcomes.| Observation | Successful filtering of 1 integrity error during the 05-06-2026 run. | Prevention | Future aggregator runs must include an auto-audit report if error_count > 0 to notify the operator immediately of missing label records.
|EC-039| (NaN Handling): Aggregator now strictly filters NaN outcomes as data errors; added print alerts for visibility.| Fixed |
|EC-040| (Indentation): Fixed Python indentation error by providing monolithic code blocks rather than partial snippets.| Fixed |
|EC-041| (Import Path): Resolved ModuleNotFoundError by hard-injecting absolute sys.path to the project root in all sub-scripts. | Fixed |
|EC-042| (Integrity Purge): Identified 16 corrupt "Zombie" records (null anchor dates) and 30 orphaned records; purged zombies and backfilled orphans |Fixed |
|EC-043|	Metadata Oversight: AI failed to verify internal file headers against provided snippets, leading to a hallucinated version increment that missed the context of the user's uploaded aggregator.py v2.2. |	Fixed |	Rule Established: AI must explicitly acknowledge and echo the VERSION and CHANGELOG from the source file metadata before suggesting any modification.
|EC-044|	Dependency Desync: A regression test attempted to import a function (calculate_z_score) from a production file that had not yet been deployed, causing an ImportError.	| Fixed |	Rule Established: Testing scripts must remain self-contained or reference dedicated utility modules to avoid import errors before production code is updated.
|EC-045|	DataFrame Column Desync: A diagnostic script explicitly called for a dataframe column (confidence_score) that did not exist in the output, causing a KeyError crash.	|Fixed|	Rule Established: Diagnostic scripts must dynamically check df.columns to verify safe existing columns before attempting to print fields.
|EC-046|	Feature Normalization Desync: intelliscan.py calculated Euclidean distance on raw price data (absolute dollars) across assets, causing a massive feature scaling failure.	|Fixed |	Rule Established: Any multi-symbol pattern matching must enforce Percentage-Based Normalization in-memory before computing vector distance metrics.
|EC-047|	Directory Map Oversight: AI neglected to verify P_300_Directory_map.txt, issuing a backup command pointing to the project root instead of the designated models\ sub-directory.	| Fixed |	Rule Established: AI must explicitly verify the root and sub-directory paths in the provided Directory Map before proposing file system or PowerShell commands.
# ---

**7. Enhancement Log**

* Add file-by-file folder map for current P_300 implementation
* Add known-good examples for pattern instance labeling
* Add IntelliScan match scoring methodology
* Add project prompt library and repeatable startup macros
* **Build `verify_ingestion.py`:** Wraps the Verify Temp + Atomic Move + Log steps from Section 2.7's Write-Operation Transaction Safety subsection. Until built, the steps are performed manually using `inspect_catalog.py` and `inspect_labels.py` against the temp DB path.
* **Milestone 5 — Trade Management:** Build module that consumes Aggregator output and produces position-sizing recommendations. Required inputs: Confidence/Win-Rate (drives position size — e.g., 80% win rate → 2% risk; 60% win rate → 0.5% risk), Expected Horizon (5d/7d/10d return reliability), and Drawdown Threshold (worst-historical-analog-based hard stop). Risk-management style (fixed percentage, volatility-based trailing, time-based exits) to be selected before build.

# ---

**8. AI Workflows & Processes**

## 8.1 **Primary Workflow**

1. Execute the P_300 Bootstrap Handshake.
2. Read system architecture document and explicitly review the Error Log.
3. Perform Catalog Check-Out (Section 2.7).
4. Summarize current milestone and next approved task.
5. Load necessary source files.
6. Propose work in the current milestone only.
7. For write operations: copy master to `temp_working.db` and operate against the temp file.
8. Produce artifact or documented output.
9. Verify temp DB; on success atomically replace master; perform Catalog Check-In.
10. Update changelog / architecture if the system meaningfully changed.

## 8.2 **Documentation Workflow**

1. Try to place new documentation in this master document first.
2. Create separate files only if content is long, frequently updated, or reused across projects.
3. Add a reference link back into this document whenever a new file is created.

## 8.3 **Daily Pattern Analysis Workflow**

Refer to Section 2.6 for the full operational pipeline. The four-step sequence (Ingest → Archive → Match → Report) is the standard for all incoming VantagePoint CSV processing, in both single-file and batch modes.

 ## 8.4 Development Standards

# 8.4.1 P_300 Python Header Standard
Every Python script MUST contain the following header block at line 1.
```python
"""
FILE: [File Name]
VERSION: 1.1
DATE: 2026-05-06
DESCRIPTION: [Briefly describe the script's core purpose]
"""
# 8.4.2 Dynamic Pathing Protocol
Hardcoded database paths are prohibited. All database interactions must use the central utility:

Utility: python/utilities/db_utils.py

Method: get_latest_catalog()

Compliance: All new scripts must implement sys.path.append to locate db_utils.py dynamically if not in the same directory.
# ---

**9. Data Design**

**Source Truth Verification:** The primary data source is verified as catalog.db (Properties verified: Modified May 3, 2026, 12:10 AM - Refer image_0ad601.png). The current production database used by the Daily Pattern Analysis Workflow is `050326geminicatalog.db`.

## **Core Data Entities**

* **Symbol** — Ticker identifier, beginning with SPY
* **Pattern Instance** — Historical setup observation tied to a symbol/date
* **Pattern Feature** — Named feature value attached to a pattern instance
* **Forward Label** — 5d / 7d / 10d profitability classification per pattern instance
* **Match Result** — Similarity lookup result comparing a live candidate to historical instances (future)

## ---

## **9.1 Schema & Feature Map**

The canonical schema is defined by `models/050326geminicatalog.db`.

### **Canonical Schema (Production)**

* **symbols:** `symbol_id` (PK), `symbol` (TEXT)
* **pattern_instances:** `pattern_instance_id` (PK), `symbol_id`, `anchor_date`
* **pattern_features:** `pattern_feature_id` (PK), `pattern_instance_id`, `feature_name`, `feature_value`
* **forward_labels:** `forward_label_id` (PK), `pattern_instance_id`, `horizon_days`, `return_pct`, `is_profitable`

**Note:** ID-003 Resolved. The production schema above is the only source of truth.

### **Verified Production State (Direction A complete)**

* 391 pattern instances ingested
* 981 forward labels generated across 5-day, 7-day, and 10-day horizons
* Spot-check confirmed: pattern_instance_id 390 captured a -0.29% / -0.78% loss with `is_profitable = 0`; pattern_instance_id 394 captured a 5.00% / 7.55% gain with `is_profitable = 1`

# ---

**10. Testing & Validation**

## **10.1 Testing Approach**

* Validate source-file imports against known historical records
* Spot-check feature generation on selected dates
* Verify label calculations against manually computed forward returns
* Confirm database row counts and null handling at dataset edges
* Validate startup process by requiring architecture summary on new sessions
* Confirm Catalog Check-Out runs cleanly at session start
* Confirm Catalog Check-In delta matches expected row counts after each DB op
* Confirm temp DB verification succeeds before any atomic move to the master

## **10.2 Validation Checklist**

* Architecture document loaded at session start
* P_300 Bootstrap Handshake executed and Error Log verified
* Catalog Check-Out completed before any work
* Current milestone correctly stated
* SPY source file recognized correctly
* Feature logic version identified
* Forward-label windows verified
* No undocumented schema changes
* Catalog Check-In completed after any DB-touching operation
* For writes: Lock verified, temp DB used, temp verified, atomic move completed, row count + schema version logged

## **10.3 Known Issues / Limitations**

| Issue ID | Description | Severity | Workaround | Status |
| :---- | :---- | :---- | :---- | :---- |
| ID-001 | Context loss across new threads | High | Execute P_300 Bootstrap Handshake | Controlled |
| ID-002 | Exact P_300 file map not yet fully embedded | Medium | Add appendix in next revision | Open |
| ID-003 | Schema divergence between baseline and production | Medium | n/a | Resolved (canonical schema declared in Section 9.1) |
| ID-004 | `verify_ingestion.py` not yet built | Low | Manual verification with `inspect_catalog.py` + `inspect_labels.py` against temp DB | Open (tracked in Enhancement Log) |

# ---

**11. Daily Operations & Session Management**

## **11.1 Session Start Protocol**

At the beginning of each new session, the AI must explicitly:

1. Read this document fully.
2. Review **Section 6 (Error Corrections Log)** to ensure past mistakes are not repeated.
3. Perform **Catalog Check-Out** per Section 2.7 (verify `050326geminicatalog.db` opens cleanly and record pre-op row counts).
4. State current milestone.
5. State last completed work.
6. State approved next task.
7. Ask for clarification only if the next task is ambiguous.

## **11.2 Maintenance**

| Task | Frequency | Owner | Notes |
| :---- | :---- | :---- | :---- |
| Architecture review | Weekly or after major change | Anthony | Update milestone and file map |
| Startup prompt review | As needed | Anthony | Refine session consistency |
| Schema review | At each DB milestone | Anthony | Keep SQLite design current |
| Error log review | When issue repeats | Anthony | Promote repeats into permanent fixes |
| Catalog Check-Out / Check-In log review | After every DB op | Anthony | Confirm bracketing was honored |

## **11.3 Next Session Prompt**

**The Handshake Prompt:** Read P300_System_Architecture.md first. Next, explicitly review **Section 6 (Error Corrections Log)** to understand past failures and ensure you do not repeat errors that cause hallucination or drift. Perform the **Catalog Check-Out** (Section 2.7) on `050326geminicatalog.db`. Finally, summarize the current project status, identify the current milestone, restate the next approved objective, list any required reference files, and wait for confirmation or proceed only within those constraints. Treat the validated SPY-first POC as the default implementation path and flag any new parser, schema, workflow, or generalized approach as POC drift unless explicitly approved.

## **11.4 Mandatory Pre-Flight Audit**

Before providing any response containing code, script generation, or architectural changes, the AI MUST explicitly output the following audit block. If any item cannot be checked, the AI must halt and resolve the deficiency before proceeding.

### **P_300 PRE-FLIGHT AUDIT**

* [ ] **Artifact Complete:** Entire file/codeblock provided? (MUST be YES)
* [ ] **Path Resolved:** Dynamic pathing used (no hard-coded paths)? (MUST be YES)
* [ ] **Finality:** No requests for user audit/verification? (MUST be YES)
* [ ] **Schema Parity:** Data origin type included/handled? (MUST be YES)
* [ ] **Context Sync:** Filename resolved from *geminicatalog.db? (MUST be YES)

## **11.5 Daily Pattern Analysis Workflow (Operational Reference)**

Refer to Section 2.6 for full detail. Quick-reference sequence:

1. Drop one or many CSVs into `data\live\`.
2. Run `python\utilities\P_300-00_ingest.ps1` (Ingest — invokes Lock + Temp-DB write per Section 2.7).
3. Run `python\utilities\P_300_10_ArchiveCSV.ps1` (Archive to `data\processed\`).
4. Run `python\utilities\P_300_20_PatternMatch.ps1` (IntelliScan).
5. Run `python\utilities\P_300_50_ConReport.ps1` (Confidence Report — auto-detects newest IDs).
6. Perform **Catalog Check-In** per Section 2.7 to confirm row-count delta and log schema version.

If `.ps1` scripts fail to load due to ExecutionPolicy (see EC-015), run once per PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

# ---

**12. Troubleshooting & Support**

## **12.1 Common Issues**

### **Issue — AI forgets prior discussion**

* **Symptoms:** New thread starts with incorrect assumptions, generic responses, or drift.
* **Root Cause:** Session context was not reloaded, or the Error Log was ignored.
* **Solution:** Force the P_300 Bootstrap Handshake to anchor the session.
* **Prevention:** Use the startup protocol in every new thread.

### **Issue — Wrong milestone focus**

* **Symptoms:** Work begins on future tasks before current foundation is complete.
* **Root Cause:** No explicit milestone restatement at session start.
* **Solution:** Require milestone confirmation in the startup step.
* **Prevention:** Keep Section 1 and Section 5 updated.

### **Issue — PowerShell `.ps1` script blocked from running**

* **Symptoms:** "File ... cannot be loaded. The file ... is not digitally signed." Script returns no output and downstream Python args become empty.
* **Root Cause:** Default Windows PowerShell ExecutionPolicy blocks unsigned local scripts.
* **Solution:** Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once at the start of each PowerShell session.
* **Prevention:** Sign the workflow scripts long-term, or document the bypass requirement in the Daily Pattern Analysis Workflow operational checklist.

### **Issue — Aggregator returns 0 rows or stale data**

* **Symptoms:** Confidence report runs but reports no patterns, or reports old patterns from a prior batch.
* **Root Cause:** Catalog Check-In was skipped after ingest, so the aggregator queried an unverified state. Or, ingest failed silently and never inserted rows.
* **Solution:** Re-run Catalog Check-Out, verify pattern_instances row count, re-run ingest if needed, then Check-In.
* **Prevention:** Honor the Check-In / Check-Out bracketing rule on every operation.

### **Issue — Master DB shows partial or corrupted state after a failed write**

* **Symptoms:** Row counts mid-range; some tables updated, others not; schema queries return unexpected results after an interrupted ingest.
* **Root Cause:** A write was performed directly against the master DB instead of through `temp_working.db`. The Lock + Temp-DB + Atomic Move pattern was bypassed.
* **Solution:** Restore the master from the most recent verified backup. Re-run the ingest with the temp-DB pattern.
* **Prevention:** All write operations must target `temp_working.db` first; the master is only replaced via atomic move after verification passes.

## **12.2 Escalation Path**

| Level | Condition | Action |
| :---- | :---- | :---- |
| Self-correct | Minor drift | Restate architecture rule |
| Session reset | Repeated misunderstanding | Start new thread with P_300 Bootstrap Handshake |
| Documentation update | Repeat issue twice | Add permanent rule or example to this doc |
| System redesign | Architecture no longer fits project | Open enhancement item and revise structure |

# ---

**13. Appendices**

## **Appendix A — Glossary**

| Term | Definition |
| :---- | :---- |
| Carryover Summary | Compact project-state summary copied into a new thread |
| P_300 Bootstrap Handshake | Mandatory read-first startup process that includes Error Log review and Catalog Check-Out |
| Pattern Label | Outcome classification based on future price movement |
| Grid Match | Similarity match between a current pattern and historical analog |
| Catalog Check-Out | Pre-operation read/inspection of the SQLite catalog |
| Catalog Check-In | Post-operation validation of the SQLite catalog |
| Direction A | Real-data labeling milestone (Complete) |
| Direction B | IntelliScan similarity engine upgrade milestone (In Progress) |
| Temp-DB Pattern | Lock + Copy-to-Temp + Verify + Atomic Move sequence applied to all writes against the canonical DB |

## **Appendix B — Related Documentation**

| Document | Purpose |
| :---- | :---- |
| README.md | Hub-wide foundation architecture context |
| UNIVERSAL_PROJECT_TEMPLATE_v1_1.md | Template source for this system document |
| Trading_Projects_Folder_Architecture.md | Hub environment and standards reference |
| Future P300 prompt file | Startup prompt and session control |

## **Appendix C — Configuration Reference**

| Item | Value |
| :---- | :---- |
| Shared Python Environment | p140 |
| Python Path | C:\Users\Trader\.conda\envs\p140\python.exe |
| Local LLM Endpoint | http://localhost:1234/v1 |
| Local LLM Model Reference | deepseek-r1-distill-qwen-14b (daily driver) / qwen2.5-coder-32b-instruct (batch) / llama-4-scout-17b-16e-instruct (long context) |
| Production Catalog DB | C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\050326geminicatalog.db |
| Working Temp DB | C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\models\temp_working.db |
| PowerShell ExecutionPolicy (per session) | Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass |

## **Appendix D — Document Control**

| Field | Value |
| :---- | :---- |
| Document Owner | Anthony Zoppi |
| Classification | Internal |
| Template Version | UNIVERSAL_PROJECT_TEMPLATE_v1_1 |
| Review Schedule | Weekly during active build or after major architecture change |

## **Appendix E — Working Folder Map**

* python/ingest/
  * ingest_vp_catalog.py
  * batch_ingest.py
* python/feature_engineering/
* python/matching/
  * intelliscan.py
* python/labeling/
* python/reporting/
  * aggregator.py (smart, auto-ID-detection)
* python/utilities/
  * P_300-00_ingest.ps1
  * P_300_10_ArchiveCSV.ps1
  * P_300_20_PatternMatch.ps1
  * P_300_50_ConReport.ps1
  * inspect_catalog.py
  * inspect_labels.py
  * resolve_catalog.ps1
  * verify_ingestion.py (planned)
* data/live/
* data/raw/
* data/processed/
* data/historical/
* data/reference/
* outputs/reports/
* outputs/charts/
* outputs/exports/
* docs/architecture/
* docs/prompts/
* docs/notes/
* docs/validation/
* models/catalog.db
* models/050326geminicatalog.db
* models/temp_working.db (transient — exists only during active write operations)
* models/schema/

## **Appendix F — Prompt Library Entry**

**P_300 Bootstrap Handshake:** Read the architecture first. Explicitly review the Error Log (Section 6) to prevent repeating past drift/hallucinations. Perform Catalog Check-Out (Section 2.7). Summarize milestone status and next task, confirm measurable objectives and replacement-file workflow, then wait or proceed only within constraints.

## **Addendum - Versioning Convention**

* Use major.minor.patch for the architecture file.
* Major changes represent structural or architectural redesigns.
* Minor changes represent meaningful but non-breaking additions.
* Patch changes represent small clarifications, examples, and rule additions.
* Keep small documentation updates in the patch level until a broader workflow change justifies a minor bump.

## **Appendix G — Historical Threads**

| Thread | Description |
| :---- | :---- |
| Thread Link 1 | Initial architecture design and discussion |
| Thread Link 2 | Decision to use SQLite as the primary database |
| Thread Link 3 | Implementation of feature extraction process |
| Thread Link 4 | Handling of data cleaning and standardization |
| Thread Link 5 (Gemini, 2026-05-03) | Direction A completion, Daily Pattern Analysis Workflow finalization, Check-In/Check-Out requirement, Database Integrity Protocol additions |

## **Appendix H — Trade Management**

**TRADING LOGIC & RULES (P_030):**

* **BUY Requirement:** 100% Buy rating across 20, 50, 100, and 200-day Moving Averages.
* **Risk Management:** Standard Risk Budget = $525 (1.5% of $35k).
* **Size Penalty:** You need to apply 200MA Penalty sizing if price is below the 200MA.
* **Liquidity Floor:** Spread ≤ 10%, OI ≥ 150.

**P_030 RESPONSE FORMAT:**

* You need to always filter new mentions through "Founder-led" vs. "Manager-led" criteria.
* You need to provide a "Rolling Summary" table of active positions ($LPTH, $NESR, $PHM).
* You need to remind me to "Flush the noise" when macro events create volatility.

**Milestone 5 — Trade Management Module (Planned):**

The Trade Management module will consume Aggregator output from the Daily Pattern Analysis Workflow and produce position-sizing recommendations. Three required inputs from the aggregator results:

| Input | Purpose | Example Mapping |
| :---- | :---- | :---- |
| Confidence / Win-Rate | Position size driver | 80% win rate → 2% risk; 60% win rate → 0.5% risk |
| Expected Horizon | Hold-period selection | Pick the day (5d / 7d / 10d) with the most reliable historical return |
| Drawdown Threshold | Hard stop-loss placement | Set stop based on the worst historical analog's drawdown |

Risk-management style (fixed percentage stop-loss, volatility-based trailing stop, or time-based exits) to be selected before build begins.
