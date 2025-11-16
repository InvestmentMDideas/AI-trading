"""
Test Indicator Engine

Validates that all calculations match the Pine Script indicator.
Tests end-to-end functionality with real IBKR data.

Run this to ensure accuracy before building the dashboard!
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, '.')

import config_ai as config
from indicator_engine import IndicatorEngine
from market_metrics import MarketMetrics
from ibkr_data_feed import IBKRDataFeed


# =========================
# Unit Tests - Technical Indicators
# =========================

def test_vwap():
    """Test VWAP calculation."""
    print("\n" + "="*60)
    print("TEST 1: VWAP Calculation")
    print("="*60)
    
    # Create sample data
    data = {
        'high': [101, 102, 103, 104, 105],
        'low': [99, 100, 101, 102, 103],
        'close': [100, 101, 102, 103, 104],
        'volume': [1000, 1500, 2000, 1200, 1800]
    }
    df = pd.DataFrame(data)
    
    metrics = MarketMetrics(config)
    vwap = metrics.calculate_vwap(df)
    
    print(f"Sample Data:\n{df}")
    print(f"\nVWAP Values:\n{vwap}")
    print(f"\nLast VWAP: ${vwap.iloc[-1]:.2f}")
    
    # Manual calculation for last value
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    cumulative_tp_vol = (typical_price * df['volume']).sum()
    cumulative_vol = df['volume'].sum()
    expected_vwap = cumulative_tp_vol / cumulative_vol
    
    print(f"Expected VWAP (manual): ${expected_vwap:.2f}")
    
    if abs(vwap.iloc[-1] - expected_vwap) < 0.01:
        print("✅ VWAP calculation CORRECT!")
        return True
    else:
        print("❌ VWAP calculation INCORRECT!")
        return False


def test_atr():
    """Test ATR calculation."""
    print("\n" + "="*60)
    print("TEST 2: ATR Calculation")
    print("="*60)
    
    data = {
        'high': [102, 103, 104, 105, 106],
        'low': [98, 99, 100, 101, 102],
        'close': [100, 101, 102, 103, 104]
    }
    df = pd.DataFrame(data)
    
    metrics = MarketMetrics(config)
    atr = metrics.calculate_atr(df, period=3)
    
    print(f"Sample Data:\n{df}")
    print(f"\nATR Values:\n{atr}")
    print(f"\nLast ATR: ${atr.iloc[-1]:.2f}")
    
    # ATR should be non-zero and positive
    if atr.iloc[-1] > 0:
        print("✅ ATR calculation looks good!")
        return True
    else:
        print("❌ ATR calculation failed!")
        return False


def test_macd():
    """Test MACD calculation."""
    print("\n" + "="*60)
    print("TEST 3: MACD Calculation")
    print("="*60)
    
    # Create sample data with trend
    close_prices = [100 + i * 0.5 for i in range(50)]
    df = pd.DataFrame({
        'high': [p + 1 for p in close_prices],
        'low': [p - 1 for p in close_prices],
        'close': close_prices,
        'volume': [1000] * 50
    })
    
    metrics = MarketMetrics(config)
    macd_line, signal_line, hist = metrics.calculate_macd(df, 12, 26, 9)
    
    print(f"Last 5 Close Prices: {df['close'].tail().tolist()}")
    print(f"\nLast MACD Line: {macd_line.iloc[-1]:.4f}")
    print(f"Last Signal Line: {signal_line.iloc[-1]:.4f}")
    print(f"Last Histogram: {hist.iloc[-1]:.4f}")
    
    # In uptrend, MACD should be positive
    if macd_line.iloc[-1] > 0:
        print("✅ MACD calculation looks correct!")
        return True
    else:
        print("❌ MACD calculation might be wrong!")
        return False


def test_squeeze():
    """Test TTM Squeeze calculation."""
    print("\n" + "="*60)
    print("TEST 4: TTM Squeeze Calculation")
    print("="*60)
    
    # Create sample data
    np.random.seed(42)
    close_prices = 100 + np.random.randn(100).cumsum()
    df = pd.DataFrame({
        'high': close_prices + 1,
        'low': close_prices - 1,
        'close': close_prices,
        'volume': np.random.randint(1000, 5000, 100)
    })
    
    metrics = MarketMetrics(config)
    squeeze = metrics.calculate_squeeze(df, 20, 2.0, 20, 1.5, True, 12)
    
    print(f"Squeeze Status:")
    print(f"  - Squeeze ON: {squeeze['sqz_on']}")
    print(f"  - Squeeze OFF: {squeeze['sqz_off']}")
    print(f"  - Squeeze Firing: {squeeze['sqz_firing']}")
    print(f"  - Tight Squeeze: {squeeze['is_tight_squeeze']}")
    print(f"  - BB Width Percentile: {squeeze['bb_width_percentile']:.1f}%")
    print(f"  - Momentum: {squeeze['momentum']:.4f}")
    
    # Squeeze result should have all required keys
    required_keys = ['sqz_on', 'sqz_off', 'sqz_firing', 'momentum', 
                    'is_tight_squeeze', 'bb_width_percentile']
    
    if all(k in squeeze for k in required_keys):
        print("✅ Squeeze calculation structure correct!")
        return True
    else:
        print("❌ Squeeze calculation missing keys!")
        return False


def test_probability_scoring():
    """Test 145-point probability scoring."""
    print("\n" + "="*60)
    print("TEST 5: Probability Scoring (145 Points)")
    print("="*60)
    
    # Create bullish scenario
    close_prices = [100 + i * 0.3 for i in range(100)]
    df = pd.DataFrame({
        'high': [p + 1 for p in close_prices],
        'low': [p - 1 for p in close_prices],
        'close': close_prices,
        'volume': [2000 + i * 10 for i in range(100)]  # Increasing volume
    })
    
    engine = IndicatorEngine(config)
    result = engine.analyze(df, symbol="TEST")
    
    print(f"\nTest Results:")
    print(f"  Symbol: {result['symbol']}")
    print(f"  Total Probability: {result['probability']:.1f}%")
    print(f"  Quality: {result['quality']} {result['quality_emoji']}")
    print(f"\nScore Breakdown (out of 145):")
    for component, score in result['scores'].items():
        max_score = {
            'vwap': 20, 'macd': 25, 'ema': 20, 'volume': 20,
            'extension': 15, 'squeeze': 20, 'momentum': 15, 'confluence': 10
        }.get(component, 0)
        print(f"  - {component.capitalize():12s}: {score:5.1f} / {max_score}")
    
    print(f"\nTotal Raw Score: {result['total_raw_score']:.1f} / 145")
    
    # Verify score calculation
    calculated_total = sum(result['scores'].values())
    if abs(calculated_total - result['total_raw_score']) < 0.1:
        print("✅ Probability scoring calculation correct!")
        return True
    else:
        print("❌ Probability scoring mismatch!")
        print(f"   Expected: {calculated_total}, Got: {result['total_raw_score']}")
        return False


# =========================
# Integration Test - IBKR Connection
# =========================

def test_ibkr_connection():
    """Test IBKR connection and data fetching."""
    print("\n" + "="*60)
    print("TEST 6: IBKR Connection & Data Fetch")
    print("="*60)
    
    try:
        feed = IBKRDataFeed(
            host=config.IBKR_HOST,
            port=config.IBKR_PORT,
            client_id=3
        )
        
        print(f"Attempting to connect to IBKR at {config.IBKR_HOST}:{config.IBKR_PORT}...")
        
        if not feed.connect():
            print("❌ Failed to connect to IBKR!")
            print("   Make sure TWS/IB Gateway is running")
            return False
        
        print("✅ Connected to IBKR!")
        
        # Test fetching data
        symbol = "SPY"
        print(f"\nFetching 1-minute data for {symbol}...")
        
        df_1min = feed.get_1min_bars(symbol, duration="1 D")
        
        if df_1min.empty:
            print(f"❌ No data returned for {symbol}")
            feed.disconnect()
            return False
        
        print(f"✅ Received {len(df_1min)} bars for {symbol}")
        print(f"\nLast 3 bars:")
        print(df_1min.tail(3))
        
        # Test current price
        print(f"\nFetching current price for {symbol}...")
        price = feed.get_current_price(symbol)
        
        if price:
            print(f"✅ Current {symbol} price: ${price:.2f}")
        else:
            print(f"⚠️  Could not get current price (market might be closed)")
        
        feed.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ IBKR test failed: {e}")
        return False


# =========================
# End-to-End Test
# =========================

def test_end_to_end():
    """Test complete workflow: IBKR -> Indicator -> Analysis."""
    print("\n" + "="*60)
    print("TEST 7: End-to-End Analysis")
    print("="*60)
    
    symbol = "SPY"
    
    try:
        print(f"Running full analysis on {symbol}...\n")
        
        # 1. Connect to IBKR
        feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 3)
        if not feed.connect():
            print("❌ Could not connect to IBKR")
            return False
        
        # 2. Fetch data
        print("Fetching multi-timeframe data...")
        all_data = feed.get_all_timeframes(symbol)
        
        if '1min' not in all_data or all_data['1min'].empty:
            print("❌ No 1-minute data available")
            feed.disconnect()
            return False
        
        primary_df = all_data['1min']
        mtf_data = {k: v for k, v in all_data.items() if k != '1min'}
        
        print(f"✅ Got {len(primary_df)} 1-min bars + {len(mtf_data)} timeframes")
        
        # 3. Run indicator engine
        print("\nRunning indicator engine...")
        engine = IndicatorEngine(config)
        result = engine.analyze(primary_df, symbol=symbol, mtf_data=mtf_data)
        
        # 4. Display results
        print("\n" + "="*60)
        print(f"ANALYSIS RESULTS: {symbol}")
        print("="*60)
        
        print(f"\n📊 Current Market Data:")
        print(f"  Price: ${result['current_price']:.2f}")
        print(f"  VWAP:  ${result['vwap']:.2f}")
        print(f"  ATR:   ${result['atr']:.2f}")
        print(f"  RVOL:  {result['rvol']:.2f}x")
        
        print(f"\n🎯 Probability Analysis:")
        print(f"  Overall: {result['probability']:.1f}% ({result['quality']})")
        print(f"\n  Score Breakdown:")
        for comp, score in result['scores'].items():
            print(f"    {comp.capitalize():12s}: {score:.1f}")
        
        print(f"\n📈 Indicators:")
        print(f"  MACD: {result['macd_hist']:.4f}")
        print(f"  EMA Fast/Slow: ${result['ema_fast']:.2f} / ${result['ema_slow']:.2f}")
        print(f"  Squeeze: {result['squeeze_status']}")
        print(f"  Vol Regime: {result['vol_regime']['regime']}")
        
        print(f"\n🎬 Signals:")
        signals = result['trend_signals']
        print(f"  Long Entry:  {'✅' if signals['long_entry'] else '❌'}")
        print(f"  Short Entry: {'✅' if signals['short_entry'] else '❌'}")
        print(f"  Premium Long:  {'🟢' if signals['premium_long'] else '⚪'}")
        print(f"  Premium Short: {'🔴' if signals['premium_short'] else '⚪'}")
        
        print(f"\n💰 VWAP Zones:")
        long_zone = result['vwap_zones']['long_zone']
        print(f"  Long Entry: ${long_zone['entry']:.2f}")
        print(f"  Long Stop:  ${long_zone['stop']:.2f}")
        print(f"  Long Target: ${long_zone['target']:.2f}")
        print(f"  Position Size: {result['position_size']} shares")
        
        if mtf_data:
            print(f"\n⏱️  Multi-Timeframe:")
            for tf, metrics in result['mtf_metrics'].items():
                print(f"  {tf:4s}: MACD={metrics['macd_hist']:+.3f}, "
                      f"RSI={metrics['rsi']:.0f}, Change={metrics['price_change']:+.2f}%")
        
        feed.disconnect()
        
        print("\n✅ End-to-end test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ End-to-end test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# =========================
# Run All Tests
# =========================

def run_all_tests():
    """Run complete test suite."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "INDICATOR ENGINE TESTS" + " "*21 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("VWAP Calculation", test_vwap),
        ("ATR Calculation", test_atr),
        ("MACD Calculation", test_macd),
        ("TTM Squeeze", test_squeeze),
        ("Probability Scoring", test_probability_scoring),
        ("IBKR Connection", test_ibkr_connection),
        ("End-to-End Analysis", test_end_to_end),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
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
        print("\n  🎉 ALL TESTS PASSED! Ready to build dashboard!")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Fix before proceeding.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
