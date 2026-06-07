# GIT_WORKFLOW.md
## AI-Agent-Learning-Hub — Git Workflow & Commit Policy
**Version:** 1.0  
**Created:** 2026-06-07  
**Owner:** P_000

---

## Commit Frequency

Commit after every completed work order (WO closes). If no WO activity on a given day but code changes exist, commit by end of day.

**Default:** at least one commit per trading day if changes were made.

---

## Commit Message Format

```
WO-[ID] - [deliverable brief] - [date]
```

### Examples

- `WO-P000-E2.001 - Finalize .gitignore and configure git workflow - 2026-06-07`
- `WO-P010-E1.003 - Add SPY intraday posture detection - 2026-06-08`
- `WO-P300-E2.001 - Refactor pattern recognition logic - 2026-06-09`

---

## Scope — What Gets Committed

**YES — commit these:**
- Python source code (.py files)
- Documentation (README.md, .md files in /docs)
- Configuration files (config.yaml, config.json)
- Batch scripts and PowerShell files (.bat, .ps1)
- .gitignore and workflow docs (GIT_WORKFLOW.md, etc.)
- Work-order ledger (04-Shared-Resources/work_orders/)
- ThinkScript files (.ts in tos_scripts/)
- Templates and prompts (llm_prompts/)

**NO — do NOT commit these:**
- Logs (logs/ folder, *.log files)
- __pycache__, .pyc, build artifacts
- .env, local_config.json, secrets.json
- data/xml_exports/, data/historical/ (large data files)
- .vscode local settings, .idea IDE files
- Anything in .gitignore

---

## Push Discipline

**Push to GitHub immediately after every commit.**

Command:
```
git push
```

This ensures cloud backup is current. Do not let local commits pile up — every commit → immediate push.

---

## Branch Strategy

**Single branch only: `main`**

No feature branches (single operator, simple workflow). All commits go directly to `main`.

---

## Typical Session Workflow

1. Start work on a WO
2. Write code / docs / configs
3. Test locally
4. `git add .` (or `git add [files]` for selective staging)
5. `git commit -m "WO-[ID] - [brief] - [date]"`
6. `git push` (to GitHub)
7. WO marked complete
8. Repeat

---

## Recovery Procedure

If local changes are lost:
```
git clone https://github.com/[account]/AI-Agent-Learning-Hub.git [new-folder]
```

All committed history + files restored in seconds.

---

## Non-Negotiables

- **.env and secrets.json MUST NOT be committed** — verify via `git status` before every push
- **Every commit must be pushed same day** — no stale local commits
- **Use WO message format consistently** — audit trail requires it
- **.gitignore must be kept current** — add exclusions as new file types appear

---

**End of GIT_WORKFLOW.md**
