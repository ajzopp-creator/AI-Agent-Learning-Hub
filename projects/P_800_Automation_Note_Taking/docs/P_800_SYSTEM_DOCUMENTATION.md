# P_800 SYSTEM_DOCUMENTATION
## Automation Note-Taking & Knowledge Building

---

**Project ID:** P_800
**Version:** 4.0
**Created:** 2026-03-07
**Last Updated:** 2026-06-07
**Owner:** Tony
**Status:** Active

---

## Section 0 — What Changed in v4.0

Full architecture pivot on 2026-06-07. The single-stream `Trades/` mirror has been retired. P_800 now owns the **Obsidian Interface Layer** — a unified, multi-project data surface fed by all trading systems. Key shifts:

- **Vault redesign**: TradeManagement/{P115, P300, P400, P020, signals} + TradeOrderManagement/signals + KnowledgeBase + Bases + Dashboard.md (replaces old Trades/ folder pattern)
- **Python writers**: Consolidated under `python\obsidian_writers\` (renamed from `scripts\` in E3.001); public API via `write_to_vault()` in `shared_resources\python_utils\vault_interface.py`
- **Interface docs**: Detailed schemas, bases, and roadmap live in `P_800_Interface_Arch_Part1_Schemas_v1_0.md` and `P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` (canonical reference; not duplicated here)
- **Phase progress**: E-series cleanup (E1-E3) complete; Interface Layer Phases 5A–5D done; 5E–5H pending (cross-project integrations)

**See Section 0 History** (below) for v3.0 and prior changes.

### Section 0 History

**v3.0 (2026-05-11):** Full vault rebuild on C: Hub, outside OneDrive; daily note ISO format; Bases architecture (Templates/, Bases/, Trades/); MCP bridge reconfigured; fraud cleanup (scam contacts purged); master template consolidation. Vault location: `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\`.

---

## Section 1 — Project Overview

### 1.1 Purpose
P_800 eliminates manual typing and repetitive setup in Tony's daily workflow. It automates note-taking, knowledge capture, and integration across Obsidian, Claude, trading systems (P_115, P_300, P_400, P_020), and external tools.

### 1.2 Goals
- Minimize keystrokes in daily trading and research workflow
- Build a consistent, searchable knowledge base in Obsidian (Interface Layer)
- Feed all trading systems' output into unified queryable Bases
- Provide a daily entry point (Dashboard.md) for all trade/market/research data
- Integrate Claude, Grok, Perplexity, and Gemini efficiently
- Connect automation to Tony's trading projects via the public `write_to_vault()` API

### 1.3 Scope
- Obsidian vault under the Hub at `trading_journal\` (the Interface Layer)
- TradeManagement/ and TradeOrderManagement/ folders (normalized data from all projects)
- KnowledgeBase/ (articles, clipped content, AI summaries)
- Bases/ folder (`.base` files for queryable views)
- Dashboard.md (daily entry point)
- Python automation: `obsidian_writers` package + public `vault_interface.py` API
- Claude ↔ Obsidian MCP bridge (direct read/write to vault)
- Text expansion and voice input workflows (future phases)

### 1.4 Out of Scope
- Trading strategy development (P_115/116/117/118 own)
- Brokerage API connections (P_020 owns)
- Market Posture JSON generation (P_010 owns; P_800 reads only)
- Trade rules / scoring (P_115/116/117/118 + Excel tracker own; P_800 mirrors)
- Signal generation logic (P_115, P_300, P_400 own)

---

## Section 1.5 — Definitions & Acronyms

| Term | Definition |
|------|-----------|
| P_800 | This project — Automation Note-Taking & Knowledge Building |
| Interface Layer | Obsidian vault (trading_journal/) acting as unified display/query surface fed by all upstream projects |
| TradeManagement/ | Vault subfolder containing per-project normalized frontmatter notes: P115/, P300/, P400/, P020/ (and signals/) |
| TradeOrderManagement/ | Vault subfolder for raw JSON signal packets (P_115 → P_400 handoff, not Obsidian notes) |
| KnowledgeBase/ | Vault subfolder for articles, AI summaries, research clipped content |
| Bases/ | Vault subfolder containing `.base` files (Obsidian Bases feature for queryable views) |
| Dashboard.md | Daily entry point note in vault root; links to all six Base views |
| Writer Module | Python script (in obsidian_writers/) that normalizes source data → YAML frontmatter `.md` files |
| write_to_vault() | Public API function in shared_resources\python_utils\vault_interface.py; used by all sending projects |
| obsidian_writers | Python package at projects\P_800_Automation_Note_Taking\python\obsidian_writers\; owns all vault write logic |
| P400SIG | Schema name for raw JSON signal packets (P_115 → P_400); routed to TradeOrderManagement/signals/ |
| SIGNALS_DIR | Config constant pointing to TradeOrderManagement/signals/ (raw JSON signal packets, not frontmatter notes) |
| Frontmatter | YAML metadata block at top of .md file (parsed by Obsidian Bases) |
| Base | Obsidian Bases `.base` file — defines a filtered, sorted, columnar view of notes |
| WHY code | P_020 tag identifying the trading system (e.g., BTD = Buy The Dip, VPT = VantagePoint) |
| SIG code | P_020 tag for signal conviction (A=high, B=standard, C=marginal, X=counter) |
| SoT | Source of Truth — the upstream system (Excel, SQLite, TXT, JSON) that owns the data |
| MCP | Model Context Protocol — open standard for connecting Claude to external tools (Obsidian vault) |
| Local REST API | Obsidian community plugin creating a local server for MCP bridge |
| MCP Bridge | Connection between Claude Desktop and Obsidian via Local REST API + claude_desktop_config.json |
| P_010 | Tony's prompt system for market posture analysis (owns posture JSON, RiskConfig.json) |
| P_020 | Performance analysis + cross-system trade management (owns SQLite trade DB, P_020 tags) |
| P_115 | Buy The Dip trading system (V110 with 200-MA filter) |
| P_300 | VantagePoint Grid system |
| P_400 | Trade Order Management (BUY signal intake + Council logic) |
| TOS | ThinkOrSwim — primary trading platform |
| VantagePoint | AI-based market forecasting tool |

---

## Section 2 — Operating Rules

### 2.1 AI Behavior Rules & Constraints

**MUST:**
- Acknowledge current date at start of each session
- Prioritize low-typing / minimal-effort solutions for Tony
- Suggest Claude Artifacts before recommending external software installs
- Use the Obsidian MCP tools to read/write vault content when bridge is configured
- Treat P_800_Daily_Flow.md as the ONE master template — never create competing templates
- Excel tracker is source-of-truth for trades; Obsidian notes are one-way mirrors
- File size discipline: 300 lines max per code/config file, 50 lines max per function
- Refer to Interface Arch docs as canonical for detailed schemas/bases (avoid duplication)

**MUST NOT:**
- Recommend solutions requiring heavy coding without providing full code
- Assume Tony knows advanced Python or VS Code features
- Suggest paid tools without exhausting free options first
- Build artifacts that generate or modify P_010 market posture data
- Create or modify Obsidian templates outside of P_800
- Write to Excel tracker from Obsidian (one-way mirror only)
- Re-introduce scam-contact references (Investment Pioneer Club, Club 84, Freedom Income Options)

---

## Section 3 — Daily Flow Reference

Tony's daily routine and automation targets:

| Time | Activity | Automation Target |
|------|----------|------------------|
| Morning | Open Obsidian daily note | Ctrl+N at vault root → Templater fires P_800_Daily_Flow.md |
| Morning | Bible verse + daily quote + humor | Auto-fetched by Templater via tp.obsidian.requestUrl |
| Morning | Senior exercise routine | Pre-filled wrist-friendly checklist in template |
| Morning | Google Calendar review | Claude MCP injects events on request |
| Morning | TOS + VantagePoint pre-market | Manual notes into Market Analysis section |
| Morning | Market Posture | P_010 generates JSON → paste into Market Analysis → Market Posture subsection |
| Midday | Trade execution | Logged to Excel tracker; nightly export writes to TradeManagement/P115/ (or relevant folder) |
| Evening | AI trends review | Template section |
| Evening | Daily rollover / review | Tasks plugin checkboxes |

---

## Section 4 — Tool Inventory

| Tool | Category | Status | Notes |
|------|----------|--------|-------|
| Obsidian | Note-taking | ✅ Active (1.12.7+) | Primary knowledge base — vault on C: Hub |
| Claude (claude.ai + Desktop) | AI Assistant | ✅ Active | Primary AI tool; Desktop required for MCP |
| ThinkOrSwim (TOS) | Trading Platform | ✅ Active | Primary brokerage platform |
| VantagePoint | Market Forecasting | ✅ Active | AI-based forecasting |
| Grok | AI Assistant | ✅ Active | Secondary AI |
| Perplexity | AI Search | ✅ Active | Research + quotes |
| Gemini / NotebookLM | AI Assistant | ✅ Active | Supplementary |
| LM Studio | Local LLM | ✅ Active | `http://127.0.0.1:1234/v1` — local LLM |
| Espanso | Text Expander | Planned | Free, cross-platform |
| AutoHotkey | Windows Automation | Planned | Free |
| Templater | Obsidian Plugin | ✅ Installed + Configured | Folder template binding `/` → `Templates/P_800_Daily_Flow.md` |
| QuickAdd | Obsidian Plugin | ✅ Installed | Hotkey macros |
| Google Calendar | Obsidian Plugin | ✅ Installed | Calendar sync |
| Tasks | Obsidian Plugin | ✅ Installed | Checkbox tracking |
| Obsidian Web Clipper | Browser Extension | ✅ Installed | Web capture |
| Obsidian Local REST API | Obsidian Plugin | ✅ Installed + Active | MCP bridge endpoint — port 27124 HTTPS |
| Bases (Obsidian core) | Native feature | ✅ Available | No plugin install — query notes as a database |
| Claude Desktop App | AI Desktop App | ✅ Installed + Active | Required for MCP bridge |
| Claude ↔ Obsidian MCP Bridge | Integration | ✅ Configured 2026-06-07 | Points to C: Hub vault; uses p140 conda Python |

---

## Section 5 — Build Roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Obsidian daily note template (initial version) | ✅ Complete (2026-03-07) |
| 2 | Obsidian Web Clipper + Defuddle setup guide | ✅ Complete (2026-03-08) |
| 3 | Market Posture Display artifact | ✅ Complete (2026-03-08) |
| 3.5 | Claude ↔ Obsidian MCP Bridge | ✅ Complete (2026-03-16) |
| 3.6 | Template ownership transfer + consolidation | ✅ Complete (2026-03-19) |
| 4 | Vault rebuild — clean architecture, Bases foundation, C: Hub location | ✅ Complete (2026-05-11) |
| E1 | Python project structure (initial) | ✅ Complete (2026-05-22) |
| E2 | Duplicate/dead code cleanup | ✅ Complete (2026-06-04) |
| E3 | Folder structure cleanup (scripts\ → python\); import hygiene | ✅ Complete (2026-06-06) |
| 5A | Vault subfolders (TradeManagement/, TradeOrderManagement/, KnowledgeBase/, Bases/) | ✅ Complete (2026-05-22) |
| 5B | Six .base files (P115_Evaluations, P300_Signals, P400_Trades, P020_Performance, Open_Positions, KB_Articles) | ✅ Complete (2026-05-22) |
| 5C | Dashboard.md — link-only v1.0 | ✅ Complete (2026-05-22) |
| 5D | Vault interface engine + public API + README | ✅ Complete (2026-05-22) |
| 5E | P_300 integration — call write_to_vault() from P_300 project | Planned |
| 5F | P_020 integration — call write_to_vault() from P_020 project | Planned |
| 5G | KB Templater template + Web Clipper config | Planned |
| 5H | P_400 integration — after P_400 schema locked | Planned |
| 4 checkpoint | E4.001 — Git + Backup strategy | Planned |
| 6 | Dataview embedded dashboard (trigger: 2+ projects live) | Planned |

---

## Section 5.1 — Enhancement Backlog

| # | Date Logged | Enhancement | Detail | Priority |
|---|-------------|-------------|--------|----------|
| 1 | 2026-03-12 | Telegram API — Chat Extraction | Auto-extract messages from legitimate Telegram trading channels. Scam channels permanently excluded. | High |
| 2 | 2026-03-12 | Google Calendar API — Python Script | Lower priority — Claude MCP + Google Calendar MCP may replace Python script. Re-evaluate before building. | Medium |
| 3 | 2026-05-11 | Global Environment Detection Skill | Promote STEP 0 (Windows-MCP check) from project-scoped to a global skill. Partially live via `system-doc-initializer`; formalize. | Medium |
| 4 | 2026-04-08 | Claude Code Evaluation | Evaluate as potential replacement for standalone Python scripts in P_800 automations. | Medium |

---

## Section 5.2 — MCP Bridge Configuration

### Claude ↔ Obsidian MCP Bridge

**What it does:** Allows Claude to read and write directly to the active Obsidian vault. Claude can inject content into any note on command.

**Components:**

| Component | Details |
|-----------|---------|
| Obsidian Plugin | Local REST API — installed and enabled |
| Plugin Port | 27124 (HTTPS encrypted) |
| Plugin Host | 127.0.0.1 (localhost) |
| API Key | Auto-generated per vault by Local REST API plugin; stored in `claude_desktop_config.json` |
| Config File | `%APPDATA%\Claude\claude_desktop_config.json` |
| MCP Server | `mcp_obsidian` Python package, invoked via p140 conda Python |

**`claude_desktop_config.json` — obsidian entry (canonical):**

```json
"obsidian": {
  "command": "C:\\Users\\Trader\\.conda\\envs\\p140\\python.exe",
  "args": [
    "-c",
    "from mcp_obsidian import main; main()"
  ],
  "env": {
    "OBSIDIAN_API_KEY": "<stored in config file>",
    "OBSIDIAN_HOST": "127.0.0.1"
  }
}
```

**Capabilities unlocked:**
- Read any note in the active vault
- Write / append content to daily notes on command
- List vault files and directories
- Inject formatted content directly into note sections

**Active vault:**
- Vault path: `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\`
- Daily note format: `trading_journal/YYYY-MM-DD.md`
- Templates: `trading_journal/Templates/`
- Bases: `trading_journal/Bases/`
- Dashboard: `trading_journal/Dashboard.md`
- Master template: `Templates/P_800_Daily_Flow.md`

**Claude Desktop restart requirement:**
After any change to OBSIDIAN_API_KEY, Claude Desktop must be fully quit (tray icon → Quit) and reopened.

---

## Section 5.3 — Interface Layer Architecture

### Canonical Reference

Detailed schemas, base definitions, Python writer structure, and build phase details live in:
- `P_800_Interface_Arch_Part1_Schemas_v1_0.md` (vault folder structure, data schemas for P115/P300/P400/P020/KB)
- `P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` (six Bases definitions, Dashboard design, Python writers, roadmap 5A–5H)

**Do not duplicate** architecture docs here. This section summarizes only the folder map and APIs.

### Vault Folder Map (Source: config.py VAULT_FOLDER_MAP)

```
TradeManagement/P115/     ← one frontmatter .md per P_115 evaluation
TradeManagement/P300/     ← one frontmatter .md per P_300 signal report
TradeManagement/P400/     ← one frontmatter .md per P_400 trade lifecycle
TradeManagement/P020/     ← one frontmatter .md per P_020 closed trade
TradeOrderManagement/signals/  ← raw JSON signal packets (P_115 → P_400, P400SIG schema)
KnowledgeBase/            ← articles, AI summaries, research clipped content
Bases/                    ← six .base queryable views (canonical in Arch Part2)
Templates/                ← P_800_Daily_Flow.md (master template)
Dashboard.md              ← daily entry point (vault root)
```

### Public API

All sending projects (P_115, P_300, P_400, P_020) import and call:

```python
from shared_resources.python_utils.vault_interface import write_to_vault

write_to_vault("P115", {"date": "2026-06-07", "symbol": "AAPL", ...})
write_to_vault("P400", {"date": "2026-06-07", "ticker": "NVDA", ...})
```

**Implementation:** `shared_resources\python_utils\vault_interface.py` (reads canonical schemas from `obsidian_writers\schemas.py`, orchestrates write_handler, confirms routing to correct TradeManagement/<schema> subfolder).

**No upstream project has Obsidian knowledge.** P_800 handles all vault logic.

---

## Section 6 — Obsidian Template Reference

### 6.1 Template Ownership
**P_800 owns ALL Obsidian templates.** No other project creates or modifies templates.

### 6.2 Active Templates

| File | Status | Owner | Purpose |
|------|--------|-------|---------|
| `P_800_Daily_Flow.md` | ✅ Active master (v3.0) | P_800 | Full daily note template — vault root |

### 6.3 Master Template Location

**Live path:**
`C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\Templates\P_800_Daily_Flow.md`

### 6.4 P_800_Daily_Flow.md Contents (v3.0)

**Frontmatter schema:**

```yaml
---
date: <% tp.date.now("YYYY-MM-DD") %>
day_of_week: <% tp.date.now("dddd") %>
template_version: "3.0"
template_owner: "P_800"
market_posture: null
market_regime: null
risk_level: null
trade_count: 0
key_setups: []
session_status: open
---
```

**Body sections (in order):**
1. H1 date header
2. Morning Starter — Verse of the Day, Daily Quote, Joke (auto-fetched)
3. Senior Exercise (wrist-friendly checklist)
4. Schedule Check — placeholder; Claude MCP injects Google Calendar events on request
5. Market Analysis
   - Pre-Market Analysis (TOS + VantagePoint notes)
   - Market Posture (paste-target for P_010 JSON block)
6. AI Trends & Research
7. Daily Rollover / Review (checkbox list)

Footer: `*Template owner: P_800 -- v3.0*`

**Templater settings:**
- Template folder location: `Templates`
- Trigger Templater on new file creation: ON
- Folder template — `/` (vault root): `Templates/P_800_Daily_Flow.md`

---

## Section 7 — Folder Structure

### 7.1 Active Vault

```
C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\
├── .obsidian\                              <- Obsidian config (auto-created)
├── Templates\
│   └── P_800_Daily_Flow.md                 <- Master template (P_800 owned)
├── Bases\
│   ├── P115_Evaluations.base
│   ├── P300_Signals.base
│   ├── P400_Trades.base
│   ├── P020_Performance.base
│   ├── Open_Positions.base
│   └── KB_Articles.base
├── TradeManagement\
│   ├── P115\                               <- one .md per P_115 evaluation
│   ├── P300\                               <- one .md per P_300 signal
│   ├── P400\                               <- one .md per P_400 trade
│   ├── P020\                               <- one .md per P_020 closed trade
│   └── signals\                            <- legacy folder (not in config map)
├── TradeOrderManagement\
│   └── signals\                            <- raw JSON signal packets (P400SIG schema)
├── KnowledgeBase\                          <- articles, clipped content, AI summaries
├── Dashboard.md                            <- daily entry point (vault root)
└── YYYY-MM-DD.md                           <- daily notes (one per day)
```

### 7.2 Hub Project Folder

```
C:\Users\Trader\AI-Agent-Learning-Hub\
├── trading_journal\                        <- Obsidian vault (above)
└── projects\
    └── P_800_Automation_Note_Taking\
        ├── docs\
        │   ├── P_800_SYSTEM_DOCUMENTATION.md    <- this file (v4.0)
        │   ├── P_800_Interface_Arch_Part1_Schemas_v1_0.md
        │   ├── P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md
        │   └── backups\
        ├── claude_artifacts\
        ├── espanso\
        └── python\
            └── obsidian_writers\
                ├── __init__.py
                ├── config.py
                ├── schemas.py
                ├── domain\
                │   ├── validator.py
                │   ├── frontmatter_builder.py
                │   └── filename_builder.py
                ├── infrastructure\
                │   └── vault_writer.py
                ├── application\
                │   └── write_handler.py
                ├── logger_setup.py
                └── tests\
```

---

## Section 8 — Workflows

### Workflow 8.1 — Morning Startup (Minimal Typing)
1. Open Obsidian (vault auto-loads to `trading_journal`)
2. Ctrl+N at vault root → Templater fires P_800_Daily_Flow.md
3. Verse, quote, joke auto-fetched. Frontmatter populates with date/day.
4. Rename file to today's date in `YYYY-MM-DD.md` format
5. Tell Claude: "Inject today's Google Calendar events into my daily note"
6. Open P_010 artifact → generate Market Posture JSON → paste into Market Analysis → Market Posture subsection
7. TOS + VantagePoint → notes into Pre-Market Analysis subsection
8. Dictate trade plans via Win+H if helpful

### Workflow 8.2 — New Claude Artifact Build
1. Start session in P_800
2. Describe the tool needed
3. Claude builds artifact → test in session → save to `claude_artifacts\` folder

### Workflow 8.3 — Claude Direct Vault Write (MCP Bridge)
1. Start Claude Desktop session (MCP tools load automatically)
2. Tell Claude what to write and where: "Append today's TOS notes to the Pre-Market Analysis section of today's daily note"
3. Claude reads current note, appends or injects content, confirms success
4. Verify in Obsidian — content appears immediately

### Workflow 8.4 — Template Update Process
1. Open session in P_800 project
2. Read current template
3. Edit via `filesystem:write_file` or PowerShell with UTF8 no-BOM encoding
4. Verify by Ctrl+N test in Obsidian
5. Bump template_version in frontmatter

### Workflow 8.5 — Interface Layer Data Intake (write_to_vault API)
1. Upstream project (P_115, P_300, P_400, P_020) imports `write_to_vault` from shared_resources
2. Project normalizes its data dict: `{"date": "...", "symbol": "...", ...}` (per schema in Arch Part1)
3. Project calls: `write_to_vault("P115", data_dict)`
4. `vault_interface.py` validates schema, routes to TradeManagement/P115/, writes frontmatter .md
5. Obsidian Bases query the folder; data appears in views automatically

---

## Section 9 — Error Corrections Log

| # | Date | Error | Correction | Severity |
|---|------|-------|-----------|----------|
| 1 | 2026-03-07 | Created unnecessary sub-projects | P_800 is one project — use sections | Medium |
| 2 | 2026-03-08 | Built Market Posture JSON Generator in P_800 | P_800 displays P_010 output only — never generates posture data | High |
| 3–5 | 2026-03-12 | Incorrect contact names, channels, Telegram mapping | All identified as coordinated scams; all references purged | Medium |
| 6 | 2026-03-16 | Vault root recorded as outer "Trading Journal" folder | Corrected; real root = `TradingJournal\` | Medium |
| 7 | 2026-03-16 | Vault path recorded as `D:\OneDrive\...` throughout v1.9–v2.0 | OneDrive Documents redirect masked byte location; both C: and D: claims were half-true. Solution: vault relocated to C: Hub outside OneDrive. | High |
| 8 | 2026-03-19 | P_010 owned Obsidian templates — scope creep | P_800 owns ALL templates. P_010 generates content only. | Medium |
| 9 | 2026-05-11 | Templater used non-existent `tp.web.request()` function | Use `tp.obsidian.requestUrl({url: "..."})` for external HTTP calls. | Medium |
| 10 | 2026-05-22 | Vault layout Trades/ → Interface Layer (TradeManagement/TradeOrderManagement/KnowledgeBase/Bases) not documented | Architecture pivot completed; detailed docs (Arch Part1 & Part2) created as canonical reference. | High |
| 11 | 2026-06-06 | Python folder structure `scripts\` → `python\`; E3.001 cleanup completed | Verified E3 work complete; import all modules clean. | Medium |
| 12 | 2026-06-07 | System doc v3.0 stale (described old Trades/ layout) | Updated to v4.0; reflects live Interface Layer architecture (TradeManagement/TradeOrderManagement/KnowledgeBase/Bases) and Python writer consolidation. | High |

---

## Section 10 — Session Log

| Date | Session Topic | Key Decisions |
|------|--------------|---------------|
| 2026-03-07 | Project inception | P_800 created, single project structure |
| 2026-03-08 | Phase 3 — Market Posture Display | P_010 owns posture generation; P_800 reads only |
| 2026-03-16 | Phase 3.5 — MCP Bridge | Local REST API installed; vault read/write confirmed live |
| 2026-03-19 | Phase 3.6 — Template ownership transfer | All templates moved to P_800 ownership |
| 2026-05-11 | Phase 4 — Vault rebuild | New vault at `trading_journal\` (C: Hub, outside OneDrive); Bases/Templates subfolders; Templater bound |
| 2026-05-22 | Phases 5A–5D — Interface Layer | Vault subfolders created; six .base files; Dashboard.md; vault_interface.py + README; public API locked |
| 2026-06-04 | E-series cleanup (E1, E2 complete) | Duplicate code purged; dead imports removed |
| 2026-06-06 | E3.001 complete | Folder structure scripts → python; import test verified clean |
| 2026-06-07 | System doc v4.0 rewrite | Architecture pivot documented; Interface Arch docs confirmed as canonical reference; legacy folders cleaned |

---

## Section 11 — Parameter Registry

| Parameter | Value |
|-----------|-------|
| Project ID | P_800 |
| Project structure | Single project — no sub-projects |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project folder | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\` |
| Docs folder | `...\projects\P_800_Automation_Note_Taking\docs\` |
| Python folder | `...\projects\P_800_Automation_Note_Taking\python\` |
| obsidian_writers package | `...\python\obsidian_writers\` |
| vault_interface.py | `shared_resources\python_utils\vault_interface.py` |
| Obsidian vault root | `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` |
| Daily note format | `YYYY-MM-DD.md` |
| Templates folder | `trading_journal\Templates\` |
| Master template | `Templates\P_800_Daily_Flow.md` (v3.0) |
| Bases folder | `trading_journal\Bases\` |
| Dashboard | `trading_journal\Dashboard.md` |
| TradeManagement folder | `trading_journal\TradeManagement\` |
| TradeOrderManagement folder | `trading_journal\TradeOrderManagement\` |
| KnowledgeBase folder | `trading_journal\KnowledgeBase\` |
| SIGNALS_DIR (config constant) | `trading_journal\TradeOrderManagement\signals\` |
| Interface Arch Part1 | `docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` |
| Interface Arch Part2 | `docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` |
| Template owner | P_800 (all templates) |
| Trade source-of-truth | Excel tracker (P_115/P_300/P_400/P_020 feed via write_to_vault) |
| Trade sync direction | Upstream → TradeManagement/ (one-way via write_to_vault) |
| Primary note-taking tool | Obsidian (1.12.7+) |
| Primary AI tool | Claude (Desktop required for MCP) |
| Trading platform | ThinkOrSwim (TOS) |
| Conda environment | p140 (`C:\Users\Trader\.conda\envs\p140\python.exe`) |
| Local LLM | LM Studio at `http://127.0.0.1:1234/v1` |
| Obsidian Local REST API port | 27124 (HTTPS) |
| MCP server command | `C:\Users\Trader\.conda\envs\p140\python.exe -c "from mcp_obsidian import main; main()"` |
| Claude Desktop config | `%APPDATA%\Claude\claude_desktop_config.json` |
| MCP Bridge status | ✅ LIVE — configured 2026-06-07 |
| File size discipline | 300 lines max per code/config file; 50 lines max per function |
| Python skill level | Novice |
| VS Code skill level | Novice |

---

*End of P_800 SYSTEM DOCUMENTATION v4.0 — 2026-06-07*
