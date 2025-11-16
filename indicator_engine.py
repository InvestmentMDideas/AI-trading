"""
Indicator Engine
Calculates 145-point probability scoring system.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from market_metrics import MarketMetrics
from ibkr_data_feed import IBKRDataFeed
import config_ai as config


class IndicatorEngine:
    """Main indicator calculation engine."""
    
    def __init__(self, data_feed: IBKRDataFeed):
        """
        Initialize indicator engine.
        
        Args:
            data_feed: Connected IBKR data feed
        """
        self.data_feed = data_feed
        self.metrics = MarketMetrics(config)
        self.config = config
    
    def analyze(self, symbol: str) -> Dict[str, Any]:
        """
        Perform complete analysis on a symbol.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dict with all analysis results
        """
        # Fetch 1-minute bars
        df = self.data_feed.get_1min_bars(symbol)
        
        # Handle failed data fetch - CRITICAL FIX
        if not isinstance(df, pd.DataFrame):
            print(f"[ERROR] Data fetch failed for {symbol}: {df}")
            return {
                'symbol': symbol,
                'error': 'Data fetch failed',
                'probability': 0,
                'quality': 'ERROR',
                'current_price': 0,
                'squeeze_status': 'ERROR',
                'vol_regime': 'UNKNOWN',
                'signals': {},
                'score_breakdown': {},
                'vwap_zones': {},
                'atr': 0,
                'rvol': 0
            }
        
        if df.empty or len(df) < self.config.MIN_BARS_REQUIRED:
            print(f"[WARN] Insufficient data for {symbol}: {len(df)} bars")
            return {
                'symbol': symbol,
                'error': 'Insufficient data',
                'probability': 0,
                'quality': 'INSUFFICIENT_DATA'
            }
        
        # Get current price
        current_price = self.data_feed.get_current_price(symbol)
        if not current_price:
            current_price = df['close'].iloc[-1]
        
        # Calculate all metrics
        try:
            # VWAP
            vwap = self.metrics.calculate_vwap(df)
            vwap_current = vwap.iloc[-1]
            
            # ATR
            atr = self.metrics.calculate_atr(df, self.config.ATR_LENGTH)
            atr_current = atr.iloc[-1]
            
            # MACD
            macd_line, signal_line, histogram = self.metrics.calculate_macd(
                df, self.config.MACD_FAST, self.config.MACD_SLOW, self.config.MACD_SIGNAL
            )
            
            # EMA
            fast_ema = self.metrics.calculate_ema(df['close'], self.config.FAST_EMA)
            slow_ema = self.metrics.calculate_ema(df['close'], self.config.SLOW_EMA)
            
            # Squeeze
            squeeze_status, momentum_value = self.metrics.calculate_squeeze(
                df, 
                self.config.BB_LENGTH, self.config.BB_MULT,
                self.config.KC_LENGTH, self.config.KC_MULT,
                self.config.MOM_LENGTH, self.config.USE_TRUE_RANGE
            )
            
            # Volume
            rvol = self.metrics.calculate_relative_volume(df, self.config.RVOL_PERIOD)
            rvol_current = rvol.iloc[-1]
            
            # Volatility Regime
            vol_regime = self.metrics.detect_volatility_regime(atr, self.config.ATR_LOOKBACK)
            
            # Calculate 145-point probability score
            score_breakdown = self._calculate_probability_scores(
                df, current_price, vwap_current, atr_current,
                macd_line.iloc[-1], signal_line.iloc[-1], histogram.iloc[-1],
                fast_ema.iloc[-1], slow_ema.iloc[-1],
                rvol_current, squeeze_status, momentum_value, vol_regime
            )
            
            total_score = sum(score_breakdown.values())
            probability = min(100, (total_score / 145) * 100)
            
            # Determine quality
            if probability >= self.config.HIGH_PROB_THRESHOLD:
                quality = 'HIGH'
            elif probability >= self.config.MED_PROB_THRESHOLD:
                quality = 'MEDIUM'
            else:
                quality = 'LOW'
            
            # Generate signals
            signals = self._generate_signals(
                current_price, vwap_current, atr_current,
                macd_line.iloc[-1], signal_line.iloc[-1],
                fast_ema.iloc[-1], slow_ema.iloc[-1],
                squeeze_status, probability, quality
            )
            
            # Calculate VWAP zones
            vwap_zones = self._calculate_vwap_zones(
                current_price, vwap_current, atr_current, df
            )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'probability': round(probability, 2),
                'quality': quality,
                'squeeze_status': squeeze_status,
                'squeeze_momentum': round(momentum_value, 2),
                'vol_regime': vol_regime,
                'atr': round(atr_current, 2),
                'rvol': round(rvol_current, 2),
                'vwap': round(vwap_current, 2),
                'score_breakdown': score_breakdown,
                'signals': signals,
                'vwap_zones': vwap_zones,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[ERROR] Analysis failed for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'symbol': symbol,
                'error': str(e),
                'probability': 0,
                'quality': 'ERROR'
            }
    
    def _calculate_probability_scores(self, df: pd.DataFrame, price: float, 
                                     vwap: float, atr: float, macd: float, 
                                     signal: float, histogram: float, 
                                     fast_ema: float, slow_ema: float,
                                     rvol: float, squeeze_status: str, 
                                     momentum: float, vol_regime: str) -> Dict[str, float]:
        """Calculate individual component scores for 145-point system."""
        
        scores = {}
        
        # VWAP Score (0-20)
        vwap_distance = abs(price - vwap) / atr if atr > 0 else 999
        if vwap_distance < 0.5:
            scores['vwap'] = 20
        elif vwap_distance < 1.0:
            scores['vwap'] = 15
        elif vwap_distance < 2.0:
            scores['vwap'] = 10
        elif vwap_distance < 3.0:
            scores['vwap'] = 5
        else:
            scores['vwap'] = 0
        
        # MACD Score (0-25)
        if macd > signal and histogram > 0:
            scores['macd'] = 25
        elif macd > signal:
            scores['macd'] = 20
        elif abs(macd - signal) / price < 0.001:
            scores['macd'] = 15
        elif histogram > 0:
            scores['macd'] = 10
        else:
            scores['macd'] = 5
        
        # EMA Score (0-20)
        if fast_ema > slow_ema and price > fast_ema:
            scores['ema'] = 20
        elif fast_ema > slow_ema:
            scores['ema'] = 15
        elif price > fast_ema:
            scores['ema'] = 10
        else:
            scores['ema'] = 5
        
        # Volume Score (0-20)
        if rvol >= 2.0:
            scores['volume'] = 20
        elif rvol >= 1.5:
            scores['volume'] = 15
        elif rvol >= 1.0:
            scores['volume'] = 10
        elif rvol >= 0.5:
            scores['volume'] = 5
        else:
            scores['volume'] = 0
        
        # Extension Score (0-15)
        extension_pct = abs(price - vwap) / vwap * 100 if vwap > 0 else 0
        if extension_pct < 1.0:
            scores['extension'] = 15
        elif extension_pct < 2.0:
            scores['extension'] = 10
        elif extension_pct < 3.0:
            scores['extension'] = 5
        else:
            scores['extension'] = 0
        
        # Squeeze Score (0-20)
        if squeeze_status == 'FIRING':
            scores['squeeze'] = 20
        elif squeeze_status == 'TIGHT':
            scores['squeeze'] = 15
        elif squeeze_status == 'MODERATE':
            scores['squeeze'] = 10
        elif squeeze_status == 'LOOSE':
            scores['squeeze'] = 5
        else:
            scores['squeeze'] = 0
        
        # Momentum Score (0-15)
        if abs(momentum) >= 3.0:
            scores['momentum'] = 15
        elif abs(momentum) >= 2.0:
            scores['momentum'] = 10
        elif abs(momentum) >= 1.0:
            scores['momentum'] = 5
        else:
            scores['momentum'] = 0
        
        # Confluence Bonus (0-10)
        confluence_count = 0
        if scores['vwap'] >= 15:
            confluence_count += 1
        if scores['macd'] >= 20:
            confluence_count += 1
        if scores['ema'] >= 15:
            confluence_count += 1
        if scores['squeeze'] >= 15:
            confluence_count += 1
        
        if confluence_count >= 4:
            scores['confluence'] = 10
        elif confluence_count >= 3:
            scores['confluence'] = 7
        elif confluence_count >= 2:
            scores['confluence'] = 4
        else:
            scores['confluence'] = 0
        
        return scores
    
    def _generate_signals(self, price: float, vwap: float, atr: float,
                         macd: float, signal: float, fast_ema: float,
                         slow_ema: float, squeeze_status: str,
                         probability: float, quality: str) -> Dict[str, bool]:
        """Generate trading signals."""
        
        signals = {}
        
        # Basic conditions
        bullish_macd = macd > signal
        bullish_ema = fast_ema > slow_ema
        near_vwap = abs(price - vwap) < (atr * 1.0)
        squeeze_firing = squeeze_status == 'FIRING'
        
        # Long entry
        signals['long_entry'] = (
            bullish_macd and 
            bullish_ema and
            probability >= self.config.MED_PROB_THRESHOLD
        )
        
        # Short entry
        signals['short_entry'] = (
            not bullish_macd and
            not bullish_ema and
            probability >= self.config.MED_PROB_THRESHOLD
        )
        
        # Premium long (highest quality)
        signals['premium_long'] = (
            signals['long_entry'] and
            squeeze_firing and
            near_vwap and
            quality == 'HIGH'
        )
        
        # Premium short
        signals['premium_short'] = (
            signals['short_entry'] and
            squeeze_firing and
            near_vwap and
            quality == 'HIGH'
        )
        
        return signals
    
    def _calculate_vwap_zones(self, price: float, vwap: float, 
                             atr: float, df: pd.DataFrame) -> Dict[str, Dict]:
        """Calculate VWAP-based entry/exit zones."""
        
        zones = {}
        
        # Long zone
        long_entry = vwap + (atr * self.config.VWAP_ENTRY_DISTANCE)
        long_stop = vwap - (atr * self.config.VWAP_STOP_DISTANCE)
        long_target = long_entry + (atr * self.config.VWAP_TARGET_MULTIPLE)
        
        risk_per_share = long_entry - long_stop
        if risk_per_share > 0:
            position_size = int((self.config.ACCOUNT_EQUITY * self.config.RISK_PERCENT / 100) / risk_per_share)
        else:
            position_size = 0
        
        zones['long'] = {
            'entry': round(long_entry, 2),
            'stop': round(long_stop, 2),
            'target': round(long_target, 2),
            'position_size': position_size
        }
        
        # Short zone
        short_entry = vwap - (atr * self.config.VWAP_ENTRY_DISTANCE)
        short_stop = vwap + (atr * self.config.VWAP_STOP_DISTANCE)
        short_target = short_entry - (atr * self.config.VWAP_TARGET_MULTIPLE)
        
        risk_per_share = short_stop - short_entry
        if risk_per_share > 0:
            position_size = int((self.config.ACCOUNT_EQUITY * self.config.RISK_PERCENT / 100) / risk_per_share)
        else:
            position_size = 0
        
        zones['short'] = {
            'entry': round(short_entry, 2),
            'stop': round(short_stop, 2),
            'target': round(short_target, 2),
            'position_size': position_size
        }
        
        return zones


if __name__ == "__main__":
    # Quick test
    from ibkr_data_feed import create_data_feed
    
    with create_data_feed(config) as feed:
        engine = IndicatorEngine(feed)
        result = engine.analyze('SPY')
        
        print(f"\nAnalysis for {result['symbol']}:")
        print(f"  Probability: {result['probability']}% ({result['quality']})")
        print(f"  Squeeze: {result['squeeze_status']}")
        print(f"  Signals: {result['signals']}")
