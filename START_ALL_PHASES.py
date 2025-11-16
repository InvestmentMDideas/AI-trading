"""
AI Trading Companion - COMPLETE SYSTEM LAUNCHER
Ensures ALL 4 PHASES run together:
  ✅ Phase 1: Indicator Engine
  ✅ Phase 2: AI Analyst  
  ✅ Phase 3: Dashboard (Real-time UI)
  ✅ Phase 4: Paper Trading (3 scenarios)
"""

import sys
import os
import time
from pathlib import Path


def print_banner():
    """Print startup banner."""
    print("\n" + "="*70)
    print("🎯 AI TRADING COMPANION - COMPLETE SYSTEM")
    print("="*70)
    print("\n📦 ALL 4 PHASES:")
    print("  ✅ Phase 1: Indicator Engine (145-point scoring)")
    print("  ✅ Phase 2: AI Analyst (Multi-stage reasoning)")
    print("  ✅ Phase 3: Dashboard (Real-time UI)")
    print("  ✅ Phase 4: Paper Trading (3 scenarios, $45k)")
    print("\n" + "="*70 + "\n")


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        print(f"   Current: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check all required packages."""
    print("\n📦 Checking dependencies...")
    
    required = {
        'Core Data': ['pandas', 'numpy', 'ib_insync'],
        'AI Engine': ['ollama'],
        'Dashboard': ['dash', 'dash_bootstrap_components', 'plotly']
    }
    
    all_ok = True
    for category, packages in required.items():
        print(f"\n  {category}:")
        for package in packages:
            try:
                __import__(package)
                print(f"    ✅ {package}")
            except ImportError:
                print(f"    ❌ {package} - MISSING")
                all_ok = False
    
    if not all_ok:
        print("\n❌ Missing packages detected!")
        print("\n💡 Install with:")
        print("   pip install pandas numpy ib_insync ollama dash dash-bootstrap-components plotly")
        return False
    
    print("\n✅ All dependencies installed")
    return True


def check_files():
    """Check all required files exist."""
    print("\n📁 Checking system files...")
    
    required_files = {
        'Phase 1 (Indicator)': [
            'config_ai.py',
            'market_metrics.py', 
            'indicator_engine.py',
            'ibkr_data_feed.py'
        ],
        'Phase 2 (AI)': [
            'ai_analyst.py',
            'ai_cache.py',
            'prompt_templates.py'
        ],
        'Phase 3 (Dashboard)': [
            'level2_handler.py',
            'layout_components.py'
        ],
        'Phase 4 (Paper Trading)': [
            'paper_trading_engine.py',
            'trade_logger.py'
        ]
    }
    
    all_ok = True
    for phase, files in required_files.items():
        print(f"\n  {phase}:")
        for filename in files:
            if Path(filename).exists():
                print(f"    ✅ {filename}")
            else:
                print(f"    ❌ {filename} - MISSING")
                all_ok = False
    
    # Check for integrated dashboard
    print(f"\n  Integrated Dashboard:")
    if Path("dashboard_unified_INTEGRATED.py").exists():
        print(f"    ✅ dashboard_unified_INTEGRATED.py (ALL 4 PHASES)")
    else:
        print(f"    ❌ dashboard_unified_INTEGRATED.py - MISSING")
        all_ok = False
    
    if not all_ok:
        print("\n❌ Missing files! Make sure you downloaded ALL files.")
        return False
    
    print("\n✅ All required files present")
    return True


def check_ibkr_connection():
    """Check IBKR connection (optional)."""
    print("\n🔌 Checking IBKR connection...")
    print("   (TWS/IB Gateway should be running on port 7497)")
    
    try:
        import config_ai as config
        from ibkr_data_feed import IBKRDataFeed
        
        feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 3)
        
        if feed.connect(timeout=5):
            print(f"   ✅ Connected to IBKR at {config.IBKR_HOST}:{config.IBKR_PORT}")
            feed.disconnect()
            return True
        else:
            print(f"   ⚠️  Could not connect to IBKR")
            print(f"   💡 Start TWS/IB Gateway and try again")
            print(f"   💡 System will start anyway (some features may not work)")
            return False
            
    except Exception as e:
        print(f"   ⚠️  IBKR check failed: {e}")
        print(f"   💡 System will start anyway")
        return False


def check_ollama():
    """Check Ollama AI availability (optional)."""
    print("\n🤖 Checking Ollama AI...")
    print("   (qwen2.5:7b model required for AI reasoning)")
    
    try:
        import ollama
        
        # Try to list models
        response = ollama.list()
        models = []
        
        if hasattr(response, 'models'):
            for m in response.models:
                if hasattr(m, 'model'):
                    models.append(m.model)
                elif hasattr(m, 'name'):
                    models.append(m.name)
        
        if 'qwen2.5:7b' in models:
            print(f"   ✅ Ollama running with qwen2.5:7b")
            return True
        else:
            print(f"   ⚠️  qwen2.5:7b model not found")
            print(f"   💡 Run: ollama pull qwen2.5:7b")
            print(f"   💡 System will start anyway (AI features disabled)")
            return False
            
    except Exception as e:
        print(f"   ⚠️  Ollama not running: {e}")
        print(f"   💡 Start Ollama and run: ollama pull qwen2.5:7b")
        print(f"   💡 System will start anyway (AI features disabled)")
        return False


def prepare_logs():
    """Create log directories."""
    print("\n📊 Preparing logs...")
    
    log_dirs = [
        "logs",
        "logs/ai_paper_trading"
    ]
    
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {log_dir}/")
    
    print("\n✅ Log directories ready")
    return True


def main():
    """Main launcher."""
    print_banner()
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("System Files", check_files),
        ("IBKR Connection", check_ibkr_connection),
        ("Ollama AI", check_ollama),
        ("Log Directories", prepare_logs)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            result = check_func()
            results[name] = result
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("STARTUP CHECK SUMMARY")
    print("="*70)
    
    critical_checks = ["Python Version", "Dependencies", "System Files", "Log Directories"]
    optional_checks = ["IBKR Connection", "Ollama AI"]
    
    print("\n📋 Critical Checks:")
    critical_ok = True
    for check in critical_checks:
        status = "✅ PASS" if results.get(check, False) else "❌ FAIL"
        print(f"  {status}  {check}")
        if not results.get(check, False):
            critical_ok = False
    
    print("\n📋 Optional Checks:")
    for check in optional_checks:
        status = "✅ PASS" if results.get(check, False) else "⚠️  WARN"
        print(f"  {status}  {check}")
    
    # Decide if we can start
    if not critical_ok:
        print("\n❌ CRITICAL CHECKS FAILED!")
        print("\n💡 Fix the issues above and try again.")
        return False
    
    # Show what will run
    print("\n" + "="*70)
    print("SYSTEM READY TO START")
    print("="*70)
    
    print("\n✅ ALL 4 PHASES WILL RUN:")
    print("  📊 Phase 1: Indicator Engine")
    print("  🤖 Phase 2: AI Analyst" + (" (⚠️  Ollama not detected)" if not results.get("Ollama AI", False) else ""))
    print("  🖥️  Phase 3: Dashboard → http://localhost:8052")
    print("  💰 Phase 4: Paper Trading (3 scenarios, $45k)" + (" (⚠️  IBKR not connected)" if not results.get("IBKR Connection", False) else ""))
    
    if not results.get("IBKR Connection", False):
        print("\n⚠️  WARNING: IBKR not connected")
        print("   - Dashboard will start but won't get live data")
        print("   - Start TWS/IB Gateway for full functionality")
    
    if not results.get("Ollama AI", False):
        print("\n⚠️  WARNING: Ollama AI not available")
        print("   - Indicator engine will still work")
        print("   - AI reasoning will be disabled")
    
    # Launch
    print("\n" + "="*70)
    print("🚀 LAUNCHING COMPLETE SYSTEM...")
    print("="*70)
    
    # Import and start the integrated dashboard
    try:
        # First, try the integrated dashboard
        if Path("dashboard_unified_INTEGRATED.py").exists():
            print("\n[INFO] Using integrated dashboard (ALL 4 PHASES)...")
            import dashboard_unified_INTEGRATED as dashboard_module
        else:
            print("\n[INFO] Using standard dashboard...")
            import dashboard_unified as dashboard_module
        
        dashboard = dashboard_module.UnifiedDashboard(port=8052, enable_paper_trading=True)
        
        print("\n✨ Starting dashboard...")
        print("\n📍 Dashboard URL: http://localhost:8052")
        print("📊 Monitoring: Live data every 3 seconds")
        print("💰 Paper Trading: Active (3 scenarios)")
        print("\n⏹️  Press Ctrl+C to stop\n")
        
        dashboard.start()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down...")
        if 'dashboard' in locals():
            dashboard.stop()
        print("✅ Stopped cleanly")
        
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Launcher failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
