@echo off
REM P_805 Daily Pipeline - Phase 3 -> 3.5 -> 4 -> 5.3
REM Run at 9:15 AM: extract signals, enrich direction, rank consensus, move mail
REM v1.0 - 2026-07-18

setlocal enabledelayedexpansion

cd /d "C:\Users\Trader\AI-Agent-Learning-Hub\projects\P_805_Email_Trade_Extractor"

if not exist "python\logs" mkdir python\logs

set logfile=python\logs\pipeline_runs.log

echo. >> "%logfile%"
echo ================================================================================ >> "%logfile%"
echo P_805 DAILY PIPELINE - %date% %time% >> "%logfile%"
echo ================================================================================ >> "%logfile%"

REM --- STEP 1: Phase 3 - Ticker Extraction ---
echo [STEP 1/4] Phase 3 - Ticker extraction... >> "%logfile%"
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\cli.py" --phase 3 >> "%logfile%" 2>&1
set p3err=%errorlevel%

if %p3err% equ 0 (
    echo [SUCCESS] Phase 3 complete - %date% %time% >> "%logfile%"
) else (
    echo [ERROR] Phase 3 failed - exit code %p3err% - %date% %time% >> "%logfile%"
    echo [ABORT] No signals CSV - downstream phases skipped. >> "%logfile%"
    goto :end
)

REM --- STEP 2: Phase 3.5 - LLM Direction Enrichment ---
echo [STEP 2/4] Phase 3.5 - LLM direction enrichment... >> "%logfile%"
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\cli.py" --phase 35 >> "%logfile%" 2>&1
set p35err=%errorlevel%

if %p35err% equ 0 (
    echo [SUCCESS] Phase 3.5 complete - %date% %time% >> "%logfile%"
) else (
    echo [WARNING] Phase 3.5 failed - exit code %p35err% - %date% %time% >> "%logfile%"
    echo   Continuing to Phase 4 - unresolved rows stay direction=unknown. >> "%logfile%"
)

REM --- STEP 3: Phase 4 - Consensus Ranking ---
echo [STEP 3/4] Phase 4 - Consensus ranking... >> "%logfile%"
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\cli.py" --phase 4 >> "%logfile%" 2>&1
set p4err=%errorlevel%

if %p4err% equ 0 (
    echo [SUCCESS] Phase 4 complete - ranked CSV written - %date% %time% >> "%logfile%"
) else (
    echo [ERROR] Phase 4 failed - exit code %p4err% - %date% %time% >> "%logfile%"
    echo [ABORT] No ranked CSV - Phase 5.3 skipped. >> "%logfile%"
    goto :end
)

REM --- STEP 4: Phase 5.3 - IMAP Move to ExtractedNewsletterFolder ---
echo [STEP 4/4] Phase 5.3 - IMAP move... >> "%logfile%"
"C:\Users\Trader\.conda\envs\p140\python.exe" "python\cli.py" --phase 53 >> "%logfile%" 2>&1
set p53err=%errorlevel%

if %p53err% equ 0 (
    echo [SUCCESS] Phase 5.3 complete - mail moved - %date% %time% >> "%logfile%"
) else (
    echo [ERROR] Phase 5.3 failed - exit code %p53err% - %date% %time% >> "%logfile%"
    echo   Ranked CSV is still valid - this is non-critical to the morning output. >> "%logfile%"
)

:end
echo ================================================================================ >> "%logfile%"
echo P_805 PIPELINE RUN COMPLETE - %date% %time% >> "%logfile%"
echo ================================================================================ >> "%logfile%"
