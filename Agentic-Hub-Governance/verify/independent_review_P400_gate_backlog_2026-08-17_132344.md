# Independent Review Task -- P_400 Gate Backlog

**Staged:** 2026-08-17, P_000 session (claude.ai). This session found these
four WOs but cannot review them itself -- it's the session that would be
reviewing, not implementing, so it's structurally eligible, but `python.exe`
hangs through windows-mcp every time, so no test suite can actually be run
from there. Handed to Claude Code CLI, which runs local commands directly.

**Run this from the Hub root:**
```
cd C:\Users\Trader\AI-Agent-Learning-Hub
claude
```
Then paste this file's path, or paste this whole brief.

---

## What "Independent Review" means here

Per `Agentic-Hub-Governance\work_orders\WO_COMPLETION_GATE.md`: a session
that did NOT implement the WO re-reads the WO's Acceptance Criteria against
the actual code and output, and confirms each item independently -- not by
trusting the WO's own self-reported "VERIFY -- FINAL" section. You (this
Claude Code session) did not implement any of these four. You qualify.

**Do not rubber-stamp.** If a test count doesn't match what the WO claims,
if a file doesn't match the Execution table, or if you can't confirm
something, stop and report the discrepancy in the WO file rather than
checking the box anyway. A wrong CLOSED is worse than a WO left at
OWNER_DONE with an honest note.

---

## The four WOs

All four live in `Agentic-Hub-Governance\work_orders\`, all `Owner: P_400`,
all `Affects: none -- internal P_400 only`, all currently `OWNER_DONE` with
no Completion Gate block at all.

| WO | Claim to verify | Test file(s) claimed |
|---|---|---|
| `WO-P400-E4.004.md` | Spread-plausibility gate (`MAX_PLAUSIBLE_SPREAD_PCT`) blocks before R:R math corrupts on a wide spread | `test_evaluate_signal.py` -- 10/10 incl. `test_spread_too_wide_blocks_before_rr_math`, `test_spread_under_threshold_not_blocked_by_spread_gate` |
| `WO-P400-E4.005.md` | `is_market_open_now()` computes real wall-clock market state instead of hardcoded `True` | `test_market_hours.py` -- 7/7 |
| `WO-P400-E4.006.md` | Holiday-aware market calendar (`domain\market_holidays.py`, rule-based, no dependency) wired into both `market_hours.py` and `_sessions_since_earnings()` | `test_market_holidays.py` -- 13 tests (NEW); `test_market_hours.py` +1; `test_evaluate_signal.py` +1 |
| `WO-P400-E5.001.md` | `record --paper` overrides `trade_mode` at fill time, call-scoped, never mutates `eval_cache` | `test_record_commands.py` -- 11/11 (8 pre-existing + 3 new) |

Project root: `projects\P_400_TradeOrderManagement\python\`
Python: `C:\Users\Trader\.conda\envs\p140\python.exe` (p140 env, never a new venv)

---

## Steps

1. Read each WO's full file -- the WHY, Scope/Execution table, and VERIFY
   section already there. That's the claim; you're checking it, not
   trusting it.
2. From `projects\P_400_TradeOrderManagement\python\`, run the full suite:
   ```
   C:\Users\Trader\.conda\envs\p140\python.exe -m pytest -q
   ```
   Compare the pass count against each WO's own claimed number (270 for
   E4.004/E4.005, 285 for E4.006, and E5.001's local 11/11 -- note E5.001
   was verified 2026-07-29, two days after E4.006's 285, so the current
   full-suite count should be >= 285, not 270 or 285 exactly if anything
   shipped between).
3. Spot-check the actual changed files listed in each Execution table
   still exist and roughly match the described change (line counts,
   function names) -- `domain\market_holidays.py`, `domain\market_hours.py`,
   `application\evaluate_signal.py`, `application\record_commands.py`,
   `cli.py`, `config.py`, `domain\council_codes.py`,
   `application\tape_block.py`.
4. For each WO, copy the current Completion Gate checklist template from
   `Agentic-Hub-Governance\work_orders\WO_COMPLETION_GATE.md` (the block
   under "Completion Gate Checklist" -- includes Caller Propagation and
   Imperative Sweep items, added 2026-08-03) into the WO file, fill it
   honestly based on what you actually checked, and add an
   `## Independent Review` section: date, this being a separate
   session/tool from the implementer, and the pytest result you personally
   ran.
5. If everything checks out clean: move `Status` from `OWNER_DONE` to
   `CLOSED`. If anything doesn't check out: leave at `OWNER_DONE`, write
   exactly what didn't match, and stop -- don't fix it silently in the
   same pass as the review (that would make you the implementer again).
6. Backup each WO file before editing (`Copy-Item` with a timestamp suffix,
   same as any other Hub write), `[System.IO.File]::WriteAllText(...,
   [System.Text.UTF8Encoding]::new($false))`, verify with `.Contains()`
   before/after.

---

## One more thing found while staging this, not part of the four above

`p400-project-context` SKILL.md's "Bugs Already Fixed" table (around line
204) documents E4.005, E4.006, E5.001, and five others -- but **not
E4.004**, despite E4.004 fixing a real live bug (the CAE spread
corruption) and the skill file's own Update trigger requiring a Bugs row
+ matching test for any WO that fixes a bug here, same session. This is
the same doc-sync gap class this file's changelog already lists five
prior instances of (E5.001 sat 14 days, WO-P800-E3.003's rename sat 2
days, etc.). Add the row while you're in this file for the other four --
same pattern as the existing E4.005/E4.006 rows, referencing
`MAX_PLAUSIBLE_SPREAD_PCT` / the spread-plausibility gate / `test_spread_
too_wide_blocks_before_rr_math`.