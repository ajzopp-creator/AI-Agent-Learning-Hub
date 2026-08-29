# P_400 SIP Changelog Archive

Entries older than current+prior version, moved out of the live SIP (`docs/prompts/P_400_SESSION_INITIALIZATION_PROMPT_v2_0.md`) per the two-version retention rule set 2026-08-29. The live SIP's "Changelog" section keeps only the current and immediately prior version; anything older lands here.

---

### v2.1 — 2026-06-16
- Phase E3 options pipeline integrated (WO-P400-E3.003); chain template added; options/spread CLI variants added.

---

### v2.2 — 2026-06-18
- Appendices A1, B, C removed; content migrated to architecture doc Sections 4.9, 6.2 (JSON template added). Steps 0–7 unchanged. SIP is now steps-only.

---

### v2.4 -- 2026-07-20
- RISK role never blocks (Tony directive): heat/position-count/daily-loss/sector checks downgraded BLOCK -> SEVERE_WARNING; new CASH_BELOW_RISK check added; open-position list attached to every RISK annotation. Matching Tier-1 change in domain/screen.py (HEAT_BREACH/POSITION_COUNT downgraded FAIL -> WARN, no longer auto-disposed). STEP 5 gains an APPROVED_WITH_SEVERE_WARNING branch. See Architecture v2.2.

---

**End of P_400 SIP Changelog Archive**
