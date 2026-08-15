# GIT_WORKFLOW.md
## AI-Agent-Learning-Hub | Git Backup Workflow
## Owner: P_000 (WO-P000-E2.001)

---

## Critical Rule

**Never run git commands through Windows-MCP.** Every git command hung to the
transport timeout in testing (credential-helper conflict with the MCP shell).
All git operations run manually in Anaconda Prompt or Claude Code CLI.

Claude's role in a git session is limited to: drafting commands for Tony to
run himself, reading `git status` / `git log` output Tony pastes back, and
deciding what to stage or restore based on that output. Claude does not
attempt git through any MCP tool, ever.

---

## Repo Info

| | |
|---|---|
| Remote | `https://github.com/ajzopp-creator/AI-Agent-Learning-Hub.git` |
| Branch | `main` (tracks `origin/main`) |
| Root | `C:\Users\Trader\AI-Agent-Learning-Hub\` |

---

## Standard Session-End Workflow

1. `git status` — review what changed this session.
2. Stage deliberately. For large sessions, prefer `git add -A` then restore
   anything that shouldn't ship (see Exclusions below) rather than trying to
   hand-pick hundreds of files.
3. `git status` again — confirm the staged list is what you actually want
   committed before running `git commit`.
4. `git commit -m "<message>"` — see Commit Message Convention below.
5. `git push origin main`.
6. Confirm the push output shows the expected commit range
   (`<old-hash>..<new-hash> main -> main`).

---

## Known Exclusions (Restore Before Committing)

**2024 and 2025 P115 trade journal history** — not needed in the repo.
Confirmed by Tony 2026-08-04. If a broad `git add -A` picks these up:

```
git restore --staged "trading_journal/TradeManagement/P115/2024-*"
git restore --staged "trading_journal/TradeManagement/P115/2025-*"
git restore --staged "trading_journal/TradeOrderManagement/P115/2024-*"
git restore --staged "trading_journal/TradeOrderManagement/P115/2025-*"
```

**Terminal output redirects** — leftovers from `> filename.txt` style
redirects during a session (e.g. `outputgit.txt`, `scriptsout.txt`). Check
`git status` for unfamiliar top-level or `projects/` root files before
committing; restore anything that's clearly a stray redirect, not a Hub
deliverable.

---

## .gitignore Backup Pattern

Any file write in this session that creates a dated backup copy
(`Copy-Item $path "$path.backup_$dt"`, per the PowerShell file-write
standard) should be excluded from version control. `.gitignore` includes
`*.backup_*` to cover this. If a new backup naming convention gets
introduced, add its pattern to `.gitignore` in the same session — don't let
backup files start piling into `git status`.

---

## Commit Message Convention

`Session <YYYY-MM-DD>: <short summary of WOs / work closed this session>`

Example:
`Session 2026-08-04: PEH v1.4 (WO-P000-E11.001/E12.001), WO-P000-E10.001 caller-propagation triage across P_020/P_400/P_300/P_805`

Keep it to one line. If multiple unrelated WOs closed in one session, list
the WO IDs rather than trying to summarize the work in prose.

---

## Renames Show as Delete+Add Sometimes

Git's rename detection is similarity-based, not path-based. Large restructures
(e.g. the TradeManagement -> TradeOrderManagement vault rename from
WO-P800-E3.003) will show correctly as `renamed:` for files git can match,
but small or heavily-edited files may show as separate `deleted:` / `new file:`
pairs instead. This is a display quirk, not a data problem — don't try to
force git to recognize a rename it didn't detect.

---

## Last Updated
2026-08-04 — Initial version, drafted after first full-session commit+push
under the current governance-heavy session pattern (WO-P000-E2.001).