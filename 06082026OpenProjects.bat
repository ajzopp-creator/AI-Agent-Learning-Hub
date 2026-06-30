:: OpenProjects.bat
:: Save to: C:\Users\Trader\AI-Agent-Learning-Hub\OpenProjects.bat
:: Picks an environment (CMD/PowerShell), then a project folder, then opens
:: that environment inside the selected project directory.

@echo off
setlocal EnableDelayedExpansion
cls

:: --- Configuration ---
set "PROJECTS_ROOT=C:\Users\Trader\AI-Agent-Learning-Hub\projects"
set "ENV_TYPE=NONE"
set "SELECTED_PROJECT="


:environment_menu
cls
echo ====================================================
echo       SELECT INITIAL ENVIRONMENT OR PROCEED
echo ====================================================
echo  [1] Open Command Prompt (CMD) in project directory
echo  [2] Open PowerShell in project directory
echo  [3] Skip environment - just open the project folder
echo  [4] Exit
echo ====================================================
echo.

set /p env_choice="Enter your choice (1-4): "

if "%env_choice%"=="1" (
    set "ENV_TYPE=CMD"
    goto project_menu
)
if "%env_choice%"=="2" (
    set "ENV_TYPE=PS"
    goto project_menu
)
if "%env_choice%"=="3" (
    set "ENV_TYPE=NONE"
    goto project_menu
)
if "%env_choice%"=="4" exit

echo Invalid choice, please try again.
pause
goto environment_menu


:project_menu
cls
echo ====================================================
echo               SELECT A PROJECT
echo ====================================================
echo  Root: %PROJECTS_ROOT%
echo ----------------------------------------------------

:: Verify the projects root exists before listing
if not exist "%PROJECTS_ROOT%\" (
    echo  ERROR: Projects folder not found:
    echo  %PROJECTS_ROOT%
    pause
    goto environment_menu
)

:: Build a numbered list of every subfolder under the root
set count=0
for /d %%D in ("%PROJECTS_ROOT%\*") do (
    set /a count+=1
    set "proj[!count!]=%%~fD"
    echo  [!count!] %%~nxD
)

if %count%==0 (
    echo  No project folders found under the root.
    pause
    goto environment_menu
)

echo ----------------------------------------------------
echo  [B] Back to environment menu
echo  [X] Exit
echo ====================================================
echo.

set /p proj_choice="Enter project number: "

if /i "%proj_choice%"=="B" goto environment_menu
if /i "%proj_choice%"=="X" exit

:: Reject anything that is not a valid list entry
if not defined proj[%proj_choice%] (
    echo Invalid choice, please try again.
    pause
    goto project_menu
)

set "SELECTED_PROJECT=!proj[%proj_choice%]!"
goto launch


:launch
:: /d sets the starting directory for the launched window
if "%ENV_TYPE%"=="CMD" (
    start "AJZ Project" /d "%SELECTED_PROJECT%" cmd.exe
)
if "%ENV_TYPE%"=="PS" (
    start "AJZ Project" /d "%SELECTED_PROJECT%" powershell.exe -NoExit
)
if "%ENV_TYPE%"=="NONE" (
    start "" explorer.exe "%SELECTED_PROJECT%"
)
goto main_menu


:main_menu
cls
echo ====================================================
echo                    MAIN MENU
echo ====================================================
echo  Active project: %SELECTED_PROJECT%
echo ----------------------------------------------------
:: Insert your existing menu options and logic here
echo  [A] Existing Option 1
echo  [B] Existing Option 2
echo  [X] Exit
echo ====================================================
echo.

set /p main_choice="Enter your choice: "

:: Add your existing choice handling logic below
if /i "%main_choice%"=="X" exit

echo Option selected: %main_choice%
pause
goto main_menu
