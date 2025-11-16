"""
AI Analyst Engine
Multi-stage reasoning system for trading decisions.
"""

import time
import json
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

try:
    import ollama
except ImportError:
    print("[ERROR] ollama package not found. Install with: pip install ollama")
    ollama = None

from prompt_templates import PromptTemplates
from ai_cache import AICache


class AIAnalyst:
    """Multi-stage AI reasoning engine for trading analysis."""
    
    def __init__(self, model: str = "qwen2.5:7b", use_cache: bool = True):
        """
        Initialize AI Analyst.
        
        Args:
            model: Ollama model name
            use_cache: Enable response caching for speed
        """
        self.model = model
        self.use_cache = use_cache
        self.cache = AICache(max_size=100, ttl=300) if use_cache else None
        self.templates = PromptTemplates()
        
        # Performance tracking
        self.call_count = 0
        self.total_time = 0
        self.cache_hits = 0
        
        # Verify Ollama is available
        if ollama is None:
            raise ImportError("Ollama not installed. Run: pip install ollama")
        
        # Check if model is available
        self._check_ollama_models()
    
    def _check_ollama_models(self):
        """Check if required model is available in Ollama."""
        try:
            # List available models
            models_response = ollama.list()
            
            # Extract model names - handle different response formats
            available_models = []
            
            # Try different response formats
            if hasattr(models_response, 'models'):
                # Response is an object with models attribute
                for m in models_response.models:
                    if hasattr(m, 'model'):
                        available_models.append(m.model)
                    elif hasattr(m, 'name'):
                        available_models.append(m.name)
                    elif isinstance(m, dict):
                        available_models.append(m.get('model') or m.get('name', ''))
            elif isinstance(models_response, dict) and 'models' in models_response:
                # Response is a dict with models key
                for m in models_response['models']:
                    available_models.append(m.get('model') or m.get('name', ''))
            
            # Check if our model is available
            if self.model not in available_models:
                print(f"[WARN] Model '{self.model}' not found in Ollama")
                print(f"[WARN] Available models: {available_models}")
                print(f"[WARN] Run: ollama pull {self.model}")
                return False
            
            print(f"[AI] ✅ Model '{self.model}' is available")
            return True
            
        except Exception as e:
            print(f"[WARN] Could not check Ollama models: {e}")
            print(f"[INFO] Attempting to continue anyway...")
            return False
    
    def _call_ai(self, prompt: str, timeout: int = 15) -> str:
        """
        Call Ollama AI with caching and retry logic.
        
        Args:
            prompt: The prompt to send
            timeout: Maximum seconds to wait
            
        Returns:
            AI response text
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(prompt)
            if cached:
                self.cache_hits += 1
                return cached
        
        # Make AI call with retries
        max_retries = 2
        for attempt in range(max_retries):
            try:
                start = time.time()
                
                def ai_function():
                    return ollama.generate(
                        model=self.model,
                        prompt=prompt,
                        options={'temperature': 0.1}
                    )
                
                # Call with timeout
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(ai_function)
                    try:
                        response = future.result(timeout=timeout)
                        raw_response = response.response if hasattr(response, 'response') else str(response)
                    except TimeoutError:
                        print(f"[WARN] AI call timeout (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            continue
                        return "{}"
                
                elapsed = time.time() - start
                self.call_count += 1
                self.total_time += elapsed
                
                # Cache the response
                if self.cache:
                    self.cache.set(prompt, raw_response)
                
                return raw_response
                
            except Exception as e:
                print(f"[ERROR] AI call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                return "{}"
        
        return "{}"
    
    def _clean_json_response(self, response: str) -> Dict[str, Any]:
        """Clean and parse AI JSON response."""
        try:
            # Remove markdown code blocks
            cleaned = response.replace('```json', '').replace('```', '').strip()
            
            # Try to parse
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            try:
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = cleaned[start:end]
                    return json.loads(json_str)
            except:
                pass
            
            return {}
    
    def analyze_context(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 1: Analyze market context."""
        prompt = self.templates.market_context(indicator_data)
        response = self._call_ai(prompt)
        result = self._clean_json_response(response)
        
        return {
            'regime': result.get('regime', 'NORMAL'),
            'session': result.get('session', 'REGULAR'),
            'assessment': result.get('assessment', 'Unknown'),
            'score': result.get('score', 50)
        }
    
    def analyze_technical(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Analyze technical setup."""
        prompt = self.templates.technical_analysis(indicator_data)
        response = self._call_ai(prompt)
        result = self._clean_json_response(response)
        
        return {
            'probability_assessment': result.get('probability_assessment', 'Unknown'),
            'squeeze_evaluation': result.get('squeeze_evaluation', 'Unknown'),
            'trend_quality': result.get('trend_quality', 'Unknown'),
            'score': result.get('score', 50)
        }
    
    def analyze_risk(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 3: Analyze risk factors."""
        prompt = self.templates.risk_assessment(indicator_data)
        response = self._call_ai(prompt)
        result = self._clean_json_response(response)
        
        return {
            'entry_quality': result.get('entry_quality', 'Unknown'),
            'stop_placement': result.get('stop_placement', 'Unknown'),
            'r_r_ratio': result.get('r_r_ratio', 0),
            'score': result.get('score', 50)
        }
    
    def analyze_scenario(self, scenario_type: str, indicator_data: Dict[str, Any], 
                        context: Dict, technical: Dict, risk: Dict) -> Dict[str, Any]:
        """
        Stage 4: Analyze specific scenario (aggressive/moderate/conservative).
        
        Args:
            scenario_type: 'aggressive', 'moderate', or 'conservative'
            indicator_data: Full indicator results
            context: Context analysis results
            technical: Technical analysis results
            risk: Risk analysis results
            
        Returns:
            Scenario decision with action, entry, stop, target, etc.
        """
        # Get the appropriate prompt template
        if scenario_type == 'aggressive':
            prompt = self.templates.aggressive_scenario(indicator_data, context, technical, risk)
        elif scenario_type == 'moderate':
            prompt = self.templates.moderate_scenario(indicator_data, context, technical, risk)
        elif scenario_type == 'conservative':
            prompt = self.templates.conservative_scenario(indicator_data, context, technical, risk)
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
        
        response = self._call_ai(prompt)
        result = self._clean_json_response(response)
        
        return {
            'action': result.get('action', 'WAIT'),
            'entry': result.get('entry'),
            'stop': result.get('stop'),
            'target': result.get('target'),
            'size': result.get('size', 0),
            'confidence': result.get('confidence', 0),
            'reasoning': result.get('reasoning', 'No reasoning provided')
        }
    
    def analyze_scenarios_parallel(self, indicator_data: Dict[str, Any],
                                   context: Dict, technical: Dict, risk: Dict) -> Dict[str, Dict]:
        """
        Analyze all three scenarios in parallel for speed.
        
        Returns:
            Dict with keys 'aggressive', 'moderate', 'conservative'
        """
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                'aggressive': executor.submit(
                    self.analyze_scenario, 'aggressive', indicator_data, context, technical, risk
                ),
                'moderate': executor.submit(
                    self.analyze_scenario, 'moderate', indicator_data, context, technical, risk
                ),
                'conservative': executor.submit(
                    self.analyze_scenario, 'conservative', indicator_data, context, technical, risk
                )
            }
            
            return {
                scenario: future.result()
                for scenario, future in futures.items()
            }
    
    def pick_recommendation(self, scenarios: Dict[str, Dict]) -> str:
        """
        Pick the best scenario based on confidence scores.
        
        Returns:
            'aggressive', 'moderate', or 'conservative'
        """
        # Filter out WAIT actions
        valid_scenarios = {
            name: scenario 
            for name, scenario in scenarios.items() 
            if scenario.get('action') != 'WAIT'
        }
        
        if not valid_scenarios:
            return 'conservative'  # Default to conservative if all are WAIT
        
        # Pick highest confidence
        best = max(valid_scenarios.items(), key=lambda x: x[1].get('confidence', 0))
        return best[0]
    
    def analyze(self, indicator_data: Dict[str, Any], symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """
        Complete multi-stage AI analysis.
        
        Args:
            indicator_data: Results from IndicatorEngine.analyze()
            symbol: Stock symbol
            
        Returns:
            Complete analysis with all stages and scenarios
        """
        start_time = time.time()
        
        try:
            print(f"[AI] Analyzing {symbol}...")
            
            # Stage 1: Context
            print("  Stage 1: Market Context...")
            context = self.analyze_context(indicator_data)
            
            # Stage 2: Technical
            print("  Stage 2: Technical Analysis...")
            technical = self.analyze_technical(indicator_data)
            
            # Stage 3: Risk
            print("  Stage 3: Risk Assessment...")
            risk = self.analyze_risk(indicator_data)
            
            # Stage 4: Scenarios (parallel)
            print("  Stage 4: Three Scenarios (parallel)...")
            scenarios = self.analyze_scenarios_parallel(indicator_data, context, technical, risk)
            
            # Stage 5: Recommendation
            print("  Stage 5: Final Recommendation...")
            recommended = self.pick_recommendation(scenarios)
            
            analysis_time = time.time() - start_time
            
            result = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'context': context,
                'technical': technical,
                'risk': risk,
                'scenarios': scenarios,
                'recommendation': recommended,
                'recommended_confidence': scenarios[recommended].get('confidence', 0),
                'analysis_time': round(analysis_time, 2)
            }
            
            print(f"[AI] ✅ Analysis complete in {analysis_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"[ERROR] AI analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_time = self.total_time / self.call_count if self.call_count > 0 else 0
        cache_stats = self.cache.get_stats() if self.cache else {}
        
        return {
            'total_calls': self.call_count,
            'total_time': round(self.total_time, 2),
            'avg_time_per_call': round(avg_time, 2),
            'cache_hits': self.cache_hits,
            'cache_hit_rate': round(self.cache_hits / self.call_count * 100, 1) if self.call_count > 0 else 0,
            **cache_stats
        }


def test_ai_analyst():
    """Quick test of AI analyst."""
    analyst = AIAnalyst()
    
    # Mock data
    mock_data = {
        'symbol': 'AAPL',
        'current_price': 150.0,
        'probability': 65,
        'quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': 'NORMAL',
        'signals': {'long_entry': True}
    }
    
    result = analyst.analyze_context(mock_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_ai_analyst()
