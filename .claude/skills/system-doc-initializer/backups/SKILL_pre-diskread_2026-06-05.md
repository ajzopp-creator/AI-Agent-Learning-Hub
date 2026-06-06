---
name: system-doc-initializer
description: >
  Session initializer for AI-Agent-Learning-Hub projects. Triggers on the FIRST
  message of any session. Verifies runtime environment, loads 4 critical sections
  from the project system doc, outputs a suggested chat name, and enforces standing
  protocols for Python architecture, file delivery, PowerShell timeouts, and failure
  loop recognition. Use at session start in any Claude Desktop or claude.ai project
  that has a SYSTEM_DOCUMENTATION or MASTER_DOC file.
---

# system-doc-initializer
## AI-Agent-Learning-Hub Edition

Loads project context and enforces operating protocols before every response.
Runs silently. Tony never sees this skill referenced unless he asks.

---

## ⛔ APPROVAL GATE — NON-NEGOTIABLE

**Before writing ANY file, code, or making ANY change to the Hub, Claude MUST:**

1. Present the complete plan (all files, what changes, why, save paths)
2. STOP and wait for Tony to say "go ahead", "yes", "proceed", or equivalent
3. Only after explicit approval: execute

**This applies to:**
- Python scripts, batch files, PowerShell scripts
- Skill files, documentation, config files
- Any modification to an existing file
- Any new file created anywhere in the Hub

**Diagnosis is not permission. Understanding the problem is not permission.
Being asked to investigate is not permission to fix.
Only Tony's explicit "go ahead" is permission.**

Violation example (DO NOT repeat):
> Claude read logs, diagnosed timeout root cause, then immediately wrote
> 7 files across 4 projects and modified production Python without asking.
> Correct behavior: stop after diagnosis, present plan, wait for approval.

---

## When to Trigger

First message of any session in a Claude Project. Do not wait. Do not skip.

---

## Step 0 — Runtime Check (RUN FIRST)

Call `tool_search(query="PowerShell")` and classify:

| Result | Environment |
|---|---|
| `Windows-MCP:PowerShell` returned | Claude Desktop — local filesystem access available |
| Nothing returned | claude.ai web — sandboxed, no local filesystem access |

State result in ONE line at the top of the first response:

`🖥 Runtime: Claude Desktop (Windows-MCP loaded) — local filesystem access available`
or
`🖥 Runtime: claude.ai web — sandboxed, no local filesystem access`

Do NOT claim file access is available or unavailable until this check runs.

---

## Step 1 — Find System Documentation

Search project knowledge in order, stop at first match:
1. `UNIVERSAL_PROJECT_TEMPLATE`
2. `SYSTEM_DOCUMENTATION`
3. `PROJECT_TEMPLATE`
4. `MASTER_DOC`
5. `system documentation`

No match → skip to Step 5. Match found → Step 2.

---

## Step 2 — Read Only These 4 Sections

| Section | Content to Load |
|---|---|
| 1.5 — Definitions & Acronyms | All term/definition pairs |
| 3.4 — AI Behavior Rules | All MUST/MUST NOT rules — hard constraints |
| 6 — Error Corrections Log | All documented errors — never repeat them |
| 11.4 — Parameter Registry | All fixed values — never substitute assumed values |

---

## Step 3 — Output Suggested Chat Name

```
📋 Suggested chat name: [Project ID] — [Topic] — MM-DD-YYYY
```

- **Project ID:** from document header (e.g., P_115, P_300, P_000)
- **Topic:** 2–5 words from the user's first message
- **Date:** today in MM-DD-YYYY format

---

## Step 4 — Apply Context for the Full Session

- Parameters (11.4) → use exactly, never invent
- Behavior rules (3.4) → enforce throughout
- Error corrections (6) → check before every output of that type
- Definitions (1.5) → use project-specific terminology

---

## Step 5 — Standing Protocols (Every Session)

---

### Protocol A — Python Architecture

**Trigger:** any session where Python code will be created, extended, or refactored.

| Check | Rule |
|---|---|
| **Approval first** | Tony has said "go ahead" — if not, present plan and STOP |
| Environment | p140 conda only — `C:\Users\Trader\.conda\envs\p140\python.exe` |
| LLM preference | Local LM Studio first — Claude API only when local is insufficient |
| File plan | List all files with line counts BEFORE writing any code |
| File size | Hard limit 300 lines. Begin splitting at 250 |
| Function size | Hard limit 50 lines per function |
| Layer separation | domain/ = logic · infrastructure/ = IO · application/ = orchestration |
| One file per block | Never combine multiple Python files in one code block |
| Completion | Output ✅ FILE COMPLETE: filename (N lines) after each file |
| No monoliths | Never write everything into a single main.py |

---

### Protocol B — File Output & Artifact Delivery

**Trigger:** any file is created — Python, Markdown, batch, config, or any other type.

**Rule 0 — APPROVAL BEFORE ACTION**

Present the full plan first. Wait for Tony's explicit approval.
Do not write a single file until Tony says "go ahead" or equivalent.
This is the first rule. It overrides convenience, efficiency, and apparent obviousness.

**Rule 1 — Publish artifact BEFORE giving instructions**

If Tony needs to act on a file, publish the artifact FIRST — then give instructions.

**Rule 2 — Always offer an artifact download with save path**

```
📥 DOWNLOAD READY: filename.ext
📁 Save to: C:\Users\Trader\AI-Agent-Learning-Hub\[project]\[subfolder]\
```

**Rule 3 — Standard save paths**

| File type | Save path |
|---|---|
| Python script | `...\projects\[P_XXX]\python\` |
| ThinkScript | `...\projects\[P_XXX]\tos_scripts\` |
| Shared utility | `...\shared_resources\python_utils\` |
| Prompt template | `...\shared_resources\llm_prompts\` |
| Skill file | `...\shared_resources\skills\[skill-name]\` |
| Project notes | `...\docs\project_notes\` |

**Rule 4 — After any SKILL.md, README.md, or architectural reference file**

`📌 To add to Claude Project: Project Settings → Add Content → Upload this file`

**Rule 5 — Multi-file delivery order**

Config → Domain → Infrastructure → Application → CLI → .bat launcher

**Rule 6 — Never deliver incomplete files**

`⏸ PAUSING — [filename] will be in the next response. Type "continue" to proceed.`

---

### Protocol C — Windows-MCP PowerShell Timeout Handling

**Trigger:** any session where Windows-MCP PowerShell tool is loaded and may be invoked.

The `windows-mcp:PowerShell` tool has TWO independent timeout mechanisms:

| Mechanism | Ceiling | Configurable? |
|---|---|---|
| Tool `timeout` parameter | Set per call (default 30s) | Yes — pass `timeout:N` |
| MCP global protocol ceiling | ~240 seconds hard | NO — cannot be overridden |

**The MCP global ceiling (~240s) is the dominant failure mode.**

**Rule 1 — Default timeout only for trivial reads**

30s is fine for: `Test-Path`, `Get-ChildItem`, `Get-Content`, single small-file reads.

**Rule 2 — Explicit timeouts for slow operations**

| Operation | Timeout (seconds) |
|---|---|
| `python -m pip install <single package>` | 120 |
| `pip install -r requirements.txt` | 300 |
| `uvx` / `npx` first-run | 300 |
| `conda install` / `conda env update` | 600 |
| `Invoke-WebRequest` to large files | 180 |
| Recursive Hub scans (1000+ files) | 120 |
| ThinkOrSwim XML export reads | 60 |

**Rule 3 — When in doubt, set timeout = 120**

**Rule 4 — On unexpected timeout, escalate — do not retry blindly**

Tier up: 30 → 120 → 300 → 600. If 600s fails, stop and report.

**Rule 5 — Verified baseline (do not re-test)**

PowerShell 7.5.4 cold start ~0.5s. Active AV: Aura. Shell startup is not the bottleneck.

**Rule 6 — Transport failures are a different problem**

Toasts "Failed to call tool" or "Tool result could not be submitted" = transport failure,
not command timeout. Refresh first, check session usage second. If >85%, new chat.

**Rule 7 — Never call a Python .bat file synchronously via PowerShell**

Multi-step bats exceed the 4-minute MCP ceiling. Always use the `_mcp.ps1` wrapper.

| Project bat | MCP-safe wrapper |
|---|---|
| `P_010_daily_posture.bat` | `P_010_daily_posture_mcp.ps1` |
| `P_010_run_intraday_vp_check.bat` | `P_010_intraday_mcp.ps1` |
| `P_300_DailyEval_v2.bat` | `P_300_DailyEval_mcp.ps1 -Symbol XYZ` |
| `P_300_AddPattern.bat` | `P_300_AddPattern_mcp.ps1 -XlsxPath "..."` |
| `P_020_Weekly_Update.bat` | `P_020_WeeklyUpdate_mcp.ps1` |

Shared engine: `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\hub_mcp_launcher.ps1`

**Rule 8 — New bat files get a matching `_mcp.ps1` wrapper before the session ends**

---

### Protocol D — Failure Loop Recognition

**Trigger:** fix attempted more than once, recurring error, or systemic failure pattern.

| Loop | Pattern | Break |
|---|---|---|
| A — Runtime Misclassification | Wrong environment assumption | Run Step 0 first |
| B — Timeout Confusion | 30s fires → assumes failure → retries | Classify: command vs transport (Protocol C) |
| C — Architecture Drift | Skip folder rules → artifacts land wrong | Check Protocols A and B before file generation |
| D — Research Starvation | Speed pressure → shallow fix → repeat | Gather evidence first |
| E — Shifting the Burden | One-session patch → no durable update | Fix works → update skill or project doc |

**Non-negotiables:**
- Do not confuse command timeout, transport failure, permission errors
- Do not assume a file/tool/path is absent without verifying
- Do not retry repeatedly when observability is missing
- Do not optimize for speed when Tony needs diagnosis

**Structure recurring failures as:**

| Layer | Question |
|---|---|
| Immediate Containment | What stops the failure right now? |
| Structural Repair | What rule/skill/path change prevents recurrence? |
| Prevention | What durable artifact locks in the fix? |

---

## Edge Cases

| Situation | Action |
|---|---|
| tool_search errors in Step 0 | State the error, ask Tony to confirm environment |
| No system doc found | Skip name suggestion, apply Protocols, proceed |
| Sections missing | Load what exists, skip missing, still output name |
| Multiple files match | Read the most recently updated one |
| User says "ignore the system doc" | Comply — user overrides skill |
| User pastes SESSION_INITIALIZATION_PROMPT | Their content takes precedence |
| User says "just show me the code" | Still require approval before writing |

---

## What This Skill Does NOT Do

- Does not read the entire documentation file
- Does not report what it loaded to the user
- Does not replace the full documentation
- Does not run on every message — only the first message of a session
- Does not override user instructions given in the current session

---

## Standing Rule — Conversation Context Integrity

**NEVER assume an action was NOT taken if it was discussed or performed earlier
in the current session.**

Before reporting something didn't happen:
1. Review conversation history
2. Verify with tools if still uncertain
3. Only then report a negative result

---

*Last Updated: May 29, 2026 — Added ⛔ APPROVAL GATE at top of skill. Added
Rule 0 (Approval Before Action) to Protocol B. Added Approval as first check
in Protocol A table. Violation example documented. Added Protocol C Rules 7 & 8
(MCP global ceiling, detached-launch pattern, wrapper table). lm_studio_api.py
v1.2: fixed 400 Bad Request via _wait_for_model_ready() readiness poll.*


---

## Error Corrections Log

### EC-001 — Skill File Written to Wrong Location (2026-05-29)

**Severity:** High
**Category:** Research-Before-Action failure (Protocol D, Loop D)

**What happened:**
Claude wrote `system-doc-initializer\SKILL.md` to `shared_resources\skills\`
instead of `.claude\skills\`. The file landed in the wrong folder, causing
the upload dialog to show an empty folder.

**Root cause:**
Claude did not verify where existing skills lived before writing the new file.
`.claude\skills\` is the correct and only location for all Hub skill files.
`shared_resources\skills\` is not a valid skill location.

**Correct rule:**
All skill files MUST be written to:
`C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\[skill-name]\SKILL.md`

Before writing any skill file, verify the target folder by checking:
`C:\Users\Trader\AI-Agent-Learning-Hub\.claude\skills\`

Never write a skill file to `shared_resources\` or any other location
without first confirming it matches the existing skill folder structure.

**Fix applied:**
File copied from `shared_resources\skills\system-doc-initializer\SKILL.md`
to `.claude\skills\system-doc-initializer\SKILL.md`. Correct location confirmed.
