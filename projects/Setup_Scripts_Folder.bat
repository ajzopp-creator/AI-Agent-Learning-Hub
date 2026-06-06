@echo off
echo Creating C:\Users\Trader\Scripts\ ...
if not exist "C:\Users\Trader\Scripts\" mkdir "C:\Users\Trader\Scripts\"

echo Moving batch files...
move /Y "%~dp0OpenProjects.bat" "C:\Users\Trader\Scripts\"
move /Y "%~dp0OpenProjects_ISE.bat" "C:\Users\Trader\Scripts\"

echo.
echo Done! Both files are now in C:\Users\Trader\Scripts\
echo.
pause
