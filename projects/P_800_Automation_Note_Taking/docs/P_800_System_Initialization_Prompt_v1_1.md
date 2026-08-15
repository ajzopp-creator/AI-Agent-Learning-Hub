# P_800 System Initialization Prompt (SIP) v1.1

**File:** `docs/P_800_System_Initialization_Prompt_v1_1.md`
**Version:** 1.2
**Last Updated:** 2026-08-07
**Pairs With:** `docs/P_800_SYSTEM_DOCUMENTATION.md` (v3.0) + `system-doc-initializer` SKILL

---

## Purpose

Bootstraps every P_800 chat: loads system version, vault state, work orders, account params, market posture.

## Trigger

`INIT` | `P_800` | `P_800 INIT`

---

## INIT Sequence — complete Steps 0-7 before writing code or taking action

### Step 0 — Environment Discovery (Silent)
`tool_search("PowerShell")`. Present -> proceed. Absent -> fall back to project-attached snapshots, skip Step 5, warn in Step 6.

### Step 0.5 — Work Order Review
Query `Agentic-Hub-Governance\work_orders\`:
- Owner=P_800, status not CLOSED -> display, **HALT** if action required before session
- P_800 in Affects, Ack pending -> display, **ACTION REQUIRED** after session

Ledger unavailable -> proceed with inline note.

### Step 1 — Session Header
Display: `P_800 [Day], [Month] [DD], [YYYY] [HH:MM] ET [optional label]`
Time via `windows-mcp:PowerShell`, fallback `time not available`.

### Step 2 — Verify SKILL Loaded
Confirm `system-doc-initializer` active by referencing one rule unprompted. Missing -> request manual paste, do not proceed.

### Step 3 — Load Working State
Read (filesystem MCP, live disk):
- `docs\P_800_SYSTEM_DOCUMENTATION.md` -- master state, version, vault path, build phase, error log
- `docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` -- vault structure, YAML schemas
- `docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` -- bases, dashboard, Python writers

System doc missing -> **HALT**, verify `docs\` manually. Interface arch docs missing -> warn inline, may not yet exist, proceed.

### Step 4 — Load External Context
Read `P_000_Account_Parameters_Current.md` (balance, risk budget, max position) and `P_010_RiskConfig.json` (SPY/QQQ avg, risk mode). Either missing -> note unavailable, do not invent, proceed.

### Step 5 — Vault State Check
Skip with warning if MCP unavailable. Via `windows-mcp:PowerShell`:
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
Vault root missing -> **HALT**, verify path before proceeding.

### Step 6 — Session Summary
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
  TradeManagement/P115    [OK|X] · <N> files
  TradeManagement/P300    [OK|X] · <N> files
  TradeManagement/P400    [OK|X] · <N> files
  TradeManagement/P020    [OK|X] · <N> files
  KnowledgeBase/          [OK|X] · <N> files
  Bases/                  [OK|X] · <N> files
  Dashboard.md            [OK|X]

Active phase:    Phase <N> — <phase name>
Next task:       <first incomplete item from build roadmap>
─────────────────────────────────────────────────────────────
```

### Step 7 — Confirm Session Focus
Ask: "Proceeding with `<next task>`, or steering elsewhere?" Wait for confirmation -- do NOT propose work or act until confirmed.

---

## Fail-Fast Conditions

| Condition | Action |
|-----------|--------|
| SKILL not loaded | Request manual paste; do not proceed |
| System doc missing | HALT; verify `docs\` folder |
| Vault root missing | HALT; verify path before vault work |
| `windows-mcp:PowerShell` unavailable | Notify; skip Step 5; vault state unknown |
| P_000 or P_010 missing | Note unavailable; do not invent; proceed |
| Work order blocks session | HALT; resolve first |

Never proceed past a HALT silently.

## This SIP Does NOT
Load full architecture docs into context (on-demand only) · duplicate SKILL content · write code/files · assume prior chat context.

---

## Quick Reference

| Resource | Path |
|----------|------|
| Project root | `...\projects\P_800_Automation_Note_Taking\` |
| Vault root | `...\trading_journal\` |
| System doc | `...\docs\P_800_SYSTEM_DOCUMENTATION.md` |
| Interface arch pt1/pt2 | `...\docs\P_800_Interface_Arch_Part{1,2}_*.md` |
| Python env | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| P_000 params | `...\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| P_010 posture | `...\P_010_Current_Market_Posture\P_010_RiskConfig.json` |
| Work orders | `Agentic-Hub-Governance\work_orders\` |

**Standing rules:** P_800 is READ-ONLY relative to every other project -- never write to P_010/P_115/P_300/P_020 or source files. P_800 owns templates -- never create/modify them elsewhere. Excel tracker is source of truth -- TradeManagement/ is a one-way mirror only. 300 lines max/file · 50 lines max/function · one file/code block · plan files with line counts before writing code.

---

## Manual Fallback
```
P_800 INIT. Read in order: (1) P_800_SYSTEM_DOCUMENTATION.md, (2) Interface Arch Part1, (3) Part2, (4) P_000_Account_Parameters_Current.md, (5) P_010_RiskConfig.json. Run vault state PowerShell (Step 5). If missing, note unavailable. Display session summary. Ask session focus. Do not propose work until confirmed.
```

---

## Changelog

### v1.2 -- 2026-08-07
- Session header fixed to canonical Hub-wide format (ref WO-P000-E4.001) -- was still the pre-revision `[Day, Month DD, YYYY -- HH:MM ET]` draft.
- Compressed 192 -> 140 lines: tightened step prose, condensed Quick Reference paths, trimmed footer. No step, HALT condition, or path removed.
- Prior: v1.1 (2026-06-04) added Step 0.5 Work Order Review; compressed 213->150 at the time (later regrew to 192 through subsequent additions -- noting since the earlier line-count claim no longer matched reality on disk).

### v1.0 -- 2026-05-22
Initial release, adapted from P_300 v2.7.

---

*Owner: Anthony Zoppi · Pairs with P_800_SYSTEM_DOCUMENTATION.md v3.0*
