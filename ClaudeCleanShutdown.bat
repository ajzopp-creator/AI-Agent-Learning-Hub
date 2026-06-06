@echo off
echo Closing Claude Desktop cleanly...
taskkill /F /IM claude.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM claude_crashpad_handler.exe /T 2>nul
echo Claude processes closed.
timeout /t 3
