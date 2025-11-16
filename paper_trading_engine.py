"""
Paper Trading Engine
Runs 3 scenarios simultaneously in background.
"""

import time
from datetime import datetime
from threading import Thread, Lock
from typing import Dict, Any, Optional
from collections import defaultdict

from trade_logger import TradeLogger
import config_ai as config


class PaperPosition:
    """Represents a paper trading position."""
    
    def __init__(self, symbol: str, entry_price: float, size: int, 
                 stop: float, target: float, direction: str = 'LONG',
                 metadata: Dict = None):
        self.symbol = symbol
        self.entry_price = entry_price
        self.size = size
        self.stop = stop
        self.target = target
        self.direction = direction
        self.entry_time = datetime.now()
        self.metadata = metadata or {}
        self.trade_id = None
    
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate current P&L."""
        if self.direction == 'LONG':
            return (current_price - self.entry_price) * self.size
        else:
            return (self.entry_price - current_price) * self.size
    
    def check_exit(self, current_price: float, current_high: float, 
                   current_low: float) -> Optional[str]:
        """
        Check if position should be exited.
        
        Returns:
            Exit reason or None
        """
        if self.direction == 'LONG':
            if current_low <= self.stop:
                return 'STOP_LOSS'
            if current_high >= self.target:
                return 'TARGET'
        else:
            if current_high >= self.stop:
                return 'STOP_LOSS'
            if current_low <= self.target:
                return 'TARGET'
        
        return None


class ScenarioTrader:
    """Manages one trading scenario."""
    
    def __init__(self, name: str, config: Dict[str, Any], logger: TradeLogger):
        self.name = name
        self.config = config
        self.logger = logger
        
        # Account
        self.starting_equity = config.get('starting_equity', 15000)
        self.equity = self.starting_equity
        self.cash = self.equity
        
        # Position tracking
        self.position: Optional[PaperPosition] = None
        self.pending_order = None
        
        # Stats
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        
        print(f"[{self.name.upper()}] Initialized with ${self.starting_equity:,.2f}")
    
    def process_signal(self, ai_decision: Dict, indicator_data: Dict, 
                      current_price: float, l2_data: Dict = None):
        """
        Process AI decision and potentially enter trade.
        
        Args:
            ai_decision: AI scenario decision
            indicator_data: Indicator analysis
            current_price: Current market price
            l2_data: Optional Level 2 data
        """
        # Log the signal
        self.logger.log_signal({
            'scenario': self.name,
            'symbol': indicator_data.get('symbol', 'UNKNOWN'),
            'action': ai_decision.get('action', 'WAIT'),
            'current_price': current_price,
            'indicator_prob': indicator_data.get('probability', 0),
            'squeeze_status': indicator_data.get('squeeze_status', 'UNKNOWN'),
            'ai_confidence': ai_decision.get('confidence', 0),
            'ai_action': ai_decision.get('action', 'WAIT'),
            'reasoning': ai_decision.get('reasoning', '')
        })
        
        # Skip if already in position
        if self.position:
            return
        
        action = ai_decision.get('action', 'WAIT')
        
        # Check entry conditions based on scenario type
        if self.name == 'aggressive':
            # Enter immediately if signal appears
            if action in ['ENTER_LONG', 'ENTER_SHORT']:
                self._enter_position(ai_decision, indicator_data, current_price, l2_data)
        
        elif self.name == 'moderate':
            # Wait for zone entry or enter immediately
            if action == 'ENTER_LONG':
                self._enter_position(ai_decision, indicator_data, current_price, l2_data)
            elif action == 'ENTER_AT_ZONE':
                # Check if we're at the zone
                entry_price = ai_decision.get('entry', current_price)
                if abs(current_price - entry_price) / entry_price < 0.002:  # Within 0.2%
                    self._enter_position(ai_decision, indicator_data, current_price, l2_data)
                else:
                    self.pending_order = {
                        'type': 'LIMIT',
                        'price': entry_price,
                        'decision': ai_decision,
                        'indicator_data': indicator_data,
                        'l2_data': l2_data
                    }
        
        elif self.name == 'conservative':
            # Only high-quality setups
            if action in ['ENTER_LONG', 'ENTER_SHORT']:
                prob = indicator_data.get('probability', 0)
                if prob >= config.CONSERVATIVE_MIN_PROB:
                    self._enter_position(ai_decision, indicator_data, current_price, l2_data)
    
    def _enter_position(self, ai_decision: Dict, indicator_data: Dict, 
                       price: float, l2_data: Dict = None):
        """Enter a position."""
        action = ai_decision.get('action', 'WAIT')
        
        if 'LONG' in action:
            direction = 'LONG'
        elif 'SHORT' in action:
            direction = 'SHORT'
        else:
            return
        
        size = ai_decision.get('size', 0)
        if size == 0:
            return
        
        stop = ai_decision.get('stop', price * 0.98)
        target = ai_decision.get('target', price * 1.02)
        
        # Check if we have enough cash
        cost = price * size
        if cost > self.cash:
            print(f"[{self.name.upper()}] Insufficient cash: ${self.cash:.2f} < ${cost:.2f}")
            return
        
        # Create position
        self.position = PaperPosition(
            symbol=indicator_data.get('symbol', 'UNKNOWN'),
            entry_price=price,
            size=size,
            stop=stop,
            target=target,
            direction=direction,
            metadata={
                'indicator_prob': indicator_data.get('probability', 0),
                'indicator_quality': indicator_data.get('quality', 'UNKNOWN'),
                'squeeze_status': indicator_data.get('squeeze_status', 'UNKNOWN'),
                'vol_regime': indicator_data.get('vol_regime', {}).get('regime', 'UNKNOWN'),
                'ai_confidence': ai_decision.get('confidence', 0),
                'ai_reasoning': ai_decision.get('reasoning', ''),
                'l2_imbalance': l2_data.get('imbalance', 0) if l2_data else 0,
                'l2_spread': l2_data.get('spread', 0) if l2_data else 0
            }
        )
        
        # Update cash
        self.cash -= cost
        
        # Log entry
        trade_data = {
            'scenario': self.name,
            'symbol': self.position.symbol,
            'entry_price': price,
            'size': size,
            'stop_price': stop,
            'target_price': target,
            'direction': direction,
            **self.position.metadata
        }
        
        self.position.trade_id = self.logger.log_trade_entry(trade_data)
        self.total_trades += 1
        
        print(f"[{self.name.upper()}] ENTRY: {direction} {size} {self.position.symbol} @ ${price:.2f} | Stop: ${stop:.2f} | Target: ${target:.2f}")
    
    def update_position(self, current_price: float, high: float, low: float):
        """Update position and check for exits."""
        if not self.position:
            # Check pending orders
            if self.pending_order:
                if self.pending_order['type'] == 'LIMIT':
                    order_price = self.pending_order['price']
                    # Check if price touched our limit
                    if low <= order_price <= high:
                        print(f"[{self.name.upper()}] Limit order filled @ ${order_price:.2f}")
                        self._enter_position(
                            self.pending_order['decision'],
                            self.pending_order['indicator_data'],
                            order_price,
                            self.pending_order.get('l2_data')
                        )
                        self.pending_order = None
            return
        
        # Check for exit
        exit_reason = self.position.check_exit(current_price, high, low)
        
        if exit_reason:
            # Determine exit price
            if exit_reason == 'STOP_LOSS':
                exit_price = self.position.stop
            elif exit_reason == 'TARGET':
                exit_price = self.position.target
            else:
                exit_price = current_price
            
            # Exit position
            self._exit_position(exit_price, exit_reason)
    
    def _exit_position(self, price: float, reason: str):
        """Exit current position."""
        if not self.position:
            return
        
        # Calculate P&L
        pnl = self.position.calculate_pnl(price)
        
        # Update cash and equity
        proceeds = price * self.position.size
        self.cash += proceeds
        self.equity = self.cash  # In paper trading, equity = cash when no position
        
        if self.position:
            self.equity += self.position.calculate_pnl(price)
        
        # Track win/loss
        if pnl > 0:
            self.wins += 1
        elif pnl < 0:
            self.losses += 1
        
        # Log exit
        exit_data = {
            'exit_price': price,
            'exit_reason': reason,
            'notes': f'Equity: ${self.equity:.2f}'
        }
        
        self.logger.log_trade_exit(self.position.trade_id, exit_data)
        
        print(f"[{self.name.upper()}] EXIT: {self.position.symbol} @ ${price:.2f} | {reason} | P&L: ${pnl:.2f} | Equity: ${self.equity:.2f}")
        
        self.position = None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current scenario statistics."""
        win_rate = (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            'name': self.name,
            'equity': round(self.equity, 2),
            'cash': round(self.cash, 2),
            'starting_equity': self.starting_equity,
            'pnl': round(self.equity - self.starting_equity, 2),
            'pnl_percent': round((self.equity - self.starting_equity) / self.starting_equity * 100, 2),
            'total_trades': self.total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': round(win_rate, 1),
            'in_position': self.position is not None,
            'current_position': {
                'symbol': self.position.symbol,
                'direction': self.position.direction,
                'entry_price': self.position.entry_price,
                'size': self.position.size,
                'unrealized_pnl': round(self.position.calculate_pnl(0), 2) if self.position else 0
            } if self.position else None
        }


class PaperTradingEngine:
    """Main paper trading engine managing all 3 scenarios."""
    
    def __init__(self):
        self.logger = TradeLogger(config.PAPER_TRADE_LOG_DIR)
        
        # Create 3 scenario traders
        self.scenarios = {
            'aggressive': ScenarioTrader(
                'aggressive',
                {
                    'starting_equity': config.PAPER_EQUITY_PER_SCENARIO,
                    'min_prob': config.AGGRESSIVE_MIN_PROB,
                    'risk_percent': config.AGGRESSIVE_RISK
                },
                self.logger
            ),
            'moderate': ScenarioTrader(
                'moderate',
                {
                    'starting_equity': config.PAPER_EQUITY_PER_SCENARIO,
                    'min_prob': config.MODERATE_MIN_PROB,
                    'risk_percent': config.MODERATE_RISK
                },
                self.logger
            ),
            'conservative': ScenarioTrader(
                'conservative',
                {
                    'starting_equity': config.PAPER_EQUITY_PER_SCENARIO,
                    'min_prob': config.CONSERVATIVE_MIN_PROB,
                    'risk_percent': config.CONSERVATIVE_RISK
                },
                self.logger
            )
        }
        
        self.running = False
        self.lock = Lock()
        
        print("[PAPER TRADING] Engine initialized with 3 scenarios")
    
    def process_ai_analysis(self, ai_result: Dict, indicator_data: Dict, 
                           current_price: float, current_high: float,
                           current_low: float, l2_data: Dict = None):
        """
        Process AI analysis and update all scenarios.
        
        Args:
            ai_result: Complete AI analysis
            indicator_data: Indicator analysis
            current_price: Current price
            current_high: Current bar high
            current_low: Current bar low
            l2_data: Optional Level 2 data
        """
        with self.lock:
            # Update existing positions
            for scenario in self.scenarios.values():
                scenario.update_position(current_price, current_high, current_low)
            
            # Process new signals
            if 'scenarios' in ai_result:
                for name, decision in ai_result['scenarios'].items():
                    if name in self.scenarios:
                        self.scenarios[name].process_signal(
                            decision, indicator_data, current_price, l2_data
                        )
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all scenarios."""
        with self.lock:
            stats = {
                scenario_name: scenario.get_stats()
                for scenario_name, scenario in self.scenarios.items()
            }
            
            # Overall stats
            total_equity = sum(s['equity'] for s in stats.values())
            total_starting = sum(s['starting_equity'] for s in stats.values())
            total_pnl = total_equity - total_starting
            
            stats['overall'] = {
                'total_equity': round(total_equity, 2),
                'total_starting': round(total_starting, 2),
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percent': round(total_pnl / total_starting * 100, 2) if total_starting > 0 else 0
            }
            
            return stats
    
    def export_performance_report(self):
        """Export performance report."""
        return self.logger.export_performance_report()


if __name__ == "__main__":
    # Quick test
    engine = PaperTradingEngine()
    
    # Simulate AI analysis
    mock_indicator = {
        'symbol': 'AAPL',
        'probability': 68,
        'quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': {'regime': 'NORMAL'}
    }
    
    mock_ai = {
        'scenarios': {
            'aggressive': {
                'action': 'ENTER_LONG',
                'entry': 150.30,
                'stop': 149.00,
                'target': 152.00,
                'size': 120,
                'confidence': 65,
                'reasoning': 'Squeeze firing, enter now'
            },
            'moderate': {
                'action': 'ENTER_AT_ZONE',
                'entry': 150.00,
                'stop': 148.50,
                'target': 152.00,
                'size': 100,
                'confidence': 72,
                'reasoning': 'Wait for VWAP zone'
            },
            'conservative': {
                'action': 'WAIT',
                'reasoning': 'Prefer 70%+ probability'
            }
        }
    }
    
    # Process
    engine.process_ai_analysis(mock_ai, mock_indicator, 150.30, 150.50, 150.10)
    
    # Get stats
    import json
    print("\nCurrent Stats:")
    print(json.dumps(engine.get_all_stats(), indent=2))
