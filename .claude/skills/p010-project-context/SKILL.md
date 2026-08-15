---
name: p010-project-context
description: >
  P_010 Current Market Posture — project-specific operating rules, critical
  paths, risk-mode calculation, and anti-patterns. Load at the start of ANY
  session involving P_010 work. Triggers on any reference to P_010,
  RiskConfig.json, avg_posture, risk_mode, VXX signal, VantagePoint Grid,
  intraday_adjustment, morning_risk_mode, or the Obsidian daily note writer.
  Always read BEFORE writing any code or file path.
---

# P_010 Project Context

## Purpose & Pairs With

Auto-loading protection layer for P_010 — the Hub's single source of truth
for daily market risk posture. Computes `risk_mode` from VantagePoint Grid
predictions each morning, refines it intraday, and feeds the result to
P_115/P_118 for position sizing. Also auto-generates the Obsidian daily
trading journal note. Full domain rules live in the system doc, loaded on
demand.

| File | Role |
| :---- | :---- |
| `SESSION_INITIALIZATION_PROMPT.md` (v2.9) | INIT sequence — steps only |
| `P_010_System_Documentation_v3.md` (v3.3) | Full spec — risk formula, schema, PowerShell rules, task scheduler |
| `docs/P_010_Error_Corrections_Log.md` | ERROR 001/002 — read before touching intraday or PowerShell execution |
| `docs/P_010_Enhancement_Backlog.md` | Open/in-progress items — check before assuming a feature exists |
| `docs/P_010_Quick_Reference_Guide.md` | Condensed operator reference |
| **THIS FILE** | Always-active protection rules |

---

## Critical Paths

| Path | Resolution |
| :---- | :---- |
| Hub root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |
| Project root | `<Hub>\projects\P_010_Current_Market_Posture\` |
| Python | `C:\Users\Trader\.conda\envs\p140\python.exe` (shared conda env — never suggest a new venv) |
| Master config | `P_010_RiskConfig.json` (project root) — the ONE file P_115/P_118 read for sizing |
| Intraday snapshot | `grid_snapshot_latest.json` (project root) |
| Morning script | `python\P_010_daily_posture_v5.py` — ACTIVE (reads `data\excel_exports\History Grid (SPY/QQQ/VXX)_v3.xlsx`) |
| Intraday script | `python\P_010_intraday_vp_check_v4.py` — ACTIVE |
| Note writer | `python\P_010_write_daily_note.py` — ACTIVE, writes Obsidian daily note |
| Obsidian vault | `C:\Users\Trader\Documents\AJZStrategies_TradingJournal\Trading Journal\TradingJournal\DD-MM-YYYY.md` |
| Skip-automation flag | `SKIP_TODAY.flag` (project root) — drop here to suppress all automation for the day |
| Session Guardian | `P_010_Start_Guardian.bat` — double-click each morning; auto-runs the missed morning posture if today's log is absent, then monitors for Claude Desktop sync/API errors |
| Error log | `docs\P_010_Error_Corrections_Log.md` |
| Failure flag | `MORNING_RUN_FAILED.flag` (project root) -- written/cleared by `P_010_daily_posture_v5.py`; `P_010_daily_posture.bat` skips STEP 2 (note writer) if present; Guardian checks it too (WO-P010-E1.003) |
| Toast notifier | `python\toast_notify.py` -- BurntToast-based, NOT windows-mcp:Notification (that tool needs a live MCP session; unattended runs have none). See ERROR 003. |
| Staleness check | `python\staleness_check.py` -- keys off RiskConfig's `timestamp` field, never `grid_date` (grid_date legitimately lags over weekends) |
| Note writer split | `python\note_api_fetchers.py` / `note_content_builders.py` / `note_template_engine.py` -- extracted from the note writer 2026-08-10 to clear the 300-line limit; `P_010_write_daily_note.py` is orchestration only now |
| Intraday split | `python\intraday_risk_logic.py` -- PRANGE validation + risk-mode decision, extracted 2026-08-10; `P_010_intraday_vp_check_v4.py` is orchestration only now |

**Task Scheduler (locked bat filenames — never rename, Scheduler references them directly):**
`P_010_daily_posture.bat` (weekdays 7:30 AM trigger, runs ~9:30 AM) | `P_010_run_intraday_vp_check.bat` (weekdays 2:00 PM)

---

## Risk Mode Calculation (Section 4, System Doc v3.3)

```
Medium_Term_Diff = (predicted_close - current_close) / current_close x 100
Long_Term_Diff   = similar calc, longer timeframe
Posture_Score    = (Medium_Term_Diff + Long_Term_Diff) / 2   -- per symbol

avg_posture = (SPY_posture + QQQ_posture) / 2

avg_posture >= 1.0  -> risk_mode = FULL
avg_posture >= 0.0  -> risk_mode = HALF
avg_posture <  0.0  -> risk_mode = OFF
```

This formula is what *generates* `risk_mode` in the JSON — it is not a
separate reference table competing with the JSON. Once written, `risk_mode`
in `P_010_RiskConfig.json` is authoritative for every downstream consumer;
no consumer should re-derive it from `avg_posture` independently.

**VXX overlay (advisory only — never changes `risk_mode`):**
```
vxx_posture < -1.0          -> BULLISH_CONFIRM
-1.0 <= vxx_posture < 0.5   -> NEUTRAL
0.5 <= vxx_posture < 1.5    -> CAUTION
vxx_posture >= 1.5          -> WARNING
```

**Intraday adjustment (2 PM check, PRANGE-based):**
```
Both symbols within PRANGE      -> intraday_adjustment = NONE
One symbol outside PRANGE (>2%) -> intraday_adjustment = HALF
Both outside OR deviation >5%   -> intraday_adjustment = REDUCED

Risk hierarchy (most restrictive wins): OFF < REDUCED < HALF < NONE < FULL
Final mode = MIN(morning risk_mode, intraday_adjustment)
```

**`HOT` is not a P_010 output.** P_010's `risk_mode` field is only ever
FULL / HALF / OFF. "HOT" is a P_115-side derived tier (avg_posture > 1.08,
tiered 2–5% sizing) applied downstream on top of a FULL morning read — never
write HOT into `P_010_RiskConfig.json` or treat it as a fourth risk_mode value.

---

## P_010_RiskConfig.json Schema (v5)

**After morning run:**
```json
{
  "timestamp": "...",
  "spy_posture": -4.13, "qqq_posture": -1.28, "avg_posture": -2.70,
  "risk_mode": "OFF",
  "source": "Grid_XLSX",
  "spy_grid_date": "...", "qqq_grid_date": "...",
  "vxx_posture": 3.03, "vxx_signal": "WARNING", "vxx_note": "...",
  "vxx_close": 35.67, "vxx_pred_high": 37.71, "vxx_pred_low": 33.83,
  "vxx_grid_date": "..."
}
```

**After intraday run (adds 2 fields in place):**
```json
{
  "...all morning fields...": "...",
  "intraday_adjustment": "REDUCED",
  "intraday_reason": "Both symbols outside PRANGE"
}
```

**`morning_risk_mode`** is a separate, locked field the intraday script must
preserve — see ERROR 001 below. It does not appear in the schema table above
because it is written defensively on first intraday run of the day, not by
the morning script itself.

**Downstream consumer logic (P_115/P_118):**
```
IF intraday_adjustment exists -> final = MIN(risk_mode, intraday_adjustment)
ELSE                          -> final = risk_mode
```

---

## Anti-Patterns (Forbidden by Construction)

1. **Reading `morning_risk_mode` from the live `risk_mode` field** — ERROR
   001 (2026-03-31, HIGH). Running the intraday check more than once in a
   day caused `risk_mode` to cascade upward (OFF → HALF → FULL) because each
   run treated the *previous* intraday-adjusted value as if it were the
   morning baseline. Always read `morning_risk_mode` (preserved, locked) for
   the baseline — never `risk_mode`. If `morning_risk_mode` is missing,
   capture and write it on that run; never invent a value.
2. **`Start-Process python.exe -NoNewWindow` from Windows-MCP** — ERROR 002
   (2026-06-01, HIGH). The child process inherits MCP's stdio pipes, so the
   MCP server blocks until the child exits — a ~4-minute hang with no
   output. ALWAYS use the `Start-Job` + `cmd /c` pattern (System Doc Section
   8) instead: launch in one tool call, `Start-Sleep` + `Get-Content` the
   output file in a second call. Sleep sizing: no subprocess=0s | Python, no
   Excel=20s | Python+Excel=45s | batch=90s.
3. **Treating the VXX signal as something that changes `risk_mode`** — it is
   a sentiment confirmation layer only (BULLISH_CONFIRM/NEUTRAL/CAUTION/
   WARNING). It informs the operator's read of the session; it never feeds
   back into the FULL/HALF/OFF calculation.
4. **Writing `HOT` into `P_010_RiskConfig.json`** — `risk_mode` is strictly
   FULL/HALF/OFF. HOT is a P_115-side interpretation of `avg_posture > 1.08`
   layered on top of a FULL read downstream, never a P_010 output value.
5. **Assuming a stale `P_010_RiskConfig.json` is current** — check the
   `timestamp` / grid-date fields against today's date before treating the
   file as live. Task Scheduler can silently skip the morning run on a
   battery-boot (root cause of the original Guardian-bat fix); the Guardian
   auto-recovers this if it was launched, but don't assume it always was.
6. **Overwriting an existing Obsidian daily note** — the note writer never
   overwrites `TradingJournal/DD-MM-YYYY.md`; if a re-run is needed, the
   existing file must be deleted first (Section 10 troubleshooting), not
   silently replaced by re-running the script.
7. **Trusting a subprocess exit code alone as proof a Windows notification
   fired** -- ERROR 003 (2026-08-10, MEDIUM). Two-stage silent failure:
   NotifyIcon.ShowBalloonTip "succeeded" with no message loop to render it,
   then BurntToast's replacement call also returned exit 0 after a
   terminating Import-Module error (powershell.exe -Command doesn't
   reliably propagate -ErrorAction Stop into its own exit code). Neither
   failure was visible to any automated check -- only confirmed by Tony
   watching the screen and seeing nothing. Fix: wrap the PowerShell call in
   try/catch with an explicit exit code, and treat non-empty stderr as
   failure even when the exit code claims success. Any unattended-script
   notification mechanism needs a human-watched screen test before it's
   trusted, not just a clean return.
8. **Assuming EZBreakouts exposure data or the P_300-in-P_010 migration
   already exist** — both are open backlog items (IN PROGRESS / QUEUED),
   not shipped features. Check `docs/P_010_Enhancement_Backlog.md` before
   referencing either as if it's live.

---

## Layer / Pipeline Architecture

```
Three-script pipeline (9:30 AM, Task Scheduler -> P_010_daily_posture.bat):
  STEP 1: P_010_daily_posture_v5.py
    reads  data\excel_exports\History Grid (SPY/QQQ/VXX)_v3.xlsx
    writes P_010_RiskConfig.json (master), grid_snapshot_latest.json,
           data\snapshots\grid_snapshot_YYYYMMDD_HHMMSS.json
  STEP 2: P_010_write_daily_note.py
    reads  P_010_RiskConfig.json, grid_snapshot_latest.json,
           Templates\P_010_TemplateSchema_v*.md (auto-picks highest version)
    fetches live Scripture/Quote/Joke APIs (fails gracefully, inline message)
    writes Obsidian TradingJournal\DD-MM-YYYY.md

Intraday pipeline (2:00 PM, Task Scheduler -> P_010_run_intraday_vp_check.bat):
  P_010_intraday_vp_check_v4.py
    reads   grid_snapshot_latest.json, live SPY/QQQ prices via yfinance
    updates P_010_RiskConfig.json in place (adds intraday_adjustment,
            intraday_reason, preserves morning_risk_mode)
    writes  outputs\intraday_vp_check_YYYYMMDD_HHMMSS.json (audit)
```

`python/` root holds only production scripts; `python/archive/` holds prior
versions for reference — never import from `archive/`.

---

## Session Guardian & Morning Startup

```
Step 1: Double-click P_010_Start_Guardian.bat  -- background error watcher
        (checks for today's posture log; auto-runs the morning batch first
        if it's missing, then starts monitoring)
Step 2: Open Claude Desktop -- Guardian runs silently alongside
Step 3: Verify P_010_RiskConfig.json timestamp is today's (Task Scheduler
        or the Guardian's catch-up run should have produced it)
```

Guardian alert severities: **DATA LOSS WARNING** [RED] = stop pasting new
work immediately | **Sync Blocked** [YELLOW] | **Server Error** [YELLOW] |
**Request Failed** [RED] = non-retryable failure on last message.

---

## AI Behavioral Rules

**Must:**
1. Read `morning_risk_mode` (never `risk_mode`) as the baseline on any
   intraday-adjustment logic or troubleshooting (ERROR 001 guard).
2. Use `Start-Job` + `cmd /c` for any Python launch via Windows-MCP;
   never `Start-Process -NoNewWindow` (ERROR 002 guard).
3. Check the config `timestamp`/grid-date against today's date before
   treating `P_010_RiskConfig.json` as current.
4. Treat `risk_mode` as authoritative once read — never re-derive it from
   `avg_posture` downstream; that arithmetic only runs inside the morning
   script itself.
5. Confirm `intraday_adjustment` presence before deciding whether MIN()
   logic applies (it may not exist before the 2 PM run).
6. Check `docs/P_010_Enhancement_Backlog.md` before assuming a queued or
   in-progress feature (EZBreakouts feed, P_300 migration) is live.

**Must Not:**
1. Let the VXX signal influence `risk_mode` — advisory layer only.
2. Write `HOT` as a `risk_mode` value — P_010 only ever emits FULL/HALF/OFF.
3. Overwrite an existing Obsidian daily note — delete first if a re-run is
   genuinely needed.
4. Rename `P_010_daily_posture.bat` or `P_010_run_intraday_vp_check.bat` —
   Task Scheduler references these filenames directly.
5. Retry a hung `Start-Process` call — kill and switch to `Start-Job` +
   `cmd /c` immediately; retrying the same pattern just re-hangs.

---

## Session-Start Checklist

- [ ] Call `tool_search` for PowerShell/Windows-MCP first — never claim
      web/Desktop status before this check
- [ ] Check `Agentic-Hub-Governance\work_orders\` for Owner=P_010 or P_010
      in Affects, Status not CLOSED
- [ ] Read `P_010_RiskConfig.json`; confirm `timestamp`/grid-date is today
      — if stale, surface "run INIT daily" rather than proceeding on old data
- [ ] Confirm `morning_risk_mode` field is present before any intraday
      troubleshooting (its absence is the ERROR 001 risk signal)
- [ ] Display risk_mode, avg_posture, SPY/QQQ posture, vxx_signal, and
      intraday_adjustment (or "not run") in the session summary

---

## When to Consult the Full System Doc

Load `P_010_System_Documentation_v3.md` for:
- Full three-script pipeline detail and file-by-file read/write contracts
- Section 6 position sizing table (FULL/HALF/OFF percentages, HOT tier
  dollar amounts as consumed downstream by P_115)
- Section 7 Obsidian note writer internals (template selection, auto-fill
  sections, safety rules)
- Section 8 exact PowerShell command blocks for manual INIT daily/intraday
- Section 11 Task Scheduler trigger configuration
- Section 12 full version history

Do NOT load reflexively — this SKILL covers routine INIT and troubleshooting.

---

## Maintenance

- **Owner:** Anthony Zoppi (review), Claude (drafting)
- **Update trigger:** New ERROR-XXX entry in the error corrections log, a
  RiskConfig schema version bump (v5 -> v6+), or a Task Scheduler /
  automation change discovered in a live session (add here same session,
  per Hub-wide rule in `WO_COMPLETION_GATE.md`)

## Changelog

### 2026-08-10
- WO-P010-E1.003 (fail-loud alerting) landed: MORNING_RUN_FAILED.flag
  halt mechanism (P_010_daily_posture_v5.py writes/clears it,
  P_010_daily_posture.bat checks it before STEP 2, note writer never
  runs against a failed morning read), 	oast_notify.py (native Windows
  toast, BurntToast-based -- see ERROR 003), staleness_check.py (keys off
  	imestamp, never grid_date -- grid_date legitimately lags over
  weekends). Also split two files that had grown past the 300-line hard
  limit: P_010_write_daily_note.py (429 -> 151 lines, extracted
  
ote_api_fetchers.py / 
ote_content_builders.py /
  
ote_template_engine.py) and P_010_intraday_vp_check_v4.py
  (299 -> 238 lines, extracted intraday_risk_logic.py). Anti-pattern 7
  added (ERROR 003). Item 4 from the WO (intraday .bat errorlevel bug
  printing [ERROR] after [SUCCESS]) still open -- no repro found on a
  static read, needs a live repro log before touching it. STEP 3
  (market_health.cli) deliberately left unconditional -- confirmed
  independent of STEP 1's output, no dependency to gate.

### 2026-07-08
- Initial build. Created under WO-P000-E6.001 (Gap 3 of the 2026-07-06
  context-engineering KB review, final of the three skills — P_115 and
  P_400 already complete). Content sourced directly from
  `SESSION_INITIALIZATION_PROMPT.md` v2.9, `P_010_System_Documentation_v3.md`
  v3.3 (risk formula, schema, PowerShell rules, task scheduler), and
  `docs/P_010_Error_Corrections_Log.md` (ERROR 001 morning_risk_mode
  cascade, ERROR 002 Start-Process hang). Live `P_010_RiskConfig.json` and
  `grid_snapshot_latest.json` read directly to confirm schema accuracy
  against the current production file, not just the doc's example block.

---

**End of P_010 Project Context SKILL**
