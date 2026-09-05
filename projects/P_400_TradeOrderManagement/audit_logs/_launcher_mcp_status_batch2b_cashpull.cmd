@echo off
call "%~1"
if errorlevel 1 (
    echo FAILED:%errorlevel% > "%~2"
) else (
    echo SUCCESS > "%~2"
)
