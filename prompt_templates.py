"""
AI Prompt Templates
Optimized prompts for fast, reliable AI responses.
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of optimized AI prompts."""
    
    @staticmethod
    def market_context(data: Dict[str, Any]) -> str:
        """Stage 1: Market context analysis."""
        symbol = data.get('symbol', 'UNKNOWN')
        vol_regime = data.get('vol_regime', 'NORMAL')
        atr = data.get('atr', 0)
        rvol = data.get('rvol', 1.0)
        
        return f"""Analyze market context for {symbol}:
Volatility: {vol_regime} (ATR: {atr:.2f})
RVOL: {rvol:.2f}x

Respond ONLY with JSON:
{{
  "regime": "LOW_VOL|NORMAL|HIGH_VOL",
  "session": "PREMARKET|REGULAR|AFTERHOURS",
  "assessment": "brief 1-line summary",
  "score": 0-100
}}"""
    
    @staticmethod
    def technical_analysis(data: Dict[str, Any]) -> str:
        """Stage 2: Technical setup analysis."""
        symbol = data.get('symbol', 'UNKNOWN')
        prob = data.get('probability', 0)
        quality = data.get('quality', 'UNKNOWN')
        squeeze = data.get('squeeze_status', 'UNKNOWN')
        
        breakdown = data.get('score_breakdown', {})
        vwap_score = breakdown.get('vwap', 0)
        macd_score = breakdown.get('macd', 0)
        ema_score = breakdown.get('ema', 0)
        
        return f"""Analyze technical setup for {symbol}:
Probability: {prob}% ({quality})
Squeeze: {squeeze}
Scores: VWAP={vwap_score}/20, MACD={macd_score}/25, EMA={ema_score}/20

Respond ONLY with JSON:
{{
  "probability_assessment": "brief assessment",
  "squeeze_evaluation": "brief evaluation",
  "trend_quality": "brief quality assessment",
  "score": 0-100
}}"""
    
    @staticmethod
    def risk_assessment(data: Dict[str, Any]) -> str:
        """Stage 3: Risk analysis."""
        symbol = data.get('symbol', 'UNKNOWN')
        price = data.get('current_price', 0)
        
        vwap_zones = data.get('vwap_zones', {})
        long_zone = vwap_zones.get('long', {})
        entry = long_zone.get('entry', price)
        stop = long_zone.get('stop', price * 0.98)
        target = long_zone.get('target', price * 1.02)
        
        return f"""Analyze risk for {symbol}:
Price: ${price:.2f}
Entry: ${entry:.2f}
Stop: ${stop:.2f}
Target: ${target:.2f}

Respond ONLY with JSON:
{{
  "entry_quality": "brief assessment",
  "stop_placement": "brief assessment",
  "r_r_ratio": calculated R:R ratio,
  "score": 0-100
}}"""
    
    @staticmethod
    def aggressive_scenario(data: Dict[str, Any], context: Dict, technical: Dict, risk: Dict) -> str:
        """Stage 4a: Aggressive scenario."""
        symbol = data.get('symbol', 'UNKNOWN')
        prob = data.get('probability', 0)
        price = data.get('current_price', 0)
        
        vwap_zones = data.get('vwap_zones', {})
        long_zone = vwap_zones.get('long', {})
        entry = long_zone.get('entry', price)
        stop = long_zone.get('stop', price * 0.98)
        target = long_zone.get('target', price * 1.02)
        
        return f"""AGGRESSIVE strategy for {symbol}:
Rules: Min 45% prob, enter NOW, 1.2% risk, wider stops
Current: {prob}% probability
Price: ${price:.2f}
Context: {context.get('regime', 'NORMAL')}
Entry: ${entry:.2f}, Stop: ${stop:.2f}, Target: ${target:.2f}

Decide: ENTER_LONG, ENTER_SHORT, or WAIT

Respond ONLY with JSON:
{{
  "action": "ENTER_LONG|ENTER_SHORT|WAIT",
  "entry": entry_price,
  "stop": stop_price,
  "target": target_price,
  "size": share_count,
  "confidence": 0-100,
  "reasoning": "brief 1-line reason"
}}"""
    
    @staticmethod
    def moderate_scenario(data: Dict[str, Any], context: Dict, technical: Dict, risk: Dict) -> str:
        """Stage 4b: Moderate scenario."""
        symbol = data.get('symbol', 'UNKNOWN')
        prob = data.get('probability', 0)
        price = data.get('current_price', 0)
        
        vwap_zones = data.get('vwap_zones', {})
        long_zone = vwap_zones.get('long', {})
        entry = long_zone.get('entry', price)
        stop = long_zone.get('stop', price * 0.98)
        target = long_zone.get('target', price * 1.02)
        
        return f"""MODERATE strategy for {symbol}:
Rules: Min 55% prob, wait for zone, 1.0% risk
Current: {prob}% probability
Price: ${price:.2f}
Context: {context.get('regime', 'NORMAL')}
Entry Zone: ${entry:.2f}, Stop: ${stop:.2f}, Target: ${target:.2f}

Decide: ENTER_LONG, ENTER_AT_ZONE, ENTER_SHORT, or WAIT

Respond ONLY with JSON:
{{
  "action": "ENTER_LONG|ENTER_AT_ZONE|ENTER_SHORT|WAIT",
  "entry": entry_price,
  "stop": stop_price,
  "target": target_price,
  "size": share_count,
  "confidence": 0-100,
  "reasoning": "brief 1-line reason"
}}"""
    
    @staticmethod
    def conservative_scenario(data: Dict[str, Any], context: Dict, technical: Dict, risk: Dict) -> str:
        """Stage 4c: Conservative scenario."""
        symbol = data.get('symbol', 'UNKNOWN')
        prob = data.get('probability', 0)
        price = data.get('current_price', 0)
        squeeze = data.get('squeeze_status', 'UNKNOWN')
        
        vwap_zones = data.get('vwap_zones', {})
        long_zone = vwap_zones.get('long', {})
        entry = long_zone.get('entry', price)
        stop = long_zone.get('stop', price * 0.98)
        target = long_zone.get('target', price * 1.02)
        
        return f"""CONSERVATIVE strategy for {symbol}:
Rules: Min 70% prob, tight squeeze preferred, 0.75% risk
Current: {prob}% probability, Squeeze: {squeeze}
Price: ${price:.2f}
Context: {context.get('regime', 'NORMAL')}
Pullback Zone: ${entry:.2f}, Stop: ${stop:.2f}, Target: ${target:.2f}

Decide: Only take HIGH quality setups or WAIT

Respond ONLY with JSON:
{{
  "action": "ENTER_LONG|ENTER_SHORT|WAIT",
  "entry": entry_price_or_null,
  "stop": stop_price_or_null,
  "target": target_price_or_null,
  "size": share_count_or_0,
  "confidence": 0-100_or_0,
  "reasoning": "brief 1-line reason"
}}"""


if __name__ == "__main__":
    # Quick test
    templates = PromptTemplates()
    
    mock_data = {
        'symbol': 'AAPL',
        'probability': 68,
        'quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': 'NORMAL',
        'atr': 2.5,
        'rvol': 1.5,
        'current_price': 150.0
    }
    
    prompt = templates.market_context(mock_data)
    print(f"Market Context Prompt ({len(prompt)} chars):")
    print(prompt)