@echo off
REM Examples of using LM Studio Transcription with Llama 4 Scout

echo ========================================
echo LM Studio Transcription Examples
echo Model: Llama 4 Scout 17B
echo ========================================
echo.

echo EXAMPLE 1: Quick Summary
echo transcribe.bat "podcast.mp3"
echo.

echo EXAMPLE 2: Trading Ideas (BEST FOR TRADING)
echo transcribe.bat "webinar.mp3" trade_ideas small
echo.

echo EXAMPLE 3: Risk Analysis
echo transcribe.bat "risk_lesson.mp3" risk_analysis base
echo.

echo EXAMPLE 4: Study Questions
echo transcribe.bat "tutorial.mp3" questions base
echo.

echo EXAMPLE 5: Key Points
echo transcribe.bat "morning_brief.mp3" key_points base
echo.

echo EXAMPLE 6: Setup Identification
echo transcribe.bat "setup_tutorial.mp3" setup_identification small
echo.

echo ========================================
echo Available Analysis Types:
echo ========================================
echo - summary           (quick overview)
echo - key_points        (main ideas)
echo - trade_ideas       (trading strategies) *** RECOMMENDED ***
echo - risk_analysis     (risk management)
echo - questions         (study questions)
echo - setup_identification (trading setups)
echo.

echo ========================================
echo Whisper Models:
echo ========================================
echo - tiny    (fastest, basic)
echo - base    (balanced - DEFAULT)
echo - small   (better quality)
echo - medium  (high quality)
echo - large   (best quality)
echo.

pause
