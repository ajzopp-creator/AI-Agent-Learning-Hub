@echo off
echo ========================================
echo LM Studio Transcription Setup
echo ========================================
echo.

cd C:\Users\Trader\AI-Agent-Learning-Hub

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing required packages...
python -m pip install --upgrade pip --break-system-packages
python -m pip install openai-whisper requests --break-system-packages

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open LM Studio
echo 2. Load your Llama model
echo 3. Start the server (Local Server tab)
echo 4. Run: python 03-Local-LLM\Audio-Transcription\scripts\transcribe_lmstudio.py your_audio.mp3
echo.
pause
