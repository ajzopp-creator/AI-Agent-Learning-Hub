# HANDOFF -- E13.001 Blocked-Project Unblock + Two Follow-On WOs

Read C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\WO-P000-E13.001.md
in full first, specifically the PHASE 2 EXECUTION LOG section (2026-08-07 pass)
-- this handoff picks up exactly where that pass stopped: P_020, P_300, and
P_800 blocked on pre-existing collection breaks.

Approved in a Claude Desktop chat session: config-exclusion unblock for the
three blocked projects, plus filing two follow-on WOs for the two genuine
production/test drift bugs found along the way. Use p140 for everything
Python: C:\Users\Trader\.conda\envs\p140\python.exe

## Task 1 -- Unblock via config exclusion (not code fixes)

Three files are misnamed like tests but aren't real pytest tests. Exclude
each from collection via conftest.py/pytest.ini path exclusion -- do not
edit the files themselves, this is a config-only change:

1. `projects\P_020_AJZStrategies_PerformanceAnalysisSystem\python\api\test_schwab.py`
   -- manual Schwab-auth diagnostic script, calls `sys.exit(1)` at module level.
2. `projects\P_300_Vantage_Point_Pattern_Recognition\python\tests\test_signal_emitter_dry_run_backup_2026-07-25_WO-P800-E3.003.py`
   -- a backup file, not a test; filename isn't even a valid Python module
   name. This WO's own Phase 3 already names it for deletion/archiving --
   your call whether to exclude-and-leave for Phase 3, or delete it now
   since it's clearly unwanted and is blocking Phase 2. Either is fine,
   state which you did.
3. `projects\P_800_Automation_Note_Taking\python\tests\test_signal_v2_e2e.py`
   -- Finding-5-style harness: helper functions named `test_*` called
   manually from the file's own `main()`, not real pytest tests.

Do NOT exclude `test_eval_incremental.py` (P_300) or `test_p115_write.py`
(P_800) -- those are real broken tests covered by Task 2 below, not config
exclusions.

## Task 2 -- Complete Phase 2 for all three projects

Once each project's fake-test file is excluded:
1. Full-run baseline again (same rule as the original Phase 2 handoff --
   full suite, not `--collect-only`).
2. Add `conftest.py` per the same pattern used on the other 7 projects.
3. Re-run, compare collected count against this new baseline (post-
   exclusion, not the original blocked baseline).
4. `test_eval_incremental.py` and `test_p115_write.py` will still fail or
   error -- that's expected and correct, they're real bugs, not something
   this task fixes. Collected count should include them (pytest can still
   find them), they just won't pass.

## Task 3 -- File two follow-on WOs

Standard WO template, same shape as the others in this ledger (Status /
Owner / Affects / Depends On / WHY / Scope / Acceptance Criteria /
Completion Gate). Check `Agentic-Hub-Governance\work_orders\` for the
current highest P_300 and P_800 extension numbers before assigning IDs --
don't guess.

**WO 1 -- P_300, `test_eval_incremental.py`:** `assemble_incremental_post_batch`
is imported from `domain.eval_incremental` but doesn't exist there.
Cross-reference WO-P000-E10.001 (Hub-Wide Caller-Propagation Triage) --
Finding 7 in E13.001 already identifies this as WO-P000-E10.001's own miss
(it moved this function and didn't catch this test caller). Consider
whether this WO belongs to P_300 or should be a correction folded into
E10.001 itself -- state your reasoning either way, don't default to P_300
just because that's where the test file sits.

**WO 2 -- P_800, `test_p115_write.py`:** `P115Record` schema now requires
`signal_date` and `written_by`; the test's sample data predates that
requirement (real schema drift, not a test bug). Owner P_800.

Report back with: which projects unblocked cleanly, the P_300 backup-file
decision (excluded vs deleted), and the two new WO IDs assigned.
