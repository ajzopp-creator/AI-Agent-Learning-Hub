---
name: system-doc-modification-skill
description: "..."
author: tony
version: '3.1'
---

# System Doc Modification Skill# System Doc Modification Skill
## P_999 Edition

Use this skill for any Space, thread, or project that begins with `P_999`.
All routing is rooted at `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_999`.
Skill files belong only in `.perplexity\skills\[skill-name]\SKILL.md`.

***

## Non-Negotiable Approval
Before writing any file, code, or doc change, present the full plan and wait for explicit approval such as "go ahead", "yes", or "proceed". This applies to all docs, scripts, configs, skill files, and new artifacts.

***

## Trigger
Apply this skill when the Space, thread, project title, or request begins with `P_999`, when the user asks to modify or place a Hub artifact, or when the task creates validation, prompt, report, chart, data, schema, database, Python, ThinkScript, or related files.

***

## Runtime Check
First, determine whether a PowerShell / Windows filesystem tool is available. State one line at the top of the first response: `🖥 Runtime: Local (PowerShell tool available) — local filesystem access available` or `🖥 Runtime: Web sandbox — no local filesystem access`.

***

## System Doc Lookup
Search in order and stop at the first match: `UNIVERSAL_PROJECT_TEMPLATE`, `SYSTEM_DOCUMENTATION`, `PROJECT_TEMPLATE`, `MASTER_DOC`, `system documentation`. If found, load only these sections: 1.5 Definitions & Acronyms, 3.4 AI Behavior Rules, 6 Error Corrections Log, and 11.4 Parameter Registry.

***

## Session Rules
Use definitions and fixed values exactly as written. Enforce behavior rules throughout. Check error corrections before repeating a prior mistake.

***

## Routing
| Artifact type / keyword | Destination |
|---|---|
| validation, review, audit, check, label_logic | `projects\P_999\docs\validation` |
| prompt, bootstrap, macro | `projects\P_999\docs\prompts` |
| report, summary, analysis | `projects\P_999\outputs\reports` |
| charts, images | `projects\P_999\outputs\charts` |
| exports | `projects\P_999\outputs\exports` |
| .db databases | `projects\P_999\models` |
| schema files | `projects\P_999\models\schema` |
| VP / history-grid inputs | `projects\P_999\data\raw` or `projects\P_999\data\historical` |
| processed / reference data | `projects\P_999\data\processed` or `projects\P_999\data\reference` |
| Python | `projects\P_999\python\<subarea>` |
| ThinkScript | `projects\P_999\tos_scripts` |
| shared Python utility | `shared_resources\python_utils` |
| shared prompt template | `shared_resources\llm_prompts` |
| skill file | `.perplexity\skills\[skill-name]` |
| project notes | `docs\project_notes` |

Do not route docs into `docs\architecture` or `docs\notes`.

***

## Delivery
Default to `Copy-Item`. Use `Move-Item` only when the source should be removed or the file is already inside the Hub. If path certainty is low, use `-WhatIf` first. Publish the artifact before giving instructions.

## File Artifact Rule
When a document or skill is requested, create the actual file artifact first and expose it as the downloadable deliverable. Do not substitute a quoted path, text-only answer, or internal folder reference when a downloadable artifact is expected. Provide only the minimum install path if it is needed to complete the task.

***

## Python
If Python is created or changed, keep files under 300 lines, functions under 50 lines, and separate logic, IO, and orchestration. Never combine multiple Python files in one block.

***

## Timeout Handling
Treat command timeout and transport failure as different problems. Use 30s for trivial reads, 120s when unsure, and escalate only when needed. Never call a Python `.bat` synchronously; use an `_async.ps1` wrapper.

***

## Failure Loops
Watch for runtime misclassification, timeout confusion, routing drift, research starvation, and one-session fixes that do not persist. If a failure repeats, verify the environment, file path, and routing rule before trying again.

***

## Error Corrections Log
### EC-001 — Wrong skill location
A skill file was written to `shared_resources\skills\` instead of `.perplexity\skills\`. Correct rule: all skill files must be written only to `.perplexity\skills\[skill-name]\SKILL.md`.

***

*Last Updated: June 3, 2026 — Install-ready compressed P_999 version.*

## Output Guarantee
When a file is requested, always return the created artifact as the primary deliverable. If a downloadable artifact cannot be exposed, say that immediately and do not replace it with a text-only substitute unless the user explicitly asks for text.