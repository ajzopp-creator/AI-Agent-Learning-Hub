---
name: system-doc-initializer
description: >
  Session initializer for AI-Agent-Learning-Hub projects. Triggers on the FIRST
  message of any session. Verifies runtime, loads 4 critical system-doc sections,
  outputs a suggested chat name, and enforces standing protocols for Python
  architecture, file delivery, PowerShell timeouts, mixed-environment file handling,
  and failure-loop recognition. Use at session start in any Claude Desktop or
  claude.ai project with a SYSTEM_DOCUMENTATION or MASTER_DOC file.
---

# system-doc-initializer - AI-Agent-Learning-Hub Edition

Loads project context and enforces operating protocols before every response.
Runs silently. Tony never sees this skill referenced unless he asks.

---

## APPROVAL GATE - NON-NEGOTIABLE

Before writing ANY file/code or changing ANYTHING in the Hub:
1. Present the complete plan (files, changes, why, save paths)
2. STOP and wait for Tony's "go ahead" / "yes" / "proceed" / equivalent
3. Execute only after explicit approval

Applies to all file types (Python, batch, PowerShell, skills, docs, config) and any new or modified file anywhere in the Hub.

Diagnosis, understanding, or being asked to investigate is NOT permission. Only Tony's explicit approval is.

> Violation (do not repeat): diagnosed a timeout, then wrote 7 files across 4 projects and modified production Python without asking. Correct: stop after diagnosis, present plan, wait.

---

## When to Trigger

First message of any session in a Claude Project. Do not wait. Do not skip.

---

## Step 0 - Runtime Check (RUN FIRST)

Call `tool_search(query="PowerShell")`:

| Result | Environment | State at top of first response |
|---|---|---|
| `Windows-MCP:PowerShell` returned | Claude Desktop - local filesystem | `Runtime: Claude Desktop (Windows-MCP loaded) - local filesystem access available` |
| Nothing returned | claude.ai web - sandboxed | `Runtime: claude.ai web - sandboxed, no local filesystem access` |

Do NOT claim file access either way until this runs.

---

## Step 1 - Find System Documentation (disk-canonical)

Architecture docs live on disk, NOT in Project knowledge. Read the system doc directly via filesystem / Windows-MCP:
  C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_DOCUMENTATION.md
If absent or no filesystem access (claude.ai web): skip to Step 5, apply protocols, proceed.

Only TONY_ABOUT_ME.md and TONY_STYLE_RULES.md stay in Project knowledge (always-on); their full versions are also on disk.

Reference docs on disk -- read ON DEMAND when a task needs them; do NOT load every session. Paths under C:\Users\Trader\AI-Agent-Learning-Hub\ :

| Doc | Path |
|---|---|
| Folder architecture | Trading_Projects_Folder_Architecture.md |
| Local LLM upgrade plan | projects\P_000_PythonClaudeLocalLLM\docs\Local_LLM_Upgrade_Plan_V2.0.md |
| Summarizer app arch | projects\P_000_PythonClaudeLocalLLM\docs\Claude_Summarizer_App_Architecture.md |
| Agentic migration | projects\P_000_PythonClaudeLocalLLM\docs\Claude-Python_Agentic_Migration_1.md |
| INIT prompt (governance ref) | projects\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_INITIALIZATION_PROMPT_v1_0.md |
| Work-order ledger | 04-Shared-Resources\work_orders\ (alias Agentic-Hub-Governance) |

## Step 2 - Read Only These 4 Sections

| Section | Load |
|---|---|
| 1.5 Definitions & Acronyms | all term/definition pairs |
| 3.4 AI Behavior Rules | all MUST / MUST NOT rules |
| 6 Error Corrections Log | all documented errors |
| 11.4 Parameter Registry | all fixed values - never substitute |

---

## Step 3 - Output Suggested Chat Name

`Suggested chat name: [Project ID] - [Topic] - MM-DD-YYYY`
Project ID from doc header; Topic = 2-5 words from first message; Date = today.

---

## Step 4 - Apply Context All Session

Parameters (11.4) used exactly; behavior rules (3.4) enforced; error corrections (6) checked before each matching output; definitions (1.5) for terminology.

---

## Step 5 - Standing Protocols

### Protocol A - Python Architecture
Trigger: any session creating/extending/refactoring Python.

| Check | Rule |
|---|---|
| Approval first | If Tony hasn't said "go ahead", present plan and STOP |
| Environment | p140 conda only - `C:\Users\Trader\.conda\envs\p140\python.exe` |
| LLM preference | Local LM Studio first; Claude API only if local insufficient |
| File plan | List all files + line counts BEFORE any code |
| File size | Hard 300 lines; split at 250 |
| Function size | Hard 50 lines |
| Layers | domain/ = logic; infrastructure/ = IO; application/ = orchestration |
| One file per block | Never combine Python files in one block |
| Completion | Output `FILE COMPLETE: filename (N lines)` after each |
| No monoliths | Never put everything in one main.py |

### Protocol B - File Output & Artifact Delivery
Trigger: any file created (any type).

- **Rule 0 - Approval before action.** Present full plan; write nothing until Tony approves. Overrides convenience and obviousness.
- **Rule 1.** If Tony must act on a file, publish the artifact FIRST, then give instructions.
- **Rule 2.** Always offer a download with save path:
  `DOWNLOAD READY: filename.ext` / `Save to: C:\Users\Trader\AI-Agent-Learning-Hub\[project]\[subfolder]\`
- **Rule 3 - Standard save paths:**

| File type | Path |
|---|---|
| Python script | `...\projects\[P_XXX]\python\` |
| ThinkScript | `...\projects\[P_XXX]\tos_scripts\` |
| Shared utility | `...\shared_resources\python_utils\` |
| Prompt template | `...\shared_resources\llm_prompts\` |
| Skill file | `.claude\skills\[skill-name]\SKILL.md` (ONLY) |
| Project notes | `...\docs\project_notes\` |

- **Rule 4.** After any SKILL.md / README.md / architectural ref: `To update in the app: Customize -> Skills -> open the skill -> edit/replace`
- **Rule 5 - Delivery order:** Config -> Domain -> Infrastructure -> Application -> CLI -> .bat
- **Rule 6.** Never deliver incomplete files: `PAUSING - [filename] next response. Type "continue".`

### Protocol C - Windows-MCP PowerShell Timeouts
Trigger: any session where Windows-MCP PowerShell may run.

Two timeouts: tool `timeout` param (default 30s, set per call) and MCP global ceiling (~240s hard, NOT overridable). The ~240s global ceiling is the dominant failure mode.

- **Rule 1.** Default 30s only for trivial reads: `Test-Path`, `Get-ChildItem`, `Get-Content`, small reads.
- **Rule 2 - Explicit timeouts:**

| Operation | Timeout (s) |
|---|---|
| pip install (single package) | 120 |
| pip install -r requirements.txt | 300 |
| uvx / npx first-run | 300 |
| conda install / env update | 600 |
| Invoke-WebRequest (large) | 180 |
| Recursive Hub scans (1000+ files) | 120 |
| TOS XML export reads | 60 |

- **Rule 3.** When in doubt, timeout = 120.
- **Rule 4.** On unexpected timeout, escalate 30 -> 120 -> 300 -> 600; if 600 fails, stop and report.
- **Rule 5 - Verified baseline (don't re-test):** PowerShell 7.5.4 cold start ~0.5s; AV = Aura; shell startup is not the bottleneck.
- **Rule 6 - Transport != timeout.** Toasts "Failed to call tool" / "Tool result could not be submitted" / "No result received after waiting" = transport failure. Refresh first, check session usage; if >85%, new chat. Do NOT retry with escalating timeouts.
- **Rule 7.** Never call a Python .bat synchronously via PowerShell - multi-step bats exceed the 4-min ceiling. Use the `_mcp.ps1` wrapper:

| Project bat | MCP-safe wrapper |
|---|---|
| P_010_daily_posture.bat | P_010_daily_posture_mcp.ps1 |
| P_010_run_intraday_vp_check.bat | P_010_intraday_mcp.ps1 |
| P_300_DailyEval_v2.bat | P_300_DailyEval_mcp.ps1 -Symbol XYZ |
| P_300_AddPattern.bat | P_300_AddPattern_mcp.ps1 -XlsxPath "..." |
| P_020_Weekly_Update.bat | P_020_WeeklyUpdate_mcp.ps1 |

Shared engine: `...\shared_resources\hub_mcp_launcher.ps1`
- **Rule 8.** New bat files get a matching `_mcp.ps1` wrapper before session end.
- **Rule 9.** Multi-step or escaping-heavy operations: write a real `.ps1` to the Hub and run it; do not cram complex logic into the inline command param.

### Protocol E - Mixed-Environment File Handling
Trigger: file output needed but runtime may be Linux sandbox (claude.ai web) while destination is Windows.

- **Rule 1 - Detect:** Windows-MCP present -> direct PowerShell write to Windows paths. Absent -> Linux sandbox, no local access.
- **Rule 2 - Sandbox->Windows workflow:** (1) create in `/mnt/user-data/outputs/`; (2) `present_files`; (3) manifest table of Windows destinations; (4) user downloads + places.
- **Rule 3 - Delivery format:**
  ```
  CREATED IN: /mnt/user-data/outputs/
  TARGET (copy to):
  | File | Windows Destination |
  ```
- **Rule 4.** Optional: PowerShell helper that copies all outputs to destinations (user runs after download).
- **Rule 5 - Skill files: editing the disk file does NOT update the live skill.** The Claude desktop app runs an UPLOADED copy, not the `.claude\skills\` file (that is Claude Code behavior). Canonical source stays at `C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\[skill-name]\SKILL.md`; after editing it, the live skill must be updated IN THE APP via Customize -> Skills. Never write skills to `/mnt/skills/` (read-only).

### Protocol D - Failure Loop Recognition
Trigger: fix attempted more than once, recurring error, or systemic failure.

| Loop | Pattern | Break |
|---|---|---|
| A Runtime misclassification | wrong environment assumption | run Step 0 first |
| B Timeout confusion | 30s fires -> assume fail -> retry | classify command vs transport (Protocol C) |
| C Architecture drift | skip folder rules -> wrong location | check Protocols A & B before generating |
| D Research starvation | speed -> shallow fix -> repeat | gather evidence first |
| E Shifting the burden | one-session patch, no durable update | fix works -> update skill or doc |

Non-negotiables: don't confuse command timeout / transport / permission errors; don't assume a file/tool/path is absent without verifying; don't retry blindly without observability; don't optimize for speed when Tony needs diagnosis.

Structure recurring failures: Immediate Containment (stop it now) -> Structural Repair (rule/skill/path change) -> Prevention (durable artifact).

---

## Edge Cases

| Situation | Action |
|---|---|
| tool_search errors in Step 0 | state error, ask Tony to confirm environment |
| No system doc found | skip name, apply protocols, proceed |
| Sections missing | load what exists, still output name |
| Multiple files match | read most recently updated |
| "ignore the system doc" | comply - user overrides |
| User pastes SESSION_INITIALIZATION_PROMPT | their content takes precedence |
| "just show me the code" | still require approval before writing |

---

## This Skill Does NOT

Read the whole doc; report what it loaded; replace the full doc; run on every message (first only); override current-session user instructions.

---

## Standing Rule - Conversation Context Integrity

Never assume an action wasn't taken if it was discussed/performed earlier this session. Before reporting a negative: (1) review history, (2) verify with tools, (3) only then report.

---

*Last Updated: June 5, 2026 - Compressed v2.0 + disk-canonical Step 1. All protocols (A-E), edge cases, and EC log retained.*

---

## Error Corrections Log

**EC-002 - Skill file placed in wrong location (2026-06-04). Severity: High.**
What: updated skill in read-only `/mnt/skills/user/...` instead of creating a downloadable copy in `/mnt/user-data/outputs/` for manual placement.
Root cause: assumed editing the system skill would auto-sync to the app; Rule 3 had a wrong "shared_resources\skills" example; Protocol E lacked an explicit skill destination.
Rule: skill files go ONLY to `C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\[skill-name]\SKILL.md`, and the live skill is updated IN THE APP (Customize -> Skills). Never write to `/mnt/skills/`, `shared_resources\skills\`, or assume editing the disk file updates the running skill.

**EC-001 - Skill file written to wrong location (2026-05-29). Severity: High.**
What: wrote SKILL.md to `shared_resources\skills\` instead of `.claude\skills\`; upload dialog showed an empty folder.
Root cause: didn't verify where existing skills lived before writing.
Rule: write skill files only to `.claude\skills\[skill-name]\SKILL.md`; verify that folder first. Never write skills elsewhere without confirming structure.
