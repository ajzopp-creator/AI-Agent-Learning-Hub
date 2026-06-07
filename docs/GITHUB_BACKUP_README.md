# GITHUB_BACKUP_README.md
## GitHub as Primary Backup for AI-Agent-Learning-Hub
**Version:** 1.0  
**Created:** 2026-06-07  
**Owner:** P_000

---

## Why GitHub

Three critical folders are continuously backed up to GitHub:

1. **projects/** (~500 MB–1 GB)
   - All project code, configs, work-order artifacts
   - P_000, P_010, P_020, P_115, P_300, P_400, P_800, P_805, etc.

2. **04-Shared-Resources/** (~5–20 MB)
   - Work-order ledger, shared utilities, governance
   - Hub-wide single source of truth

3. **trading_journal/** (~100 MB–500 MB)
   - Obsidian vault, daily notes, trade logs, templates
   - Access offline, sync back to local after recovery

**Total:** ~1–2 GB. Well within GitHub free tier limits.

**Risk mitigated:** Local disk failure = instant recovery via `git clone`.

---

## How to Push

After every commit, push to GitHub:

```bash
git push
```

This command:
- Uploads all local commits since last push
- Updates GitHub's remote tracking branches
- Keeps cloud backup current (same-day, automatic)

No authentication prompt if you've set up credentials once (PAT or Git Credential Manager).

---

## How to Recover

If local Hub is lost or corrupted, restore in seconds:

```bash
git clone https://github.com/[account]/AI-Agent-Learning-Hub.git [recovery-folder]
cd [recovery-folder]
```

All files, commit history, and branches are restored. The working directory is ready to use immediately.

---

## .gitignore Discipline

**Critical:** .gitignore MUST exclude:
- Logs (logs/, *.log)
- __pycache__, .pyc, build artifacts
- .env, local_config.json, secrets.json — **NEVER commit credentials**
- Large data files (data/xml_exports/, data/historical/)
- OS junk (.DS_Store, Thumbs.db)

**Before every push, verify:**
```bash
git status
```

Check that only intended files are staged. If you see .env, secrets.json, or __pycache__, they should be gitignored, not staged.

---

## Private Repository

The GitHub repo is **PRIVATE** — trading data, account configs, strategy code are not exposed to the public internet.

Only you can view or clone the repo (unless you grant collaborator access).

---

## Backup Schedule

- **Frequency:** After every completed work order, or daily if changes exist
- **Method:** `git push` immediately after `git commit`
- **Verification:** GitHub web UI shows latest commit and file count

---

## Typical Workflow

1. Work on trading projects, scripts, configs
2. Test locally
3. Commit: `git commit -m "WO-[ID] - [brief] - [date]"`
4. Push: `git push`
5. GitHub now has the latest backup
6. Sleep well — cloud backup is current

---

**For full workflow details, see GIT_WORKFLOW.md**

**End of GITHUB_BACKUP_README.md**
