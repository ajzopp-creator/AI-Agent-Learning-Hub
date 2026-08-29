
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

================================================================================

ERROR 003 -- Toast Notification Silent Failure (Two-Stage)
Date Fixed : 2026-08-10
Severity   : MEDIUM (no data-integrity impact, but defeats the point of
             fail-loud alerting -- a silently-broken notification looks
             identical to a genuinely quiet, healthy day)
Symptom    : send_toast() returned True / PowerShell exit code 0, but no
             toast notification was ever visible on screen. Confirmed only
             by Tony watching the screen and seeing nothing -- no automated
             check (exit code, Test-Path, log output) can detect this class
             of failure by itself.
Root Cause : TWO SEPARATE bugs, found in sequence:
             (1) v1 used System.Windows.Forms.NotifyIcon.ShowBalloonTip.
                 NotifyIcon requires an active Windows message loop
                 (Application.Run / Application.DoEvents) to actually
                 render the balloon. A bare console script has no message
                 loop, so the call "succeeds" but nothing ever displays.
             (2) v2 switched to BurntToast (New-BurntToastNotification),
                 which fixed (1) but exposed a second bug: BurntToast was
                 installed via windows-mcp:PowerShell (PowerShell 7 / pwsh),
                 but toast_notify.py's subprocess call invokes powershell.exe
                 (Windows PowerShell 5.1, separate PSModulePath / edition).
                 Compounding this, powershell.exe -Command was returning
                 exit code 0 even after a terminating Import-Module error
                 inside the script block -- so send_toast() had no signal
                 the import had failed.
Fix Applied: (1) Switched to BurntToast module entirely (no message-loop
                 dependency).
             (2) PowerShell template wrapped in explicit try/catch with
                 Continue = 'Stop' and an explicit exit 1 on
                 catch, so a failed Import-Module reliably produces a
                 non-zero process exit. send_toast() also treats non-empty
                 stderr as failure even if the exit code is (wrongly) 0 --
                 belt-and-suspenders against the same class of lie
                 recurring under a different PowerShell host/version.
Rule       : (a) Any Windows notification mechanism built for an unattended
                 script MUST be verified with an actual human watching the
                 screen, not just a clean exit code -- this class of bug is
                 structurally invisible to automated checks.
             (b) When a Python script's subprocess call targets a specific
                 PowerShell executable (here: powershell.exe, i.e. Windows
                 PowerShell 5.1), any module install/verification must be
                 done against THAT SAME executable/edition -- installing or
                 testing via a different PowerShell edition (pwsh / PS7)
                 does not guarantee the module is visible to the one the
                 script actually calls.
             (c) Never trust a subprocess exit code alone as proof of
                 success for a PowerShell -Command block containing
                 -ErrorAction Stop -- wrap in try/catch with an explicit
                 exit code, and treat non-empty stderr as failure too.
Verify     : send_toast() only returns True when PowerShell exits 0 AND
             stderr is empty. A missing/broken BurntToast module now
             produces a visible False return instead of a silent lie.

================================================================================
================================================================================

ERROR 004 -- Intraday .bat False [ERROR] Alongside [SUCCESS] (Unescaped Parens)
Date Fixed : 2026-08-26
Severity   : MEDIUM (no data-integrity impact -- P_010_RiskConfig.json was
             always written correctly -- but trains the operator to ignore
             [ERROR] output, which defeats the point of WO-P010-E1.003's
             fail-loud alerting. First flagged 2026-07-17 as a WO-P010-E1.003
             addendum; sat unfixed for 40 days across two OWNER_DONE passes
             on that WO until reproduced live and root-caused this session.)
Symptom    : P_010_run_intraday_vp_check.bat printed
             "[SUCCESS] Intraday VP validation completed." immediately
             followed by "[ERROR] Intraday check failed with exit code 0"
             on a genuinely clean run (correct JSON, correct signal, exit
             code actually 0).
Root Cause : One echo line inside the `if %errorlevel% equ 0 ( ... ) else
             ( ... )` block contained an unescaped, unmatched-looking
             parenthesis pair in plain text: `(in outputs/)`. cmd.exe's
             parser reads the whole if/else as one parenthesized unit; the
             stray `)` after "outputs/" closed the outer `if (` block early.
             Everything after that point -- the rest of the SUCCESS
             branch's echoes, the literal `) else (`, and the ELSE branch's
             echoes -- then ran as ordinary unconditional commands instead
             of being gated by the if/else, so both branches always
             printed regardless of the real exit code.
Fix Applied: Escaped the literal parentheses with carets:
             `(in outputs/)` -> `^(in outputs/^)`.
Rule       : Any literal `(` or `)` inside an `echo` line -- or any other
             command -- that sits inside a parenthesized `if`/`for`/`else`
             block in a `.bat` file MUST be escaped with `^` or the block
             will silently mis-parse. This applies even when the
             parentheses look balanced in the source (`(in outputs/)`
             reads as balanced to a human, not to cmd.exe inside an
             already-open block).
Verify     : Re-ran P_010_run_intraday_vp_check.bat live (2026-08-26,
             market closed, real grid data) -- output now shows
             "[SUCCESS] Intraday VP validation completed." alone, no
             accompanying [ERROR] line.

================================================================================

