"""
Tests for AI Analyst Engine
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("[WARN] ollama not installed. Run: pip install ollama")

from prompt_templates import PromptTemplates
from ai_cache import AICache
from ai_analyst import AIAnalyst


def test_ollama_connection():
    """Test 1: Ollama Connection"""
    print("\n" + "="*60)
    print("TEST 1: Ollama Connection")
    print("="*60)
    
    if not OLLAMA_AVAILABLE:
        print("❌ Ollama package not installed")
        return False
    
    try:
        # Try to list models
        response = ollama.list()
        print("✅ Ollama is running")
        
        # Try to check if qwen2.5:7b is available
        models = []
        if hasattr(response, 'models'):
            for m in response.models:
                if hasattr(m, 'model'):
                    models.append(m.model)
                elif hasattr(m, 'name'):
                    models.append(m.name)
                elif isinstance(m, dict):
                    models.append(m.get('model') or m.get('name', ''))
        
        if 'qwen2.5:7b' in models:
            print("✅ qwen2.5:7b model is available")
            return True
        else:
            print(f"⚠️  qwen2.5:7b not found. Available models: {models}")
            print("   Run: ollama pull qwen2.5:7b")
            return False
            
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        print("   Make sure Ollama is running")
        return False


def test_prompt_templates():
    """Test 2: Prompt Templates"""
    print("\n" + "="*60)
    print("TEST 2: Prompt Templates")
    print("="*60)
    
    templates = PromptTemplates()
    
    mock_data = {
        'symbol': 'AAPL',
        'current_price': 150.0,
        'probability': 68,
        'quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': 'NORMAL',
        'atr': 2.5,
        'rvol': 1.5
    }
    
    mock_context = {'regime': 'NORMAL', 'score': 75}
    mock_technical = {'score': 80}
    mock_risk = {'score': 85}
    
    tests = [
        ('Market Context', templates.market_context(mock_data)),
        ('Technical Analysis', templates.technical_analysis(mock_data)),
        ('Risk Assessment', templates.risk_assessment(mock_data)),
        ('Aggressive Scenario', templates.aggressive_scenario(mock_data, mock_context, mock_technical, mock_risk)),
        ('Moderate Scenario', templates.moderate_scenario(mock_data, mock_context, mock_technical, mock_risk)),
        ('Conservative Scenario', templates.conservative_scenario(mock_data, mock_context, mock_technical, mock_risk))
    ]
    
    all_passed = True
    for name, prompt in tests:
        if prompt and len(prompt) > 50:
            print(f"  ✅ {name}: {len(prompt)} chars")
        else:
            print(f"  ❌ {name}: Invalid")
            all_passed = False
    
    if all_passed:
        print("\n✅ All prompt templates working!")
    return all_passed


def test_json_cleaning():
    """Test 3: JSON Response Cleaning"""
    print("\n" + "="*60)
    print("TEST 3: JSON Response Cleaning")
    print("="*60)
    
    analyst = AIAnalyst()
    
    test_cases = [
        ('```json\n{"score": 75}\n```', True),
        ('{"regime": "NORMAL", "score": 80}', True),
        ('Some text before\n{"score": 70}\nSome text after', True),
        ('Not valid JSON at all', False)
    ]
    
    all_passed = True
    for i, (response, should_work) in enumerate(test_cases, 1):
        result = analyst._clean_json_response(response)
        worked = bool(result)
        
        if worked == should_work:
            print(f"  ✅ Case {i}: {'Cleaned and parsed successfully' if worked else 'Correctly failed to parse'}")
        else:
            print(f"  ❌ Case {i}: Expected {'success' if should_work else 'failure'}, got {'success' if worked else 'failure'}")
            all_passed = False
    
    return all_passed


def test_cache():
    """Test 4: AI Response Cache"""
    print("\n" + "="*60)
    print("TEST 4: AI Response Cache")
    print("="*60)
    
    cache = AICache(max_size=10, ttl=2)
    
    # Test basic set/get
    cache.set("test_key", "test_value")
    result = cache.get("test_key")
    if result == "test_value":
        print("  ✅ Basic cache set/get works")
    else:
        print("  ❌ Cache get failed")
        return False
    
    # Test cache miss
    result = cache.get("nonexistent_key")
    if result is None:
        print("  ✅ Cache miss works")
    else:
        print("  ❌ Cache miss failed")
        return False
    
    # Test expiration
    cache.set("expire_key", "expire_value")
    time.sleep(2.1)
    result = cache.get("expire_key")
    if result is None:
        print("  ✅ Cache expiration works")
    else:
        print("  ❌ Cache expiration failed")
        return False
    
    # Test stats
    stats = cache.get_stats()
    print(f"\n  Cache Stats: {stats}")
    if 'hit_rate' in stats:
        print("  ✅ Cache statistics working")
        return True
    else:
        print("  ❌ Cache statistics failed")
        return False


def test_ai_analyst_simple():
    """Test 5: AI Analyst Simple Call"""
    print("\n" + "="*60)
    print("TEST 5: AI Analyst Simple Call")
    print("="*60)
    
    if not OLLAMA_AVAILABLE:
        print("❌ Ollama not available")
        return False
    
    try:
        print("\n  Running AI analysis...")
        analyst = AIAnalyst(model="qwen2.5:7b")
        
        mock_data = {
            'symbol': 'AAPL',
            'current_price': 150.0,
            'probability': 68,
            'quality': 'MEDIUM',
            'squeeze_status': 'FIRING',
            'vol_regime': 'NORMAL',
            'atr': 2.5,
            'rvol': 1.5,
            'signals': {'long_entry': True}
        }
        
        result = analyst.analyze_context(mock_data)
        
        print(f"\n  Result: {result}")
        
        if 'regime' in result and 'score' in result:
            print("  ✅ AI analysis working!")
            return True
        else:
            print("  ❌ Missing expected fields")
            return False
            
    except Exception as e:
        print(f"  ❌ AI call failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_analysis():
    """Test 6: Full AI Analysis"""
    print("\n" + "="*60)
    print("TEST 6: Full AI Analysis")
    print("="*60)
    
    if not OLLAMA_AVAILABLE:
        print("❌ Ollama not available")
        return False
    
    try:
        print("\n  Running FULL AI analysis (all 6 stages)...")
        print("  This will take ~5-10 seconds...")
        
        analyst = AIAnalyst(model="qwen2.5:7b")
        
        # Create comprehensive mock data
        mock_indicator_data = {
            'symbol': 'SPY',
            'current_price': 450.0,
            'probability': 68,
            'quality': 'MEDIUM',
            'squeeze_status': 'FIRING',
            'squeeze_strength': 'MODERATE',
            'vol_regime': 'NORMAL',
            'atr': 2.5,
            'rvol': 1.5,
            'signals': {
                'long_entry': True,
                'short_entry': False,
                'premium_long': False
            },
            'score_breakdown': {
                'vwap': 15,
                'macd': 20,
                'ema': 15,
                'volume': 15,
                'extension': 10,
                'squeeze': 15,
                'momentum': 10,
                'confluence': 5
            },
            'vwap_zones': {
                'long': {
                    'entry': 451.0,
                    'stop': 448.0,
                    'target': 455.0,
                    'position_size': 100
                }
            }
        }
        
        start = time.time()
        result = analyst.analyze(mock_indicator_data, symbol='SPY')
        elapsed = time.time() - start
        
        print(f"\n  ⏱️  Analysis completed in {elapsed:.2f}s")
        
        # Check required fields
        required_fields = ['context', 'technical', 'risk', 'scenarios', 'recommendation']
        missing = [f for f in required_fields if f not in result]
        
        if missing:
            print(f"  ❌ Missing fields: {missing}")
            return False
        
        # Check scenarios
        if 'aggressive' not in result['scenarios']:
            print("  ❌ Missing aggressive scenario")
            return False
        
        if 'moderate' not in result['scenarios']:
            print("  ❌ Missing moderate scenario")
            return False
        
        if 'conservative' not in result['scenarios']:
            print("  ❌ Missing conservative scenario")
            return False
        
        print("\n  ✅ Full analysis working!")
        print(f"  Recommended: {result['recommendation']}")
        print(f"  Confidence: {result['recommended_confidence']}%")
        
        # Show stats
        stats = analyst.get_stats()
        print(f"\n  Performance Stats:")
        print(f"    Total AI calls: {stats['total_calls']}")
        print(f"    Avg time/call: {stats['avg_time_per_call']}s")
        print(f"    Cache hit rate: {stats['cache_hit_rate']}%")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Full analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("║" + " "*21 + "AI ANALYST TESTS" + " "*23 + "║")
    print("="*60)
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Prompt Templates", test_prompt_templates),
        ("JSON Cleaning", test_json_cleaning),
        ("Cache System", test_cache),
        ("AI Analyst Simple", test_ai_analyst_simple),
        ("Full AI Analysis", test_full_analysis)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("║" + " "*20 + "TEST SUMMARY" + " "*27 + "║")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n  🎉 ALL TESTS PASSED!")
    else:
        failed_count = total_count - passed_count
        print(f"\n  ❌ {failed_count} test(s) failed")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)