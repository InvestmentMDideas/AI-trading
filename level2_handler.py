"""
Level 2 Order Book Handler
Manages real-time market depth data from IBKR.
"""

import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import pandas as pd
from ib_insync import IB, Stock


class Level2Handler:
    """Handles Level 2 market depth data."""
    
    def __init__(self, ib: IB):
        """
        Initialize Level 2 handler.
        
        Args:
            ib: Connected IB instance
        """
        self.ib = ib
        self.current_symbol = None
        self.market_depth = {'bids': [], 'asks': []}
        self.last_update = 0
        
    def subscribe_market_depth(self, symbol: str, rows: int = 10):
        """
        Subscribe to Level 2 market depth.
        
        Args:
            symbol: Stock symbol
            rows: Number of depth rows (default 10)
        """
        if symbol == self.current_symbol:
            return  # Already subscribed
        
        # Unsubscribe from previous symbol
        if self.current_symbol:
            self.unsubscribe_market_depth()
        
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)
            
            # Request market depth
            self.ib.reqMktDepth(contract, numRows=rows)
            self.current_symbol = symbol
            self.last_update = time.time()
            
            print(f"[L2] ✅ Subscribed to {symbol} market depth")
            
        except Exception as e:
            print(f"[ERROR] Failed to subscribe to market depth for {symbol}: {e}")
    
    def unsubscribe_market_depth(self):
        """Unsubscribe from current market depth."""
        if self.current_symbol:
            try:
                contract = Stock(self.current_symbol, 'SMART', 'USD')
                self.ib.cancelMktDepth(contract)
                print(f"[L2] Unsubscribed from {self.current_symbol}")
            except:
                pass
            self.current_symbol = None
            self.market_depth = {'bids': [], 'asks': []}
    
    def get_market_depth(self) -> Dict[str, List]:
        """
        Get current market depth data.
        
        Returns:
            Dict with 'bids' and 'asks' lists
        """
        if not self.current_symbol or not self.ib.isConnected():
            return {'bids': [], 'asks': []}
        
        try:
            # Get market depth from IB
            contract = Stock(self.current_symbol, 'SMART', 'USD')
            ticker = self.ib.ticker(contract)
            
            # Extract bids and asks
            bids = []
            asks = []
            
            if hasattr(ticker, 'domBids') and ticker.domBids:
                for level in ticker.domBids:
                    if level.price > 0 and level.size > 0:
                        bids.append({
                            'price': level.price,
                            'size': level.size,
                            'marketMaker': getattr(level, 'marketMaker', '')
                        })
            
            if hasattr(ticker, 'domAsks') and ticker.domAsks:
                for level in ticker.domAsks:
                    if level.price > 0 and level.size > 0:
                        asks.append({
                            'price': level.price,
                            'size': level.size,
                            'marketMaker': getattr(level, 'marketMaker', '')
                        })
            
            # Sort bids descending, asks ascending
            bids.sort(key=lambda x: x['price'], reverse=True)
            asks.sort(key=lambda x: x['price'])
            
            self.market_depth = {'bids': bids, 'asks': asks}
            self.last_update = time.time()
            
            return self.market_depth
            
        except Exception as e:
            print(f"[WARN] Failed to get market depth: {e}")
            return {'bids': [], 'asks': []}
    
    def calculate_imbalance(self) -> float:
        """
        Calculate bid/ask imbalance ratio.
        
        Returns:
            Imbalance percentage (-100 to +100)
            Positive = more bids (bullish)
            Negative = more asks (bearish)
        """
        depth = self.get_market_depth()
        
        if not depth['bids'] or not depth['asks']:
            return 0.0
        
        total_bid_size = sum(b['size'] for b in depth['bids'])
        total_ask_size = sum(a['size'] for a in depth['asks'])
        
        if total_bid_size + total_ask_size == 0:
            return 0.0
        
        imbalance = ((total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)) * 100
        return round(imbalance, 2)
    
    def get_depth_at_price(self, price: float, side: str = 'both') -> Dict:
        """
        Get order book depth at a specific price level.
        
        Args:
            price: Price level to check
            side: 'bid', 'ask', or 'both'
            
        Returns:
            Dict with bid/ask sizes at that level
        """
        depth = self.get_market_depth()
        
        result = {'bid_size': 0, 'ask_size': 0}
        
        if side in ['bid', 'both']:
            for bid in depth['bids']:
                if abs(bid['price'] - price) < 0.01:
                    result['bid_size'] = bid['size']
                    break
        
        if side in ['ask', 'both']:
            for ask in depth['asks']:
                if abs(ask['price'] - price) < 0.01:
                    result['ask_size'] = ask['size']
                    break
        
        return result
    
    def get_support_resistance_levels(self, num_levels: int = 3) -> Dict:
        """
        Identify key support/resistance from order book.
        
        Args:
            num_levels: Number of levels to identify
            
        Returns:
            Dict with support and resistance prices
        """
        depth = self.get_market_depth()
        
        if not depth['bids'] or not depth['asks']:
            return {'support': [], 'resistance': []}
        
        # Sort by size to find largest levels
        support_levels = sorted(depth['bids'], key=lambda x: x['size'], reverse=True)[:num_levels]
        resistance_levels = sorted(depth['asks'], key=lambda x: x['size'], reverse=True)[:num_levels]
        
        return {
            'support': [level['price'] for level in support_levels],
            'resistance': [level['price'] for level in resistance_levels]
        }
    
    def format_for_display(self) -> pd.DataFrame:
        """
        Format market depth for dashboard display.
        
        Returns:
            DataFrame with bid/ask ladder
        """
        depth = self.get_market_depth()
        
        if not depth['bids'] and not depth['asks']:
            return pd.DataFrame()
        
        # Combine bids and asks
        max_rows = max(len(depth['bids']), len(depth['asks']))
        
        rows = []
        for i in range(max_rows):
            row = {}
            
            # Bid side
            if i < len(depth['bids']):
                bid = depth['bids'][i]
                row['Bid Size'] = bid['size']
                row['Bid Price'] = f"${bid['price']:.2f}"
            else:
                row['Bid Size'] = ''
                row['Bid Price'] = ''
            
            # Ask side
            if i < len(depth['asks']):
                ask = depth['asks'][i]
                row['Ask Price'] = f"${ask['price']:.2f}"
                row['Ask Size'] = ask['size']
            else:
                row['Ask Price'] = ''
                row['Ask Size'] = ''
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def get_stats(self) -> Dict:
        """Get Level 2 statistics."""
        depth = self.get_market_depth()
        
        if not depth['bids'] or not depth['asks']:
            return {
                'symbol': self.current_symbol or 'N/A',
                'bid_levels': 0,
                'ask_levels': 0,
                'spread': 0.0,
                'imbalance': 0.0,
                'last_update': 0
            }
        
        best_bid = depth['bids'][0]['price'] if depth['bids'] else 0
        best_ask = depth['asks'][0]['price'] if depth['asks'] else 0
        spread = best_ask - best_bid if best_bid > 0 and best_ask > 0 else 0
        
        return {
            'symbol': self.current_symbol,
            'bid_levels': len(depth['bids']),
            'ask_levels': len(depth['asks']),
            'spread': round(spread, 2),
            'imbalance': self.calculate_imbalance(),
            'best_bid': best_bid,
            'best_ask': best_ask,
            'last_update': self.last_update
        }


if __name__ == "__main__":
    # Quick test
    from ibkr_data_feed import IBKRDataFeed
    
    with IBKRDataFeed() as feed:
        l2 = Level2Handler(feed.ib)
        l2.subscribe_market_depth('AAPL')
        
        time.sleep(2)  # Wait for data
        
        stats = l2.get_stats()
        print(f"\nLevel 2 Stats:")
        print(f"  Symbol: {stats['symbol']}")
        print(f"  Spread: ${stats['spread']:.2f}")
        print(f"  Imbalance: {stats['imbalance']:.1f}%")
        print(f"  Bid Levels: {stats['bid_levels']}")
        print(f"  Ask Levels: {stats['ask_levels']}")
        
        df = l2.format_for_display()
        print(f"\nOrder Book:")
        print(df.head())
