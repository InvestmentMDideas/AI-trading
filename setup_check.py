"""
Quick Setup Script for AI Trading Companion
Run this first to verify everything is configured correctly.
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ Python version OK")
    return True

def check_dependencies():
    """Check required packages."""
    print("\nChecking dependencies...")
    
    required = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'ib_insync': 'ib_insync'
    }
    
    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All dependencies installed")
    return True

def check_config():
    """Check configuration."""
    print("\nChecking configuration...")
    
    try:
        import config_ai as config
        
        print(f"  IBKR Host: {config.IBKR_HOST}")
        print(f"  IBKR Port: {config.IBKR_PORT}")
        
        if hasattr(config, 'POLYGON_API_KEY'):
            if config.POLYGON_API_KEY:
                print(f"  Polygon API: ✅ Configured")
            else:
                print(f"  Polygon API: ⚠️  Not configured (optional)")
        
        print("\n✅ Configuration loaded")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def check_ibkr_connection():
    """Check IBKR connection."""
    print("\nChecking IBKR connection...")
    print("  (Make sure TWS/IB Gateway is running!)")
    
    try:
        import config_ai as config
        from ibkr_data_feed import IBKRDataFeed
        
        feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 3)
        
        if feed.connect(timeout=5):
            print(f"  ✅ Connected to IBKR at {config.IBKR_HOST}:{config.IBKR_PORT}")
            feed.disconnect()
            return True
        else:
            print(f"  ❌ Could not connect to IBKR")
            print(f"  💡 Make sure TWS/IB Gateway is running on port {config.IBKR_PORT}")
            return False
            
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        print(f"  💡 Make sure TWS/IB Gateway is running")
        return False

def check_project_structure():
    """Check if files are in the right place."""
    print("\nChecking project structure...")
    
    required_files = [
        'config_ai.py',
        'market_metrics.py',
        'indicator_engine.py',
        'ibkr_data_feed.py',
        'test_indicator.py'
    ]
    
    all_present = True
    for filename in required_files:
        if Path(filename).exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} - MISSING")
            all_present = False
    
    if not all_present:
        print("\n❌ Missing files. Make sure all files are in the same directory.")
        return False
    
    print("\n✅ All required files present")
    return True

def main():
    """Run all checks."""
    print("="*70)
    print("AI TRADING COMPANION - SETUP VERIFICATION")
    print("="*70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Project Structure", check_project_structure),
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("IBKR Connection", check_ibkr_connection)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("SETUP VERIFICATION SUMMARY")
    print("="*70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 SETUP COMPLETE! Ready to run tests.")
        print("\nNext step: python test_indicator.py")
    elif passed >= total - 1 and not results[-1][1]:
        print("\n⚠️  Setup mostly complete!")
        print("IBKR connection failed - make sure TWS/IB Gateway is running.")
        print("\nYou can still run unit tests: python test_indicator.py")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")
        print("\n💡 COMMON FIXES:")
        print("  - Missing packages: pip install pandas numpy ib_insync")
        print("  - Wrong directory: Make sure you're in ai_trading_companion folder")
        print("  - IBKR not running: Start TWS or IB Gateway on port 7497")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
