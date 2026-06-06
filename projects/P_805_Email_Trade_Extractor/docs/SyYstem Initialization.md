╔════════════════════════════════════════════════════════════════╗
║  P_805 EMAIL TRADE EXTRACTOR — SESSION INITIALIZATION          ║
╚════════════════════════════════════════════════════════════════╝

TRIGGER: Type "INIT", "P_805", or "P_805 INIT" at session start.

───────────────────────────────────────────────────────────────

STEP 1 — Session Header
Display: P_805 [Day, Month DD, YYYY — HH:MM ET]

───────────────────────────────────────────────────────────────

STEP 2 — Verify Working State
Load from disk (if available via filesystem MCP):
- C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\docs\P_805_SYSTEM_DOCUMENTATION.md (v1.4 or current)
- C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor\python\config.py (for current constants)
- Active phase status, daily output location, KB status

If MCP unavailable: request upload of SYSTEM_DOCUMENTATION.md and config.py.

───────────────────────────────────────────────────────────────

STEP 3 — Current Phase & Progress
From SYSTEM_DOCUMENTATION Section 7:
- Phase 1 (Scan): ✅ COMPLETE
- Phase 2 (Sender Filter): ✅ COMPLETE
- Phase 3 (Ticker Extract): ✅ COMPLETE
- Phase 4 (Consensus Ranking): ⏭ NEXT
- Phase 5 (Writer): ⏭ FUTURE
- KB Integration: ✅ COMPLETE (standalone path to Obsidian)

Latest daily CSV: `data\daily\<date>_signals.csv`

───────────────────────────────────────────────────────────────

STEP 4 — Queued Items (Section 12.3)
1. Expand DIRECTION_KEYWORDS with newsletter verbs
2. Fix CSV encoding for Excel (UTF-8 BOM)
3. Phase 4 consensus ranking

───────────────────────────────────────────────────────────────

STEP 5 — Session Summary Block

P_805 SESSION INITIALIZED
────────────────────────────────
Architecture:      v1.4
Python env:        p140 @ C:\Users\Trader\.conda\envs\p140\python.exe
Active phase:      Phase 4 (Consensus Ranking) or [user-specified]
Last output:       data\daily\<YYYY-MM-DD>_signals.csv
Sender whitelist:  59 enabled (sender_sheet.csv)
KB path:           ACTIVE — data\inbox\ → KnowledgeBase/
Queued work:       [item #1, #2, or #3 from Step 4]
────────────────────────────────

───────────────────────────────────────────────────────────────

STEP 6 — Confirm Focus
Ask: "Proceeding with [Phase 4 / queued item #X / other], or steering elsewhere?"

Wait for confirmation. Do NOT code until operator confirms.

───────────────────────────────────────────────────────────────

BRIEFING COMPRESSION (for long sessions):
If chat gets long, copy the session summary above + the operator's
last confirmed direction + the specific task block from
SYSTEM_DOCUMENTATION for that phase. Paste into a new chat as:

"P_805 SESSION RESUME — [previous phase/task]. Context: [paste summary].
Proceeding with [specific task from prior session]."

This restarts clean without losing state.

───────────────────────────────────────────────────────────────