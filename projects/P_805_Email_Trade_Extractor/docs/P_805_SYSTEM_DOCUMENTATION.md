# P_805 SYSTEM_DOCUMENTATION

## Email Trade Extractor

***

**Project ID:** P_805 **Project Name:** Email Trade Extractor **Version:** 2.8 **Created:** 2026-04-20 **Updated:** 2026-09-06 (v2.8 — corrected a stale Section 12.0 queue item: "Outlook OAuth2 first login" was still listed as outstanding even though Entry 015 and this header both already confirm it succeeded 2026-08-23. Documentation only — no code changed, no new finding, just the queue list catching up to the header it contradicted.) **Prior:** 2026-09-06 (v2.7 — Yahoo retention policy set: 10-day "Delete messages more than 10 days old" applied to Yahoo's `ExtractedNewsletterFolder`, matching icloud/gmail. Last item on the Section 12.0 queued list closed out.) **Prior:** 2026-09-06 (v2.6 — Entry 016: root-caused a silent 32-day gap in the 9:15 AM scheduled pipeline (2026-07-22 through 2026-08-23, zero `data\daily\*_signals.csv` output) to the task's Interactive logon requirement — no error surfaced anywhere, Task Scheduler simply skips the run if Tony isn't logged into an active Windows session at 9:15 AM. Confirmed live 2026-09-06 that every run since 2026-08-23 has produced a CSV daily through today, no further gaps. Documentation only — no code changed this entry.) **Prior:** 2026-08-23 (v2.5 — Entry 015: fixed a missing configure_logging() call in the `--outlook-oauth-login` path (new `application/outlook_oauth_login.py` wrapper) — the login had actually succeeded, the terminal just never showed it. **Outlook OAuth2 is now confirmed LIVE**: first browser login succeeded, `--check-imap-auth --account outlook` passes silently on refresh via the DPAPI cache.) **Prior:** 2026-08-23 (v2.4 — Entry 014: Outlook OAuth2 token storage moved from keyring (Entry 013, hit a real WinError 1783 on Tony's first live login — Windows Credential Manager's \~1280-2560 char cap) to msal-extensions' DPAPI-encrypted file cache. Fix found already implemented on disk mid-session, not written by this chat — verified via full test suite, found and fixed one real test bug. 10/10 tests pass. Outlook still not live — Tony re-running the login.) **Prior:** 2026-08-23 (v2.3 — Entry 013: Outlook OAuth2 IMAP support built. New `infrastructure/oauth2_outlook.py` (msal token cache lifecycle), `infrastructure/imap_mover.py` branches to XOAUTH2 for outlook, `config.py` adds OAuth block, `config.MOVE_SKIP_ACCOUNTS` reverted to empty. 11/11 tests pass via PEH. Outlook not yet live — pending Tony's one-time `--outlook-oauth-login` browser consent and a live `--check-imap-auth --account outlook` pass.) **Prior:** 2026-07-18 (v2.2 — Sector-weighted consensus built: `RankedSignal.sector_count` added to schema, `load_sender_sectors()` added to `infrastructure/sender_sheet.py`, `domain/ranker.py` and `application/phase4_rank.py` wired to compute distinct-sector count per consensus ticker (untagged senders bucket as 'unknown' and don't inflate the count). Populated `sector` for 25 of 59 senders in `sender_sheet.csv` from real subject-line/raw_context evidence across 4 days of signals history — remaining 34 left blank for Tony (no ticker-producing history yet to categorize from). Flagged `alex@kryptonstreet.ccsend.com` / `gary@marketcrux.ccsend.com` as likely same publisher (same ccsend.com platform, same tickers same days, near-identical copy) — tagged both `momentum_promo` rather than opening a separate parent_domain investigation; ticker GIPR in the first live run correctly showed `sector_count=1` for this pair, confirming the mechanism catches it. Verified via live `--phase 4` run against real 2026-07-18 signals (25 consensus tickers, `sector_count` column present and correct). Entry 012 logged: Windows-MCP PowerShell hangs (\~4 min, transport error) on `python ... | Select-Object -Last N`-style piped calls even for sub-second commands — `Start-Process -Wait` with `-RedirectStandardOutput/-RedirectStandardError` to a file is the reliable pattern for short synchronous Python calls in this environment.) **Prior:** 2026-07-18 (v2.1 — Task Scheduler wiring complete: `P_805_daily_pipeline.bat` + `P_805_daily_pipeline_mcp.ps1` built, chaining Phase 3 → 3.5 → 4 → 5.3 with abort-on-failure for Phase 3/4 and continue-on-failure for 3.5/5.3. Registered as scheduled task `P_805_Daily_Pipeline_915AM`, daily 9:15 AM, Interactive logon (required for keyring access), Limited run level. First live manual run 2026-07-18: Phase 3 = 205 signals, Phase 3.5 = complete (a few transient Gemini 503s, LM Studio fallback covered them), Phase 4 = ranked CSV written, Phase 5.3 = Moved=57 DryRun=0 NotFound=6 Failed=0. Full pipeline runtime \~7 minutes end to end.) **Owner:** Tony **Status:** **ACTIVE** — Phases 1, 2, 3, 3.5, 4, 5.3 complete and live. Full daily pipeline (3→3.5→4→5.3) scheduled via Task Scheduler at 9:15 AM. Phase 5 KB mode live for .eml ingestion. Outlook OAuth2 is LIVE (Entries 013/014/015) — first login succeeded, `--check-imap-auth --account outlook` passes silently on refresh. **Parent Relationship:** Peer of P_800 (no sub-project relationship; peer within multi-project hub) **Root Path:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\`

***

## Table of Contents

1.  Project Overview
2.  Architecture & Tech Stack
3.  AI Behavior Rules & Constraints
4.  Folder Structure
5.  Approved Senders Registry
6.  Error Corrections Log
7.  Build Roadmap
8.  Enhancement Backlog
9.  Parameter Registry
10. Session Close & Resume Path

***

## Section 1 — Project Overview

### 1.1 Purpose

Extract ticker recommendations and trade signals from email newsletters stored in Thunderbird, deduplicate across sources, and produce a daily ranked output that feeds Tony's morning trading workflow. Once a message is successfully identified and extracted (at least one ticker found), it is moved to an `ExtractedNewsletterFolder` — a peer folder of Inbox — via a real IMAP move on the mail server (Phase 5.3, live 2026-07-14). All four accounts including Outlook are covered — Outlook authenticates via OAuth2/XOAUTH2 instead of Basic Auth (Entry 013), pending Tony's one-time browser consent. The system never sends, replies to, forwards, or deletes mail.

### 1.2 Goals

-   Scan approved-sender emails over a configurable lookback window (default 30 days)
-   Extract tickers, direction (long/short/watch), and entry/stop/target where provided
-   Dedupe signals and rank by source agreement
-   Write daily output to `data\daily\` as CSV (markdown + JSON come in Phase 5)
-   Optional: inject summary into Obsidian daily note via P_800's MCP bridge

### 1.3 In-Scope

-   Reading mail from Tony's four IMAP accounts in priority order (iCloud \> Gmail \> Outlook \> Yahoo) via Thunderbird's local mbox cache under the **m306ztzh.IETimport** profile
-   Parsing mbox files using Python's `mailbox` module
-   Whitelist-based sender filtering (source: `data\sender_sheet.csv`, currently 59 enabled)
-   Regex-based ticker extraction with extensible pattern list in `config.py`
-   Real IMAP move of successfully-extracted messages to `ExtractedNewsletterFolder` (peer of Inbox) for all four accounts including Outlook (Phase 5.3, live; Outlook via OAuth2/XOAUTH2, Entry 013, pending Tony's one-time login).

### 1.4 Out-of-Scope

-   Sending, replying to, forwarding, or deleting any email
-   Executing trades (P_805 produces a research list only)
-   **Category-based email triage and LLM summarization across the whole mailbox** — that is a separate future project, NOT P_805

### 1.5 Definitions & Acronyms

-   **Approved Sender** — email address on the whitelist in `data\sender_sheet.csv` with `enabled=true`
-   **Ticker Signal** — `TickerSignal` Pydantic record (ticker, direction, confidence, pattern, source, timestamp, subject, raw_context, account)
-   **Consensus Signal** — ticker appearing in ≥2 approved sources within the lookback window (Phase 4 concept). `sector_count` (added v2.2) is the number of distinct sender sectors among those sources — a proxy for how independent the agreeing sources actually are; untagged senders bucket as `unknown` and don't inflate the count.
-   **mbox** — Thunderbird's mail file format (one flat file per folder, no extension)
-   **Cashtag** — ticker prefixed with `$`, e.g. `$TSLA` or `$AAPL` (Twitter/Stocktwits convention)
-   **Pattern** — one entry in `config.TICKER_PATTERNS`, used by the extractor; new patterns are added by appending a dict to that list
-   **Lookback Window** — number of days back from today to scan (constant: `SCAN_DAYS` in `config.py`, default 30)
-   **LM Studio** — local LLM runtime, primary LLM per Tony's priority
-   **P_800** — peer project (Obsidian automation); P_805 may call its MCP bridge for output delivery

***

## Section 2 — Architecture & Tech Stack

### 2.1 Runtime

-   **Python:** `C:\Users\Trader\.conda\envs\p140\python.exe` (shared p140 conda env)
-   **OS:** Windows 11
-   **IDE:** VS Code

### 2.2 Languages

-   **Python** — primary, all core logic
-   **PowerShell** — only for filesystem probes; never used for mbox parsing

### 2.3 Libraries

-   `mailbox` (stdlib) — mbox parsing
-   `email` (stdlib) — header and body extraction
-   `html.parser` (stdlib) — HTML stripping
-   `pydantic` v2 — schemas for persistent file I/O
-   `pandas` — dedup, ranking, daily frame output (Phase 4+)
-   `requests` — LLM API calls (LM Studio or Claude) (Phase 3.5+ when LLM enrichment is added)
-   `obsidian_writers` — Obsidian vault automation (P_800 integration; KB mode)

`imaplib` and `keyring` are **NOT** used. The previous plan for direct IMAP access was shelved when the actual live Thunderbird profile was identified (see Entry 005).

### 2.4 Storage

-   Filesystem only. No database in Phase 1–3.
-   Daily output: `data\daily\YYYY-MM-DD_signals.csv` (Phase 3 produces this; Phase 5 will add `.md` and `.json`)
-   Logs: `python\logs\p805.log` (rotating, 5 MB × 3) and `python\logs\rejected.log` (rotating, 5 MB × 3)
-   Monthly rollups: `data\monthly\` (Phase 4+)

### 2.5 LLM Priority

Per Tony's global preference: **LM Studio first** (local, free, private), **Claude API second** (fallback when LM Studio unavailable or when reasoning quality matters — e.g., ambiguous extraction).

### 2.6 Code Architecture Standard

This project follows the Hub-wide **python-project-architecture** standard:

-   Code lives under `python\`, split into `domain\` (logic, no I/O), `infrastructure\` (all I/O), `application\` (orchestration).
-   All constants and paths live in `python\config.py`. Never hardcoded elsewhere.
-   Any persistent file read or write requires a Pydantic schema in `python\schemas.py`.
-   Hard limits: 300 lines per file, 50 lines per function.
-   All runtime output uses the `logging` module via `infrastructure\logging_setup.py`. Bare `print()` is permitted ONLY in `_legacy\` diagnostic scripts.

***

## Section 3 — Operating Rules

### 3.4 AI Behavior Rules & Constraints

**MUST:**

-   At session start in Claude Desktop, run `tool_search` for filesystem write capability. When writing or editing project code under `C:\Users\Trader\AI-Agent-Learning-Hub` or `D:\OneDrive`, use `filesystem:write_file` or `filesystem:edit_file` directly to the final project path. NEVER use `create_file` + `present_files` for project code (that's the download-and-manually-move pattern).
-   Use Python `mailbox.mbox()` for mbox parsing. Never split on `^From ` with regex, and never use `email.message_from_binary_file` with manual file seeking (Entry 001).
-   Respect the approved-sender whitelist from `data\sender_sheet.csv` (rows where `enabled=true`). Reject any sender not on the list. Also reject any sender whose From header contains a substring from `EXCLUDED_SENDER_SUBSTRINGS`.
-   Output unparsed signals with raw context when extraction is ambiguous — never fabricate tickers.
-   Split code per Tony's rules: 300 lines max per file, 50 lines max per function.
-   Put all constants, paths, thresholds, **and regex patterns** in `python\config.py`. No hardcoded values elsewhere.
-   State full Windows save path for every file produced (when files leave the writeable workspace).
-   Keep layers separated: `domain\` (logic) → `infrastructure\` (I/O) → `application\` (orchestration).

**MUST NOT:**

-   Send, reply to, forward, or delete any email.
-   Move messages to any folder other than `ExtractedNewsletterFolder`.
-   Move messages for any account in `config.MOVE_SKIP_ACCOUNTS` (empty by default as of Entry 013 — reserved for a future account if ever needed).
-   Handle IMAP credentials as plaintext anywhere — keyring only, never in config.py, never logged, never in any file.
-   Point `PROFILE_PATH` at `2slie5gz.default-release` — that profile's IMAP caches are stale (frozen at late 2019). The live profile is `m306ztzh.IETimport` (Entry 005).
-   Hard-code profile paths or any other configuration values outside `python\config.py`.
-   Call the Claude API when LM Studio is reachable unless explicitly overridden.
-   Write to any persistent file without a matching Pydantic schema in `python\schemas.py`.

***

## Section 4 — Folder Structure

```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\
├── docs\
│   └── P_805_SYSTEM_DOCUMENTATION.md         # this file (v2.2)
├── tasks\
│   └── todo.md                               # current-state checkout (Protocol F2)
├── P_805_daily_pipeline.bat                  # Phase 3→3.5→4→5.3 chain, 9:15 AM scheduled task
├── P_805_daily_pipeline_mcp.ps1               # MCP-safe launcher wrapper (Protocol C)
├── data\
│   ├── daily\
│   │   └── 2026-04-26_signals.csv            # first Phase 3 output (175 rows)
│   ├── monthly\                              # Phase 4+ rollups
│   └── sender_sheet.csv                      # AUTHORITATIVE whitelist (59 enabled)
└── python\
    ├── config.py                             # all paths, thresholds, patterns, keywords, IMAP/keyring settings
    ├── schemas.py                            # ApprovedSender, TickerSignal, RankedSignal, MovedMessage
    ├── cli.py                                # entry point: --phase 1|3|35|4|53, --check-imap-auth, --account
    ├── requirements.txt                      # pydantic, email-validator, python-dateutil, google-genai, python-dotenv, keyring, msal
    ├── domain\                               # pure logic, no I/O
    │   ├── __init__.py
    │   ├── headers.py                        # RFC 2047 header decoding
    │   ├── html_strip.py                     # HTML → text
    │   ├── sender_filter.py                  # extract address, approved-set membership
    │   ├── ticker_extractor.py               # find_tickers, infer_direction
    │   ├── ranker.py                         # rank_signals, majority_direction (Phase 4)
    │   └── message_selector.py               # select_candidates: which messages to IMAP-move (Phase 5.3)
    ├── infrastructure\                       # all I/O
    │   ├── __init__.py
    │   ├── logging_setup.py                  # main + reject loggers, rotating
    │   ├── mbox_body.py                      # extract plain-text body from message
    │   ├── mbox_reader.py                    # stdlib mailbox.mbox() wrapper
    │   ├── sender_sheet.py                   # load CSV → enabled set
    │   ├── daily_csv_reader.py               # load signals CSV → TickerSignal list (Phase 4)
    │   ├── moved_log.py                      # read/write moved_messages.csv audit log (Phase 5.3)
    │   ├── imap_mover.py                     # IMAP connect/move/check_auth — keyring LOGIN + outlook XOAUTH2 (Phase 5.3, Entry 013)
    │   └── oauth2_outlook.py                 # Outlook OAuth2 token cache lifecycle via msal (Entry 013)
    ├── application\                          # orchestration
    │   ├── __init__.py
    │   ├── phase1_scan.py                    # scan + sender filter + per-account summary
    │   ├── phase3_extract.py                 # scan + ticker extraction + daily CSV (now captures Message-ID)
    │   ├── phase35_enrich.py                 # LLM direction enrichment for unknown signals (Phase 3.5)
    │   ├── phase4_rank.py                    # load signals → consensus ranking → ranked CSV (Phase 4)
    │   ├── phase53_move.py                   # orchestrate real IMAP move to ExtractedNewsletterFolder (Phase 5.3)
    │   ├── imap_auth_check.py                # standalone connect+login+logout credential check
    │   └── p805_kb_writer.py                 # KB mode: ingest .eml from data/inbox/, summarize, write to P_800 vault
    ├── tests\                                # permanent regression tests (one per real post-build bug fix)
    │   ├── __init__.py
    │   ├── test_imap_mover.py                # Entry 010: dry-run must never call conn.create(); Entry 013: XOAUTH2 string format
    │   ├── test_message_selector.py          # Entry 011: skip_accounts excluded even with valid message_id
    │   └── test_oauth2_outlook.py            # Entry 013: OAuth token cache load/save/silent-refresh (mocked)
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

***

## Section 5 — Approved Senders Registry

### 5.1 Authoritative Source

The approved-sender whitelist is `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\data\sender_sheet.csv`.

### 5.2 CSV Schema

| Column          | Type           | Purpose                                                                                                                              |
|-----------------|----------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `email_address` | string         | Full sender address (e.g., `daily@wallstreetzen.com`)                                                                                |
| `sender_name`   | string         | Display name for reports                                                                                                             |
| `date_added`    | YYYY-MM-DD     | When sender was whitelisted                                                                                                          |
| `sector`        | string         | Sector tag; 25 of 59 populated as of v2.2 from real subject-line/raw_context evidence. Feeds `RankedSignal.sector_count` in Phase 4. |
| `enabled`       | `true`/`false` | Only `true` rows are scanned                                                                                                         |

### 5.3 Current State

As of 2026-04-26, the sheet contains **59 enabled senders**. The original 30 (after the broken `zacks.com` row was removed) plus 29 additions discovered by reviewing `python\logs\rejected.log` after the first Phase 2 run. Coverage now spans Zacks (3 sender variants), Wall Street Zen (2 variants), Big Trends (2), T3 Live (2), Stocktwits Daily Rip, Michael Burry, Motley Fool, McMillan Option Strategist, Earnings Whispers, Macro Notes, Moonshot Minute, Katusa Research, Kiyosaki, Acorn Wealth, 30 Second Trader, Stocks To Trade, Moby, plus the original Hedgeye, Chaikin, Analyst Ratings, Beehiiv newsletters, Substack newsletters, Tim Sykes, Trade Elite, Market Taker, Trading Pub, Daily Upside, Tradethirsty, Activate Trade, Freedom Income Options, and others.

### 5.4 Editing

Tony edits the CSV directly (Excel or text editor). No code change is needed to add, remove, or disable a sender — flip `enabled` to `false` to stop scanning without losing history.

### 5.5 Open Items

-   `sector` column: 25 of 59 populated (v2.2), from real evidence in signals history — the other 34 have produced no ticker signals yet, so there's nothing to categorize from. Tony to fill in as they accumulate history, or when he knows the newsletter's focus firsthand.
-   Some entries share a parent domain (e.g., multiple `@mail.beehiiv.com` senders) — consider a `parent_domain` column if dedup-by-publisher becomes useful. `alex@kryptonstreet.ccsend.com` / `gary@marketcrux.ccsend.com` are the concrete case that surfaced this (v2.2): same `.ccsend.com` platform, same tickers same days, near-identical copy — likely one publisher under two names. Currently handled by tagging both `momentum_promo` (weak-sector bucket) rather than a dedicated dedup pass.
-   The `expected_account` column proposed in v1.3 is no longer urgent because all four accounts scan in well under a second from local mbox.

***

## Section 6 — Error Corrections Log

### Entry 001 — mbox Regex Parse Dead-End

-   **Date:** 2026-04-17
-   **Severity:** High
-   **Context:** Extracted email blocks by splitting raw mbox content on `(?m)^From ` in PowerShell, and later iterated with `email.message_from_binary_file` + manual `seek()` on top-of-file `From_` detection in Python.
-   **Failure mode:** Multipart MIME boundaries and quoted-printable content contain lines starting with "From " that got misattributed as new messages.
-   **Correction:** Use Python's `mailbox.mbox()` parser exclusively.

### Entry 002 — Ignored python-project-architecture Skill

-   **Date:** 2026-04-20
-   **Severity:** Medium
-   **Context:** First drafted Phase 1 code with a `scripts\reader\read_mbox.py` monolith and a `config\parameters.json` runtime config file, ignoring the Hub-wide `python-project-architecture` skill.
-   **Correction:** Read `/mnt/skills/user/python-project-architecture/SKILL.md` at the start of any Python work.

### Entry 003 — Wrong Thunderbird Profile + Ignored ImapMail Directory

-   **Date:** 2026-04-20
-   **Severity:** High
-   **Context:** Configured `PROFILE_PATH = m306ztzh.IETimport` (mistakenly believed to be archive at the time) and scoped scanning to `<profile>\Mail\` only. First Phase 1 run produced 130+ Local Folders archive mbox files.
-   **Correction:** Switched to `2slie5gz.default-release` and walked both `Mail\` and `ImapMail\`. **Note:** This correction was itself wrong — see Entry 005.

### Entry 004 — Thunderbird Local Cache Believed Stale

-   **Date:** 2026-04-20
-   **Severity:** Project-blocking (at the time)
-   **Context:** Once the scanner was pointed at `2slie5gz.default-release\ImapMail\`, every IMAP inbox file appeared frozen in late 2019.
-   **Correction (at the time):** Project parked; Phase 1.5 (direct IMAP via `imaplib` + `keyring`) promoted to critical path.
-   **Correction (actual, see Entry 005):** This conclusion was wrong. The frozen mboxes were in the wrong profile.

### Entry 005 — Live Profile Was IETimport All Along (Reverses Entries 003 & 004)

-   **Date:** 2026-04-26
-   **Severity:** High (positive)
-   **Context:** Diagnostic listing of `m306ztzh.IETimport\ImapMail\` showed every INBOX file modified within the past hour and gigabytes of recent content. Running `check_ietimport_dates.py` confirmed: Yahoo, Gmail, iCloud, and Outlook INBOXes all current with newest messages from today.
-   **Failure mode:** Thunderbird appends `-1` to a server hostname when the same hostname appears across multiple account configs. The IETimport profile holds `imap.gmail-1.com` and `imap.mail.me-1.com` (the live caches); the default-release profile holds the un-suffixed versions (which are dormant). The naming made IETimport look like an "import archive" when it is in fact the live profile.
-   **Correction:** `PROFILE_PATH` set to `m306ztzh.IETimport`; `MBOX_FILES` dict updated with the `-1` hostnames for Gmail and iCloud. Phase 1.5 IMAP detour shelved entirely. `imaplib`, `keyring`, and app-specific passwords are no longer needed for this project.

### Entry 006 — Sandbox Download Pattern for Files That Belong in the Project

-   **Date:** 2026-04-26
-   **Severity:** Medium (recurring across many sessions)
-   **Context:** For multiple files during the early part of this session, code was generated via `create_file` to `/mnt/user-data/outputs/` and surfaced via `present_files`. Tony then had to manually move each file to its project location, and at one point overwrote the wrong file because the new version landed in `Downloads`.
-   **Failure mode:** Defaulting to the sandbox download pattern when filesystem MCP write tools were available the whole time.
-   **Correction:** Memory edit added (rule \#1): in Claude Desktop, always call `tool_search` for filesystem write capability at session start; for any project code under `C:\Users\Trader\AI-Agent-Learning-Hub` or `D:\OneDrive`, write directly to the final project path via `filesystem:write_file` or `filesystem:edit_file`. The sandbox `/mnt/user-data/outputs/` path is reserved for one-off diagnostics only.

### Entry 007 — MIME-Encoded Subject Headers in KB Mode Output

-   **Date:** 2026-05-25
-   **Severity:** High
-   **Context:** `p805_kb_writer.py` read raw email Subject and From headers via `msg.get("Subject")` without decoding, passing MIME-encoded values directly to Obsidian as note titles. Example: `=?UTF-8?B?8J+UkQ==?= Create your second brain.` (an encoded emoji + text) was slugified to `UTF-8B8JUKQ-CREATE-YOUR-SECOND-BRAIN.md`.
-   **Failure mode:** RFC 2047 encoded headers (common in international newsletters) landed un-decoded in KB frontmatter `title` field and filename slugs, breaking readability and searchability.
-   **Correction:** Import `decode_header_safe()` from `domain.headers` (already in use in Phase 3). Apply to both `Subject` and `From` headers before storing in KB record. `decode_header_safe()` uses Python's `email.header.decode_header()` + `make_header()` to safely convert encoded tokens to plain Unicode.

### Entry 008 — LM Studio Context Window Overflow on Longer Emails

-   **Date:** 2026-05-25
-   **Severity:** High
-   **Context:** KB mode summarization of longer newsletter emails (\~4000+ tokens) failed with `400 Bad Request` from LM Studio. Initial investigation pointed to wrong model name, timeout settings, and system prompt interference. Actual cause discovered via enhanced error logging: `{"error":"The number of tokens to keep from the initial prompt is greater than the context length (n_keep: 4162>= n_ctx: 4096)"}`.
-   **Failure mode:** deepseek-r1-distill-qwen-14b was loaded with `n_ctx=4096` (4K context window). Email body + system prompt = 4162 tokens. LM Studio rejected the request (400) before Truncate Middle could apply.
-   **Correction:** Reload the model with larger context length (`n_ctx=8192` or higher). Deepseek natively supports 128K+ context; 8K is well within spec and costs \~1–2GB additional VRAM per model instance. Updated `lm_studio_caller.py` error handler to capture and log LM Studio's actual error response body for faster future diagnosis. Also added regex to strip `<think>...</think>` blocks from reasoning-model outputs to prevent reasoning artifacts in KB note bodies.

### Entry 009 — config.py Drift Silently Broke Phase 3.5 Classification (Reverted Fixes from v1.8)

-   **Date:** 2026-07-14
-   **Severity:** High
-   **Context:** Session review of Phase 3.5 found `config.py` no longer matched the documented v1.8 state: `RAW_CONTEXT_CHARS`/`DIRECTION_WINDOW_CHARS` had reverted to the pre-fix values (80/120 instead of 500/500), `LM_STUDIO_MODEL` had reverted to `deepseek-r1-distill-qwen-14b` (the model already documented in Entry 008/Phase 3.5 notes as unusable for single-word classification), and `LLM_PRIMARY`/`LLM_FALLBACK` still read `"LM Studio"`/`"Claude API"`, not reflecting the actual Gemini-primary/LM-Studio-fallback code path. Root cause of the drift itself not identified (likely a git restore or manual edit outside a tracked session). Config was corrected first, but a smoke test then surfaced a **second, deeper bug**: `_get_lm_model_id()` in `lm_studio_caller.py` always returned `models[0]` from LM Studio's `/v1/models` response regardless of `config.LM_STUDIO_MODEL` — so even with the correct model configured, the actual classification calls were silently using whatever model LM Studio happened to load first (frequently the broken deepseek reasoning model). Additionally, `classify_direction()` passed `max_tokens=10` to Gemini, too small for `gemini-2.5-flash` to spend thinking tokens and still emit an answer.
-   **Failure mode:** Config-level fix alone was insufficient — the LM Studio fallback path had a code-level bug that ignored config entirely. Silent failure mode: no exception, just wrong/empty classifications defaulting to `unknown`.
-   **Correction:** `_get_lm_model_id()` now prefers `config.LM_STUDIO_MODEL` when present in the loaded model list (with partial-match fallback for quant-suffixed IDs), only falling back to `models[0]` with a warning if the configured model isn't loaded. `classify_direction()` max_tokens raised from 10 to 64 for both Gemini and LM Studio calls. `_parse()` now scans all whitespace-split tokens for a valid label instead of only checking the first token, tolerating chattier model responses. Verified via `Agentic-Hub-Governance\verify\run_this.py` smoke test — three unambiguous synthetic cases (long/short/watch) all classified correctly, empty-context case correctly returned `unknown`. PASS.

### Entry 010 — Dry-Run Mode Still Mutated the Server (Folder Creation)

-   **Date:** 2026-07-14
-   **Severity:** High
-   **Context:** First live dry-run of Phase 5.3 against real IMAP accounts showed `[icloud] created folder 'ExtractedNewsletterFolder'` in the log — a real server-side `CREATE` — even though `config.MOVE_DRY_RUN=True`. `_ensure_destination_folder()` had no awareness of dry-run mode; the dry-run check in `move_message()` only gated the later COPY/STORE/EXPUNGE steps.
-   **Failure mode:** "Dry run" was not actually side-effect-free. Only iCloud was reachable that run (see Entry 011), so the blast radius was one folder creation on one account, but the same gap would have applied everywhere.
-   **Correction:** `_ensure_destination_folder()` now takes an explicit `dry_run` parameter and returns early (logging "would create") instead of calling `conn.create()` when `dry_run=True`. Added `infrastructure.imap_mover.check_auth()` (connect+login+logout only, no folder/search/mail touch) plus `application/imap_auth_check.py` and `cli.py --check-imap-auth` so credentials can be verified any time without going near the move/folder logic at all. Permanent regression test: `tests/test_imap_mover.py` (fake IMAP connection, asserts `create()` is never called under `dry_run=True`, is called under `dry_run=False`).

### Entry 011 — Outlook/Microsoft 365 Rejects Basic Auth for IMAP (OAuth2-Only)

-   **Date:** 2026-07-14
-   **Severity:** Medium (scoped down, not blocking)
-   **Context:** Same live dry-run: `gmail` (10x, wrong-password-shaped error), `outlook` (1x), and `yahoo` (1x) all failed to authenticate. Gmail and Yahoo were credential issues (missing/incorrect app passwords — resolved separately by regenerating and re-storing via keyring). Outlook kept failing with a generic `AUTHENTICATE failed` even after regenerating the app password twice and confirming two-step verification was on. Checking Thunderbird's own account settings for that mailbox showed **Authentication method: OAuth2** — Thunderbird has never used a plain password for this account; it uses a browser-based OAuth2 token. This Microsoft 365 tenant has Basic Auth (plain IMAP `LOGIN`) disabled for this mailbox, which is a server-side policy independent of whether the app password itself is correct.
-   **Failure mode:** `imap_mover.py` only implements `IMAP4_SSL.login(username, password)` (Basic Auth / plain LOGIN). No app password, however correctly generated and stored, will ever authenticate against an account with Basic Auth disabled — the server rejects the *mechanism*, not the credential. The generic error message made this indistinguishable from a typo/paste error for several attempts.
-   **Correction:** Building OAuth2 support (`msal` + one-time browser consent + token cache/refresh, then `AUTHENTICATE XOAUTH2` instead of `LOGIN`) is real added scope — deferred, not built this session. Decision (confirmed with Tony): **skip** `outlook` **entirely for Phase 5.3 move.** Added `config.MOVE_SKIP_ACCOUNTS = {"outlook"}`; `domain.message_selector.select_candidates()` takes a `skip_accounts` param and excludes any signal from a skipped account before it can become a move candidate, regardless of a valid `message_id`. Phase 3 (mbox-based extraction) is unaffected — it reads Thunderbird's local cache, not live IMAP, so Outlook mail is still fully scanned and produces signals; those messages simply stay in Inbox instead of being auto-filed. Permanent regression test: `tests/test_message_selector.py`.

### Entry 012 — Windows-MCP PowerShell Transport Hangs on Piped Python Calls

-   **Date:** 2026-07-18
-   **Severity:** Medium (workflow friction, not a P_805 data bug)
-   **Context:** Testing the Phase 4 sector-weighting change, calls of the shape `& python.exe "cli.py" --phase 4 2>&1 | Select-Object -Last N` through the Windows-MCP PowerShell tool hung for the full \~4-minute MCP ceiling and returned a transport error ("No result received"), twice in a row, even though Phase 4 alone completes in under a second. A trivial `Get-Date` call through the same tool in between returned instantly, confirming the tool itself wasn't down — it was specifically piped output from a python subprocess that stalled the transport.
-   **Failure mode:** The blocking pipe (`| Select-Object -Last N`) appears to wait on the full buffered stdout/stderr stream from the child python process in a way the MCP transport doesn't handle cleanly, even for fast, short-lived commands. This is distinct from the already-documented Protocol C ceiling (long *bat* files exceeding 240s) — here the command itself was fast; the pipe pattern was the problem.
-   **Correction:** For short synchronous Python calls needing captured output, use `Start-Process -FilePath ... -ArgumentList ... -RedirectStandardOutput <file> -RedirectStandardError <file> -Wait`, then read the redirected files separately. Confirmed reliable in this session for a `--phase 4` smoke test. No permanent regression test (workflow pattern, not application code) — noted here and in `tasks\todo.md` for the next session.

### Entry 013 — Outlook OAuth2 IMAP Support (Reverses Entry 011)

-   **Date:** 2026-08-23
-   **Severity:** Medium (feature completion, not a bug)
-   **Context:** Entry 011 permanently skipped 'outlook' from Phase 5.3 move because the Microsoft 365 tenant rejects Basic Auth (plain IMAP LOGIN) entirely. Tony asked for Outlook included in the live move. Fix required real OAuth2 support: an Azure AD app registration (in Tony's own new tenant, `ajzoppoutlook.onmicrosoft.com` — his personal outlook.com account had no existing tenant of its own, discovered via the "Microsoft Services" tenant error when first attempting registration), `msal` for the token flow, and `AUTHENTICATE XOAUTH2` instead of `LOGIN` for the outlook account only.
-   **App registration gotchas hit live:** (1) Signing into entra.microsoft.com with a personal Microsoft account with no tenant of its own lands in Microsoft's internal "Microsoft Services" tenant (ID `f8cdef31-a31e-4b4a-93e4-5f571e91255a`), which has no directory Tony controls — fixed by signing up for a free Azure account, which auto-provisions a real tenant and makes the signing-in account Global Administrator. (2) The `IMAP.AccessAsUser.All` delegated permission is added via the **Microsoft Graph** API picker in the Entra admin center, not a separate "Office 365 Exchange Online" API (that API/service principal isn't present in a fresh consumer-only tenant) — but the actual OAuth scope requested at runtime is `https://outlook.office.com/IMAP.AccessAsUser.All`, not a `graph.microsoft.com` scope; the Graph picker is just where the admin center groups this permission for consent purposes. (3) Registering the app as "My organization only" (single tenant) blocks the personal `ajzopp@outlook.com` account from ever signing in — must be "Any Entra ID Tenant + Personal Microsoft accounts". (4) Switching that setting in the UI failed with `Property api.requestedAccessTokenVersion is invalid` — apps supporting personal accounts require API token version 2; fixed by editing the app Manifest directly (`api.requestedAccessTokenVersion: null` → `2`) before the Supported Accounts change would save.
-   **Correction:** `config.py` adds `OAUTH_ACCOUNTS = {"outlook"}`, `OUTLOOK_OAUTH_CLIENT_ID`, `OUTLOOK_OAUTH_AUTHORITY` (`https://login.microsoftonline.com/common` — required for the multitenant-plus-personal-accounts audience), `OUTLOOK_OAUTH_SCOPES`, `OAUTH_KEYRING_SERVICE`. New `infrastructure/oauth2_outlook.py` owns the MSAL token cache lifecycle: `get_access_token()` (silent refresh from a keyring-cached token, raises `OAuthError` with a clear next step if nothing is cached yet) and `interactive_login()` (one-time browser consent — Tony runs this himself via `cli.py --outlook-oauth-login`, never called from within the move/check_auth path, same principle as keyring app-password credentials). `infrastructure/imap_mover.py`'s `_connect()` now branches on `config.OAUTH_ACCOUNTS`: outlook builds an XOAUTH2 SASL string (`_xoauth2_string()`) from the cached token and calls `conn.authenticate("XOAUTH2", ...)`; all other accounts are unchanged (`conn.login()` with keyring app password). `config.MOVE_SKIP_ACCOUNTS` reverted to an empty set — Outlook is no longer excluded from Phase 5.3 move once Tony completes the one-time interactive login and a live `--check-imap-auth --account outlook` pass confirms it. Permanent regression tests: `tests/test_imap_mover.py` (`TestXOAuth2String` — exact wire format per Microsoft's spec) and `tests/test_oauth2_outlook.py` (token cache load/save/refresh, all mocked — no real network call, no browser). All 11 tests (2 pre-existing + 9 new) verified passing via PEH (`Agentic-Hub-Governance\verify\run_this_P805_20260823_094510.py`) before this entry was written. **Outlook is not yet live** — Tony must run `cli.py --outlook-oauth-login` once (browser consent) and confirm `--check-imap-auth --account outlook` passes before Phase 5.3 will actually move Outlook mail; until then it behaves as it did pre-fix (scanned, never filed).

### Entry 014 — Keyring Storage Too Small for MSAL Token Cache (Supersedes Entry 013 Storage Design)

-   **Date:** 2026-08-23
-   **Severity:** High (broke the first live login attempt outright)
-   **Context:** Tony ran `cli.py --outlook-oauth-login` for the first time. Browser consent succeeded, but the process then crashed writing the token to keyring: `win32ctypes.pywin32.pywintypes.error: (1783, 'CredWrite', 'The stub received bad data')`. Windows Credential Manager caps a single generic credential's secret blob at roughly 1280–2560 characters; a real MSAL token cache for a personal Microsoft account (access token + refresh token + ID token + account metadata, all JSON) routinely exceeds that — `IMAP_USERNAMES`/app-password credentials never hit this because a password is tiny by comparison.
-   **Failure mode:** Entry 013's `_load_cache()`/`_save_cache()` design stored the entire serialized cache as one `keyring.set_password()` call. Worked fine against every mocked test (mocks don't enforce the OS's real size cap), failed immediately on the first real write.
-   **Correction:** Replaced keyring storage with `msal-extensions`' `FilePersistenceWithDataProtection` — a DPAPI-encrypted cache file at `config.OAUTH_CACHE_PATH` (`python\.secrets\outlook_oauth_cache.bin`), tied to Tony's Windows login, same security property as Credential Manager (only his account can decrypt it) with no practical size limit. This is Microsoft's own documented persistence pattern for MSAL Python public-client apps. `oauth2_outlook.py` simplified: `_load_cache()`/`_save_cache()` removed entirely (msal-extensions handles read/write transparently on every token operation); replaced with a single `_build_cache()` returning a `PersistedTokenCache`. `config.py`'s `OAUTH_KEYRING_SERVICE`/keyring-chunking constants removed, replaced with `OAUTH_CACHE_DIR`/`OAUTH_CACHE_PATH`. `requirements.txt` adds `msal-extensions>=1.2.0` (installed into p140). Regression tests rewritten: `tests/test_oauth2_outlook.py` `TestBuildCache` locks in the DPAPI-file construction and parent-directory creation — one test (`test_creates_parent_directory`) initially failed with `AttributeError: 'WindowsPath' object attribute 'mkdir' is read-only` because `Path` uses `__slots__` and can't be patched via `patch.object()` on an instance; fixed by patching the class method (`patch("pathlib.Path.mkdir")`) instead. All 10 tests pass (one fewer than Entry 013's 11 — the keyring chunk-count/round-trip tests no longer apply and were replaced by the two `TestBuildCache` tests).
-   **Provenance note:** This fix was found already implemented on disk (config.py, oauth2_outlook.py, requirements.txt all consistent) when the session went to patch the bug — written by a separate process/session, not this chat. Verified rather than assumed correct: read all three files, ran the full test suite, found and fixed the one real test bug above, confirmed 10/10 passing before logging this entry. Outlook is **still not live** — no `.secrets\outlook_oauth_cache.bin` exists yet on disk, meaning the first login has not yet succeeded end-to-end with this new storage. Tony needs to re-run `cli.py --outlook-oauth-login`.

### Entry 015 — --outlook-oauth-login Ran Silently, No Success/Failure Message (Missing Logging Setup)

-   **Date:** 2026-08-23
-   **Severity:** Low (cosmetic — the login itself worked, Tony just couldn't tell)
-   **Context:** Tony re-ran `cli.py --outlook-oauth-login` after Entry 014's DPAPI storage fix. Browser consent completed (confirmed via the Microsoft success page), but the terminal printed nothing at all — no success message, no error. Checked the cache file directly: `.secrets\outlook_oauth_cache.bin` existed, 6.2KB, timestamped to the exact run — the login had actually succeeded.
-   **Failure mode:** Every other `cli.py` command routes through an `application/` wrapper that calls `infrastructure.logging_setup.configure_logging()` before doing anything else (documented convention in `logging_setup.py`'s own docstring: "Call configure_logging() once at the top of any application entry point"). `--outlook-oauth-login` was wired directly to `infrastructure.oauth2_outlook.interactive_login()` with no wrapper — the only cli.py path that skipped it. With no handler configured on the `p805` logger, `logger.info()` calls are silently dropped (Python's logging module has no default output for INFO without an explicit handler).
-   **Correction:** Added `application/outlook_oauth_login.py` (new, thin wrapper — `run()` calls `configure_logging()` then `oauth2_outlook.interactive_login()`), matching the exact pattern `imap_auth_check.py` already uses. `cli.py` now imports `run` from the new application module instead of importing `interactive_login` directly from infrastructure. Verified: re-ran `--check-imap-auth --account outlook` after the fix — PASS, output landed correctly (in stderr, which is where Python's `logging.StreamHandler` writes by default — not a bug, just where console logs go in this project). Also verified, while investigating: `msal_extensions.PersistedTokenCache.modify()` (read from the installed package source directly, not assumed) automatically reloads and flushes to the DPAPI file on every token operation — confirmed the silent-refresh path in `get_access_token()` has no save gap; no code change needed there.

### Entry 016 — Task Scheduler Silent 32-Day Gap (Interactive Logon Requires Active Session)

-   **Date:** 2026-09-06 (discovery date; the underlying gap spans 2026-07-22 through 2026-08-23)
-   **Severity:** High (32 days of zero pipeline output, undetected for over a month)
-   **Context:** Live `Get-ScheduledTaskInfo` and a `data\daily\` folder listing (2026-09-06) showed the last signals CSV before a long gap was `2026-07-22_signals.csv`, then nothing until `2026-08-23_signals.csv` — a silent 32-day gap. `Get-ScheduledTaskInfo` showed `LastTaskResult: 0` (success) for today's run, and every run from 2026-08-23 through 2026-09-06 has produced a CSV daily, confirmed live via `pipeline_runs.log`'s tail (today's run: Phase 3 = 9 signals, Phase 3.5 enrichment ran, Phase 4 found 0 consensus tickers, Phase 5.3 moved 5 messages — all phases reported SUCCESS).
-   **Failure mode:** `P_805_Daily_Pipeline_915AM` is registered with **Interactive logon** (required for keyring access, per the 2026-07-18 v2.1 entry). This logon type only fires the task if Tony is actually logged into an active Windows session at 9:15 AM — if the machine is off, locked, or logged out at that moment, Task Scheduler does not run the task at all, and surfaces no error, no failure entry, nothing to alert on. No other candidate explanation fits: config, code, and network all functioned correctly both immediately before 2026-07-22 and immediately after 2026-08-23, with no changes logged in between. Not confirmed against Task Scheduler's own run-history log (does not retain history that far back by default) — this is the most likely explanation given everything else checked out, not a certainty.
-   **Correction:** Not yet built — documentation only this entry. Two options for a future session: (1) move the task off Interactive logon to a service/S4U logon type that doesn't require an active session — untested whether keyring (Windows Credential Manager, DPAPI-backed) access survives that logon context change, needs a real trial, not a drop-in swap; (2) lower-risk alternative: a lightweight daily check (e.g., confirm `data\daily\<today>_signals.csv` exists by 9:30 AM) that alerts Tony instead of fixing the logon requirement itself. No code changed this entry.

***

## Section 7 — Build Roadmap

**Phase 1 — Reader: ✅ COMPLETE (2026-04-26)** Walks all four IMAP INBOX caches under the live profile, prints sender + subject + date for every message in the lookback window. Successful end-to-end run: 1,209 messages in file across four accounts, 1,174 in 30-day window.

**Phase 1.5 — Direct IMAP: ❌ SHELVED (2026-04-26)** Was promoted from backlog to critical path on 2026-04-20 under the false belief that local cache was stale. Entry 005 reversed that. Direct IMAP is no longer on the path. Could be revived in the future if the desktop client is removed from the workflow, but no current need.

**Phase 2 — Approved Sender Filter + Logging Migration: ✅ COMPLETE (2026-04-26)** Console output replaced by main + reject loggers (rotating files at `python\logs\p805.log` and `python\logs\rejected.log`). Sender filter loads `data\sender_sheet.csv`, validates rows through `ApprovedSender` Pydantic schema, returns lowercased enabled-set. Result on first run: 240 of 1,174 in-window messages approved (20.4%) across 59 enabled senders.

**Phase 3 — Ticker Extraction: ✅ COMPLETE (2026-04-26)** Regex extractor with four configured patterns (`exchange_paren`, `cashtag`, `wsz_url`, `bare_paren`). Pattern list lives in `config.TICKER_PATTERNS` as a list of dicts; adding a new pattern is a one-line edit with no domain-code changes. Direction inference is keyword-based via `config.DIRECTION_KEYWORDS`. First run produced 175 rows in `data\daily\2026-04-26_signals.csv` covering \~140 unique tickers across all four accounts. Scheduled to run daily at 9:15 AM via Windows Task Scheduler.

**Phase 3.5 — LLM Direction Enrichment: ✅ COMPLETE (2026-06-14)** Runs after Phase 3, before Phase 4. Loads today's signals CSV, calls LM Studio for every `direction=unknown` row, rewrites CSV in-place. Non-unknown rows are never touched. Production run: 203 of 275 unknowns resolved (74%); 72 remain unknown (genuinely ambiguous context). Key learnings: DeepSeek R1 distill models (any size) consume all tokens on reasoning and return empty `content` — unusable for single-word classification. **Qwen2.5-7B-Instruct (bartowski Q4_K_S)** is the correct model — returns answers directly in `content` with no reasoning overhead. `RAW_CONTEXT_CHARS` must be ≥300 for reliable classification; raised to 500 alongside `DIRECTION_WINDOW_CHARS`. Synonym mapping in parser handles model returning `bullish`/`bearish`/`neutral` instead of `long`/`short`/`watch`. Direction majority vote in Phase 4 is correct behavior when sources disagree.

**Phase 4 — Aggregation & Ranking: ✅ COMPLETE (2026-06-14)** Dedup across sources, consensus filter (`CONSENSUS_THRESHOLD=2`), rank by source count descending then ticker ascending. Output: `data\daily\YYYY-MM-DD_ranked.csv` (one row per consensus ticker, columns: ticker, source_count, sources, direction, first_seen, last_seen). New modules: `domain\ranker.py`, `infrastructure\daily_csv_reader.py`, `application\phase4_rank.py`. First run: 347 raw signals → 20 consensus tickers. Top hits: ADBE (3 sources, short), SPCX (3 sources, long). 12 of 20 returned direction=unknown — expected until Phase 3.5 LLM enrichment is added.

**Phase 5 — Writer: ⏳ PARTIALLY LIVE (2026-05-25)** KB mode (`--kb-mode summary|full`) complete and producing Obsidian notes from `.eml` files in `data\inbox\`. Integrates with P_800's `obsidian_writers` package and LM Studio for optional email summarization. Each email → one note with title (decoded subject), frontmatter (source, date, tags, ticker relevance), and body (full or summarized per CLI flag). Moves to `trading_journal\KnowledgeBase\` via P_800 interface. CSV output (Phase 5.1) and `.md`/`.json` alongside CSV (Phase 5.2) are future items.

**Phase 5.3 — IMAP Move to ExtractedNewsletterFolder: ✅ COMPLETE and LIVE (2026-07-14); Outlook added 2026-08-23, pending Tony's first login** Real server-side move (not local mbox editing) of every message that produced at least one `TickerSignal`, via `COPY` + `STORE \Deleted` + `EXPUNGE` over `imaplib`. Credentials for iCloud/Gmail/Yahoo via `keyring` only (service `p805_imap`), never in config or logs; Outlook via OAuth2 XOAUTH2 (Entry 013) — cached token via keyring under a separate service, never a plaintext file. Destination folder auto-created per account if missing. Idempotent via `data\moved_messages.csv` audit log — already-`moved` messages are never retried; `dry_run` log entries don't block a later real attempt. Safety default `config.MOVE_DRY_RUN` rehearsed the full flow before going live (Entry 010 caught and fixed a dry-run-still-mutates-server bug in folder creation). `outlook` was permanently excluded via `config.MOVE_SKIP_ACCOUNTS` from 2026-07-14 to 2026-08-23 (Entry 011, Basic Auth rejected server-side) — Entry 013 built OAuth2 support and reverted the skip; Outlook won't actually move mail until Tony runs `cli.py --outlook-oauth-login` once and a live `--check-imap-auth --account outlook` pass confirms it. Standalone credential check: `cli.py --check-imap-auth [--account X]` (connect+login+logout only, safe to run any time). First live run (iCloud/Gmail/Yahoo, 2026-07-14): **18 moved** (8 icloud + 10 gmail), **1 not-found** (yahoo — message left INBOX between Phase 3 scan and move attempt, benign), **0 failed**. Tony set a 10-day retention policy on the destination folder in Thunderbird for icloud/gmail (yahoo pending first real content).

***

## Section 8 — Enhancement Backlog

-   ~~Direct IMAP pull (remove Thunderbird dependency)~~ — SHELVED (2026-04-26, Entry 005). Local cache works.
-   ~~Expand~~ `DIRECTION_KEYWORDS` ~~with newsletter-typical verbs~~ — DONE (2026-06-14). Added ripped, soared, popped, cratered, tumbled, tanked, jumped, climbed, plunged and others.
-   ~~Fix CSV encoding for Excel~~ — DONE (2026-06-14). `phase3_extract.py:write_csv` now uses `encoding="utf-8-sig"`.
-   ~~LLM-based direction & conviction scoring (LM Studio first, fall back to Claude API)~~ — DONE (2026-06-14) as Phase 3.5. Qwen2.5-7B-Instruct via LM Studio; 74% unknown resolution rate.
-   Sentiment analysis on subject lines
-   Historical signal performance tracking vs. actual ticker moves (hooks into P_010 data)
-   Populate `sector` column in `sender_sheet.csv` for sector-weighted consensus — CODE DONE (2026-07-18) as part of v2.2: `RankedSignal.sector_count`, `load_sender_sectors()`, ranker/phase4 wiring all live. DATA partially done: 25 of 59 senders tagged from real evidence; 34 remain (no ticker-producing history yet). See Section 5.5.
-   Add a `parent_domain` column to `sender_sheet.csv` for dedup-by-publisher — concrete case identified 2026-07-18: `alex@kryptonstreet.ccsend.com` / `gary@marketcrux.ccsend.com` look like the same publisher. Not yet built; see Section 5.5.
-   ~~Stocktwits Daily Rip per-sender ticker cap~~ — DONE (2026-06-14). `SENDER_MAX_TICKERS` in config.py; Stocktwits Daily Rip capped at 5 tickers/email.
-   BigTrends Sunday Night Trader pattern check (deferred 2026-04-26) — only worth doing if Phase 4 shows we're missing structured picks from that source
-   Gmail MCP connector as alternative Gmail source (parallel path, not replacement)
-   WhatsApp export ingestion path shared with P_800 (reuse extractor layer)

***

## Section 11 — Parameters

### 11.4 Parameter Registry

All parameters live as constants in `python\config.py`. This table is the canonical list; the code file is the source of truth.

| Parameter                                  | Value                                                  | Notes                                                                                                                                                                     |
|--------------------------------------------|--------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `HUB_ROOT`                                 | `C:\Users\Trader\AI-Agent-Learning-Hub`                | Only hardcoded path allowed per architecture standard                                                                                                                     |
| `SCAN_DAYS`                                | `30`                                                   | Default lookback window                                                                                                                                                   |
| `THUNDERBIRD_ROOT`                         | `C:\Users\Trader\AppData\Roaming\Thunderbird\Profiles` |                                                                                                                                                                           |
| `PROFILE_PATH`                             | `m306ztzh.IETimport`                                   | Live profile (Entry 005)                                                                                                                                                  |
| `PROFILE_ROOT` / `MAIL_ROOT` / `IMAP_ROOT` | derived                                                |                                                                                                                                                                           |
| `MBOX_FILES`                               | dict, 4 entries                                        | iCloud / Gmail / Outlook / Yahoo INBOX paths under `IMAP_ROOT`. Gmail and iCloud use `-1` hostname suffix.                                                                |
| `IMAP_ACCOUNT_ORDER`                       | `["icloud", "gmail", "outlook", "yahoo"]`              | Trading-info priority                                                                                                                                                     |
| `EXTRACTED_FOLDER_NAME`                    | `ExtractedNewsletterFolder`                            | Phase 5+                                                                                                                                                                  |
| `EXTRACTED_FOLDER_AUTOCREATE`              | `True`                                                 |                                                                                                                                                                           |
| `SENDER_SHEET`                             | `<PROJECT>\data\sender_sheet.csv`                      | Authoritative approved-sender list                                                                                                                                        |
| `DATA_DAILY_DIR`                           | `<PROJECT>\data\daily`                                 | Phase 3 output location                                                                                                                                                   |
| `DATA_MONTHLY_DIR`                         | `<PROJECT>\data\monthly`                               | Phase 4+ rollups                                                                                                                                                          |
| `LOGS_DIR`                                 | `<PROJECT>\python\logs`                                | Run logs                                                                                                                                                                  |
| `LOG_FILE`                                 | `LOGS_DIR\p805.log`                                    | Main log, rotating 5 MB × 3                                                                                                                                               |
| `REJECT_LOG_FILE`                          | `LOGS_DIR\rejected.log`                                | Rejected senders, rotating 5 MB × 3                                                                                                                                       |
| `LOG_LEVEL_CONSOLE`                        | `"INFO"`                                               |                                                                                                                                                                           |
| `LOG_LEVEL_FILE`                           | `"DEBUG"`                                              |                                                                                                                                                                           |
| `LOG_MAX_BYTES`                            | `5_000_000`                                            |                                                                                                                                                                           |
| `LOG_BACKUP_COUNT`                         | `3`                                                    |                                                                                                                                                                           |
| `TICKER_PATTERNS`                          | list of 4 dicts                                        | `exchange_paren`, `cashtag`, `wsz_url`, `bare_paren` — extension point: append new dicts here                                                                             |
| `BARE_PAREN_BLOCKLIST`                     | set, \~50 entries                                      | Common parenthesized non-tickers (CEO, USA, PDF, etc.)                                                                                                                    |
| `DIRECTION_KEYWORDS`                       | dict (long/short/watch → keyword lists)                | Extension point: edit lists in config                                                                                                                                     |
| `DIRECTION_WINDOW_CHARS`                   | `500`                                                  | Context window for direction inference (raised from 120, 2026-06-14)                                                                                                      |
| `RAW_CONTEXT_CHARS`                        | `500`                                                  | Stored on each `TickerSignal.raw_context` (raised from 80, 2026-06-14)                                                                                                    |
| `EXCLUDED_SENDER_SUBSTRINGS`               | `["impens", "andreessen", "gaud"]`                     | Substring match against From header                                                                                                                                       |
| `DAILY_OUTPUT_CSV`                         | `"{date}_signals.csv"`                                 | Phase 3 output filename pattern                                                                                                                                           |
| `CONSENSUS_THRESHOLD`                      | `2`                                                    | Min source count for consensus signal (Phase 4+)                                                                                                                          |
| `LLM_PRIMARY`                              | `"LM Studio"`                                          | localhost                                                                                                                                                                 |
| `LLM_FALLBACK`                             | `"Claude API"`                                         |                                                                                                                                                                           |
| `GEMINI_MODEL`                             | `"gemini-2.5-flash"`                                   | Gemini primary for classify_direction and summarize; key loaded from python.env                                                                                           |
| `SENDER_MAX_TICKERS`                       | `{"newsletter@thedailyrip.stocktwits.com": 5}`         | Per-sender cap on tickers per email; checked in phase3_extract.py after \_best_per_ticker()                                                                               |
| `LM_STUDIO_URL`                            | `"http://127.0.0.1:1234/v1"`                           | OpenAI-compatible endpoint                                                                                                                                                |
| `LM_STUDIO_MODEL`                          | `"qwen2.5-7b-instruct"`                                | Phase 3.5 direction classification (bartowski Q4_K_S). KB summarization uses deepseek-r1-distill-qwen-14b at n_ctx=8192 — swap model in LM Studio before running KB mode. |
| `LM_STUDIO_TEMP`                           | `0.3`                                                  | Lower temp for focused summaries                                                                                                                                          |
| `LM_STUDIO_MAX_TOKENS`                     | `300`                                                  | Output limit per summary                                                                                                                                                  |
| `LM_STUDIO_TIMEOUT`                        | `60`                                                   | Request timeout in seconds                                                                                                                                                |
| `KB_MODE_PATTERN_FULL`                     | `r"--full\.eml$"`                                      | Filename pattern for full-text ingestion                                                                                                                                  |
| `KB_MODE_PATTERN_SUMMARIZE`                | `r"--summarize\.eml$"`                                 | Filename pattern for summarization                                                                                                                                        |
| `PROJECT_ROOT`                             | `<HUB_ROOT>\projects\P_805_Email_Trade_Extractor`      | KB mode data dir                                                                                                                                                          |
| `INBOX_PATH`                               | `<PROJECT_ROOT>\data\inbox`                            | .eml files staged here for KB ingestion                                                                                                                                   |
| `KEYRING_SERVICE_NAME`                     | `"p805_imap"`                                          | Phase 5.3; credentials retrieved via `keyring.get_password(KEYRING_SERVICE_NAME, account)`, never stored in any file                                                      |
| `IMAP_SERVERS`                             | dict, 4 entries                                        | (host, port) per account, port 993 for all                                                                                                                                |
| `IMAP_USERNAMES`                           | dict, 4 entries                                        | Real login addresses — not secret, the password is what's in keyring                                                                                                      |
| `MOVE_DRY_RUN`                             | `False` (as of 2026-07-14, was `True`)                 | Safety flag; `True` = connect+search+log only, no mutation                                                                                                                |
| `MOVE_SKIP_ACCOUNTS`                       | `set()`                                                | Empty as of Entry 013 (was `{"outlook"}` under Entry 011)                                                                                                                 |
| `IMAP_CONNECT_TIMEOUT`                     | `30`                                                   | Seconds                                                                                                                                                                   |
| `MOVED_LOG_PATH`                           | `<PROJECT_ROOT>\data\moved_messages.csv`               | Phase 5.3 audit/idempotency log                                                                                                                                           |
| `OAUTH_ACCOUNTS`                           | `{"outlook"}`                                          | Accounts using XOAUTH2 instead of keyring LOGIN (Entry 013)                                                                                                               |
| `OUTLOOK_OAUTH_CLIENT_ID`                  | `"20df0d61-7668-4b75-a778-b67d22fe841b"`               | Not secret; Azure AD app in Tony's own tenant `ajzoppoutlook.onmicrosoft.com`                                                                                             |
| `OUTLOOK_OAUTH_AUTHORITY`                  | `"https://login.microsoftonline.com/common"`           | Multitenant + personal accounts audience                                                                                                                                  |
| `OUTLOOK_OAUTH_SCOPES`                     | `["https://outlook.office.com/IMAP.AccessAsUser.All"]` | Legacy-protocol resource scope, not a Graph scope despite being added via the Graph permission picker                                                                     |
| `OAUTH_KEYRING_SERVICE`                    | `"p805_oauth_outlook"`                                 | Serialized MSAL token cache stored here via keyring, never a plaintext file                                                                                               |

***

## Section 12 — Session Close & Resume Path

### 12.1 Status at Close (2026-08-23, v2.3)

Outlook OAuth2 IMAP support built (Entry 013): `infrastructure/oauth2_outlook.py` (new), `infrastructure/imap_mover.py` (XOAUTH2 branch), `config.py` (OAuth block), `cli.py` (`--outlook-oauth-login` flag), two new/extended test files, 11/11 tests passing via PEH. **Not yet live** — Tony still needs to run `cli.py --outlook-oauth-login` once (one-time browser consent) and confirm `--check-imap-auth --account outlook` passes before Phase 5.3 will actually move Outlook mail. Independent Review still required before WO-P805-E2.001 can move OWNER_DONE → CLOSED.

### 12.0c Prior Status at Close (2026-07-18, v2.2)

Phases 1, 2, 3, 3.5, 4, and 5.3 complete and live, fully wired to run automatically every morning. Phase 4 now computes `sector_count` for cross-sector consensus weighting; `sender_sheet.csv` has 25 of 59 senders tagged. Phase 5 KB mode partially live (as before).

### 12.0 Prior Status at Close (2026-07-18, v2.1 same day)

Task Scheduler chain built and registered this session — see Section 7.

### 12.0b Prior Status at Close (2026-07-14, v2.0)

Phases 1, 2, 3, 3.5, 4, and 5.3 are complete and live. Phase 5 KB mode partially live (as before). Phase 5.3 (IMAP move) built and taken live that session — see Section 7 and Entries 010/011.

What works end-to-end:

-   `python cli.py` — Phase 1 scan with per-account summary
-   `python cli.py --phase 1 --account icloud` — single-account scan
-   `python cli.py --phase 3` — full extraction → daily signals CSV (scheduled 9:15 AM), now captures Message-ID per signal
-   `python cli.py --phase 35` — LLM direction enrichment on today's signals CSV
-   `python cli.py --phase 4` — consensus ranking → ranked CSV, now includes `sector_count` column (v2.2)
-   `python cli.py --phase 53` — real IMAP move of extracted messages to ExtractedNewsletterFolder (icloud/gmail/yahoo; outlook skipped). `config.MOVE_DRY_RUN` gates real vs. rehearsal.
-   `python cli.py --check-imap-auth [--account X]` — connect+login+logout credential check only, safe any time
-   `python cli.py --kb-mode summary` — ingest .eml files, summarize via LM Studio (load deepseek-r1-distill-qwen-14b at n_ctx=8192 first), write KB notes to Obsidian vault
-   `python cli.py --kb-mode full` — ingest .eml files, write full-text KB notes
-   `python -m unittest discover -s tests -v` — permanent regression suite (Entries 010, 011)
-   `P_805_daily_pipeline.bat` — chains Phase 3 → 3.5 → 4 → 5.3, abort-on-failure for 3/4, continue-on-failure for 3.5/5.3, logs to `python\logs\pipeline_runs.log`
-   `P_805_daily_pipeline_mcp.ps1` — MCP-safe detached launcher wrapper for the bat (Protocol C); note: launched via `Start-Process` directly in this session after the wrapper produced no status file on first attempt — `Invoke-HubBat` in the shared launcher needs a look before relying on it again
-   Scheduled task `P_805_Daily_Pipeline_915AM` — daily 9:15 AM, Interactive logon (keyring needs user context), Limited run level, State: Ready
-   All runs go through `infrastructure\logging_setup.py` for consistent log handling
-   `data\sender_sheet.csv` — single source of truth for whitelist (59 enabled rows)
-   `python\config.py` — single source of truth for all paths, thresholds, patterns, LLM settings, IMAP/keyring settings

**Important model note:** `LM_STUDIO_MODEL` is `qwen2.5-7b-instruct` (Phase 3.5). KB mode (`--kb-mode`) requires swapping to `deepseek-r1-distill-qwen-14b` at `n_ctx=8192` in LM Studio before running.

**Credential note:** IMAP passwords for icloud/gmail/yahoo live only in Windows Credential Manager via `keyring` (service `p805_imap`), set with `keyring.set_password('p805_imap', '<account>', '<app password>')` run by Tony directly at his terminal — never through Claude, never in any file. Outlook (as of Entry 013) uses OAuth2 instead — a cached MSAL token in keyring (service `p805_oauth_outlook`), obtained via a one-time browser login Tony runs himself (`cli.py --outlook-oauth-login`), never a password Claude or Tony types anywhere.

What's queued (in priority order):

1.  **~~Schedule Phase 3.5, Phase 4, and Phase 5.3.~~** DONE (2026-07-18). `P_805_Daily_Pipeline_915AM` registered and verified with a full live run.
2.  **~~Sector weighting (code).~~** DONE (2026-07-18, v2.2). `sector_count` live in Phase 4 output.
3.  **~~Outlook OAuth2 first login.~~** DONE (2026-08-23, Entry 015). First browser login succeeded, `--check-imap-auth --account outlook` passes silently on refresh. This line was left un-struck after Entry 015 confirmed it — corrected 2026-09-06.
4.  **Sector weighting (data).** 34 of 59 senders still untagged — fill in as they accumulate ticker-producing history, or when Tony knows the newsletter's focus firsthand.
5.  **parent_domain dedup.** New backlog item from 2026-07-18 — KryptonStreet/MarketCrux look like one publisher under two names. Not yet built.
6.  **~~Yahoo retention policy.~~** DONE (2026-09-06). 10-day "Delete messages more than 10 days old" applied to Yahoo's `ExtractedNewsletterFolder`, matching icloud/gmail.

### 12.2 Session Identifier for Resume Reference

-   Chat on 2026-08-23 (v2.3) covered: Outlook OAuth2 IMAP support (Entry 013), per Tony's request to include Outlook in the live move. Walked Tony through Azure AD app registration live, in-chat, screenshot by screenshot — hit and resolved three real gotchas: (1) a personal outlook.com account with no tenant of its own lands in Microsoft's internal "Microsoft Services" tenant, fixed by signing up for a free Azure account; (2) `IMAP.AccessAsUser.All` is added via the Microsoft Graph permission picker, not a separate Exchange Online API (which isn't present in a fresh consumer tenant) — confirmed via web search against current Microsoft documentation; (3) enabling personal-account sign-in failed with `api.requestedAccessTokenVersion is invalid`, fixed by editing the app manifest directly (`null` → `2`). Built `infrastructure/oauth2_outlook.py` (new, MSAL token cache lifecycle), branched `infrastructure/imap_mover.py._connect()` on `config.OAUTH_ACCOUNTS` for XOAUTH2, added `cli.py --outlook-oauth-login` (Tony-run-only, never called from within the move path — same principle as keyring credentials), extended `tests/test_imap_mover.py` and added `tests/test_oauth2_outlook.py` (11 tests total, all mocked, no real network/browser). Installed `msal` into p140. Verified all 11 tests passing via PEH (`Agentic-Hub-Governance\verify\run_this_P805_20260823_094510.py`) before writing this doc update. `config.MOVE_SKIP_ACCOUNTS` reverted to empty. Outlook is not yet live in production — Tony still needs to run the one-time interactive login himself.
-   Chat on 2026-07-18 (v2.2) covered: sector-weighted consensus. Added `RankedSignal.sector_count`, `infrastructure.sender_sheet.load_sender_sectors()`, wired `domain.ranker.build_ranked_signals()` and `application.phase4_rank.py` to compute distinct-sector count per ticker. Populated `sector` for 25 of 59 senders in `sender_sheet.csv` from real subject-line/raw_context evidence pulled from 4 days of signals history on disk — explicitly declined to guess sectors from sender names/domains alone (would have fabricated categorization data). Flagged `alex@kryptonstreet.ccsend.com` / `gary@marketcrux.ccsend.com` as likely the same publisher (same platform, same tickers same days, near-identical copy) and tagged both `momentum_promo` rather than opening a full parent_domain dedup pass — confirmed working when GIPR came back `sector_count=1` for that pair in the live test. Hit a real bug during testing: `PermissionError` writing the ranked CSV because Tony had it open in Excel — not a code defect, resolved by closing the file. Also hit and logged Entry 012: Windows-MCP PowerShell hangs on piped python output even for fast commands; `Start-Process -Wait` with redirected output files is the reliable workaround.
-   Chat on 2026-07-18 (v2.1, earlier same day) covered: Task Scheduler wiring for the full daily pipeline. Built `P_805_daily_pipeline.bat` (Phase 3→3.5→4→5.3, abort-on-failure for 3/4, continue-on-failure for 3.5/5.3) and `P_805_daily_pipeline_mcp.ps1` (MCP-safe wrapper). Discovered no P_805 task previously existed in Task Scheduler (only P_010 tasks were registered). Ran the pipeline live end to end: Phase 3 = 205 signals, Phase 3.5 = complete despite transient Gemini 503s (LM Studio fallback covered them), Phase 4 = ranked CSV, Phase 5.3 = Moved=57 DryRun=0 NotFound=6 Failed=0. Registered `P_805_Daily_Pipeline_915AM` (daily 9:15 AM, Interactive logon, Limited run level). Noted the MCP wrapper's `Invoke-HubBat` didn't launch on first attempt (no status file) — worked around via direct `Start-Process`; wrapper itself unverified for next session.
-   Prior chat on 2026-07-14 covered: config.py drift fix (Entry 009) + a live `_get_lm_model_id()` bug fix, full Phase 5.3 IMAP move feature build (config/schemas/domain/infrastructure/application/cli), a live dry-run catching a real dry-run-still-mutates-server bug (Entry 010), Gmail/Yahoo credential troubleshooting, Outlook OAuth2-only discovery and scope-out (Entry 011), a clean live dry-run (Moved=0 DryRun=18 NotFound=1 Failed=0), and the first live move (Moved=18 NotFound=1 Failed=0).

### 12.3 First Tasks on Resume

1.  Read Section 12, confirm date and status with Tony.
2.  Verify `tool_search` for filesystem write tools.
3.  Ask Tony which queued item to start with — likely parent_domain dedup or continuing sector data as history accumulates.
4.  If touching the MCP wrapper: `Invoke-HubBat` produced no status file on 2026-07-18 — verify before trusting it for a long-running P_805 call.
5.  For any short synchronous `python cli.py` test call: use `Start-Process -Wait` with redirected output files, not a piped `| Select-Object` call (Entry 012) — the latter hung the MCP transport twice in the 2026-07-18 v2.2 session.
6.  Before opening any `data\daily\*.csv` in Excel while a session is active: closing it is required before the next Phase 4 run can overwrite it (hit this directly in v2.2).

***

*End of P_805 SYSTEM_DOCUMENTATION v2.8 — ACTIVE*
