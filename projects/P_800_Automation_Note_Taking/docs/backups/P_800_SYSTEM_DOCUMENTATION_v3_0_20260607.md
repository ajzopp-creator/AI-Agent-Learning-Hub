# P_800 SYSTEM_DOCUMENTATION
## Automation Note-Taking & Knowledge Building

---

**Project ID:** P_800
**Version:** 3.0
**Created:** 2026-03-07
**Last Updated:** 2026-05-11
**Owner:** Tony
**Status:** Active

---

## Section 0 — What Changed in v3.0

Full vault rebuild on 2026-05-11. Key changes from v2.1:

- **Vault relocated** from OneDrive-redirected `C:\Users\Trader\Documents\...` to `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` — outside OneDrive's reach, peer to `projects\`, cross-system rather than per-project data
- **Daily note format** changed to ISO `YYYY-MM-DD.md` (was `MM-DD-YYYY.md`)
- **Bases architecture** added — Templates/, Bases/, TradeManagement/ subfolders under vault root; Excel tracker remains source of truth; Python export script will write one frontmatter-only `.md` per trade row to `TradeManagement/`; Bases queries the folder
- **Master template P_800_Daily_Flow.md** rebuilt clean — 6 body sections, frontmatter schema for Bases queries, no WhatsApp section (scam contacts purged), Market Posture absorbed into Market Analysis, no Trade Execution Log table (redundant with TradeManagement/ base)
- **MCP config** corrected to reflect actual command (`p140` conda Python invoking `mcp_obsidian.main`, not `uvx mcp-obsidian` as v2.1 documented)
- **Templater API** corrected — `tp.web.request` does not exist; `tp.obsidian.requestUrl` is the supported function for external HTTP calls
- **OneDrive Documents redirect lesson** logged — Windows redirects `C:\Users\<user>\Documents` to `D:\OneDrive\Documents` when OneDrive Documents sync is enabled, masking the true byte location. Both prior C:/D: claims were half-true. Solution: keep AJZ Strategies work under the Hub (outside OneDrive's scope by default)
- **Fraud cleanup ratified** — Investment Pioneer Club, Club 84, Freedom Income Options contacts confirmed purged from all documentation

---

## Section 1 — Project Overview

### 1.1 Purpose
P_800 exists to eliminate manual typing and repetitive setup in Tony's daily workflow. It automates note-taking, knowledge capture, AI prompting, and daily flow initialization across Obsidian, Claude, and connected tools.

### 1.2 Goals
- Minimize keystrokes in daily trading and research workflow
- Build a consistent, searchable knowledge base in Obsidian
- Mirror the Excel trade tracker into a queryable Bases-driven structure
- Integrate Claude, Grok, Perplexity, and Gemini efficiently
- Connect automation to Tony's existing trading projects (P_010, P_020, etc.)

### 1.3 Scope
- Obsidian vault under the Hub at `trading_journal\`
- Templates folder (P_800 owns ALL templates)
- Bases folder (`.base` files for trade and posture queries)
- TradeManagement folder (one frontmatter-only `.md` per trade, machine-generated)
- Claude Artifacts for daily tools
- Text expansion tools (Espanso, AutoHotkey, Windows PowerToys)
- Voice input workflows
- Python automation scripts (Phase 5 onward — Excel→Markdown export, Telegram extraction)
- Claude ↔ Obsidian MCP bridge (direct read/write to vault)

### 1.4 Out of Scope
- ThinkScript strategy development (trading project series)
- Brokerage API connections (P_020 series)
- Market Posture JSON generation (P_010 owns; P_800 reads only)
- Trade rules / scoring (P_115/116/117/118 + Excel tracker; P_800 mirrors only)
- Cross-system Trade Management logic (P_020)

---

## Section 1.5 — Definitions & Acronyms

| Term | Definition |
|------|-----------|
| P_800 | This project — Automation Note-Taking & Knowledge Building |
| Daily Flow | Tony's morning-to-evening routine: quotes → exercise → calendar → market posture → TOS analysis → AI trends |
| Market Posture JSON | Structured JSON block summarizing daily market bias (bullish/neutral/bearish), regime, key setups, risk level |
| P_010 | Tony's prompt system for market posture analysis (owns posture JSON, RiskConfig.json) |
| P_020 | Tony's performance analysis + cross-system trade management |
| P_115 | Buy The Dip trading system (V110 with 200-MA filter) |
| TOS | ThinkOrSwim — primary trading platform |
| VantagePoint | AI-based market forecasting tool used alongside TOS |
| Templater | Obsidian community plugin for dynamic template population |
| QuickAdd | Obsidian plugin for hotkey-triggered macros |
| Espanso | Free cross-platform text expander (system-wide) |
| AHK | AutoHotkey — Windows automation scripting tool |
| Market Posture Display | P_800 read-only artifact — displays P_010 JSON, outputs Obsidian note block |
| MCP | Model Context Protocol — open standard for connecting Claude to external tools and data |
| Local REST API | Obsidian community plugin that creates a local server Claude can connect to via MCP |
| MCP Bridge | Connection between Claude Desktop and Obsidian via Local REST API + claude_desktop_config.json |
| Bases | Obsidian core feature (1.12.7+) — query notes as a database using frontmatter properties; `.base` files define views |
| TradeManagement/ | Vault subfolder containing one frontmatter-only `.md` per trade row, machine-generated from the Excel tracker |
| Excel Tracker | `Tracker_Log_Schema_v9_4_0_1.md` — 27-LOCKED-column source-of-truth for all TradeManagement |

---

## Section 2 — Operating Rules

### 2.1 AI Behavior Rules & Constraints

**MUST:**
- Acknowledge current date at start of each session
- Run `tool_search("PowerShell")` at session start (handled globally by the `system-doc-initializer` skill — verifies Claude Desktop runtime)
- Prioritize low-typing / minimal-effort solutions for Tony
- Suggest Claude Artifacts before recommending external software installs
- Keep instructions step-by-step and beginner-friendly
- Use the Obsidian MCP tools to read/write vault content when the bridge is configured for the active vault
- Treat `P_800_Daily_Flow.md` as the ONE master template — never create competing templates
- Excel tracker is the source-of-truth for TradeManagement; Obsidian TradeManagement/ is a one-way mirror
- File size discipline: 300 lines max per code/config file, 50 lines max per function

**MUST NOT:**
- Recommend solutions requiring heavy coding without providing the full code
- Assume Tony knows advanced Python or VS Code features
- Suggest paid tools without first exhausting free options
- Skip the SYSTEM_DOCUMENTATION load at session start
- Build artifacts that generate or modify the Market Posture JSON — that belongs to P_010
- Allow P_800 artifacts to write to the P_010 posture file under any circumstances
- Create or modify Obsidian templates outside of P_800 — P_800 owns all templates
- Write to the Excel tracker from Obsidian — one-way only
- Re-introduce scam-contact references (Investment Pioneer Club, Club 84, Freedom Income Options) anywhere in docs, templates, or scripts

---

## Section 3 — Daily Flow Reference

Tony's daily routine and automation targets:

| Time | Activity | Automation Target |
|------|----------|------------------|
| Morning | Open Obsidian daily note | Ctrl+N at vault root → Templater fires P_800_Daily_Flow.md |
| Morning | Bible verse + daily quote + humor joke | Auto-fetched by Templater (`tp.obsidian.requestUrl` + `tp.web.daily_quote`) |
| Morning | Senior exercise routine | Pre-filled wrist-friendly checklist in template |
| Morning | Google Calendar review | Claude MCP injects events on request |
| Morning | TOS + VantagePoint pre-market | Manual notes into Market Analysis section |
| Morning | Market Posture | P_010 generates JSON → paste into Market Analysis → Market Posture subsection |
| Midday | Trade execution | Logged to Excel tracker; nightly Excel→Markdown export writes to TradeManagement/ |
| Midday | Trade rules / signals | Generated by P_115/116/117/118 prompt suite |
| Evening | AI trends review | Template section |
| Evening | Daily rollover / review | Tasks plugin checkboxes |

Manual chat-channel intelligence (formerly WhatsApp section) is discontinued. Channels purged as confirmed scams. A legitimate replacement source, if one emerges, will be scoped explicitly.

---

## Section 4 — Tool Inventory

| Tool | Category | Status | Notes |
|------|----------|--------|-------|
| Obsidian | Note-taking | ✅ Active (1.12.7+) | Primary knowledge base — vault on C: Hub |
| Claude (claude.ai + Desktop) | AI Assistant | ✅ Active | Primary AI tool; Desktop required for Windows-MCP |
| ThinkOrSwim (TOS) | Trading Platform | ✅ Active | Primary brokerage platform |
| VantagePoint | Market Forecasting | ✅ Active | AI-based forecasting |
| Grok | AI Assistant | ✅ Active | Secondary AI |
| Perplexity | AI Search | ✅ Active | Research + quotes |
| Gemini / NotebookLM | AI Assistant | ✅ Active | Supplementary |
| Copilot | AI (MS Apps) | ✅ Active | Microsoft integration |
| LM Studio | Local LLM | ✅ Active | `http://127.0.0.1:1234/v1` — primary LLM for briefing pipeline |
| Espanso | Text Expander | Planned | Free, cross-platform |
| AutoHotkey | Windows Automation | Planned | Free |
| Templater | Obsidian Plugin | ✅ Installed + Configured | Folder template binding `/` → `Templates/P_800_Daily_Flow.md` |
| QuickAdd | Obsidian Plugin | ✅ Installed | Hotkey macros |
| Google Calendar | Obsidian Plugin | ✅ Installed | Calendar sync |
| Tasks | Obsidian Plugin | ✅ Installed | Checkbox tracking |
| Obsidian Web Clipper | Browser Extension | ✅ Installed | Web capture (Defuddle 0.10.9+) |
| Obsidian Local REST API | Obsidian Plugin | ✅ Installed + Active | MCP bridge endpoint — port 27124 HTTPS |
| Bases (Obsidian core) | Native feature | ✅ Available | No plugin install — query notes as a database |
| Claude Desktop App | AI Desktop App | ✅ Installed + Active | Required for MCP bridge |
| Claude ↔ Obsidian MCP Bridge | Integration | ✅ Reconfigured 2026-05-11 | Points at new vault; uses p140 conda Python |
| Telegram API | Chat Extraction | Enhancement Backlog | See Section 5.1, Enhancement #1 |

---

## Section 5 — Build Roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Obsidian daily note template (initial version) | ✅ Complete (2026-03-07) |
| 2 | Obsidian Web Clipper + Defuddle setup guide | ✅ Complete (2026-03-08) |
| 3 | Market Posture Display artifact | ✅ Complete (2026-03-08) |
| 3.5 | Claude ↔ Obsidian MCP Bridge (D: vault) | ✅ Complete (2026-03-16) |
| 3.6 | Template ownership transfer + consolidation | ✅ Complete (2026-03-19) |
| 4 | Vault rebuild — clean architecture, Bases foundation, C: Hub location | ✅ Complete (2026-05-11) |
| 5 | Excel→Markdown export script + three starter `.base` files | Planned |
| 6 | Chat Formatter (formerly WhatsApp — channels purged; legitimate source TBD) | ⏸ Paused |
| 7 | Daily Flow Launcher artifact | Planned |
| 8 | Espanso text expansion setup | Planned |
| 9 | Voice input workflow guide | Planned |

---

## Section 5.1 — Enhancement Backlog

| # | Date Logged | Enhancement | Detail | Priority |
|---|-------------|-------------|--------|----------|
| 1 | 2026-03-12 | Telegram API — Chat Extraction | Auto-extract messages from legitimate Telegram trading channels (https://core.telegram.org/api). Scam channels permanently excluded. | High |
| 2 | 2026-03-12 | Google Calendar API — Python Script | Lower priority — Claude MCP + Google Calendar MCP may replace Python script. Re-evaluate before building. | Medium |
| 3 | 2026-05-11 | Global Environment Detection Skill | Promote STEP 0 (Windows-MCP check via `tool_search`) from project-scoped P_115 to a global skill. Partially live via `system-doc-initializer`; formalize as a dedicated `environment-detection` skill. | Medium |
| 4 | 2026-04-08 | Claude Code Evaluation | Evaluate as potential replacement for standalone Python scripts in P_800 automations. | Medium |

---

## Section 5.2 — MCP Bridge Configuration

### Claude ↔ Obsidian MCP Bridge

**What it does:** Allows Claude to read and write directly to the active Obsidian vault. Claude can inject content into any section of any daily note on command.

**Components:**

| Component | Details |
|-----------|---------|
| Obsidian Plugin | Local REST API — installed and enabled |
| Plugin Port | 27124 (HTTPS encrypted) |
| Plugin Host | 127.0.0.1 (localhost) |
| API Key | Auto-generated per vault by the Local REST API plugin; stored in `claude_desktop_config.json` |
| Config File | `%APPDATA%\Claude\claude_desktop_config.json` |
| MCP Server | `mcp_obsidian` Python package, invoked via the p140 conda Python |

**`claude_desktop_config.json` — obsidian entry (canonical as of v3.0):**

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

Note: v2.1 documented a `uvx mcp-obsidian` command — that was never the actual config. The p140 conda invocation has been live since the bridge was first set up.

**Capabilities unlocked:**
- Read any note in the active vault
- Write / append content to daily notes on command
- List vault files and directories
- Inject formatted content directly into note sections

**Scope boundary:** MCP write access is for daily note content only. Claude must never write to P_010 posture files via MCP. Claude must never modify Excel tracker rows via MCP.

**Active vault (C: Hub — v3.0):**
- Vault path: `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\`
- Daily note format: `trading_journal/YYYY-MM-DD.md`
- Templates: `trading_journal/Templates/`
- Bases: `trading_journal/Bases/`
- TradeManagement: `trading_journal/TradeManagement/`
- Master template: `Templates/P_800_Daily_Flow.md`

**Claude Desktop restart requirement:**
After any change to OBSIDIAN_API_KEY (e.g., switching vaults or rotating the key), Claude Desktop must be fully quit (tray icon → Quit) and reopened. The MCP server holds the env vars in memory at spawn time.

---

## Section 5.3 — Bases Architecture (NEW in v3.0)

### Source-of-truth split
- **Excel tracker** (`Tracker_Log_Schema_v9_4_0_1.md` — 27 LOCKED columns) remains the canonical record for every trade
- **Obsidian TradeManagement/** is a one-way mirror: each `.xlsx` row becomes one frontmatter-only `.md` file
- One-way sync means Obsidian edits cannot corrupt Excel

### Why Excel stays SoT
Locked 27-column schema, V110 scoring logic, copy-paste Excel-ready workflow are battle-tested. Rebuilding in Obsidian destroys value. Bases needs notes (not table rows) for granular queries by ticker, outcome, signal source, date range, strategy.

### Trade note frontmatter (27 columns → snake_case YAML)

```yaml
---
date: 2026-05-09
symbol: MOD
signal_source: P_115
step1_verdict: BUY
pattern_type: "--"
breakout_verdict: "--"
breakout_volume_multiple: null
distribution_day_count: null
follow_through_day: null
market_direction: STANDARD
rs_vs_spy: null
fundamentals_tier: 3
analysis_tier: 3
candle_tier: 2
setup_score: 3
liquidity_tier: null
traded: N
entry_price: null
tp_level: null
sl_level: null
stop_level: null
risk_pct: null
account_balance: 32812
outcome: null
recheck_status: null
simulation_notes: ""
comments: "HybridTier=6"
---
```

### File naming
- Daily notes: `trading_journal/{YYYY-MM-DD}.md` (vault root)
- Trade notes: `trading_journal/TradeManagement/{YYYY-MM-DD}_{SYMBOL}_{SIGNAL_SOURCE}.md`
  - Example: `TradeManagement/2026-05-09_MOD_P_115.md`
- Templates: `trading_journal/Templates/`
- Bases: `trading_journal/Bases/`

### Three starter `.base` views (Phase 5)

1. **`daily_trades.base`** — table of all TradeManagement in `TradeManagement/`, sorted by date desc; columns: date, symbol, signal_source, step1_verdict, tiers, setup_score, traded, outcome
2. **`open_positions.base`** — filter `traded == "Y" AND outcome == null`; columns: date, symbol, signal_source, entry_price, tp_level, sl_level, risk_pct, account_balance, days_held formula
3. **`performance_by_strategy.base`** — group by signal_source; columns: signal_source, count, count(outcome="TP Hit"), win_rate

### Phase 5 export script (planned)

Save path: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts\trade_log_export\`

| File | ~Lines | Purpose |
|------|--------|---------|
| `__init__.py` | 5 | package marker |
| `config.py` | 40 | Excel path, output path, schema map |
| `excel_reader.py` | 80 | read `.xlsx` via openpyxl, normalize rows |
| `frontmatter_writer.py` | 80 | dict → YAML frontmatter, write `.md` |
| `main.py` | 60 | orchestration entry point |
| `logger_setup.py` | 40 | logging |

Run mode: on-demand (manually triggered after Excel updates), not scheduled.
Environment: p140 conda.

---

## Section 6 — Obsidian Template Reference

### 6.1 Template Ownership
**P_800 owns ALL Obsidian templates.** P_010 generates daily note content (market posture data) but does not own or manage templates.

### 6.2 Active Templates

| File | Status | Owner | Purpose |
|------|--------|-------|---------|
| `P_800_Daily_Flow.md` | ✅ Active master (v3.0) | P_800 | Full daily note template — rebuilt clean 2026-05-11 |

Prior templates (`P_010_TemplateSchema_v1.md`, `Daily-Flow.md`, `Web Clipper Whats App.md`) all retired with the vault rebuild. The vault is fresh — no template archive carried over.

### 6.3 Master Template Location

**Live (active) path:**
`C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\Templates\P_800_Daily_Flow.md`

### 6.4 P_800_Daily_Flow.md — What It Contains (v3.0)

**Frontmatter schema** (drives Bases queries on daily notes):

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
1. H1 date header — `dddd, MMMM D, YYYY` via Templater
2. Morning Starter — Verse of the Day, Daily Quote, Joke of the Day (all auto-fetched)
3. Senior Exercise (wrist-friendly checklist)
4. Schedule Check — placeholder; Claude MCP injects Google Calendar events on request
5. Market Analysis
   - Pre-Market Analysis (TOS + VantagePoint notes)
   - Market Posture (paste-target for P_010 JSON block)
6. AI Trends & Research
7. Daily Rollover / Review (checkbox list)

Footer: `*Template owner: P_800 -- v3.0*`

**Auto-fetch API calls:**
- Bible verse: `tp.obsidian.requestUrl({url: "https://labs.bible.org/api/?passage=votd&type=json&formatting=plain"})`
- Daily quote: `tp.web.daily_quote()` (Templater built-in)
- Joke: `tp.obsidian.requestUrl({url: "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single"})`

**Removed from v2.1 template:**
- WhatsApp section entirely (scam contacts purged)
- Trade Execution Log table (redundant — TradeManagement live in `TradeManagement/` base)
- Separate Market Posture section (now a subsection of Market Analysis)
- Manual Notebook Activities section (rarely used)

**Cursor tab stops:** 5 (one per editable section after the auto-fetched morning starter)

### 6.5 Templater Settings (locked configuration)

| Setting | Value |
|---------|-------|
| Template folder location | `Templates` |
| Trigger Templater on new file creation | ON |
| Folder template — `/` (vault root) | `Templates/P_800_Daily_Flow.md` |

### 6.6 Plugins Required
1. Templater — dynamic template population
2. QuickAdd — hotkey macros
3. Tasks — checkbox tracking
4. Local REST API — MCP bridge endpoint (port 27124)
5. Google Calendar — calendar sync
6. Bases — core feature (no install)
7. Web Clipper — browser extension

---

## Section 7 — Folder Structure

### 7.1 Active Vault

```
C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\
├── .obsidian\                              <- Obsidian config (auto-created)
├── Templates\
│   └── P_800_Daily_Flow.md                 <- Master template (P_800 owned)
├── Bases\                                  <- .base view files (Phase 5)
├── TradeManagement\                                 <- One .md per trade (Phase 5)
└── YYYY-MM-DD.md                           <- Daily notes (one per day)
```

### 7.2 Hub Project Folder

```
C:\Users\Trader\AI-Agent-Learning-Hub\
├── trading_journal\                        <- Obsidian vault (above)
└── projects\
    └── P_800_Automation_Note_Taking\
        ├── docs\
        │   ├── P_800_SYSTEM_DOCUMENTATION.md   <- This file (v3.0)
        │   ├── BASES_VAULT_REBUILD_PLAN.md     <- Vault rebuild plan
        │   └── backups\                        <- Archived old docs
        ├── claude_artifacts\
        ├── espanso\
        └── scripts\                            <- Python automation (Phase 5+)
```

### 7.3 File Save Path Quick Reference

| File Type | Save Path |
|-----------|-----------|
| Obsidian vault root | `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` |
| Obsidian templates (live) | `...\trading_journal\Templates\` |
| Daily notes | `...\trading_journal\YYYY-MM-DD.md` |
| Trade notes | `...\trading_journal\TradeManagement\YYYY-MM-DD_SYMBOL_SOURCE.md` |
| Bases views | `...\trading_journal\Bases\*.base` |
| P_800 docs | `C:\...\P_800_Automation_Note_Taking\docs\` |
| Claude artifacts | `C:\...\P_800_Automation_Note_Taking\claude_artifacts\` |
| Python scripts | `C:\...\P_800_Automation_Note_Taking\scripts\` |

---

## Section 8 — Workflows

### Workflow 8.1 — Morning Startup (Minimal Typing)
1. Open Obsidian (vault auto-loads to `trading_journal`)
2. Ctrl+N at vault root → Templater fires P_800_Daily_Flow.md
3. Verse, quote, joke auto-fetched. Frontmatter populates with date/day.
4. Rename the new file to today's date in `YYYY-MM-DD.md` format
5. Tell Claude: "Inject today's Google Calendar events into my daily note"
6. Open P_010 artifact → generate Market Posture JSON → paste into Market Analysis → Market Posture subsection
7. TOS + VantagePoint → notes into Pre-Market Analysis subsection
8. Dictate trade plans via Win+H if helpful

### Workflow 8.2 — New Claude Artifact Build
1. Start session in P_800
2. Describe the tool needed
3. Claude builds artifact → test in session → save to `claude_artifacts\` folder

### Workflow 8.3 — Claude Direct Vault Write (MCP Bridge)
1. Start Claude Desktop session (MCP tools load automatically when bridge is active)
2. Tell Claude what to write and where: "Append today's TOS notes to the Pre-Market Analysis section of today's daily note"
3. Claude reads the current note, appends or injects the content, confirms success
4. Verify in Obsidian — content appears immediately, no copy-paste needed

### Workflow 8.4 — Template Update Process (P_800 owns all templates)
1. Open session in P_800 project
2. Read current template via Windows-MCP PowerShell or `filesystem:read_file`
3. Edit via `filesystem:write_file` (avoids apostrophe escaping) or PowerShell `[System.IO.File]::WriteAllText` with a single-quoted here-string (doubled apostrophes)
4. Verify by Ctrl+N test in Obsidian
5. Bump template_version in frontmatter

### Workflow 8.5 — Trade Log Export (Phase 5, planned)
1. Update Excel tracker after each trade as usual
2. Run `python -m trade_log_export.main` from the p140 conda env (or batch launcher)
3. Script reads all rows, writes/updates one `.md` per trade in `TradeManagement/`
4. Bases views refresh automatically in Obsidian

---

## Section 9 — Error Corrections Log

| # | Date | Error | Correct Behavior | Severity |
|---|------|-------|-----------------|----------|
| 1 | 2026-03-07 | Created unnecessary sub-projects | P_800 is one project — use sections, not sub-projects | Medium |
| 2 | 2026-03-08 | Built Market Posture JSON Generator in P_800 — generating posture data is P_010's job | P_800 only displays P_010 output — never generates or writes market posture data | High |
| 3 | 2026-03-12 | Misspelled a contact name | Moot — contact later identified as scam; all references purged | Low |
| 4 | 2026-03-12 | Incorrect chat channel names and membership | Channels later all identified as coordinated scams; all references purged | Medium |
| 5 | 2026-03-12 | Incorrect Telegram contacts mapping | Channels later all identified as coordinated scams; all references purged | Medium |
| 6 | 2026-03-16 | Vault root recorded as outer "Trading Journal" folder | Correct then-current vault root was the inner `TradingJournal\` folder | Medium |
| 7 | 2026-03-16 | Vault path recorded as `D:\OneDrive\...` throughout v1.9/v2.0 | Active vault then was actually under `C:\Users\Trader\Documents\...` — but OneDrive Documents redirect made both half-true. See Error #11. | High |
| 8 | 2026-03-19 | Misspelling persisted in templates | Moot — scam-identified, all references purged | Low |
| 9 | 2026-03-19 | P_010 owned Obsidian templates — scope creep | P_800 owns ALL Obsidian templates. P_010 generates content only. | Medium |
| 10 | 2026-04-XX | Trading channels identified as coordinated scams (Investment Pioneer Club, Club 84, Freedom Income Options) | All contact and channel references purged from documentation, templates, and scripts. Scam-recovery follow-up contacts also identified as scams. Tony advised to contact financial institutions and authorities. | Critical |
| 11 | 2026-05-11 | OneDrive Documents redirect masked the true byte location of the vault — produced C: vs D: confusion across v1.9–v2.1 | Windows redirects `C:\Users\<user>\Documents` to `D:\OneDrive\Documents` when OneDrive Documents sync is enabled. Both "C:" and "D:" claims were half-true. Solution: vault relocated to `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` — outside OneDrive's reach. | High |
| 12 | 2026-05-11 | Used `tp.web.request()` in Templater — function does not exist | Use `tp.obsidian.requestUrl({url: "..."})` for external HTTP calls. Returns an object with a `.json` property. | Medium |

---

## Section 10 — Session Log

| Date | Session Topic | Key Decisions |
|------|--------------|---------------|
| 2026-03-07 | Project inception | P_800 created, single project structure, no sub-projects |
| 2026-03-08 | Phase 3 — Market Posture Display | P_010 owns posture generation; P_800 reads only |
| 2026-03-08 | Phase 2 — Web Clipper + Defuddle | 5 templates built; NPM not needed |
| 2026-03-12 | Enhancement backlog + contact corrections | Telegram API logged; channel names corrected (later moot — all scams) |
| 2026-03-16 | Phase 3.5 — MCP Bridge | Local REST API installed; vault read/write confirmed live |
| 2026-03-16 | Doc update v2.0 | Vault path correction |
| 2026-03-19 | Phase 3.6 — Template ownership transfer + consolidation | All templates moved to P_800 ownership |
| 2026-04-XX | Scam identification + cleanup | All scam-channel references purged; outreach drafted to the real Marc Andreessen |
| 2026-05-09 | Vault architecture pivot | Decision: rebuild vault outside OneDrive at `trading_journal\` under the Hub; integrate Bases; abandon old D: and `C:\Users\Trader\Documents\` copies |
| 2026-05-11 | Phase 4 — Vault rebuild (Steps 1–10) | New vault built at `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\`; Templates/Bases/TradeManagement subfolders created; 5 community plugins installed; Templater bound `/` → `P_800_Daily_Flow.md`; Local REST API key rotated; MCP config updated; clean v3.0 template tested end-to-end (Verse/Quote/Joke all populating); system doc rewritten to v3.0 |

---

## Section 11 — Parameter Registry

| Parameter | Value |
|-----------|-------|
| Project ID | P_800 |
| Project structure | Single project — no sub-projects |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project folder | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\` |
| Obsidian vault root | `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` |
| Daily note format | `YYYY-MM-DD.md` |
| Templates folder | `trading_journal\Templates\` |
| Bases folder | `trading_journal\Bases\` |
| TradeManagement folder | `trading_journal\TradeManagement\` |
| Master template | `Templates\P_800_Daily_Flow.md` (v3.0) |
| Template owner | P_800 (all templates) |
| Trade source-of-truth | Excel tracker (`Tracker_Log_Schema_v9_4_0_1.md`, 27 LOCKED columns) |
| Trade sync direction | Excel → Obsidian TradeManagement/ (one-way) |
| Primary note-taking tool | Obsidian (1.12.7+) |
| Primary AI tool | Claude (Desktop required for MCP) |
| Trading platform | ThinkOrSwim (TOS) |
| Tony skill level — Python | Novice |
| Tony skill level — VS Code | Novice |
| Wrist constraint | Yes — avoid wrist-intensive exercises |
| Conda environment | p140 (`C:\Users\Trader\.conda\envs\p140\python.exe`) |
| Primary local LLM | LM Studio at `http://127.0.0.1:1234/v1` |
| Fallback LLM | Claude API |
| Obsidian Local REST API port | 27124 (HTTPS) |
| MCP server command | `C:\Users\Trader\.conda\envs\p140\python.exe -c "from mcp_obsidian import main; main()"` |
| Claude Desktop config | `%APPDATA%\Claude\claude_desktop_config.json` |
| MCP Bridge status | ✅ LIVE — reconfigured 2026-05-11 |
| File size discipline | 300 lines max per file, 50 lines max per function |

---

*End of P_800 SYSTEM DOCUMENTATION v3.0 — 2026-05-11*
