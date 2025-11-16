@echo off
cls
echo.
echo ============================================================================
echo.
echo      ___    ___   ______              ___              
echo     / _ \  /   ^| /_  __/______ _____/ (_)__  ___ _    
echo    / __ \/ /^| ^|  / / / __/ _ `/ _  / / _ \/ _ `/    
echo   /_/ /_/_/ ^|_^| /_/ /_/  \_,_/\_,_/_/_//_/\_, /     
echo                                          /___/       
echo   ____                                  _          
echo  / ___|___  _ __ ___  _ __   __ _ _ __ (_) ___  _ __  
echo ^| ^|   / _ \^| '_ ` _ \^| '_ \ / _` ^| '_ \^| ^|/ _ \^| '_ \ 
echo ^| ^|__^| (_) ^| ^| ^| ^| ^| ^| ^|_) ^| (_^| ^| ^| ^| ^| ^| (_) ^| ^| ^| ^|
echo  \____\___/^|_^| ^|_^| ^|_^| .__/ \__,_^|_^| ^|_^|_^|\___/^|_^| ^|_^|
echo                       ^|_^|                            
echo.
echo ============================================================================
echo.
echo  AI TRADING COMPANION - UNIFIED SYSTEM LAUNCHER
echo.
echo  This will start:
echo    - Indicator Engine (145-point probability system)
echo    - AI Analyst (Multi-stage reasoning with qwen2.5:7b)
echo    - Level 2 Order Book Handler
echo    - Paper Trading Engine (3 scenarios, $45,000 total)
echo    - Unified Dashboard (http://localhost:8052)
echo.
echo  REQUIREMENTS:
echo    1. TWS/IB Gateway running on port 7497
echo    2. Ollama running with qwen2.5:7b model
echo    3. All Python dependencies installed
echo.
echo ============================================================================
echo.
echo Press any key to start, or Ctrl+C to cancel...
pause > nul

echo.
echo Starting AI Trading Companion...
echo.

python start_trading_companion.py

echo.
echo ============================================================================
echo Dashboard stopped.
echo ============================================================================
pause
