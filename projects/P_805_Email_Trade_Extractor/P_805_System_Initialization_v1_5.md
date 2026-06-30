╔════════════════════════════════════════════════════════════════╗
║  P_805 EMAIL TRADE EXTRACTOR — SESSION INITIALIZATION v1.5    ║
╚════════════════════════════════════════════════════════════════╝

TRIGGER: "INIT", "P_805", or "P_805 INIT"

───────────────────────────────────────────────────────────────

STEP 1 — Session Header
Display: P_805 [Day, Month DD, YYYY — HH:MM ET]

───────────────────────────────────────────────────────────────

STEP 0.5 — Work Order Review
Query shared ledger: C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\
- Owner=P_805, status not CLOSED → Display; HALT if required
- P_805 in Affects, Ack pending → Display; ACTION REQUIRED after session

If unavailable: proceed with inline note.

───────────────────────────────────────────────────────────────

STEP 2 — Verify Working State
Load from disk (filesystem MCP):
- P_805_SYSTEM_DOCUMENTATION.md (v1.4+) — phases, KB status, queued work
- python\config.py — constants, active settings
- Latest daily output: data\daily\<YYYY-MM-DD>_signals.csv

If MCP unavailable: request upload of SYSTEM_DOCUMENTATION.md + config.py.

───────────────────────────────────────────────────────────────

STEP 3 — Current Phase & Progress
From SYSTEM_DOCUMENTATION Section 7:
- Phase 1 (Scan):           ✅ COMPLETE
- Phase 2 (Sender Filter):  ✅ COMPLETE
- Phase 3 (Ticker Extract): ✅ COMPLETE
- Phase 4 (Consensus Rank): ⏭ NEXT
- Phase 5 (Writer):         ⏭ FUTURE
- KB Integration:           ✅ ACTIVE (data\inbox\ → KnowledgeBase/)

───────────────────────────────────────────────────────────────

STEP 4 — Session Summary Block

P_805 SESSION INITIALIZED
────────────────────────────────
Architecture:      v1.4
Python env:        p140 @ C:\Users\Trader\.conda\envs\p140\python.exe
Work Orders:       [status or OK]
Active phase:      Phase 4 (Consensus Ranking) or [user-specified]
Last output:       data\daily\<YYYY-MM-DD>_signals.csv
Sender whitelist:  59 enabled (sender_sheet.csv)
KB path:           ACTIVE — data\inbox\ → KnowledgeBase/
Queued work:       [from Section 12.3 of SYSTEM_DOCUMENTATION]
────────────────────────────────

───────────────────────────────────────────────────────────────

STEP 5 — Confirm Focus
Ask: "Proceeding with [Phase 4 / queued item #X / other], or steering elsewhere?"

Wait for confirmation. Do NOT code until confirmed.

───────────────────────────────────────────────────────────────

BRIEFING COMPRESSION (long sessions):
Copy session summary + last confirmed direction + specific task block
from SYSTEM_DOCUMENTATION. Paste into new chat as:

"P_805 SESSION RESUME — [phase]. Context: [summary]. Proceeding with [task]."

───────────────────────────────────────────────────────────────

CHANGELOG:
v1.5 (2026-06-04): Added STEP 0.5 Work Order Review (governance).
v1.4 (original): Initial minimal init with phase tracking.

───────────────────────────────────────────────────────────────
