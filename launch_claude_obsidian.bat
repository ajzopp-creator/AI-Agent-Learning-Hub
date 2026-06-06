@echo off
REM Launch Obsidian + Claude Desktop together
REM P_800 — launch_claude_obsidian.bat

start "" "C:\Program Files\Obsidian\Obsidian.exe"
timeout /t 3 /nobreak >nul

REM Get current Claude Desktop path dynamically
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-Process claude -ErrorAction SilentlyContinue | Select-Object -First 1).Path"`) do set CLAUDE_PATH=%%i

REM If Claude is already running, path is found above; otherwise find the exe
if "%CLAUDE_PATH%"=="" (
    for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "Get-ChildItem 'C:\Program Files\WindowsApps' -Recurse -Filter 'Claude.exe' -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notlike '*claude-cli*' } | Select-Object -First 1 -ExpandProperty FullName"`) do set CLAUDE_PATH=%%i
)

start "" "%CLAUDE_PATH%"