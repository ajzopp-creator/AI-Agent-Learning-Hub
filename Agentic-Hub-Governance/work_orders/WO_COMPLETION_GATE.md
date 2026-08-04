# WO_COMPLETION_GATE.md
# Location: Agentic-Hub-Governance\work_orders\WO_COMPLETION_GATE.md
# Owner: P_000
# Loaded by INIT every session. Governs all WO closures Hub-wide.
# Last updated: 2026-07-27 (checklist now includes project skill files -- WO-P800-E3.003 renamed a shared vault path and went 2 days undetected in p400-project-context skill, since only CLAUDE.md/P_000 doc were checked)
# Last updated: 2026-08-03 (added Caller Propagation + Imperative Sweep checks -- WO-P115-E2.001 wired support fields into emit_signal() but never into cli.py, the only entry point, and closed anyway; architecture v1.3 removed P_115 sizing but was logged only in changelogs while 9 imperative rules still commanded sizing. Both closed on "the owning layer is done." Ref WO-P115-E3.001)
# Last updated: 2026-07-29 (added Enforcement section -- Completion Gate block must exist at time OWNER_DONE is set, not backfilled later; ref EC-005, WO-P000-E9.001)

---

## Purpose

No work order is COMPLETE until this checklist is satisfied.
The closing project fills it out. P_000 verifies any WO that affects
shared resources or downstream projects.

---

## Completion Gate Checklist

Copy this block into the WO before marking OWNER_DONE:

```
## Completion Gate (ref WO-P000-E3.001)

[ ] All file paths use Hub canonical paths (see WO_COMPLETION_GATE.md)
[ ] Any new or changed shared-resource location reflected in:
    - P_000_SYSTEM_DOCUMENTATION.md (Document Index section)
    - Affected project CLAUDE.md files
    - Affected project skill files (.claude\skills\*\SKILL.md) referencing the changed path
[ ] CALLER PROPAGATION: for every capability added, changed, or REMOVED,
    each entry point / caller that must use it has been updated in the same
    WO -- not just the owning module. Name the callers checked. A parameter
    the CLI cannot pass is not delivered. (ref WO-P115-E2.001)
[ ] IMPERATIVE SWEEP: if this WO changed a RULE, the change is reflected in
    the imperative text that drives behavior -- Musts, Must Nots,
    anti-patterns, workflow command lines, NEVER VIOLATE blocks, and the
    claude.ai Project Instructions -- not only in a changelog entry.
    A changelog is a record, not a rule. (ref WO-P115-E3.001)
[ ] Downstream projects in Affects: notified (WO comment or session note)
[ ] No sys.path side-channels introduced (ref WO-P000-E2.003)
[ ] If schema/signal contract changed: version bumped, consuming projects notified
[ ] DRAFT files for this WO deleted from Agentic-Hub-Governance\work_orders\
[ ] One ledger entry per WO confirmed
```

---

## Independent Review Requirement

The session that implements a WO does not close it. Before OWNER_DONE moves
to CLOSED, a separate session -- a fresh chat, or a Claude Code subagent, not
the one that wrote the fix -- re-reads the WO's Acceptance Criteria against
the actual code and output, and confirms each box independently.

Reason: the implementing session grading its own work is how the ten P_400 /
P_300 WOs sat OWNER_DONE with an empty Completion Gate checklist for weeks --
nothing forced a second look before self-certifying done.

This applies Hub-wide, to every project, no exceptions for small WOs.

## Why Caller Propagation and Imperative Sweep Exist

Both were added 2026-08-03 after two failures with the same shape, found in
one session:

1. **WO-P115-E2.001** built `intelliscan_support_1/2` into `emit_signal()`
   and closed. `cli.py` -- the only entry point in use -- never defined the
   arguments or passed them. The feature existed and was unreachable for
   seven weeks.

2. **Architecture v1.3** removed order management from P_115 and recorded it
   in three changelogs. Nine imperative rules across four surfaces still
   instructed P_115 to size positions and run options gates. A live P_116
   signal (ZION, 2026-08-03) produced a full three-gate block, a fabricated
   7.09:1 R:R, and an options-chain request -- all P_400's.

Both closed on "the owning layer is done." Neither checked the layer that
calls it, or the text that commands it. The owning layer is the start of a
change, not the end.

---

## Never Touch

These are known, Hub-wide. No WO overrides this list without a new WO
that explicitly supersedes the entry.

| Path / item | Reason |
|---|---|
| `tracker_reader.py` line 24 | Deliberately left on old D_130 reference for backward compatibility (D_130->P_110 rename audit) |
| 17 frozen/archived files from D_130->P_110 rename audit | Frozen intentionally; do not update to P_110 |
| `WO-P000-E1.002_backup_2026-06-05.md` and any `*_backup_*.md` in the live ledger folder | Backups only, not registered WOs; do not treat as OPEN or action their contents |
| `claude_desktop_config.json` | Must be written with `[System.IO.File]::WriteAllText()`, no BOM; `isDxtAutoUpdatesEnabled: false` -- editing carelessly reverts config |
| `.env` files anywhere in the Hub | Never read or modify |
| git operations via windows-mcp | Always hangs -- credential helper conflict. Use Anaconda Prompt or Claude Code CLI directly, never git.exe through MCP |

## Hub Canonical Path Standards

| What | Canonical Path |
|------|---------------|
| Work order ledger | `Agentic-Hub-Governance\work_orders\` |
| Shared code library | `shared_resources\python_utils\` |
| vault_interface.py | `shared_resources\python_utils\vault_interface.py` |
| Account parameters | `projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| Schwab Token Manager | `integrations\schwab_api\` |
| Hub editable install | `pyproject.toml` at Hub root |
| p140 interpreter | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| LM Studio API | `integrations\lm_studio\` |

---

## INIT Daily Check

At session start P_000 INIT confirms:
- Any WO marked OWNER_DONE since last session has this checklist present and complete
- No DRAFT files are orphaned in the ledger alongside a registered WO
- Affects: field is populated on all OPEN/PENDING WOs
