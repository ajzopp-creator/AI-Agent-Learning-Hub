@echo off
REM Quick Transcription Wrapper for Llama 4 Scout
REM Usage: transcribe.bat <audio_file> [analysis_type] [whisper_model]

cd /d C:\Users\Trader\AI-Agent-Learning-Hub\03-Local-LLM\Audio-Transcription\scripts
call ..\..\..\venv\Scripts\activate.bat

python transcribe_lmstudio.py %*

pause
