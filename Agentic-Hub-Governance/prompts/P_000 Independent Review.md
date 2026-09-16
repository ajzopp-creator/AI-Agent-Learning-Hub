Built it — one reusable script, works for any project. Confirmed it resolves correctly across P_020, P_400, P_115, P_800.

**📁 Saved:** `C:\Users\Trader\AI-Agent-Learning-Hub\Agentic-Hub-Governance\utils\launch_independent_review.ps1`

Going forward, one line, from anywhere:

```powershell
.\launch_independent_review.ps1 -WOId "WO-P400-E7.002"
```

It figures out the project folder from the WO number itself (same disk-scan logic the daily boot script uses — no hardcoded project list to keep in sync), writes a fresh generic review prompt for that specific WO, and launches it detached via `--bg`. Optional `-MaxBudget` (default $3.00) and `-MaxTurns` (default 40) if a review needs more room.

Same rule as tonight: it can only touch the one WO file, only writes a verdict (CLOSED or `BLOCKED ON:`), never edits code. Check on any of them with `claude logs <session-id>`, or just reopen the WO — the Status line is the real signal.