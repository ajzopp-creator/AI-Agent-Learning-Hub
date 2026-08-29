# P_810 — Email Tax Extractor

Extracts AJZ Strategies-related tax emails (receipts, notifications, statements) from Tony's Thunderbird mbox cache and produces a dated record for tax recordkeeping. Peer project to P_805 (Email Trade Extractor) — shares the reusable mbox/IMAP/header-decode layer via `shared_resources\python_utils\`, but has its own sender whitelist, schema, and output.

**Status:** Scaffold only — docs and folder structure exist, no code yet. See `docs\P_810_SYSTEM_DOCUMENTATION.md` Section 12.3 for what's needed to start Phase 1.

**Owner:** Tony
**Root path:** `C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_810_Email_Tax_Extractor\`
**Python:** `C:\Users\Trader\.conda\envs\p140\python.exe` (shared p140 conda env — never a project-local venv)

## Quick Reference

| Need | See |
|------|-----|
| Full architecture, rules, roadmap | `docs\P_810_SYSTEM_DOCUMENTATION.md` |
| Approved tax senders | `data\sender_sheet.csv` (currently empty — awaiting real data) |
| Session state / what's next | `tasks\todo.md` |
| Hub-wide standards | `..\P_000_PythonClaudeLocalLLM\docs\P_000_SYSTEM_DOCUMENTATION.md` |
