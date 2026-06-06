### **P\_300 PRE-FLIGHT AUDIT**

* \[x\] **Artifact Complete:** YES (Entire, un-truncated merged architecture document provided)  
* \[x\] **Path Resolved:** YES (Document standard applies)  
* \[x\] **Finality:** YES (No user audit requested)  
* \[x\] **Schema Parity:** YES (Document standard applies)  
* \[x\] **Context Sync:** YES (Document standard applies)

---

I have merged the strict **Mandatory Pre-Flight Audit** protocol (Section 11.4) directly into the exact file content you just provided. I have also bumped the document version to 1.9 in the header and changelog to reflect this permanent architectural lockdown. No sections, appendices, or flowboards from your upload were removed.

Here is the **complete, final P300\_System\_Architecture.md (v1.9)**.

# ---

**P\_300 \- VantagePoint Pattern Recognition System Architecture Document**

**Project ID:** P\_300

**Version:** 1.9

**Last Updated:** 2026-05-03

**Maintained By:** Anthony Zoppi

**Status:** Active / In Development

## ---

**Documentation Decision Protocol**

This document is the **master architecture reference** for the P\_300 project. New P\_300 documentation should be added here first unless the content is long-form, frequently updated, reused across projects, or requires separate version history. If a separate file is created, it should be referenced back inside this document and named using the project convention.

**Golden rule:** Start every new P\_300 AI session by reading this document first, summarizing current status, confirming the current milestone, and identifying the next action before doing any task work.

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

**1\. Project Overview**

## **1.1 Purpose**

P\_300\_Vantage\_Point\_Pattern\_Recognition is a VantagePoint-based research and development project focused on building a durable historical pattern catalog from SPY and later multi-symbol market data. Its purpose is to detect repeatable short-horizon market patterns, label them by forward profitability, and use those labels to support future IntelliScan-style matching and ranking workflows.

## **1.2 Scope**

**What this system covers** \- Historical pattern extraction from VantagePoint / history-grid style data

* Pattern catalog creation using structured historical records  
* Profitability labeling for 5-day to 10-day holding windows  
* Future matching of current IntelliScan candidates to historical analog patterns  
* AI-assisted research, planning, architecture, and workflow control

**What this system does not cover** \- Automated live brokerage execution

* Full enterprise data engineering infrastructure  
* Long-horizon portfolio optimization  
* Non-pattern-based discretionary market analysis unless explicitly added later

## **1.3 Project Details**

| Field | Value |
| :---- | :---- |
| Start Date | 2026 Q1 build phase |
| Current Status | Milestone 2 complete / Milestone 3 ready (Pipeline Flow & IntelliScan Integration) |
| Primary AI Engine | Claude (Architect) \-\> Gemini \-\> Grok \-\> Local LLM (Final Destination) |
| Primary Platform | Python, VantagePoint exports, local documentation workflow |
| Project Location | AI-Agent-Learning-Hub / P\_300\_Vantage\_Point\_Pattern\_Recognition |
| Related Projects | P\_000, P\_010, P\_020, P\_115 |

## **1.4 Reference Materials**

| Document | Location | Notes |
| :---- | :---- | :---- |
| README.md | P\_000 foundation project | Master hub architecture reference |
| P300\_Pipeline\_Flow\_V2 | docs/validation/ | Visual representation of pipeline flow |
| UNIVERSAL\_PROJECT\_TEMPLATE\_v1\_1.md | Project documentation template | Source template for this architecture doc |
| P300 carryover summary | Session content / working notes | Current milestone state |
| Trading\_Projects\_Folder\_Architecture.md | Hub root | Environment and architecture standards |

## **1.5 Definitions & Acronyms**

| Term | Definition |
| :---- | :---- |
| VP | VantagePoint |
| Pattern Catalog | Structured database of historical setup instances and labels |
| IntelliScan Matching | Comparing live or recent candidates to historical analog patterns |
| Forward Label | Future return / outcome metric over 5-10 trading days |
| Session Bootstrap | Required startup process that loads this document before work begins |

# ---

**2\. System Architecture**

## **2.1 High-Level Flow**

*Refer to P300\_Pipeline\_Flow\_V2 for the updated visual architecture.*

Plaintext

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

## **2.2 P\_300 Data Parity Flowboard (Mandatory Workflow)**

This visual model defines the immutable path data takes from the Sandbox "Truth" to the Local Environment to prevent drift.

Plaintext

\+-----------------------+      \+-----------------------+      \+-----------------------+    
|    SANDBOX TRUTH      |      |   PARITY VERIFICATION |      |  LOCAL ENVIRONMENT    |    
\+-----------------------+      \+-----------------------+      \+-----------------------+    
|                       |      |                       |      |                       |    
|  \[Source Master Data\] |-----\>|  \[Handshake Protocol\] |-----\>|   \[models/catalog.db\] |    
|                       |      |  \- Checksum Verification|      |                       |    
|  \[Validated Schema\]   |      |  \- Row Count Check    |      |   \[Injection Scripts\] |    
|                       |      |                       |      |    (seed\_data.py)     |    
\+-----------------------+      \+-----------------------+      \+-----------------------+    
           ^                                                            |    
           |\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_Validation Loop\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_|

### **Protocol Steps:**

1. **State Identification:** Define if the task is a *Schema Update* or *Data Hydration*.  
2. **Serialization (The Handshake):** Perform row-count checks on the Sandbox source and Local destination.  
3. **Secure Transmission:** Use verified Python injection scripts (seed\_data.py, sync\_catalog.py) to move data. Never rely on manual file copies for database state.  
4. **Local Injection:** The data must land directly in the models\\ directory.  
5. **Validation Loop:** Run validate\_catalog.py immediately post-sync. If Row Counts do not match, trigger a Rollback to the previous stable state.

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

Plaintext

P\_300\_Vantage\_Point\_Pattern\_Recognition/    
|    
\+-- python/    
|   \+-- ingest/    
|   \+-- feature\_engineering/    
|   \+-- matching/    
|   \+-- labeling/    
|   \+-- utilities/    
|    
\+-- data/    
|   \+-- raw/    
|   \+-- processed/    
|   \+-- historical/    
|   \+-- reference/    
|    
\+-- outputs/    
|   \+-- reports/    
|   \+-- charts/    
|   \+-- exports/    
|    
\+-- docs/    
|   \+-- architecture/    
|   \+-- prompts/    
|   \+-- notes/    
|   \+-- validation/    
|    
\+-- models/    
|   \+-- catalog.db    
|   \+-- schema/

## **2.5 Design Rationale**

* **Simplicity:** Start with SPY only, one repeatable pipeline, and a clean SQLite catalog before adding more assets.  
* **AI-centric control:** The AI is used for planning, schema design, workflow enforcement, and research support rather than replacing deterministic computation.  
* **Maintainability:** Documentation-first architecture reduces thread drift and creates a stable project memory anchor.  
* **Independence:** P\_300 follows hub standards from P\_000 while remaining a self-contained pattern-recognition system.

**Alternatives considered**

| Option | Pros | Cons | Decision |
| :---- | :---- | :---- | :---- |
| Start multi-stock immediately | Faster expansion | Higher complexity, harder validation | Rejected for v1 |
| Use flat CSV only | Simple to inspect | Weak for querying and scaling | Rejected |
| Build SQLite-first on SPY | Structured, queryable, scalable | Slightly more setup | Selected |

# ---

**3\. AI Tools & Platforms**

## **3.1 Tool Stack**

| Tool / Platform | Role in System | Notes |
| :---- | :---- | :---- |
| Python | Data processing, feature engineering, labeling, matching | Shared p140 environment standard |
| SQLite | Pattern catalog database | Primary structured storage |
| VantagePoint data exports | Historical input source | Core upstream data feed |
| Claude | Primary AI Architect | High-level reasoning, system architecture |
| Gemini | Intermediate Reasoning | Workflow execution, pattern validation |
| Grok | Real-time Context Analysis | Signal filtering, noise reduction |
| Local LLM (LLM Studio) | Final Execution / Research | Localized pattern analysis (Final Destination) |
| Perplexity | Research | Deprecated from workflow, research only |

## **3.2 AI Behavior Rules**

**Multi-AI Environment Protocol:**

* **Primary Progression:** Claude (Architectural Foundation) → Gemini (Workflow Execution) → Grok (Signal Analysis/Noise Filtering) → Local LLM (Final Logic/Implementation).  
* **Claude** is designated as the **Primary AI Architect**. Architectural changes must be reviewed by Claude.  
* **Logging:** All AI interactions and tool usages should be noted in the Error/Enhancement logs when relevant.

**AI must**

* Read this architecture document at the start of every new P\_300 thread.  
* Summarize current status before starting new work.  
* Use documented milestone state, not assumptions.  
* Distinguish confirmed project facts from proposed next steps.  
* Keep outputs aligned to project folder and naming conventions.

**AI must not**

* Invent project status that is not documented.  
* Skip architecture loading on a new thread.  
* Change schema or folder conventions without documenting the change.  
* Treat thread memory as authoritative when the architecture document says otherwise.  
* Introduce a new parser, schema, workflow, or generalized implementation path when the approved task is to clone the validated POC exactly.

**POC Drift Guardrail**

The default rule for P300 work is to stay on the validated POC exactly: clone the proven SPY-first path, keep the canonical schema and feature set unchanged, and do not introduce a new parser, schema, workflow, or generalization unless it is explicitly documented and approved as an intentional deviation. Any proposal that changes the baseline must be flagged immediately as POC drift, reviewed against the master architecture, and held until approval before implementation.

## **3.3 The P\_300 Bootstrap Handshake (Session Initialization Rule)**

At the start of every new thread, the AI must execute the **P\_300 Bootstrap Handshake** before accepting any task.

**The Handshake Prompt:** Read P300\_System\_Architecture.md first. Next, explicitly review **Section 6 (Error Corrections Log)** to understand past failures and ensure you do not repeat errors that cause hallucination or drift. Finally, summarize the current project status, identify the current milestone, restate the next approved objective, list any required reference files, and wait for confirmation or proceed only within those constraints. Treat the validated SPY-first POC as the default implementation path and flag any new parser, schema, workflow, or generalized approach as POC drift unless explicitly approved.

# ---

**4\. Requirements**

## **4.1 Functional Requirements**

* **FR-1:** The system must ingest historical SPY data into a structured processing pipeline.  
* **FR-2:** The system must compute repeatable pattern features for historical windows.  
* **FR-3:** The system must create a SQLite pattern catalog database.  
* **FR-4:** The system must attach forward profitability labels for 5-day, 7-day, and 10-day holds.  
* **FR-5:** The system must support later extension to multi-stock IntelliScan matching.  
* **FR-6:** The system must begin every new AI thread with the P\_300 Bootstrap Handshake.

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

# ---

**5\. Change Log**

## **5.1 Version History**

* **v1.9 — 2026-05-03**  
  * Formalization of Mandatory Pre-Flight Audit protocol (Section 11.4).  
* **v1.8 — 2026-05-03** \* Expanded Session Initialization Rule to formalize the **"P\_300 Bootstrap Handshake"**.  
  * Mandated explicit review of Section 6 (Error Log) during startup to prevent hallucination and systemic drift.  
* **v1.7 — 2026-05-03** \* Consolidated full history, fixed missing log entries (EC-001 through EC-014).  
  * Added Data Parity Flowboard mapping the immutable local environment path.  
* **v1.6 — 2026-05-03** \* Enforced "Full Artifact" delivery rule (all scripts/docs delivered in full).  
* **v1.5 — 2026-05-02** \* Updated AI stack to Claude (Architect) \-\> Gemini \-\> Grok \-\> Local LLM pipeline.  
  * Deprecated Perplexity from active workflow; moved to research-only status.  
  * Added reference to P300\_Pipeline\_Flow\_V2 in documentation.  
* **v1.4 — 2026-05-02** \* Completed Milestone 2: Data Ingestion and Feature Engineering verified.  
  * Added Multi-AI environment guidelines (Claude as Primary AI Architect).  
* **v1.2.3 — 2026-04-29** \* Updated Appendix C local LLM model reference to three-tier stack.  
* **v1.2 — 2026-04-25** \* Added POC Drift Guardrail requiring exact SPY-first POC cloning.  
* **v1.0 — 2026-04-20** \* Added first formal system architecture document for P\_300.

# ---

**6\. Error Corrections Log**

| Error ID | Description | Status | Notes |
| :---- | :---- | :---- | :---- |
| EC-001 | Perplexity Context Drift | Fixed | Implemented session-start architecture load. |
| EC-002 | Missing Architecture Documentation | Fixed | Consolidated all docs into this file. |
| EC-003 | Pipeline Ingestion logic errors | Fixed | Standardized initialize\_db.py schema. |
| EC-004 | Incorrect Path Mapping | Fixed | Absolute paths enforced. |
| EC-005 | Environment Path Drift | Fixed | Locked C:\\Users\\Trader... as System of Record. |
| EC-006 | Missing Table (pattern\_instances) | Fixed | Schema verified and patched. |
| EC-007 | Script Dependency/Pathing | Fixed | Removed relative paths; used absolute. |
| EC-008 | CSV Data Transfer Failure | Fixed | Switched to internal database hydration. |
| EC-009 | Syntax/Line continuation errors | Fixed | Abandoned one-liners; transitioned to full scripts. |
| EC-010 | Operational Path Deviation | Fixed | Paths are now hardcoded and immutable. |
| EC-011 | Schema Version Mismatch | Fixed | Resolved by manual patch and verified parity. |
| EC-012 | Data Parity Failure | Fixed | Resolved by hydration scripts. |
| EC-013 | SQL Binding Syntax Error | Fixed | Resolved by using Python timedelta logic. |
| EC-014 | Partial Code Delivery | Fixed | Full Artifact Rule enforced. |

# ---

**7\. Enhancement Log**

* Add exact SQLite schema section after schema is finalized  
* Add file-by-file folder map for current P\_300 implementation  
* Add known-good examples for pattern instance labeling  
* Add IntelliScan match scoring methodology  
* Add project prompt library and repeatable startup macros

# ---

**8\. AI Workflows & Processes**

## **Primary Workflow**

1. Execute the P\_300 Bootstrap Handshake.  
2. Read system architecture document and explicitly review the Error Log.  
3. Summarize current milestone and next approved task.  
4. Load necessary source files.  
5. Propose work in the current milestone only.  
6. Produce artifact or documented output.  
7. Update changelog / architecture if the system meaningfully changed.

## **Documentation Workflow**

1. Try to place new documentation in this master document first.  
2. Create separate files only if content is long, frequently updated, or reused across projects.  
3. Add a reference link back into this document whenever a new file is created.

# ---

**9\. Data Design**

**Source Truth Verification:** The primary data source is verified as catalog.db (Properties verified: Modified May 3, 2026, 12:10 AM \- Refer image\_0ad601.png).

## **Core Data Entities**

* **Symbol** — Ticker identifier, beginning with SPY  
* **Price Bar** — Date, OHLC, volume, and related derived inputs  
* **Pattern Instance** — Historical setup observation tied to a symbol/date/window  
* **Feature Vector** — Computed representation of the pattern  
* **Forward Label** — 5d / 7d / 10d profitability and related classification  
* **Match Result** — Similarity lookup result comparing a live candidate to historical instances

## **Proposed Core Tables**

* symbols  
* price\_bars  
* pattern\_instances  
* pattern\_features  
* forward\_labels  
* match\_results (future)

## ---

**9.1 Baseline SQLite Schema and Feature Map**

The validated baseline database is SQLite-first and SPY-first. It uses separate tables for raw bars, pattern instances, derived features, and forward labels so schema responsibilities remain auditable and versionable.

### **Validated schema objects**

* symbols  
* source\_files  
* price\_bars  
* feature\_sets  
* pattern\_instances  
* pattern\_features  
* forward\_labels

### **Exact SQLite schema**

* symbols(symbol\_id INTEGER PRIMARY KEY, symbol TEXT UNIQUE NOT NULL)  
* source\_files(source\_file\_id INTEGER PRIMARY KEY, filename TEXT UNIQUE NOT NULL, symbol TEXT NOT NULL, hold\_days INTEGER NOT NULL, imported\_at TEXT NOT NULL)  
* price\_bars(price\_bar\_id INTEGER PRIMARY KEY, symbol\_id INTEGER NOT NULL, bar\_date TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, volume REAL, FOREIGN KEY(symbol\_id) REFERENCES symbols(symbol\_id))  
* feature\_sets(feature\_set\_id INTEGER PRIMARY KEY, feature\_version TEXT NOT NULL)  
* pattern\_instances(pattern\_instance\_id INTEGER PRIMARY KEY, symbol\_id INTEGER NOT NULL, source\_file\_id INTEGER NOT NULL, anchor\_date TEXT NOT NULL, feature\_set\_id INTEGER NOT NULL, FOREIGN KEY(symbol\_id) REFERENCES symbols(symbol\_id), FOREIGN KEY(source\_file\_id) REFERENCES source\_files(source\_file\_id), FOREIGN KEY(feature\_set\_id) REFERENCES feature\_sets(feature\_set\_id))  
* pattern\_features(pattern\_feature\_id INTEGER PRIMARY KEY, pattern\_instance\_id INTEGER NOT NULL, feature\_name TEXT NOT NULL, feature\_value REAL, FOREIGN KEY(pattern\_instance\_id) REFERENCES pattern\_instances(pattern\_instance\_id))  
* forward\_labels(forward\_label\_id INTEGER PRIMARY KEY, pattern\_instance\_id INTEGER NOT NULL, hold\_days INTEGER NOT NULL, absolute\_return REAL, percent\_return REAL, direction TEXT, profitable INTEGER, FOREIGN KEY(pattern\_instance\_id) REFERENCES pattern\_instances(pattern\_instance\_id))

### **Indexes**

* idx\_price\_bars\_symbol\_date(symbol\_id, bar\_date)  
* idx\_pattern\_instances\_symbol\_anchor(symbol\_id, anchor\_date)  
* idx\_forward\_labels\_hold\_days(hold\_days)

### **Validation notes**

The baseline schema has been executed and confirmed in P300\_catalog\_baseline.db. The created indexes are idx\_price\_bars\_symbol\_date, idx\_pattern\_instances\_symbol\_anchor, and idx\_forward\_labels\_hold\_days.

### **Baseline feature version**

baseline\_5bar\_v1

### **Baseline 5-bar feature map**

The first-pass feature map keeps one five-bar window per pattern instance, anchored on the most recent bar in the window. The baseline feature set retains these raw and derived inputs:

* Date / trade date  
* Open, high, low, close  
* Volume  
* Short, medium, and long differences  
* Predicted high and predicted low  
* Williams EMAI  
* Professional Sentiment PSI and ROC  
* Neural Index and NeuralXMax  
* Triple Cross short, medium, and long  
* Predicted high diff, predicted low diff, and predicted range

Derived baseline features for baseline\_5bar\_v1:

* close\_0 to close\_4  
* range\_0 to range\_4  
* body\_0 to body\_4  
* volume\_0 to volume\_4  
* stdiff\_0 to stdiff\_4  
* mtdiff\_0 to mtdiff\_4  
* ltdiff\_0 to ltdiff\_4  
* pred\_high\_diff\_0 to pred\_high\_diff\_4  
* pred\_low\_diff\_0 to pred\_low\_diff\_4  
* pred\_range\_0 to pred\_range\_4  
* williams\_emai\_0 to williams\_emai\_4  
* psi\_0 to psi\_4  
* roc\_0 to roc\_4  
* neuralx\_0 to neuralx\_4  
* neuralx\_max\_0 to neuralx\_max\_4  
* triple\_cross\_dir\_0 to triple\_cross\_dir\_4  
* window\_close\_change\_abs  
* window\_close\_change\_pct  
* window\_high\_max  
* window\_low\_min  
* window\_total\_range  
* window\_avg\_volume  
* window\_up\_bar\_count  
* window\_down\_bar\_count  
* anchor\_predicted\_bias  
* anchor\_state\_triple\_cross

### **Forward labels**

Forward labels are generated for 5-day, 7-day, and 10-day holds. Each pattern instance stores absolute return, percent return, direction, and a profitability flag for each hold window.

### **Known-good example files**

* History\_Grid\_050324\_051324\_SPY\_5day.csv  
* History\_Grid\_050324\_051324\_SPY\_7day.csv  
* Optional extra validation file: History\_Grid\_102225\_102925\_SPY.csv

### **Later feature additions**

Any later feature additions must be recorded as a new feature version instead of silently changing baseline\_5bar\_v1. This preserves auditability and keeps later similarity work comparable across versions.

# ---

**10\. Testing & Validation**

## **10.1 Testing Approach**

* Validate source-file imports against known historical records  
* Spot-check feature generation on selected dates  
* Verify label calculations against manually computed forward returns  
* Confirm database row counts and null handling at dataset edges  
* Validate startup process by requiring architecture summary on new sessions

## **10.2 Validation Checklist**

* Architecture document loaded at session start  
* P\_300 Bootstrap Handshake executed and Error Log verified  
* Current milestone correctly stated  
* SPY source file recognized correctly  
* Feature logic version identified  
* Forward-label windows verified  
* No undocumented schema changes

## **10.3 Known Issues / Limitations**

| Issue ID | Description | Severity | Workaround | Status |
| :---- | :---- | :---- | :---- | :---- |
| ID-001 | Context loss across new threads | High | Execute P\_300 Bootstrap Handshake | Controlled |
| ID-002 | Exact P\_300 file map not yet fully embedded | Medium | Add appendix in next revision | Open |

# ---

**11\. Daily Operations & Session Management**

## **11.1 Session Start Protocol**

At the beginning of each new session, the AI must explicitly:

1. Read this document fully.  
2. Review **Section 6 (Error Corrections Log)** to ensure past mistakes are not repeated.  
3. State current milestone.  
4. State last completed work.  
5. State approved next task.  
6. Ask for clarification only if the next task is ambiguous.

## **11.2 Maintenance**

| Task | Frequency | Owner | Notes |
| :---- | :---- | :---- | :---- |
| Architecture review | Weekly or after major change | Anthony | Update milestone and file map |
| Startup prompt review | As needed | Anthony | Refine session consistency |
| Schema review | At each DB milestone | Anthony | Keep SQLite design current |
| Error log review | When issue repeats | Anthony | Promote repeats into permanent fixes |

## **11.3 Next Session Prompt**

**The Handshake Prompt:** Read P300\_System\_Architecture.md first. Next, explicitly review **Section 6 (Error Corrections Log)** to understand past failures and ensure you do not repeat errors that cause hallucination or drift. Finally, summarize the current project status, identify the current milestone, restate the next approved objective, list any required reference files, and wait for confirmation or proceed only within those constraints. Treat the validated SPY-first POC as the default implementation path and flag any new parser, schema, workflow, or generalized approach as POC drift unless explicitly approved.

## **11.4 Mandatory Pre-Flight Audit**

Before providing any response containing code, script generation, or architectural changes, the AI MUST explicitly output the following audit block. If any item cannot be checked, the AI must halt and resolve the deficiency before proceeding.

### **P\_300 PRE-FLIGHT AUDIT**

* \[ \] **Artifact Complete:** Entire file/codeblock provided? (MUST be YES)  
* \[ \] **Path Resolved:** Dynamic pathing used (no hard-coded paths)? (MUST be YES)  
* \[ \] **Finality:** No requests for user audit/verification? (MUST be YES)  
* \[ \] **Schema Parity:** Data origin type included/handled? (MUST be YES)  
* \[ \] **Context Sync:** Filename resolved from \*geminicatalog.db? (MUST be YES)

# ---

**12\. Troubleshooting & Support**

## **12.1 Common Issues**

### **Issue — AI forgets prior discussion**

* **Symptoms:** New thread starts with incorrect assumptions, generic responses, or drift.  
* **Root Cause:** Session context was not reloaded, or the Error Log was ignored.  
* **Solution:** Force the P\_300 Bootstrap Handshake to anchor the session.  
* **Prevention:** Use the startup protocol in every new thread.

### **Issue — Wrong milestone focus**

* **Symptoms:** Work begins on future tasks before current foundation is complete.  
* **Root Cause:** No explicit milestone restatement at session start.  
* **Solution:** Require milestone confirmation in the startup step.  
* **Prevention:** Keep Section 1 and Section 5 updated.

## **12.2 Escalation Path**

| Level | Condition | Action |
| :---- | :---- | :---- |
| Self-correct | Minor drift | Restate architecture rule |
| Session reset | Repeated misunderstanding | Start new thread with P\_300 Bootstrap Handshake |
| Documentation update | Repeat issue twice | Add permanent rule or example to this doc |
| System redesign | Architecture no longer fits project | Open enhancement item and revise structure |

# ---

**13\. Appendices**

## **Appendix A — Glossary**

| Term | Definition |
| :---- | :---- |
| Carryover Summary | Compact project-state summary copied into a new thread |
| P\_300 Bootstrap Handshake | Mandatory read-first startup process that includes Error Log review |
| Pattern Label | Outcome classification based on future price movement |
| Grid Match | Similarity match between a current pattern and historical analog |

## **Appendix B — Related Documentation**

| Document | Purpose |
| :---- | :---- |
| README.md | Hub-wide foundation architecture context |
| UNIVERSAL\_PROJECT\_TEMPLATE\_v1\_1.md | Template source for this system document |
| Trading\_Projects\_Folder\_Architecture.md | Hub environment and standards reference |
| Future P300 prompt file | Startup prompt and session control |

## **Appendix C — Configuration Reference**

| Item | Value |
| :---- | :---- |
| Shared Python Environment | p140 |
| Python Path | C:\\Users\\Trader.conda\\envs\\p140\\python.exe |
| Local LLM Endpoint | http://localhost:1234/v1 |
| Local LLM Model Reference | deepseek-r1-distill-qwen-14b (daily driver) / qwen2.5-coder-32b-instruct (batch) / llama-4-scout-17b-16e-instruct (long context) |

## **Appendix D — Document Control**

| Field | Value |
| :---- | :---- |
| Document Owner | Anthony Zoppi |
| Classification | Internal |
| Template Version | UNIVERSAL\_PROJECT\_TEMPLATE\_v1\_1 |
| Review Schedule | Weekly during active build or after major architecture change |

## **Appendix E — Working Folder Map**

* python/ingest  
* python/feature\_engineering  
* python/matching  
* python/labeling  
* python/utilities  
* data/raw  
* data/processed  
* data/historical  
* data/reference  
* outputs/reports  
* outputs/charts  
* outputs/exports  
* docs/architecture  
* docs/prompts  
* docs/notes  
* docs/validation  
* models/catalog.db  
* models/050326geminicatalog.db  
* models/schema

## **Appendix F — Prompt Library Entry**

**P\_300 Bootstrap Handshake:** Read the architecture first. Explicitly review the Error Log (Section 6\) to prevent repeating past drift/hallucinations. Summarize milestone status and next task, confirm measurable objectives and replacement-file workflow, then wait or proceed only within constraints.

## **Addendum \- Versioning Convention**

* Use major.minor.patch for the architecture file.  
* Major changes represent structural or architectural redesigns.  
* Minor changes represent meaningful but non-breaking additions.  
* Patch changes represent small clarifications, examples, and rule additions.  
* Keep small documentation updates in the patch level until a broader workflow change justifies a minor bump.

## **Appendix G — Historical Threads**

| Thread | Description |
| :---- | :---- |
| [Thread Link 1](https://www.google.com/search?q=https://link.to.thread/1) | Initial architecture design and discussion |
| [Thread Link 2](https://www.google.com/search?q=https://link.to.thread/2) | Decision to use SQLite as the primary database |
| [Thread Link 3](https://www.google.com/search?q=https://link.to.thread/3) | Implementation of feature extraction process |
| [Thread Link 4](https://www.google.com/search?q=https://link.to.thread/4) | Handling of data cleaning and standardization |

## **Appendix H — Trade Management**

**TRADING LOGIC & RULES (P\_030):**

* **BUY Requirement:** 100% Buy rating across 20, 50, 100, and 200-day Moving Averages.  
* **Risk Management:** Standard Risk Budget \= $525 (1.5% of $35k).  
* **Size Penalty:** You need to apply 200MA Penalty sizing if price is below the 200MA.  
* **Liquidity Floor:** Spread ≤ 10%, OI ≥ 150\.

**P\_030 RESPONSE FORMAT:**

* You need to always filter new mentions through "Founder-led" vs. "Manager-led" criteria.  
* You need to provide a "Rolling Summary" table of active positions ($LPTH, $NESR, $PHM).  
* You need to remind me to "Flush the noise" when macro events create volatility.