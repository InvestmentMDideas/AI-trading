"""
Test Paper Trading Engine
Validate all 3 scenarios with simulated data.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from paper_trading_engine import PaperTradingEngine
import json


def test_basic_trade():
    """Test 1: Basic trade entry and exit."""
    print("\n" + "="*60)
    print("TEST 1: Basic Trade Entry & Exit")
    print("="*60)
    
    engine = PaperTradingEngine()
    
    # Simulate indicator data
    indicator_data = {
        'symbol': 'AAPL',
        'probability': 68,
        'quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': {'regime': 'NORMAL'},
        'current_price': 150.30
    }
    
    # Simulate AI analysis
    ai_result = {
        'scenarios': {
            'aggressive': {
                'action': 'ENTER_LONG',
                'entry': 150.30,
                'stop': 149.00,
                'target': 152.00,
                'size': 120,
                'confidence': 65,
                'reasoning': 'Squeeze firing, moderate probability'
            },
            'moderate': {
                'action': 'ENTER_AT_ZONE',
                'entry': 150.00,
                'stop': 148.50,
                'target': 152.00,
                'size': 100,
                'confidence': 72,
                'reasoning': 'Wait for VWAP zone entry'
            },
            'conservative': {
                'action': 'WAIT',
                'confidence': 0,
                'reasoning': 'Probability below 70% threshold'
            }
        }
    }
    
    # Process initial signal
    print("\n📊 Processing AI Signal...")
    engine.process_ai_analysis(ai_result, indicator_data, 150.30, 150.50, 150.10)
    
    # Show stats after entry
    stats = engine.get_all_stats()
    print("\n📈 Stats After Entry:")
    print(json.dumps(stats, indent=2))
    
    # Simulate price movement to target
    print("\n📊 Simulating price move to target...")
    time.sleep(1)
    engine.process_ai_analysis(
        {'scenarios': {}},  # No new signals
        indicator_data,
        current_price=151.80,
        current_high=152.10,
        current_low=151.50
    )
    
    # Show final stats
    stats = engine.get_all_stats()
    print("\n📈 Final Stats:")
    print(json.dumps(stats, indent=2))
    
    # Check results
    aggressive = stats['aggressive']
    if aggressive['total_trades'] > 0 and aggressive['wins'] > 0:
        print("\n✅ Test 1 PASSED: Trade executed and exited at target")
        return True
    else:
        print("\n❌ Test 1 FAILED")
        return False


def test_stop_loss():
    """Test 2: Stop loss hit."""
    print("\n" + "="*60)
    print("TEST 2: Stop Loss Execution")
    print("="*60)
    
    engine = PaperTradingEngine()
    
    indicator_data = {
        'symbol': 'TSLA',
        'probability': 72,
        'quality': 'HIGH',
        'squeeze_status': 'FIRING',
        'vol_regime': {'regime': 'NORMAL'}
    }
    
    ai_result = {
        'scenarios': {
            'aggressive': {
                'action': 'ENTER_LONG',
                'entry': 245.00,
                'stop': 243.00,
                'target': 250.00,
                'size': 60,
                'confidence': 70,
                'reasoning': 'High probability setup'
            },
            'moderate': {
                'action': 'WAIT',
                'reasoning': 'Waiting for zone'
            },
            'conservative': {
                'action': 'WAIT',
                'reasoning': 'Waiting for pullback'
            }
        }
    }
    
    # Entry
    print("\n📊 Entering position...")
    engine.process_ai_analysis(ai_result, indicator_data, 245.00, 245.50, 244.80)
    
    # Price moves against us - hit stop
    print("\n📉 Price dropping to stop loss...")
    time.sleep(1)
    engine.process_ai_analysis(
        {'scenarios': {}},
        indicator_data,
        current_price=242.50,
        current_high=244.00,
        current_low=242.50
    )
    
    stats = engine.get_all_stats()
    aggressive = stats['aggressive']
    
    print(f"\n📈 Aggressive Stats:")
    print(f"  Trades: {aggressive['total_trades']}")
    print(f"  Losses: {aggressive['losses']}")
    print(f"  P&L: ${aggressive['pnl']:.2f}")
    
    if aggressive['losses'] > 0 and aggressive['pnl'] < 0:
        print("\n✅ Test 2 PASSED: Stop loss executed correctly")
        return True
    else:
        print("\n❌ Test 2 FAILED")
        return False


def test_moderate_zone_entry():
    """Test 3: Moderate scenario zone entry."""
    print("\n" + "="*60)
    print("TEST 3: Moderate Zone Entry")
    print("="*60)
    
    engine = PaperTradingEngine()
    
    indicator_data = {
        'symbol': 'SPY',
        'probability': 65,
        'quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': {'regime': 'NORMAL'}
    }
    
    ai_result = {
        'scenarios': {
            'aggressive': {
                'action': 'WAIT',
                'reasoning': 'Below 55% threshold'
            },
            'moderate': {
                'action': 'ENTER_AT_ZONE',
                'entry': 450.00,
                'stop': 448.00,
                'target': 453.00,
                'size': 30,
                'confidence': 68,
                'reasoning': 'Waiting for VWAP zone @ $450.00'
            },
            'conservative': {
                'action': 'WAIT',
                'reasoning': 'Below 70% threshold'
            }
        }
    }
    
    # Initial signal - price not at zone yet
    print("\n📊 Initial signal - price @ $451.00 (not at zone)...")
    engine.process_ai_analysis(ai_result, indicator_data, 451.00, 451.50, 450.80)
    
    stats = engine.get_all_stats()
    if stats['moderate']['in_position']:
        print("❌ Moderate entered too early!")
        return False
    
    print("✅ Moderate waiting for zone")
    
    # Price pulls back to zone
    print("\n📊 Price pulled back to zone @ $450.00...")
    time.sleep(1)
    engine.process_ai_analysis(ai_result, indicator_data, 450.00, 450.20, 449.90)
    
    stats = engine.get_all_stats()
    moderate = stats['moderate']
    
    print(f"\n📈 Moderate Stats:")
    print(f"  In Position: {moderate['in_position']}")
    print(f"  Trades: {moderate['total_trades']}")
    
    if moderate['total_trades'] > 0:
        print("\n✅ Test 3 PASSED: Moderate entered at zone correctly")
        return True
    else:
        print("\n❌ Test 3 FAILED")
        return False


def test_conservative_strict():
    """Test 4: Conservative only takes 70%+ probability."""
    print("\n" + "="*60)
    print("TEST 4: Conservative Strict Thresholds")
    print("="*60)
    
    engine = PaperTradingEngine()
    
    # LOW probability setup
    indicator_data_low = {
        'symbol': 'NVDA',
        'probability': 55,
        'quality': 'MEDIUM',
        'squeeze_status': 'MODERATE',
        'vol_regime': {'regime': 'NORMAL'}
    }
    
    ai_result_low = {
        'scenarios': {
            'aggressive': {
                'action': 'ENTER_LONG',
                'entry': 500.00,
                'stop': 495.00,
                'target': 510.00,
                'size': 30,
                'confidence': 60,
                'reasoning': 'Moderate setup'
            },
            'moderate': {
                'action': 'ENTER_LONG',
                'entry': 500.00,
                'stop': 495.00,
                'target': 510.00,
                'size': 30,
                'confidence': 60,
                'reasoning': 'Acceptable for moderate'
            },
            'conservative': {
                'action': 'ENTER_LONG',
                'entry': 500.00,
                'stop': 495.00,
                'target': 510.00,
                'size': 20,
                'confidence': 60,
                'reasoning': 'Medium quality'
            }
        }
    }
    
    print("\n📊 55% probability setup...")
    engine.process_ai_analysis(ai_result_low, indicator_data_low, 500.00, 500.50, 499.50)
    
    stats = engine.get_all_stats()
    
    print(f"\nTrades executed:")
    print(f"  Aggressive: {stats['aggressive']['total_trades']}")
    print(f"  Moderate: {stats['moderate']['total_trades']}")
    print(f"  Conservative: {stats['conservative']['total_trades']}")
    
    if stats['conservative']['total_trades'] == 0:
        print("\n✅ Test 4 PASSED: Conservative rejected 55% setup")
        return True
    else:
        print("\n❌ Test 4 FAILED: Conservative should reject <70% probability")
        return False


def test_performance_logging():
    """Test 5: Performance logging."""
    print("\n" + "="*60)
    print("TEST 5: Performance Logging")
    print("="*60)
    
    engine = PaperTradingEngine()
    
    # Execute a few trades
    for i in range(3):
        indicator_data = {
            'symbol': 'AAPL',
            'probability': 65 + i * 5,
            'quality': 'MEDIUM',
            'squeeze_status': 'FIRING',
            'vol_regime': {'regime': 'NORMAL'}
        }
        
        ai_result = {
            'scenarios': {
                'aggressive': {
                    'action': 'ENTER_LONG',
                    'entry': 150.00 + i,
                    'stop': 149.00 + i,
                    'target': 152.00 + i,
                    'size': 100,
                    'confidence': 65,
                    'reasoning': f'Trade {i+1}'
                },
                'moderate': {
                    'action': 'WAIT',
                    'reasoning': 'Waiting'
                },
                'conservative': {
                    'action': 'WAIT',
                    'reasoning': 'Waiting'
                }
            }
        }
        
        # Entry
        engine.process_ai_analysis(ai_result, indicator_data, 150.00 + i, 150.50 + i, 149.80 + i)
        time.sleep(0.5)
        
        # Exit at target
        engine.process_ai_analysis(
            {'scenarios': {}},
            indicator_data,
            152.00 + i,
            152.50 + i,
            151.50 + i
        )
        time.sleep(0.5)
    
    # Export performance report
    print("\n📊 Exporting performance report...")
    report = engine.export_performance_report()
    
    print(f"\n📈 Performance Report:")
    print(json.dumps(report, indent=2))
    
    # Check if report was created
    from pathlib import Path
    report_file = Path(f"logs/ai_paper_trading/performance_{report['date']}.json")
    
    if report_file.exists():
        print(f"\n✅ Test 5 PASSED: Performance report created at {report_file}")
        return True
    else:
        print("\n❌ Test 5 FAILED: Performance report not created")
        return False


def run_all_tests():
    """Run complete test suite."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "PAPER TRADING ENGINE TESTS" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Basic Trade Entry & Exit", test_basic_trade),
        ("Stop Loss Execution", test_stop_loss),
        ("Moderate Zone Entry", test_moderate_zone_entry),
        ("Conservative Strict Thresholds", test_conservative_strict),
        ("Performance Logging", test_performance_logging)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            time.sleep(1)
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*20 + "TEST SUMMARY" + " "*26 + "║")
    print("╚" + "="*58 + "╝")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED!")
        print("\n  Paper trading engine is ready!")
        print("\n  Next: Integrate with dashboard using DASHBOARD_INTEGRATION_INSTRUCTIONS.txt")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
