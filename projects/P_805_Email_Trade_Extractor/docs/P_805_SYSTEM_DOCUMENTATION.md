# P_805 SYSTEM_DOCUMENTATION
## Email Trade Extractor

---

**Project ID:** P_805
**Project Name:** Email Trade Extractor
**Version:** 1.8
**Created:** 2026-04-20
**Updated:** 2026-06-14 (v1.8 — per-sender ticker cap added; SENDER_MAX_TICKERS in config.py; Stocktwits Daily Rip capped at 5 tickers/email; Gemini 2.5 Flash added as LLM primary for direction enrichment and KB summarization)
**Owner:** Tony
**Status:** **ACTIVE** — Phases 1, 2, 3, 3.5, 4 complete. Phase 5 Writer (KB mode) live for .eml ingestion. Phase 3 (daily ticker CSV) on 30-day schedule via scheduled task.
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
12. Session Close & Resume Path

---

## Section 1 — Project Overview

### 1.1 Purpose
Extract ticker recommendations and trade signals from email newsletters stored in Thunderbird, deduplicate across sources, and produce a daily ranked output that feeds Tony's morning trading workflow. Once a message is successfully identified and extracted, move it to an `ExtractedNewsletterFolder` — a peer folder of Inbox — in the current hosted email client. The system never sends, replies to, forwards, or deletes mail.

### 1.2 Goals
- Scan approved-sender emails over a configurable lookback window (default 30 days)
- Extract tickers, direction (long/short/watch), and entry/stop/target where provided
- Dedupe signals and rank by source agreement
- Write daily output to `data\daily\` as CSV (markdown + JSON come in Phase 5)
- Optional: inject summary into Obsidian daily note via P_800's MCP bridge

### 1.3 In-Scope
- Reading mail from Tony's four IMAP accounts in priority order (iCloud > Gmail > Outlook > Yahoo) via Thunderbird's local mbox cache under the **m306ztzh.IETimport** profile
- Parsing mbox files using Python's `mailbox` module
- Whitelist-based sender filtering (source: `data\sender_sheet.csv`, currently 59 enabled)
- Regex-based ticker extraction with extensible pattern list in `config.py`
- Moving extracted messages to `ExtractedNewsletterFolder` (peer of Inbox) in the active email client (Phase 5 work)

### 1.4 Out-of-Scope
- Sending, replying to, forwarding, or deleting any email
- Executing trades (P_805 produces a research list only)
- **Category-based email triage and LLM summarization across the whole mailbox** — that is a separate future project, NOT P_805

### 1.5 Definitions & Acronyms
- **Approved Sender** — email address on the whitelist in `data\sender_sheet.csv` with `enabled=true`
- **Ticker Signal** — `TickerSignal` Pydantic record (ticker, direction, confidence, pattern, source, timestamp, subject, raw_context, account)
- **Consensus Signal** — ticker appearing in ≥2 approved sources within the lookback window (Phase 4 concept)
- **mbox** — Thunderbird's mail file format (one flat file per folder, no extension)
- **Cashtag** — ticker prefixed with `$`, e.g. `$TSLA` or `$AAPL` (Twitter/Stocktwits convention)
- **Pattern** — one entry in `config.TICKER_PATTERNS`, used by the extractor; new patterns are added by appending a dict to that list
- **Lookback Window** — number of days back from today to scan (constant: `SCAN_DAYS` in `config.py`, default 30)
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
- **PowerShell** — only for filesystem probes; never used for mbox parsing

### 2.3 Libraries
- `mailbox` (stdlib) — mbox parsing
- `email` (stdlib) — header and body extraction
- `html.parser` (stdlib) — HTML stripping
- `pydantic` v2 — schemas for persistent file I/O
- `pandas` — dedup, ranking, daily frame output (Phase 4+)
- `requests` — LLM API calls (LM Studio or Claude) (Phase 3.5+ when LLM enrichment is added)
- `obsidian_writers` — Obsidian vault automation (P_800 integration; KB mode)

`imaplib` and `keyring` are **NOT** used. The previous plan for direct IMAP access was shelved when the actual live Thunderbird profile was identified (see Entry 005).

### 2.4 Storage
- Filesystem only. No database in Phase 1–3.
- Daily output: `data\daily\YYYY-MM-DD_signals.csv` (Phase 3 produces this; Phase 5 will add `.md` and `.json`)
- Logs: `python\logs\p805.log` (rotating, 5 MB × 3) and `python\logs\rejected.log` (rotating, 5 MB × 3)
- Monthly rollups: `data\monthly\` (Phase 4+)

### 2.5 LLM Priority
Per Tony's global preference: **LM Studio first** (local, free, private), **Claude API second** (fallback when LM Studio unavailable or when reasoning quality matters — e.g., ambiguous extraction).

### 2.6 Code Architecture Standard
This project follows the Hub-wide **python-project-architecture** standard:
- Code lives under `python\`, split into `domain\` (logic, no I/O), `infrastructure\` (all I/O), `application\` (orchestration).
- All constants and paths live in `python\config.py`. Never hardcoded elsewhere.
- Any persistent file read or write requires a Pydantic schema in `python\schemas.py`.
- Hard limits: 300 lines per file, 50 lines per function.
- All runtime output uses the `logging` module via `infrastructure\logging_setup.py`. Bare `print()` is permitted ONLY in `_legacy\` diagnostic scripts.

---

## Section 3 — Operating Rules

### 3.4 AI Behavior Rules & Constraints

**MUST:**
- At session start in Claude Desktop, run `tool_search` for filesystem write capability. When writing or editing project code under `C:\Users\Trader\AI-Agent-Learning-Hub` or `D:\OneDrive`, use `filesystem:write_file` or `filesystem:edit_file` directly to the final project path. NEVER use `create_file` + `present_files` for project code (that's the download-and-manually-move pattern).
- Use Python `mailbox.mbox()` for mbox parsing. Never split on `^From ` with regex, and never use `email.message_from_binary_file` with manual file seeking (Entry 001).
- Respect the approved-sender whitelist from `data\sender_sheet.csv` (rows where `enabled=true`). Reject any sender not on the list. Also reject any sender whose From header contains a substring from `EXCLUDED_SENDER_SUBSTRINGS`.
- Output unparsed signals with raw context when extraction is ambiguous — never fabricate tickers.
- Split code per Tony's rules: 300 lines max per file, 50 lines max per function.
- Put all constants, paths, thresholds, **and regex patterns** in `python\config.py`. No hardcoded values elsewhere.
- State full Windows save path for every file produced (when files leave the writeable workspace).
- Keep layers separated: `domain\` (logic) → `infrastructure\` (I/O) → `application\` (orchestration).

**MUST NOT:**
- Send, reply to, forward, or delete any email.
- Move messages to any folder other than `ExtractedNewsletterFolder`.
- Point `PROFILE_PATH` at `2slie5gz.default-release` — that profile's IMAP caches are stale (frozen at late 2019). The live profile is `m306ztzh.IETimport` (Entry 005).
- Hard-code profile paths or any other configuration values outside `python\config.py`.
- Call the Claude API when LM Studio is reachable unless explicitly overridden.
- Write to any persistent file without a matching Pydantic schema in `python\schemas.py`.

---

## Section 4 — Folder Structure

```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\
├── docs\
│   └── P_805_SYSTEM_DOCUMENTATION.md         # this file (v1.4)
├── data\
│   ├── daily\
│   │   └── 2026-04-26_signals.csv            # first Phase 3 output (175 rows)
│   ├── monthly\                              # Phase 4+ rollups
│   └── sender_sheet.csv                      # AUTHORITATIVE whitelist (59 enabled)
└── python\
    ├── config.py                             # all paths, thresholds, patterns, keywords
    ├── schemas.py                            # ApprovedSender, TickerSignal, RankedSignal
    ├── cli.py                                # entry point: --phase 1|3|35|4, --account icloud|gmail|outlook|yahoo
    ├── requirements.txt                      # pydantic, email-validator, python-dateutil
    ├── domain\                               # pure logic, no I/O
    │   ├── __init__.py
    │   ├── headers.py                        # RFC 2047 header decoding
    │   ├── html_strip.py                     # HTML → text
    │   ├── sender_filter.py                  # extract address, approved-set membership
    │   ├── ticker_extractor.py               # find_tickers, infer_direction
    │   └── ranker.py                         # rank_signals, majority_direction (Phase 4)
    ├── infrastructure\                       # all I/O
    │   ├── __init__.py
    │   ├── logging_setup.py                  # main + reject loggers, rotating
    │   ├── mbox_body.py                      # extract plain-text body from message
    │   ├── mbox_reader.py                    # stdlib mailbox.mbox() wrapper
    │   ├── sender_sheet.py                   # load CSV → enabled set
    │   └── daily_csv_reader.py               # load signals CSV → TickerSignal list (Phase 4)
    ├── application\                          # orchestration
    │   ├── __init__.py
    │   ├── phase1_scan.py                    # scan + sender filter + per-account summary
    │   ├── phase3_extract.py                 # scan + ticker extraction + daily CSV
    │   ├── phase35_enrich.py                 # LLM direction enrichment for unknown signals (Phase 3.5)
    │   ├── phase4_rank.py                    # load signals → consensus ranking → ranked CSV (Phase 4)
    │   └── p805_kb_writer.py                 # KB mode: ingest .eml from data/inbox/, summarize, write to P_800 vault
    ├── logs\                                 # run logs (rotating)
    │   ├── p805.log
    │   ├── rejected.log
    │   └── approved_bodies_sample.txt        # one-off diagnostic dump (2026-04-26)
    └── _legacy\                              # pre-architecture + diagnostic scripts
        ├── diagnose.py
        ├── p805_scanner_simple.py            # source of EXCLUDED_SENDER_SUBSTRINGS
        ├── check_dates.py
        ├── check_all_inboxes.py
        ├── check_ietimport_dates.py          # April 26 — found live profile is IETimport
        └── peek_approved_bodies.py           # April 26 — dumped real bodies to design extractor
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
As of 2026-04-26, the sheet contains **59 enabled senders**. The original 30 (after the broken `zacks.com` row was removed) plus 29 additions discovered by reviewing `python\logs\rejected.log` after the first Phase 2 run. Coverage now spans Zacks (3 sender variants), Wall Street Zen (2 variants), Big Trends (2), T3 Live (2), Stocktwits Daily Rip, Michael Burry, Motley Fool, McMillan Option Strategist, Earnings Whispers, Macro Notes, Moonshot Minute, Katusa Research, Kiyosaki, Acorn Wealth, 30 Second Trader, Stocks To Trade, Moby, plus the original Hedgeye, Chaikin, Analyst Ratings, Beehiiv newsletters, Substack newsletters, Tim Sykes, Trade Elite, Market Taker, Trading Pub, Daily Upside, Tradethirsty, Activate Trade, Freedom Income Options, and others.

### 5.4 Editing
Tony edits the CSV directly (Excel or text editor). No code change is needed to add, remove, or disable a sender — flip `enabled` to `false` to stop scanning without losing history.

### 5.5 Open Items
- `sector` column is unpopulated — tag senders by sector before Phase 4 ranking so consensus can be weighted by cross-sector agreement.
- Some entries share a parent domain (e.g., multiple `@mail.beehiiv.com` senders) — consider a `parent_domain` column if dedup-by-publisher becomes useful.
- The `expected_account` column proposed in v1.3 is no longer urgent because all four accounts scan in well under a second from local mbox.

---

## Section 6 — Error Corrections Log

### Entry 001 — mbox Regex Parse Dead-End
- **Date:** 2026-04-17
- **Severity:** High
- **Context:** Extracted email blocks by splitting raw mbox content on `(?m)^From ` in PowerShell, and later iterated with `email.message_from_binary_file` + manual `seek()` on top-of-file `From_` detection in Python.
- **Failure mode:** Multipart MIME boundaries and quoted-printable content contain lines starting with "From " that got misattributed as new messages.
- **Correction:** Use Python's `mailbox.mbox()` parser exclusively.

### Entry 002 — Ignored python-project-architecture Skill
- **Date:** 2026-04-20
- **Severity:** Medium
- **Context:** First drafted Phase 1 code with a `scripts\reader\read_mbox.py` monolith and a `config\parameters.json` runtime config file, ignoring the Hub-wide `python-project-architecture` skill.
- **Correction:** Read `/mnt/skills/user/python-project-architecture/SKILL.md` at the start of any Python work.

### Entry 003 — Wrong Thunderbird Profile + Ignored ImapMail Directory
- **Date:** 2026-04-20
- **Severity:** High
- **Context:** Configured `PROFILE_PATH = m306ztzh.IETimport` (mistakenly believed to be archive at the time) and scoped scanning to `<profile>\Mail\` only. First Phase 1 run produced 130+ Local Folders archive mbox files.
- **Correction:** Switched to `2slie5gz.default-release` and walked both `Mail\` and `ImapMail\`. **Note:** This correction was itself wrong — see Entry 005.

### Entry 004 — Thunderbird Local Cache Believed Stale
- **Date:** 2026-04-20
- **Severity:** Project-blocking (at the time)
- **Context:** Once the scanner was pointed at `2slie5gz.default-release\ImapMail\`, every IMAP inbox file appeared frozen in late 2019.
- **Correction (at the time):** Project parked; Phase 1.5 (direct IMAP via `imaplib` + `keyring`) promoted to critical path.
- **Correction (actual, see Entry 005):** This conclusion was wrong. The frozen mboxes were in the wrong profile.

### Entry 005 — Live Profile Was IETimport All Along (Reverses Entries 003 & 004)
- **Date:** 2026-04-26
- **Severity:** High (positive)
- **Context:** Diagnostic listing of `m306ztzh.IETimport\ImapMail\` showed every INBOX file modified within the past hour and gigabytes of recent content. Running `check_ietimport_dates.py` confirmed: Yahoo, Gmail, iCloud, and Outlook INBOXes all current with newest messages from today.
- **Failure mode:** Thunderbird appends `-1` to a server hostname when the same hostname appears across multiple account configs. The IETimport profile holds `imap.gmail-1.com` and `imap.mail.me-1.com` (the live caches); the default-release profile holds the un-suffixed versions (which are dormant). The naming made IETimport look like an "import archive" when it is in fact the live profile.
- **Correction:** `PROFILE_PATH` set to `m306ztzh.IETimport`; `MBOX_FILES` dict updated with the `-1` hostnames for Gmail and iCloud. Phase 1.5 IMAP detour shelved entirely. `imaplib`, `keyring`, and app-specific passwords are no longer needed for this project.

### Entry 006 — Sandbox Download Pattern for Files That Belong in the Project
- **Date:** 2026-04-26
- **Severity:** Medium (recurring across many sessions)
- **Context:** For multiple files during the early part of this session, code was generated via `create_file` to `/mnt/user-data/outputs/` and surfaced via `present_files`. Tony then had to manually move each file to its project location, and at one point overwrote the wrong file because the new version landed in `Downloads`.
- **Failure mode:** Defaulting to the sandbox download pattern when filesystem MCP write tools were available the whole time.
- **Correction:** Memory edit added (rule #1): in Claude Desktop, always call `tool_search` for filesystem write capability at session start; for any project code under `C:\Users\Trader\AI-Agent-Learning-Hub` or `D:\OneDrive`, write directly to the final project path via `filesystem:write_file` or `filesystem:edit_file`. The sandbox `/mnt/user-data/outputs/` path is reserved for one-off diagnostics only.

### Entry 007 — MIME-Encoded Subject Headers in KB Mode Output
- **Date:** 2026-05-25
- **Severity:** High
- **Context:** `p805_kb_writer.py` read raw email Subject and From headers via `msg.get("Subject")` without decoding, passing MIME-encoded values directly to Obsidian as note titles. Example: `=?UTF-8?B?8J+UkQ==?= Create your second brain.` (an encoded emoji + text) was slugified to `UTF-8B8JUKQ-CREATE-YOUR-SECOND-BRAIN.md`.
- **Failure mode:** RFC 2047 encoded headers (common in international newsletters) landed un-decoded in KB frontmatter `title` field and filename slugs, breaking readability and searchability.
- **Correction:** Import `decode_header_safe()` from `domain.headers` (already in use in Phase 3). Apply to both `Subject` and `From` headers before storing in KB record. `decode_header_safe()` uses Python's `email.header.decode_header()` + `make_header()` to safely convert encoded tokens to plain Unicode.

### Entry 008 — LM Studio Context Window Overflow on Longer Emails
- **Date:** 2026-05-25
- **Severity:** High
- **Context:** KB mode summarization of longer newsletter emails (\~4000+ tokens) failed with `400 Bad Request` from LM Studio. Initial investigation pointed to wrong model name, timeout settings, and system prompt interference. Actual cause discovered via enhanced error logging: `{"error":"The number of tokens to keep from the initial prompt is greater than the context length (n_keep: 4162>= n_ctx: 4096)"}`.
- **Failure mode:** deepseek-r1-distill-qwen-14b was loaded with `n_ctx=4096` (4K context window). Email body + system prompt = 4162 tokens. LM Studio rejected the request (400) before Truncate Middle could apply.
- **Correction:** Reload the model with larger context length (`n_ctx=8192` or higher). Deepseek natively supports 128K+ context; 8K is well within spec and costs \~1–2GB additional VRAM per model instance. Updated `lm_studio_caller.py` error handler to capture and log LM Studio's actual error response body for faster future diagnosis. Also added regex to strip `<think>...</think>` blocks from reasoning-model outputs to prevent reasoning artifacts in KB note bodies.

---

## Section 7 — Build Roadmap

**Phase 1 — Reader: ✅ COMPLETE (2026-04-26)**
Walks all four IMAP INBOX caches under the live profile, prints sender + subject + date for every message in the lookback window. Successful end-to-end run: 1,209 messages in file across four accounts, 1,174 in 30-day window.

**Phase 1.5 — Direct IMAP: ❌ SHELVED (2026-04-26)**
Was promoted from backlog to critical path on 2026-04-20 under the false belief that local cache was stale. Entry 005 reversed that. Direct IMAP is no longer on the path. Could be revived in the future if the desktop client is removed from the workflow, but no current need.

**Phase 2 — Approved Sender Filter + Logging Migration: ✅ COMPLETE (2026-04-26)**
Console output replaced by main + reject loggers (rotating files at `python\logs\p805.log` and `python\logs\rejected.log`). Sender filter loads `data\sender_sheet.csv`, validates rows through `ApprovedSender` Pydantic schema, returns lowercased enabled-set. Result on first run: 240 of 1,174 in-window messages approved (20.4%) across 59 enabled senders.

**Phase 3 — Ticker Extraction: ✅ COMPLETE (2026-04-26)**
Regex extractor with four configured patterns (`exchange_paren`, `cashtag`, `wsz_url`, `bare_paren`). Pattern list lives in `config.TICKER_PATTERNS` as a list of dicts; adding a new pattern is a one-line edit with no domain-code changes. Direction inference is keyword-based via `config.DIRECTION_KEYWORDS`. First run produced 175 rows in `data\daily\2026-04-26_signals.csv` covering \~140 unique tickers across all four accounts. Scheduled to run daily at 9:15 AM via Windows Task Scheduler.

**Phase 3.5 — LLM Direction Enrichment: ✅ COMPLETE (2026-06-14)**
Runs after Phase 3, before Phase 4. Loads today's signals CSV, calls LM Studio for every `direction=unknown` row, rewrites CSV in-place. Non-unknown rows are never touched. Production run: 203 of 275 unknowns resolved (74%); 72 remain unknown (genuinely ambiguous context). Key learnings: DeepSeek R1 distill models (any size) consume all tokens on reasoning and return empty `content` — unusable for single-word classification. **Qwen2.5-7B-Instruct (bartowski Q4_K_S)** is the correct model — returns answers directly in `content` with no reasoning overhead. `RAW_CONTEXT_CHARS` must be ≥300 for reliable classification; raised to 500 alongside `DIRECTION_WINDOW_CHARS`. Synonym mapping in parser handles model returning `bullish`/`bearish`/`neutral` instead of `long`/`short`/`watch`. Direction majority vote in Phase 4 is correct behavior when sources disagree.

**Phase 4 — Aggregation & Ranking: ✅ COMPLETE (2026-06-14)**
Dedup across sources, consensus filter (`CONSENSUS_THRESHOLD=2`), rank by source count descending then ticker ascending. Output: `data\daily\YYYY-MM-DD_ranked.csv` (one row per consensus ticker, columns: ticker, source_count, sources, direction, first_seen, last_seen). New modules: `domain\ranker.py`, `infrastructure\daily_csv_reader.py`, `application\phase4_rank.py`. First run: 347 raw signals → 20 consensus tickers. Top hits: ADBE (3 sources, short), SPCX (3 sources, long). 12 of 20 returned direction=unknown — expected until Phase 3.5 LLM enrichment is added.

**Phase 5 — Writer: ⏳ PARTIALLY LIVE (2026-05-25)**
KB mode (`--kb-mode summary|full`) complete and producing Obsidian notes from `.eml` files in `data\inbox\`. Integrates with P_800's `obsidian_writers` package and LM Studio for optional email summarization. Each email → one note with title (decoded subject), frontmatter (source, date, tags, ticker relevance), and body (full or summarized per CLI flag). Moves to `trading_journal\KnowledgeBase\` via P_800 interface. CSV output (Phase 5.1) and `.md`/`.json` alongside CSV (Phase 5.2) are future items.

---

## Section 8 — Enhancement Backlog

- ~~Direct IMAP pull (remove Thunderbird dependency)~~ — SHELVED (2026-04-26, Entry 005). Local cache works.
- ~~Expand `DIRECTION_KEYWORDS` with newsletter-typical verbs~~ — DONE (2026-06-14). Added ripped, soared, popped, cratered, tumbled, tanked, jumped, climbed, plunged and others.
- ~~Fix CSV encoding for Excel~~ — DONE (2026-06-14). `phase3_extract.py:write_csv` now uses `encoding="utf-8-sig"`.
- ~~LLM-based direction & conviction scoring (LM Studio first, fall back to Claude API)~~ — DONE (2026-06-14) as Phase 3.5. Qwen2.5-7B-Instruct via LM Studio; 74% unknown resolution rate.
- Sentiment analysis on subject lines
- Historical signal performance tracking vs. actual ticker moves (hooks into P_010 data)
- Populate `sector` column in `sender_sheet.csv` for sector-weighted consensus
- Add a `parent_domain` column to `sender_sheet.csv` for dedup-by-publisher
- ~~Stocktwits Daily Rip per-sender ticker cap~~ — DONE (2026-06-14). `SENDER_MAX_TICKERS` in config.py; Stocktwits Daily Rip capped at 5 tickers/email.
- BigTrends Sunday Night Trader pattern check (deferred 2026-04-26) — only worth doing if Phase 4 shows we're missing structured picks from that source
- Gmail MCP connector as alternative Gmail source (parallel path, not replacement)
- WhatsApp export ingestion path shared with P_800 (reuse extractor layer)

---

## Section 11 — Parameters

### 11.4 Parameter Registry
All parameters live as constants in `python\config.py`. This table is the canonical list; the code file is the source of truth.

| Parameter | Value | Notes |
|-----------|-------|-------|
| `HUB_ROOT` | `C:\Users\Trader\AI-Agent-Learning-Hub` | Only hardcoded path allowed per architecture standard |
| `SCAN_DAYS` | `30` | Default lookback window |
| `THUNDERBIRD_ROOT` | `C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles` | |
| `PROFILE_PATH` | `m306ztzh.IETimport` | Live profile (Entry 005) |
| `PROFILE_ROOT` / `MAIL_ROOT` / `IMAP_ROOT` | derived | |
| `MBOX_FILES` | dict, 4 entries | iCloud / Gmail / Outlook / Yahoo INBOX paths under `IMAP_ROOT`. Gmail and iCloud use `-1` hostname suffix. |
| `IMAP_ACCOUNT_ORDER` | `["icloud", "gmail", "outlook", "yahoo"]` | Trading-info priority |
| `EXTRACTED_FOLDER_NAME` | `ExtractedNewsletterFolder` | Phase 5+ |
| `EXTRACTED_FOLDER_AUTOCREATE` | `True` | |
| `SENDER_SHEET` | `<PROJECT>\data\sender_sheet.csv` | Authoritative approved-sender list |
| `DATA_DAILY_DIR` | `<PROJECT>\data\daily` | Phase 3 output location |
| `DATA_MONTHLY_DIR` | `<PROJECT>\data\monthly` | Phase 4+ rollups |
| `LOGS_DIR` | `<PROJECT>\python\logs` | Run logs |
| `LOG_FILE` | `LOGS_DIR\p805.log` | Main log, rotating 5 MB × 3 |
| `REJECT_LOG_FILE` | `LOGS_DIR\rejected.log` | Rejected senders, rotating 5 MB × 3 |
| `LOG_LEVEL_CONSOLE` | `"INFO"` | |
| `LOG_LEVEL_FILE` | `"DEBUG"` | |
| `LOG_MAX_BYTES` | `5_000_000` | |
| `LOG_BACKUP_COUNT` | `3` | |
| `TICKER_PATTERNS` | list of 4 dicts | `exchange_paren`, `cashtag`, `wsz_url`, `bare_paren` — extension point: append new dicts here |
| `BARE_PAREN_BLOCKLIST` | set, ~50 entries | Common parenthesized non-tickers (CEO, USA, PDF, etc.) |
| `DIRECTION_KEYWORDS` | dict (long/short/watch → keyword lists) | Extension point: edit lists in config |
| `DIRECTION_WINDOW_CHARS` | `500` | Context window for direction inference (raised from 120, 2026-06-14) |
| `RAW_CONTEXT_CHARS` | `500` | Stored on each `TickerSignal.raw_context` (raised from 80, 2026-06-14) |
| `EXCLUDED_SENDER_SUBSTRINGS` | `["impens", "andreessen", "gaud"]` | Substring match against From header |
| `DAILY_OUTPUT_CSV` | `"{date}_signals.csv"` | Phase 3 output filename pattern |
| `CONSENSUS_THRESHOLD` | `2` | Min source count for consensus signal (Phase 4+) |
| `LLM_PRIMARY` | `"LM Studio"` | localhost |
| `LLM_FALLBACK` | `"Claude API"` | |
| `GEMINI_MODEL` | `"gemini-2.5-flash"` | Gemini primary for classify_direction and summarize; key loaded from python\.env |
| `SENDER_MAX_TICKERS` | `{"newsletter@thedailyrip.stocktwits.com": 5}` | Per-sender cap on tickers per email; checked in phase3_extract.py after _best_per_ticker() |
| `LM_STUDIO_URL` | `"http://127.0.0.1:1234/v1"` | OpenAI-compatible endpoint |
| `LM_STUDIO_MODEL` | `"qwen2.5-7b-instruct"` | Phase 3.5 direction classification (bartowski Q4_K_S). KB summarization uses deepseek-r1-distill-qwen-14b at n_ctx=8192 — swap model in LM Studio before running KB mode. |
| `LM_STUDIO_TEMP` | `0.3` | Lower temp for focused summaries |
| `LM_STUDIO_MAX_TOKENS` | `300` | Output limit per summary |
| `LM_STUDIO_TIMEOUT` | `60` | Request timeout in seconds |
| `KB_MODE_PATTERN_FULL` | `r"--full\.eml$"` | Filename pattern for full-text ingestion |
| `KB_MODE_PATTERN_SUMMARIZE` | `r"--summarize\.eml$"` | Filename pattern for summarization |
| `PROJECT_ROOT` | `<HUB_ROOT>\projects\P_805_Email_Trade_Extractor` | KB mode data dir |
| `INBOX_PATH` | `<PROJECT_ROOT>\data\inbox` | .eml files staged here for KB ingestion |

---

## Section 12 — Session Close & Resume Path

### 12.1 Status at Close (2026-06-14)
Phases 1, 2, 3, 3.5, and 4 are complete. Full pipeline runs daily: Phase 3 → Phase 3.5 → Phase 4. Per-sender ticker cap live (v1.8).

What works end-to-end:
- `python cli.py` — Phase 1 scan with per-account summary
- `python cli.py --phase 1 --account icloud` — single-account scan
- `python cli.py --phase 3` — full extraction → daily signals CSV (scheduled 9:15 AM). Latest: 347 signals, 2026-06-14.
- `python cli.py --phase 35` — LLM direction enrichment on today's signals CSV. Latest: 203/275 unknowns resolved.
- `python cli.py --phase 4` — consensus ranking → ranked CSV. Latest: 22 consensus tickers.
- `python cli.py --kb-mode summary` — ingest .eml files, summarize via LM Studio (load deepseek-r1-distill-qwen-14b at n_ctx=8192 first), write KB notes to Obsidian vault
- `python cli.py --kb-mode full` — ingest .eml files, write full-text KB notes
- All runs go through `infrastructure\logging_setup.py` for consistent log handling
- `data\sender_sheet.csv` — single source of truth for whitelist (59 enabled rows)
- `python\config.py` — single source of truth for all paths, thresholds, patterns, LLM settings

**Important model note:** `LM_STUDIO_MODEL` is now `qwen2.5-7b-instruct` (Phase 3.5). KB mode (`--kb-mode`) requires swapping to `deepseek-r1-distill-qwen-14b` at `n_ctx=8192` in LM Studio before running.

What's queued (in priority order):
1. **Schedule Phase 3.5 and Phase 4.** Add both to Windows Task Scheduler so the full pipeline runs automatically after Phase 3 at 9:15 AM.
2. **Sector weighting.** Populate `sector` column in `sender_sheet.csv` so Phase 4 can weight consensus by cross-sector agreement.
3. **Entry 009.** Add an error corrections entry documenting the DeepSeek R1 distill reasoning-model failure for single-word classification tasks.

### 12.2 Session Identifier for Resume Reference
- Chat on 2026-06-14 covered: DIRECTION_KEYWORDS expansion, CSV UTF-8 BOM fix, Phase 4 build, Phase 3.5 LLM enrichment build, DeepSeek R1 distill failure diagnosis, Qwen2.5-7B-Instruct adoption, RAW_CONTEXT_CHARS/DIRECTION_WINDOW_CHARS raised to 500, full pipeline producing 22 consensus tickers (ADBE long 3 sources, SPCX long 3 sources, TSLA short, PLTR short, GLD short).

### 12.3 First Tasks on Resume
1. Read Section 12, confirm date and status with Tony.
2. Verify `tool_search` for filesystem write tools.
3. Ask Tony which queued item to start with — likely Phase 3.5 scheduling or Phase 5 scoping.

---

*End of P_805 SYSTEM_DOCUMENTATION v1.8 — ACTIVE*
