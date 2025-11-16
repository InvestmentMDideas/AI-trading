"""
Complete Example: Indicator + AI Analysis

Shows full workflow from data fetching to AI decision.
"""

import sys
import config_ai as config
from indicator_engine import IndicatorEngine
from ibkr_data_feed import IBKRDataFeed
from ai_analyst import analyze_with_ai


def analyze_symbol_complete(symbol: str):
    """
    Complete analysis workflow:
    1. Connect to IBKR
    2. Fetch multi-timeframe data
    3. Run indicator engine (145-point scoring)
    4. Run AI analyst (6-stage reasoning + 3 scenarios)
    5. Display comprehensive results
    
    Args:
        symbol: Stock symbol to analyze
    """
    print(f"\n{'='*70}")
    print(f"COMPLETE ANALYSIS: {symbol}")
    print(f"{'='*70}\n")
    
    # =========================
    # Step 1: Connect to IBKR
    # =========================
    print("[STEP 1] Connecting to IBKR...")
    feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 3)
    
    if not feed.connect():
        print("❌ Failed to connect to IBKR!")
        return
    
    print("✅ Connected!\n")
    
    # =========================
    # Step 2: Fetch Data
    # =========================
    print("[STEP 2] Fetching multi-timeframe data...")
    try:
        all_data = feed.get_all_timeframes(symbol)
        
        if '1min' not in all_data or all_data['1min'].empty:
            print(f"❌ No data available for {symbol}")
            feed.disconnect()
            return
        
        primary_df = all_data['1min']
        mtf_data = {k: v for k, v in all_data.items() if k != '1min'}
        
        print(f"✅ Got {len(primary_df)} 1-min bars + {len(mtf_data)} timeframes\n")
        
    except Exception as e:
        print(f"❌ Data fetch failed: {e}")
        feed.disconnect()
        return
    
    # =========================
    # Step 3: Indicator Analysis
    # =========================
    print("[STEP 3] Running indicator engine (145-point scoring)...")
    try:
        engine = IndicatorEngine(config)
        indicator_result = engine.analyze(primary_df, symbol=symbol, mtf_data=mtf_data)
        
        print("✅ Indicator analysis complete!\n")
        
        # Quick indicator summary
        print(f"  📊 Indicator Results:")
        print(f"    Probability: {indicator_result['probability']:.1f}% "
              f"({indicator_result['quality']})")
        print(f"    Squeeze: {indicator_result['squeeze_status']}")
        print(f"    Vol Regime: {indicator_result['vol_regime']['regime']}")
        print(f"    Signals: Long={indicator_result['trend_signals']['long_entry']}, "
              f"Short={indicator_result['trend_signals']['short_entry']}")
        print()
        
    except Exception as e:
        print(f"❌ Indicator analysis failed: {e}")
        feed.disconnect()
        return
    
    # =========================
    # Step 4: AI Analysis
    # =========================
    print("[STEP 4] Running AI analyst (6 stages + 3 scenarios)...")
    print("  This will take ~5-10 seconds...\n")
    
    try:
        ai_result = analyze_with_ai(indicator_result, symbol=symbol, use_cache=True)
        
        print("✅ AI analysis complete!\n")
        
    except Exception as e:
        print(f"❌ AI analysis failed: {e}")
        import traceback
        traceback.print_exc()
        feed.disconnect()
        return
    
    # Disconnect IBKR
    feed.disconnect()
    
    # =========================
    # Step 5: Display Results
    # =========================
    print_comprehensive_results(symbol, indicator_result, ai_result)


def print_comprehensive_results(symbol: str, indicator_result: dict, ai_result: dict):
    """Pretty print comprehensive analysis results."""
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + f"  COMPLETE ANALYSIS: {symbol}".ljust(68) + "║")
    print("╚" + "="*68 + "╝")
    
    # =========================
    # Market Data
    # =========================
    print("\n📊 MARKET DATA:")
    print(f"  Price:    ${indicator_result['current_price']:.2f}")
    print(f"  VWAP:     ${indicator_result['vwap']:.2f}")
    print(f"  Distance: {indicator_result['distance_from_vwap_atr']:.2f} ATR")
    print(f"  ATR:      ${indicator_result['atr']:.2f}")
    print(f"  RVOL:     {indicator_result['rvol']:.2f}x")
    
    # =========================
    # Indicator Analysis
    # =========================
    print("\n🎯 INDICATOR ANALYSIS (145-Point System):")
    print(f"  Overall: {indicator_result['probability']:.1f}% "
          f"{indicator_result['quality_emoji']} ({indicator_result['quality']})")
    
    print(f"\n  Component Breakdown:")
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
        score = indicator_result['scores'].get(key, 0)
        pct = (score / max_score * 100) if max_score > 0 else 0
        bar = '█' * int(pct / 5) + '░' * (20 - int(pct / 5))
        print(f"    {name:18s} [{bar}] {score:5.1f}/{max_score}")
    
    print(f"\n  Squeeze: {indicator_result['squeeze_status']}")
    print(f"  Vol Regime: {indicator_result['vol_regime']['regime']} "
          f"(ATR {indicator_result['vol_regime']['atr_percentile']:.0f}%ile)")
    
    # =========================
    # AI Analysis
    # =========================
    print("\n🤖 AI ANALYSIS (6-Stage Reasoning):")
    
    # Stage scores
    print(f"\n  Stage Scores:")
    print(f"    Market Context:     {ai_result['context']['score']}/100")
    print(f"    Technical Analysis: {ai_result['technical']['score']}/100")
    print(f"    Risk Assessment:    {ai_result['risk']['score']}/100")
    
    # Context
    print(f"\n  Context Assessment:")
    print(f"    {ai_result['context']['assessment']}")
    print(f"    Favorable: {'✅' if ai_result['context']['favorable'] else '❌'}")
    
    # Technical
    print(f"\n  Technical Assessment:")
    print(f"    {ai_result['technical']['assessment']}")
    if ai_result['technical']['strengths']:
        print(f"    Strengths: {', '.join(ai_result['technical']['strengths'])}")
    if ai_result['technical']['weaknesses']:
        print(f"    Weaknesses: {', '.join(ai_result['technical']['weaknesses'])}")
    
    # Risk
    print(f"\n  Risk Assessment:")
    print(f"    Entry Quality: {ai_result['risk']['entry_quality']}")
    print(f"    Stop Quality:  {ai_result['risk']['stop_quality']}")
    print(f"    R:R Ratio:     {ai_result['risk']['r_r_ratio']:.1f}")
    
    # =========================
    # Three Scenarios
    # =========================
    print("\n🎬 THREE SCENARIOS:")
    
    scenarios_display = {
        'aggressive': ('AGGRESSIVE', '🔴'),
        'moderate': ('MODERATE', '🟡'),
        'conservative': ('CONSERVATIVE', '🟢')
    }
    
    for key, (name, emoji) in scenarios_display.items():
        scenario = ai_result['scenarios'][key]
        print(f"\n  {emoji} {name}:")
        print(f"    Action:     {scenario['action']}")
        if scenario.get('entry'):
            print(f"    Entry:      ${scenario['entry']:.2f}")
            print(f"    Stop:       ${scenario['stop']:.2f}")
            print(f"    Target:     ${scenario['target']:.2f}")
            print(f"    Size:       {scenario.get('size', 0)} shares")
        print(f"    Confidence: {scenario['confidence']}%")
        print(f"    Reasoning:  {scenario['reasoning']}")
    
    # =========================
    # Final Verdict
    # =========================
    print("\n🎯 FINAL VERDICT:")
    verdict_emoji = "🟢" if ai_result['overall_verdict'] == 'TRADE' else "🟡" if ai_result['overall_verdict'] == 'WAIT' else "🔴"
    print(f"  {verdict_emoji} {ai_result['overall_verdict']}")
    print(f"\n  Recommended Strategy: {ai_result['recommended_scenario'].upper()}")
    print(f"  Confidence: {ai_result['recommended_confidence']}%")
    print(f"  Reason: {ai_result['recommendation']['reason']}")
    
    # Conflicts
    if ai_result['conflicts']['conflicts']:
        print(f"\n  ⚠️  CONFLICTS DETECTED:")
        for conflict in ai_result['conflicts']['conflicts']:
            print(f"    - {conflict}")
        print(f"  Severity: {ai_result['conflicts']['severity']}")
    
    # =========================
    # Entry/Exit Levels
    # =========================
    recommended = ai_result['recommended_scenario']
    scenario_data = ai_result['scenarios'][recommended]
    
    if scenario_data.get('entry'):
        print(f"\n💰 RECOMMENDED TRADE LEVELS ({recommended.upper()}):")
        print(f"  Entry:  ${scenario_data['entry']:.2f}")
        print(f"  Stop:   ${scenario_data['stop']:.2f}")
        print(f"  Target: ${scenario_data['target']:.2f}")
        print(f"  Size:   {scenario_data.get('size', 0)} shares")
        
        risk = abs(scenario_data['entry'] - scenario_data['stop']) * scenario_data.get('size', 0)
        reward = abs(scenario_data['target'] - scenario_data['entry']) * scenario_data.get('size', 0)
        print(f"  Risk:   ${risk:.2f}")
        print(f"  Reward: ${reward:.2f}")
        print(f"  R:R:    {reward/risk:.2f}" if risk > 0 else "  R:R:    N/A")
    
    # =========================
    # Performance
    # =========================
    print(f"\n⚡ PERFORMANCE:")
    print(f"  Analysis Time: {ai_result.get('analysis_time', 0):.2f}s")
    if 'cache_stats' in ai_result:
        print(f"  Cache Hit Rate: {ai_result['cache_stats']['hit_rate']:.1f}%")
    
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
    
    analyze_symbol_complete(symbol)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
