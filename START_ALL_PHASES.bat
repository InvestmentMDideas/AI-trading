@echo off
echo.
echo ================================================================
echo AI TRADING COMPANION - COMPLETE SYSTEM
echo ================================================================
echo.
echo This will start ALL 4 PHASES:
echo   Phase 1: Indicator Engine (145-point scoring)
echo   Phase 2: AI Analyst (Multi-stage reasoning)
echo   Phase 3: Dashboard (Real-time UI)
echo   Phase 4: Paper Trading (3 scenarios, $45k total)
echo.
echo ================================================================
echo.
echo Requirements:
echo   1. TWS/IB Gateway running on port 7497 (optional but recommended)
echo   2. Ollama running with qwen2.5:7b model (optional but recommended)
echo   3. All Python dependencies installed
echo.
echo Dashboard will open at: http://localhost:8052
echo.
echo Press any key to start...
pause > nul

echo.
echo Starting complete system...
python START_ALL_PHASES.py

pause
