@echo off
echo.
echo ================================================================
echo AI ANALYST TESTS
echo ================================================================
echo.
echo This will test the AI reasoning engine:
echo   1. Ollama connection
echo   2. Prompt templates
echo   3. JSON parsing
echo   4. Cache system
echo   5. AI analyst (simple)
echo   6. Full AI analysis (6 stages)
echo.
echo Make sure Ollama is running with qwen2.5:7b model!
echo.
pause

python test_ai_analyst.py

echo.
pause
