---
name: p000-chat-session-initializer
description: >
  Automatically loads critical context from a project's System Documentation file at the
  start of every session. Use this skill immediately at the start of ANY new conversation
  within a Claude Project — before responding to the user's first message. Triggers whenever
  a session begins in a project that may have a system documentation file (look for files
  named *SYSTEM_DOCUMENTATION*, *PROJECT_TEMPLATE*, *_MASTER_DOC*, or similar). This skill
  prevents parameter drift, repeated errors, and missing context that occurs when Claude
  starts a session cold. ALWAYS trigger this skill on the first user message in a project
  session — even if the request seems simple or unrelated to the documentation.
---

# P_000_ChatSession_Initializer
## AI-Agent-Learning-Hub Edition

---

## Purpose

Load critical operating context from the project's master documentation file at session
start — silently and automatically — so Claude never starts a session cold.

This skill also enforces three standing protocols that apply to EVERY session in this Hub:
1. **Python Architecture Protocol** — loaded whenever any Python code will be created
2. **File Output Protocol** — applied whenever any file is created or delivered
3. **Windows-MCP PowerShell Execution Protocol** — applied whenever external processes are launched via MCP

---

## When to Trigger

Trigger on the FIRST user message of any session in a Claude Project.

**Do not wait** for the user to ask. Do not skip because the first message seems simple.
The whole point is that this runs BEFORE responding, every time.

---

## Step 1: Find the System Documentation File

Search project knowledge for the master documentation file using these search terms
(try in order until you find a match):

1. `UNIVERSAL_PROJECT_TEMPLATE`
2. `SYSTEM_DOCUMENTATION`
3. `PROJECT_TEMPLATE`
4. `MASTER_DOC`
5. `system documentation`

If NO file is found after all 5 searches → skip silently, proceed normally.
If a file IS found → proceed to Step 2.

---

## Step 2: Read Only These 4 Sections

Do NOT read the entire document. Read ONLY the sections below.
Search for each section by its heading:

### Section 1.5 — Definitions & Acronyms
- Load all term/definition pairs into active context
- These define the vocabulary for this project

### Section 3.4 — AI Behavior Rules & Constraints
- Load all MUST and MUST NOT rules
- These are Claude's operating constraints for this project
- Treat these as hard rules equivalent to system prompt instructions

### Section 6 — Error Corrections Log
- Load all documented errors and their correct behavior
- Pay special attention to errors marked Critical or High severity
- These represent mistakes that have already happened — do not repeat them

### Section 11.4 — Parameter Registry
- Load all parameter name/value pairs
- These are fixed values (e.g., account balance, risk %, thresholds)
- Never substitute default or assumed values when these are provided

---

## Step 3: Output a Suggested Chat Name

After loading context, output ONE line at the very top of your first response:

```
📋 Suggested chat name: [Project ID] — [Topic] — MM-DD-YYYY
```

**How to determine each part:**

- **Project ID:** Read from the document header field "Project ID"
  (e.g., P_115, P_300, P_000). If not found, use the document filename prefix.
- **Topic:** Infer from the user's first message — 2-5 words capturing what
  they are asking about. Keep it specific enough to be useful as a search term.
  Examples: "Schema Recovery", "Signal Analysis", "Template Build", "Error Fix"
- **Date:** Today's date in MM-DD-YYYY format.

**Examples:**
```
📋 Suggested chat name: P_115 — Schema Recovery — 02-25-2026
📋 Suggested chat name: P_300 — TTD Trade Review — 02-25-2026
📋 Suggested chat name: P_000 — Python FastAPI Setup — 02-25-2026
```

Then immediately continue with the response to the user's first message.
No other commentary about the skill or documentation loading.

---

## Step 4: Apply Context Throughout the Session

The loaded context is active for the entire session:

- **Parameters** from Section 11.4 → use these values, never assume or invent
- **Behavior rules** from Section 3.4 → enforce throughout, not just at start
- **Error corrections** from Section 6 → check before every output of that type
- **Definitions** from Section 1.5 → use project-specific terminology correctly

---

## Step 5: Load Standing Protocols (ALWAYS — every session)

These two protocols apply to EVERY session in the AI-Agent-Learning-Hub,
regardless of whether a system doc file was found.

---

### STANDING PROTOCOL A — Python Architecture

**Trigger:** Any session where Python code will be created, extended, or refactored.

**Reference file:**
```
AI-Agent-Learning-Hub/shared_resources/skills/python-project-architecture/SKILL.md
```
Also available as a Claude Project file named: `python-project-architecture`

**Before writing any Python code, confirm all of the following:**

| Check | Rule |
|-------|------|
| Environment | Always use p140 conda — path: `C:\Users\Trader\.conda\envs\p140\python.exe` |
| LLM preference | Local LM Studio first, Claude API only when local is insufficient |
| File plan | List all files with estimated line counts BEFORE writing any code |
| File size limit | Hard limit: 300 lines per file. Split before reaching 250 lines |
| Function size limit | Hard limit: 50 lines per function |
| Layer separation | domain/ = logic only · infrastructure/ = IO only · application/ = orchestration |
| One file per block | Never combine multiple Python files into one code block |
| Completion check | Output ✅ FILE COMPLETE: filename (N lines) after each file |
| No monoliths | Never write everything into a single main.py |

**If the session involves Python and this reference file is not yet loaded →
state: "Loading Python Architecture protocol" and apply the rules from the table above.**

---

### STANDING PROTOCOL B — File Output & Artifact Delivery

**Trigger:** ANY time a file is created — Python, Markdown, batch, config, prompt template, or any other file type.

**Rule 1 — Always offer an artifact download**

When creating any file, deliver it as a downloadable artifact so Tony can save it
directly to the correct Hub folder without copy-pasting. Use this format:

```
📥 DOWNLOAD READY: filename.ext
📁 Save to: C:\Users\Trader\AI-Agent-Learning-Hub\[project]\[subfolder]\
```

**Rule 2 — Always state the target save path**

Every file delivery must include the full recommended Windows path based on the
Hub folder structure. Examples:

| File type | Example save path |
|-----------|------------------|
| Python script | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\python\` |
| ThinkScript | `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_300_Vantage_Point_Pattern_Recognition\tos_scripts\` |
| Shared utility | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\python_utils\` |
| Prompt template | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\llm_prompts\` |
| Skill file | `C:\Users\Trader\AI-Agent-Learning-Hub\shared_resources\skills\[skill-name]\` |
| Project notes | `C:\Users\Trader\AI-Agent-Learning-Hub\docs\project_notes\` |

**Rule 3 — Offer Claude Project upload option**

After delivering any SKILL.md, README.md, or architectural reference file, add:

```
📌 To add to Claude Project: Open Project Settings → Add Content → Upload this file
   Once uploaded, Claude will load it automatically in every future session.
```

**Rule 4 — Multi-file delivery order**

When delivering multiple files in one session, always deliver in this order:
1. Config files first (config.py, .env template, requirements.txt)
2. Domain/logic files second
3. Infrastructure files third
4. Application/orchestration files fourth
5. CLI / entry point last
6. Batch launcher (.bat) last of all

This order means each file Tony saves is immediately usable before the next one arrives.

**Rule 5 — Never deliver incomplete files**

If a file cannot be completed in the current response:
- Stop before starting it
- Output: `⏸ PAUSING — [filename] will be in the next response. Type "continue" to proceed.`
- Wait for Tony's confirmation before proceeding

---

### STANDING PROTOCOL C — Windows-MCP PowerShell Execution

**Trigger:** ANY session that uses Windows-MCP PowerShell to run external processes
(Python scripts, batch files, executables, or any long-running command).

---

#### RULE 1 — NEVER use `Start-Process -NoNewWindow`

**This is a confirmed bug (06-01-2026).** `Start-Process -NoNewWindow` causes the
child process to inherit the MCP server's stdio pipes. The MCP server cannot return
a response until the child exits — even without `-Wait`. The session hangs until
Claude Desktop's request timeout fires (~4 minutes), then the tool call fails.

❌ **BANNED — never use these patterns:**
```powershell
Start-Process python.exe -NoNewWindow -Wait
Start-Process python.exe -NoNewWindow -PassThru
Start-Process python.exe -NoNewWindow  # fire-and-forget still hangs
```

✅ **ALWAYS use Start-Job with cmd /c:**
```powershell
$job = Start-Job -ScriptBlock {
    cmd /c """C:\path\to\python.exe"" ""C:\path\to\script.py"" > ""C:\out.txt"" 2>&1"
}
# Wait for completion
Start-Sleep -Seconds 30   # adjust to expected runtime
# Read results
Get-Content "C:\out.txt"
```

---

#### RULE 2 — Redirect output to a temp file, never capture inline

Jobs and long-running processes must write output to a file. Never try to capture
output directly from a job via `Receive-Job` in the same call — read the file instead.

```powershell
# Launch
$job = Start-Job -ScriptBlock {
    cmd /c """python.exe"" ""script.py"" > ""$env:TEMP\out.txt"" 2>&1"
}

# In a separate PowerShell call after sleeping:
Get-Content "$env:TEMP\out.txt"
```

---

#### RULE 3 — Split launch and read into separate tool calls

Never launch a job and read its output in the same PowerShell tool call. The
`Start-Sleep` required to wait for completion will block MCP for the sleep duration.

```powershell
# CALL 1 — launch only
$job = Start-Job -ScriptBlock { cmd /c "..." }
Write-Host "Job $($job.Id) launched"

# CALL 2 — after sufficient wait (use Start-Sleep in the read call, not the launch call)
Start-Sleep -Seconds 45
Get-Content "$env:TEMP\out.txt"
```

---

#### RULE 4 — Timeout sizing

Use these defaults unless the script is known to be faster or slower:

| Script type | Sleep before reading |
|-------------|----------------------|
| Quick PS commands | No sleep needed — direct execution fine |
| Single Python script (no Excel) | 20 seconds |
| Single Python script (reads Excel) | 45 seconds |
| Multi-step Python batch / backfill loop | 90 seconds |

If output file is empty after the sleep, wait another interval before declaring failure.

---

#### RULE 5 — Working directory for Python scripts

When a Python script uses relative imports or relative file paths, set the working
directory explicitly inside the `cmd /c` string:

```powershell
$job = Start-Job -ScriptBlock {
    cmd /c "cd /d ""C:\project\python"" && ""C:\python.exe"" -m module.name > ""C:\out.txt"" 2>&1"
}
```

---

## Edge Cases

| Situation | Action |
|-----------|--------|
| No system doc file found | Skip name suggestion, apply Standing Protocols, proceed normally |
| File found but sections 1.5 / 3.4 / 6 / 11.4 are empty or missing | Load what exists, skip missing sections, still output name suggestion |
| Multiple files match the search | Read the most recently updated one (check filename version number) |
| User explicitly says "ignore the system doc" | Comply — user instruction overrides skill |
| User pastes a SESSION_INITIALIZATION_PROMPT manually | Their pasted content takes precedence over what the skill loaded |
| Python session but architecture SKILL.md not found as Project file | Apply the rules from the Standing Protocol A table directly |
| User says "just show me the code" without asking for a file | Still deliver as artifact with save path — don't skip the protocol |

---

## What This Skill Does NOT Do

- Does NOT read the entire documentation file
- Does NOT summarize or report what it loaded to the user
- Does NOT replace the full documentation — it loads a subset
- Does NOT run on every message — only on the first message of a session
- Does NOT override user instructions given in the current session

---

## Design Notes

**Why load architecture rules here instead of separately?**
Tony has experienced Claude starting sessions without context and reverting to
monolithic script generation. Embedding the architecture check in the session
initializer means it is impossible to skip — it runs before any code is written.

**Why the artifact/download protocol?**
Copy-pasting code from chat into VS Code and then navigating to the correct folder
is friction that slows down the workflow. Delivering files as artifacts with explicit
save paths eliminates that friction and reduces save-to-wrong-folder errors.

**Why deliver config files first?**
Each subsequent file often imports from config.py. If Tony saves files in delivery
order, imports resolve correctly from the first run without modification.

---

## Last Updated
June 1, 2026

---

## Standing Rule — Conversation Context Integrity

**NEVER assume an action was NOT taken if it was discussed or performed earlier in the current session.**

Before declaring that something didn't happen or wasn't done:
1. Review the current conversation history first
2. If still uncertain — verify with tools (check logs, files, task status)
3. Only after checking may Claude report a negative result

**Example of the failure this prevents:**
- User and Claude add a Task Scheduler trigger together in the same chat
- User reboots and asks why the task didn't run at logon
- Claude incorrectly says "the AtLogon trigger was not added"
- CORRECT behavior: Claude checks the conversation history, sees the trigger was added, verifies with Get-ScheduledTask, reports correctly

This rule applies to ALL sessions in ALL projects.
