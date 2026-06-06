# P_800 SYSTEM_DOCUMENTATION
## Automation Note-Taking & Knowledge Building

---

**Project ID:** P_800  
**Version:** 2.0  
**Created:** 2026-03-07  
**Last Updated:** 2026-03-16  
**Owner:** Tony  
**Status:** Active

---

## Section 1 — Project Overview

### 1.1 Purpose
P_800 exists to eliminate manual typing and repetitive setup in Tony's daily workflow. It automates note-taking, knowledge capture, AI prompting, and daily flow initialization across Obsidian, Claude, and connected tools.

### 1.2 Goals
- Minimize keystrokes in daily trading and research workflow
- Build a consistent, searchable knowledge base in Obsidian
- Integrate Claude, Grok, Perplexity, and Gemini efficiently
- Connect automation to Tony's existing trading projects (P_010, P_020, etc.)

### 1.3 Scope
- Obsidian daily note templates and plugins
- Claude Artifacts for daily tools (JSON generator, chat formatter, etc.)
- Text expansion tools (Espanso, AutoHotkey, Windows PowerToys)
- Voice input workflows
- Python automation scripts (future)
- Claude ↔ Obsidian MCP bridge (direct read/write to vault)

### 1.4 Out of Scope
- ThinkScript strategy development (belongs in trading project series)
- Brokerage API connections (belongs in P_020 series)
- Market Posture JSON generation (belongs to P_010 — P_800 reads only, never writes)

---

## Section 1.5 — Definitions & Acronyms

| Term | Definition |
|------|-----------|
| P_800 | This project — Automation Note-Taking & Knowledge Building |
| Daily Flow | Tony's morning-to-evening routine: quotes → exercise → calendar → WhatsApp chats → market posture → TOS analysis → AI trends |
| Market Posture JSON | Structured JSON block summarizing daily market bias (bullish/neutral/bearish), regime, key setups, risk level |
| P_010 | Tony's existing Claude prompt system for market posture analysis |
| P_020 | Tony's performance analysis / trading data system |
| TOS | ThinkOrSwim — primary trading platform |
| VantagePoint | AI-based market forecasting tool used alongside TOS |
| Impens | Daniel Impens — Investment Pioneer Club (WhatsApp) |
| Alice | Alice (no last name) — Investment Pioneer Club (WhatsApp) |
| Andreessen | Marc Andreessen — AI Quantitative Trading 84 / Club 84 (WhatsApp + Telegram) |
| Gaud | Casey Gaud — AI Quantitative Trading 84 / Club 84 (WhatsApp + Telegram) |
| Stubbs | Casey Stubbs — Freedom Income Options (Telegram, Forex focus) |
| Pioneer Club | Investment Pioneer Club — WhatsApp channel: Daniel Impens, Alice |
| Club 84 | AI Quantitative Trading 84 / Club 84 — WhatsApp + Telegram: Marc Andreessen, Casey Gaud |
| Freedom Income Options | Casey Stubbs' Telegram channel — Forex / Income Options focus |
| Templater | Obsidian community plugin for dynamic template population |
| QuickAdd | Obsidian plugin for hotkey-triggered macros |
| Espanso | Free cross-platform text expander (system-wide) |
| AHK | AutoHotkey — Windows automation scripting tool |
| Market Posture Display | P_800 read-only artifact — displays P_010 JSON, outputs Obsidian note block |
| MCP | Model Context Protocol — open standard allowing Claude to connect to external tools and data sources |
| Local REST API | Obsidian community plugin that creates a local server Claude can connect to via MCP |
| MCP Bridge | The connection between Claude Desktop and Obsidian via Local REST API + claude_desktop_config.json |

---

## Section 2 — Operating Rules

### 2.1 — AI Behavior Rules & Constraints

**MUST:**
- Always acknowledge current date and time at the start of each session
- Prioritize low-typing / minimal-effort solutions for Tony
- Suggest Claude Artifacts before recommending external software installs
- Keep instructions step-by-step and beginner-friendly
- Ask clarifying questions using the ask_user_input widget when choices are needed
- Reference existing projects (P_010, P_020) when automation connects to them
- Use the Obsidian MCP tools to read/write vault content when available in session

**MUST NOT:**
- Recommend solutions requiring heavy coding without providing the full code
- Assume Tony knows advanced Python or VS Code features
- Suggest paid tools without first exhausting free options
- Skip the SYSTEM_DOCUMENTATION load at session start
- Build artifacts that generate or modify the Market Posture JSON — that belongs to P_010
- Allow P_800 artifacts to write to the P_010 posture file under any circumstances

---

## Section 3 — Daily Flow Reference

Tony's daily routine that automation supports:

| Time | Activity | Automation Target |
|------|----------|------------------|
| Morning | Open Obsidian daily note | Templater auto-creation |
| Morning | Inspirational + humor quote | Auto-fetch or rotation |
| Morning | Senior exercise routine | Pre-filled template block |
| Morning | Google Calendar review | Claude MCP → inject via Google Calendar MCP (replaces Python script approach) |
| Morning | WhatsApp — Investment Pioneer Club (Impens, Alice) | Web Clipper → formatter |
| Morning | WhatsApp — Club 84 (Andreessen, Gaud) | Web Clipper → formatter |
| Morning | Telegram — Club 84 (Andreessen, Gaud) + Freedom Income Options (Stubbs) | Enhancement Backlog — Telegram API (see Section 5.1, Enhancement #1) |
| Morning | Market Posture display | P_010 generates JSON → P_800 display artifact reads it → paste to Obsidian |
| Midday | TOS + VantagePoint analysis | Template section + screenshots |
| Midday | Trade execution notes | Claude MCP → inject directly to daily note Trade Log section |
| Evening | AI trends review | Template section |
| Evening | Daily rollover / review | Tasks plugin |

---

## Section 4 — Tool Inventory

| Tool | Category | Status | Notes |
|------|----------|--------|-------|
| Obsidian | Note-taking | Installed | Primary knowledge base |
| Claude (claude.ai) | AI Assistant | Active | Primary AI tool |
| ThinkOrSwim (TOS) | Trading Platform | Active | Primary brokerage platform |
| VantagePoint | Market Forecasting | Active | AI-based forecasting |
| Grok | AI Assistant | Active | Secondary AI |
| Perplexity | AI Search | Active | Research + quotes |
| Gemini / NotebookLM | AI Assistant | Active | Club 84 / Gaud notes |
| Copilot | AI (MS Apps) | Active | Microsoft integration |
| Espanso | Text Expander | Planned | Free, cross-platform |
| AutoHotkey | Windows Automation | Planned | Free |
| Templater | Obsidian Plugin | ✅ Installed | Dynamic templates |
| QuickAdd | Obsidian Plugin | ✅ Installed | Hotkey macros |
| Google Calendar Plugin | Obsidian Plugin | ✅ Installed | Calendar sync |
| Tasks Plugin | Obsidian Plugin | ✅ Installed | Checkbox tracking |
| Obsidian Web Clipper | Browser Extension | ✅ Installed | WhatsApp/X capture (target v0.10.9+) |
| Obsidian Local REST API | Obsidian Plugin | ✅ Installed & Active | MCP bridge endpoint — port 27124 |
| Claude Desktop App | AI Desktop App | ✅ Installed & Active | Required for MCP bridge |
| Claude ↔ Obsidian MCP Bridge | Integration | ✅ LIVE (2026-03-16) | Claude reads/writes vault directly — see Section 5.2 |
| Google Calendar API | Python Integration | Enhancement Backlog | Now lower priority — Claude MCP + Google Calendar MCP may replace this |
| Telegram API | Chat Extraction | Enhancement Backlog | Club 84 + Freedom Income Options — see Section 5.1, Enhancement #1 |

---

## Section 5 — Build Roadmap

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 1 | Obsidian daily note template (final version) | ✅ Complete |
| 2 | Obsidian Web Clipper + Defuddle setup guide (Chrome) | ✅ Complete |
| 3 | Market Posture Display artifact (reads P_010 JSON — read-only) | ✅ Complete |
| 3.5 | Claude ↔ Obsidian MCP Bridge (direct vault read/write) | ✅ Complete — 2026-03-16 |
| 4 | WhatsApp Chat Formatter artifact | ⏸ Paused — real-world testing of Phases 1–3 first |
| 5 | Daily Flow Launcher artifact | Planned |
| 6 | Espanso text expansion setup | Planned |
| 7 | Voice input workflow guide | Planned |

---

## Section 5.1 — Enhancement Backlog

Enhancements requested but not yet scheduled for a build phase. Logged and preserved for future planning.

| # | Date Logged | Enhancement | Detail | Priority |
|---|-------------|-------------|--------|----------|
| 1 | 2026-03-12 | Telegram API — Chat Extraction | Auto-extract chat messages from Telegram trading channels. Reference: https://core.telegram.org/api | High |
| 2 | 2026-03-12 | Google Calendar API — Python Script | Auto-fetch today's Google Calendar events and inject into Obsidian daily note. Note: MCP bridge now live — may replace Python script approach entirely via Google Calendar MCP. Re-evaluate approach before building. | Medium (downgraded — MCP bridge changes implementation path) |

---

### Enhancement #1 Notes — Telegram API Chat Extraction

**Telegram Channels & Contacts:**

| Contact | Channel | Trading Focus |
|---------|---------|---------------|
| Marc Andreessen | AI Quantitative Trading 84 / Club 84 | Equities / AI Trading |
| Casey Gaud | AI Quantitative Trading 84 / Club 84 | Equities / AI Trading |
| Casey Stubbs | Freedom Income Options | Forex / Income Options |

**Cross-platform contact map (full picture):**

| Contact | WhatsApp | Telegram | Channel |
|---------|----------|----------|---------|
| Daniel Impens | ✅ | ❌ | Investment Pioneer Club |
| Alice (no last name) | ✅ | ❌ | Investment Pioneer Club |
| Marc Andreessen | ✅ | ✅ | Club 84 |
| Casey Gaud | ✅ | ✅ | Club 84 |
| Casey Stubbs | ❌ | ✅ | Freedom Income Options |

**Implementation notes:**
- **API reference:** https://core.telegram.org/api
- **Goal:** Replace manual copy-paste of Telegram intelligence into Obsidian daily notes
- **Implementation path TBD:** Python script (scripts\ folder) most likely — to be scoped when phase begins
- **Scope boundary:** P_800 reads and formats chat content only — never generates or modifies market posture data

---

### Enhancement #2 Notes — Google Calendar API

**Goal:** Replace the manual step of opening Google Calendar and copy-pasting events into the Obsidian daily note.

**Updated approach (as of 2026-03-16):**
Now that the Claude ↔ Obsidian MCP bridge is live, the Google Calendar MCP (already connected to Claude) can inject events directly into the daily note via Claude — without needing a separate Python script. Re-evaluate whether Python script is still needed before building.

**Option A — Claude MCP approach (preferred, no coding):**
- Claude fetches today's events via Google Calendar MCP
- Claude injects them directly into the `## 📅 Calendar` section via Obsidian MCP
- Zero Python, zero OAuth setup, zero maintenance

**Option B — Python script (original plan, fallback):**
- Python script authenticates with Google Calendar API (OAuth)
- Fetches events, formats as markdown bullets, writes to daily note
- Libraries: `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
- Save path: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\scripts\`

**Clarifying questions outstanding (as of 2026-03-12 — pending re-evaluation given MCP bridge):**
1. OAuth flow or service account for Google Calendar authentication?
2. Exact Calendar section header in the daily note template
3. Exact daily note file path pattern
4. Preferred event format (time range, title, location)
5. Pull from primary calendar only, or multiple calendars?

---

## Section 5.2 — MCP Bridge Configuration

### Claude ↔ Obsidian MCP Bridge (LIVE — 2026-03-16)

**What it does:** Allows Claude to read and write directly to Tony's Obsidian vault without copy-paste. Claude can inject content into any section of the daily note on command.

**Components:**

| Component | Details |
|-----------|---------|
| Obsidian Plugin | Local REST API — installed and enabled |
| Plugin Port | 27124 (default) |
| Plugin Host | 127.0.0.1 (localhost) |
| API Key | Stored in claude_desktop_config.json |
| Config File | `%APPDATA%\Claude\claude_desktop_config.json` |
| MCP Package | `mcp-obsidian` (run via uvx) |

**claude_desktop_config.json — Obsidian entry:**
```json
"obsidian": {
  "command": "C:\\Users\\Trader\\.local\\bin\\uvx.exe",
  "args": [
    "mcp-obsidian"
  ],
  "env": {
    "OBSIDIAN_API_KEY": "<stored in config file>",
    "OBSIDIAN_HOST": "127.0.0.1",
    "OBSIDIAN_PORT": "27124"
  }
}
```

**Capabilities unlocked:**
- Read any note in the vault
- Write / append content to daily notes on command
- List vault files and directories
- Inject formatted content directly into note sections
- No copy-paste required for any Obsidian write operation

**Scope boundary:** MCP write access is for daily note content only. Claude must never write to P_010 posture files via MCP.

**Vault confirmed:**
- Vault path: `D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\`
- Vault root seen by MCP: `TradingJournal/`
- Daily note format confirmed: `TradingJournal/MM-DD-YYYY.md`
- Templates folder: `TradingJournal/Templates/`
- P_010 template confirmed at: `TradingJournal/Templates/P_010_TemplateSchema_v1.md`

---

## Section 6 — Obsidian Template Reference

### 6.1 Daily Note Template Location
`Templates/Daily-Flow.md` inside Obsidian vault

**Vault path:**
`D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\Templates\Daily-Flow.md`

**Hub save path (backup copy):**
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\templates\Daily-Flow.md`

### 6.2 Daily Note Sections
1. Inspiration & Warmup (Quote, Humor, Exercise)
2. Schedule Check (Google Calendar)
3. WhatsApp Trading Channels (Investment Pioneer Club + Club 84)
4. Market Posture (P_010 Prompts + JSON)
5. TOS + VantagePoint Analysis
6. Manual Notebook Activities
7. AI Trends & Analysis

### 6.3 Plugins Installed (Priority Order)
1. Templater ✅ — dynamic date/time/cursor population
2. QuickAdd ✅ — hotkey macros for section insertion
3. Google Calendar ✅ — auto-inject schedule
4. Tasks ✅ — checkbox tracking
5. Obsidian Web Clipper ✅ — WhatsApp/X capture (browser extension, target v0.10.9+)
6. Local REST API ✅ — MCP bridge endpoint (port 27124)

---

## Section 7 — Folder Structure

### 7.1 Hub Project Folder (C: drive — unchanged)

```
C:\Users\Trader\AI-Agent-Learning-Hub\
└── projects\
    └── P_800_Automation_Note_Taking\
        ├── templates\          <- Backup copies of Obsidian templates
        ├── claude_artifacts\   <- JSON Generator, Chat Formatter, Daily Flow Launcher
        ├── espanso\            <- Espanso text expansion configs (Phase 6)
        ├── scripts\            <- Python automation scripts (future Telegram API)
        └── docs\               <- Setup guides, plugin instructions, reference docs
```

### 7.2 Obsidian Vault Folder (D: drive)

```
D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\
├── Templates\                  <- Daily-Flow.md, P_010_TemplateSchema_v1.md
├── MM-DD-YYYY.md               <- Daily notes (e.g. 03-16-2026.md)
└── ...
```

### 7.3 File Save Path Quick Reference

| File Type | Save Path |
|-----------|-----------|
| Obsidian vault root | `D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\` |
| Obsidian templates (live) | `D:\OneDrive\...\Trading Journal\Templates\` |
| Obsidian templates (backup) | `C:\...\P_800_Automation_Note_Taking\templates\` |
| Daily notes | `D:\OneDrive\...\Trading Journal\MM-DD-YYYY.md` |
| Claude artifacts (exported) | `C:\...\P_800_Automation_Note_Taking\claude_artifacts\` |
| Espanso configs | `C:\...\P_800_Automation_Note_Taking\espanso\` |
| Python scripts (future) | `C:\...\P_800_Automation_Note_Taking\scripts\` |
| Guides & docs | `C:\...\P_800_Automation_Note_Taking\docs\` |

---

## Section 8 — Workflows

### Workflow 8.1 — Morning Startup (Minimal Typing)
1. Open Obsidian → Ctrl+P → "Open today's daily note" (auto-creates from template)
2. Quote/Exercise block is pre-filled — no typing needed
3. Tell Claude: "Inject today's Google Calendar events into my daily note" (via MCP bridge)
4. Open WhatsApp Web → Web Clipper → paste Investment Pioneer Club + Club 84 sections
5. Open P_010 artifact → generate Market Posture JSON → copy → paste into P_800 Display artifact → one-click copy Obsidian block → paste to daily note
6. Open TOS → run pre-market analysis → dictate notes via Win+H

### Workflow 8.2 — New Claude Artifact Build
1. Start session in P_800
2. Describe the tool needed
3. Claude builds artifact → test in session → save to claude_artifacts\ folder

### Workflow 8.3 — Claude Direct Vault Write (MCP Bridge)
1. Start Claude Desktop session (MCP tools load automatically when bridge is active)
2. Tell Claude what to write and where: e.g. "Write my trade notes for SNT into the Trade Log section of today's daily note"
3. Claude reads the current note, appends or injects the content, confirms success
4. Check Obsidian — content appears immediately, no copy-paste needed

---

## Section 9 — Error Corrections Log

| # | Date | Error | Correct Behavior | Severity |
|---|------|-------|-----------------|----------|
| 1 | 2026-03-07 | Created unnecessary sub-projects | P_800 is one project — use sections, not sub-projects | Medium |
| 2 | 2026-03-08 | Built Market Posture JSON Generator in P_800 — generating posture data is P_010's job | P_800 only displays P_010 output — never generates or writes market posture data | High |
| 3 | 2026-03-12 | Misspelled Marc Andreessen's last name as "Anderssen" | Correct spelling: Marc Andreessen | Low |
| 4 | 2026-03-12 | Incorrect WhatsApp channel names and membership | Investment Pioneer Club: Impens + Alice. Club 84 / AI Quantitative Trading 84: Andreessen + Gaud | Medium |
| 5 | 2026-03-12 | Incorrect Telegram contacts — listed Marc, Daniel, Alice | Telegram contacts: Casey Gaud + Marc Andreessen (Club 84) and Casey Stubbs (Freedom Income Options/Forex) | Medium |
| 6 | 2026-03-16 | Vault path recorded as C:\Users\Trader\Documents\... throughout docs | Correct vault path: D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\ — Hub stays on C:, vault is on D: | Medium |

---

## Section 10 — Session Log

| Date | Session Topic | Key Decisions |
|------|--------------|---------------|
| 2026-03-07 | Project inception | P_800 created, single project structure confirmed, no sub-projects |
| 2026-03-08 | Phase 3 — Market Posture Display artifact | P_010 owns posture generation; P_800 reads P_010 JSON, displays it, outputs Obsidian block |
| 2026-03-08 | Phase 2 — Web Clipper + Defuddle setup guide | Chrome update 0.2.9 → latest; 5 Web Clipper templates built (WhatsApp, IBD, X, News, Catch-all); NPM not needed |
| 2026-03-12 | Enhancement Backlog + Contact Corrections | Telegram API logged (Enhancement #1); all channel names, spellings, and membership corrected |
| 2026-03-12 | Enhancement #2 — Google Calendar API Python Script | Scoped Python script to auto-fetch today's Google Calendar events and inject into Obsidian daily note Calendar section; replaces manual copy-paste; 5 clarifying questions outstanding before build begins; save path: scripts\ folder |
| 2026-03-16 | Phase 3.5 — Claude ↔ Obsidian MCP Bridge | Local REST API plugin installed in Obsidian; MCP entry added to claude_desktop_config.json; vault read/write confirmed live; Enhancement #2 Python script approach now superseded by MCP approach; Workflow 8.3 added |
| 2026-03-16 | Doc update v2.0 — vault path correction | Corrected vault path from C: to D: throughout all sections; Hub stays on C:; vault confirmed on D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\; Templater + Core Templates both pointed to Templates folder; P_010_TemplateSchema_v1.md confirmed present in Templates\ |

---

## Section 11 — Parameter Registry

| Parameter | Value |
|-----------|-------|
| Project ID | P_800 |
| Project structure | Single project — no sub-projects |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project folder | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\` |
| Obsidian vault root | `D:\OneDrive\Documents\AJZStrategies_TradingJournal\Trading Journal\` |
| Vault root seen by MCP | `TradingJournal/` |
| Daily note format | `TradingJournal/MM-DD-YYYY.md` |
| Templates folder (vault) | `TradingJournal/Templates/` |
| Primary note-taking tool | Obsidian |
| Primary AI tool | Claude |
| Trading platform | ThinkOrSwim (TOS) |
| Tony skill level - Python | Novice |
| Tony skill level - VS Code | Novice |
| Wrist constraint | Yes — avoid wrist-intensive exercises |
| Obsidian plugins installed | Templater, QuickAdd, Google Calendar, Tasks, Web Clipper, Local REST API |
| Obsidian Local REST API port | 27124 |
| MCP Bridge status | ✅ LIVE — 2026-03-16 |
| WhatsApp Channel 1 | Investment Pioneer Club — Daniel Impens, Alice (no last name) |
| WhatsApp Channel 2 | AI Quantitative Trading 84 / Club 84 — Marc Andreessen, Casey Gaud |
| Telegram Channel 1 | AI Quantitative Trading 84 / Club 84 — Marc Andreessen, Casey Gaud |
| Telegram Channel 2 | Freedom Income Options — Casey Stubbs (Forex) |
