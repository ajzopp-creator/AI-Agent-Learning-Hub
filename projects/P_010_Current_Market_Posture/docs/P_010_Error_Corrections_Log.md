
================================================================================
ERROR CORRECTIONS LOG
================================================================================

ERROR 001 — Intraday Cascading Upgrade Bug
Date Fixed : 2026-03-31
Severity   : HIGH
Symptom    : Running intraday check multiple times in one day caused
             risk_mode to cascade: OFF → HALF → FULL (wrong).
             Each run read morning_baseline from risk_config['risk_mode'],
             which was already overwritten by the previous intraday run.
Root Cause : intraday script read morning_baseline = risk_config['risk_mode']
             instead of a preserved field.
Fix Applied: Script now checks for 'morning_risk_mode' field on load.
             If missing (first run of day): captures and writes it.
             If present: always reads from it — never from 'risk_mode'.
Rule       : NEVER read morning baseline from 'risk_mode'. Always use
             'morning_risk_mode' (preserved). If field is missing from
             config, the morning script needs to be updated to write it.
Verify     : After intraday run, P_010_RiskConfig.json must contain BOTH:
               "morning_risk_mode": "OFF"   <- locked, never changes
               "risk_mode": "HALF"          <- adjusted final mode

================================================================================

================================================================================

ERROR 002 — Windows-MCP Start-Process Hang Bug
Date Fixed : 2026-06-01
Severity   : HIGH
Symptom    : Start-Process python.exe -NoNewWindow caused MCP to block ~4 min then time out.
Root Cause : Child process inherits MCP stdio pipes; MCP server blocks until child exits.
Fix Applied: All Python launches use Start-Job + cmd /c (child detached from MCP pipes).
Rule       : NEVER use Start-Process -NoNewWindow. ALWAYS use Start-Job + cmd /c.
             See Section 8 Manual Triggers for canonical command block.
Verify     : ~4 min hang with no output is the symptom. Fix = switch to Start-Job pattern.

================================================================================