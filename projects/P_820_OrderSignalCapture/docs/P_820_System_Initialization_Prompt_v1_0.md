# P_820 System Initialization Prompt (SIP) v1.0

**File:** `docs/P_820_System_Initialization_Prompt_v1_0.md`
**Version:** 1.0
**Last Updated:** 2026-08-16
**Pairs With:** `docs/P_820_SYSTEM_DOCUMENTATION.md` (v1.0) + `p820-project-context` SKILL

---

## Purpose

Bootstraps a P_820 session: confirms the skill is loaded, checks the
vault output folder, and gets Claude ready to capture a dictated
signal. Deliberately lighter than P_800's SIP -- P_820 has one folder
to check and no external dependencies to load.

## Trigger

`INIT` | `P_820` | `P_820 INIT`

Also fires implicitly any time Tony dictates a signal in a session
where the skill hasn't been confirmed loaded yet -- see Step 2.

---

## INIT Sequence -- complete Steps 0-5 before logging a signal

### Step 0 -- Environment Discovery (Silent)
`tool_search("PowerShell")`. Present -> proceed to Step 0.5. Absent ->
skip Step 4 (vault state check), warn in Step 5, still usable --
`write_to_vault()` will fail loudly on its own if the environment
truly can't write.

### Step 0.5 -- Work Order Review
Query `Agentic-Hub-Governance\work_orders\` for Owner=P_820 or P_820 in
Affects, status not CLOSED. None exist as of this SIP's writing --
proceed. If the ledger is unavailable, proceed with an inline note
(matches P_800's SIP fallback).

### Step 1 -- Session Header
Display: `P_820 [Day], [Month] [DD], [YYYY] [HH:MM] ET [optional label]`
Time via `windows-mcp:PowerShell`, fallback `time not available`.

### Step 2 -- Verify SKILL Loaded
Confirm `p820-project-context` active by referencing one rule
unprompted (e.g. the resolver priority, or the snake_case field
rule). Missing -> read
`<Hub>\.claude\skills\p820-project-context\SKILL.md` directly before
proceeding -- do not guess the field list from memory.

### Step 3 -- Load Working State (on demand, not required every session)
Read `docs\P_820_SYSTEM_DOCUMENTATION.md` only if the session needs
more than the skill file covers (e.g. reviewing the routing table in
full, or updating this documentation itself). For a routine
"log this signal" request, the skill file alone is sufficient --
do not reflexively load the full system doc.

### Step 4 -- Vault State Check
Skip with warning if MCP unavailable (Step 0). Via
`windows-mcp:PowerShell`:
```powershell
$vault = "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\TradeOrderManagement\P820"
$exists = Test-Path $vault
$count = if ($exists) { (Get-ChildItem $vault -File -EA SilentlyContinue).Count } else { 0 }
Write-Output "P820 | exists=$exists | files=$count"
```
Folder missing -> not a HALT condition (P_800's `write_to_vault()`
creates it on first write) -- note it and proceed.

### Step 5 -- Session Summary
```
-----------------------------------------------------------------
P_820 SESSION INITIALIZED
-----------------------------------------------------------------
System Doc:      P_820_SYSTEM_DOCUMENTATION.md v<X.X>
Filesystem MCP:  [available | unavailable]
SKILL status:    [loaded | NOT LOADED]
Work Orders:     [status or OK]

Vault: C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\
  TradeOrderManagement/P820   [OK|X] · <N> files

Ready to log a signal. Give me: symbol, source (P_116/P_117/SNT/
P_118/P_910/P_920/WSZ/etc.), and date -- entry/stop/target/notes if
you have them.
-----------------------------------------------------------------
```

No Step 7-style "confirm session focus" gate -- unlike P_800, P_820
has exactly one workflow (log a signal), so the summary itself is the
invitation to proceed. If Tony's message already contains a signal to
log, skip straight to logging it; don't make him repeat it after INIT.

---

## Fail-Fast Conditions

| Condition | Action |
|---|---|
| SKILL not loaded | Read the skill file directly before proceeding; do not guess field names or the routing table from memory |
| `windows-mcp:PowerShell` unavailable | Notify; skip Step 4; vault state unknown, but logging can still be attempted |
| Vault output folder missing | Not a HALT -- note it, proceed; `write_to_vault()` creates it |
| Work order blocks session | HALT; resolve first (same as every Hub project) |

Never proceed past a HALT silently.

## This SIP Does NOT
Load the full system documentation by default (on-demand only, Step 3)
· duplicate skill content · perform any evaluation or scoring logic ·
assume prior chat context.

---

## Quick Reference

| Resource | Path |
|---|---|
| Project root | `...\projects\P_820_OrderSignalCapture\` |
| Skill file | `...\.claude\skills\p820-project-context\SKILL.md` |
| System doc | `...\docs\P_820_SYSTEM_DOCUMENTATION.md` |
| Vault output | `trading_journal\TradeOrderManagement\P820\` |
| Vault write API | `shared_resources\python_utils\vault_interface.py` |
| Work orders | `Agentic-Hub-Governance\work_orders\` |

**Standing rules:** P_820 has no Python code and no evaluation logic --
if a session drifts toward adding either, stop and flag it rather than
building it. Resolver priority is fixed: P_820 > ThinkLog > Tracker >
default. `signal_date` is always resolved to a real date before
writing, never passed through as a relative string.

---

## Manual Fallback
```
P_820 INIT. Confirm p820-project-context skill is loaded (state one
rule unprompted). Check vault folder
trading_journal\TradeOrderManagement\P820\ exists (not a HALT if
missing). Display session summary. Ready to log a signal immediately
-- no separate confirmation step needed.
```

---

## Changelog

### v1.0 -- 2026-08-16
Initial release, adapted from P_800's SIP v1.2 structure and
condensed for P_820's much smaller scope -- one vault folder instead
of six, no Interface Arch docs to load, no session-focus confirmation
gate (single workflow only).

---

*Owner: Anthony Zoppi · Pairs with P_820_SYSTEM_DOCUMENTATION.md v1.0*
