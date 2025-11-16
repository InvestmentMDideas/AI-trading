"""
Configuration for AI Trading Companion
"""

import sys
import os
from pathlib import Path

# ========================================
# TRY TO LOAD EXISTING CONFIG
# ========================================
config_loaded = False

# Try parent directory
parent_dir = Path(__file__).parent.parent
if (parent_dir / "config.py").exists():
    sys.path.insert(0, str(parent_dir))
    try:
        from config import *
        config_loaded = True
        print(f"[CONFIG] ✅ Loaded from: {parent_dir}")
    except:
        pass

# Try project subdirectory
if not config_loaded:
    project_dir = parent_dir / "project"
    if (project_dir / "config.py").exists():
        sys.path.insert(0, str(project_dir))
        try:
            from config import *
            config_loaded = True
            print(f"[CONFIG] ✅ Loaded from: {project_dir}")
        except:
            pass

# Use defaults if not found
if not config_loaded:
    print("[CONFIG] Using defaults (config.py not found)")
    IBKR_HOST = "127.0.0.1"
    IBKR_PORT = 7497
    POLYGON_API_KEY = ""
    ACCOUNT_SIZE = 10000
    RISK_PER_TRADE = 0.01

# ========================================
# INDICATOR PARAMETERS
# ========================================

# Basic
CONFIRM_ON_CLOSE = True
MIN_BARS_REQUIRED = 50
ATR_LENGTH = 14

# TTM Squeeze
BB_LENGTH = 20
BB_MULT = 2.0
KC_LENGTH = 20
KC_MULT = 1.5
USE_TRUE_RANGE = True
MOM_LENGTH = 12

# Probability (145 points)
PROB_VWAP_MAX = 20
PROB_MACD_MAX = 25
PROB_EMA_MAX = 20
PROB_VOLUME_MAX = 20
PROB_EXTENSION_MAX = 15
PROB_SQUEEZE_MAX = 20
PROB_MOMENTUM_MAX = 15
PROB_CONFLUENCE_MAX = 10

# MACD
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Volume
VOL_SURGE_MULTIPLIER = 1.5
MIN_RVOL = 0.9
RVOL_PERIOD = 20

# Thresholds
HIGH_PROB_THRESHOLD = 70
MED_PROB_THRESHOLD = 50
USE_VOL_REGIME = True
ATR_LOOKBACK = 100

# VWAP
VWAP_ENTRY_DISTANCE = 0.7
VWAP_STOP_DISTANCE = 0.75
VWAP_TARGET_MULTIPLE = 1.5
MAX_VWAP_DISTANCE = 3.0

# Pullback
SWING_LOOKBACK = 10
PULLBACK_ENTRY_LEVEL = 0.50
STOP_BEYOND_SWING = 0.3
MIN_EXTENSION = 2.0

# Risk
ACCOUNT_EQUITY = 15000
RISK_PERCENT = 1.0
USE_TRAILING_STOP = True
TRAIL_MULTIPLIER = 2.0

# MTF
SHOW_DAILY = True
SHOW_4H = True
SHOW_15M = True
SHOW_5M = True

# EMA
FAST_EMA = 9
SLOW_EMA = 21

# ========================================
# AI SETTINGS
# ========================================

AI_MODEL = "qwen2.5:7b"
AI_TIMEOUT = 15
AI_MAX_RETRIES = 2

# Three Scenarios
AGGRESSIVE_MIN_PROB = 45
AGGRESSIVE_RISK = 1.2
AGGRESSIVE_STOP_ATR = 2.5

MODERATE_MIN_PROB = 55
MODERATE_RISK = 1.0
MODERATE_STOP_ATR = 2.0

CONSERVATIVE_MIN_PROB = 70
CONSERVATIVE_RISK = 0.75
CONSERVATIVE_STOP_ATR = 1.5

# ========================================
# DASHBOARD
# ========================================

AI_DASHBOARD_PORT = 8052
AI_DASHBOARD_HOST = "127.0.0.1"
AI_UPDATE_INTERVAL = 3000
AI_ANALYSIS_INTERVAL = 5

# ========================================
# PAPER TRADING
# ========================================

PAPER_TRADE_ENABLED = True
PAPER_TRADE_SCENARIOS = 3
PAPER_EQUITY_PER_SCENARIO = 15000
PAPER_TRADE_LOG_DIR = "logs/ai_paper_trading"