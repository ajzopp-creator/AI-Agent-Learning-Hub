# P_805 SYSTEM_DOCUMENTATION
## Email Trade Extractor

---

**Project ID:** P_805
**Project Name:** Email Trade Extractor
**Version:** 1.1
**Created:** 2026-04-20
**Updated:** 2026-04-20 (Section 4 aligned to python-project-architecture standard; Section 5 pointed to authoritative CSV)
**Owner:** Tony
**Status:** Active — Phase 1 (Reader)
**Parent Relationship:** Peer of P_800 (no sub-project relationship; peer within multi-project hub)
**Root Path:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\`

---

## Table of Contents

1. Project Overview
2. Architecture & Tech Stack
3. AI Behavior Rules & Constraints
4. Folder Structure
5. Approved Senders Registry
6. Error Corrections Log
7. Build Roadmap
8. Enhancement Backlog
11. Parameter Registry

---

## Section 1 — Project Overview

### 1.1 Purpose
Extract ticker recommendations and trade signals from email newsletters stored in Thunderbird, deduplicate across sources, and produce a daily ranked output that feeds Tony's morning trading workflow. Once a message is successfully identified and extracted, move it to an `ExtractedNewsletterFolder` — a peer folder of Inbox — in the current hosted email client. The system never sends, replies to, forwards, or deletes mail.

### 1.2 Goals
- Scan approved-sender emails over a configurable lookback window (default 30 days)
- Extract tickers, direction (long/short/watch), and entry/stop/target where provided
- Dedupe signals and rank by source agreement
- Write daily output to `data\daily\` as markdown + JSON
- Optional: inject summary into Obsidian daily note via P_800's MCP bridge

### 1.3 In-Scope
- Reading Thunderbird client (current) — but can be any Windows email client when specified
- Parsing mbox files using Python's `mailbox` module
- Whitelist-based sender filtering (source: `data\sender_sheet.csv`)
- Regex + LLM hybrid ticker extraction
- Moving extracted messages to `ExtractedNewsletterFolder` (peer of Inbox) in the active email client

### 1.4 Out-of-Scope
- Sending, replying to, forwarding, or deleting any email
- Credential-based IMAP access (Phase 1 uses Thunderbird's already-downloaded cache only)
- Executing trades (P_805 produces a research list only)

### 1.5 Definitions & Acronyms
- **Approved Sender** — email address on the whitelist in `data\sender_sheet.csv` with `enabled=true`
- **Ticker Signal** — tuple of (ticker, direction, source, timestamp, raw_context)
- **Consensus Signal** — ticker appearing in ≥2 approved sources within the lookback window
- **mbox** — Thunderbird's mail file format (one flat file per folder, no extension)
- **Profile Path** — Thunderbird user profile directory, typically ends in `.default-release` or similar
- **Lookback Window** — number of days back from today to scan (constant: `SCAN_DAYS` in `config.py`)
- **LM Studio** — local LLM runtime, primary LLM per Tony's priority
- **P_800** — peer project (Obsidian automation); P_805 may call its MCP bridge for output delivery

---

## Section 2 — Architecture & Tech Stack

### 2.1 Runtime
- **Python:** `C:\Users\Trader\.conda\envs\p140\python.exe` (shared p140 conda env)
- **OS:** Windows 11
- **IDE:** VS Code

### 2.2 Languages
- **Python** — primary, all core logic
- **PowerShell** — deprecated for mbox parsing after April 17, 2026 failure (see Section 6, entry 001); retained only for file-system probes

### 2.3 Libraries
- `mailbox` (stdlib) — mbox parsing
- `email` (stdlib) — header and body extraction
- `pydantic` — schemas for persistent file I/O (Phase 4+)
- `pandas` — dedup, ranking, daily frame output
- `requests` — LLM API calls (LM Studio or Claude)

### 2.4 Storage
- Filesystem only. No database in Phase 1.
- Daily output: `data\daily\YYYY-MM-DD_signals.md` and `.json`
- Monthly rollups: `data\monthly\`
- Raw cache: `data\raw\` (optional, for replay during debug)

### 2.5 LLM Priority
Per Tony's global preference: **LM Studio first** (local, free, private), **Claude API second** (fallback when LM Studio unavailable or when reasoning quality matters — e.g., ambiguous extraction).

### 2.6 Code Architecture Standard
This project follows the Hub-wide **python-project-architecture** standard:
- Code lives under `python\`, split into `domain\` (logic, no I/O), `infrastructure\` (all I/O), `application\` (orchestration).
- All constants and paths live in `python\config.py`. Never hardcoded elsewhere.
- Any persistent file read or write requires a Pydantic schema in `python\schemas.py`.
- Hard limits: 300 lines per file, 50 lines per function.
- All runtime output uses the `logging` module. Bare `print()` is permitted ONLY in Phase 1 exploratory scripts; from Phase 2 onward, all modules must use `logging.getLogger(__name__)` with a shared configuration in `python\infrastructure\logging_setup.py`. Logs land in `python\logs\`.

---

## Section 3 — Operating Rules

### 3.4 AI Behavior Rules & Constraints

**MUST:**
- Use Python `mailbox.mbox()` for mbox parsing. Never split on `^From ` with regex, and never use `email.message_from_binary_file` with manual file seeking (both approaches failed in the April 17 session — see Entry 001).
- Respect the approved-sender whitelist from `data\sender_sheet.csv` (rows where `enabled=true`). Reject any sender not on the list.
- Output unparsed signals with raw context when extraction is ambiguous — never fabricate tickers.
- Split code per Tony's rules: 300 lines max per file, 50 lines max per function.
- Put all constants, paths, and thresholds in `python\config.py`. No hardcoded values elsewhere.
- State full Windows save path for every file produced.
- Keep layers separated: `domain\` (logic) → `infrastructure\` (I/O) → `application\` (orchestration). No monolithic scripts.

**MUST NOT:**
- Send, reply to, forward, or delete any email.
- Move messages to any folder other than `ExtractedNewsletterFolder`.
- Access IMAP servers directly in Phase 1 (Phase 2+ only, behind explicit constant flag).
- Hard-code profile paths or any other configuration values outside `python\config.py`.
- Call the Claude API when LM Studio is reachable unless explicitly overridden.
- Write to any persistent file without a matching Pydantic schema in `python\schemas.py`.

---

## Section 4 — Folder Structure

```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\
├── docs\
│   └── P_805_SYSTEM_DOCUMENTATION.md
├── data\
│   ├── daily\                      # daily signal output (Phase 5+)
│   ├── monthly\                    # monthly rollups
│   └── sender_sheet.csv            # AUTHORITATIVE approved-sender whitelist
└── python\
    ├── config.py                   # all paths, thresholds, constants
    ├── schemas.py                  # Pydantic models (added Phase 4+)
    ├── cli.py                      # command-line entry point
    ├── launcher.bat                # Windows launcher (added later)
    ├── requirements.txt            # project dependencies
    ├── domain\                     # pure logic, no I/O
    │   └── headers.py              # RFC 2047 header decoding
    ├── infrastructure\             # all I/O (mbox, CSV, LLM)
    │   └── mbox_reader.py          # stdlib mailbox.mbox() wrapper
    ├── application\                # orchestration of domain + infra
    │   └── phase1_scan.py          # Phase 1 scan workflow
    ├── logs\                       # run logs, rejected senders, errors
    └── _legacy\                    # pre-architecture scripts, preserved for reference
        ├── diagnose.py             # April 17 — diagnostic scan
        └── p805_scanner_simple.py  # April 17 — monolithic scanner (violates Section 3.4)
```

---

## Section 5 — Approved Senders Registry

### 5.1 Authoritative Source
The approved-sender whitelist is `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\data\sender_sheet.csv`.

### 5.2 CSV Schema
| Column | Type | Purpose |
|--------|------|---------|
| `email_address` | string | Full sender address (e.g., `daily@wallstreetzen.com`) |
| `sender_name` | string | Display name for reports |
| `date_added` | YYYY-MM-DD | When sender was whitelisted |
| `sector` | string | Sector tag (optional; currently unpopulated) |
| `enabled` | `true`/`false` | Only `true` rows are scanned |

### 5.3 Current State
As of 2026-04-20, the sheet contains **31 enabled senders** covering Zacks, Wall Street Zen, Analyst Ratings, Chaikin, Hedgeye, Beehiiv newsletters, Substack newsletters, Tim Sykes, Trading Pub, Trade Elite, Market Taker, Activate Trade, Freedom Income Options, Tradethirsty, Daily Upside, and several others.

### 5.4 Editing
Tony edits the CSV directly (Excel or text editor). No code change is needed to add, remove, or disable a sender — flip `enabled` to `false` to stop scanning without losing history.

### 5.5 Open Items
- `sector` column is unpopulated — tag senders by sector before Phase 4 ranking so consensus can be weighted by cross-sector agreement.
- Some entries share a parent domain (e.g., multiple `@mail.beehiiv.com` senders) — consider a `parent_domain` column if dedup-by-publisher becomes useful.

---

## Section 6 — Error Corrections Log

### Entry 001 — mbox Regex Parse Dead-End
- **Date:** 2026-04-17
- **Severity:** High
- **Context:** Extracted email blocks by splitting raw mbox content on `(?m)^From ` in PowerShell, and later iterated with `email.message_from_binary_file` + manual `seek()` on top-of-file `From_` detection in Python.
- **Failure mode:** Multipart MIME boundaries and quoted-printable content contain lines starting with "From " that got misattributed as new messages. Sender and subject extraction returned partial or wrong data. The Python binary-file approach has the same vulnerability once past the first message.
- **Correction:** Use Python's `mailbox.mbox()` parser exclusively. It handles MIME boundaries, Content-Transfer-Encoding, and `From_` line escaping per RFC 4155.
- **Rule added:** See Section 3.4 MUST rule.

### Entry 002 — Ignored python-project-architecture Skill
- **Date:** 2026-04-20
- **Severity:** Medium
- **Context:** First drafted Phase 1 code with a `scripts\reader\read_mbox.py` monolith and a `config\parameters.json` runtime config file, ignoring the Hub-wide `python-project-architecture` skill that defines the `python\` layout with `domain\`, `infrastructure\`, `application\` layer separation and `config.py` as the canonical constants location.
- **Failure mode:** Delivered a 125-line single-file script and a parallel JSON config, neither of which matched Tony's existing project layout or standards.
- **Correction:** Read `/mnt/skills/user/python-project-architecture/SKILL.md` at the start of any Python work. File plan gets validated against the skill BEFORE code is written.
- **Rule added:** Sections 2.6 and 3.4 now explicitly reference the architecture standard.

---

## Section 7 — Build Roadmap

**Phase 1 — Reader (current)**
Open one Thunderbird mbox file, iterate messages, print sender + subject + date for the lookback window. No filtering yet. Target: `python\application\phase1_scan.py` calling `python\infrastructure\mbox_reader.py`.

**Phase 2 — Approved Sender Filter + Logging Migration**
First task: create `python\infrastructure\logging_setup.py` with a shared logger configured to write both to console and to `python\logs\p805.log` (rotating). Migrate all Phase 1 `print()` calls in `application\phase1_scan.py` to `logger.info()` / `logger.warning()`. Then load `data\sender_sheet.csv`, filter Phase 1 output to `enabled=true` rows. Log rejected senders to `python\logs\rejected.log` so the whitelist can be tuned.

**Phase 3 — Ticker Extraction**
Regex pass first (cashtags `\$[A-Z]{1,5}`, common patterns) with a non-ticker blocklist ported from `_legacy\p805_scanner_simple.py`. LLM fallback via LM Studio for ambiguous bodies. Output: list of `Ticker Signal` tuples. Also port the `EXCLUDED_SENDERS` list from legacy (filters WhatsApp contacts that appear in email exports).

**Phase 4 — Aggregation & Ranking**
Dedup, compute consensus (≥2 sources), rank by source count and recency. Pandas DataFrame output. Introduce `python\schemas.py` with Pydantic models for the output rows.

**Phase 5 — Writer**
Write `data\daily\YYYY-MM-DD_signals.md` + `.json`. Optional P_800 MCP hook to inject a summary block into today's Obsidian daily note.

---

## Section 8 — Enhancement Backlog

- Direct IMAP pull (remove Thunderbird dependency)
- Gmail MCP connector as alternative source
- LLM-based signal quality scoring (conviction, recency, specificity)
- Sentiment analysis on subject lines
- Historical signal performance tracking vs. actual ticker moves (hooks into P_010 data)
- WhatsApp export ingestion path shared with P_800 (reuse extractor layer)
- Populate `sector` column in `sender_sheet.csv` for sector-weighted consensus

---

## Section 11 — Parameters

### 11.4 Parameter Registry
All parameters live as constants in `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python\config.py`. This table is the canonical list; the code file is the source of truth.

| Parameter | Value | Notes |
|-----------|-------|-------|
| `HUB_ROOT` | `C:\Users\Trader\AI-Agent-Learning-Hub` | Only hardcoded path allowed per architecture standard |
| `SCAN_DAYS` | `30` | Default lookback window |
| `PROFILE_PATH` | `m306ztzh.IETimport` | Confirmed 2026-04-20; IMAP-import profile containing newsletter archive |
| `THUNDERBIRD_ROOT` | `C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles` | |
| `MBOX_FILE` | `""` (blank) | Relative path under `MAIL_ROOT`. Blank → first run lists candidates. |
| `EXTRACTED_FOLDER_NAME` | `ExtractedNewsletterFolder` | Peer of Inbox; destination for successfully extracted messages |
| `EXTRACTED_FOLDER_AUTOCREATE` | `True` | Create folder on first run if missing |
| `SENDER_SHEET` | `<PROJECT>\data\sender_sheet.csv` | Authoritative approved-sender list |
| `DATA_DAILY_DIR` | `<PROJECT>\data\daily` | Phase 5 output |
| `DATA_MONTHLY_DIR` | `<PROJECT>\data\monthly` | Monthly rollups |
| `LOGS_DIR` | `<PROJECT>\python\logs` | Run logs, rejected senders |
| `LLM_PRIMARY` | `"LM Studio"` | localhost |
| `LLM_FALLBACK` | `"Claude API"` | Used only when LM Studio unreachable or flag set |
| `CONSENSUS_THRESHOLD` | `2` | Min source count for consensus signal (Phase 4+) |

**Never substitute assumed values for these constants.** If a constant needs to change, update `config.py` — do not hardcode in any other file.

---

*End of P_805 SYSTEM_DOCUMENTATION v1.1*
