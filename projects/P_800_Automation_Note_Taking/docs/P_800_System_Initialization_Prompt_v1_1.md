# P_800 System Initialization Prompt (SIP) v1.1

**File:** `docs/prompts/P_800_System_Initialization_Prompt_v1_1.md`  
**Version:** 1.1  
**Last Updated:** 2026-06-04  
**Pairs With:** `docs/P_800_SYSTEM_DOCUMENTATION.md` (v3.0) + `system-doc-initializer` SKILL

---

## Purpose

Bootstraps every new P_800 chat. Loads system version, vault state, work orders, account params, and market posture so the AI starts oriented.

---

## How to Trigger

```
INIT  |  P_800  |  P_800 INIT
```

---

## INIT Sequence (Execute in Order)

**RULE: Complete Steps 0 through 7 before writing code or taking action.**

### Step 0 — Environment Capability Discovery (Silent)

Call `tool_search("PowerShell")`. If `windows-mcp:PowerShell` returned, proceed. If absent, fall back to project-attached snapshots; skip Step 5; warn in Step 6.

### Step 0.5 — Work Order Review

Query shared work order ledger at `C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\`:
- **Owner=P_800, status not CLOSED** → Display; **HALT** if action required before session
- **P_800 in Affects, Ack pending** → Display; **ACTION REQUIRED** after session work

If ledger unavailable, proceed with inline note.

### Step 1 — Session Header

Display: `P_800 [Day, Month DD, YYYY — HH:MM ET]`  
Get time via `windows-mcp:PowerShell` or fallback to `time not available`.

### Step 2 — Verify SKILL Loaded

Confirm `system-doc-initializer` SKILL active by referencing one rule unprompted. If missing: request manual paste; do not proceed.

### Step 3 — Load Working State Files

Read via filesystem MCP (live disk):
- `docs\P_800_SYSTEM_DOCUMENTATION.md` — master state, version, vault path, build phase, error log
- `docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` — vault structure, YAML schemas
- `docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` — bases, dashboard, Python writers

**If system doc missing: HALT** — verify docs\ folder manually.  
**If interface arch docs missing:** warn inline; they may not yet exist; proceed.

### Step 4 — Load External Context

Read:
- `P_000_Account_Parameters_Current.md` → balance, risk budget, max position
- `P_010_RiskConfig.json` → SPY/QQQ avg, risk mode

If either missing: note unavailable; do not invent; proceed.

### Step 5 — Vault State Check

Run via `windows-mcp:PowerShell` (skip with warning if MCP unavailable):
```powershell
$vault = "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal"
$folders = @("TradeManagement\P115","TradeManagement\P300","TradeManagement\P400","TradeManagement\P020","KnowledgeBase","Bases")
foreach ($f in $folders) {
    $p = "$vault\$f"; $exists = Test-Path $p
    $count = if ($exists) { (Get-ChildItem $p -File -EA SilentlyContinue).Count } else { 0 }
    Write-Output "$f | exists=$exists | files=$count"
}
Write-Output "Dashboard.md | exists=$(Test-Path "$vault\Dashboard.md")"
```

**If vault root missing: HALT** — verify path before proceeding.

### Step 6 — Display Session Summary

```
─────────────────────────────────────────────────────────────
P_800 SESSION INITIALIZED
─────────────────────────────────────────────────────────────
System Doc:      P_800_SYSTEM_DOCUMENTATION.md v<X.X>
Filesystem MCP:  [available | unavailable]
SKILL status:    [loaded | NOT LOADED]
Work Orders:     [status or OK]
Account:         $<balance> · Risk $<budget> · Max pos $<max>
Market posture:  SPY <p> / QQQ <p> · Avg <avg> · Mode <mode>

Vault: C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\
  TradeManagement/P115    [✓ | ✗] · <N> files
  TradeManagement/P300    [✓ | ✗] · <N> files
  TradeManagement/P400    [✓ | ✗] · <N> files
  TradeManagement/P020    [✓ | ✗] · <N> files
  KnowledgeBase/          [✓ | ✗] · <N> files
  Bases/                  [✓ | ✗] · <N> files
  Dashboard.md            [✓ | ✗]

Active phase:    Phase <N> — <phase name>
Next task:       <first incomplete item from build roadmap>
─────────────────────────────────────────────────────────────
```

### Step 7 — Confirm Session Focus

Ask:
> "Proceeding with `<next task>`, or steering elsewhere?"

Wait for operator confirmation. Do NOT propose work or take action until confirmed.

---

## What This SIP Does NOT Do

Load full architecture docs into context (on-demand only), duplicate SKILL content, write code/files, or assume previous chat context.

---

## Fail-Fast Conditions

| Condition | Action |
|-----------|--------|
| SKILL not loaded | Request manual paste; do not proceed |
| `P_800_SYSTEM_DOCUMENTATION.md` missing | HALT; verify docs\ folder |
| Vault root `trading_journal\` missing | HALT; verify path before vault work |
| `windows-mcp:PowerShell` unavailable | Notify; skip Step 5; note vault state unknown |
| P_000 or P_010 missing | Note unavailable; do not invent; proceed |
| Work order blocks session | HALT; resolve first |

Never proceed past a HALT condition silently.

---

## Quick Reference

| Resource | Path |
|----------|------|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\` |
| Vault root | `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` |
| System doc | `...\docs\P_800_SYSTEM_DOCUMENTATION.md` |
| Interface arch pt1 | `...\docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` |
| Interface arch pt2 | `...\docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` |
| Python env | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| P_000 params | `C:\...\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| P_010 posture | `C:\...\P_010_Current_Market_Posture\P_010_RiskConfig.json` |
| Work orders | `C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\work_orders\` |

### Standing Rules

- **P_800 READ-ONLY** relative to all other projects — never write to P_010, P_115, P_300, P_020, or source files
- **P_800 owns templates** — never create/modify templates elsewhere
- **Excel tracker SoT** — TradeManagement/ is one-way mirror only
- **300 lines max/file · 50 lines max/function · one file/code block**
- **Plan all files with line counts BEFORE writing code**

---

## Manual Fallback

If SKILL unavailable, paste:
```
P_800 INIT.

Read in order: (1) P_800_SYSTEM_DOCUMENTATION.md, (2) Interface Arch Part1, (3) Part2,
(4) P_000_Account_Parameters_Current.md, (5) P_010_RiskConfig.json.

Run vault state PowerShell (Step 5). If missing, note unavailable.

Display session summary. Ask session focus. Do not propose work until confirmed.
```

---

## Changelog

### v1.1 — 2026-06-04
- Added STEP 0.5 Work Order Review (governance).
- Compressed from 213 → 150 lines: condensed purpose, tightened Step 0, removed build phase snapshot table, collapsed manual fallback, removed prior changelog entries.

### v1.0 — 2026-05-22
Initial release. Adapted from P_300_System_Initialization_Prompt_v2.7. Key differences: vault state check (Step 5) replaces catalog reconciliation; `system-doc-initializer` SKILL; P_800 paths; build roadmap from Interface Arch Part 2.

---

*P_800 System Initialization Prompt v1.1 — 2026-06-04*
*Owner: Anthony Zoppi · Pairs with P_800_SYSTEM_DOCUMENTATION.md v3.0*
