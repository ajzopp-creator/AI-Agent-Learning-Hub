# P_805 EMAIL TRADE EXTRACTOR — SESSION INITIALIZATION v1.5

**Trigger:** `INIT` | `P_805` | `P_805 INIT`

---

### Step 1 — Session Header
Display: `P_805 [Day], [Month] [DD], [YYYY] [HH:MM] ET [optional label]`

### Step 0.5 — Work Order Review
Query `Agentic-Hub-Governance\work_orders\`:
- Owner=P_805, status not CLOSED -> display, HALT if required
- P_805 in Affects, Ack pending -> display, ACTION REQUIRED after session

Unavailable -> proceed with inline note.

### Step 2 — Verify Working State
Load from disk (filesystem MCP):
- `P_805_SYSTEM_DOCUMENTATION.md` (v1.4+) -- phases, KB status, queued work
- `python\config.py` -- constants, active settings
- Latest daily output: `data\daily\<YYYY-MM-DD>_signals.csv`

MCP unavailable -> request upload of SYSTEM_DOCUMENTATION.md + config.py.

### Step 3 — Current Phase & Progress
From SYSTEM_DOCUMENTATION Section 7:
- Phase 1 (Scan) -- COMPLETE
- Phase 2 (Sender Filter) -- COMPLETE
- Phase 3 (Ticker Extract) -- COMPLETE
- Phase 4 (Consensus Rank) -- NEXT
- Phase 5 (Writer) -- FUTURE
- KB Integration -- ACTIVE (`data\inbox\` -> `KnowledgeBase/`)

### Step 4 — Session Summary
```
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
```

### Step 5 — Confirm Focus
Ask: "Proceeding with [Phase 4 / queued item #X / other], or steering elsewhere?" Wait for confirmation -- do NOT code until confirmed.

---

**Briefing compression (long sessions):** copy session summary + last confirmed direction + specific task block from SYSTEM_DOCUMENTATION. Paste into new chat as: *"P_805 SESSION RESUME -- [phase]. Context: [summary]. Proceeding with [task]."*

---

## Changelog
- v1.6 (2026-08-07): Session header fixed to canonical Hub-wide format (ref WO-P000-E4.001) -- was still the pre-revision `[Day, Month DD, YYYY -- HH:MM ET]` draft. Box-drawing separators replaced with plain markdown for Hub-wide style consistency and file-size reduction (79 -> ~55 lines). Duplicate file consolidated: this `docs\` copy is now the sole canonical file; the byte-identical project-root copy is removed (ref WO-P000-E4.001).
- v1.5 (2026-06-04): Added STEP 0.5 Work Order Review (governance).
- v1.4 (original): Initial minimal init with phase tracking.
