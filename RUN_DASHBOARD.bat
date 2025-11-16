@echo off
echo ================================================================
echo AI TRADING COMPANION - UNIFIED DASHBOARD
echo ================================================================
echo.
echo This will start the unified trading dashboard on port 8052
echo.
echo Requirements:
echo   1. TWS/IB Gateway running on port 7497
echo   2. Ollama running with qwen2.5:7b model
echo   3. All Python dependencies installed
echo.
echo Dashboard will open at: http://localhost:8052
echo.
echo Press any key to start...
pause > nul

echo.
echo Starting dashboard...
python dashboard_unified.py

pause
