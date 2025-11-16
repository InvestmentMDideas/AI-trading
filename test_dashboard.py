"""
Dashboard Component Tests
Quick validation of all dashboard components.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("DASHBOARD COMPONENT TESTS")
print("="*60)

# Test 1: Import all modules
print("\nTest 1: Module Imports")
print("-"*60)

try:
    from indicator_engine import IndicatorEngine
    print("  ✅ indicator_engine")
except Exception as e:
    print(f"  ❌ indicator_engine: {e}")

try:
    from ai_analyst import AIAnalyst
    print("  ✅ ai_analyst")
except Exception as e:
    print(f"  ❌ ai_analyst: {e}")

try:
    from ibkr_data_feed import IBKRDataFeed
    print("  ✅ ibkr_data_feed")
except Exception as e:
    print(f"  ❌ ibkr_data_feed: {e}")

try:
    from level2_handler import Level2Handler
    print("  ✅ level2_handler")
except Exception as e:
    print(f"  ❌ level2_handler: {e}")

try:
    from layout_components import *
    print("  ✅ layout_components")
except Exception as e:
    print(f"  ❌ layout_components: {e}")

try:
    from dashboard_unified import UnifiedDashboard
    print("  ✅ dashboard_unified")
except Exception as e:
    print(f"  ❌ dashboard_unified: {e}")

# Test 2: Check Dash dependencies
print("\nTest 2: Dash Dependencies")
print("-"*60)

try:
    import dash
    print(f"  ✅ dash {dash.__version__}")
except ImportError:
    print("  ❌ dash not installed")
    print("     Run: pip install dash")

try:
    import dash_bootstrap_components
    print(f"  ✅ dash_bootstrap_components")
except ImportError:
    print("  ❌ dash_bootstrap_components not installed")
    print("     Run: pip install dash-bootstrap-components")

try:
    import plotly
    print(f"  ✅ plotly {plotly.__version__}")
except ImportError:
    print("  ❌ plotly not installed")
    print("     Run: pip install plotly")

# Test 3: Layout Components
print("\nTest 3: Layout Components")
print("-"*60)

try:
    from layout_components import (
        create_header, create_metric_card, create_probability_bar,
        create_scenario_card, create_l2_table, create_status_indicator
    )
    
    # Test header
    header = create_header("AAPL", 150.25, 1.5)
    print("  ✅ create_header")
    
    # Test metric card
    card = create_metric_card("Test", "100%", "subtitle", "#27ae60")
    print("  ✅ create_metric_card")
    
    # Test probability bar
    prob_bar = create_probability_bar(75, "HIGH")
    print("  ✅ create_probability_bar")
    
    # Test scenario card
    scenario_data = {
        'action': 'ENTER_LONG',
        'confidence': 75,
        'reasoning': 'Test reasoning',
        'entry': 150.0,
        'stop': 148.0,
        'target': 154.0,
        'size': 100
    }
    scenario = create_scenario_card("moderate", scenario_data, True)
    print("  ✅ create_scenario_card")
    
    # Test L2 table
    bids = [{'price': 150.0, 'size': 100}, {'price': 149.99, 'size': 200}]
    asks = [{'price': 150.01, 'size': 150}, {'price': 150.02, 'size': 250}]
    l2_table = create_l2_table(bids, asks)
    print("  ✅ create_l2_table")
    
    # Test status indicator
    status = create_status_indicator('success', 'Test message')
    print("  ✅ create_status_indicator")
    
    print("\n  ✅ All layout components working!")
    
except Exception as e:
    print(f"  ❌ Layout components failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Dashboard Initialization (dry run)
print("\nTest 4: Dashboard Initialization (Dry Run)")
print("-"*60)

try:
    from dashboard_unified import UnifiedDashboard
    
    # Create dashboard instance (don't start)
    dashboard = UnifiedDashboard(port=8052)
    print("  ✅ Dashboard instance created")
    print(f"  ✅ Default symbol: {dashboard.current_symbol}")
    print(f"  ✅ Port: {dashboard.port}")
    print("  ✅ Layout built successfully")
    
except Exception as e:
    print(f"  ❌ Dashboard initialization failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)
print("""
To run the dashboard:
  1. Make sure TWS/IB Gateway is running on port 7497
  2. Make sure Ollama is running with qwen2.5:7b model
  3. Run: python dashboard_unified.py
  4. Open: http://localhost:8052

Or use the batch file:
  RUN_DASHBOARD.bat
""")

print("="*60)
