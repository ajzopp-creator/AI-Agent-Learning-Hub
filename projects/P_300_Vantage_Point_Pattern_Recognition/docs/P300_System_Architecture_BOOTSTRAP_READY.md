# P_300 - VantagePoint Pattern Recognition System Architecture Document

**Project ID:** P_300  
**Version:** 1.1  
**Last Updated:** 2026-04-20  
**Maintained By:** Anthony Zoppi  
**Status:** Active / In Development

---

## Documentation Decision Protocol

This document is the **master architecture reference** for the P_300 project. New P_300 documentation should be added here first unless the content is long-form, frequently updated, reused across projects, or requires separate version history. If a separate file is created, it should be referenced back inside this document and named using the project convention. [file:39]

**Golden rule:** Start every new P_300 AI session by reading this document first, summarizing current status, confirming the current milestone, and identifying the next action before doing any task work. [file:39]

---

## Table of Contents

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

---

# 1. Project Overview

## 1.1 Purpose

P_300_Vantage_Point_Pattern_Recognition is a VantagePoint-based research and development project focused on building a durable historical pattern catalog from SPY and later multi-symbol market data. Its purpose is to detect repeatable short-horizon market patterns, label them by forward profitability, and use those labels to support future IntelliScan-style matching and ranking workflows. [file:37]

## 1.2 Scope

**What this system covers**
- Historical pattern extraction from VantagePoint / history-grid style data
- Pattern catalog creation using structured historical records
- Profitability labeling for 5-day to 10-day holding windows
- Future matching of current IntelliScan candidates to historical analog patterns
- AI-assisted research, planning, architecture, and workflow control

**What this system does not cover**
- Automated live brokerage execution
- Full enterprise data engineering infrastructure
- Long-horizon portfolio optimization
- Non-pattern-based discretionary market analysis unless explicitly added later

## 1.3 Project Details

| Field | Value |
|---|---|
| Start Date | 2026 Q1 build phase |
| Current Status | Milestone 1 complete / Milestone 2 ready |
| Primary AI Engine | Perplexity / Claude-style AI workflow |
| Primary Platform | Python, VantagePoint exports, local documentation workflow |
| Project Location | AI-Agent-Learning-Hub / P_300_Vantage_Point_Pattern_Recognition |
| Related Projects | P_000, P_010, P_020, P_115 |

## 1.4 Reference Materials

| Document | Location | Notes |
|---|---|---|
| README.md | P_000 foundation project | Master hub architecture reference |
| UNIVERSAL_PROJECT_TEMPLATE_v1_1.md | Project documentation template | Source template for this architecture doc |
| P300 carryover summary | Session content / working notes | Current milestone state |
| Trading_Projects_Folder_Architecture.md | Hub root | Environment and architecture standards |

## 1.5 Definitions & Acronyms

| Term | Definition |
|---|---|
| VP | VantagePoint |
| Pattern Catalog | Structured database of historical setup instances and labels |
| IntelliScan Matching | Comparing live or recent candidates to historical analog patterns |
| Forward Label | Future return / outcome metric over 5-10 trading days |
| Session Bootstrap | Required startup process that loads this document before work begins |

---

# 2. System Architecture

## 2.1 High-Level Flow

```text
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

**Description**  
The system ingests historical market data, normalizes it into structured pattern-ready records, computes repeatable feature sets, and stores each pattern instance in a database with forward outcome labels. That database becomes the foundation for later analog matching against new candidates and eventually multi-stock scanning. [file:39]

## 2.2 Core Components

### Component 1 — Data Input Layer
- **Responsibility:** Load SPY and future multi-symbol historical data from VantagePoint exports, spreadsheets, CSV, or transformed files.
- **Inputs:** History-grid exports, CSV files, Excel files, manually validated pattern examples.
- **Outputs:** Clean bar-level records and normalized data tables.
- **Tools Used:** Python, CSV/XLSX processing, hub folder structure.
- **Dependencies:** Consistent source files, file naming discipline, project folder conventions. [file:37]

### Component 2 — Pattern Engineering Layer
- **Responsibility:** Transform cleaned market records into comparable pattern feature vectors.
- **Inputs:** Clean historical OHLCV-style records and derived indicators.
- **Outputs:** Pattern signatures, window encodings, feature hashes, and similarity-ready representations.
- **Tools Used:** Python scripts, reusable utilities from hub architecture.
- **Dependencies:** Stable feature definitions and version-controlled logic.

### Component 3 — Catalog & Labeling Layer
- **Responsibility:** Persist pattern instances in SQLite and attach future profitability labels for defined hold periods.
- **Inputs:** Pattern vectors plus future return windows.
- **Outputs:** SQLite catalog tables, forward-return labels, win/loss classifications, hit-rate-ready records.
- **Tools Used:** Python, SQLite.
- **Dependencies:** Historical completeness, label definitions, schema control.

### Component 4 — Matching & Decision Support Layer
- **Responsibility:** Query historical analogs for current patterns and rank likely outcomes.
- **Inputs:** Current candidate pattern, pattern catalog, match criteria.
- **Outputs:** Ranked analogs, expected return tendencies, confidence context.
- **Tools Used:** Python, AI reasoning workflow, future IntelliScan integration.
- **Dependencies:** Pattern database quality, similarity rules, clean session context.

### Component 5 — AI Session Control Layer
- **Responsibility:** Maintain consistency across sessions using architecture documents, startup prompts, and documented rules.
- **Inputs:** This architecture document, project summaries, thread startup instructions.
- **Outputs:** Context continuity, reduced drift, more consistent task execution.
- **Tools Used:** Perplexity/Claude-style project workflows, markdown documentation.
- **Dependencies:** User discipline to load architecture first every session. [file:39]

## 2.3 System Decomposition

```text
P_300_Vantage_Point_Pattern_Recognition/
|
+-- python/
|   +-- ingest/
|   +-- feature_engineering/
|   +-- matching/
|   +-- labeling/
|   +-- utilities/
|
+-- data/
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
|   +-- schema/
```

## 2.4 Design Rationale

- **Simplicity:** Start with SPY only, one repeatable pipeline, and a clean SQLite catalog before adding more assets.
- **AI-centric control:** The AI is used for planning, schema design, workflow enforcement, and research support rather than replacing deterministic computation.
- **Maintainability:** Documentation-first architecture reduces thread drift and creates a stable project memory anchor. [file:39]
- **Independence:** P_300 follows hub standards from P_000 while remaining a self-contained pattern-recognition system. [file:37]

**Alternatives considered**

| Option | Pros | Cons | Decision |
|---|---|---|---|
| Start multi-stock immediately | Faster expansion | Higher complexity, harder validation | Rejected for v1 |
| Use flat CSV only | Simple to inspect | Weak for querying and scaling | Rejected |
| Build SQLite-first on SPY | Structured, queryable, scalable | Slightly more setup | Selected |

---

# 3. AI Tools & Platforms

## 3.1 Tool Stack

| Tool / Platform | Role in System | Notes |
|---|---|---|
| Python | Data processing, feature engineering, labeling, matching | Shared p140 environment standard from hub |
| SQLite | Pattern catalog database | Primary structured storage for v1 |
| VantagePoint data exports | Historical input source | Core upstream data feed |
| Perplexity / AI assistant | Planning, architecture, workflow reasoning | Used with startup protocol |
| LM Studio / local LLM | Optional privacy-first experimentation | Hub-supported reference capability |

## 3.2 AI Behavior Rules

**AI must**
- Read this architecture document at the start of every new P_300 thread. [file:39]
- Summarize current status before starting new work. [file:39]
- Use documented milestone state, not assumptions.
- Distinguish confirmed project facts from proposed next steps.
- Keep outputs aligned to project folder and naming conventions. [file:37]

**AI must not**
- Invent project status that is not documented.
- Skip architecture loading on a new thread.
- Change schema or folder conventions without documenting the change.
- Treat thread memory as authoritative when the architecture document says otherwise.

## 3.3 Session Initialization Rule

At the start of each new thread, use the following startup instruction:

> Read `P300_System_Architecture.md` first. Summarize current project status, identify current milestone, restate the next approved objective, list any required reference files, and wait for confirmation or proceed only within those constraints.

---

# 4. Requirements

## 4.1 Functional Requirements

- **FR-1:** The system must ingest historical SPY data into a structured processing pipeline.
- **FR-2:** The system must compute repeatable pattern features for historical windows.
- **FR-3:** The system must create a SQLite pattern catalog database.
- **FR-4:** The system must attach forward profitability labels for 5-day, 7-day, and 10-day holds.
- **FR-5:** The system must support later extension to multi-stock IntelliScan matching.
- **FR-6:** The system must begin every new AI thread with architecture-document bootstrap.

## 4.2 Non-Functional Requirements

- **NFR-1 Accuracy:** No fabricated pattern statistics or milestone claims.
- **NFR-2 Consistency:** Same startup process every new session.
- **NFR-3 Auditability:** Schema, rules, and milestone changes must be documented.
- **NFR-4 Maintainability:** Folder conventions and master-document links must remain stable.
- **NFR-5 Scalability:** SPY-first design must support later multi-symbol expansion.

## 4.3 Requirements Matrix

| ID | Description | Component | Status |
|---|---|---|---|
| FR-1 | Historical ingest | Data Input Layer | In progress |
| FR-2 | Feature engineering | Pattern Engineering Layer | Pending |
| FR-3 | SQLite catalog | Catalog & Labeling Layer | Pending |
| FR-4 | 5-10 day labels | Catalog & Labeling Layer | Pending |
| FR-5 | Multi-stock readiness | Matching Layer | Planned |
| FR-6 | Session bootstrap | AI Session Control Layer | Ready to implement |

---

# 5. Change Log

## Version History

### v1.0 — 2026-04-20
- Added first formal system architecture document for P_300
- Derived structure from universal project template
- Incorporated hub architecture role from P_000 README
- Added mandatory startup protocol for new threads

---

# 6. Error Corrections Log

| Error ID | Description | Status | Notes |
|---|---|---|---|
| EC-001 | Session drift due to missing prior discussion context in new thread | Open / mitigated | Resolved operationally by requiring architecture doc first
EC-002 | AI drift or repeat errors not logged into permanent document | High | Add to Error Corrections Log (Section 6) immediately | Open - now enforced |

---

# 7. Enhancement Log

- Add exact SQLite schema section after schema is finalized
- Add file-by-file folder map for current P_300 implementation
- Add known-good examples for pattern instance labeling
- Add IntelliScan match scoring methodology
- Add project prompt library and repeatable startup macros

---

# 8. AI Workflows & Processes

## Primary Workflow
1. Read system architecture document
2. Summarize current milestone and next approved task
3. Load necessary source files
4. Propose work in the current milestone only
5. Produce artifact or documented output
6. Update changelog / architecture if the system meaningfully changed

## Documentation Workflow
1. Try to place new documentation in this master document first. [file:39]
2. Create separate files only if content is long, frequently updated, or reused across projects. [file:39]
3. Add a reference link back into this document whenever a new file is created. [file:39]

---

# 9. Data Design

## Core Data Entities

- **Symbol** — Ticker identifier, beginning with SPY
- **Price Bar** — Date, OHLC, volume, and related derived inputs
- **Pattern Instance** — Historical setup observation tied to a symbol/date/window
- **Feature Vector** — Computed representation of the pattern
- **Forward Label** — 5d / 7d / 10d profitability and related classification
- **Match Result** — Similarity lookup result comparing a live candidate to historical instances

## Proposed Core Tables
- `symbols`
- `price_bars`
- `pattern_instances`
- `pattern_features`
- `forward_labels`
- `match_results` (future)

---

## 9.1 Baseline SQLite Schema and Feature Map

The validated baseline database is SQLite-first and SPY-first. It uses separate tables for raw bars, pattern instances, derived features, and forward labels so schema responsibilities remain auditable and versionable.

### Validated schema objects

- `symbols`
- `source_files`
- `price_bars`
- `feature_sets`
- `pattern_instances`
- `pattern_features`
- `forward_labels`

### Exact SQLite schema

- `symbols(symbol_id INTEGER PRIMARY KEY, symbol TEXT UNIQUE NOT NULL)`
- `source_files(source_file_id INTEGER PRIMARY KEY, filename TEXT UNIQUE NOT NULL, symbol TEXT NOT NULL, hold_days INTEGER NOT NULL, imported_at TEXT NOT NULL)`
- `price_bars(price_bar_id INTEGER PRIMARY KEY, symbol_id INTEGER NOT NULL, bar_date TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, volume REAL, FOREIGN KEY(symbol_id) REFERENCES symbols(symbol_id))`
- `feature_sets(feature_set_id INTEGER PRIMARY KEY, feature_version TEXT NOT NULL)`
- `pattern_instances(pattern_instance_id INTEGER PRIMARY KEY, symbol_id INTEGER NOT NULL, source_file_id INTEGER NOT NULL, anchor_date TEXT NOT NULL, feature_set_id INTEGER NOT NULL, FOREIGN KEY(symbol_id) REFERENCES symbols(symbol_id), FOREIGN KEY(source_file_id) REFERENCES source_files(source_file_id), FOREIGN KEY(feature_set_id) REFERENCES feature_sets(feature_set_id))`
- `pattern_features(pattern_feature_id INTEGER PRIMARY KEY, pattern_instance_id INTEGER NOT NULL, feature_name TEXT NOT NULL, feature_value REAL, FOREIGN KEY(pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id))`
- `forward_labels(forward_label_id INTEGER PRIMARY KEY, pattern_instance_id INTEGER NOT NULL, hold_days INTEGER NOT NULL, absolute_return REAL, percent_return REAL, direction TEXT, profitable INTEGER, FOREIGN KEY(pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id))`

### Indexes

- `idx_price_bars_symbol_date(symbol_id, bar_date)`
- `idx_pattern_instances_symbol_anchor(symbol_id, anchor_date)`
- `idx_forward_labels_hold_days(hold_days)`


### Validation notes

The baseline schema has been executed and confirmed in `P300_catalog_baseline.db`. The created indexes are `idx_price_bars_symbol_date`, `idx_pattern_instances_symbol_anchor`, and `idx_forward_labels_hold_days`.

### Baseline feature version

`baseline_5bar_v1`

### Baseline 5-bar feature map

The first-pass feature map keeps one five-bar window per pattern instance, anchored on the most recent bar in the window. The baseline feature set retains these raw and derived inputs:

- Date / trade date
- Open, high, low, close
- Volume
- Short, medium, and long differences
- Predicted high and predicted low
- Williams EMAI
- Professional Sentiment PSI and ROC
- Neural Index and NeuralXMax
- Triple Cross short, medium, and long
- Predicted high diff, predicted low diff, and predicted range

Derived baseline features for `baseline_5bar_v1`:

- `close_0` to `close_4`
- `range_0` to `range_4`
- `body_0` to `body_4`
- `volume_0` to `volume_4`
- `stdiff_0` to `stdiff_4`
- `mtdiff_0` to `mtdiff_4`
- `ltdiff_0` to `ltdiff_4`
- `pred_high_diff_0` to `pred_high_diff_4`
- `pred_low_diff_0` to `pred_low_diff_4`
- `pred_range_0` to `pred_range_4`
- `williams_emai_0` to `williams_emai_4`
- `psi_0` to `psi_4`
- `roc_0` to `roc_4`
- `neuralx_0` to `neuralx_4`
- `neuralx_max_0` to `neuralx_max_4`
- `triple_cross_dir_0` to `triple_cross_dir_4`
- `window_close_change_abs`
- `window_close_change_pct`
- `window_high_max`
- `window_low_min`
- `window_total_range`
- `window_avg_volume`
- `window_up_bar_count`
- `window_down_bar_count`
- `anchor_predicted_bias`
- `anchor_state_triple_cross`

### Forward labels

Forward labels are generated for 5-day, 7-day, and 10-day holds. Each pattern instance stores absolute return, percent return, direction, and a profitability flag for each hold window.

### Known-good example files

- `History_Grid_050324_051324_SPY_5day.csv`
- `History_Grid_050324_051324_SPY_7day.csv`
- Optional extra validation file: `History_Grid_102225_102925_SPY.csv`

### Later feature additions

Any later feature additions must be recorded as a new feature version instead of silently changing `baseline_5bar_v1`. This preserves auditability and keeps later similarity work comparable across versions.

# 10. Testing & Validation

## 10.1 Testing Approach

- Validate source-file imports against known historical records
- Spot-check feature generation on selected dates
- Verify label calculations against manually computed forward returns
- Confirm database row counts and null handling at dataset edges
- Validate startup process by requiring architecture summary on new sessions

## 10.2 Validation Checklist

- Architecture document loaded at session start
- Current milestone correctly stated
- SPY source file recognized correctly
- Feature logic version identified
- Forward-label windows verified
- No undocumented schema changes

## 10.3 Known Issues / Limitations

| Issue ID | Description | Severity | Workaround | Status |
|---|---|---|---|---|
| ID-001 | Context loss across new threads | High | Read architecture doc first | Controlled |
| ID-002 | Exact P_300 file map not yet fully embedded | Medium | Add appendix in next revision | Open |

---

# 11. Daily Operations & Session Management

## 11.1 Session Start Protocol

At the beginning of each new session:
1. Read this document fully
2. State current milestone
3. State last completed work
4. State approved next task
5. Ask for clarification only if the next task is ambiguous

## 11.2 Maintenance

| Task | Frequency | Owner | Notes |
|---|---|---|---|
| Architecture review | Weekly or after major change | Anthony | Update milestone and file map |
| Startup prompt review | As needed | Anthony | Refine session consistency |
| Schema review | At each DB milestone | Anthony | Keep SQLite design current |
| Error log review | When issue repeats | Anthony | Promote repeats into permanent fixes |

---

# 12. Troubleshooting & Support

## 12.1 Common Issues

### Issue — AI forgets prior discussion
- **Symptoms:** New thread starts with incorrect assumptions or generic responses.
- **Root Cause:** Session context was not reloaded from architecture/project documentation. [file:39]
- **Solution:** Read this architecture document first, summarize current status, and restate the next step before proceeding. [file:39]
- **Prevention:** Use the startup protocol in every new thread. [file:39]

### Issue — Wrong milestone focus
- **Symptoms:** Work begins on future tasks before current foundation is complete.
- **Root Cause:** No explicit milestone restatement at session start.
- **Solution:** Require milestone confirmation in the startup step.
- **Prevention:** Keep Section 1 and Section 5 updated.

## 12.2 Escalation Path

| Level | Condition | Action |
|---|---|---|
| Self-correct | Minor drift | Restate architecture rule |
| Session reset | Repeated misunderstanding | Start new thread with architecture bootstrap |
| Documentation update | Repeat issue twice | Add permanent rule or example to this doc |
| System redesign | Architecture no longer fits project | Open enhancement item and revise structure |

---

# 13. Appendices

## Appendix A — Glossary

| Term | Definition |
|---|---|
| Carryover Summary | Compact project-state summary copied into a new thread |
| Architecture Bootstrap | Mandatory read-first startup process |
| Pattern Label | Outcome classification based on future price movement |
| Grid Match | Similarity match between a current pattern and historical analog |

## Appendix B — Related Documentation

| Document | Purpose |
|---|---|
| README.md | Hub-wide foundation architecture context |
| UNIVERSAL_PROJECT_TEMPLATE_v1_1.md | Template source for this system document |
| Trading_Projects_Folder_Architecture.md | Hub environment and standards reference |
| Future P300 prompt file | Startup prompt and session control |

## Appendix C — Configuration Reference

| Item | Value |
|---|---|
| Shared Python Environment | p140 |
| Python Path | C:\Users\Trader\.conda\envs\p140\python.exe |
| Local LLM Endpoint | http://localhost:1234/v1 |
| Local LLM Model Reference | llama-4-scout-17b-16e-instruct |

## Appendix D — Document Control

| Field | Value |
|---|---|
| Document Owner | Anthony Zoppi |
| Classification | Internal |
| Template Version | UNIVERSAL_PROJECT_TEMPLATE_v1_1 |
| Review Schedule | Weekly during active build or after major architecture change |

## Appendix E — Working Folder Map

- `python/ingest`
- `python/feature_engineering`
- `python/matching`
- `python/labeling`
- `python/utilities`
- `data/raw`
- `data/processed`
- `data/historical`
- `data/reference`
- `outputs/reports`
- `outputs/charts`
- `outputs/exports`
- `docs/architecture`
- `docs/prompts`
- `docs/notes`
- `docs/validation`
- `models/catalog.db`
- `models/schema`




## 11.3 Next Session Prompt

Read `P300_System_Architecture.md` first. Summarize current milestone status, last completed work, and next approved objective. Confirm the measurable milestone objectives, IntelliScan readiness criteria, and documentation workflow rule that the user uploads source documents and the AI returns replacement files. Then wait for confirmation or proceed only within those constraints.

## Appendix F — Prompt Library Entry

P_300 bootstrap: read the architecture first, summarize milestone status and next task, confirm measurable objectives and replacement-file workflow, then wait or proceed only within constraints.
