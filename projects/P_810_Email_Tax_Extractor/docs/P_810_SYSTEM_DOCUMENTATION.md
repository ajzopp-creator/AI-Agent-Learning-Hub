# P_810 SYSTEM_DOCUMENTATION
## Email Tax Extractor

---

**Project ID:** P_810
**Project Name:** Email Tax Extractor
**Version:** 1.2
**Created:** 2026-08-20
**Updated:** 2026-08-20 (v1.2 — reverted from P_820 back to P_810, same session, before any code was written; P_820 was a mistaken ID collision with a separate planned project, Order Signal Capture, per Tony. v1.1 briefly renamed this to P_820. v1.0 was initial scaffold: docs + folder structure only, no Python. Created via WO-P810-E1.001.)
**Owner:** Tony
**Status:** **SCAFFOLD** — docs and folder structure exist; no code yet. Awaiting real AJZ Strategies tax sender list before Phase 1 build starts.
**Parent Relationship:** Peer of P_805 (no sub-project relationship; shares reusable mbox/IMAP layer via `shared_resources\python_utils\`, does not depend on P_805's code directly)
**Root Path:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_810_Email_Tax_Extractor\`

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
Extract AJZ Strategies-related tax emails — receipts, notifications, statements, tax-document-ready alerts — from the same Thunderbird mbox cache P_805 reads, and produce a dated record for tax recordkeeping. This is category-based mailbox triage scoped to tax-relevant senders only — explicitly the kind of work P_805's own doc (Section 1.4) carves out as out-of-scope for that project, which is why this is a peer project rather than a `--taxes` flag on P_805.

### 1.2 Goals
- Scan approved AJZ Strategies tax-related senders over a configurable lookback window
- Identify and categorize tax-relevant messages (receipt, notification, statement, document-ready alert — categories to be finalized against real sender data)
- Produce a dated output record for Tony's tax recordkeeping — no ranking, no consensus (this is not a signal-aggregation problem like P_805's ticker consensus)
- The system never sends, replies to, forwards, or deletes mail (same hard rule as P_805)

### 1.3 In-Scope
- Reading mail from the same four IMAP account caches P_805 uses, via the live Thunderbird profile `m306ztzh.IETimport`
- Whitelist-based sender filtering against a P_810-specific `data\sender_sheet.csv` (AJZ Strategies tax senders only — separate list from P_805's trading-newsletter whitelist)
- Categorizing messages by type (receipt / notification / statement / other — pending real evidence)
- Dated output record, format TBD in Phase 1 planning (likely CSV, matching Hub convention)

### 1.4 Out-of-Scope
- Sending, replying to, forwarding, or deleting any email
- Trading signal extraction — that's P_805, not this project
- IMAP move to a processed-mail folder — not yet decided whether tax emails should be moved (open question, see Section 8)
- Filing or submitting taxes — this produces a research/recordkeeping list only

### 1.5 Definitions & Acronyms
- **AJZ Strategies** — Tony's trading entity; source of the tax-relevant correspondence this project targets
- **Approved Sender** — email address on the whitelist in `data\sender_sheet.csv` with `enabled=true`
- **Category** — message type tag (receipt / notification / statement / other) — column in `sender_sheet.csv`, replaces P_805's `sector` concept since tax emails aren't being ranked by consensus
- **mbox** — Thunderbird's mail file format (one flat file per folder, no extension)
- **P_805** — peer project (Email Trade Extractor); shares the reusable mbox/IMAP/header-decode layer via `shared_resources\python_utils\`

---

## Section 2 — Architecture & Tech Stack

### 2.1 Runtime
- **Python:** `C:\Users\Trader\.conda\envs\p140\python.exe` (shared p140 conda env — never a new venv)
- **OS:** Windows 11
- **IDE:** VS Code

### 2.2 Shared-Code Strategy
P_810 reuses P_805's proven mbox/IMAP/header-decoding layer rather than reimplementing it. Plan (not yet executed — separate code WO):
- Promote P_805's `domain\headers.py`, `domain\html_strip.py`, `infrastructure\mbox_reader.py`, `infrastructure\mbox_body.py` into `shared_resources\python_utils\` so both P_805 and P_810 import from one place.
- P_810 owns its own: `config.py`, `schemas.py` (tax-record schema, not `TickerSignal`), sender whitelist, categorization logic, output writer.
- No shared `sender_sheet.csv` — P_805's trading-newsletter whitelist and P_810's tax-sender whitelist are separate lists with separate governance (Tony edits each independently).

### 2.3 Libraries (planned, matches P_805's proven stack)
- `mailbox` (stdlib) — mbox parsing
- `email` (stdlib) — header and body extraction
- `pydantic` v2 — schemas for persistent file I/O
- `pandas` — output formatting

### 2.4 Storage (planned)
- Filesystem only, same pattern as P_805.
- Daily output: `data\daily\YYYY-MM-DD_tax_records.csv` (exact schema TBD in Phase 1 planning)
- Logs: `python\logs\p810.log` (rotating), `python\logs\rejected.log` (rotating) — same pattern as P_805

### 2.5 Code Architecture Standard
Hub-wide **python-project-architecture** standard, same as every project:
- Code lives under `python\`, split into `domain\` (logic, no I/O), `infrastructure\` (all I/O), `application\` (orchestration).
- All constants and paths live in `python\config.py`. Never hardcoded elsewhere.
- Any persistent file read or write requires a Pydantic schema in `python\schemas.py`.
- Hard limits: 300 lines per file, 50 lines per function.

---

## Section 3 — AI Behavior Rules & Constraints

**MUST:**
- At session start in Claude Desktop, run `tool_search` for filesystem write capability. Write directly to the final project path via `filesystem:write_file` / `filesystem:edit_file` — never `create_file` + `present_files` for project code.
- Reuse P_805's proven mbox/IMAP patterns (Entry 001, Entry 005 in P_805's doc) rather than rediscovering the same mistakes — read `P_805_SYSTEM_DOCUMENTATION.md` Section 6 before building the reader.
- Respect the approved-sender whitelist from `data\sender_sheet.csv` (rows where `enabled=true`). Reject any sender not on the list.
- No guessing categories or senders — populate from real evidence (subject lines, actual sender addresses Tony provides) only, same discipline as P_805's sector tagging.
- Split code per Hub rules: 300 lines max per file, 50 lines max per function, domain/infrastructure/application layers separated.
- State full Windows save path for every file produced.

**MUST NOT:**
- Send, reply to, forward, or delete any email.
- Handle IMAP credentials as plaintext anywhere — keyring only, if/when live IMAP access is added.
- Fabricate a sender list or category taxonomy without real evidence.
- Duplicate P_805's mbox/IMAP code — import from `shared_resources\python_utils\` once promoted there.

---

## Section 4 — Folder Structure

```
C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_810_Email_Tax_Extractor\
├── docs\
│   └── P_810_SYSTEM_DOCUMENTATION.md         # this file (v1.2)
├── tasks\
│   └── todo.md                               # current-state checkout (Protocol F2)
├── data\
│   ├── daily\                                 # Phase 1+ output (empty)
│   ├── monthly\                               # future rollups (empty)
│   └── sender_sheet.csv                       # AJZ Strategies tax sender whitelist (headers only — Tony to populate)
├── README.md
└── python\
    ├── __init__.py
    ├── domain\
    │   └── __init__.py                        # empty — logic modules TBD
    ├── infrastructure\
    │   └── __init__.py                        # empty — I/O modules TBD
    ├── application\
    │   └── __init__.py                        # empty — orchestration TBD
    ├── tests\
    │   └── __init__.py                        # empty — regression tests TBD
    └── logs\                                   # empty — run logs land here
```

No `config.py`, `schemas.py`, or `cli.py` yet — those are Phase 1 deliverables, planned with a file-and-line-count list before any code is written (Protocol A).

---

## Section 5 — Approved Senders Registry

### 5.1 Authoritative Source
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_810_Email_Tax_Extractor\data\sender_sheet.csv`

### 5.2 CSV Schema
| Column | Type | Purpose |
|--------|------|---------|
| `email_address` | string | Full sender address |
| `sender_name` | string | Display name for reports |
| `date_added` | YYYY-MM-DD | When sender was whitelisted |
| `category` | string | receipt / notification / statement / other — populated from real evidence only, same discipline as P_805 sector tags |
| `enabled` | `true`/`false` | Only `true` rows are scanned |

### 5.3 Current State
Headers only — zero rows. Tony to supply the real AJZ Strategies tax-related sender addresses before Phase 1 build starts.

### 5.4 Editing
Same convention as P_805: Tony edits the CSV directly. No code change needed to add, remove, or disable a sender.

---

## Section 6 — Error Corrections Log

*Empty — no build yet. First real entry lands when the first bug is found and fixed, same discipline as every other Hub project's log.*

---

## Section 7 — Build Roadmap

**Phase 0 — Scaffold: ✅ COMPLETE (2026-08-20)**
Docs, folder structure, sender_sheet.csv scaffold. No code. Ref WO-P810-E1.001.

**Phase 1 — Reader: ⏳ NOT STARTED**
Blocked on: (1) real AJZ Strategies tax sender list from Tony, (2) shared-code promotion of P_805's mbox/IMAP layer into `shared_resources\python_utils\`. File-and-line-count plan required before any code is written (Protocol A).

---

## Section 8 — Enhancement Backlog

- Open question: should extracted tax emails be moved to a processed folder (like P_805's `ExtractedNewsletterFolder`), or left in place? Decide once Phase 1 shows real volume.
- Open question: output format — CSV only, or also a `.md`/summary for Tony's tax prep workflow? Decide with Tony once category taxonomy is real.

---

## Section 11 — Parameters

### 11.4 Parameter Registry
Empty — no `config.py` exists yet. Will mirror P_805's pattern (all paths/thresholds/patterns as named constants, nothing hardcoded elsewhere) once Phase 1 starts.

---

## Section 12 — Session Close & Resume Path

### 12.1 Status at Close (2026-08-20, v1.2)
Scaffold only: docs, folder structure, empty sender_sheet.csv. No Python. WO-P810-E1.001 OWNER_DONE pending Independent Review. Project ID churned P_810 → P_820 → P_810 within this one session, before any code existed — no downstream references broke.

### 12.3 First Tasks on Resume
1. Confirm Tony has supplied the real AJZ Strategies tax sender list — if not, that's still the blocker, don't guess.
2. If sender list is ready: present the shared-code promotion plan (P_805 → `shared_resources\python_utils\`) for approval before touching P_805's code.
3. Then present Phase 1 file-and-line-count plan for P_810 itself (config.py → schemas.py → domain → infrastructure → application → cli.py), per Protocol A.

---

*End of P_810 SYSTEM_DOCUMENTATION v1.2 — SCAFFOLD*
