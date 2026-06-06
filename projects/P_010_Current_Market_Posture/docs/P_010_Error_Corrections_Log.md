
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
