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

**End of P_300 SIP Changelog Archive**
