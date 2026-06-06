@echo off
echo Testing LM Studio Connection...
echo.

cd C:\Users\Trader\AI-Agent-Learning-Hub
call venv\Scripts\activate.bat

python -c "import requests; r = requests.get('http://localhost:1234/v1/models', timeout=2); print('? LM Studio is running!' if r.status_code == 200 else '? LM Studio not responding')"

echo.
pause
