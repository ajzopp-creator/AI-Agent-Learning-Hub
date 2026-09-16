---
name: system-doc-initializer
description: >
  Session initializer for AI-Agent-Learning-Hub projects. Triggers on the FIRST
  message of any session, and re-triggers mid-session if a Windows-MCP call
  unexpectedly fails or Tony indicates a client switch (Desktop/web/relay).
  Verifies runtime, loads 4 critical system-doc sections, outputs a suggested
  chat name, and enforces standing protocols for Python architecture, file
  delivery, PowerShell timeouts, mixed-environment file handling, output
  integrity, and failure-loop recognition. Use at session start in any
  Claude Desktop or claude.ai project with a SYSTEM_DOCUMENTATION or MASTER_DOC file.
---

# system-doc-initializer — AI-Agent-Learning-Hub Edition

Runs silently on first message. Tony never sees this referenced unless he asks.

---

## APPROVAL GATE — NON-NEGOTIABLE

Before writing ANY file/code/change: present complete plan (files, changes, why, save paths) → STOP for explicit "go ahead"/"yes"/"proceed" → execute only after approval. Diagnosis/being asked to investigate is NOT permission. (Violation precedent: diagnosed a timeout, wrote 7 files across 4 projects unasked — never repeat.)

---

## Step 0 — Runtime Check (FIRST + re-check on signal)

`tool_search(query="PowerShell")`: returns `Windows-MCP:PowerShell` → Claude Desktop, local filesystem available. Returns nothing → claude.ai web, sandboxed. Do not claim file access until this runs.

**Re-check trigger (added 2026-09-07, ref EC-009).** The Step 0 result goes stale mid-chat — Tony runs the same conversation across Desktop and browser tabs and switches mid-session, with no new "first message" to re-trigger this step. Re-run `tool_search(query="PowerShell")` immediately if: a Windows-MCP call that worked earlier this session now errors "not available" / times out with no response, or Tony states or implies a client switch ("switched to web," "back on desktop," "moved to browser," etc.). Treat the new result as authoritative over the session-start read — never assume the original Step 0 result still holds partway through a session.

---

## Step 0.5 — Identify Active Project (BEFORE Step 1)

Attached knowledge/imported-Project name (system prompt's imported_knowledge/project-context block — not guessed) is this session's Project ID everywhere below, not whichever doc Step 1 loads.

- P_000's SYSTEM_DOCUMENTATION.md always loads in Step 1 regardless of attached project (Hub-wide reference, by design) — that does NOT make this a "P_000 session." Use the attached Project (P_400/P_800/P_300/etc.) in the Step 3 chat name and any WO/ledger/review-note session label.

**Fallback chain (added 2026-08-11, ref WO-P000-E17.001/EC-006/EC-007) — run in order, stop at the first hit:**

1. Attached-project block present and unambiguous → use it. Done.
2. Missing or ambiguous → `recent_chats(n=1)`. Title carries a clean P_XXX prefix → use it.
3. Still missing/ambiguous → widen to `recent_chats(n=3-5)`. A consistent P_XXX pattern across them → use it.
4. Still nothing → check that Project's architecture doc header (on-demand doc, e.g. P_XXX_SYSTEM_DOCUMENTATION.md) for its Project ID field → use it.
5. No doc either → ask Tony directly. Never default to P_000. (See EC-003, EC-007.)

This chain recovers a *missing or ambiguous* Project ID from conversation/doc context. It does not help when no Claude.ai Project is attached to the chat at all (a Project-settings issue, not a Step 0.5 issue) — that case still lands on step 5, ask Tony, same as before.

---

## Step 0.6 - Boot-File Check (added 2026-09-11, ref WO-P000-E29.001)

After Step 0.5 identifies the Project ID, check for a same-day boot file before running Steps 1/1b/2 in full.

1. `Test-Path Agentic-Hub-Governance\boot\[Project ID]_Boot.md`. Not found -> skip to Step 1, full sequence, unchanged.
2. Found -> fresh check, both must hold: (a) boot file's LastWriteTime is today's calendar date, AND (b) no `WO-[Project ID]-*.md` under `Agentic-Hub-Governance\work_orders\` has a LastWriteTime newer than the boot file's. Either fails -> STALE, skip to Step 1, full sequence, unchanged -- never silently trust a stale boot file.
3. FRESH -> display the boot file's content verbatim (it already carries its own Suggested chat name heading, WO table, flags, next step) instead of the Steps 1/1b/2 DOC PULLS specifically (P_000_SYSTEM_DOCUMENTATION.md, on-demand docs). Step 0 (runtime check) still runs regardless -- a headless run minutes earlier attests to nothing about THIS session's own MCP connection (EC-009 precedent).
3b. FRESH does NOT substitute for the project's own session header/summary or its lessons-file read (added 2026-09-14, ref P_115 session 09:59-10:41 ET, roughly 1/3 of a 42-min session attributed to this gap). A FRESH hit still must: (a) read the active project's own lessons/durable-findings file if its project-context skill mandates one at INIT (e.g. p115-project-context's tasks/lessons.md) -- the boot file covers WO status only, never durable lessons; (b) live-read account params + risk config and display them as the session header/summary block (balance, risk mode, trading mode, strategies active) -- the boot file's WO/flags/next-step content is not a substitute for this and was never designed to be. Do these as one combined read, not a second full INIT pass.
4. Lazy-load exception: if the session's actual task needs system-doc detail the boot file doesn't carry (Python architecture rules, exact parameter values, a specific past error correction), run Step 1/2 on demand at that point, not preemptively.
5. On a FRESH hit, Step 3's chat-name heading is already satisfied by the boot file's own heading -- do not regenerate that specifically. Step 3b above (header/summary/lessons) is not covered by this exception.

---

## Step 1 — Load System Doc (disk-canonical)

Read: `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_DOCUMENTATION.md`

No filesystem access → skip to Step 5, apply protocols, proceed.

TONY_ABOUT_ME.md and TONY_STYLE_RULES.md are always-on in Project knowledge.

On-demand (read only when task needs it):

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

`[Project ID]` = the Project identified in Step 0.5. Never P_000 unless Step 0.5 actually identified P_000.

`Suggested chat name: [Project_ID] [Day], [Month] [DD], [YYYY] [HH:MM] ET [optional session-type label]`

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

| Rule | Value |
|---|---|
| 0 Approval | Write nothing until Tony approves |
| 1 Artifact order | Publish artifact FIRST if Tony must act on it, then instructions |
| 2 Save path | State: `Save to: C:\Users\Trader\AI-Agent-Learning-Hub\[project]\[subfolder]\` |
| 4 Skill update note | After any SKILL.md/README.md/arch ref: "Customize → Skills → open → edit/replace" |
| 5 Delivery order | Config → Domain → Infrastructure → Application → CLI → .bat |
| 6 No partial files | `PAUSING — [filename] next response. Type "continue".` |

Standard paths (Rule 3):

| Type | Path |
|---|---|
| Python | `...\projects\[P_XXX]\python\` |
| ThinkScript | `...\projects\[P_XXX]\tos_scripts\` |
| Shared util | `...\shared_resources\python_utils\` |
| Prompt template | `...\shared_resources\llm_prompts\` |
| Skill file | `.claude\skills\[skill-name]\SKILL.md` ONLY |
| Project notes | `...\docs\project_notes\` |

### Protocol C — PowerShell Timeouts
Trigger: any session using Windows-MCP PowerShell. Two limits: tool `timeout` param and MCP global ceiling (~240s hard, not overridable — dominant failure mode). Default 30s for trivial reads only (`Test-Path`, `Get-ChildItem`, small `Get-Content`).

| Operation | Timeout (s) |
|---|---|
| pip install (single) | 120 |
| pip install -r requirements.txt | 300 |
| uvx / npx first-run | 300 |
| conda install / env update | 600 |
| Invoke-WebRequest (large) | 180 |
| Recursive Hub scans (1000+ files) | 120 |
| TOS XML export reads | 60 |

Unsure → 120s. Unexpected timeout → escalate 30→120→300→600; 600 fails → stop, report. Baseline (don't re-test): PowerShell 7.5.4 cold start ~0.5s; AV=Aura; startup not the bottleneck.

**Transport ≠ timeout.** "Failed to call tool"/"No result received" = transport failure — refresh; session >85% → new chat. Never retry with escalating timeouts — switch to Claude Code CLI (`cd` project folder in Anaconda Prompt → `claude`).

Never call a Python .bat synchronously via PowerShell — use `_mcp.ps1` wrappers:

| Bat | MCP-safe wrapper |
|---|---|
| P_010_daily_posture.bat | P_010_daily_posture_mcp.ps1 |
| P_010_run_intraday_vp_check.bat | P_010_intraday_mcp.ps1 |
| P_300_DailyEval_v2.bat | P_300_DailyEval_mcp.ps1 -Symbol XYZ |
| P_300_AddPattern.bat | P_300_AddPattern_mcp.ps1 -XlsxPath "..." |
| P_020_Weekly_Update.bat | P_020_WeeklyUpdate_mcp.ps1 |

Shared engine: `...\shared_resources\hub_mcp_launcher.ps1`. New bats get a matching `_mcp.ps1` wrapper before session end. Multi-step/escaping-heavy ops: write a `.ps1` to disk and run it — never cram complex logic into an inline command param.

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

Non-negotiables: never confuse command timeout/transport/permission errors · never assume absent without verifying · never retry blindly · never optimize for speed when Tony needs diagnosis · never emit `[OK]`/`SUCCESS`/`DONE`/`written` without the real call return confirming it — no placeholder string survives a session boundary.

Structure recurring failures: Immediate Containment → Structural Repair (rule/skill/doc change) → Prevention (durable artifact).

### Protocol E — Mixed-Environment File Handling
Trigger: file output needed; runtime may be Linux sandbox, destination Windows.

- Windows-MCP present → write directly to Windows paths.
- No Windows-MCP → Linux sandbox: create in `/mnt/user-data/outputs/` → `present_files` → manifest table of Windows destinations → Tony downloads + places. Format: `CREATED IN: /mnt/user-data/outputs/` + `TARGET (copy to): | File | Windows Destination |`
- **Skill files:** editing the disk file does NOT update the live skill. Canonical source: `.claude\skills\[skill-name]\SKILL.md`. After editing, update IN THE APP via Customize → Skills. Never write to `/mnt/skills/` (read-only).

### Protocol F — Session Close
Trigger: Tony signals the session is ending, or a WO closes this session. Two independent checks, both run every time — neither excuses the other.

**F1 Lessons.** New lesson for a future session (fix that worked, mistake not to repeat, architecture decision + why)? Yes → write into the relevant project's SKILL.md/bug table now, not a someday-note. No → skip silently.

**F2 State.** Session changed code, ran a validation, or moved project state (file versions, validation numbers, blocked/next items)? Yes → write a Current-State entry to `[Project ID]/tasks/todo.md` (Project ID from Step 0.5), verified via mtime check — same discipline as any other Hub write. NOT skippable when state changed; F1's "skip if nothing new" does not apply to F2. State can change with no new lesson, or vice versa — check both, every time. (See EC-004.)

**F3 Status-Claim Verification.** Before any session-close summary or multi-item recap stating WO, Independent Review, or completion status: re-read each item's Status line / relevant checkbox live, in the same turn -- never from memory of the session's own actions. Same rule as the Standing Rule below, applied specifically at session close. (See EC-005.)

**F4 Git Session-End Reminder.** Trigger: same as Protocol F. Git commands hang via windows-mcp (credential-helper conflict) -- Claude never runs them (GIT_WORKFLOW.md Never Touch rule). Surface as a mandatory close-out line every session, not conditional on F1/F2 findings: "Run your GIT_WORKFLOW.md session-end steps (status -> stage -> commit -> push) before ending this session." Written discipline with no execution trigger doesn't happen -- same failure shape as P_115's orphaned lessons.md. (See EC-008.)

## Edge Cases

| Situation | Action |
|---|---|
| tool_search errors in Step 0 | State error, ask Tony to confirm environment |
| Windows-MCP call fails mid-session after working earlier | Re-run Step 0 immediately — treat the new result as authoritative (see Step 0 re-check trigger) |
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

Before reporting ANY claim about session or WO state -- negative or positive -- review history → verify with tools → only then report. Never assume an action was or wasn't taken from memory of the session's own narrative. Independent Review claims specifically: "this session did the work" and "a separate session reviewed it" are different facts -- never state the second without a live-checked WO file backing it. (See EC-005.)

---

## Error Corrections Log

**EC-010 -- Step 0.6 boot-file FRESH hit skipped SIP Step 1 (session header) and Step 4 (summary), plus the active project's own lessons.md read (2026-09-14). High.** A P_115 session hit a FRESH boot-file match and, per the then-current Step 0.6 text, treated the boot file's WO/flags content as covering the whole INIT -- it does not, and never claimed to. Two concrete failures resulted: (1) never displayed the mandated balance/risk-mode/trading-mode/strategies-active session summary at all, caught only when Tony asked directly; (2) never read p115-project-context's own tasks/lessons.md, so an already-written 8/18/26 fix (unrelated chart overlay badges are not a competing verdict authority) was not loaded and the same mistake recurred on a live signal call, requiring a Tony correction mid-session. Tony flagged the combined cost afterward as roughly 42 minutes for what should be an established, fast process, with roughly a third of it attributable to this gap by his own accounting. Fix: Step 0.6 item 3 narrowed to explicitly cover only the Steps 1/1b/2 doc-pull portion; new item 3b added requiring the project's own lessons read plus a live-read session header/summary on every FRESH hit, not treated as covered by the boot file.

**EC-009 -- Step 0 result assumed valid for the whole session; no re-check on mid-chat client switch (2026-09-07). Medium.** A P_800 session ran Step 0 at first message (Windows-MCP present, Desktop) and used it correctly for several turns of live disk reads. Tony then switched the same chat from Desktop to a web browser tab mid-conversation -- no new "first message" existed to re-trigger Step 0, so the session kept assuming file access two turns after it was actually gone. Caught only because a Windows-MCP call was tested live and returned "not available." Fix: Step 0 re-check trigger added -- re-run `tool_search` immediately on a Windows-MCP call failure or a stated/implied client switch; the new result overrides the session-start read.

**EC-008 -- GIT_WORKFLOW.md session-end steps never wired into INIT/session-close (2026-08-29). Medium.** GIT_WORKFLOW.md prescribes a status/stage/commit/push routine every session, but nothing in this skill's Protocol F, P_000_SYSTEM_DOCUMENTATION.md, or WO_COMPLETION_GATE.md ever surfaced it -- a written instruction with no executed step, same shape as P_115's orphaned lessons.md (SIP v3.6). Found while investigating a live 3-day commit gap flagged in WO-P000-E2.001's own Independent Review. Fix: Protocol F4 added -- mandatory close-out reminder every session, not conditional on F1/F2 findings.

**EC-006 -- Step 0.5 asked Tony with no fallback attempt despite recoverable context (2026-08-11). Medium.** A P_400 session asked Tony directly which project was attached -- the only fallback Step 0.5 had, working as designed but never attempting conversation- or doc-context recovery first. Fix: four-step fallback chain added to Step 0.5 (`recent_chats(n=1)` → widen to n=3-5 → project doc header check → ask Tony), ref WO-P000-E17.001. Also logged as EC-007 in P_000_SYSTEM_DOCUMENTATION.md Section 6 (Hub-wide log).

**EC-005 -- Session-close recap claimed Independent Review for two WOs that never received it (2026-08-07). High.** After completing real OWNER_DONE-level work on WO-P000-E3.001 and WO-P000-E7.001 (Completion Gate items, doc fixes) in the same session, the closing chat summary described both as "closed out... with real Independent Review" -- conflating "this session did the work" with "a separate session reviewed it," which the implementing session structurally cannot supply for itself. The WO files were internally accurate the whole time (E3.001 said "pending," E7.001's checkbox was unchecked); only the free-text chat summary was wrong, because it was generated from memory of the session's actions instead of a live re-check. Fix: Standing Rule broadened to cover positive claims, not just negatives; Protocol F3 added requiring a live status re-check before any multi-item session-close summary.

**EC-004 — State from 2 sessions never reached todo.md (2026-07-12/13). High.** Protocol F only checked for lessons; state is a different question F1 never asked — F1 found no new "lesson" either session despite `pattern_miner.py` moving v1.4→v2.1 across two validation rounds. Next session's INIT loaded stale todo.md, re-opened an already-resolved question. Fix: F1/F2 split, F2 mandatory + mtime-verified whenever state changed.

**EC-003 — Session mislabeled as P_000 despite P_800 attached (2026-07-08). Medium.** Step 1 loads P_000's doc regardless of attached project by design; nothing checked attached-Project vs. loaded doc, so every note/label defaulted to "P_000" — 5 ledger entries hand-corrected after. Fix: Step 0.5.

**EC-002 — Skill file placed in wrong location (2026-06-04). High.** Wrote to read-only `/mnt/skills/user/...` instead of outputting for manual placement. Rule: skill files go ONLY to `.claude\skills\[skill-name]\SKILL.md`; update live skill IN THE APP.

**EC-001 — Skill file written to wrong location (2026-05-29). High.** Wrote SKILL.md to `shared_resources\skills\` instead of `.claude\skills\`. Rule: verify `.claude\skills\` exists first; write only there.

---

*Last Updated: 2026-09-14 -- Step 0.6 amended (EC-010): FRESH boot-file hit no longer substitutes for the project's own lessons.md read or the live session header/summary (balance, risk mode, trading mode, strategies active) -- only for the Steps 1/1b/2 system-doc pulls. Prior: 2026-09-11 -- Step 0.6 Boot-File Check added (ref WO-P000-E29.001): a same-day boot file with no newer WO file for that project lets a live session skip straight to displaying it instead of running Steps 1/1b/2 in full; Step 0's own runtime check still runs every session regardless -- a headless run minutes earlier proves nothing about this session's own MCP connection. Prior: 2026-09-07 -- Step 0 re-check trigger added (EC-009): a mid-session Desktop-to-web client switch went undetected for several turns until a live Windows-MCP call failed; Step 0 now re-runs on a call failure or a stated/implied client switch, not just at the session's first message. Prior: 2026-08-29 -- Protocol F4 added (git session-end reminder, EC-008): GIT_WORKFLOW.md's session-end routine existed but no session-close step ever invoked it. Prior: 2026-08-11 — Step 0.5 fallback chain added (EC-006, ref WO-P000-E17.001): `recent_chats(n=1)` → widen n=3-5 → project doc header check → ask Tony, replacing the ask-Tony-only fallback that ran with no recovery attempt first. Prior: 2026-07-13 Protocol F split into F1 (lessons) + F2 (state checkout, mandatory, mtime-verified) (EC-004); inline violation blockquotes collapsed to EC-log pointers; Protocol B/E prose tightened into tables. No rule/path/condition removed. Prior: 2026-07-08 Step 0.5 added (EC-003). Prior: 2026-07-06 Protocol F added. Prior: 2026-06-12 Compressed v3.0.*
