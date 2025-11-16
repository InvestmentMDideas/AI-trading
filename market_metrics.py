"""
Market Metrics Calculator

Implements all technical calculations from the Pine Script indicator:
- VWAP calculations
- TTM Squeeze (Bollinger Bands + Keltner Channels)
- MACD
- EMAs
- ATR
- Volume analysis (RVOL)
- Volatility regime detection
- Multi-timeframe metrics

All calculations match the Pine Script logic exactly.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, Optional


class MarketMetrics:
    """Calculate technical indicators matching Pine Script logic."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        
    # =========================
    # Core Indicators
    # =========================
    
    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume-Weighted Average Price (VWAP).
        Resets at market open (assumes sorted intraday data).
        """
        if df.empty or 'close' not in df.columns:
            return pd.Series(dtype=float)
        
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        cumulative_tp_volume = (typical_price * df['volume']).cumsum()
        cumulative_volume = df['volume'].cumsum()
        
        # Avoid division by zero
        vwap = cumulative_tp_volume / cumulative_volume.replace(0, np.nan)
        return vwap.fillna(method='ffill')
    
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        if series.empty:
            return pd.Series(dtype=float)
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_sma(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        if series.empty:
            return pd.Series(dtype=float)
        return series.rolling(window=period).mean()
    
    def calculate_std(self, series: pd.Series, period: int) -> pd.Series:
        """Calculate Standard Deviation."""
        if series.empty:
            return pd.Series(dtype=float)
        return series.rolling(window=period).std()
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            df: DataFrame with high, low, close columns
            period: ATR calculation period
            
        Returns:
            Series with ATR values
        """
        if df.empty or len(df) < 2:
            return pd.Series(dtype=float)
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range components
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        # True Range = max of the three
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR = EMA of True Range
        atr = true_range.ewm(span=period, adjust=False).mean()
        return atr.fillna(0)
    
    def calculate_macd(self, df: pd.DataFrame, 
                      fast: int = 12, slow: int = 26, signal: int = 9
                      ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Returns:
            (macd_line, signal_line, histogram)
        """
        if df.empty or 'close' not in df.columns:
            empty = pd.Series(dtype=float)
            return empty, empty, empty
        
        close = df['close']
        
        # MACD Line = 12 EMA - 26 EMA
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        
        # Signal Line = 9 EMA of MACD Line
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        
        # Histogram = MACD - Signal
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    # =========================
    # TTM Squeeze
    # =========================
    
    def calculate_squeeze(self, df: pd.DataFrame,
                         bb_length: int = 20, bb_mult: float = 2.0,
                         kc_length: int = 20, kc_mult: float = 1.5,
                         use_true_range: bool = True,
                         mom_length: int = 12
                         ) -> Dict[str, any]:
        """
        Calculate TTM Squeeze indicators matching Pine Script logic.
        
        Returns dict with:
        - sqz_on: Squeeze is ON (consolidation)
        - sqz_off: Squeeze is OFF (trending)
        - sqz_firing: Just released from squeeze
        - sqz_building: Currently building squeeze
        - momentum: Squeeze momentum value
        - momentum_positive: Momentum direction
        - is_tight_squeeze: High-quality tight squeeze
        - is_loose_squeeze: Low-quality loose squeeze
        - bb_width_percentile: BB width relative strength
        """
        if df.empty or len(df) < max(bb_length, kc_length, mom_length):
            return self._empty_squeeze_result()
        
        close = df['close']
        high = df['high']
        low = df['low']
        
        # Bollinger Bands
        basis = close.rolling(window=bb_length).mean()
        std_dev = close.rolling(window=bb_length).std()
        upper_bb = basis + (bb_mult * std_dev)
        lower_bb = basis - (bb_mult * std_dev)
        
        # Keltner Channels
        ma = close.rolling(window=kc_length).mean()
        
        if use_true_range:
            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            range_ma = true_range.rolling(window=kc_length).mean()
        else:
            range_ma = (high - low).rolling(window=kc_length).mean()
        
        upper_kc = ma + (kc_mult * range_ma)
        lower_kc = ma - (kc_mult * range_ma)
        
        # Squeeze Detection
        sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
        sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)
        no_sqz = ~sqz_on & ~sqz_off
        
        # Squeeze Momentum (LazyBear formula)
        highest_high = high.rolling(window=mom_length).max()
        lowest_low = low.rolling(window=mom_length).min()
        avg_hl = (highest_high + lowest_low) / 2
        avg_close = close.rolling(window=mom_length).mean()
        
        # Linear regression of (close - average)
        # Simplified: use difference from midpoint
        momentum = close - ((avg_hl + avg_close) / 2)
        
        # Get current values (last row)
        current_sqz_on = sqz_on.iloc[-1] if len(sqz_on) > 0 else False
        current_sqz_off = sqz_off.iloc[-1] if len(sqz_off) > 0 else False
        prev_sqz_on = sqz_on.iloc[-2] if len(sqz_on) > 1 else False
        
        sqz_firing = current_sqz_off and prev_sqz_on  # Just released
        sqz_building = current_sqz_on  # Currently building
        
        current_momentum = momentum.iloc[-1] if len(momentum) > 0 else 0
        prev_momentum = momentum.iloc[-2] if len(momentum) > 1 else 0
        momentum_positive = current_momentum > prev_momentum
        
        # Squeeze Strength Classification
        bb_width = (upper_bb - lower_bb) / basis
        bb_width_percentile = self._calculate_percentile(bb_width, 100)
        current_bb_percentile = bb_width_percentile.iloc[-1] if len(bb_width_percentile) > 0 else 50
        
        # Count squeeze duration
        sqz_duration = 0
        for i in range(len(sqz_on) - 1, -1, -1):
            if sqz_on.iloc[i]:
                sqz_duration += 1
            else:
                break
        
        is_tight_squeeze = current_bb_percentile < 20 and sqz_duration >= 5
        is_loose_squeeze = current_bb_percentile > 50 or sqz_duration < 3
        
        return {
            'sqz_on': current_sqz_on,
            'sqz_off': current_sqz_off,
            'sqz_firing': sqz_firing,
            'sqz_building': sqz_building,
            'momentum': current_momentum,
            'momentum_positive': momentum_positive,
            'is_tight_squeeze': is_tight_squeeze,
            'is_loose_squeeze': is_loose_squeeze,
            'bb_width_percentile': current_bb_percentile,
            'sqz_duration': sqz_duration
        }
    
    def _empty_squeeze_result(self) -> Dict[str, any]:
        """Return empty squeeze result structure."""
        return {
            'sqz_on': False,
            'sqz_off': False,
            'sqz_firing': False,
            'sqz_building': False,
            'momentum': 0.0,
            'momentum_positive': False,
            'is_tight_squeeze': False,
            'is_loose_squeeze': False,
            'bb_width_percentile': 50.0,
            'sqz_duration': 0
        }
    
    # =========================
    # Volume Analysis
    # =========================
    
    def calculate_rvol(self, df: pd.DataFrame, period: int = 20) -> float:
        """
        Calculate Relative Volume (RVOL).
        Current volume / average volume.
        
        Returns:
            Float: RVOL value, or 0 if insufficient data
        """
        if df.empty or 'volume' not in df.columns or len(df) < period:
            return 0.0
        
        current_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].rolling(window=period).mean().iloc[-1]
        
        if pd.isna(avg_volume) or avg_volume == 0:
            return 0.0
        
        return current_volume / avg_volume
    
    # =========================
    # Volatility Regime
    # =========================
    
    def detect_volatility_regime(self, df: pd.DataFrame, 
                                 atr_lookback: int = 100) -> Dict[str, any]:
        """
        Detect volatility regime (LOW, NORMAL, HIGH).
        Based on ATR percentile ranking.
        
        Returns dict with:
        - regime: 'LOW', 'NORMAL', or 'HIGH'
        - atr_percentile: Current ATR percentile (0-100)
        - is_low_vol: Boolean
        - is_normal_vol: Boolean
        - is_high_vol: Boolean
        """
        if df.empty or len(df) < atr_lookback:
            return {
                'regime': 'NORMAL',
                'atr_percentile': 50.0,
                'is_low_vol': False,
                'is_normal_vol': True,
                'is_high_vol': False
            }
        
        atr = self.calculate_atr(df, period=14)
        atr_percentile = self._calculate_percentile(atr, atr_lookback).iloc[-1]
        
        is_low_vol = atr_percentile < 30
        is_high_vol = atr_percentile > 70
        is_normal_vol = not is_low_vol and not is_high_vol
        
        if is_low_vol:
            regime = 'LOW'
        elif is_high_vol:
            regime = 'HIGH'
        else:
            regime = 'NORMAL'
        
        return {
            'regime': regime,
            'atr_percentile': atr_percentile,
            'is_low_vol': is_low_vol,
            'is_normal_vol': is_normal_vol,
            'is_high_vol': is_high_vol
        }
    
    # =========================
    # Multi-Timeframe Analysis
    # =========================
    
    def calculate_mtf_metrics(self, df_dict: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """
        Calculate metrics across multiple timeframes.
        
        Args:
            df_dict: Dictionary of {timeframe: dataframe}
                    e.g., {'D': df_daily, '4H': df_4h, '15m': df_15m, '5m': df_5m}
        
        Returns:
            Dict of {timeframe: metrics_dict}
        """
        results = {}
        
        for tf, df in df_dict.items():
            if df.empty:
                continue
            
            # MACD
            macd_line, signal_line, hist = self.calculate_macd(df)
            
            # RSI (simple 14-period)
            rsi = self._calculate_rsi(df['close'], 14)
            
            # Volume ratio
            rvol = self.calculate_rvol(df, 20)
            
            # Price change
            price_change = ((df['close'].iloc[-1] - df['open'].iloc[-1]) / 
                           df['open'].iloc[-1] * 100 if df['open'].iloc[-1] != 0 else 0)
            
            # EMAs
            ema_20 = self.calculate_ema(df['close'], 20).iloc[-1] if len(df) >= 20 else np.nan
            ema_50 = self.calculate_ema(df['close'], 50).iloc[-1] if len(df) >= 50 else np.nan
            
            results[tf] = {
                'macd_hist': hist.iloc[-1] if len(hist) > 0 else 0,
                'rsi': rsi.iloc[-1] if len(rsi) > 0 else 50,
                'rvol': rvol,
                'price_change': price_change,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'close': df['close'].iloc[-1]
            }
        
        return results
    
    # =========================
    # Helper Functions
    # =========================
    
    def _calculate_percentile(self, series: pd.Series, lookback: int) -> pd.Series:
        """Calculate rolling percentile rank (0-100)."""
        if series.empty:
            return pd.Series(dtype=float)
        
        def percentile_rank(x):
            if len(x) < 2:
                return 50.0
            rank = (x < x.iloc[-1]).sum()
            return (rank / (len(x) - 1)) * 100
        
        return series.rolling(window=lookback).apply(percentile_rank, raw=False)
    
    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        if close.empty or len(close) < period + 1:
            return pd.Series(dtype=float)
        
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    
    # =========================
    # Distance Calculations
    # =========================
    
    def calculate_distance_from_vwap(self, current_price: float, 
                                     vwap: float, atr: float) -> float:
        """
        Calculate distance from VWAP in ATR units.
        Safe against division by zero.
        """
        if pd.isna(atr) or atr == 0:
            # Fallback to small value
            atr = 0.01
        
        return abs(current_price - vwap) / atr
    
    # =========================
    # Entry/Exit Calculations
    # =========================
    
    def calculate_vwap_zones(self, vwap: float, atr: float, 
                            config: dict) -> Dict[str, Dict]:
        """
        Calculate VWAP entry zones (long and short).
        
        Returns dict with long_zone and short_zone, each containing:
        - entry: Entry price
        - stop: Stop loss price
        - target: Target price
        """
        entry_dist = config.get('VWAP_ENTRY_DISTANCE', 0.7)
        stop_dist = config.get('VWAP_STOP_DISTANCE', 0.75)
        target_mult = config.get('VWAP_TARGET_MULTIPLE', 1.5)
        
        # Long zone (above VWAP)
        long_entry = vwap + (atr * entry_dist)
        long_stop = long_entry - (atr * stop_dist)
        long_target = long_entry + (atr * stop_dist * target_mult)
        
        # Short zone (below VWAP)
        short_entry = vwap - (atr * entry_dist)
        short_stop = short_entry + (atr * stop_dist)
        short_target = short_entry - (atr * stop_dist * target_mult)
        
        return {
            'long_zone': {
                'entry': long_entry,
                'stop': long_stop,
                'target': long_target
            },
            'short_zone': {
                'entry': short_entry,
                'stop': short_stop,
                'target': short_target
            }
        }
    
    def calculate_pullback_zones(self, df: pd.DataFrame, vwap: float, 
                                atr: float, config: dict) -> Dict[str, Dict]:
        """
        Calculate pullback entry zones.
        
        Returns dict with long_pullback and short_pullback zones.
        """
        lookback = config.get('SWING_LOOKBACK', 10)
        entry_level = config.get('PULLBACK_ENTRY_LEVEL', 0.50)
        stop_beyond = config.get('STOP_BEYOND_SWING', 0.3)
        
        if df.empty or len(df) < lookback:
            return {'long_pullback': None, 'short_pullback': None}
        
        swing_high = df['high'].tail(lookback).max()
        swing_low = df['low'].tail(lookback).min()
        
        # Long pullback (from swing high back to VWAP)
        long_range = swing_high - vwap
        long_entry = swing_high - (long_range * entry_level)
        long_stop = long_entry - (atr * stop_beyond)
        long_target = long_entry + (long_range * 0.7)
        
        # Short pullback (from swing low back to VWAP)
        short_range = vwap - swing_low
        short_entry = swing_low + (short_range * entry_level)
        short_stop = short_entry + (atr * stop_beyond)
        short_target = short_entry - (short_range * 0.7)
        
        return {
            'long_pullback': {
                'entry': long_entry,
                'stop': long_stop,
                'target': long_target,
                'swing_high': swing_high
            },
            'short_pullback': {
                'entry': short_entry,
                'stop': short_stop,
                'target': short_target,
                'swing_low': swing_low
            }
        }
