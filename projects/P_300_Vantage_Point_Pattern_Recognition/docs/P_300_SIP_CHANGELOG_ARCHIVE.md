# P_300 SIP Changelog Archive

Entries older than current+prior version, moved out of the live SIP (`docs/P_300_System_Initialization_Prompt_v3_1.md`) per the two-version retention rule set 2026-06-18. The live SIP's "Recent Changelog" section keeps only the current and immediately prior version; anything older lands here.

---

### v2.8–v3.1 — 2026-05-29 to 2026-06-04 (condensed)
LM Studio Readiness Check added (v2.8) → Steps 4–5c made an uninterruptible block (v3.0) → Step 0.5 Work Order Review added + first major compression pass, 179→140 lines (v3.1).

*(Entries prior to v2.8 / 2026-05-18 were removed outright during the v3.0 compression pass — no earlier record exists.)*

---

### v3.2 -- 2026-06-18
- **WO-P000-E4.001 -- INIT execution bypass.** Steps 5b/5c read `P_300_preflight_status.json` (written by operator-run `P_300_Preflight.bat`) instead of invoking `python` via PowerShell -- removes the ~4-min subprocess timeout from every INIT run. `File:` header path corrected.

---

### v3.3 — 2026-06-18
- **Decision flags line made real.** Step 5 now greps `config.py`; Step 6 template gained the `Decision flags:` line.
- **Step 1A added** — non-HALTing preflight freshness reminder right after the session header.
- **Compression pass** (~20% shorter); top RULE line corrected "0 through 6" → "0 through 7". Header separator dropped (WO-P000-E4.001 v1.1): no `--` required between date and time.

---

### v3.4 -- 2026-07-22
- **WO-P000-E8.001 pilot: working-state doc retention.** `CLAUDE.md` added at project root (architecture snapshot + Locked Decisions) -- Step 4 now reads it alongside `tasks/lessons.md`/`tasks/todo.md`. Both files split live/archive (`tasks/lessons_archive.md`, `tasks/todo_archive.md`) to stay under a size cap after growing large enough to hit real tool-read limits.
- v3.2 entry moved to this archive per the two-version retention rule.

---

**End of P_300 SIP Changelog Archive**
