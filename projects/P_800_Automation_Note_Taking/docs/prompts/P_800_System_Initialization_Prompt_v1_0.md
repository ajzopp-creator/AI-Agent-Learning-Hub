# P_800 System Initialization Prompt (SIP) v1.0

**File:** `docs/prompts/P_800_System_Initialization_Prompt_v1_0.md`
**Version:** 1.0
**Last Updated:** 2026-05-22
**Pairs With:** `docs/P_800_SYSTEM_DOCUMENTATION.md` (v3.0)
**Companion Docs:**
  - `docs/P_800_Interface_Arch_Part1_Schemas_v1_0.md`
  - `docs/P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md`
**SKILL Companion:** `system-doc-initializer` (auto-loads in P_800 Claude Project)

---

## Purpose

Bootstraps every new P_800 chat. Loads live operating state — system version,
vault folder state, active build phase, account params, market posture — so the
AI starts oriented instead of cold.

The SIP works with the auto-loading `system-doc-initializer` SKILL. The SKILL
provides protection rules and schema shorthand; the SIP loads live state.

---

## How to Trigger

```
INIT
P_800
P_800 INIT
```

If the SKILL auto-loaded successfully, the AI executes the INIT sequence below
automatically. If not, paste the contents of this file directly.

---

## INIT Sequence (Mandatory Execution Order)

### Step 0 — Environment Capability Discovery (Silent Pre-Check)

BEFORE displaying anything, call `tool_search("PowerShell")`.

| Result | Environment | Implication |
|--------|-------------|-------------|
| `windows-mcp:PowerShell` returned | Claude Desktop — Tony's Windows machine | Live disk reads available for Steps 3–5 |
| Nothing returned | claude.ai web — sandboxed Linux | Fall back to project-attached doc snapshots; Step 5 is skipped with a warning |

Per system-doc-initializer SKILL: NEVER claim the environment without running
`tool_search` first. Client identity is not reliably detectable from the system
prompt; tool availability IS.

### Step 1 — Session Header

Display exactly:

```
P_800 [Day, Month DD, YYYY — HH:MM ET]
```

**Wall-clock time:** attempt `windows-mcp:PowerShell`:
```powershell
[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId(
  [DateTime]::UtcNow, "Eastern Standard Time"
).ToString("dddd, MMMM dd, yyyy — HH:mm")
```
Fallback if unavailable: `P_800 [Friday, May 22, 2026 — time not available]`

### Step 2 — Verify SKILL Loaded

Confirm `system-doc-initializer` SKILL is active by referencing one of its
rules unprompted (e.g., the 300-line file limit or P_800 read-only boundary).

If NOT loaded:
- Notify Tony
- Request manual paste of SKILL.md from project knowledge
- Do not proceed until SKILL content is in context

### Step 3 — Load Working State Files

Read via filesystem MCP (live disk — NOT project-attached snapshots, which lag):

| File | Purpose |
|------|---------|
| `C:\...\P_800_Automation_Note_Taking\docs\P_800_SYSTEM_DOCUMENTATION.md` | Master state — version, vault path, build roadmap, error log, parameter registry |
| `C:\...\P_800_Automation_Note_Taking\docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` | Interface layer — architecture, vault structure, all five YAML schemas |
| `C:\...\P_800_Automation_Note_Taking\docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` | Bases definitions, dashboard design, Python writer plan, build roadmap |

Full paths (expand `...` to hub root `C:\Users\Trader\AI-Agent-Learning-Hub\projects`):

**If system doc is missing, HALT:**
> "Cannot proceed — P_800_SYSTEM_DOCUMENTATION.md not found at expected path.
> Verify the docs\ folder before starting any session work."

Interface arch docs: if missing, warn inline and proceed — they are newer and
may not yet exist on disk; Tony is aware.

### Step 4 — Load External Context

| File | Purpose |
|------|---------|
| `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` | Account balance, risk budget, max position |
| `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json` | Market posture — SPY/QQQ avg, risk mode |

If either file is missing: note unavailable; do not invent values; proceed.

### Step 5 — Vault State Check

Run via `windows-mcp:PowerShell` (skip and warn if MCP unavailable):

```powershell
$vault = "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal"
$folders = @(
    "TradeManagement\P115",
    "TradeManagement\P300",
    "TradeManagement\P400",
    "TradeManagement\P020",
    "KnowledgeBase",
    "Bases"
)
foreach ($f in $folders) {
    $p = "$vault\$f"
    $exists = Test-Path $p
    $count = if ($exists) {
        (Get-ChildItem $p -File -ErrorAction SilentlyContinue).Count
    } else { 0 }
    Write-Output "$f | exists=$exists | files=$count"
}
$dash = Test-Path "$vault\Dashboard.md"
Write-Output "Dashboard.md | exists=$dash"
```

Capture: folder existence, file count per folder, Dashboard.md presence.

**If vault root missing, HALT:**
> "trading_journal\ not found. Verify vault path before proceeding."

### Step 6 — Display Session Summary

Output exactly this format (fill in actual values):

```
─────────────────────────────────────────────
P_800 SESSION INITIALIZED
─────────────────────────────────────────────
System Doc:      P_800_SYSTEM_DOCUMENTATION.md  v<X.X>
Filesystem MCP:  [available | unavailable]
SKILL status:    [loaded | NOT LOADED]
Account:         $<balance> · Risk $<budget> · Max pos $<max>
Market posture:  SPY <p> / QQQ <p> · Avg <avg> · Mode <mode>

Vault: C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\
  TradeManagement/P115    [✓ | MISSING] · <N> files
  TradeManagement/P300    [✓ | MISSING] · <N> files
  TradeManagement/P400    [✓ | MISSING] · <N> files
  TradeManagement/P020    [✓ | MISSING] · <N> files
  KnowledgeBase/          [✓ | MISSING] · <N> files
  Bases/                  [✓ | MISSING] · <N> .base files
  Dashboard.md            [✓ | MISSING]

Active phase:    Phase <N> — <phase name>
Next task:       <first incomplete item from build roadmap>
─────────────────────────────────────────────
```

### Step 7 — Confirm Session Focus

Ask one question:

> "Proceeding with `<next task>` as the session focus, or steering elsewhere?"

Wait for Tony's confirmation or redirection. Do NOT propose work, write code,
or take action until Tony confirms session focus.

---

## What This SIP Does NOT Do

- Does not load full architecture docs into context — referenced on demand
- Does not duplicate SKILL content — protection rules live in the SKILL
- Does not write code or files — Tony approves a file plan first
- Does not assume previous chat context — every chat starts fresh from disk

---

## Fail-Fast Conditions

| Condition | Action |
|-----------|--------|
| SKILL not loaded | Request manual paste; do not proceed |
| `P_800_SYSTEM_DOCUMENTATION.md` missing | HALT; verify docs\ folder manually |
| Vault root `trading_journal\` missing | HALT; verify path before any vault work |
| `windows-mcp:PowerShell` unavailable | Notify; skip Step 5; note vault state unknown |
| P_000 or P_010 file missing | Note unavailable; do not invent values; proceed |
| Interface arch docs missing | Warn inline; they may not yet exist; proceed |

Never proceed past a HALT condition silently. Confirm state with Tony first.

---

## Quick Reference

### Critical Paths

| Resource | Path |
|----------|------|
| Project root | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\` |
| Vault root | `C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal\` |
| System doc | `...\docs\P_800_SYSTEM_DOCUMENTATION.md` |
| Interface arch (schemas) | `...\docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md` |
| Interface arch (bases) | `...\docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md` |
| Python writers | `...\scripts\obsidian_writers\` |
| Claude artifacts | `...\claude_artifacts\` |
| Python env | `C:\Users\Trader\.conda\envs\p140\python.exe` |
| P_000 params | `C:\...\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md` |
| P_010 posture | `C:\...\P_010_Current_Market_Posture\P_010_RiskConfig.json` |
| Dashboard | `C:\...\trading_journal\Dashboard.md` |

### Standing Rules (enforced every session)

- P_800 is READ-ONLY relative to all other projects — never writes to P_010,
  P_115, P_300, P_020, or any project's source files
- P_800 owns ALL Obsidian templates — never create or modify templates elsewhere
- Excel tracker is SoT for trades; TradeManagement/ is a one-way mirror
- 300 lines max per file · 50 lines max per function · one file per code block
- Plan all files with line counts BEFORE writing any code

### Build Phase Snapshot (as of 2026-05-22)

| Phase | Deliverable | Status |
|-------|-------------|--------|
| 5A | Vault subfolders (P115/, P300/, P400/, P020/, KnowledgeBase/) | 🔵 Next |
| 5B | Six .base files | Planned |
| 5C | Dashboard.md | Planned |
| 5D | `p115_writer.py` | Planned |
| 5E | `p300_writer.py` | Planned |
| 5F | `p020_writer.py` | Planned |
| 5G | KB Templater template | Planned |
| 5H | `p400_writer.py` | Planned (after P_400 schema locked) |

---

## Manual Fallback

If the SKILL doesn't auto-load AND this SIP isn't available, paste:

```
P_800 INIT.

Read these files in order:
1. C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\docs\P_800_SYSTEM_DOCUMENTATION.md
2. C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\docs\P_800_Interface_Arch_Part1_Schemas_v1_0.md
3. C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_800_Automation_Note_Taking\docs\P_800_Interface_Arch_Part2_Bases_Dashboard_v1_0.md
4. C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\config\P_000_Account_Parameters_Current.md
5. C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_010_Current_Market_Posture\P_010_RiskConfig.json

Then run this PowerShell to check vault state:
  $vault = "C:\Users\Trader\AI-Agent-Learning-Hub\trading_journal"
  $folders = @("TradeManagement\P115","TradeManagement\P300","TradeManagement\P400","TradeManagement\P020","KnowledgeBase","Bases")
  foreach ($f in $folders) {
      $p = "$vault\$f"; $e = Test-Path $p
      $c = if ($e) { (Get-ChildItem $p -File -EA SilentlyContinue).Count } else { 0 }
      Write-Output "$f | exists=$e | files=$c"
  }
  Write-Output "Dashboard.md | exists=$(Test-Path "$vault\Dashboard.md")"

Display the standard P_800 session summary and ask what I want to focus on.
Do not propose work until I confirm.
```

---

## Changelog

### v1.0 — 2026-05-22
Initial release. Adapted from P_300_System_Initialization_Prompt_v2.7.
Key differences: vault state check (Step 5) replaces catalog reconciliation;
`system-doc-initializer` SKILL replaces `p300-project-context`; P_800 paths
throughout; build roadmap from Interface Arch Part 2 replaces stage tracking;
no catalog DB or catalog timeout logic.

---

*P_800 System Initialization Prompt v1.0 — 2026-05-22*
*Owner: Anthony Zoppi · Pairs with P_800_SYSTEM_DOCUMENTATION.md v3.0*
