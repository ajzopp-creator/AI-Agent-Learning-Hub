# WO_COMPLETION_GATE.md
# Location: Agentic-Hub-Governance\work_orders\WO_COMPLETION_GATE.md
# Owner: P_000
# Loaded by INIT every session. Governs all WO closures Hub-wide.
# Last updated: 2026-06-09 (WO-P000-E3.001)

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
[ ] Downstream projects in Affects: notified (WO comment or session note)
[ ] No sys.path side-channels introduced (ref WO-P000-E2.003)
[ ] If schema/signal contract changed: version bumped, consuming projects notified
[ ] DRAFT files for this WO deleted from Agentic-Hub-Governance\work_orders\
[ ] One ledger entry per WO confirmed
```

---

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
