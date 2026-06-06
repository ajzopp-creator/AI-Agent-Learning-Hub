# PROJECT CONSOLIDATION CONTINUATION PROMPT
*Paste this at the start of a new chat when resuming document merge/cleanup work*
*Update the COMPLETED and PENDING sections as work progresses*

---

## Context
We are consolidating the P_115 project knowledge base to reduce file count, eliminate duplicates, and merge related documents into single authoritative files. Goal: stay under the project file limit while improving document quality.

---

## COMPLETED MERGES (files already uploaded to project, originals can be deleted)

| Merged Output File | Source Files Merged | Status |
|---|---|---|
| P_115_Strategy_Guide_MERGED.md | P_115_Strategy_Guide.md + P_115_Strategy_Guide_V110_Addendum.md | Upload done — delete sources |
| P_115_StrategyGuide_ChangeLog.md | P_115_Strategy_Change_Log.md + STRATEGY_CHANGE_LOG_V110.md | Upload done — delete sources |

## COMPLETED ADDITIONS (new condensed summaries uploaded)
These replaced original PDFs that were deleted:
- P115_MasterTheMarket_Summary.md
- P115_RSI_BullBear_Summary.md
- P115_Options_Combined_Summary.md
- Price_Action_Edge_Summary.md

---

## CURRENT PROJECT FILE INVENTORY
*(Update this list as files are added/deleted)*

### Keep — Core Strategy Docs
- [ ] P_115_Strategy_Guide_MERGED.md ← new merged file
- [ ] P_115_StrategyGuide_ChangeLog.md ← new merged file
- [ ] P_116_Income_Launchpad.md
- [ ] P_117_AdHoc_Guide_1_.md
- [ ] P_118_EddieZ_Guide.md

### Keep — System Operations
- [ ] SESSION_INITIALIZATION_PROMPT.md
- [ ] CLAUDE_ASSISTANT_INSTRUCTIONS_v2_1_.md
- [ ] SYSTEM_ARCHITECTURE_OVERVIEW_1_.md
- [ ] ACCOUNT_PARAMETERS_CURRENT.md
- [ ] Quick_Reference_Prompts_v9_4_1.md
- [ ] P_115_Daily_WorkFlow_

### Keep — Schema & Reference
- [ ] Tracker_Log_Schema_v9_4_0.md ← most current schema
- [ ] POSITION_SIZING_THREE_GATE_REFERENCE.md
- [ ] OPTIONS_RISK_METHODOLOGY.md

### Keep — Book Summaries
- [ ] P115_MasterTheMarket_Summary.md
- [ ] P115_RSI_BullBear_Summary.md
- [ ] P115_Options_Combined_Summary.md
- [ ] Price_Action_Edge_Summary.md

### Keep — Code & Specs
- [ ] p301_trend_filter.py
- [ ] Z_SCORE_INTEGRATION_SPEC.md
- [ ] FEATURES_ROADMAP_2026.md

### PENDING DECISION — Merge or Delete Candidates
| File | Recommendation | Reason |
|---|---|---|
| Tracker_Log_Schema.md | DELETE or merge into v9_4_0 | Older version superseded by v9_4_0 |
| Tracker_Log_Schema_v9_3_1_.md | DELETE | Superseded by v9_4_0 |
| SYSTEM_CORRECTIONS_LOG.md | Consider merge into StrategyGuide_ChangeLog | Historical corrections already captured in change log |
| DOCUMENTATION_UPDATE_SUMMARY_1_.md | Review — likely deletable | May be superseded by change log |
| TTD_Trade_Analysis_and_Fix.md | Review — trade-specific | Keep if still relevant as a methodology reference |
| __Claude-Python_Agentic_Migration.md | Review | Keep if active development, delete if completed |

### DELETE — Originals replaced by merged files above
- [ ] P_115_Strategy_Guide.md ← replaced by MERGED version
- [ ] P_115_Strategy_Guide_V110_Addendum.md ← merged in
- [ ] P_115_Strategy_Change_Log.md ← replaced by ChangeLog
- [ ] STRATEGY_CHANGE_LOG_V110.md ← merged in

---

## MERGE RULES (maintain these across sessions)
1. Newest/most complete version wins when content conflicts
2. Version history sections are always preserved in the merged output
3. File naming: use the most descriptive existing name or create logical new name
4. Always write merged output to /mnt/user-data/outputs/ for download, then user uploads to project
5. After confirming upload, note originals as ready to delete
6. Never delete source content until merged output is confirmed uploaded

---

## NEXT STEPS (pick up here in new chat)
1. Review PENDING DECISION files above with Tony
2. Merge or delete Tracker_Log_Schema.md and v9_3_1_ (both superseded by v9_4_0)
3. Review DOCUMENTATION_UPDATE_SUMMARY_1_.md — merge into ChangeLog or delete
4. Review SYSTEM_CORRECTIONS_LOG.md — content likely captured in ChangeLog already
5. Confirm final file count is under project limit
