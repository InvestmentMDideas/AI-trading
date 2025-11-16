"""
AI Trading Companion - Main Launcher
One-click startup for the complete system.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ required")
    sys.exit(1)

print("=" * 70)
print("🎯 AI TRADING COMPANION - STARTUP")
print("=" * 70)
print()

# Step 1: Check dependencies
print("📦 Step 1/6: Checking dependencies...")
missing = []

try:
    import pandas
    print("  ✅ pandas")
except ImportError:
    missing.append('pandas')
    print("  ❌ pandas")

try:
    import numpy
    print("  ✅ numpy")
except ImportError:
    missing.append('numpy')
    print("  ❌ numpy")

try:
    import ib_insync
    print("  ✅ ib_insync")
except ImportError:
    missing.append('ib_insync')
    print("  ❌ ib_insync")

try:
    import dash
    print("  ✅ dash")
except ImportError:
    missing.append('dash')
    print("  ❌ dash")

try:
    import ollama
    print("  ✅ ollama")
except ImportError:
    missing.append('ollama')
    print("  ❌ ollama")

if missing:
    print(f"\n❌ Missing packages: {', '.join(missing)}")
    print(f"Install with: pip install {' '.join(missing)}")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n✅ All dependencies installed!\n")

# Step 2: Check files
print("📁 Step 2/6: Checking system files...")
required_files = [
    'config_ai.py',
    'indicator_engine.py',
    'ai_analyst.py',
    'ibkr_data_feed.py',
    'level2_handler.py',
    'paper_trading_engine.py',
    'trade_logger.py',
    'dashboard_unified.py'
]

missing_files = []
for f in required_files:
    if Path(f).exists():
        print(f"  ✅ {f}")
    else:
        print(f"  ❌ {f}")
        missing_files.append(f)

if missing_files:
    print(f"\n❌ Missing files: {', '.join(missing_files)}")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n✅ All system files present!\n")

# Step 3: Load configuration
print("⚙️  Step 3/6: Loading configuration...")
try:
    import config_ai as config
    print(f"  ✅ IBKR Host: {config.IBKR_HOST}")
    print(f"  ✅ IBKR Port: {config.IBKR_PORT}")
    print(f"  ✅ AI Model: {config.AI_MODEL}")
    print(f"  ✅ Dashboard Port: {config.AI_DASHBOARD_PORT}")
    print(f"  ✅ Paper Trading: ${config.PAPER_EQUITY_PER_SCENARIO:,} per scenario")
except Exception as e:
    print(f"\n❌ Configuration error: {e}")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("\n✅ Configuration loaded!\n")

# Step 4: Check IBKR connection
print("🔌 Step 4/6: Checking IBKR connection...")
print("  (Make sure TWS/IB Gateway is running!)")

try:
    from ibkr_data_feed import IBKRDataFeed
    
    feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 99)  # Use unique client ID for test
    
    if feed.connect(timeout=5):
        print(f"  ✅ Connected to IBKR at {config.IBKR_HOST}:{config.IBKR_PORT}")
        feed.disconnect()
        ibkr_ok = True
    else:
        print(f"  ⚠️  Could not connect to IBKR")
        print(f"  💡 Make sure TWS/IB Gateway is running on port {config.IBKR_PORT}")
        ibkr_ok = False
        
except Exception as e:
    print(f"  ⚠️  IBKR connection error: {e}")
    ibkr_ok = False

if not ibkr_ok:
    print("\n⚠️  WARNING: IBKR not connected!")
    print("The dashboard will start but won't receive live data.")
    response = input("\nContinue anyway? (y/n): ").lower()
    if response != 'y':
        print("\nStartup cancelled. Start TWS/IB Gateway and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)
else:
    print("\n✅ IBKR connection verified!\n")

# Step 5: Check Ollama
print("🤖 Step 5/6: Checking Ollama AI...")

try:
    import ollama
    
    # Try to list models
    models_response = ollama.list()
    
    # Check for qwen2.5:7b
    available_models = []
    if hasattr(models_response, 'models'):
        for m in models_response.models:
            if hasattr(m, 'model'):
                available_models.append(m.model)
            elif hasattr(m, 'name'):
                available_models.append(m.name)
    
    if config.AI_MODEL in available_models:
        print(f"  ✅ Ollama is running")
        print(f"  ✅ Model '{config.AI_MODEL}' is available")
        ollama_ok = True
    else:
        print(f"  ⚠️  Ollama is running but model '{config.AI_MODEL}' not found")
        print(f"  💡 Run: ollama pull {config.AI_MODEL}")
        ollama_ok = False
        
except Exception as e:
    print(f"  ⚠️  Ollama not running: {e}")
    print(f"  💡 Start Ollama and run: ollama pull {config.AI_MODEL}")
    ollama_ok = False

if not ollama_ok:
    print("\n⚠️  WARNING: Ollama AI not ready!")
    print("The dashboard will start but AI analysis won't work.")
    response = input("\nContinue anyway? (y/n): ").lower()
    if response != 'y':
        print("\nStartup cancelled. Start Ollama and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)
else:
    print("\n✅ Ollama AI ready!\n")

# Step 6: Create logs directory
print("📊 Step 6/6: Preparing logs directory...")
log_dir = Path(config.PAPER_TRADE_LOG_DIR)
log_dir.mkdir(parents=True, exist_ok=True)
print(f"  ✅ Logs: {log_dir}")

print("\n" + "=" * 70)
print("🚀 STARTUP COMPLETE - LAUNCHING DASHBOARD")
print("=" * 70)
print()
print(f"📍 Dashboard URL: http://localhost:{config.AI_DASHBOARD_PORT}")
print(f"📊 Paper Trading: 3 scenarios with ${config.PAPER_EQUITY_PER_SCENARIO * 3:,} total capital")
print(f"📁 Trade Logs: {log_dir}")
print()
print("Press Ctrl+C to stop")
print("=" * 70)
print()

# Small delay for dramatic effect
time.sleep(2)

# Launch dashboard
try:
    from dashboard_unified import UnifiedDashboard
    
    dashboard = UnifiedDashboard(port=config.AI_DASHBOARD_PORT)
    dashboard.start()
    
except KeyboardInterrupt:
    print("\n\n🛑 Shutdown requested...")
    print("Stopping dashboard...")
    try:
        dashboard.stop()
    except:
        pass
    print("✅ Shutdown complete")
    
except Exception as e:
    print(f"\n❌ Dashboard error: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)
