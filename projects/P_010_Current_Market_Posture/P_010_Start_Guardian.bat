@echo off
title P_010 Claude Session Guardian
echo =============================================
echo  P_010 Claude Session Guardian -- STARTING
echo  Run this at the start of every trading day.
echo  Close this window to stop monitoring.
echo =============================================
echo.

REM ---------------------------------------------------------------
REM  MISSED MORNING RUN CHECK
REM  If daily posture log doesn't exist for today, run it now.
REM  Catches late laptop starts where Task Scheduler missed 7:30 AM.
REM ---------------------------------------------------------------
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set today=%%c%%a%%b)
set LOGCHECK=%~dp0logs\P_010_Daily_%today%.log

if not exist "%LOGCHECK%" (
    echo [GUARDIAN] Daily posture log not found for today -- running now...
    echo [GUARDIAN] Log will be written to: %LOGCHECK%
    echo.
    call "%~dp0P_010_daily_posture.bat"
    echo.
    echo [GUARDIAN] Daily posture complete -- starting session monitor...
    echo.
) else (
    echo [GUARDIAN] Daily posture already ran today -- OK
    echo [GUARDIAN] Log: %LOGCHECK%
    echo.
)

REM ---------------------------------------------------------------
REM  START SESSION GUARDIAN
REM ---------------------------------------------------------------
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0P_010_Claude_Session_Guardian.ps1"
pause
