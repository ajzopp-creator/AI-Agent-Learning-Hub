# P_300 — VantagePoint Pattern Recognition System Architecture

**Project ID:** P_300
**Version:** 2.7
**Last Updated:** 2026-05-20
**Maintained By:** Anthony Zoppi
**Status:** Active / Stages 6/7/8/9 Sealed / Stage 9-followup volatility-divergence flag shipped 2026-05-20 / Milestone 6 (Trade Management) Planned

---

## Documentation Decision Protocol

This document is the **master architecture reference** for the P_300 project. New P_300 documentation belongs here first unless content is long-form, frequently updated, reused across projects, or needs separate version history. Separate files are referenced back from this document and named to the project convention.

**Session bootstrap is handled automatically by two mechanisms:**

1. **`p300-project-context` SKILL** at `C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\p300-project-context\SKILL.md` — auto-loads on the first prompt of any P_300 chat. Contains concise protection rules, anti-patterns, schema shorthand, critical paths.
2. **System Initialization Prompt (SIP)** at `docs/prompts/P_300_System_Initialization_Prompt_v2.md` — runs the INIT sequence (account params, market posture, lessons.md, current task queue, live catalog state).

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
- Position-sizing recommendation based on confidence + risk config (Milestone 6)

**What this system does not cover:**

- Automated live brokerage execution
- Enterprise data engineering infrastructure
- Long-horizon portfolio optimization
- Non-pattern-based discretionary analysis

## 1.3 Project Details

| Field | Value |
| :---- | :---- |
| Start Date | 2026 Q1 build phase |
| Current Status | Stages 7/8/9 ALL SEALED 2026-05-19 in a triple closeout. Catalog: 25 symbols / 25 patterns / 500 bars / 125 forward_labels / 0 hollow / OVERALL: HEALTHY. Pipeline A (Add Pattern) + Pipeline B (Daily Evaluate) + Post-Decision Narrator all production-shipped. ID-007 small-catalog signal caveat RESOLVED — BUY structurally reachable at all 5 horizons. Stage 9 ablation/sweep utilities delivered with sparse-N caveat (re-run at N >= 50 backlogged). Stage 9-followup (2026-05-20): post-classification volatility-divergence flag (range_pct-based, Decision B preserved) + both operator process runbooks (`docs/processes/evaluate_trade.md`, `docs/processes/add_pattern.md`) shipped. Next architectural milestone: Milestone 6 Trade Management Module (planned; gated on live P_300 trading first). |
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
       Pattern_*.xlsx                 History Grid (*).xlsx
              |                            |
              v                            v
        Pipeline A: Add                Pipeline B: Daily
        Pattern (WRITE)                Evaluate (READ-ONLY)
              |                            |
              v                            v
      Normalize → Ingest →           In-memory candidate →
      Features → Labels              similarity → aggregate →
              |                      signal: BUY/WATCH/PASS
              v
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
| Source | `data/historical_patterns/` (filename pattern `Pattern_YYYYMMDD_YYYYMMDD_SYMBOL.xlsx`) |
| Transaction safety | Lock + Temp-DB + Atomic Move (Section 2.6) |
| Verification | Post-ingest health check (Ghost Patterns vs. Valid Patterns) |
| Failure mode | Halt + rollback to last verified state |

Pipeline A grows the long-term mathematical "DNA" library. Quality over speed. Every write is bracketed by Catalog Check-Out → operation → Catalog Check-In.

### Pipeline B — Daily Evaluate

| Property | Value |
| :---- | :---- |
| Direction | READ-ONLY — queries the catalog; no writes to historical tables; no EVAL_SET inserts (Decision E, Stage 6) |
| Primary tempo | Fast, integrated, real-time decision support |
| Source | `data/live/` (filename pattern `History Grid (<symbol>).xlsx` per M-010 instance #3) |
| Output | Inline terminal report with BUY/WATCH/PASS signal per symbol; optional file output to `outputs/reports/` |
| Failure mode | Fail to "PASS" (no trade) — never silently produce a BUY |

Pipeline B is the decision engine. Live candidates are normalized in-memory and matched against the historical training pool (`data_origin_type='PATTERN_IDENT'`); no EVAL_SET rows are persisted to `pattern_instances` (Decision E, locked at Stage 6 start — revisit if the Stage 8 narrator, SEALED 2026-05-19, eventually wants a persistence hook for "today's signal history").

### Anti-Pattern: Workflow Conflation

The two pipelines must NEVER be merged into a single script. Gemini-era v1.16 attempted this and produced four hours of drift work. Sequential safety (Pipeline A) and integrated speed (Pipeline B) are different design constraints; mixing them corrupts both.

## 2.3 Layer Architecture (Hub Standard)

The Python codebase follows the Hub-wide clean-architecture standard. Every Python file belongs to exactly one layer:

```
python/
├── config.py              ← All constants and paths
├── schemas.py             ← Pydantic models for Pipeline A persistent file I/O
├── schemas_pipeline_b.py  ← Pydantic models for Pipeline B (in-memory)
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
- **`infrastructure/`** — All file reads/writes, SQLite queries, network calls. NO business logic. Returns raw data to the application layer. Examples: catalog reader/writer, VP XLSX parser, P_010 risk config loader.
- **`application/`** — Orchestration only. Calls domain functions and infrastructure functions in sequence. Contains the workflow logic. NO raw business logic. NO direct I/O. Examples: `run_add_pattern_pipeline()`, `run_daily_evaluate()`.
- **`config.py`** — All constants, paths, thresholds. Single source of truth. Imported by every layer that needs a value.
- **`schemas.py` + `schemas_pipeline_b.py`** — Pydantic models for every CSV, JSON, DB read/write that persists between runs, plus in-memory Pipeline B types. Schema validation at the data boundary, not after corruption. Two files exist to honor the §8.4.2 300-line file-size limit; `schemas_pipeline_b.py` was split out at Stage 6 (DEBT NOTE: NormalizedBar / PatternBarRecord share columns and are Backlog candidates for a shared-base refactor).

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

For Pipeline B (READ-only per Decision E), Check-In verifies the catalog is UNCHANGED — no EVAL_SET leakage into `pattern_instances`.

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
- **Module file in `domain/` / `infrastructure/` / `application/` sharing a name with a Python stdlib module.** Script-mode invocation prepends script's directory to `sys.path[0]`; downstream `import <stdlib_name>` finds the local file first and raises cryptic circular-import errors that point at third-party libraries instead of the real cause. (Source: EC-068 / M-018; Stage 6 `signal.py` → `signal_classifier.py` rename.)
- **Unicode characters in any string flowing through Python stdout when invoked from PowerShell.** PowerShell stdout default encoding is cp1252; box-drawing (`═`, `─`, `│`), em-dashes (`—`), and arrows (`→`) crash with `UnicodeEncodeError`. ASCII-only on stdout (`=`, `-`, `|`, `--`, `->`); Unicode is safe only in file writes via explicit `encoding="utf-8"`. (Source: EC-069 / M-019; Stage 6 `report_writer.py` v1.0 → v1.1.)
- **Treating `forward_labels.return_pct` as a percentage.** Storage convention is decimal fraction (0.0672 represents 6.72%); display layer multiplies by 100. Internal callers (aggregator, signal_classifier) operate in decimal space; only the render boundary converts. (Source: EC-070 / M-020; Stage 6 `report_writer.py` v1.1 hotfix.)

---

# 3. AI Tools & Platforms

## 3.1 Tool Stack

| Tool / Platform | Role | Notes |
| :---- | :---- | :---- |
| Python (p140 conda env) | All runtime logic — deterministic | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| SQLite | Pattern catalog database | One DB per active baseline (`mmddyycatalog.db`) |
| VantagePoint | Historical and live market data source | Vendor — may drift; schema protects us |
| Claude | Architect + Code Author | Writes all Python; reviews architecture changes |
| Local LLM (LM Studio) | Dev Assistant + Post-Decision Narrator (Stage 8, SEALED 2026-05-19) | Never in the runtime decision path |
| DB Browser for SQLite | Visual catalog inspection | Used during Check-Out verification |
| PowerShell ISE | Workflow orchestration | Hosts the launcher wrappers; profile prepends p140 to PATH (M-016) |
| `windows-mcp:FileSystem` MCP | Direct file writes Claude → Hub | Eliminates download-and-move pattern |
| `windows-mcp:PowerShell` MCP | Catalog state queries at INIT Step 5b | Subject to ~4-min subprocess timeout; live validation falls back to operator-run pattern |

## 3.2 Local LLM Split (Critical)

The Local LLM is split into two roles with a hard boundary between them:

- **Dev Assistant role** — generates Python code, reviews architecture, answers documentation questions. Runs during development. Output is reviewed by the operator before being committed.
- **Post-Decision Narrator role** — after the deterministic pipeline produces a BUY/WATCH/PASS signal with statistics, the Local LLM generates a human-readable summary ("Today's BUY on SPY is driven by 12 historical analogs averaging 4.2% over 7 days, strongest match from 2024-11-14 which returned 5.8%"). Runs at the end of Pipeline B (Stage 8 wiring, SEALED 2026-05-19 — see §7 Stage 8 closeout; NFR-1 boundary preserved by computing signal class BEFORE any LLM call).

**The Local LLM is NEVER in the BUY/WATCH/PASS decision logic.** Same SPY data must always produce the same signal. Determinism is non-negotiable for trading decisions. (See Gemini-era failures EC-022, EC-027, ID-005 for what happens when LLMs leak into the runtime path. NFR-1 verified 2026-05-18 in Stage 6 determinism test.)

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
11. **Call `tool_search` at session start** to discover filesystem MCP capability (`windows-mcp:FileSystem`, `windows-mcp:PowerShell`, `filesystem:read_text_file`, or equivalent) BEFORE concluding the environment is ephemeral
12. When filesystem MCP is available, **perform file modifications directly via MCP** — do not hand the operator text to paste for any change spanning 2+ lines or 2+ places
13. **Refuse to propose new ingest or catalog-touching work until INIT Step 5b catalog reconciliation has run clean.** Catalog DB is ground truth; tracking docs describe it (M-017, embedded in SKILL Must #13)

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
13. **Trust tracking docs (`todo.md`, `lessons.md`) over the live catalog DB on conflict.** Catalog wins (M-017, embedded in SKILL Must Not #13)

---

# 4. Requirements

## 4.1 Functional Requirements

| ID | Description | Component | Status |
| :---- | :---- | :---- | :---- |
| FR-1 | Ingest VantagePoint history-grid data into structured pipeline | Pipeline A | Complete (Stage 4) |
| FR-2 | Compute repeatable pattern features with cross-symbol normalization | `domain/` + Pipeline A | Complete (Stage 4) |
| FR-3 | Maintain SQLite pattern catalog with 7-table normalized schema | Schema | Complete (Stage 3) |
| FR-4 | Generate forward profitability labels at 5/7/10/15/20 day horizons | Pipeline A | Complete (Stage 4) |
| FR-5 | Support multi-symbol from day 1 | Schema + Matching | Built-in to schema |
| FR-6 | Bootstrap each session via SKILL + SIP | Session control | Complete (Stage 3); catalog reconciliation added Stage 6 start (SIP v2.4 Step 5b) |
| FR-7 | Batch XLSX processing through Pipeline A | Pipeline A | Complete (Stage 4) |
| FR-8 | Catalog Check-In / Check-Out bracketing on every DB operation | All scripts | Procedural rule |
| FR-9 | Lock + Temp-DB + Atomic Move on writes to canonical DB | Pipeline A | Complete (Stage 4) |
| FR-10 | Cross-symbol similarity matching with percentage normalization | Pipeline B | Complete (Stage 6) |
| FR-11 | BUY / WATCH / PASS signal output with Z-score confidence | Pipeline B | Complete (Stage 6) |
| FR-12 | Local LLM post-decision narrative generation | Pipeline B (final step) | Complete (Stage 8 SEAL 2026-05-19) |
| FR-13 | Position-sizing recommendation from confidence + risk config | Pipeline B | Milestone 6 (planned) |

## 4.2 Non-Functional Requirements

- **NFR-1 Determinism:** Same input data must always produce the same signal output. No LLM in the runtime decision path. (VERIFIED 2026-05-18 in Stage 6 determinism test — two `daily-evaluate` runs on the same SPY XLSX produced identical output: composite=12.7997 both times, all stats identical to 3 decimals, same signal class + chosen horizon.)
- **NFR-2 Auditability:** Every pattern in the catalog must be traceable to a source file via `source_files`.
- **NFR-3 Schema integrity:** No hollow records possible. NOT NULL constraints + FK constraints + atomic ingest.
- **NFR-4 Layer separation:** Code is structurally organized so concerns cannot silently mix.
- **NFR-5 Vendor-drift resilience:** VP export format changes are contained to the manifest layer.
- **NFR-6 Reproducibility:** Forward labels at 5/7/10/15/20 horizons computed deterministically from market data. Stage 5 validation is a manual spot-check of one known pattern — compute labels by hand, verify pipeline output matches exactly. (VERIFIED 2026-05-16 on AAPL pattern_id=1; all 5 horizons match XLSX Close to 4 decimals. RE-VERIFIED 2026-05-18 as Stage 6 regression replay; Pipeline A untouched by Pipeline B build.)

## 4.3 Requirements Matrix

See FR table above. Status reflects Stage 6 closeout; implementation tracking in `tasks/todo.md`.

---

# 5. Change Log

## v2.7 — 2026-05-20 — Stage 9-followup: Volatility Divergence Flag + Process Runbooks

- **Post-SEAL feature delivery (NOT a stage transition).** Stages 1-9 all remain SEALED. Volatility-divergence flag attaches as post-classification metadata on SignalReport without touching the Stage 6 Decision B distance computation or the Stage 6 Decision F BUY/WATCH/PASS gate. NFR-1 preserved end-to-end (verified against live SPY 2026-05-19: signal byte-identical to Stage 7 SEAL output).
- **Audit-driven design choice.** Stage 9 ablation showed `range_pct` carries signal. A fresh cap-sensitivity audit (`utilities/cap_sensitivity_audit.py` v1.0 NEW, ~125 lines) ranked all 17 raw + 10 normalized fields by per-symbol stdev of medians. Among normalized fields, `range_pct` is the cleanest cap/volatility-class axis (OII ~0.046 vs SPY ~0.009, ~5x ratio; monotonic with cap-proxy ordering). `volume_zscore` has larger dispersion but encodes volume regime, not cap; `close_pct_from_anchor` encodes trend bias. `range_pct` therefore became the divergence axis. Audit also confirmed `triple_cross_short/medium/long` are PRICE LEVELS (dispersion identical to OHLC ~242), not crossover signals — documentation in older notes mentioning 16 raw VP fields was off-by-one; actual count is 17 (Backlog cleanup).
- **Post-filter, not pre-filter, not extend-space.** Pre-filter (cap/sector exclusion before similarity) dies at N=25 (GLP alone in small-cap). Extend-space (add `range_pct` as an 11th `SIMILARITY_FEATURE`) would change Decision B. Post-classification metadata leaves the signal class unchanged and surfaces the cap/volatility apples-to-oranges concern alongside the BUY/WATCH/PASS verdict.
- **Severity thresholds locked at v1.0.** NONE < 1.5x, MILD [1.5, 2.0), STRONG ≥ 2.0x ratio between candidate-window median range_pct and top-K median range_pct (symmetric max/min). Aggregation per match: median-of-medians weighting matches equally regardless of window_length 5-20. Degenerate input (either median 0.0) returns severity NONE with ratio 1.0. Three production runs (SPY/BBY/CNX 2026-05-19) verified end-to-end: SPY STRONG ratio 2.73 against high-vol top-K (TTD/AMD/PLTR/GLP); BBY NONE ratio 1.24 against mixed top-K; CNX PASS h=7 with narrator pass clean.
- **7 files delivered.** `schemas_pipeline_b.py` v1.1 → v1.2 (added `Severity` enum + `VolatilityDivergence` model + optional `volatility_divergence` field on `SignalReport` + `_volatility_divergence_consistency` model_validator); `domain/volatility_divergence.py` v1.0 NEW (220 lines, pure compute, no I/O); `application/daily_evaluate_pipeline.py` v1.1 → v1.2 (new Stage 5b between classification and SignalReport construction; uses match bars already in memory from Stage 2 bulk_load — no DB re-query; SignalReport constructed via full `Model(**fields)` NOT `model_copy(update=...)` per M-021 so consistency validator fires); `infrastructure/report_writer.py` v1.2 → v1.3 (new `_build_volatility_section` between matches table and narrative — NONE = omitted, MILD = 2-line block, STRONG = labeled block with medians + n_topk_matches + apples-to-oranges note; ASCII-only on stdout per M-019); `utilities/cap_sensitivity_audit.py` v1.0 NEW; `docs/processes/evaluate_trade.md` v1.0 NEW (Pipeline B operator runbook; decision tree built around signal_class × volatility_severity matrix; sizing rules deferred to P_000/P_010); `docs/processes/add_pattern.md` v1.0 NEW (Pipeline A operator runbook; four-step integrity-check → add-pattern → catalog-summary → inspect-pattern sequence).
- **New `docs/processes/` directory convention.** Operator runbooks (per-workflow procedural documentation) live here, distinct from `docs/architecture/` (this file + successors), `docs/migrations/` (stage closeout reports), and `docs/prompts/` (SIP). Appendix E folder map updated.
- **New lessons in `tasks/lessons.md`:** M-030 (`windows-mcp:PowerShell` + `python -c` with embedded code hangs the MCP server reliably — fall back to operator-run-in-ISE pattern; M-019 covers stdout-encoding-out, M-030 covers invocation-in); M-031 (file-size accretion crossing §8.4.2 is a signal to split, not a license to slim docstrings — three current breaches identified: schemas_pipeline_b.py 408, daily_evaluate_pipeline.py 417, report_writer.py 373; promote to SKILL anti-pattern if a fourth file breaches in next 1-2 sessions); M-019 extension (PowerShell `>` redirection encodes UTF-16 LE by default regardless of Python stdout encoding — workaround: `Out-File -Encoding utf8`, `Set-Content -Encoding utf8NoBOM`, or `open(...,encoding="utf-8")` in Python).
- **§8.4.2 file size standard clarified.** When a file legitimately outgrows the 300-line budget through feature accretion (each line carrying weight), the answer is to SPLIT at a natural boundary, not to compress docstrings to fit. `schemas_pipeline_b.py` DEBT NOTE expanded to name the proper split (`schemas_pipeline_b_bar.py` + `schemas_pipeline_b_report.py`) and pair it with the NormalizedBar shared-base refactor. Both the split and the refactor remain Backlog.
- **`docs/archive/P_300_System_Architecture_v2.6.md`** — prior major version preserved.
- **SIP v2.6 → v2.7 and SKILL alignment** in flight this session; this file (v2.7) lands first, then SIP, then SKILL.

## v2.6 — 2026-05-19 — Stage 7 + 8 + 9 Triple Closeout

- **Stages 7, 8, 9 ALL SEALED 2026-05-19** in a single closeout. Stage 7 broke the small-catalog signal block (ID-007 RESOLVED); Stage 8 wired the LM Studio Post-Decision Narrator with NFR-1 preserved; Stage 9 delivered parameter sweep + outcome attribution utilities with sparse-catalog interpretation caveats. Full Stage 7/8/9 details in §7.
- **Stage 7 — Broader Catalog Ingest.** 20 symbols ingested across two sessions (2026-05-18 + 2026-05-19). Final catalog: 25 patterns / 25 symbols / 25 source_files / 500 pattern_bars / 125 forward_labels / 0 hollow / OVERALL: HEALTHY. Baseline win-rates dropped to 0.50-0.60 range at all 5 horizons (was 1.0 at 4 of 5 at Stage 6 SEAL — ID-007 spec). All 4 success criteria green: clean 20-of-20 ingests, catalog totals match target, baselines drop below 1.0 at every horizon (EXCEEDS spec which required ≤2 stuck at 1.0), NKE id=14 hand-compare clean to 4 decimals on all 5 forward closes.
- **Stage 8 — Local LLM Integration.** 5 files: `infrastructure/llm_client.py` v1.0 NEW (~8 KB), `domain/narrator_prompt.py` v1.0 NEW (system prompt + user-prompt builder), `config.py` v1.2 → v1.3 (`NARRATOR_ENABLED` kill-switch + LM Studio endpoint/timeout), `application/daily_evaluate_pipeline.py` v1.0 → v1.1 (narrator wired AFTER `classify_signal()` — NFR-1 preserved), `cli.py` v1.2 → v1.3 (`--no-narrator` flag). All narrator failure modes (LM Studio down, timeout, HTTP error, R1 truncation, malformed JSON) return `None` cleanly; signal unaffected. Determinism replay green: signal class + per-horizon stats identical across runs; narration MAY differ (acceptable since post-decision).
- **Stage 9 — Parameter Sweep + Outcome Attribution.** 3 utilities + 3 CSV outputs. `utilities/threshold_sweep.py` v1.0 NEW (~11 KB) — grid-search BUY/WATCH thresholds. `utilities/feature_ablation.py` v1.0 NEW (~10 KB) — leave-one-feature-out across the 10 `SIMILARITY_FEATURES`. `utilities/loo_replay.py` v1.0 NEW (~12 KB) — leave-one-pattern-out across the 25 catalog patterns. Findings: `volume_zscore` / `close_pct_from_anchor` / `ltdiff_pct` carry signal (largest d_precision when removed); `body_pct` likely noise (precision improves on removal); `stdiff_pct` / `pred_high_pct` / `pred_low_pct` / `pred_range_pct` show identical d_precision (correlated cluster sharing `bar.close` denominator per §9.3 — treat as ~1 effective feature in future weighted schemes). Small-N caveat alive (8 baseline BUYs at the relaxed grid); findings directional, not definitive. Re-run after catalog >= 50 (Backlog).
- **ID-007 (small-catalog signal caveat) flipped Open → Resolved.** BUY (z > 1.0) is now structurally reachable at every horizon. §10.3 row updated.
- **Stage numbering shift codified.** v2.5 had Stage 7 = Local LLM Integration; v2.6 restructures: Stage 7 = Broader Catalog Ingest (sealed this version), Stage 8 = Local LLM Integration (sealed this version), Stage 9 = Parameter Sweep + Outcome Attribution (sealed this version). Milestone 5 (Trade Management Module) renumbered to Milestone 6 per operator directive at Stage 6 SEAL (gated on live P_300 trading first). All cross-references updated through §1.2, §4.1 FR-13, §3.2, §13 Appendix H, and Stage 6 internal references to "Stage 8 parameter sweep" → "Stage 9 parameter sweep."
- **New lessons in `tasks/lessons.md`:** M-022 (target=anchor workflow lock), M-023 (VP license/access constraints + thesis-flexible substitution), M-024 (filename date format strict YYYYMMDD; no capture-date sanity check), M-025 (CWD discipline + folder convention drift), M-026 (date-validity pre-checks for AI-generated pick lists), M-027 (cost-estimate discipline: measure or admit unknown), M-028 (parameter sweeps on sparse catalogs must bracket firing region), M-029 (don't interpret domain data without confirming domain semantics — companion to M-027 for interpretation discipline).
- **New Backlog section in §7** — captures items surfaced this seal but not on the critical path: re-run sweep + ablation at N >= 50 (M-028 retire trigger); NormalizedBar / PatternBarRecord shared-base refactor; `return_pct` schema field rename to `return_fraction` / `return_decimal` (M-020 cleanup); date-validity pre-check utility (M-026); legacy 14-symbol Gemini CSVs; recover 10 singleton symbols (HL/IPI/ICE/POET/TXRH/DELL/DNN/ASTS/ESVIF); PEAK-anchor framing as second ingest pass; real-time intraday evaluation mode; skill consolidation (O-005).
- **`docs/archive/P_300_System_Architecture_v2.5.md`** — prior major version preserved.
- **SIP v2.5 → v2.6 and SKILL alignment** in progress this same session; this file (v2.6) lands first, then SIP, then SKILL alignment.

## v2.5 — 2026-05-18 — Stage 6 Closeout

- **Stage 6 SEALED 2026-05-18.** Pipeline B operational end-to-end against real live SPY XLSX. 10 of 10 files delivered. All three success criteria green: determinism (two runs identical), self-match sanity (SPY ranks #1 against live SPY at composite 12.80, QQQ second at 16.70), Stage 5 regression replay (AAPL `inspect-pattern --id 1` produces 4-decimal match on all 5 horizons; Pipeline A untouched by Stage 6 build). Catalog state: 5 symbols / 5 patterns / 100 bars / 25 forward_labels / 0 hollow / OVERALL: HEALTHY.
- **Six architectural decisions locked 2026-05-16, authoritative for downstream parameter sweeps:**
  - A — Legacy file decomposition: `matching/intelliscan.py`, `reporting/aggregator.py`, `utilities/P_300_EvaluateTrade.py` retired; work decomposed into clean-architecture layout
  - B — Distance function: DTW per-feature, equal-weight summed across the 10 normalized `pattern_bars` columns; per-feature weighting deferred to Stage 9 parameter sweep (SEALED 2026-05-19)
  - C — Top-K matches: 20 historical analogs per candidate; configurable in `config.py`
  - D — Output horizons: all 5 (5/7/10/15/20) per candidate; operator picks hold period when sizing
  - E — EVAL_SET handling: transient in-memory only; no inserts to `pattern_instances`
  - F — BUY/WATCH/PASS thresholds: AND-gate (BUY n≥5 + win_rate≥0.70 + z>1.0; WATCH n≥3 + win_rate≥0.60 + z>0.0; else PASS)
- **Stage 6 file roster (final, 10 deliveries):** `config.py` v1.1 → v1.2 (Pipeline B constants); `schemas_pipeline_b.py` v1.0 NEW (7 Pydantic models, sibling to `schemas.py` for §8.4.2 file-size limit); `infrastructure/catalog_reader.py` v1.0 NEW (read-only query API); `domain/similarity.py` v1.0 NEW (pure-Python DTW + composite distance + ranking); `domain/aggregator.py` v1.0 NEW (per-horizon stats + two-proportion z-score with degenerate-baseline guards); `domain/signal_classifier.py` v1.0 NEW (Decision F AND-gate + cross-horizon arbiter; originally `signal.py`, renamed mid-stream per M-018); `infrastructure/report_writer.py` v1.0 → v1.1 (terminal + file output, ASCII-only stdout per M-019, `return_pct` × 100 at display boundary per M-020); `infrastructure/vp_xlsx_reader.py` v1.0 → v1.1 (added `parse_live_file()` for `History Grid (SYMBOL).xlsx`; Stage 4 path untouched); `application/daily_evaluate_pipeline.py` v1.0 NEW (Pipeline B orchestrator); `cli.py` v1.1 → v1.2 (added `daily-evaluate` subcommand; CLI now exposes 5 subcommands).
- **File plan grew 9 → 10 mid-stream.** Original assumption that the existing `vp_xlsx_reader.py` regex would match `History Grid (*).xlsx` was wrong (regex was `^Pattern_*`). File #8 split into File #8a (`vp_xlsx_reader` v1.1 extended) + File #8b (orchestrator). Option A taken (extend existing file); planned `live_csv_reader.py` deleted.
- **Small-catalog signal caveat documented.** All 5 POC patterns are profitable at horizons 5/7/10/15, so baseline win-rate = 1.0 makes the two-proportion `z_score` denominator degenerate. BUY (requires z > 1.0) is structurally unreachable at 4 of 5 horizons until the broader 14-symbol historical set is ingested (Backlog, flagged "critical for unblocking BUY signals" in `tasks/todo.md`). Only horizon 20 (baseline 0.8) admits a finite z. Classifier + matcher math is correct; signal gating is gated by catalog diversity. Captured as ID-007 in §10.3.
- **New EC entries in Section 6:** EC-068 (stdlib `signal.py` collision; resolved by `signal_classifier.py` rename), EC-069 (PowerShell cp1252 stdout Unicode crash in `report_writer.py` v1.0; resolved by ASCII-only convention), EC-070 (`report_writer.py` v1.0 displayed `return_pct` × 1 instead of × 100; resolved in v1.1 hotfix).
- **Three new anti-patterns in Section 2.7** promoted from M-018, M-019, M-020: stdlib-name collisions in `domain/` / `infrastructure/` / `application/`; Unicode characters in stdout from PowerShell; treating `return_pct` as a percentage instead of a decimal fraction. Anti-patterns also added to SKILL Section "Anti-Patterns (Forbidden by Construction)" in v2.4 → v2.5 alignment this session.
- **New lessons in `tasks/lessons.md`:** M-018 (stdlib-name collisions), M-019 (PowerShell cp1252 stdout / ASCII-only), M-020 (`return_pct` decimal-fraction storage convention), M-021 (Pydantic v2 `model_copy(update=...)` skips re-validation; correct pattern for negative validator tests), M-010 instance #3 (CSV → XLSX live format standardization), M-011 extension (Python warnings — not just `logging` — render as red `NativeCommandError` in PowerShell; defenses include forward-slash literals and `warnings.filterwarnings`). M-016 + M-017 STRUCTURALLY EMBEDDED markers added to existing entries (M-016 in SKILL v2.4 Critical Paths + Workstation Resolution subsection; M-017 in SIP v2.4 Step 5b + SKILL v2.4 Must #13).
- **Pipeline B Layer Flow narrative** added to §8.3 documenting the canonical module call order for daily evaluation; layer separation (Section 2.3) is what makes the pipeline auditable.
- **ID-006 (INIT trusts tracking docs over live catalog state)** flipped from Open → Resolved. M-017 STRUCTURALLY EMBEDDED in SIP v2.4 Step 5b (catalog reconciliation via `python cli.py catalog-summary` + mtime check + symbol-set divergence halt) + SKILL Must #13 + Must Not #13.
- **FR-3 wording cleanup:** "8-table" → "7-table" (vestigial wording missed in v2.2 cleanup pass; corrected here). Schema unchanged.
- **§2.3 Layer Architecture diagram updated** to show `schemas_pipeline_b.py` sibling to `schemas.py` (Stage 6 split for §8.4.2 file-size limit). DEBT NOTE preserved: NormalizedBar / PatternBarRecord share columns and are Stage 8 shared-base refactor candidates.
- **§3.1 Tool Stack updated** to reference `windows-mcp:PowerShell` (INIT Step 5b prerequisite per M-017) and the ~4-min subprocess timeout that drives the operator-run live validation pattern adopted in Stage 6.
- **`docs/archive/P_300_System_Architecture_v2.4.md`** — prior major version preserved.
- **SIP v2.4 → v2.5 and SKILL v2.4 → v2.5 alignment** in progress this same session; this file (v2.5) lands first, then SIP and SKILL.

## v2.4 — 2026-05-16 — Stage 5 Closeout

- **Stage 5 SEALED 2026-05-16.** All 5 POC symbols ingested clean (AAPL, OII, SPY, QQQ, NVDA), pipeline math regression-verified on AAPL id=1, catalog OVERALL: HEALTHY (0 hollow records). All four Stage 5 success criteria green. Broader 14-symbol historical set (MSFT, CTRA, ATGE, VOD, CME, TR, LYV, FSLY, NFLX, APPN, BRK_A, ITA, MSA, PG) moved to backlog — not a Stage 5 blocker.
- **Stage 5 deliverables this session:**
  - `python/utilities/inspect_pattern.py` v1.0 (231 lines, 10.5 KB) — read-only single-pattern inspector with hand-compare `implied_future_close` column; AST-validated; tested on AAPL id=1
  - `python/cli.py` v1.0 → v1.1 — added `inspect-pattern --id N` subcommand (4 subcommands total: add-pattern / catalog-summary / integrity-check / inspect-pattern)
  - `D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShellISE_profile.ps1` — created with p140 PATH prepend; eliminates the `python` → wrong-interpreter friction that surfaced this session
- **Off-record ingests reconciled into tracking docs:** SPY launch 2025-06-20, QQQ launch 2026-04-14, NVDA launch 2025-10-24 — all ingested 2026-05-15 21:53 between Stage 4 seal and this session; `todo.md` Stage 5 checkboxes flipped today.
- **Regression verification:** AAPL id=1 anchor close 258.27 + OHLC + volume matched source XLSX to 4 decimals; all 5 forward horizons (+5d 269.48, +7d 275.91, +10d 273.68, +15d 264.35, +20d 274.23) matched XLSX Close to 4 decimals. Pipeline math empirically deterministic.
- **Forward-label stats across 5 POC patterns:** +5d 5/5 profitable (avg +6.72%), +7d 5/5 (+5.67%), +10d 5/5 (+4.44%), +15d 5/5 (+4.96%), +20d 4/5 (+4.58%). Tiny n=5 but spanning NVDA ~$135 → SPY ~$550, so the cross-symbol normalization layer is empirically pulling its weight.
- **New lessons in `tasks/lessons.md`:**
  - **M-016** — Verify python interpreter resolution at session start before suggesting Python commands. Trader workstation has 4 python.exe installs; without profile-driven PATH prepend, Python 3.14 wins by default. Active host is PowerShell ISE; Documents is OneDrive-redirected to D:\. Mandatory diagnostic: `$PROFILE`, `(Get-Command python).Source`, `($env:Path -split ';')[0..2]`.
  - **M-017** — INIT must reconcile live catalog state against `tasks/*.md` tracking. Catalog is ground truth; tracking docs describe it. ~6 turns wasted this session because INIT trusted stale tracking docs over live catalog state. Mandatory INIT addition: query `pattern_instances` + `source_files` row counts and symbol distribution after loading `tasks/*.md`; flag any divergence in the session summary.
  - Both flagged for structural promotion to SIP + SKILL at Stage 6 start.
- **End-of-file marker fixed.** v2.3 file still carried stale `**End of P_300 System Architecture v2.2**`. Cleaned to v2.4 in this seal.
- **`docs/archive/P_300_System_Architecture_v2.3.md`** — prior major version preserved.
- **SIP and SKILL alignment to v2.4 deferred** to Stage 6 start session, where they get touched anyway for M-016/M-017 structural promotion. Until then, SIP "Pairs With" and SKILL "Aligned With" lines continue to reference v2.3 — acceptable lag for one session.

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
- **§2.5, §7, v2.0 changelog: "8-table" → "7-table".** The "8-table" wording was a stale claim propagated from earlier planning; §9.2 has always defined 7 tables (`symbols`, `source_files`, `feature_sets`, `pattern_instances`, `pattern_bars`, `pattern_features`, `forward_labels`). No schema change — wording correction only. Caught at Stage 3c verification; codified as an instance of M-009. (FR-3 wording cleanup landed in v2.5.)
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

The full historical log is preserved. EC-060 and beyond capture the v2.0 forensics from the Claude rebuild session; EC-068 and beyond capture Stage 6 build findings.

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
| EC-019 | Polluted Stream Reporting | Fixed | Strict `data_origin_type='EVAL_SET'` filtering (Decision E supersedes — no EVAL_SET inserts at all from Stage 6) |
| EC-020 | Signal Interpretation Failure | Fixed | "No Match" = "Stay in Cash" explicitly |
| EC-021 | AI hallucinated column names | Fixed | Always request schema/DDL before SQL |
| EC-022 | Pipeline Drift — false 0.0 distances for non-SPY | Resolved in v2.0 | Normalization pre-computed on `pattern_bars` columns; cross-symbol matching valid by construction. RE-VERIFIED 2026-05-18 in Stage 6 self-match sanity check (SPY ranks #1 at composite 12.80, QQQ #2 at 16.70, OII/NVDA/AAPL #3-5). |
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
| EC-054 | Extension Blindness | Fixed historically; superseded by M-010 instance #3 | Original Gemini-era fix: target `.csv` only; ignore `.xlsx` in eval. Stage 6 inverted the rule — live evaluation now standardized on `.xlsx` per M-010 instance #3. Pattern A `.xlsx` (Stage 4) and Pipeline B `.xlsx` (Stage 6) now match. |
| EC-055 | Workflow Disparity | Fixed | Add Pattern = sequential write; Daily Eval = integrated read |
| EC-056 | Hardcoded Indices | Fixed | Use `P_010_RiskConfig.json` as global posture source |
| EC-057 | Database Orphans | Fixed | Post-ingest health check (Ghost vs Valid patterns) |
| EC-058 | Path Discovery | Fixed | `db_utils.get_latest_catalog()` mandatory |
| EC-059 | OneDrive Bridge | Fixed | Converter v6.8 dual-distributor pattern |
| **EC-060** | **Converter `df.tail(5)` truncation** | **Resolved in v2.0** | Removed in rebuild. Schema does not constrain bar count; window length is data not structure |
| **EC-061** | **v6.0 ingest TEXT in INTEGER `symbol_id` FK** | **Resolved in v2.0** | Schema FK constraint + symbols-table lookup before insert; rebuilt ingest enforces typed symbol_id |
| **EC-062** | **v6.0 ingest silently dropped `--type` argument** | **Resolved in v2.0** | Rebuilt ingest in `cli.py` uses `argparse` with required type discriminator |
| **EC-063** | **v6.0 ingest manifest targeted wrong table** | **Resolved in v2.0** | Manifest re-targeted to `pattern_bars` columns explicitly |
| **EC-064** | **v4.7 evaluator used mock data dictionary** | **Resolved in v2.0** | Pipeline B rebuilt against actual catalog queries (Stage 6); no mock data in production engines |
| **EC-065** | **Symbols table duplicate entries — observed: 'IVR' + 'History Grid (IVR)'** | **Resolved in v2.0** | Symbol parsing normalized to ticker-only; `UNIQUE` constraint enforced |
| **EC-066** | **OneDrive path hardcoded as `D:\OneDrive\...`** | **Resolved in v2.0** | `Path(os.environ["OneDrive"])` enforced per `python-project-architecture` skill |
| **EC-067** | **AI Workflow Conflation (Pipelines A & B merged in v1.16)** | **Resolved in v2.0** | Pipelines are structurally separate; merging is an architectural anti-pattern |
| **EC-068** | **Stage 6 `signal.py` stdlib name collision** | **Resolved 2026-05-18** | Module renamed to `signal_classifier.py`. Script-mode `sys.path[0]` prepend caused `import signal` (from Pydantic's deep import chain for SIGINT handling) to find the local file first and raise cryptic circular-import errors that pointed at Pydantic — masking the real cause. (M-018; promoted to Section 2.7 anti-pattern; SKILL v2.5 anti-pattern.) |
| **EC-069** | **Stage 6 `report_writer.py` v1.0 Unicode stdout crash** | **Resolved 2026-05-18** | v1.0 used `═` / `─` / `—` for 76-col table separators; first `print()` call from `daily_evaluate_pipeline.py` raised `UnicodeEncodeError: 'charmap' codec can't encode character '\u2550' in position 0`. v1.1 hotfix: ASCII-only (`=`, `-`, `--`) for any string flowing through stdout. PowerShell default stdout encoding is cp1252, not utf-8. (M-019; promoted to Section 2.7 anti-pattern; SKILL v2.5 anti-pattern.) |
| **EC-070** | **Stage 6 `report_writer.py` v1.0 displayed `return_pct` × 1 instead of × 100** | **Resolved 2026-05-18** | Storage convention is decimal fraction (0.0672 represents 6.72%); v1.0 rendered "+0.0672%" instead of "+6.72%". v1.1 hotfix: explicit × 100 at display boundary. Schema field rename to `return_fraction` / `return_decimal` deferred to Backlog alongside NormalizedBar / PatternBarRecord shared-base refactor. (M-020; promoted to Section 2.7 anti-pattern.) |

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

## Stage 5 — Re-Ingest Historical Patterns (SEALED 2026-05-16)

Delivered:

- **5 POC symbols ingested clean** — AAPL, OII, SPY, QQQ, NVDA. 100 `pattern_bars` rows, 25 `forward_labels` rows, 0 hollow records. Catalog OVERALL: HEALTHY confirmed via `catalog-summary`.
- **Regression spot-check** on AAPL id=1 — anchor close 258.27 + OHLC + volume matched source XLSX to 4 decimals; all 5 forward horizons (+5d 269.48, +7d 275.91, +10d 273.68, +15d 264.35, +20d 274.23) matched XLSX Close to 4 decimals. Pipeline math empirically deterministic.
- **`python/utilities/inspect_pattern.py`** v1.0 — read-only single-pattern inspector with hand-compare `implied_future_close` column; the regression workflow lives here.
- **`python/cli.py`** v1.0 → v1.1 — added `inspect-pattern --id N [--catalog PATH]` subcommand.
- **`D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShellISE_profile.ps1`** — created with p140 PATH prepend; eliminates the `python`→wrong-interpreter friction discovered this session.
- **Cross-symbol normalization layer empirically validated** across price range NVDA ~$135 → SPY ~$550. Forward-label win rate across n=5: 100% at +5d/+7d/+10d/+15d, 80% at +20d.

Broader 14-symbol historical set (MSFT, CTRA, ATGE, VOD, CME, TR, LYV, FSLY, NFLX, APPN, BRK_A, ITA, MSA, PG) moved to backlog. Stage 6 small-catalog signal caveat (BUY unreachable at 4 of 5 horizons until broader set is ingested) makes this backlog item critical for unblocking real BUY signals — see ID-007 in §10.3.

## Stage 6 — Rebuild Pipeline B (Daily Evaluate) (SEALED 2026-05-18)

Pipeline B operational end-to-end against real live SPY XLSX. 10 of 10 files delivered. All three success criteria green: determinism, self-match sanity, Stage 5 regression replay.

**Six architectural decisions (A-F) locked 2026-05-16 (authoritative for downstream parameter sweeps):**

- A — Legacy file decomposition (intelliscan / aggregator / EvaluateTrade retired)
- B — Distance function: DTW per-feature, equal-weight composite across the 10 `SIMILARITY_FEATURES`
- C — Top-K matches: 20 per candidate, configurable in `config.py`
- D — Output horizons: all 5 (5/7/10/15/20) emitted, operator picks hold period when sizing
- E — EVAL_SET handling: transient in-memory only — no `pattern_instances` inserts
- F — BUY/WATCH/PASS thresholds: AND-gate per horizon, strongest-class-wins arbiter with shortest-horizon tiebreak

**Files delivered (10 total):**

- `python/config.py` v1.1 → v1.2 — Pipeline B constants (`TOP_K_MATCHES=20`, `SIMILARITY_FEATURES`, BUY/WATCH AND-gate thresholds, `REPORTS_DIR`, `HISTORY_GRID_GLOB_PATTERN`)
- `python/schemas_pipeline_b.py` v1.0 NEW — 7 Pydantic models (`NormalizedBar`, `LiveCandidate`, `ForwardLabelLite`, `MatchResult`, `AggregatedSignalPerHorizon`, `SignalClass` enum, `SignalReport`); sibling to `schemas.py` for §8.4.2 file-size limit
- `python/infrastructure/catalog_reader.py` v1.0 NEW — read-only query API; caller owns sqlite3.Connection via `db_connect.connection_context` (M-012)
- `python/domain/similarity.py` v1.0 NEW — pure-Python DTW with O(min(m,n)) rolling-row reduction; `per_feature_distances`, `composite_distance` (Decision B), `rank_by_distance`
- `python/domain/aggregator.py` v1.0 NEW — per-horizon stats, two-proportion `z_score` with +inf/-inf degenerate-baseline guards, `catalog_baseline_win_rates`, `aggregate_top_k` (all horizons emitted; n=0 zeroed for consistent shape)
- `python/domain/signal_classifier.py` v1.0 NEW — Decision F AND-gate per horizon + cross-horizon strongest-class-wins arbiter (shortest-horizon tiebreak; all-PASS picks highest z); renamed from `signal.py` mid-stream per M-018
- `python/infrastructure/report_writer.py` v1.0 → v1.1 — terminal + file output, 76-col ASCII tables; ASCII-only stdout per M-019; v1.1 hotfix: `return_pct` × 100 at display boundary per M-020
- `python/infrastructure/vp_xlsx_reader.py` v1.0 → v1.1 — purely additive: `_LIVE_FILENAME_PATTERN` + `_parse_live_filename` helper + `parse_live_file(xlsx_path, manifest_path)`. Stage 4 `parse_pattern_file` untouched
- `python/application/daily_evaluate_pipeline.py` v1.0 NEW — Pipeline B orchestrator; `run_daily_evaluate` library entry, `main` standalone CLI entry; one sqlite3.Connection scoped to one evaluation pass
- `python/cli.py` v1.1 → v1.2 — added `daily-evaluate` subcommand (thin shim around `run_daily_evaluate`); CLI now exposes 5 subcommands

**Validation (operator-run, 2026-05-18 ET):**

- **Determinism:** two `daily-evaluate` runs on the same SPY XLSX → identical output (composite=12.7997 both runs; all stats identical to 3 decimals; same signal class + chosen horizon)
- **Self-match sanity:** SPY catalog pattern ranks #1 against live SPY candidate (composite 12.80); QQQ #2 at 16.70, OII #3, NVDA #4, AAPL #5. Cross-symbol distance math correctly clusters by ticker
- **Stage 5 regression replay:** `python cli.py inspect-pattern --id 1` produces AAPL 4-decimal match on all 5 forward closes (269.4800 / 275.9100 / 273.6800 / 264.3500 / 274.2300). Pipeline A untouched by Stage 6 build
- **End-to-end against real live SPY XLSX:** `History Grid (SPY).xlsx` (124 bars) → SPY candidate anchor 2026-05-15; per-horizon means match Stage 5 documented averages exactly (+6.72% / +5.67% / +4.44% / +4.96% / +4.58%); signal classification PASS at horizon 5 (small-catalog caveat)

**Small-catalog signal caveat:** Baseline win-rate = 1.0 at horizons 5/7/10/15 → degenerate two-proportion z-score denominator → BUY (requires z > 1.0) structurally unreachable at 4 of 5 horizons until broader 14-symbol set is ingested (Backlog). Only horizon 20 (baseline 0.8) admits a finite z. Classifier math is correct; signal gating is gated by catalog diversity. Tracked as ID-007 in §10.3.

**File plan grew 9 → 10 mid-stream.** Original assumption that the existing `vp_xlsx_reader.py` regex would match `History Grid (*).xlsx` was wrong (regex was `^Pattern_*`). File #8 split into File #8a (`vp_xlsx_reader` v1.1 extended) + File #8b (orchestrator). Option A taken (extend existing file); planned `live_csv_reader.py` deleted, saving ~175 lines and one reader file.

**New lessons** (full text in `tasks/lessons.md`): M-018 (stdlib name collisions), M-019 (PowerShell cp1252 stdout / ASCII-only), M-020 (`return_pct` decimal-fraction storage convention), M-021 (Pydantic v2 `model_copy(update=...)` skips re-validation), M-010 instance #3 (CSV → XLSX live format standardization), M-011 extension (Python warnings render as red `NativeCommandError` in PowerShell). M-016 + M-017 STRUCTURALLY EMBEDDED in SIP v2.4 and SKILL v2.4 at session start; aligned to v2.5 at session close.

**New EC entries:** EC-068, EC-069, EC-070 (see Section 6).
**New anti-patterns in Section 2.7:** stdlib-name collisions; Unicode in stdout from PowerShell; `return_pct` mistreated as percentage.

## Stage 7 — Broader Catalog Ingest (SEALED 2026-05-19)

**Goal achieved:** Lift baseline win-rate off 1.0 at horizons 5/7/10/15 so BUY signals become structurally reachable. ID-007 RESOLVED — baselines now in 0.50-0.60 range at all 5 horizons.

**Methodology (locked 2026-05-18, executed 2026-05-18 + 2026-05-19):**

- 20-symbol curated list spanning diverse sectors + caps + 12-month window (May 2025 – Apr 2026)
- Mix intentional: roughly 11–12 likely winners, 3–5 likely losers, rest mixed — goal is baseline below 1.0 at every horizon, NOT all winners
- **Target=anchor workflow** (locked mid-session 2026-05-18 after early offset confusion): operator picks target date as launch/anchor in VP; captures 20 trading bars BACK as setup; forward labels run 5/7/10/15/20 days FORWARD; filename uses target as first date (`Pattern_<TARGET>_<CAPTURE>_<SYMBOL>.xlsx`). M-022 captures the lesson; pre-fix ingests (TTD/AMD/LMT/MU/SHOP/NVO at slots 3-8) landed ~4 weeks past target due to off-by-window-length misread of VP's launch marker; valid data, just at later anchors than intended — not re-ingested.
- **VP license/access pattern** (M-023): operator's VP subscription excludes some sector browses (healthcare, utilities confirmed). Individual tickers may still be accessible. Substitution chain when "not found": Claude proposes thesis-preserving substitute → operator confirms reachable → cycle until accepted. Slot #20 cycled LLY (blocked) → JNJ (blocked) → NEE (blocked) → GLP accepted (small-cap MLP, added first-small-cap + first-MLP diversity).

**Final catalog state at Stage 7 SEAL:**

- 25 patterns / 25 symbols / 25 source_files / 500 pattern_bars / 125 forward_labels / 0 hollow / OVERALL: HEALTHY
- Active catalog: `models/051826catalog.db` (Stage 6 baseline `models/051426catalog.db` retained dormant)

**20-symbol roster** (target date / pattern_instance_id):

AVGO 2025-06-13/id=6 · CAT 2025-06-25/id=7 · TTD 2025-07-10/id=8 · AMD 2025-07-21/id=9 · LMT 2025-08-05/id=10 · NVO 2025-08-12/id=13 (sub for PFE/MRK/UNH) · MU 2025-08-15/id=11 · SHOP 2025-08-25/id=12 · NKE 2025-09-15/id=14 · GEV 2025-09-25/id=15 · DIS 2025-10-15/id=16 · PLTR 2025-10-23/id=17 · META 2025-11-05/id=18 · DE 2025-11-20/id=19 · GOOGL 2025-12-12/id=20 · XOM 2026-01-15/id=21 · GS 2026-01-22/id=22 · CVX 2026-02-10/id=23 · WMT 2026-02-25/id=24 · GLP 2026-03-10/id=25 (sub for LLY).

**Stage 7 success criteria — all green:**

- [x] All 20 symbols ingested clean (0 hollow, FK constraints respected, all 5 forward labels per pattern)
- [x] Catalog totals match target: 25/25/25/500/125/0
- [x] Re-run `daily-evaluate` on SPY → baseline win-rates drop below 1.0 at most horizons. RESULT EXCEEDS SPEC: all 5 horizons below 1.0 (implied baselines h=5/7/10/15/20 → 0.60/0.60/0.60/0.56/0.60). Spec required ≤2 of 5 stuck at 1.0.
- [x] Regression spot-check via `inspect-pattern --id N` on fresh Stage 7 ingest — NKE id=14 hand-compare matches XLSX to 4 decimals on all 5 forward closes (+5d 71.2800, +7d 71.2200, +10d 69.5500, +15d 71.1700, +20d 67.3800). Pipeline A regression-clean.

**Stage 7 SEAL signal report** (SPY anchor 2026-05-18): PASS at horizon 5. Sample win-rate 0.600 matches baseline 0.600 → z=0.000 fails WATCH strict-gt (correct strict-greater-than enforcement). Other horizons negative z (sample below baseline). BUY (z > 1.0) is now structurally reachable; when a future candidate genuinely outperforms its baseline, the math will fire.

**New lessons** (full text in `tasks/lessons.md`): M-022 (target=anchor workflow lock), M-023 (VP license/access constraints + thesis-flexible substitution), M-024 (filename date format strict YYYYMMDD; no capture-date sanity check), M-025 (CWD discipline + folder convention drift), M-026 (date-validity pre-checks for AI-generated pick lists).

## Stage 8 — Local LLM Integration (SEALED 2026-05-19)

Post-Decision Narrator wired into Pipeline B. **NFR-1 boundary preserved:** signal classification is locked BEFORE any LLM call; narration failure attaches `narration=None` without affecting BUY/WATCH/PASS.

**Files delivered:**

- `python/infrastructure/llm_client.py` v1.0 NEW (~8 KB) — `call_lm_studio(system_prompt, user_prompt) -> str | None`. Connection-refused, timeout, HTTP error, R1 think-truncation, malformed JSON — all failure modes return None cleanly. LM Studio reached via local HTTP endpoint configured in `config.py`.
- `python/domain/narrator_prompt.py` v1.0 NEW — `NARRATOR_SYSTEM_PROMPT` constant + `build_narrator_user_prompt(report: SignalReport) -> str` builder. Pure logic — no I/O.
- `python/config.py` v1.2 → v1.3 — `NARRATOR_ENABLED` kill-switch + LM Studio endpoint/timeout constants.
- `python/application/daily_evaluate_pipeline.py` v1.0 → v1.1 — Stage 7 of the pipeline (intra-file orchestration step) calls narrator AFTER `classify_signal()` emits; attaches result via `report.model_copy(update={"narration": text})` (M-021 — `model_copy` skips re-validation, fine here because narration has no validator).
- `python/cli.py` v1.2 → v1.3 — added `--no-narrator` flag to `daily-evaluate` subcommand for fast testing / LM-Studio-down sessions.

**Operator launch protocol:** LM Studio open + DeepSeek R1 14B manually loaded BEFORE running with narration enabled. Use `--no-narrator` (or `NARRATOR_ENABLED=False` in `config.py`) to skip the LLM call entirely.

**Determinism preserved (NFR-1):** SignalReport is built and `signal_class` + `chosen_horizon` finalized before any LLM interaction. Same SPY data produces same signal regardless of LLM availability. Narration may differ between runs (LLM non-determinism is acceptable since narration is a post-decision label, not a decision input).

## Stage 9 — Parameter Sweep + Outcome Attribution (SEALED 2026-05-19)

Three analytical utilities + outcome attribution findings on the 25-pattern catalog. Read-only against the catalog; no schema changes.

**Files delivered:**

- `python/utilities/threshold_sweep.py` v1.0 NEW (~11 KB) — grid-search BUY/WATCH thresholds across catalog replay; emits CSV of (threshold combination × per-horizon firing rate × outcome stats).
- `python/utilities/feature_ablation.py` v1.0 NEW (~10 KB) — leave-one-feature-out replay against the 10 `SIMILARITY_FEATURES`; emits CSV of (excluded_feature × signal precision/recall delta).
- `python/utilities/loo_replay.py` v1.0 NEW (~12 KB) — leave-one-pattern-out replay across the 25 catalog patterns: for each pattern, treat it as the live candidate, find top-K from the remaining 24, score the would-be signal, compare to actual forward outcome.

**Artifacts produced** (in `outputs/`): `feature_ablation_20260519_185052.csv` (3.2 KB), `feature_ablation_20260519_185356.csv` (4.5 KB), `threshold_sweep_buy_20260519_183459.csv` (21 KB).

**Findings (preliminary, interpretation pending per M-029):**

- **Signal-carrying features:** `volume_zscore` (-0.208 d_precision), `close_pct_from_anchor` (-0.175), `ltdiff_pct` (-0.148) hurt BUY precision most when removed.
- **Likely noise:** `body_pct` (+0.125 d_precision — removing IMPROVES precision); single-bar candle ratio carries no shape information across windows.
- **Suspicious correlation cluster:** `stdiff_pct`, `pred_high_pct`, `pred_low_pct`, `pred_range_pct` all show identical d_precision (+1/+0.014). Likely correlated — all four share `bar.close` as the denominator per §9.3 normalization formulas. A future weighted scheme treating them as 4 independent features would be wrong; they are closer to 1 effective feature.
- **Default thresholds too tight at N=25.** Initial `threshold_sweep_buy` grid centered on production defaults (`win_rate >= 0.70`, `z >= 1.0`) produced 0 BUYs across the entire grid at the 25-pattern catalog. Sweep was correctly executed; grid was wrong (M-028). Re-run with grid bracketing the firing region surfaced usable results.

**Small-N caveat:** 8 baseline BUYs at the relaxed grid is sparse — ±1-3 ranking shifts could come from a single pattern. Findings are directional, not definitive. Re-run after catalog >= 50 (Backlog).

**New lessons** (full text in `tasks/lessons.md`):

- **M-027** — Cost-estimate discipline: measure or admit unknown, never extrapolate from feel.
- **M-028** — Parameter sweeps on sparse catalogs must bracket the firing region, not production defaults.
- **M-029** — Don't interpret domain data without confirming domain semantics. Companion to M-027 — interpretation discipline vs measurement discipline. Stage 9 ablation labels above are interpretation-pending until VP indicator semantics are fully confirmed (Grok-authored Bullish Trend Pattern doc grounds stdiff/mtdiff/ltdiff as VP's 1/2/3-day predictive differences; pred_high/pred_low/pred_range remain ungrounded pending `normalization.py` read or VP reference).

## Stage 9-followup — Volatility Divergence Flag + Process Runbooks (2026-05-20)

**Not a stage; post-SEAL feature delivery on top of the Stage 9-sealed system.** Stages 1-9 remain SEALED. The work attaches post-classification metadata to SignalReport without changing the Stage 6 Decision B distance computation or the Decision F BUY/WATCH/PASS gate. NFR-1 preserved end-to-end.

**Context (audit-driven):** Stage 9 ablation surfaced `range_pct` as signal-carrying. A fresh cap-sensitivity audit (`utilities/cap_sensitivity_audit.py` v1.0 NEW, ~125 lines) ranked all 17 raw + 10 normalized `pattern_bars` fields by per-symbol stdev of medians. Findings:

- `range_pct` is the cleanest cap/volatility-class axis among the 10 normalized similarity features (OII ~0.046 vs SPY ~0.009, ~5x ratio; monotonic with cap-proxy ordering).
- `volume_zscore` has the largest raw dispersion (0.131) but encodes per-pattern volume-skew, not cap class.
- `close_pct_from_anchor` (0.061) encodes trend bias.
- `triple_cross_short/medium/long` carry dispersion identical to OHLC (~242) — they are PRICE LEVELS, not crossover signals; documentation referring to 16 raw VP fields was off-by-one (actual count is 17). Backlog cleanup.

**Design choice rationale:** Three options considered. Pre-filter (exclude cap-mismatched candidates BEFORE similarity) dies at N=25 — GLP would land alone in small-cap. Extend-space (add `range_pct` as an 11th `SIMILARITY_FEATURE`) would change Decision B mid-flight; rejected. Post-filter (attach as post-classification metadata) preserves Decision B and surfaces the cap/volatility concern at the decision-time display layer; selected.

**Severity thresholds (locked at v1.0):**

| Severity | Symmetric Ratio | Meaning |
| :---- | :---- | :---- |
| NONE | < 1.5x | Candidate's volatility band aligned with top-K analogs; signal stands at face value |
| MILD | 1.5x to < 2.0x | Modest cap/volatility-class mismatch; apply confidence haircut at sizing time |
| STRONG | ≥ 2.0x | Significant cap/volatility-class mismatch; treat candidate as WATCH unless other factors override |

Symmetric ratio = `max(candidate_median, topk_median) / min(...)`. Aggregation per match: per-match median first, then median-of-medians (weights matches equally regardless of `window_length` 5-20). Degenerate input (either median 0.0) returns severity NONE with ratio 1.0.

**Files delivered (7 total):**

- `python/utilities/cap_sensitivity_audit.py` v1.0 NEW (~125 lines) — read-only diagnostic over the 17 raw + 10 normalized fields on `pattern_bars`; ranked per-symbol stdev_of_medians for `range_pct` and other candidate axes; one-shot utility that may grow into a Backlog field-semantics utility once VP indicator docs are complete.
- `python/schemas_pipeline_b.py` v1.1 → v1.2 (~408 lines, +79). Added `Severity` enum + `VolatilityDivergence` Pydantic + optional `volatility_divergence` field on `SignalReport` + `_volatility_divergence_consistency` model_validator (enforces `n_topk_matches == len(top_matches)` when divergence is set). DEBT NOTE expanded to name the proper file split (`schemas_pipeline_b_bar.py` + `schemas_pipeline_b_report.py`) — pair with NormalizedBar shared-base refactor (Backlog). File-size discipline: M-031 signals "split, not slim."
- `python/domain/volatility_divergence.py` v1.0 NEW (220 lines). Pure compute, no I/O. Domain stays decoupled from bar transport: orchestrator extracts range_pct float sequences, helper computes severity. Built-in smoke harness with 4 cases (STRONG / MILD / NONE / degenerate) — all 4 verified at operator-run check.
- `python/application/daily_evaluate_pipeline.py` v1.1 → v1.2 (~417 lines, +52). New Stage 5b inserted between `classify_signal()` and `SignalReport` construction. Uses match bars already in memory from Stage 2 bulk_load (no DB re-query). SignalReport constructed via full `Model(**fields)` NOT `model_copy(update=...)` per M-021 so consistency validator fires. Empty top_matches guarded. NFR-1 preserved.
- `python/infrastructure/report_writer.py` v1.2 → v1.3 (~373 lines, +55). New `_build_volatility_section` wired into `format_signal_report` between matches table and narrative. NONE = no section (clean omission); MILD = 2-line compact block; STRONG = labeled block with candidate median, top-K median, ratio, n_topk_matches, and an apples-to-oranges note. ASCII-only on stdout per M-019.
- `docs/processes/evaluate_trade.md` v1.0 NEW (~200 lines). Operator runbook for Pipeline B. Per-candidate workflow (NOT fixed-time routine — operator has maximum flexibility on when to run). Sections: prereqs; 18:30 ET data freshness boundary (VP exports today's bar only after 18:30 daily build); mechanics (export / run / read); decision tree (signal_class × volatility_severity matrix); sizing reference (defers to P_000/P_010); failure modes; post-trade capture template; calibration markers (v1.0 heuristics explicitly named subject to refinement).
- `docs/processes/add_pattern.md` v1.0 NEW (~250 lines). Operator runbook for Pipeline A. Per-pattern workflow. Sections: prereqs; D+20 rule (target date + 20 trading days must elapse before capture); capture mechanics (target=anchor per M-022; VP license constraints per M-023; filename strict YYYYMMDD per M-024; CWD discipline per M-025; date validity pre-checks per M-026); four-step ingest workflow (integrity-check → add-pattern → catalog-summary → inspect-pattern); failure decision points; calibration markers.

**New `docs/processes/` directory convention.** Operator-facing procedural documentation (per-workflow runbooks for evaluation and ingest) lives in `docs/processes/`, distinct from `docs/architecture/` (this file + successors), `docs/migrations/` (stage closeout reports), and `docs/prompts/` (SIP). Appendix E folder map updated.

**Production runs (end-to-end verification, all 2026-05-19 anchors):**

- **SPY** — PASS at h=5. Volatility divergence: **STRONG** (ratio 2.73x, candidate 0.0078 vs top-K 0.0213). Signal byte-identical to Stage 7 SEAL output (NFR-1 verified). STRONG fires correctly: SPY matched against a top-K dominated by high-vol names (TTD, AMD, PLTR, GLP).
- **BBY** — PASS at h=5. Volatility divergence: **NONE** (ratio 1.24x, candidate 0.0275 vs top-K 0.0221). Flag correctly silent for a mid-vol mid-cap against a mixed catalog. First successful narrator pass observed: DeepSeek 566 chars, think-strip working, narrative grounded in real top-K tickers (not hallucinating).
- **CNX** — PASS at h=7. Narrative shared cleanly; report not in chat context but matches the format precedent set by SPY and BBY.

**New lessons** (full text in `tasks/lessons.md`): M-030 (PowerShell + python -c hang); M-031 (file-size accretion → split, not slim); M-019 extension (PowerShell `>` redirection UTF-16 LE).

## Backlog — Future Candidates (Not Scheduled)

Items here are real work — out of any current stage, not on the critical path, surfaced when relevant.

- **Re-run sweep + ablation at N >= 50** — Stage 9 small-N caveat retires automatically at this catalog size. At N >= 50 the threshold sweep grid can center on production defaults rather than the firing region (M-028 retire trigger).
- **NormalizedBar / PatternBarRecord shared-base refactor** — DEBT NOTE from `schemas_pipeline_b.py` v1.0 split at Stage 6. Two Pydantic models share most columns; a shared-base class would dedupe + standardize.
- **`return_pct` schema field rename** to `return_fraction` / `return_decimal` (M-020 cleanup; bundle with shared-base refactor above).
- **Date-validity pre-check utility** (from M-026) — Python helper validating dates against weekends + US market holidays before publishing date-driven pick lists. Trivial to write; only needed when next curated-list ingest is scoped.
- **Legacy 14-symbol Gemini-era CSVs** — MSFT, CTRA, ATGE, VOD, CME, TR, LYV, FSLY, NFLX, APPN, BRK_A, ITA, MSA, PG. Stage 7's 20-symbol fresh-curate replaced this work; un-ingested CSVs survive only as forensic artifacts.
- **Recover 10 singleton symbols** (HL, IPI, ICE, POET, TXRH, DELL, DNN, ASTS, ESVIF; OII already in catalog) — requires fresh VP captures.
- **PEAK-anchor framing as a second ingest pass** — same source files, anchor = trend end, captures "tops that preceded reversals" signal. Schema already supports it via `data_origin_type`. Decide value after LAUNCH-only catalog has accumulated more patterns and ablation/sweep findings stabilize.
- **Real-time intraday evaluation mode** — currently end-of-day only.
- **Skill consolidation across 5+ locations** (per O-005 in `lessons.md`).

## Milestone 6 — Trade Management Module (Planned)

**Renumbered from Milestone 5 at Stage 6 SEAL (2026-05-18)** per operator directive: build gated on live P_300 trading first. Until the system produces signals worth sizing in real time, position-sizing logic is downstream work.

Consumes Aggregator output from Pipeline B. Required inputs:

- Confidence / Win-Rate (drives position size — proposed mapping: 80% win rate → 2% risk; 60% win rate → 0.5% risk; final values set in Milestone 6)
- Expected Horizon (5/7/10/15/20-day return reliability)
- Drawdown Threshold (worst-historical-analog-based hard stop)

Risk-management style (fixed percentage, volatility-based trailing, time-based exits) to be selected before build.

Integrates with `P_010_RiskConfig.json` (global posture) and `P_000_Account_Parameters_Current.md` (account balance).

---

# 8. AI Workflows & Processes

## 8.1 Session Bootstrap (Automated)

Replaces v1.x manual "read the doc first" rule.

1. **SKILL auto-loads** at session start (`p300-project-context\SKILL.md`)
2. **SIP runs INIT sequence** — account params from P_000, market posture from P_010, lessons from `tasks/lessons.md`, active task from `tasks/todo.md`, **live catalog state via Step 5b** (per M-017)
3. **Operator confirms session focus** before AI proposes work
4. **AI references architecture doc on demand** for full spec details

## 8.2 Pipeline A — Add Pattern (Write)

1. Operator drops `Pattern_<dates>_<symbol>.xlsx` files into `data/historical_patterns/`
2. Catalog Check-Out (verify state before write)
3. `application/add_pattern_pipeline.py` orchestrates:
   - Lock verify on master DB
   - Copy master → `temp_working.db`
   - Parse each XLSX (`infrastructure/vp_xlsx_reader.py`)
   - Validate schema via `schemas.py` Pydantic models
   - Lookup or create `symbol_id` (`infrastructure/catalog_writer.py`)
   - Insert `source_files` row with filename + row_count
   - Insert `pattern_instances` row with `feature_set_id`, `source_file_id`, `window_length`, `data_origin_type='PATTERN_IDENT'`
   - Compute normalized values (`domain/normalization.py`)
   - Insert all `pattern_bars` rows with raw + normalized columns
   - Compute derived features (Stage 8 candidate — currently no derived features inserted into `pattern_features`)
   - Compute forward labels (`domain/labeler.py`)
   - Insert `forward_labels` rows at all 5 horizons where data available
4. Verify temp DB integrity (`infrastructure/verify_ingestion.py`)
5. Atomic move temp → master
6. Archive processed XLSX → `data/archive/`
7. Catalog Check-In (verify delta + spot-check)

## 8.3 Pipeline B — Daily Evaluate (Read)

1. Operator drops `History Grid (<symbol>).xlsx` files into `data/live/` (per M-010 instance #3 — CSV → XLSX live format standardization at Stage 6 start)
2. Catalog Check-Out (read-only verification)
3. `application/daily_evaluate_pipeline.py` orchestrates:
   - Read P_010 risk posture
   - For each live XLSX: parse via `infrastructure/vp_xlsx_reader.parse_live_file()` → returns `(symbol, list[VPBarRaw])`
   - Build normalized in-memory `LiveCandidate` (no DB write; Decision E)
   - Query catalog via `infrastructure/catalog_reader.py` for all `PATTERN_IDENT` pattern_ids + their normalized windows + forward labels
   - Run cross-symbol similarity search (`domain/similarity.py`): per-feature DTW across the 10 `SIMILARITY_FEATURES`, composite equal-weight sum (Decision B), rank ascending
   - Select top-K matches (default K=20, configurable in `config.py` — Decision C)
   - Aggregate matches by horizon (`domain/aggregator.py`): n, mean return, std, win_rate, two-proportion z-score against catalog baseline win-rates
   - Classify per horizon and cross-horizon (`domain/signal_classifier.py`): Decision F AND-gate (BUY n≥5 + win_rate≥0.70 + z>1.0; WATCH n≥3 + win_rate≥0.60 + z>0.0; else PASS); strongest-class-wins arbiter with shortest-horizon tiebreak
   - Format report (`infrastructure/report_writer.py`): 76-col ASCII tables with match list + per-horizon stats + final signal
4. Output combined report to terminal + optional file in `outputs/reports/`
5. Archive processed XLSX → `data/processed/`
6. Catalog Check-In (read-only — verify catalog state unchanged, no EVAL_SET leakage)

**Stage 8 SEAL 2026-05-19** added post-decision narration: after the deterministic signal is computed, the Local LLM generates a human-readable summary. The Local LLM does NOT participate in the BUY/WATCH/PASS decision logic (NFR-1). See §7 Stage 8 for the full file roster + wiring details.

### Pipeline B Layer Flow (canonical module call order)

```
   data/live/History Grid (SYMBOL).xlsx
              |
              v
   infrastructure/vp_xlsx_reader.parse_live_file()           [I/O]
              |
              v
   domain/normalization.normalize_bars()                     [logic]
              |
              v
   application/daily_evaluate_pipeline._build_live_candidate()  [orchestration]
              |
              v
   infrastructure/catalog_reader.get_all_pattern_ids(PATTERN_IDENT)  [I/O]
   infrastructure/catalog_reader.get_normalized_window(pid) x N     [I/O]
   infrastructure/catalog_reader.get_forward_labels_all(pid) x N    [I/O]
              |
              v
   domain/similarity.composite_distance() x N                [logic]
   domain/similarity.rank_by_distance() -> top-K             [logic]
              |
              v
   domain/aggregator.aggregate_top_k()                       [logic]
              |
              v
   domain/signal_classifier.classify_signal()                [logic]
              |
              v
   infrastructure/report_writer.write_report()               [I/O]
              |
              v
   terminal + outputs/reports/<date>_<symbol>.txt
```

Every step is testable in isolation: `domain/` files take data in and return data out without touching disk; `infrastructure/` files do the I/O without making business decisions; `application/` orchestrates. Layer separation (Section 2.3) is what makes the pipeline auditable. The 4-min `windows-mcp:PowerShell` subprocess timeout drove the operator-run live-validation pattern: drop test script via `windows-mcp:FileSystem`, operator runs in ISE, pastes output. Used cleanly across all 8 Stage 6 smoke tests.

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

Stage 6 honored the limit by splitting `schemas_pipeline_b.py` out from `schemas.py` rather than growing the latter past 300 lines. NormalizedBar / PatternBarRecord shared-base refactor is queued for Backlog.

**Split vs slim (M-031, Stage 9-followup clarification):** When a file legitimately exceeds the 300-line budget through feature accretion — i.e., the existing docstrings, type hints, comments, and structure all carry weight — the architectural answer is to SPLIT at a natural boundary. Compressing docstrings, removing comments, or hiding complexity to squeeze under the limit produces a file that LOOKS smaller but carries the same load; the next feature addition hits the same wall harder. Three current breaches as of Stage 9-followup: `schemas_pipeline_b.py` v1.2 at 408 lines (split candidate named in DEBT NOTE: `schemas_pipeline_b_bar.py` + `schemas_pipeline_b_report.py`); `application/daily_evaluate_pipeline.py` v1.2 at 417 lines (no clean split candidate yet — Stage 1-7 orchestration is one flow; watching); `infrastructure/report_writer.py` v1.3 at 373 lines (no clean split candidate yet — the five `_build_*` helpers are tightly coupled to the same SignalReport model; watching). Promote to SKILL anti-pattern position if a fourth file breaches in the next session or two.

### 8.4.3 Dynamic Pathing Protocol

- No hardcoded DB paths anywhere except `config.py`
- All DB access through `db_utils.get_latest_catalog()`

### 8.4.4 Schema Discipline

Every persistent file read or write requires a Pydantic model in `schemas.py` (or `schemas_pipeline_b.py` for Pipeline B in-memory types). No exceptions for "simple" CSVs — Gemini-era drift began exactly with "this CSV is too simple to need a schema" calls.

### 8.4.5 No print() in Production Code

All output goes through the `logging` module. `print()` is permitted only in `cli.py` for direct operator-facing output. The `report_writer.py` infrastructure module is the documented exception — its job is to produce operator-readable output, so `print()` calls are part of its contract. All strings flowing through `print()` must be ASCII-only when the script may be invoked from PowerShell (M-019; §2.7 anti-pattern).

### 8.4.6 Direct File Modification Standard

When filesystem MCP is available and a change to an existing file spans more than one line OR touches 2+ places, the AI performs the modification directly via filesystem MCP (`filesystem:write_file` or `windows-mcp:FileSystem` write) rather than handing the operator text to paste. This applies to:

- Project Instructions, architecture docs, `tasks/lessons.md`, `tasks/todo.md`, SIP, SKILL — any project artifact
- Code files at any layer

Paste-style code blocks are reserved for cases where filesystem MCP is unavailable, or where the operator has explicitly asked for paste-ready output.

### 8.4.7 Module-Name Discipline (Stage 6)

Module files in `domain/` / `infrastructure/` / `application/` must not share a name with any Python stdlib module (M-018; §2.7 anti-pattern). Use descriptive suffixing when a name would collide: `signal.py` → `signal_classifier.py`, `csv.py` → `csv_loader.py`, `json.py` → `json_writer.py`. The script-mode `sys.path[0]` prepend causes any later `import <stdlib_name>` to find the local file first and raise cryptic circular-import errors during dependency initialization.

---

# 9. Data Design

## 9.1 Core Data Entities

- **Symbol** — Ticker identifier
- **Source File** — A specific CSV/XLSX import, tied to a symbol
- **Feature Set** — A named, versioned feature engineering definition. Current default: `baseline_v1`. Window-agnostic: window length lives in `pattern_instances.window_length`, not encoded in the feature_set name.
- **Pattern Instance** — One historical setup observation, anchored to a symbol + date + feature_set + source_file
- **Pattern Bar** — One bar of normalized + raw VP data at a specific offset from the anchor
- **Pattern Feature** — One derived (computed) feature value per pattern (window-level aggregates)
- **Forward Label** — Outcome at a specific horizon (5/7/10/15/20 days). `return_pct` stores decimal fractions, not percentages (M-020; §2.7 anti-pattern).

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
    return_pct REAL,            -- Decimal fraction (0.0672 = 6.72%); display × 100 (M-020)
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

Computed at ingest from raw `pattern_bars` data. The 10 normalized columns are also the `SIMILARITY_FEATURES` queried by `domain/similarity.py` in Pipeline B (Decision B — equal-weight DTW composite):

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
- `EVAL_SET` — Reserved value; Pipeline B (Stage 6) does NOT insert EVAL_SET rows per Decision E (live candidates are transient in-memory only). Reserved for potential Stage 8 narrator persistence hook ("today's signal history") if useful.

---

# 10. Testing & Validation

## 10.1 Testing Approach

- **Regression test:** Stage 5 spot-check — operator selects one known pattern, computes forward labels by hand from the source CSV, verifies pipeline output matches deterministically at all 5/7/10/15/20 horizons. (PASSED 2026-05-16 on AAPL id=1; helper at `python/utilities/inspect_pattern.py`. RE-VERIFIED 2026-05-18 as Stage 6 success criterion #3.)
- **Schema integrity:** Every Pipeline A run produces a Check-In report; row-count deltas must match expected values from the source file batch.
- **No-mock-data audit:** Pipeline B output must include at least one query to the catalog. Mock dictionaries in production decision engines are forbidden.
- **Layer audit:** Static-check that no `domain/` file imports `sqlite3`, `requests`, or anything in `infrastructure/`.
- **Cross-symbol matching validation:** Spot-check a candidate against historical patterns; verify distances are non-zero and well-distributed. (VERIFIED 2026-05-18 in Stage 6 self-match sanity check: SPY catalog pattern ranks #1 against live SPY at composite 12.80; QQQ #2 at 16.70; OII / NVDA / AAPL at #3-5. Cross-symbol distance math correctly clusters by ticker.)
- **Determinism:** Two `daily-evaluate` runs on the same live XLSX must produce identical output to all decimal places + identical signal class + identical chosen horizon. (VERIFIED 2026-05-18 on SPY: composite=12.7997 both runs, all stats identical to 3 decimals.)

## 10.2 Validation Checklist

- Architecture doc version matches what the SKILL references
- SKILL auto-loaded at session start
- SIP INIT sequence ran successfully (including Step 5b catalog reconciliation per M-017)
- Catalog Check-Out completed before any work
- Layer separation enforced in any new code
- For writes: Lock verified, temp DB used, temp verified, atomic move completed, row count + schema version logged
- For reads: catalog state confirmed; no writes to historical tables; no EVAL_SET leakage
- Forward-label horizons computed at all five points where data available
- Cross-symbol normalization columns populated on every `pattern_bars` row

## 10.3 Known Issues / Limitations

| ID | Description | Severity | Workaround | Status |
| :---- | :---- | :---- | :---- | :---- |
| ID-001 | Context loss across new threads | High | SKILL auto-loads at session start | Controlled |
| ID-002 | Pipeline A not yet rebuilt | n/a | Resolved in Stage 4 closeout | Resolved |
| ID-003 | Schema divergence between baseline and production | n/a | Resolved in v2.0 schema | Resolved |
| ID-004 | `verify_ingestion.py` not built | n/a | Built in Stage 4 (`infrastructure/verify_ingestion.py` v1.0) | Resolved |
| ID-005 | Gemini intra-thread context decay | High (historical) | Migrated off Gemini; Claude as primary architect | Mitigated |
| ID-006 | INIT trusts tracking docs over live catalog state | n/a | Resolved 2026-05-16 in SIP v2.4 Step 5b (catalog reconciliation) + SKILL v2.4 Must #13 / Must Not #13 (catalog wins on conflict) | Resolved |
| ID-007 | Small-catalog signal caveat — BUY structurally unreachable at horizons 5/7/10/15 | Low (operational, not defect) | RESOLVED 2026-05-19 at Stage 7 SEAL — broader 20-symbol Stage 7 ingest expanded catalog to 25 patterns / 25 symbols; baseline win-rates dropped to 0.50-0.60 range at all 5 horizons (was 1.0 at 4 of 5). BUY (z > 1.0) is now structurally reachable at every horizon. Classifier + matcher math was correct throughout; signal gating was gated by catalog diversity, now unblocked | Resolved |

---

# 11. Daily Operations & Session Management

## 11.1 Session Start Protocol

Automated by the SKILL + SIP. The operator does not need to manually instruct the AI to read the architecture. The SKILL contains the protection rules; the SIP runs INIT (including Step 5b catalog reconciliation).

If the SKILL fails to load, the operator types `INIT` or `P_300 INIT` to manually trigger the SIP.

### 11.1.1 Environment Capability Discovery (Mandatory Step Zero)

Before executing any INIT logic, the AI MUST verify filesystem MCP capability via `tool_search`. Look for:

- `windows-mcp:FileSystem`
- `windows-mcp:PowerShell` (also required for Step 5b catalog reconciliation)
- `filesystem:read_text_file` / `filesystem:write_file`
- Any equivalent filesystem MCP server

Report capability in the session header instead of client identity:

- **"Filesystem MCP: available"** — proceed with live disk reads of `tasks/lessons.md`, `tasks/todo.md`, P_000, P_010 every session, AND live catalog query at Step 5b
- **"Filesystem MCP: unavailable"** — fall back to upload-and-download pattern; Step 5b skipped with warning

**Why this matters:** Claude.ai web, Claude Desktop with MCPs, and Claude Code present nearly identical system prompts. Client identity is not reliably detectable from the system prompt alone. Tool availability IS. Reporting capability (not client) prevents false ephemeral-environment claims when filesystem access is in fact available.

**Files read LIVE every session (never cached, never assumed stable across chats):**

| File | Update Cadence |
| :---- | :---- |
| `tasks/lessons.md` | Continuous during active build |
| `tasks/todo.md` | Every task completion |
| `P_000_Account_Parameters_Current.md` | Monthly |
| `P_010_RiskConfig.json` | Twice weekly |

**Live catalog state (per M-017, STRUCTURALLY EMBEDDED in SIP v2.4 Step 5b at Stage 6 start, 2026-05-16):** In addition to the four files above, SIP Step 5b queries `pattern_instances` count, `source_files` count, symbol distribution, and catalog file mtime via `python cli.py catalog-summary` (executed through `windows-mcp:PowerShell`) and `windows-mcp:FileSystem info`. If catalog state diverges from what the most recent dated "Closed in" subsection of `tasks/todo.md` describes (e.g., todo lists patterns as un-ingested that the catalog already holds), the catalog wins; INIT halts before proposing any work that the catalog already shows as done. Catalog mtime newer than the most recent tracking subsection issues an inline WARNING in the session summary. If `catalog-summary` fails (non-zero exit OR the ~4-min `windows-mcp:PowerShell` subprocess timeout), the SIP warns inline and surfaces stderr; the AI proceeds without catalog reconciliation but flags the gap.

**Wall-clock time:** If no shell or clock tool is available in the environment, display date only in the session header — never fabricate a time. Per M-008, attempt `bash_tool` (or PowerShell ConvertTimeBySystemTimeZoneId) BEFORE claiming time is unavailable.

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
- [ ] Module Name Discipline — no collision with Python stdlib module names (M-018)
- [ ] ASCII-only stdout — for any string that will flow through `print()` from a PowerShell-invoked script (M-019)

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
- **Fix:** Verify `pattern_bars` normalized columns are NOT NULL post-ingest; verify matching engine queries `close_pct_from_anchor` etc., not `close`. Stage 6 self-match sanity check (§10.1) catches this class of bug.

### AI proposes work the catalog already shows as done
- **Cause:** INIT trusted `tasks/todo.md` checkboxes over live catalog state (M-017)
- **Fix:** Run `python cli.py catalog-summary` to surface ground truth; reconcile `todo.md` to match. STRUCTURALLY RESOLVED 2026-05-16 in SIP v2.4 Step 5b — INIT now queries catalog automatically.

### `python` resolves to the wrong interpreter in a fresh PowerShell session
- **Cause:** PowerShell ISE profile didn't fire OR PATH prepend missing (M-016)
- **Fix:** `(Get-Command python).Source` should return `C:\Users\Trader\.conda\envs\p140\python.exe`. If not: `$PROFILE` resolves to `D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShellISE_profile.ps1`; verify the file contains the PATH prepend ahead of `Set-Location`; `. $PROFILE` to reload.

### Module fails to import with cryptic circular-import error pointing at a stdlib name
- **Symptom:** `ImportError: cannot import name X from partially initialized module 'signal'` (or `csv`, `math`, `json`, `time`, etc.) — often with a traceback pointing at a third-party library (Pydantic, etc.), masking the real cause
- **Cause:** Module file in `domain/` / `infrastructure/` / `application/` shares a name with a Python stdlib module (M-018; §2.7 anti-pattern). Script-mode `sys.path[0]` prepend causes `import <stdlib_name>` to find the local file first.
- **Fix:** Rename the local file with a descriptive suffix (e.g., `signal.py` → `signal_classifier.py`); update all imports + `cli.py` references.

### Python script output renders red ("NativeCommandError") in PowerShell despite exiting 0
- **Symptom:** All output text appears in red error styling; script succeeded, exit code 0
- **Cause:** Either Unicode characters in stdout crashed on PowerShell cp1252 (M-019; §2.7 anti-pattern), OR a `SyntaxWarning` / `DeprecationWarning` / similar emitted to stderr (M-011 extension)
- **Fix:**
  - For Unicode in stdout: replace box-drawing (`═` / `─` / `│`), em-dashes (`—`), and arrows (`→`) with ASCII (`=`, `-`, `|`, `--`, `->`). Project convention: `_BAR = "=" * 64` (see `utilities/catalog_summary.py` and `infrastructure/report_writer.py` v1.1).
  - For warnings: forward slashes in file-path string literals to avoid `SyntaxWarning: invalid escape sequence '\X'`; OR `warnings.filterwarnings("ignore", category=<Category>, message="<pattern>")` for known-cosmetic; OR `2>&1` redirection at the call site as last resort.

### Report displays returns as "+0.0672%" instead of "+6.72%"
- **Symptom:** Pipeline B report output shows return values two orders of magnitude smaller than expected
- **Cause:** Display layer missing × 100 conversion (M-020; §2.7 anti-pattern). Storage convention: `forward_labels.return_pct` is a decimal fraction; display multiplies by 100.
- **Fix:** Apply `* 100` at the render boundary (see `report_writer.py` v1.1 hotfix). Internal callers (aggregator, signal_classifier) operate in decimal space and need no conversion; only the display layer converts.

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
| Active PowerShell host | ISE — `$PROFILE` resolves to `D:\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShellISE_profile.ps1` (per M-016) |
| `windows-mcp:PowerShell` subprocess timeout | ~4 min client-side; live python validation falls back to operator-run pattern (drop script via `windows-mcp:FileSystem`, operator runs in ISE) |

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
│   ├── live/                          (Pipeline B inbox — daily VP exports, .xlsx)
│   ├── processed/                     (Pipeline B archive)
│   ├── historical_patterns/           (Pipeline A vault, .xlsx)
│   └── archive/                       (cold storage)
├── docs/
│   ├── architecture/                  (P_300_System_Architecture_v2.7.md and successors)
│   ├── archive/                       (prior major versions)
│   ├── migrations/                    (stage closeout reports + migration ledgers)
│   ├── processes/                     (operator-facing runbooks: evaluate_trade.md, add_pattern.md — new Stage 9-followup convention)
│   └── prompts/                       (SIP and prompt library)
├── models/
│   ├── <mmddyy>catalog.db             (active catalog)
│   └── archive/                       (retired catalog variants)
├── outputs/
│   └── reports/                       (Pipeline B optional file output)
├── parameters/
│   ├── optimization_config.json
│   └── ingest_manifest.json
├── python/
│   ├── config.py
│   ├── schemas.py
│   ├── schemas_pipeline_b.py
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

**P_300 SIP trigger:** Type `INIT` or `P_300 INIT` in a new chat. Skill loads protection rules automatically; SIP reads account params, market posture, lessons, current task queue, and live catalog state (Step 5b per M-017).

## Appendix G — Versioning Convention

- `major.minor` for the architecture file
- **Major (v2.0, v3.0)** — structural or architectural redesigns (this rebuild)
- **Minor (v2.1, v2.2 ... v2.5)** — meaningful non-breaking additions
- **Patch-level** changes are inline edits not bumped versions

## Appendix H — Trade Management (Milestone 6 Planning)

### Trading Logic & Rules (P_030 reference)

- BUY requirement: 100% Buy rating across 20, 50, 100, 200-day moving averages
- Risk budget: Standard $525 (1.5% of $35k account)
- Size penalty: 200MA penalty sizing if price is below 200MA
- Liquidity floor: Spread ≤ 10%, Open Interest ≥ 150

### Milestone 6 Trade Management Module

Consumes Aggregator output from Pipeline B. Three required inputs:

| Input | Purpose | Example Mapping |
| :---- | :---- | :---- |
| Confidence / Win-Rate | Position size driver | 80% win rate → 2% risk; 60% win rate → 0.5% risk |
| Expected Horizon | Hold-period selection | Pick the day (5/7/10/15/20) with most reliable historical return |
| Drawdown Threshold | Hard stop-loss placement | Set stop based on worst-historical-analog drawdown |

Risk-management style (fixed percentage, volatility-based trailing, time-based exits) to be selected before build.

---

**End of P_300 System Architecture v2.7**
