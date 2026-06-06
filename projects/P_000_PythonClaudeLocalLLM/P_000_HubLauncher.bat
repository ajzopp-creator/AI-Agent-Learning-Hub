@echo off
REM P_000_HubLauncher.bat
REM Run ONCE to create Desktop shortcut + pinnable Start Menu entry

SET HUB_PATH=C:\Users\Trader\AI-Agent-Learning-Hub
SET DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\AJZ Hub.lnk
SET START_SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\AJZ Hub.lnk
SET LAUNCHER=%HUB_PATH%\P_000_Hub_Startup.bat
SET PS_SCRIPT=%HUB_PATH%\P_000_Hub_Startup.ps1

REM ── Create PowerShell startup script ────────────────────────────────────────
echo Set-Location "%HUB_PATH%" > "%PS_SCRIPT%"
echo Write-Host "" >> "%PS_SCRIPT%"
echo Write-Host "  ==========================================" -ForegroundColor Cyan >> "%PS_SCRIPT%"
echo Write-Host "     AJZ Strategies - AI-Agent-Learning-Hub" -ForegroundColor Cyan >> "%PS_SCRIPT%"
echo Write-Host "  ==========================================" -ForegroundColor Cyan >> "%PS_SCRIPT%"
echo Write-Host "" >> "%PS_SCRIPT%"
echo Write-Host "  Projects:" -ForegroundColor Yellow >> "%PS_SCRIPT%"
echo Get-ChildItem "%HUB_PATH%\projects" -Directory ^| ForEach-Object { Write-Host "    $_" -ForegroundColor White } >> "%PS_SCRIPT%"
echo Write-Host "" >> "%PS_SCRIPT%"
echo Write-Host "  Integrations:" -ForegroundColor Yellow >> "%PS_SCRIPT%"
echo Get-ChildItem "%HUB_PATH%\integrations" -Directory ^| ForEach-Object { Write-Host "    $_" -ForegroundColor White } >> "%PS_SCRIPT%"
echo Write-Host "" >> "%PS_SCRIPT%"
echo Write-Host "  Python: C:\Users\Trader\.conda\envs\p140\python.exe" -ForegroundColor Green >> "%PS_SCRIPT%"
echo Write-Host "" >> "%PS_SCRIPT%"

REM ── Create CMD startup script ────────────────────────────────────────────────
echo @echo off > "%LAUNCHER%"
echo cd /d "%HUB_PATH%" >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo echo   ========================================== >> "%LAUNCHER%"
echo echo      AJZ Strategies - AI-Agent-Learning-Hub >> "%LAUNCHER%"
echo echo   ========================================== >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo echo   Open with: >> "%LAUNCHER%"
echo echo     1 - Command Prompt >> "%LAUNCHER%"
echo echo     2 - PowerShell >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo set /p CHOICE=  Enter 1 or 2:  >> "%LAUNCHER%"
echo if "%%CHOICE%%"=="1" goto CMD >> "%LAUNCHER%"
echo if "%%CHOICE%%"=="2" goto PS >> "%LAUNCHER%"
echo echo Invalid choice. >> "%LAUNCHER%"
echo pause >> "%LAUNCHER%"
echo goto :eof >> "%LAUNCHER%"
echo. >> "%LAUNCHER%"
echo :CMD >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo echo   Projects: >> "%LAUNCHER%"
echo dir /b /ad "%HUB_PATH%\projects" >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo echo   Integrations: >> "%LAUNCHER%"
echo dir /b /ad "%HUB_PATH%\integrations" >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo echo   Python: C:\Users\Trader\.conda\envs\p140\python.exe >> "%LAUNCHER%"
echo echo. >> "%LAUNCHER%"
echo cmd /k >> "%LAUNCHER%"
echo goto :eof >> "%LAUNCHER%"
echo. >> "%LAUNCHER%"
echo :PS >> "%LAUNCHER%"
echo start powershell.exe -NoExit -ExecutionPolicy Bypass -File "%PS_SCRIPT%" >> "%LAUNCHER%"

REM ── Create shortcuts pointing to cmd.exe (allows Pin to Start) ───────────────
SET CREATE_SHORTCUT=%TEMP%\create_shortcut.vbs

echo Set oWS = WScript.CreateObject("WScript.Shell") > "%CREATE_SHORTCUT%"
echo. >> "%CREATE_SHORTCUT%"
echo REM Desktop shortcut >> "%CREATE_SHORTCUT%"
echo Set oLink = oWS.CreateShortcut("%DESKTOP_SHORTCUT%") >> "%CREATE_SHORTCUT%"
echo oLink.TargetPath = "cmd.exe" >> "%CREATE_SHORTCUT%"
echo oLink.Arguments = "/c ""%LAUNCHER%""" >> "%CREATE_SHORTCUT%"
echo oLink.WorkingDirectory = "%HUB_PATH%" >> "%CREATE_SHORTCUT%"
echo oLink.Description = "AJZ Strategies Hub" >> "%CREATE_SHORTCUT%"
echo oLink.Save >> "%CREATE_SHORTCUT%"
echo. >> "%CREATE_SHORTCUT%"
echo REM Start Menu shortcut >> "%CREATE_SHORTCUT%"
echo Set oLink2 = oWS.CreateShortcut("%START_SHORTCUT%") >> "%CREATE_SHORTCUT%"
echo oLink2.TargetPath = "cmd.exe" >> "%CREATE_SHORTCUT%"
echo oLink2.Arguments = "/c ""%LAUNCHER%""" >> "%CREATE_SHORTCUT%"
echo oLink2.WorkingDirectory = "%HUB_PATH%" >> "%CREATE_SHORTCUT%"
echo oLink2.Description = "AJZ Strategies Hub" >> "%CREATE_SHORTCUT%"
echo oLink2.Save >> "%CREATE_SHORTCUT%"

cscript //nologo "%CREATE_SHORTCUT%"
del "%CREATE_SHORTCUT%"

echo.
echo  SUCCESS
echo  [OK] Desktop shortcut created : AJZ Hub
echo  [OK] Start Menu entry created : AJZ Hub
echo  [OK] Choice launcher created  : P_000_Hub_Startup.bat
echo  [OK] PowerShell script created: P_000_Hub_Startup.ps1
echo.
echo  To pin: Start - search AJZ Hub - right-click - Pin to Start
echo.
pause
