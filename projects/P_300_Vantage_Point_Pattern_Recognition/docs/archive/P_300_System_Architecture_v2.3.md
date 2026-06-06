# P_300 — VantagePoint Pattern Recognition System Architecture

**Project ID:** P_300
**Version:** 2.3
**Last Updated:** 2026-05-15
**Maintained By:** Anthony Zoppi
**Status:** Active / Stage 4 Sealed / Stage 5 Active

---

## Documentation Decision Protocol

This document is the **master architecture reference** for the P_300 project. New P_300 documentation belongs here first unless content is long-form, frequently updated, reused across projects, or needs separate version history. Separate files are referenced back from this document and named to the project convention.

**Session bootstrap is handled automatically by two mechanisms:**

1. **`p300-project-context` SKILL** at `C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\p300-project-context\SKILL.md` — auto-loads on the first prompt of any P_300 chat. Contains concise protection rules, anti-patterns, schema shorthand, critical paths.
2. **System Initialization Prompt (SIP)** at `docs/prompts/P_300_System_Initialization_Prompt_v2.md` — runs the INIT sequence (account params, market posture, lessons.md, current task queue).

The architecture document (this file) is the full spec. It is referenced on-demand from the SKILL and SIP, not read on every session.

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

P_300 Vantage Point Pattern Recognition is a VantagePoint-based research and trading-decision system that builds a durable historical pattern catalog across multiple symbols, labels patterns by forward profitability, and matches current candidates to historical analog patterns to produce BUY / WATCH / PASS signals.

The system is designed around the principle that **pattern structure transcends ticker** — a 5-day consolidation with rising volume and a bullish triple-cross has the same predictive value on SPY, NVDA, or AAPL when feature values are normalized to percentages. The catalog is one shared pool; matching is cross-symbol by default.

## 1.2 Scope

**What this system covers:**

- Historical pattern extraction from VantagePoint history-grid exports
- Pattern catalog with normalized cross-symbol comparability
- Forward profitability labeling at 5, 7, 10, 15, 20-day horizons
- Daily evaluation of current candidates against the historical catalog
- BUY / WATCH / PASS signal output with statistical confidence (Z-score)
- Position-sizing recommendation based on confidence + risk config (Milestone 5)

**What this system does not cover:**

- Automated live brokerage execution
- Enterprise data engineering infrastructure
- Long-horizon portfolio optimization
- Non-pattern-based discretionary analysis

## 1.3 Project Details

| Field | Value |
| :---- | :---- |
| Start Date | 2026 Q1 build phase |
| Current Status | v2.0 architectural rebuild in progress — Path B (fresh-start re-ingest); Stages 3–7 roadmap active |
| AI Engines | Claude (Architect + Code Author) → Local LLM (Dev Assistant + Post-Decision Narrator). Gemini deprecated. |
| Runtime Logic | Deterministic Python only. No LLM in the BUY/WATCH/PASS decision path. |
| Primary Platform | Python (p140 conda env), SQLite, VantagePoint exports |
| Project Location | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\` |
| Related Projects | P_000 (foundation), P_010 (market posture), P_020 (analytics) |

## 1.4 Reference Materials

| Document | Location | Notes |
| :---- | :---- | :---- |
| `p300-project-context` SKILL | `C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\p300-project-context\SKILL.md` | Auto-loads at session start; concise rules |
| System Initialization Prompt | `docs/prompts/P_300_System_Initialization_Prompt_v2.md` | INIT sequence for new chats |
| `python-project-architecture` SKILL | `docs/perplexity-skills/python-project-architecture/SKILL.md` | Hub-wide Python standards |
| README.md (P_000) | P_000 foundation project | Hub-wide context |
| Trading_Projects_Folder_Architecture.md | Hub root | Hub-wide folder standards |

## 1.5 Definitions & Acronyms

| Term | Definition |
| :---- | :---- |
| VP | VantagePoint |
| Pattern Catalog | The SQLite database (`mmddyycatalog.db`) holding all historical pattern instances, normalized bar data, derived features, and forward labels |
| Pattern Instance | One historical setup observation, tied to a symbol and anchor date, with a window of N bars and forward outcome labels |
| Pattern Bar | One row of normalized + raw VP bar data at a specific offset from the anchor (offset 0 = anchor, -1 = day before) |
| Pattern Window | The N-bar lookback that defines the pattern shape. Variable length, 5 to 20 bars |
| Forward Label | Outcome metric (return %, profitable yes/no) at a horizon (5/7/10/15/20 days) after the anchor |
| Anchor Date | The "Day 0" date of a pattern — the most recent bar in the captured window |
| Cross-Symbol Matching | Similarity search across the full catalog regardless of ticker, comparing normalized pattern shapes |
| Pipeline A — Add Pattern | Write-side workflow that ingests new historical patterns into the catalog |
| Pipeline B — Daily Evaluate | Read-side workflow that scores today's candidates against the catalog and produces BUY/WATCH/PASS |
| Catalog Check-Out | Pre-operation read/inspection of the SQLite catalog (row counts, schema integrity) |
| Catalog Check-In | Post-operation validation of the SQLite catalog (delta verification, integrity confirmation) |
| Lock + Temp-DB + Atomic Move | Transaction safety pattern: copy master → `temp_working.db` → operate → verify → atomically replace master |
| Normalization Layer | Pre-computed percentage-based columns on `pattern_bars` that make cross-symbol similarity matching valid by construction |
| SKILL | A Claude Code skill file that auto-loads at session start to set context |
| SIP | System Initialization Prompt — bootstraps a new chat with project state |

---

# 2. System Architecture

## 2.1 High-Level Flow

```
                  VantagePoint History-Grid Export
                              |
                              v
                  Converter (raw bars, no truncation)
                              |
                              v
              +---------- Splits ----------+
              |                            |
              v                            v
      data/historical_patterns/        data/live/
       (Pipeline A vault)            (Pipeline B inbox)
              |                            |
              v                            v
        Pipeline A: Add                Pipeline B: Daily
        Pattern (WRITE)                Evaluate (READ)
              |                            |
              v                            v
      Normalize → Ingest →           Ingest as EVAL_SET →
      Features → Labels              IntelliScan match →
              |                      Aggregator stats →
              v                      Signal: BUY/WATCH/PASS
       mmddyycatalog.db
       (shared catalog)
```

## 2.2 Two Pipelines, Two Disciplines

The system has two distinct pipelines with intentionally different design properties:

### Pipeline A — Add Pattern (Brain Vault)

| Property | Value |
| :---- | :---- |
| Direction | WRITE — adds permanent rows to the catalog |
| Primary tempo | Slow, careful, atomic |
| Source | `data/historical_patterns/` (filename prefix `Pattern_`) |
| Transaction safety | Lock + Temp-DB + Atomic Move (Section 2.6) |
| Verification | Post-ingest health check (Ghost Patterns vs. Valid Patterns) |
| Failure mode | Halt + rollback to last verified state |

Pipeline A grows the long-term mathematical "DNA" library. Quality over speed. Every write is bracketed by Catalog Check-Out → operation → Catalog Check-In.

### Pipeline B — Daily Evaluate

| Property | Value |
| :---- | :---- |
| Direction | READ — queries the catalog, no permanent writes to historical tables |
| Primary tempo | Fast, integrated, real-time decision support |
| Source | `data/live/` (filename pattern `History Grid (<symbol>).csv`) |
| Output | Inline terminal report with BUY/WATCH/PASS signal per symbol |
| Failure mode | Fail to "PASS" (no trade) — never silently produce a BUY |

Pipeline B is the decision engine. It may insert rows into `pattern_instances` flagged as `data_origin_type='EVAL_SET'` to enable matching the candidate, but those rows are transient or clearly tagged and never confuse the historical training set.

### Anti-Pattern: Workflow Conflation

The two pipelines must NEVER be merged into a single script. Gemini-era v1.16 attempted this and produced four hours of drift work. Sequential safety (Pipeline A) and integrated speed (Pipeline B) are different design constraints; mixing them corrupts both.

## 2.3 Layer Architecture (Hub Standard)

The Python codebase follows the Hub-wide clean-architecture standard. Every Python file belongs to exactly one layer:

```
python/
├── config.py              ← All constants and paths
├── schemas.py             ← Pydantic models for all persistent file I/O
├── domain/                ← Business logic ONLY (no I/O, no print, no DB)
│   └── *.py
├── infrastructure/        ← All I/O ONLY (files, DB, APIs, network)
│   └── *.py
├── application/           ← Orchestration ONLY (calls domain + infrastructure)
│   └── *.py
├── cli.py                 ← Entry points / command-line interface
├── launcher.bat           ← Windows batch launcher
├── requirements.txt       ← Project dependencies
└── migrations/            ← One-shot migration scripts (Stage 3+)
    └── *.py
```

### Layer Rules (enforced by directory placement)

- **`domain/`** — Pure Python functions. Takes data in, returns data out. NO file I/O. NO database. NO `print()`. NO HTTP. Fully testable without external dependencies. Examples: similarity distance math, Z-score calculation, BUY/WATCH/PASS threshold logic, normalization formulas.
- **`infrastructure/`** — All file reads/writes, SQLite queries, network calls. NO business logic. Returns raw data to the application layer. Examples: catalog reader/writer, VP CSV parser, P_010 risk config loader.
- **`application/`** — Orchestration only. Calls domain functions and infrastructure functions in sequence. Contains the workflow logic. NO raw business logic. NO direct I/O. Examples: `run_add_pattern_pipeline()`, `run_daily_evaluation()`.
- **`config.py`** — All constants, paths, thresholds. Single source of truth. Imported by every layer that needs a value.
- **`schemas.py`** — Pydantic models for every CSV, JSON, DB read/write that persists between runs. Schema validation at the data boundary, not after corruption.

### Why this matters for P_300 specifically

The Gemini-era code mixed concerns systematically: `ingest_vp_catalog.py v6.0` did DB writes, file globbing, business logic decisions, AND mocked feature extraction all in one function. The same script had three different failure modes that all looked like "ingest worked." Layer separation makes that class of bug structurally hard to write — a `domain/` file that tries to open a database fails on import because `sqlite3` isn't imported there.

## 2.4 Path Standards

| Path Type | Method | Rationale |
| :---- | :---- | :---- |
| Hub root | Hardcoded constant in `config.py` | `C:\Users\Trader\AI-Agent-Learning-Hub` — never moves |
| Conda env | Hardcoded in launcher batch files | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Catalog DB | `db_utils.get_latest_catalog()` | Glob `*catalog.db`, digit-first filter, newest by name |

Hardcoded paths anywhere outside `config.py` and the conda-env path in launcher batches are prohibited.

## 2.5 Schema as Protection Layer

The seven-table normalized schema (defined in Section 9) is the primary protection against the bug classes that plagued the Gemini era. Three guarantees are enforced at the data layer:

1. **No hollow records.** `pattern_instances` requires `feature_set_id` AND `source_file_id` NOT NULL. An ingest that skips features or loses provenance fails at INSERT, not silently at runtime. (Closes EC-027.)
2. **Variable window without schema change.** `pattern_instances.window_length` is data; `pattern_bars` rows scale 5 to 20. The converter's `df.tail(5)` truncation that locked patterns to 5 bars cannot recur because no part of the schema requires a fixed bar count.
3. **VP vendor drift contained.** When VantagePoint changes their export columns, the manifest update is contained to the `pattern_bars` INSERT path. Other tables are insulated. Schema is the contract that limits blast radius.

## 2.6 Catalog DB Check-In / Check-Out Protocol

Every operation that reads or writes the SQLite catalog is bracketed:

### Check-Out (Pre-Operation)

1. Confirm catalog file exists at the resolved `db_utils.get_latest_catalog()` path
2. Open via SQLite and row-count probe each core table (`symbols`, `source_files`, `feature_sets`, `pattern_instances`, `pattern_bars`, `pattern_features`, `forward_labels`)
3. Inspect the most recent rows in `pattern_instances` to verify schema integrity
4. Record pre-operation counts in working notes

### Check-In (Post-Operation)

1. Re-run row-count probe on each modified table
2. Confirm delta matches expectation
3. Spot-check `pattern_bars` and `forward_labels` for the newly inserted patterns
4. Record post-operation counts and schema version

### Write-Operation Transaction Safety (Lock + Temp-DB + Atomic Move)

For any write to the canonical DB:

1. **Lock verify** — confirm no other writer is active
2. **Copy to temp** — `models/temp_working.db` is the operation target, never the master
3. **Verify temp** — row-count delta, schema match, spot-check inspections against the temp file
4. **Atomic move** — only after verification, atomically replace master with verified temp
5. **Log** — record post-operation counts and schema version

Failure of any step discards the temp file and leaves the master untouched.

## 2.7 Anti-Patterns (Forbidden by Construction)

The following patterns are forbidden anywhere in the codebase. Each has documented historical damage:

- **`df.tail(N)` or `df.head(N)` truncation in the converter or ingest layer.** Patterns have variable length 5–20; truncation locks the window and silently drops bars. (Source: converter v6.8.)
- **Writing TEXT into an INTEGER foreign key column.** Pattern instances must reference `symbol_id` as INTEGER, never the ticker string. SQLite type affinity will accept the corruption silently. (Source: EC-027, ingest_vp_catalog v6.0.)
- **Raw dollar values in cross-symbol similarity matching.** SPY $500 vs NVDA $135 is incomparable. Normalization is pre-computed on `pattern_bars` columns; the matching engine queries the normalized columns. (Source: EC-046, EC-048.)
- **Mock data dictionaries inside evaluation engines.** The decision engine must query the catalog. (Source: `P_300_EvaluateTrade.py v4.7`.)
- **Hardcoded DB paths in any Python file.** All DB access goes through `db_utils.get_latest_catalog()`. (Source: EC-049, EC-058.)
- **Mixing layers in a single file.** Domain functions cannot do I/O. Infrastructure functions cannot make business decisions. (Source: ingest v6.0 conflation.)

---

# 3. AI Tools & Platforms

## 3.1 Tool Stack

| Tool / Platform | Role | Notes |
| :---- | :---- | :---- |
| Python (p140 conda env) | All runtime logic — deterministic | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| SQLite | Pattern catalog database | One DB per active baseline (`mmddyycatalog.db`) |
| VantagePoint | Historical and live market data source | Vendor — may drift; schema protects us |
| Claude | Architect + Code Author | Writes all Python; reviews architecture changes |
| Local LLM (LM Studio) | Dev Assistant + Post-Decision Narrator | Never in the runtime decision path |
| DB Browser for SQLite | Visual catalog inspection | Used during Check-Out verification |
| PowerShell | Workflow orchestration | Hosts the launcher wrappers |
| `windows-mcp:FileSystem` MCP | Direct file writes Claude → Hub | Eliminates download-and-move pattern |

## 3.2 Local LLM Split (Critical)

The Local LLM is split into two roles with a hard boundary between them:

- **Dev Assistant role** — generates Python code, reviews architecture, answers documentation questions. Runs during development. Output is reviewed by the operator before being committed.
- **Post-Decision Narrator role** — after the deterministic pipeline produces a BUY/WATCH/PASS signal with statistics, the Local LLM generates a human-readable summary ("Today's BUY on SPY is driven by 12 historical analogs averaging 4.2% over 7 days, strongest match from 2024-11-14 which returned 5.8%"). Runs at the end of Pipeline B.

**The Local LLM is NEVER in the BUY/WATCH/PASS decision logic.** Same SPY data must always produce the same signal. Determinism is non-negotiable for trading decisions. (See Gemini-era failures EC-022, EC-027, ID-005 for what happens when LLMs leak into the runtime path.)

## 3.3 AI Behavioral Rules (Mandatory for any AI working on P_300)

**Must:**

1. Read the SKILL at session start (auto-loaded)
2. Use documented project state, not assumptions
3. Distinguish confirmed facts from proposed next steps
4. Keep outputs aligned to layer architecture and naming conventions
5. Execute Catalog Check-Out before any DB-touching operation and Check-In after
6. Apply Lock + Temp-DB + Atomic Move for all writes against the canonical DB
7. If a change spans more than 2 lines or multiple functions, output the entire script
8. Include a versioned header on every Python script (Section 8.4)
9. Plan all files with line counts BEFORE writing any code (per `python-project-architecture` skill)
10. Wait for operator approval if the plan involves more than 3 files or significant structural decisions
11. **Call `tool_search` at session start** to discover filesystem MCP capability (`windows-mcp:FileSystem`, `filesystem:read_text_file`, or equivalent) BEFORE concluding the environment is ephemeral
12. When filesystem MCP is available, **perform file modifications directly via MCP** — do not hand the operator text to paste for any change spanning 2+ lines or 2+ places

**Must Not:**

1. Invent project status that is not documented
2. Change schema or folder conventions without documenting the change
3. Treat thread memory as authoritative when this document or the SKILL says otherwise
4. Introduce a new parser, schema, workflow, or generalized implementation path when the approved task is to clone the validated pattern
5. Skip the Check-Out / Check-In bracketing on any catalog operation
6. Write directly to the master DB without going through `temp_working.db` first
7. Mix layers (domain doing I/O, infrastructure doing business logic, etc.)
8. Insert LLM-generated output into the BUY/WATCH/PASS decision path
9. Use mock data in production decision engines
10. Hardcode paths anywhere outside `config.py`
11. Conclude the environment is ephemeral without first calling `tool_search`
12. Identify the client environment (web / Desktop / Code) in session output — client identity is not reliably detectable from the system prompt; report tool capability instead

---

# 4. Requirements

## 4.1 Functional Requirements

| ID | Description | Component | Status |
| :---- | :---- | :---- | :---- |
| FR-1 | Ingest VantagePoint history-grid data into structured pipeline | Pipeline A | To rebuild (Stage 4) |
| FR-2 | Compute repeatable pattern features with cross-symbol normalization | `domain/` + Pipeline A | To rebuild (Stage 4) |
| FR-3 | Maintain SQLite pattern catalog with 8-table normalized schema | Schema | To create (Stage 3) |
| FR-4 | Generate forward profitability labels at 5/7/10/15/20 day horizons | Pipeline A | To rebuild (Stage 4) |
| FR-5 | Support multi-symbol from day 1 | Schema + Matching | Built-in to schema |
| FR-6 | Bootstrap each session via SKILL + SIP | Session control | To create (Stage 3) |
| FR-7 | Batch CSV processing through Pipeline A | Pipeline A | To rebuild (Stage 4) |
| FR-8 | Catalog Check-In / Check-Out bracketing on every DB operation | All scripts | Procedural rule |
| FR-9 | Lock + Temp-DB + Atomic Move on writes to canonical DB | Pipeline A | To build (Stage 4) |
| FR-10 | Cross-symbol similarity matching with percentage normalization | Pipeline B | To rebuild (Stage 6) |
| FR-11 | BUY / WATCH / PASS signal output with Z-score confidence | Pipeline B | To rebuild (Stage 6) |
| FR-12 | Local LLM post-decision narrative generation | Pipeline B (final step) | Stage 7 |
| FR-13 | Position-sizing recommendation from confidence + risk config | Pipeline B | Milestone 5 (planned) |

## 4.2 Non-Functional Requirements

- **NFR-1 Determinism:** Same input data must always produce the same signal output. No LLM in the runtime decision path.
- **NFR-2 Auditability:** Every pattern in the catalog must be traceable to a source file via `source_files`.
- **NFR-3 Schema integrity:** No hollow records possible. NOT NULL constraints + FK constraints + atomic ingest.
- **NFR-4 Layer separation:** Code is structurally organized so concerns cannot silently mix.
- **NFR-5 Vendor-drift resilience:** VP export format changes are contained to the manifest layer.
- **NFR-6 Reproducibility:** Forward labels at 5/7/10/15/20 horizons computed deterministically from market data. Stage 5 validation is a manual spot-check of one known pattern — compute labels by hand, verify pipeline output matches exactly.

## 4.3 Requirements Matrix

See FR table above. Status reflects Stage 2 approval; implementation tracking in `tasks/todo.md`.

---

# 5. Change Log

## v2.3 — 2026-05-15 — Stage 4 Closeout

- **Stage 4 SEALED.** Pipeline A end-to-end ingest works on real VP XLSX exports. Full closeout report at `docs/migrations/STAGE_4_CLOSEOUT.md`.
- **11 of 11 Stage 4 files delivered** (~2,158 lines of new Python + 4.5 KB JSON config): `schemas.py` v2.1, `ingest_manifest.json` v2.0, `domain/normalization.py` v1.0, `domain/labeler.py` v1.0, `infrastructure/vp_xlsx_reader.py` v1.0, `utilities/vp_export_integrity_check.py` v1.0, `infrastructure/catalog_writer.py` v1.0.1, `infrastructure/verify_ingestion.py` v1.0, `application/add_pattern_pipeline.py` v1.0, `utilities/catalog_summary.py` v1.0, `cli.py` v1.0. All independently smoke-tested + integrated end-to-end.
- **POC ingested:** 2 of 5 originally approved POC symbols (AAPL launch 2026-01-27 + OII launch 2026-02-18) with cross-symbol normalization empirically validated at radically different price points. Remaining 3 POC symbols (SPY, QQQ, NVDA) rolled to Stage 5.
- **Anchor convention clarified:** `pattern_bars` = window_length bars ENDING at launch, offsets -(window_length-1) to 0 inclusive. Launch IS the anchor at offset 0. This matches the schemas.py `bar_offset Field(le=0, ge=-19)` constraint and supersedes any earlier wording that read "20 bars BEFORE launch" (which would have excluded the anchor).
- **`config.py` v1.0 → v1.1:** Removed `ONEDRIVE_ROOT` and `import os`. M-010 instance #2 — vestigial Gemini-era artifact survived the D3 converter scope trim. Surfaced when `config.py` import crashed in non-interactive shells lacking the `OneDrive` user env var. Removed from §2.3, §2.4, §8.4.3, Appendix C, SIP Critical Paths. EC-059 + EC-066 kept as historical record in §6.
- **`catalog_writer.py` v1.0 → v1.0.1:** `_CATALOG_TABLES` → `CATALOG_TABLES` (public) for cross-module reuse by `verify_ingestion.py` and `catalog_summary.py`.
- **New lessons:** M-013 (Pydantic cross-field invariants must use `@model_validator(mode="after")`, not `@field_validator`), M-014 (validate config artifacts against real source-data samples before commit), O-006 (VP merged top-row headers; openpyxl returns null on continuation cells).
- **`docs/migrations/STAGE_4_CLOSEOUT.md`** — forensic record of every delivery, validation, and decision in Stage 4.
- **`docs/archive/P_300_System_Architecture_v2.2.md`** — prior major version preserved.

## v2.2 — 2026-05-14

- **Stage 3 closeout.** All Stage 3 deliverables complete: foundation files (`config.py`, `schemas.py`), Stage 3a folder setup, Stage 3b legacy archive (10 dirs + 29 files + 47 utility-sweep + 2 cache-delete = 88 ops), Stage 3c new catalog (`models/051426catalog.db`), Stage 3.3 `db_utils.py` glob edit, Stage 3.4 migration ledger.
- **§2.5, §7, v2.0 changelog: "8-table" → "7-table".** The "8-table" wording was a stale claim propagated from earlier planning; §9.2 has always defined 7 tables (`symbols`, `source_files`, `feature_sets`, `pattern_instances`, `pattern_bars`, `pattern_features`, `forward_labels`). No schema change — wording correction only. Caught at Stage 3c verification; codified as an instance of M-009.
- **Active catalog file:** `models/051426catalog.db` (replaces planned `051126catalog.db`; date stamp = creation date 2026-05-14).
- **New file:** `python/utilities/db_connect.py` v1.0 — SQLite connection factory. Every catalog connection in the project flows through `get_connection()` or `connection_context()`, both of which set `PRAGMA foreign_keys = ON` to enforce FK constraints. Required by Stage 4 `infrastructure/catalog_writer.py` and `infrastructure/catalog_reader.py`. Per M-012.
- **`python/utilities/db_utils.py` v1.14 → v1.16.** Glob pattern updated `*geminicatalog.db` → `*catalog.db` (Stage 3.3); `MODELS_DIR` and `CATALOG_GLOB_PATTERN` now imported from `config.py` per §2.4 single-source-of-truth rule (Stage 3.3+ bonus).
- **`tasks/lessons.md` additions:** M-011 (route `logging` to stdout for PowerShell-invoked scripts) and M-012 (`PRAGMA foreign_keys = ON` on every sqlite3 connection).
- **`docs/migrations/STAGE_3_MIGRATION_LEDGER.md`** — forensic record of all Stage 3 moves and edits, plus Stage 4 inheritance list.

## v2.1 — 2026-05-13

- **Section 11.1 expanded** with new subsection **11.1.1 Environment Capability Discovery (Mandatory Step Zero)**. AI MUST call `tool_search` for filesystem MCP capability at session start BEFORE concluding the environment is ephemeral. Report capability in session header ("Filesystem MCP: available/unavailable") instead of client identity — Claude.ai web, Desktop, and Code present nearly identical system prompts; client identity is not reliably detectable but tool availability IS.
- **Section 3.3 AI Behavioral Rules** — added Must-rules #11 and #12 (call `tool_search` before assuming ephemeral; perform file modifications directly via MCP when available — no paste handoffs).
- **Section 3.3 Must Not** — added #11 and #12 (never conclude ephemeral without `tool_search`; never identify client environment in session output).
- **Section 8.4** — added subsection **8.4.6 Direct File Modification Standard** codifying MCP-first modification rule.
- **`tasks/lessons.md` and `tasks/todo.md` are read LIVE every session** (continuous and per-task-completion updates). P_000 and P_010 too (monthly and twice-weekly respectively). Cached values never reused across chats.
- **Session header time fallback** made explicit: if wall-clock time isn't available in the environment, display date only — never fabricate.
- **Doc-wide canonicalization pass** — converted 4 `e.g.` and 1 `or similar` hedge phrases to canonical statements (`Current default`, `observed`, `proposed`). Architecture doc states facts, not suggestions. Codified as M-009 in `tasks/lessons.md`.
- **Preservation CSV concept dropped** — vestigial from earlier "migrate old DB" planning. Path B = fresh start, so the pre-clean DB is a forensic-only artifact; its labels are not regression ground truth. Removed `PreservationPattern` schema, `stage_3b_preservation_export.py` script, `PRESERVATION_REFERENCE_CSV` constant, and all related references across the doc. Stage 5 validation is now a deterministic spot-check. Codified as M-010 in `tasks/lessons.md`.

## v2.0 — 2026-05-13

- **Major architectural rebuild.** Replaces v1.x Gemini-era design.
- **Path B decision** — fresh start with new schema, re-ingest from source CSVs. Old 371-pattern catalog preserved as regression reference only.
- **7-table normalized schema** — adds `source_files`, `feature_sets`, `pattern_bars` (normalized window table). Drops `trade_outcomes` (merged into `forward_labels`).
- **Cross-symbol matching from day 1** with percentage normalization pre-computed in `pattern_bars`.
- **5–20 day variable pattern window**; 5/7/10/15/20 day forward horizons.
- **Hub-standard layer architecture** — `domain/`, `infrastructure/`, `application/`, `config.py`, `schemas.py`. Replaces function-folder layout.
- **Local LLM split** — deterministic Python runtime; LLM only as dev assistant + post-decision narrator.
- **Naming change:** `mmddyycatalog.db` (drops `gemini` prefix). `db_utils` glob updated.
- **Stage roadmap 3–7** active. Stage 3 = file system cleanup + empty new schema DB.
- **Forensic findings recorded** for v6.0 ingest and v4.7 evaluator (see Section 6 EC entries).

## v1.19 — 2026-05-13

- ID-005 added documenting AddPattern spoofing and Gemini Typhoid-Mary architectural breaks.

## v1.18 — 2026-05-11

- AddPattern DailyWorkflow validation discovered many flaws.
- Discovered AddPattern not actually complete despite Gemini claims.

## v1.17 — 2026-05-10

- Daily Workflow split into Flow Streams: Add Pattern (PowerShell) + Daily Evaluation (Python).
- EC-054 through EC-057 added.

## v1.16 — 2026-05-09

- Rework Daily Workflow into Flow Streams; EC-049 through EC-053 added.

## v1.15 — 2026-05-07

- Milestone 4 (IntelliScan refinement). IntelliScan v2.2 + Aggregator v2.3 + parameter sweep tool deployed locally.

## v1.14 — 2026-05-06

- `db_utils.py` refactored for numeric prefix filtering.
- `ingest_vp_catalog.py` anchor-date extraction fix (head vs tail).

## v1.13 — 2026-05-06

- Added `db_utils.py` utility. Added Section 8.4 coding standards.

## v1.12 — 2026-05-05

- Sandbox/Deployment environment distinction. Naming convention introduced.

## v1.11 — 2026-05-03

- WorkflowLauncher.ps1 added.

## v1.10 — 2026-05-03

- Daily Pattern Analysis Workflow formalized. Check-In / Check-Out protocol added. Write-Operation Transaction Safety subsection.

## v1.9 — 2026-05-03

- Pre-Flight Audit protocol formalized.

## v1.8 — 2026-05-03

- Bootstrap Handshake formalized. Error Log review mandated.

## v1.7 — 2026-05-03

- Consolidated history. Data Parity Flowboard added.

## v1.6 — 2026-05-03

- Full Artifact delivery rule enforced.

## v1.5 — 2026-05-02

- AI stack updated to multi-LLM chain.

## v1.4 — 2026-05-02

- Milestone 2 complete.

## v1.3 — 2026-04-30

- Schema baseline (baseline_5bar_v1) validated.

## v1.2 — 2026-04-25

- Pipeline Flow V2 visual.

## v1.1 — 2026-04-20

- Master architecture established.

## v1.0 — 2026-04-15

- Initial project documentation.

---

# 6. Error Corrections Log

The full historical log is preserved. EC-060 and beyond capture the v2.0 forensics from the Claude rebuild session.

| ID | Description | Status | Resolution |
| :---- | :---- | :---- | :---- |
| EC-001 | Perplexity Context Drift | Fixed | Session-start architecture load |
| EC-002 | Missing Architecture Documentation | Fixed | Consolidated into master doc |
| EC-003 | Pipeline Ingestion logic errors | Fixed | Standardized `initialize_db.py` schema |
| EC-004 | Incorrect Path Mapping | Fixed | Absolute paths enforced |
| EC-005 | Environment Path Drift | Fixed | Hub root locked as System of Record |
| EC-006 | Missing Table (pattern_instances) | Fixed | Schema verified and patched |
| EC-007 | Script Dependency/Pathing | Fixed | Removed relative paths |
| EC-008 | CSV Data Transfer Failure | Fixed | Internal database hydration |
| EC-009 | Syntax/Line continuation errors | Fixed | Full scripts not one-liners |
| EC-010 | Operational Path Deviation | Fixed | Paths hardcoded to constants |
| EC-011 | Schema Version Mismatch | Fixed | Manual patch + parity verification |
| EC-012 | Data Parity Failure | Fixed | Hydration scripts |
| EC-013 | SQL Binding Syntax Error | Fixed | Python timedelta logic |
| EC-014 | Partial Code Delivery | Fixed | Full Artifact Rule enforced |
| EC-015 | PowerShell ExecutionPolicy block | Fixed | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| EC-016 | AI hallucinated chat-sandbox upload requirement | Fixed | Trust local directory structure; provide local commands |
| EC-017 | Rigid Lookback Horizon | Fixed | Dynamic DTW lookback up to 20 days |
| EC-018 | Time-Series Anchoring | Fixed | Single Anchor policy enforced |
| EC-019 | Polluted Stream Reporting | Fixed | Strict `data_origin_type='EVAL_SET'` filtering |
| EC-020 | Signal Interpretation Failure | Fixed | "No Match" = "Stay in Cash" explicitly |
| EC-021 | AI hallucinated column names | Fixed | Always request schema/DDL before SQL |
| EC-022 | Pipeline Drift — false 0.0 distances for non-SPY | Resolved in v2.0 | Normalization pre-computed on `pattern_bars` columns; cross-symbol matching valid by construction |
| EC-023 | Ingestion lacks idempotency | Fixed | `SELECT 1` pre-check; abort on duplicates |
| EC-024 | Pipeline lacks Fail-Fast | Fixed | `$LASTEXITCODE` checking in launchers |
| EC-025 | AI bypassed established .ps1 wrappers | Fixed | Strict wrapper invocation; no hallucinated scripts |
| EC-026 | Empty inbox doesn't trigger Fail-Fast | Fixed | `sys.exit(1)` if no files found |
| EC-027 | AI deleted core feature extraction in refactor | Resolved in v2.0 | Schema enforces NOT NULL FK to `feature_sets` and `source_files`; hollow records impossible |
| EC-028 | Unauthorized directory structures | Fixed | Adapt to operator paths; no new folders without approval |
| EC-029 | Sandbox/Deployment conflation | Fixed | Local-Verification Gate established |
| EC-030 | Code snippets instead of full files | Fixed | Hard rule: full files for non-trivial changes |
| EC-031 | DB file location assumption | Fixed | Hard-coded `models/` directory scan |
| EC-032 | Phase advancement without operator confirmation | Fixed | Wait for explicit operator confirmation |
| EC-033 | Dynamic column mapping masking vendor drift | Fixed | Strict schema validation; fatal halt on missing columns |
| EC-034 | False vendor-drift attribution | Fixed | Diagnostic re-focused on internal mapping |
| EC-035 | Schema mapping lessons not applied across phases | Fixed | Global translation layer in `ingest_manifest.json` |
| EC-036 | Code regression — solution dropped between phases | Fixed | Pre-Wash layer permanently hardcoded |
| EC-037 | Manifest path resolution mismatch | Fixed | Explicit `MANIFEST_PATH` verification with absolute path printout |
| EC-038 | NaN outcomes filter | Fixed | Aggregator auto-audit on error_count > 0 |
| EC-039 | NaN Handling | Fixed | Strict filter + print alerts |
| EC-040 | Indentation errors | Fixed | Monolithic code blocks |
| EC-041 | Import path / ModuleNotFoundError | Fixed | Absolute `sys.path` injection |
| EC-042 | Zombie records (null anchor dates) | Fixed | 16 purged + 30 orphans backfilled |
| EC-043 | Metadata oversight on file versions | Fixed | Echo VERSION + CHANGELOG before modification |
| EC-044 | Dependency desync in regression tests | Fixed | Tests self-contained or use utility modules |
| EC-045 | DataFrame column desync | Fixed | Dynamic `df.columns` check before access |
| EC-046 | Feature normalization on raw dollars | Resolved in v2.0 | Normalization pre-computed on `pattern_bars` |
| EC-047 | Directory map oversight | Fixed | Verify directory map before file-system commands |
| EC-048 | Feature normalization desync (duplicate of EC-046) | Resolved in v2.0 | Same as EC-046 |
| EC-049 | Directory map oversight (duplicate of EC-047) | Fixed | Same as EC-047 |
| EC-050 | Architectural drift / Legacy file conflict | Fixed | Manifest is sole source of truth for keys; purge live folder before conversion |
| EC-051 | Logical Blindness | Fixed | Verify `header=None` in Pandas; bypass VP metadata junk |
| EC-052 | Path Escaping | Fixed | `Path(r"...")` or forward slashes |
| EC-054 | Extension Blindness | Fixed | Target `.csv` only; ignore `.xlsx` in eval |
| EC-055 | Workflow Disparity | Fixed | Add Pattern = sequential write; Daily Eval = integrated read |
| EC-056 | Hardcoded Indices | Fixed | Use `P_010_RiskConfig.json` as global posture source |
| EC-057 | Database Orphans | Fixed | Post-ingest health check (Ghost vs Valid patterns) |
| EC-058 | Path Discovery | Fixed | `db_utils.get_latest_catalog()` mandatory |
| EC-059 | OneDrive Bridge | Fixed | Converter v6.8 dual-distributor pattern |
| **EC-060** | **Converter `df.tail(5)` truncation** | **Resolved in v2.0** | Removed in rebuild. Schema does not constrain bar count; window length is data not structure |
| **EC-061** | **v6.0 ingest TEXT in INTEGER `symbol_id` FK** | **Resolved in v2.0** | Schema FK constraint + symbols-table lookup before insert; rebuilt ingest enforces typed symbol_id |
| **EC-062** | **v6.0 ingest silently dropped `--type` argument** | **Resolved in v2.0** | Rebuilt ingest in `cli.py` uses `argparse` with required type discriminator |
| **EC-063** | **v6.0 ingest manifest targeted wrong table** | **Resolved in v2.0** | Manifest re-targeted to `pattern_bars` columns explicitly |
| **EC-064** | **v4.7 evaluator used mock data dictionary** | **Resolved in v2.0** | Pipeline B rebuilt against actual catalog queries; no mock data in production engines |
| **EC-065** | **Symbols table duplicate entries — observed: 'IVR' + 'History Grid (IVR)'** | **Resolved in v2.0** | Symbol parsing normalized to ticker-only; `UNIQUE` constraint enforced |
| **EC-066** | **OneDrive path hardcoded as `D:\OneDrive\...`** | **Resolved in v2.0** | `Path(os.environ["OneDrive"])` enforced per `python-project-architecture` skill |
| **EC-067** | **AI Workflow Conflation (Pipelines A & B merged in v1.16)** | **Resolved in v2.0** | Pipelines are structurally separate; merging is an architectural anti-pattern |

---

# 7. Enhancement Log

## Stage 3 — File System Cleanup + Empty New Schema (SEALED 2026-05-14)

Delivered (see `docs/migrations/STAGE_3_MIGRATION_LEDGER.md` for the forensic record):

- New folder structure (`domain/`, `infrastructure/`, `application/`, `archive/`, `tests/`, `tasks/`, `migrations/`)
- Archive 10 catalog variants + 4 converter versions + 3 aggregator versions + broken v6.0 ingest + broken v4.7 evaluator
- Empty `051426catalog.db` with 7-table schema
- `db_utils.py` glob update

## Stage 4 — Rebuild Pipeline A (Add Pattern) (SEALED 2026-05-15)

See `docs/migrations/STAGE_4_CLOSEOUT.md` for the full closeout report.

Delivered:

- `python/config.py` v1.1 (OneDrive removed; new constants for Stage 4 ingest)
- `python/schemas.py` v2.1 (full Pydantic models for every persistent type)
- `parameters/ingest_manifest.json` v2.0 (VP XLSX → `pattern_bars` column map)
- `python/domain/normalization.py` v1.0 (§9.3 formulas)
- `python/domain/labeler.py` v1.0 (5/7/10/15/20 forward labels)
- `python/infrastructure/vp_xlsx_reader.py` v1.0 (sheet-by-symbol parser)
- `python/utilities/vp_export_integrity_check.py` v1.0 (6-check post-VP-update diagnostic)
- `python/infrastructure/catalog_writer.py` v1.0.1 (insert API + Check-Out / Check-In)
- `python/infrastructure/verify_ingestion.py` v1.0 (hollow-record scan + atomic move)
- `python/application/add_pattern_pipeline.py` v1.0 (Pipeline A orchestrator)
- `python/utilities/catalog_summary.py` v1.0 (operator-facing catalog health check)
- `python/cli.py` v1.0 (unified entry point: add-pattern / catalog-summary / integrity-check)

Validated end-to-end on AAPL + OII XLSX exports. Cross-symbol normalization proven.

## Stage 5 — Re-Ingest Historical Patterns (ACTIVE)

- Pipeline A run against all `data/historical_patterns/*.csv` and `data/historical/Pattern_*.csv`
- Spot-check regression: compute forward labels by hand for one known pattern; verify pipeline output matches
- Multi-symbol from day 1 (~18 distinct symbols)

## Stage 6 — Rebuild Pipeline B (Daily Evaluate)

- Rebuilt `intelliscan.py` against new schema
- Rebuilt `aggregator.py` (v2.3 math + v1.9 output format)
- Rebuilt `P_300_EvaluateTrade.py` (deterministic, no mock data)
- Cross-symbol analog reporting

## Stage 7 — Local LLM Integration

- Wire LM Studio as dev assistant (code generation, doc updates)
- Wire LM Studio as post-decision narrator (BUY signal explanation)

## Milestone 5 — Trade Management Module (Planned)

Build module that consumes Aggregator output and produces position-sizing recommendations. Required inputs:

- Confidence / Win-Rate (drives position size — proposed mapping: 80% win rate → 2% risk; 60% win rate → 0.5% risk; final values set in Milestone 5)
- Expected Horizon (5/7/10/15/20-day return reliability)
- Drawdown Threshold (worst-historical-analog-based hard stop)

Risk-management style (fixed percentage, volatility-based trailing, time-based exits) to be selected before build.

---

# 8. AI Workflows & Processes

## 8.1 Session Bootstrap (Automated)

Replaces v1.x manual "read the doc first" rule.

1. **SKILL auto-loads** at session start (`p300-project-context\SKILL.md`)
2. **SIP runs INIT sequence** — account params from P_000, market posture from P_010, lessons from `tasks/lessons.md`, active task from `tasks/todo.md`
3. **Operator confirms session focus** before AI proposes work
4. **AI references architecture doc on demand** for full spec details

## 8.2 Pipeline A — Add Pattern (Write)

1. Operator drops `Pattern_<dates>_<symbol>.csv` files into `data/historical_patterns/`
2. Catalog Check-Out (verify state before write)
3. `application/add_pattern_pipeline.py` orchestrates:
   - Lock verify on master DB
   - Copy master → `temp_working.db`
   - Parse each CSV (`infrastructure/vp_csv_reader.py`)
   - Validate schema via `schemas.py` Pydantic models
   - Lookup or create `symbol_id` (`infrastructure/catalog_writer.py`)
   - Insert `source_files` row with filename + row_count
   - Insert `pattern_instances` row with `feature_set_id`, `source_file_id`, `window_length`, `data_origin_type='PATTERN_IDENT'`
   - Compute normalized values (`domain/normalization.py`)
   - Insert all `pattern_bars` rows with raw + normalized columns
   - Compute derived features (`domain/feature_engineering.py`)
   - Insert `pattern_features` rows
   - Compute forward labels (`domain/labeler.py`)
   - Insert `forward_labels` rows at all 5 horizons where data available
4. Verify temp DB integrity (`infrastructure/verify_ingestion.py`)
5. Atomic move temp → master
6. Archive processed CSVs → `data/archive/`
7. Catalog Check-In (verify delta + spot-check)

## 8.3 Pipeline B — Daily Evaluate (Read)

1. Operator drops `History Grid (<symbol>).csv` files into `data/live/`
2. Catalog Check-Out (read-only verification)
3. `application/daily_evaluate_pipeline.py` orchestrates:
   - Read P_010 risk posture
   - Parse each CSV
   - Compute candidate's normalized pattern_bars (in-memory, no DB write)
   - Run cross-symbol similarity search (`domain/similarity.py` + `infrastructure/catalog_reader.py`)
   - Aggregate matches by horizon (Z-score, win-rate, n)
   - Apply BUY/WATCH/PASS threshold logic (`domain/signal.py`)
   - Format report (`infrastructure/report_writer.py`)
4. Hand off signal + statistics to Local LLM for post-decision narration
5. Output combined report to terminal + optional file in `outputs/reports/`
6. Archive processed CSVs → `data/processed/`

## 8.4 Development Standards

### 8.4.1 Python Header Standard

Every Python file in the project must begin with:

```python
"""
FILE: <filename>.py
VERSION: <major.minor>
DATE: YYYY-MM-DD
AUTHOR: <author>
LAYER: <domain | infrastructure | application | config | schemas | cli | migration>
DESCRIPTION: <single-paragraph description>
CHANGELOG:
    - YYYY-MM-DD vX.Y: <change description>
"""
```

### 8.4.2 File Size Standards

- Hard limit: 300 lines per file
- Hard limit: 50 lines per function
- Split trigger: 250 lines

### 8.4.3 Dynamic Pathing Protocol

- No hardcoded DB paths anywhere except `config.py`
- All DB access through `db_utils.get_latest_catalog()`

### 8.4.4 Schema Discipline

Every persistent file read or write requires a Pydantic model in `schemas.py`. No exceptions for "simple" CSVs — Gemini-era drift began exactly with "this CSV is too simple to need a schema" calls.

### 8.4.5 No print() in Production Code

All output goes through the `logging` module. `print()` is permitted only in `cli.py` for direct operator-facing output.

### 8.4.6 Direct File Modification Standard

When filesystem MCP is available and a change to an existing file spans more than one line OR touches 2+ places, the AI performs the modification directly via filesystem MCP (`filesystem:edit_file` or `windows-mcp:FileSystem` write) rather than handing the operator text to paste. This applies to:

- Project Instructions, architecture docs, `tasks/lessons.md`, `tasks/todo.md`, SIP, SKILL — any project artifact
- Code files at any layer

Paste-style code blocks are reserved for cases where filesystem MCP is unavailable, or where the operator has explicitly asked for paste-ready output.

---

# 9. Data Design

## 9.1 Core Data Entities

- **Symbol** — Ticker identifier
- **Source File** — A specific CSV/XLSX import, tied to a symbol
- **Feature Set** — A named, versioned feature engineering definition. Current default: `baseline_v1`. Window-agnostic: window length lives in `pattern_instances.window_length`, not encoded in the feature_set name.
- **Pattern Instance** — One historical setup observation, anchored to a symbol + date + feature_set + source_file
- **Pattern Bar** — One bar of normalized + raw VP data at a specific offset from the anchor
- **Pattern Feature** — One derived (computed) feature value per pattern (window-level aggregates)
- **Forward Label** — Outcome at a specific horizon (5/7/10/15/20 days)

## 9.2 Canonical Schema (Production)

```sql
-- Identity & provenance
CREATE TABLE symbols (
    symbol_id INTEGER PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL
);

CREATE TABLE source_files (
    source_file_id INTEGER PRIMARY KEY,
    filename TEXT UNIQUE NOT NULL,
    symbol_id INTEGER NOT NULL,
    imported_at TEXT NOT NULL,
    row_count INTEGER NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id)
);

CREATE TABLE feature_sets (
    feature_set_id INTEGER PRIMARY KEY,
    feature_version TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

-- Pattern core
CREATE TABLE pattern_instances (
    pattern_instance_id INTEGER PRIMARY KEY,
    symbol_id INTEGER NOT NULL,
    source_file_id INTEGER NOT NULL,
    feature_set_id INTEGER NOT NULL,
    anchor_date TEXT NOT NULL,
    window_length INTEGER NOT NULL,
    data_origin_type TEXT NOT NULL,
    FOREIGN KEY (symbol_id) REFERENCES symbols(symbol_id),
    FOREIGN KEY (source_file_id) REFERENCES source_files(source_file_id),
    FOREIGN KEY (feature_set_id) REFERENCES feature_sets(feature_set_id)
);

-- Normalized window
CREATE TABLE pattern_bars (
    pattern_bar_id INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    bar_offset INTEGER NOT NULL,
    bar_date TEXT NOT NULL,
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
    pattern_feature_id INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    feature_value REAL,
    FOREIGN KEY (pattern_instance_id) REFERENCES pattern_instances(pattern_instance_id)
);

-- Outcomes
CREATE TABLE forward_labels (
    forward_label_id INTEGER PRIMARY KEY,
    pattern_instance_id INTEGER NOT NULL,
    horizon_days INTEGER NOT NULL,
    future_date TEXT,
    return_pct REAL,
    is_profitable INTEGER,
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
```

## 9.3 Normalization Formulas

Computed at ingest from raw `pattern_bars` data:

| Normalized Column | Formula | Purpose |
| :---- | :---- | :---- |
| `close_pct_from_anchor` | `(bar.close - anchor.close) / anchor.close` | Cross-symbol price-shape comparison |
| `range_pct` | `(bar.high - bar.low) / bar.close` | Cross-symbol volatility comparison |
| `body_pct` | `(bar.close - bar.open) / bar.open` | Cross-symbol candle-direction comparison |
| `volume_zscore` | `(bar.volume - window.volume_mean) / window.volume_std` | Volume anomaly detection across symbols |
| `stdiff_pct` | `bar.stdiff / bar.close` | Short-term momentum normalized to price |
| `mtdiff_pct` | `bar.mtdiff / bar.close` | Medium-term momentum normalized to price |
| `ltdiff_pct` | `bar.ltdiff / bar.close` | Long-term momentum normalized to price |
| `pred_high_pct` | `(bar.pred_high - bar.close) / bar.close` | Predicted high as % above close |
| `pred_low_pct` | `(bar.pred_low - bar.close) / bar.close` | Predicted low as % below close |
| `pred_range_pct` | `bar.pred_range / bar.close` | Predicted volatility normalized |

Already-unitless VP indicators (`psi`, `neural_index`, `williams_emai`, `triple_cross_*`) are not re-normalized — they are comparable across symbols as-is.

## 9.4 data_origin_type Values

- `PATTERN_IDENT` — Historical training pattern. Permanent. Used in similarity search.
- `EVAL_SET` — Today's evaluation candidate. Transient or clearly flagged. Excluded from similarity-search source population.

---

# 10. Testing & Validation

## 10.1 Testing Approach

- **Regression test:** Stage 5 spot-check — operator selects one known pattern, computes forward labels by hand from the source CSV, verifies pipeline output matches deterministically at all 5/7/10/15/20 horizons.
- **Schema integrity:** Every Pipeline A run produces a Check-In report; row-count deltas must match expected values from the source file batch.
- **No-mock-data audit:** Pipeline B output must include at least one query to the catalog. Mock dictionaries in production decision engines are forbidden.
- **Layer audit:** Static-check that no `domain/` file imports `sqlite3`, `requests`, or anything in `infrastructure/`.
- **Cross-symbol matching validation:** Spot-check a SPY candidate against historical NVDA patterns; verify distances are non-zero and well-distributed.

## 10.2 Validation Checklist

- Architecture doc version matches what the SKILL references
- SKILL auto-loaded at session start
- SIP INIT sequence ran successfully
- Catalog Check-Out completed before any work
- Layer separation enforced in any new code
- For writes: Lock verified, temp DB used, temp verified, atomic move completed, row count + schema version logged
- For reads: catalog state confirmed; no writes to historical tables
- Forward-label horizons computed at all five points where data available
- Cross-symbol normalization columns populated on every `pattern_bars` row

## 10.3 Known Issues / Limitations

| ID | Description | Severity | Workaround | Status |
| :---- | :---- | :---- | :---- | :---- |
| ID-001 | Context loss across new threads | High | SKILL auto-loads at session start | Controlled |
| ID-002 | Pipeline A not yet rebuilt | High | Stage 4 work | Active |
| ID-003 | Schema divergence between baseline and production | n/a | Resolved in v2.0 schema | Resolved |
| ID-004 | `verify_ingestion.py` not built | Medium | Manual verification with `inspect_catalog.py` / `inspect_labels.py` | Stage 4 |
| ID-005 | Gemini intra-thread context decay | High (historical) | Migrated off Gemini; Claude as primary architect | Mitigated |

---

# 11. Daily Operations & Session Management

## 11.1 Session Start Protocol

Automated by the SKILL + SIP. The operator does not need to manually instruct the AI to read the architecture. The SKILL contains the protection rules; the SIP runs INIT.

If the SKILL fails to load, the operator types `INIT` or `P_300 INIT` to manually trigger the SIP.

### 11.1.1 Environment Capability Discovery (Mandatory Step Zero)

Before executing any INIT logic, the AI MUST verify filesystem MCP capability via `tool_search`. Look for:

- `windows-mcp:FileSystem`
- `filesystem:read_text_file` / `filesystem:write_file`
- Any equivalent filesystem MCP server

Report capability in the session header instead of client identity:

- **"Filesystem MCP: available"** — proceed with live disk reads of `tasks/lessons.md`, `tasks/todo.md`, P_000, P_010 every session
- **"Filesystem MCP: unavailable"** — fall back to upload-and-download pattern

**Why this matters:** Claude.ai web, Claude Desktop with MCPs, and Claude Code present nearly identical system prompts. Client identity is not reliably detectable from the system prompt alone. Tool availability IS. Reporting capability (not client) prevents false ephemeral-environment claims when filesystem access is in fact available.

**Files read LIVE every session (never cached, never assumed stable across chats):**

| File | Update Cadence |
| :---- | :---- |
| `tasks/lessons.md` | Continuous during active build |
| `tasks/todo.md` | Every task completion |
| `P_000_Account_Parameters_Current.md` | Monthly |
| `P_010_RiskConfig.json` | Twice weekly |

**Wall-clock time:** If no shell or clock tool is available in the environment, display date only in the session header — never fabricate a time.

## 11.2 Maintenance

| Task | Frequency | Owner | Notes |
| :---- | :---- | :---- | :---- |
| Architecture review | Major change or weekly during active build | Anthony | Update version, status, stage roadmap |
| Error Log review | When issue repeats | Anthony | Promote into permanent rule |
| SKILL review | Quarterly or when protection rules change | Anthony | Keep rules concise |
| Catalog Check-In log review | After every DB write | Anthony | Confirm bracketing honored |
| Lessons review | Session start (via SIP) | AI | Load `tasks/lessons.md` |
| **VP export integrity check** | **After every VantagePoint version update** | **Anthony** | **Run `python/utilities/vp_export_integrity_check.py --xlsx <any-new-export>` BEFORE allowing any new XLSX into Pipeline A. Six checks; exit 0 = safe to ingest, exit 1 = update `parameters/ingest_manifest.json` and re-run.** |

## 11.3 Pre-Flight Audit (Mandatory for any code-producing response)

Before any response containing code, script generation, or architectural changes, the AI explicitly confirms:

- [ ] Artifact Complete — entire file/codeblock provided
- [ ] Path Resolved — dynamic pathing used; no hardcoded paths outside `config.py`
- [ ] Layer Discipline — file belongs to exactly one layer
- [ ] Schema Parity — Pydantic model exists if persistent file I/O involved
- [ ] Header Compliant — versioned header present per Section 8.4.1
- [ ] File Size — under 300 lines, functions under 50 lines

---

# 12. Troubleshooting & Support

## 12.1 Common Issues

### AI forgets prior discussion
- **Symptom:** New chat starts with incorrect assumptions or generic responses
- **Cause:** SKILL didn't auto-load OR SIP wasn't triggered
- **Fix:** Type `INIT` or `P_300 INIT` to manually trigger SIP

### Wrong stage focus
- **Symptom:** AI proposes work for a future stage
- **Cause:** Stage state in `tasks/todo.md` is stale
- **Fix:** Update `tasks/todo.md`; re-trigger SIP

### PowerShell `.ps1` script blocked
- **Symptom:** "File ... is not digitally signed"
- **Fix:** `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once per session

### Aggregator returns 0 rows or stale data
- **Cause:** Catalog Check-In skipped after ingest, or ingest failed silently
- **Fix:** Re-run Check-Out, verify counts, re-run ingest if needed, Check-In

### Master DB shows partial/corrupted state after failed write
- **Cause:** Direct write to master bypassing Lock + Temp-DB + Atomic Move
- **Fix:** Restore master from backup; re-run with temp-DB pattern

### Cross-symbol matching returns 0.0 distances (EC-022 recurrence)
- **Cause:** Normalization columns on `pattern_bars` not populated, OR matching engine reading raw columns instead of normalized
- **Fix:** Verify `pattern_bars` normalized columns are NOT NULL post-ingest; verify matching engine queries `close_pct_from_anchor` etc., not `close`

## 12.2 Escalation Path

| Level | Condition | Action |
| :---- | :---- | :---- |
| Self-correct | Minor drift | Restate architecture rule |
| Session reset | Repeated misunderstanding | Start new thread; SKILL re-loads |
| Documentation update | Issue repeats twice | Add permanent rule to this doc + SKILL |
| System redesign | Architecture no longer fits | Open enhancement item; revise structure |

---

# 13. Appendices

## Appendix A — Glossary

See Section 1.5.

## Appendix B — Related Documentation

| Document | Purpose |
| :---- | :---- |
| `p300-project-context\SKILL.md` | Session-start auto-load protection rules |
| `P_300_System_Initialization_Prompt_v2.md` | New-chat INIT bootstrap |
| `python-project-architecture\SKILL.md` | Hub-wide Python standards |
| `README.md` (P_000) | Hub foundation context |
| `Trading_Projects_Folder_Architecture.md` | Hub folder standards |

## Appendix C — Configuration Reference

| Item | Value |
| :---- | :---- |
| Shared Python Environment | p140 |
| Python Path | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| Hub Root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project Root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\` |
| Local LLM Endpoint | `http://localhost:1234/v1` |
| Local LLM Models | deepseek-r1-distill-qwen-14b (daily) / qwen2.5-coder-32b-instruct (batch) / llama-4-scout-17b-16e-instruct (long context) |
| Production Catalog DB | `models/<mmddyy>catalog.db` — resolved via `db_utils.get_latest_catalog()` |
| Working Temp DB | `models/temp_working.db` (transient) |
| PowerShell ExecutionPolicy (per session) | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |

## Appendix D — Document Control

| Field | Value |
| :---- | :---- |
| Document Owner | Anthony Zoppi |
| Classification | Internal |
| Template Version | UNIVERSAL_PROJECT_TEMPLATE_v1_1 |
| Review Schedule | At each stage transition + weekly during active build |

## Appendix E — Working Folder Map (Target State after Stage 3)

```
P_300_Vantage_Point_Pattern_Recognition/
├── data/
│   ├── live/                          (Pipeline B inbox — daily VP exports)
│   ├── processed/                     (Pipeline B archive)
│   ├── historical_patterns/           (Pipeline A vault)
│   └── archive/                       (cold storage)
├── docs/
│   ├── architecture/                  (P_300_System_Architecture_v2.0.md and successors)
│   └── prompts/                       (SIP and prompt library)
├── models/
│   ├── <mmddyy>catalog.db             (active catalog)
│   └── archive/                       (retired catalog variants)
├── parameters/
│   ├── optimization_config.json
│   └── ingest_manifest.json
├── python/
│   ├── config.py
│   ├── schemas.py
│   ├── domain/                        (business logic, no I/O)
│   ├── infrastructure/                (all I/O)
│   ├── application/                   (orchestration)
│   ├── cli.py
│   ├── launcher.bat
│   ├── requirements.txt
│   ├── migrations/                    (one-shot scripts)
│   └── utilities/                     (operator-facing helpers, db_utils, inspectors)
├── tests/                             (regression tests)
└── tasks/
    ├── todo.md
    └── lessons.md
```

## Appendix F — Prompt Library Entry

**P_300 SIP trigger:** Type `INIT` or `P_300 INIT` in a new chat. Skill loads protection rules automatically; SIP reads account params, market posture, lessons, and the current task queue.

## Appendix G — Versioning Convention

- `major.minor` for the architecture file
- **Major (v2.0, v3.0)** — structural or architectural redesigns (this rebuild)
- **Minor (v2.1, v2.2)** — meaningful non-breaking additions
- **Patch-level** changes are inline edits not bumped versions

## Appendix H — Trade Management (Milestone 5 Planning)

### Trading Logic & Rules (P_030 reference)

- BUY requirement: 100% Buy rating across 20, 50, 100, 200-day moving averages
- Risk budget: Standard $525 (1.5% of $35k account)
- Size penalty: 200MA penalty sizing if price is below 200MA
- Liquidity floor: Spread ≤ 10%, Open Interest ≥ 150

### Milestone 5 Trade Management Module

Consumes Aggregator output from Pipeline B. Three required inputs:

| Input | Purpose | Example Mapping |
| :---- | :---- | :---- |
| Confidence / Win-Rate | Position size driver | 80% win rate → 2% risk; 60% win rate → 0.5% risk |
| Expected Horizon | Hold-period selection | Pick the day (5/7/10/15/20) with most reliable historical return |
| Drawdown Threshold | Hard stop-loss placement | Set stop based on worst-historical-analog drawdown |

Risk-management style (fixed percentage, volatility-based trailing, time-based exits) to be selected before build.

---

**End of P_300 System Architecture v2.2**
