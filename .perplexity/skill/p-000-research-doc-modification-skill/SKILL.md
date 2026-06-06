---
name: p-000-research-doc-modification-skill
description: "Modify and maintain AI-Agent-Learning-Hub research and development documentation and route project artifacts into the correct local folders. Use when editing the research doc (starting with P_000.md), when creating any P_000 or Hub artifact (validation, prompts, reports, charts, data, schemas, .db, Python, ThinkScript), or when a file needs classifying and placing into the local Hub tree. Also loads critical doc sections at session start and enforces standing protocols for approval, Python architecture, file delivery, PowerShell timeouts, and failure-loop recognition. Triggers on P_000, Osidian, AI-Agent-Learning-Hub, or any request to modify, update, route, or place a Hub document or artifact."
metadata:
  author: tony
  version: '1.0'
  supersedes: system-doc-initializer
---

# Research_Doc Modification Skill
## AI-Agent-Learning-Hub Edition

Modifies and maintains Hub Research documentation, classifies and routes project
artifacts into the correct local folders, and enforces operating protocols on
every change. Runs silently — Tony never sees this skill referenced unless he asks.

Built for Perplexity Computer.

This skill supersedes and replaces both `p-300-artifact-handoff` and
`system-doc-initializer`. Retire those two once this one is in place.

---

## ⛔ APPROVAL GATE — NON-NEGOTIABLE

**Before writing ANY file, code, doc change, or making ANY change to the Hub, Perplexity MUST:**

1. Present the complete plan (all files, what changes, why, save paths)
2. STOP and wait for Tony to say "go ahead", "yes", "proceed", or equivalent
3. Only after explicit approval: execute

**This applies to:**
- Research documentation edits (P_000_..
.md)
- Python scripts, batch files, PowerShell scripts
- Skill files, documentation, config files
- Any modification to an existing file
- Any new file or artifact created anywhere in the Hub

**Diagnosis is not permission. Understanding the problem is not permission.
Being asked to investigate is not permission to fix.
Only Tony's explicit "go ahead" is permission.**

Violation example (DO NOT repeat):
> Perplexity read logs, diagnosed timeout root cause, then immediately wrote
> 7 files across 4 projects and modified production Python without asking.
> Correct behavior: stop after diagnosis, present plan, wait for approval.

---

## When to Trigger

Apply this skill whenever any of these are true:
- The Space, thread, project title, or user request contains `P_000`,
  `Obsidian`, or `AI-Agent-Learning-Hub`.
- The loaded architecture identifies `Project ID: P_000`.
- The user asks to modify, update, edit, route, classify, or place any Hub
  document or artifact.
- The task creates a file for validation, reporting, prompts, schemas, data,
  models, or scripts.
- It is the first message of a session in a Perplexity project or Space (run Step 0 init below).

---

## Step 0 — Runtime Check (RUN FIRST)

Discover available tools (search connected integrations for a PowerShell / Windows
filesystem tool) and classify:

| Result | Environment |
|---|---|
| A PowerShell / Windows filesystem tool is available | Local runtime — local filesystem access available |
| No such tool is available | Web sandbox — no local filesystem access |

State result in ONE line at the top of the first response:

`🖥 Runtime: Local (PowerShell tool available) — local filesystem access available`
or
`🖥 Runtime: Web sandbox — no local filesystem access`

Do NOT claim file access is available or unavailable until this check runs.

---

## Step 1 — Find Research Documentation

Search project knowledge in order, stop at first match:
1. `UNIVERSAL_PROJECT_TEMPLATE`
2. `Research_DOCUMENTATION`
3. `PROJECT_TEMPLATE`
4. `MASTER_DOC`
5. `P000_Research_Architecture.md`
6. `development documentation`

No match → skip to Standing Protocols. Match found → Step 2.

---

## Step 2 — Read Only These 4 Sections

| Section | Content to Load |
|---|---|
| 1.5 — Definitions & Acronyms | All term/definition pairs |
| 3.4 — AI Behavior Rules | All MUST/MUST NOT rules — hard constraints |
| 6 — Error Corrections Log | All documented errors — never repeat them |
| 11.4 — Parameter Registry | All fixed values — never substitute assumed values |

---

## Step 3 — Output Suggested Chat Name (session start only)

```
📋 Suggested chat name: [Project ID] — [Topic] — MM-DD-YYYY
```

- **Project ID:** from document header (e.g., P_115, P_000, P_000)
- **Topic:** 2–5 words from the user's first message
- **Date:** today in MM-DD-YYYY format
- **Time**  Military time
---

## Step 4 — Apply Context for the Full Session

- Parameters (11.4) → use exactly, never invent
- Behavior rules (3.4) → enforce throughout
- Error corrections (6) → check before every output of that type
- Definitions (1.5) → use project-specific terminology

---

## Research Documentation Modification Rules

When the task is to modify or maintain the Research documentation itself:

1. **Prefer in-place edits.** Update `P000_Reearch_Architecture.md` (or the matched
   Research doc) directly for durable documentation changes — do not spawn parallel
   notes files.
2. **Preserve numbered section structure.** Keep section numbers (1.5, 3.4, 6, 11.4,
   etc.) intact. Add new entries under the correct existing section rather than
   creating new top-level sections unless explicitly requested.
3. **Log corrections in Section 6.** When a documented error is fixed, add an
   `EC-NNN` entry to the Error Corrections Log with severity, category, what
   happened, root cause, correct rule, and fix applied.
4. **Register parameters in 11.4.** Any new fixed value goes into the Parameter
   Registry — never leave assumed values inline.
5. **State folder policy when it changes.** If a destination or path rule changes,
   say so explicitly in the response.
6. **Approval gate applies.** Present the full diff/plan and wait for "go ahead"
   before writing the modified doc.

---

## Artifact Classification & Routing

All paths are rooted at:
`C:\Users\Trader\AI-Agent-Learning-Hub`

### Classification rules

| Artifact type / keyword | Destination (relative to Hub root) |
|---|---|
| `validation`, `review`, `audit`, `check`, `label_logic` | `projects\P_000\docs\validation` |
| `prompt`, `bootstrap`, `macro` | `projects\P_000\docs\prompts` |
| `report`, `summary`, `analysis` (non-validation) | `projects\P_000\outputs\reports` |
| charts / images | `projects\P_000\outputs\charts` |
| exports | `projects\P_000\outputs\exports` |
| `.db` databases | `projects\P_000\models` |
| `schema` files | `projects\P_000\models\schema` |
| VP / history-grid inputs | `projects\P_000\data\raw` or `projects\P_000\data\historical` |
| processed / reference data | `projects\P_000\data\processed` or `projects\P_000\data\reference` |
| Python (ingest/features/matching/labeling/utilities) | `projects\P_000\python\<subarea>` |
| ThinkScript | `projects\P_000\tos_scripts` |
| Shared Python utility | `shared_resources\python_utils` |
| Prompt template (shared) | `shared_resources\llm_prompts` |
| Skill file | `.perplexity\skills\[skill-name]` |
| Project notes | `docs\project_notes` |

Do NOT route docs into `docs\architecture` or `docs\notes`.
Skill files go ONLY to `.perplexity\skills\` — never `shared_resources\skills\` (see EC-001).

### Routing behavior

When a file is created:
1. Identify the filename and artifact type.
2. Pick the destination folder from the table above.
3. Publish the artifact for download (Protocol B, Rule 1 — publish BEFORE instructions).
4. Provide a PowerShell command for the local machine.
5. Default to `Copy-Item`.
6. Use `-WhatIf` when path certainty is low.
7. For durable documentation changes, prefer editing `P300_Research_Architecture.md` directly.

### PowerShell placement template

```powershell
$projectRoot  = "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000"
$sourceFolder = Join-Path $HOME "Downloads"
$targetFolder = Join-Path $projectRoot "docs\validation"
$fileName     = "P_000_label_logic_fixed_summary.csv"

if (-not (Test-Path $targetFolder)) {
    New-Item -ItemType Directory -Path $targetFolder -Force | Out-Null
}

Copy-Item -Path (Join-Path $sourceFolder $fileName) -Destination (Join-Path $targetFolder $fileName) -Force
```

### Copy vs move

- Use `Copy-Item` by default.
- Use `Move-Item` only when Tony explicitly wants the source removed, or the file
  is already inside the local Hub tree.

---

## Standing Protocols (Every Session)

### Protocol A — Python Architecture

**Trigger:** any session where Python code will be created, extended, or refactored.

| Check | Rule |
|---|---|
| **Approval first** | Tony has said "go ahead" — if not, present plan and STOP |
| Environment | p140 conda only — `C:\Users\Trader\.conda\envs\p140\python.exe` |
| LLM preference | Local LM Studio first — hosted API only when local is insufficient |
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
| Skill file | `...\.perplexity\skills\[skill-name]\` |
| Project notes | `...\docs\project_notes\` |

**Rule 4 — After any SKILL.md, README.md, or architectural reference file**

`📌 To add to your Perplexity library: Settings → Skills → Upload this file`

**Rule 5 — Multi-file delivery order**

Config → Domain → Infrastructure → Application → CLI → .bat launcher

**Rule 6 — Never deliver incomplete files**

`⏸ PAUSING — [filename] will be in the next response. Type "continue" to proceed.`

---

### Protocol C — PowerShell Timeout Handling

**Trigger:** any session where a local PowerShell / Windows filesystem tool is
available and may be invoked.

The PowerShell tool has TWO independent timeout mechanisms:

| Mechanism | Ceiling | Configurable? |
|---|---|---|
| Tool `timeout` parameter | Set per call (default 30s) | Yes — pass `timeout:N` |
| Global protocol ceiling | ~240 seconds hard | NO — cannot be overridden |

**The global ceiling (~240s) is the dominant failure mode.**

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

Multi-step bats exceed the 4-minute global ceiling. Always use the `_async.ps1` wrapper.

| Project bat | Timeout-safe wrapper |
|---|---|
| `P_010_daily_posture.bat` | `P_010_daily_posture_async.ps1` |
| `P_010_run_intraday_vp_check.bat` | `P_010_intraday_async.ps1` |
| `P_000_DailyEval_v2.bat` | `P_000_DailyEval_async.ps1 -Symbol XYZ` |
| `P_000_AddPattern.bat` | `P_000_AddPattern_async.ps1 -XlsxPath "..."` |
| `P_020_Weekly_Update.bat` | `P_020_WeeklyUpdate_async.ps1` |

Shared engine: `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\hub_async_launcher.ps1`

**Rule 8 — New bat files get a matching `_async.ps1` wrapper before the session ends**

---

### Protocol D — Failure Loop Recognition

**Trigger:** fix attempted more than once, recurring error, or systemic failure pattern.

| Loop | Pattern | Break |
|---|---|---|
| A — Runtime Misclassification | Wrong environment assumption | Run Step 0 first |
| B — Timeout Confusion | 30s fires → assumes failure → retries | Classify: command vs transport (Protocol C) |
| C — Architecture Drift | Skip folder rules → artifacts land wrong | Check routing table + Protocols A and B before file generation |
| D — Research Starvation | Speed pressure → shallow fix → repeat | Gather evidence first |
| E — Shifting the Burden | One-session patch → no durable update | Fix works → update skill or system doc |

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
| Tool discovery fails in Step 0 | State the error, ask Tony to confirm environment |
| No Research doc found | Skip name suggestion, apply Protocols + routing, proceed |
| Sections missing | Load what exists, skip missing, still output name |
| Multiple files match | Read the most recently updated one |
| User says "ignore the Research doc" | Comply — user overrides skill |
| User pastes SESSION_INITIALIZATION_PROMPT | Their content takes precedence |
| User says "just show me the code" | Still require approval before writing |
| Path certainty is low | Use `Copy-Item -WhatIf` first, confirm, then run for real |

---

## What This Skill Does NOT Do

- Does not read the entire documentation file — only the 4 critical sections
- Does not report what it loaded to the user
- Does not replace the full documentation
- Does not route docs into `docs\architecture` or `docs\notes`
- Does not write skill files anywhere except `.perplexity\skills\`
- Does not assume a file is already on the user's machine
- Does not change folder policy without stating it
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

## Error Corrections Log

### EC-001 — Skill File Written to Wrong Location (2026-05-29)

**Severity:** High
**Category:** Research-Before-Action failure (Protocol D, Loop D)

**What happened:**
A skill file (`system-doc-initializer\SKILL.md`) was written to
`shared_resources\skills\` instead of `.perplexity\skills\`. The file landed in
the wrong folder, causing the upload dialog to show an empty folder.

**Root cause:**
The existing skill location was not verified before writing the new file.
`.perplexity\skills\` is the correct and only location for all Hub skill files.
`shared_resources\skills\` is not a valid skill location.

**Correct rule:**
All skill files MUST be written to:
`C:\Users\Trader\AI-Agent-Learning-Hub\.perplexity\skills\[skill-name]\SKILL.md`

Before writing any skill file, verify the target folder by checking:
`C:\Users\Trader\AI-Agent-Learning-Hub\.perplexity\skills\`

Never write a skill file to `shared_resources\` or any other location
without first confirming it matches the existing skill folder structure.

**Fix applied:**
File copied from `shared_resources\skills\Research-doc-initializer\SKILL.md`
to `.perplexity\skills\Research-doc-initializer\SKILL.md`. Correct location confirmed.

---

*Last Updated: May 31, 2026 — Merged `p-300-artifact-handoff` + `system-doc-initializer`
into a single doc-modification-focused skill. Standardized all artifact destinations on
the full `C:\Users\Trader\AI-Agent-Learning-Hub\...` path convention. Added Research
Documentation Modification Rules section. Skill renamed to `Research-doc-modification-skill`
and supersedes both source skills. Made the skill Perplexity-specific throughout:
runtime check uses tool discovery, skill folder convention is now `.perplexity\skills\`,
timeout wrappers are `_async.ps1`, and all assistant references read "Perplexity."*
