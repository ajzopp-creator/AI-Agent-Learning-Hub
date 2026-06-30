---
name: system-doc-initializer
description: >
  Session initializer for AI-Agent-Learning-Hub projects. Triggers on the FIRST
  message of any session. Verifies runtime, loads 4 critical system-doc sections,
  outputs a suggested chat name, and enforces standing protocols for Python
  architecture, file delivery, PowerShell timeouts, mixed-environment file handling,
  output integrity, and failure-loop recognition. Use at session start in any
  Claude Desktop or claude.ai project with a SYSTEM_DOCUMENTATION or MASTER_DOC file.
---

# system-doc-initializer — AI-Agent-Learning-Hub Edition

Runs silently on first message. Tony never sees this referenced unless he asks.

---

## APPROVAL GATE — NON-NEGOTIABLE

Before writing ANY file/code/change anywhere in the Hub:
1. Present complete plan (files, changes, why, save paths)
2. STOP — wait for Tony's explicit "go ahead" / "yes" / "proceed"
3. Execute only after approval

Diagnosis or being asked to investigate is NOT permission.
> Violation: diagnosed timeout → wrote 7 files across 4 projects without asking. Never repeat.

---

## Step 0 — Runtime Check (FIRST)

`tool_search(query="PowerShell")`:
- Returns `Windows-MCP:PowerShell` → **Claude Desktop**, local filesystem available
- Returns nothing → **claude.ai web**, sandboxed

Do not claim file access until this runs.

---

## Step 1 — Load System Doc (disk-canonical)

Read via filesystem/Windows-MCP:
`C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_DOCUMENTATION.md`

No filesystem access → skip to Step 5, apply protocols, proceed.

TONY_ABOUT_ME.md and TONY_STYLE_RULES.md are always-on in Project knowledge.

On-demand reference docs (read only when task needs them):

| Doc | Path (under Hub root) |
|---|---|
| Folder architecture | Trading_Projects_Folder_Architecture.md |
| LLM upgrade plan | projects\P_000_PythonClaudeLocalLLM\docs\Local_LLM_Upgrade_Plan_V2.0.md |
| Summarizer arch | projects\P_000_PythonClaudeLocalLLM\docs\Claude_Summarizer_App_Architecture.md |
| Agentic migration | projects\P_000_PythonClaudeLocalLLM\docs\Claude-Python_Agentic_Migration_1.md |
| INIT prompt | projects\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_INITIALIZATION_PROMPT_v1_0.md |
| Work-order ledger | Agentic-Hub-Governance\work_orders\ |

## Step 1b — Daily Gate Check

Read `Agentic-Hub-Governance\work_orders\WO_COMPLETION_GATE.md`:

| Check | If failed |
|---|---|
| Any WO OWNER_DONE since last session has complete Completion Gate checklist | Flag before any work |
| No orphaned DRAFT files alongside registered WOs | Delete DRAFT, note it |
| All OPEN/PENDING WOs have Affects: populated | Flag to Tony |

All clear → proceed silently. Any flag → surface before suggested chat name.

---

## Step 2 — Load 4 Sections Only

| Section | Load |
|---|---|
| 1.5 Definitions & Acronyms | all pairs |
| 3.4 AI Behavior Rules | all MUST/MUST NOT |
| 6 Error Corrections Log | all entries |
| 11.4 Parameter Registry | all fixed values — never substitute |

---

## Step 3 — Suggested Chat Name

`Suggested chat name: [Project ID] - [Topic] - MM-DD-YYYY`

---

## Step 4 — Apply All Session

Parameters (11.4) exact; behavior rules (3.4) enforced; EC log (6) checked before matching output; definitions (1.5) for terminology.

---

## Step 5 — Standing Protocols

### Protocol A — Python Architecture
Trigger: any Python creation/extension/refactor.

| Rule | Value |
|---|---|
| Approval first | Present plan, STOP until Tony approves |
| Environment | p140 only — `C:\Users\Trader\.conda\envs\p140\python.exe` |
| LLM preference | LM Studio first; Claude API only if local insufficient |
| File plan | All files + line counts BEFORE any code |
| File size | Hard 300 lines; split at 250 |
| Function size | Hard 50 lines |
| Layers | domain/=logic · infrastructure/=IO · application/=orchestration |
| One file per block | Never combine files in one code block |
| Completion marker | `FILE COMPLETE: filename (N lines)` after each file |
| No monoliths | Never put everything in main.py |

### Protocol B — File Output & Delivery
Trigger: any file created.

- **Rule 0** — Approval before action. Write nothing until Tony approves.
- **Rule 1** — Publish artifact FIRST if Tony must act on it, then give instructions.
- **Rule 2** — Always state save path: `Save to: C:\Users\Trader\AI-Agent-Learning-Hub\[project]\[subfolder]\`
- **Rule 3** — Standard paths:

| Type | Path |
|---|---|
| Python | `...\projects\[P_XXX]\python\` |
| ThinkScript | `...\projects\[P_XXX]\tos_scripts\` |
| Shared util | `...\shared_resources\python_utils\` |
| Prompt template | `...\shared_resources\llm_prompts\` |
| Skill file | `.claude\skills\[skill-name]\SKILL.md` ONLY |
| Project notes | `...\docs\project_notes\` |

- **Rule 4** — After any SKILL.md / README.md / arch ref: `To update in app: Customize → Skills → open → edit/replace`
- **Rule 5** — Delivery order: Config → Domain → Infrastructure → Application → CLI → .bat
- **Rule 6** — Never deliver incomplete files: `PAUSING — [filename] next response. Type "continue".`

### Protocol C — PowerShell Timeouts
Trigger: any session using Windows-MCP PowerShell.

Two limits: tool `timeout` param and MCP global ceiling (~240s hard, not overridable). The 240s ceiling is the dominant failure mode.

- Default 30s for trivial reads only (`Test-Path`, `Get-ChildItem`, small `Get-Content`).
- Explicit timeouts:

| Operation | Timeout (s) |
|---|---|
| pip install (single) | 120 |
| pip install -r requirements.txt | 300 |
| uvx / npx first-run | 300 |
| conda install / env update | 600 |
| Invoke-WebRequest (large) | 180 |
| Recursive Hub scans (1000+ files) | 120 |
| TOS XML export reads | 60 |

- When in doubt: 120s.
- On unexpected timeout escalate: 30 → 120 → 300 → 600. If 600 fails, stop and report.
- Baseline (don't re-test): PowerShell 7.5.4 cold start ~0.5s; AV=Aura; startup is not the bottleneck.
- **Transport ≠ timeout.** "Failed to call tool" / "No result received" = transport failure. Refresh; if session >85%, new chat. Do NOT retry with escalating timeouts. Switch to Claude Code CLI for file/execution tasks (`cd` project folder in Anaconda Prompt → `claude`).
- Never call a Python .bat synchronously via PowerShell — use `_mcp.ps1` wrappers:

| Bat | MCP-safe wrapper |
|---|---|
| P_010_daily_posture.bat | P_010_daily_posture_mcp.ps1 |
| P_010_run_intraday_vp_check.bat | P_010_intraday_mcp.ps1 |
| P_300_DailyEval_v2.bat | P_300_DailyEval_mcp.ps1 -Symbol XYZ |
| P_300_AddPattern.bat | P_300_AddPattern_mcp.ps1 -XlsxPath "..." |
| P_020_Weekly_Update.bat | P_020_WeeklyUpdate_mcp.ps1 |

Shared engine: `...\shared_resources\hub_mcp_launcher.ps1`
- New bat files get a matching `_mcp.ps1` wrapper before session end.
- Multi-step or escaping-heavy ops: write a `.ps1` to disk and run it; never cram complex logic into inline command param.

### Protocol D — Failure Loop Recognition
Trigger: fix attempted more than once, recurring error, or systemic failure.

| Loop | Pattern | Break |
|---|---|---|
| A | Wrong environment assumption | Run Step 0 first |
| B | Timeout confusion — 30s fires → assume fail → retry | Classify command vs transport (Protocol C) |
| C | Architecture drift — skip folder rules → wrong location | Check Protocols A & B before generating |
| D | Research starvation — speed → shallow fix → repeat | Gather evidence first |
| E | Shifting the burden — one-session patch, no durable update | Fix works → update skill or doc |
| F | Falsified output — hardcoded success string, no real call | Output `[OK]`/`DONE`/`written` only after call returns without exception |

Non-negotiables: never confuse command timeout / transport / permission errors · never assume absent without verifying · never retry blindly · never optimize for speed when Tony needs diagnosis · **never emit `[OK]`, `SUCCESS`, `DONE`, `written`, or equivalent without the real call return confirming it — no placeholder string survives a session boundary.**

Structure recurring failures: Immediate Containment → Structural Repair (rule/skill/doc change) → Prevention (durable artifact).

### Protocol E — Mixed-Environment File Handling
Trigger: file output needed; runtime may be Linux sandbox, destination Windows.

- Windows-MCP present → write directly to Windows paths.
- No Windows-MCP → Linux sandbox: (1) create in `/mnt/user-data/outputs/`; (2) `present_files`; (3) manifest table of Windows destinations; (4) Tony downloads + places.
- Delivery format when sandboxed:
  ```
  CREATED IN: /mnt/user-data/outputs/
  TARGET (copy to): | File | Windows Destination |
  ```
- **Skill files:** editing the disk file does NOT update the live skill. Canonical source: `.claude\skills\[skill-name]\SKILL.md`. After editing, update IN THE APP via Customize → Skills. Never write to `/mnt/skills/` (read-only).

---

## Edge Cases

| Situation | Action |
|---|---|
| tool_search errors in Step 0 | State error, ask Tony to confirm environment |
| No system doc found | Skip name, apply protocols, proceed |
| Sections missing | Load what exists, still output name |
| Multiple files match | Read most recently updated |
| "ignore the system doc" | Comply — user overrides |
| User pastes SESSION_INITIALIZATION_PROMPT | Their content takes precedence |
| "just show me the code" | Still require approval before writing |

---

## This Skill Does NOT

Read the whole doc · report what it loaded · replace the full doc · run on every message · override current-session user instructions.

---

## Standing Rule — Conversation Context Integrity

Before reporting a negative: (1) review history, (2) verify with tools, (3) only then report. Never assume an action wasn't taken if it was discussed this session.

---

## Error Corrections Log

**EC-002 — Skill file placed in wrong location (2026-06-04). Severity: High.**
Wrote to read-only `/mnt/skills/user/...` instead of outputting for manual placement.
Rule: skill files go ONLY to `.claude\skills\[skill-name]\SKILL.md`; update live skill IN THE APP (Customize → Skills). Never write to `/mnt/skills/` or `shared_resources\skills\`.

**EC-001 — Skill file written to wrong location (2026-05-29). Severity: High.**
Wrote SKILL.md to `shared_resources\skills\` instead of `.claude\skills\`.
Rule: verify `.claude\skills\` exists first; write only there.

---

*Last Updated: 2026-06-12 — Compressed v3.0. Protocol D Loop F added (falsified output / M-051 global rule). All protocols (A-E), edge cases, EC log retained. ~40% token reduction.*
