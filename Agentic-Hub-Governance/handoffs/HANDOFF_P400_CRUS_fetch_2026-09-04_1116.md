# Handoff: CRUS Tier-2B fetch-snapshot + fetch-chain

Date: 2026-09-04 11:16 ET
Project: P_400
Reason: Two Windows-MCP PowerShell attempts to run cli.py stalled the relay
(first: generic tool failure; second: cli.py --help hit the 4-min transport
ceiling with no result). Ping confirmed the relay itself is up both times,
so per peh-handoff v1.10 this hands off instead of retrying the work call
again through MCP.

## Run these two commands, in order, in Claude Code

```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python
set PYTHONPATH=C:\Users\Trader\AI-Agent-Learning-Hub
C:\Users\Trader\.conda\envs\p140\python.exe cli.py fetch-snapshot CRUS --earnings-date 2026-11-04 --sector Semiconductors
```

```
cd C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_400_TradeOrderManagement\python
set PYTHONPATH=C:\Users\Trader\AI-Agent-Learning-Hub
C:\Users\Trader\.conda\envs\p140\python.exe cli.py fetch-chain CRUS --type call
```

## Success criteria
- fetch-snapshot writes `snapshot_CRUS.json` with `data_source="schwab_api"`,
  real price/bid/ask/atr_14.
- fetch-chain writes a chain JSON with an auto-selected near-0.50-delta
  contract in the 21-45 DTE window (or reports why none qualified).

## If it errors
Paste the full terminal output back to Tony/Claude — do not silently retry
with different flags.

## Note
Earnings date (2026-11-04) and sector (Semiconductors) were web-search-sourced
by Claude this session per Bucket B rule, not pulled from Schwab.
