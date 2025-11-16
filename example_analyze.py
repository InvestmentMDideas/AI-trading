"""
Quick Example - Analyze a Symbol

This is a simple script to analyze any symbol using the indicator engine.
Perfect for testing and understanding how it works!
"""

import sys
import config_ai as config
from indicator_engine import IndicatorEngine
from ibkr_data_feed import IBKRDataFeed


def analyze_symbol(symbol: str):
    """
    Analyze a symbol and print results.
    
    Args:
        symbol: Stock symbol to analyze (e.g., 'SPY', 'AAPL', 'TSLA')
    """
    print(f"\n{'='*70}")
    print(f"ANALYZING: {symbol}")
    print(f"{'='*70}\n")
    
    # Connect to IBKR
    print(f"Connecting to IBKR at {config.IBKR_HOST}:{config.IBKR_PORT}...")
    feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 3)
    
    if not feed.connect():
        print("❌ Failed to connect to IBKR!")
        print("   Make sure TWS/IB Gateway is running")
        return
    
    print("✅ Connected!\n")
    
    # Fetch data
    print("Fetching market data...")
    try:
        all_data = feed.get_all_timeframes(symbol)
        
        if '1min' not in all_data or all_data['1min'].empty:
            print(f"❌ No data available for {symbol}")
            print("   Market might be closed or symbol invalid")
            feed.disconnect()
            return
        
        print(f"✅ Got {len(all_data['1min'])} bars\n")
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        feed.disconnect()
        return
    
    # Run indicator engine
    print("Running indicator analysis...")
    try:
        engine = IndicatorEngine(config)
        result = engine.analyze(
            df=all_data['1min'],
            symbol=symbol,
            mtf_data={k: v for k, v in all_data.items() if k != '1min'}
        )
        
        print("✅ Analysis complete!\n")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        feed.disconnect()
        return
    
    # Disconnect
    feed.disconnect()
    
    # Display results
    print_results(result)


def print_results(result: dict):
    """Pretty print analysis results."""
    
    print("┌" + "─"*68 + "┐")
    print("│" + f"  ANALYSIS RESULTS: {result['symbol']}".ljust(68) + "│")
    print("└" + "─"*68 + "┘")
    
    # Market Data
    print("\n📊 MARKET DATA:")
    print(f"   Price:    ${result['current_price']:.2f}")
    print(f"   VWAP:     ${result['vwap']:.2f}")
    print(f"   Distance: {result['distance_from_vwap_atr']:.2f} ATR")
    print(f"   ATR:      ${result['atr']:.2f}")
    print(f"   RVOL:     {result['rvol']:.2f}x")
    
    # Probability
    print("\n🎯 PROBABILITY ANALYSIS:")
    print(f"   Overall: {result['probability']:.1f}% {result['quality_emoji']} ({result['quality']})")
    print(f"\n   Component Breakdown:")
    
    components = {
        'vwap': ('VWAP Position', 20),
        'macd': ('MACD Alignment', 25),
        'ema': ('EMA Trend', 20),
        'volume': ('Volume Surge', 20),
        'extension': ('Price Extension', 15),
        'squeeze': ('Squeeze Status', 20),
        'momentum': ('Squeeze Momentum', 15),
        'confluence': ('Confluence Bonus', 10)
    }
    
    for key, (name, max_score) in components.items():
        score = result['scores'].get(key, 0)
        pct = (score / max_score * 100) if max_score > 0 else 0
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        print(f"   {name:18s} [{bar}] {score:5.1f}/{max_score}")
    
    print(f"\n   Total Raw Score: {result['total_raw_score']:.1f} / 145")
    
    # Indicators
    print("\n📈 INDICATORS:")
    print(f"   MACD Histogram: {result['macd_hist']:+.4f}")
    print(f"   EMA Fast/Slow:  ${result['ema_fast']:.2f} / ${result['ema_slow']:.2f}")
    print(f"   Squeeze:        {result['squeeze_status']}")
    print(f"   Vol Regime:     {result['vol_regime']['regime']} "
          f"(ATR {result['vol_regime']['atr_percentile']:.0f}%ile)")
    
    # Signals
    signals = result['trend_signals']
    print("\n🎬 SIGNALS:")
    print(f"   Bullish Trend:  {'✅' if signals['bullish_trend'] else '❌'}")
    print(f"   Bearish Trend:  {'✅' if signals['bearish_trend'] else '❌'}")
    print(f"   Long Entry:     {'🟢' if signals['long_entry'] else '⚪'}")
    print(f"   Short Entry:    {'🔴' if signals['short_entry'] else '⚪'}")
    print(f"   Premium Long:   {'⭐' if signals['premium_long'] else '⚪'}")
    print(f"   Premium Short:  {'⭐' if signals['premium_short'] else '⚪'}")
    
    # Entry/Exit Zones
    print("\n💰 VWAP ENTRY ZONES:")
    long_zone = result['vwap_zones']['long_zone']
    short_zone = result['vwap_zones']['short_zone']
    
    print(f"   LONG:  Entry ${long_zone['entry']:.2f} | "
          f"Stop ${long_zone['stop']:.2f} | "
          f"Target ${long_zone['target']:.2f}")
    print(f"   SHORT: Entry ${short_zone['entry']:.2f} | "
          f"Stop ${short_zone['stop']:.2f} | "
          f"Target ${short_zone['target']:.2f}")
    print(f"\n   Position Size: {result['position_size']} shares "
          f"(${result['position_size'] * result['current_price']:.2f} capital)")
    
    # MTF if available
    if result['mtf_metrics']:
        print("\n⏱️  MULTI-TIMEFRAME:")
        for tf in ['D', '4H', '15m', '5m']:
            if tf in result['mtf_metrics']:
                m = result['mtf_metrics'][tf]
                trend = "🟢" if m['macd_hist'] > 0 else "🔴"
                print(f"   {tf:4s}: {trend} MACD={m['macd_hist']:+.3f}, "
                      f"RSI={m['rsi']:.0f}, Chg={m['price_change']:+.2f}%")
    
    print("\n" + "─"*70 + "\n")


def main():
    """Main entry point."""
    # Get symbol from command line or prompt
    if len(sys.argv) > 1:
        symbol = sys.argv[1].upper()
    else:
        symbol = input("Enter symbol to analyze (default: SPY): ").strip().upper()
        if not symbol:
            symbol = "SPY"
    
    analyze_symbol(symbol)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
