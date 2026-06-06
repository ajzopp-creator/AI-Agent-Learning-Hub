@echo off 
cd /d "C:\Users\Trader\AI-Agent-Learning-Hub" 
echo. 
echo   ========================================== 
echo      AJZ Strategies - AI-Agent-Learning-Hub 
echo   ========================================== 
echo. 
echo   Open with: 
echo     1 - Command Prompt 
echo     2 - PowerShell 
echo. 
set /p CHOICE=  Enter 1 or 2:  
if "%CHOICE%"=="1" goto CMD 
if "%CHOICE%"=="2" goto PS 
echo Invalid choice. 
pause 
goto :eof 
 
:CMD 
echo. 
echo   Projects: 
dir /b /ad "C:\Users\Trader\AI-Agent-Learning-Hub\projects" 
echo. 
echo   Integrations: 
dir /b /ad "C:\Users\Trader\AI-Agent-Learning-Hub\integrations" 
echo. 
echo   Python: C:\Users\Trader\.conda\envs\p140\python.exe 
echo. 
cmd /k 
goto :eof 
 
:PS 
start powershell.exe -NoExit -ExecutionPolicy Bypass -File "C:\Users\Trader\AI-Agent-Learning-Hub\P_000_Hub_Startup.ps1" 
