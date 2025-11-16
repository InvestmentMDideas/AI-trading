"""
IBKR Data Feed
Manages real-time and historical data from Interactive Brokers.
"""

import time
from datetime import datetime, timedelta
from threading import Thread, Lock
from typing import Dict, List, Optional, Tuple  # ← FIXED: Added Tuple
import pandas as pd

from ib_insync import IB, Stock, util, BarDataList


class IBKRDataFeed:
    """IBKR data feed manager."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 7497, client_id: int = 3):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
        self.lock = Lock()
        self.bars_cache = {}
        self.current_prices = {}
        self.market_depth = {}
        
    def connect(self, timeout: int = 10) -> bool:
        """Connect to Interactive Brokers."""
        try:
            if self.connected:
                return True
            
            print(f"[IBKR] Connecting to {self.host}:{self.port}...")
            self.ib.connect(self.host, self.port, clientId=self.client_id, timeout=timeout)
            self.connected = True
            print("[IBKR] ✅ Connected!")
            return True
        except Exception as e:
            print(f"[ERROR] IBKR connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from IBKR."""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            print("[IBKR] Disconnected")
    
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected and self.ib.isConnected()
    
    def get_contract(self, symbol: str, exchange: str = "SMART", currency: str = "USD") -> Stock:
        """Create stock contract."""
        return Stock(symbol, exchange, currency)
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price."""
        if not self.is_connected():
            return None
        
        try:
            contract = self.get_contract(symbol)
            ticker = self.ib.reqMktData(contract, '', False, False)
            self.ib.sleep(0.5)
            
            price = ticker.last
            if pd.isna(price) or price <= 0:
                price = ticker.close
            if pd.isna(price) or price <= 0:
                if ticker.bid > 0 and ticker.ask > 0:
                    price = (ticker.bid + ticker.ask) / 2
            
            self.ib.cancelMktData(contract)
            
            if price and price > 0:
                self.current_prices[symbol] = price
                return float(price)
            return None
        except Exception as e:
            print(f"[ERROR] Failed to get price for {symbol}: {e}")
            return None
    
    def _get_historical_bars(self, symbol: str, duration: str, bar_size: str, 
                            what_to_show: str, use_rth: bool) -> pd.DataFrame:
        """Internal method to fetch historical bars."""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            contract = self.get_contract(symbol)
            bars = self.ib.reqHistoricalData(
                contract, endDateTime='', durationStr=duration,
                barSizeSetting=bar_size, whatToShow=what_to_show,
                useRTH=use_rth, formatDate=1, keepUpToDate=False
            )
            
            if not bars:
                return pd.DataFrame()
            
            df = util.df(bars)
            if df.empty:
                return pd.DataFrame()
            
            df = df.rename(columns={'date': 'timestamp'})
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            if not all(col in df.columns for col in required_cols):
                return pd.DataFrame()
            
            return df[required_cols].sort_values('timestamp').reset_index(drop=True)
        except Exception as e:
            print(f"[ERROR] Failed to fetch {bar_size} bars for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_1min_bars(self, symbol: str, duration: str = "1 D", use_rth: bool = False) -> pd.DataFrame:
        """Get 1-minute bars."""
        return self._get_historical_bars(symbol, duration, "1 min", "TRADES", use_rth)
    
    def get_daily_bars(self, symbol: str, duration: str = "90 D") -> pd.DataFrame:
        """Get daily bars."""
        return self._get_historical_bars(symbol, duration, "1 day", "TRADES", True)
    
    def get_4h_bars(self, symbol: str, duration: str = "30 D") -> pd.DataFrame:
        """Get 4-hour bars."""
        return self._get_historical_bars(symbol, duration, "4 hours", "TRADES", False)
    
    def get_15min_bars(self, symbol: str, duration: str = "7 D") -> pd.DataFrame:
        """Get 15-minute bars."""
        return self._get_historical_bars(symbol, duration, "15 mins", "TRADES", False)
    
    def get_5min_bars(self, symbol: str, duration: str = "2 D") -> pd.DataFrame:
        """Get 5-minute bars."""
        return self._get_historical_bars(symbol, duration, "5 mins", "TRADES", False)
    
    def get_all_timeframes(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Get data for all timeframes."""
        print(f"[IBKR] Fetching data for {symbol}...")
        data = {}
        data['1min'] = self.get_1min_bars(symbol, duration="1 D")
        data['D'] = self.get_daily_bars(symbol, duration="90 D")
        data['4H'] = self.get_4h_bars(symbol, duration="30 D")
        data['15m'] = self.get_15min_bars(symbol, duration="7 D")
        data['5m'] = self.get_5min_bars(symbol, duration="2 D")
        data = {k: v for k, v in data.items() if not v.empty}
        print(f"[IBKR] ✅ Fetched {len(data)} timeframes")
        return data
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def create_data_feed(config) -> IBKRDataFeed:
    """Create and connect IBKR data feed from config."""
    feed = IBKRDataFeed(config.IBKR_HOST, config.IBKR_PORT, 3)
    if feed.connect():
        return feed
    else:
        raise ConnectionError("Failed to connect to IBKR")