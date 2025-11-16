"""
Trade Logger
Comprehensive logging system for paper trading.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class TradeLogger:
    """Logs all paper trades with complete context."""
    
    def __init__(self, log_dir: str = "logs/ai_paper_trading"):
        """
        Initialize trade logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Daily log files
        self.date_str = datetime.now().strftime("%Y%m%d")
        self.trades_file = self.log_dir / f"trades_{self.date_str}.csv"
        self.signals_file = self.log_dir / f"signals_{self.date_str}.csv"
        self.performance_file = self.log_dir / f"performance_{self.date_str}.json"
        
        # Initialize CSV files with headers
        self._init_csv_files()
        
        print(f"[LOGGER] Trade logs: {self.trades_file}")
        print(f"[LOGGER] Signal logs: {self.signals_file}")
    
    def _init_csv_files(self):
        """Initialize CSV files with headers."""
        
        # Trades CSV
        if not self.trades_file.exists():
            with open(self.trades_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'trade_id', 'scenario', 'symbol', 
                    'entry_time', 'entry_price', 'size',
                    'exit_time', 'exit_price', 'exit_reason',
                    'pnl_dollar', 'pnl_percent', 'rr_achieved', 'hold_minutes',
                    'indicator_prob', 'indicator_quality', 'squeeze_status', 'vol_regime',
                    'ai_confidence', 'ai_reasoning',
                    'l2_imbalance', 'l2_spread',
                    'stop_price', 'target_price',
                    'win_loss', 'notes'
                ])
        
        # Signals CSV (all signals, not just trades)
        if not self.signals_file.exists():
            with open(self.signals_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'scenario', 'symbol', 'action',
                    'current_price', 'indicator_prob', 'squeeze_status',
                    'ai_confidence', 'ai_action', 'reasoning'
                ])
    
    def log_trade_entry(self, trade_data: Dict[str, Any]) -> str:
        """
        Log a trade entry.
        
        Args:
            trade_data: Dict with trade information
            
        Returns:
            trade_id
        """
        trade_id = f"{trade_data['scenario']}_{trade_data['symbol']}_{datetime.now():%Y%m%d_%H%M%S}"
        
        # Store for exit logging
        self._pending_trades = getattr(self, '_pending_trades', {})
        self._pending_trades[trade_id] = {
            **trade_data,
            'trade_id': trade_id,
            'entry_time': datetime.now().isoformat()
        }
        
        print(f"[LOGGER] Trade entry logged: {trade_id}")
        return trade_id
    
    def log_trade_exit(self, trade_id: str, exit_data: Dict[str, Any]):
        """
        Log a trade exit and write to CSV.
        
        Args:
            trade_id: Trade identifier
            exit_data: Exit information
        """
        self._pending_trades = getattr(self, '_pending_trades', {})
        
        if trade_id not in self._pending_trades:
            print(f"[WARN] Trade {trade_id} not found in pending trades")
            return
        
        entry_data = self._pending_trades.pop(trade_id)
        
        # Calculate metrics
        entry_time = datetime.fromisoformat(entry_data['entry_time'])
        exit_time = datetime.now()
        hold_minutes = (exit_time - entry_time).total_seconds() / 60
        
        entry_price = entry_data['entry_price']
        exit_price = exit_data['exit_price']
        size = entry_data['size']
        
        # P&L calculation
        if entry_data.get('direction', 'LONG') == 'LONG':
            pnl_dollar = (exit_price - entry_price) * size
        else:
            pnl_dollar = (entry_price - exit_price) * size
        
        pnl_percent = (pnl_dollar / (entry_price * size)) * 100 if entry_price > 0 else 0
        
        # R:R calculation
        stop_distance = abs(entry_price - entry_data.get('stop_price', entry_price))
        target_distance = abs(entry_data.get('target_price', entry_price) - entry_price)
        exit_distance = abs(exit_price - entry_price)
        
        if stop_distance > 0:
            rr_achieved = exit_distance / stop_distance
        else:
            rr_achieved = 0
        
        win_loss = 'WIN' if pnl_dollar > 0 else 'LOSS' if pnl_dollar < 0 else 'BREAKEVEN'
        
        # Write to CSV
        with open(self.trades_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade_id,
                entry_data['scenario'],
                entry_data['symbol'],
                entry_data['entry_time'],
                entry_price,
                size,
                exit_time.isoformat(),
                exit_price,
                exit_data.get('exit_reason', 'UNKNOWN'),
                round(pnl_dollar, 2),
                round(pnl_percent, 2),
                round(rr_achieved, 2),
                round(hold_minutes, 1),
                entry_data.get('indicator_prob', 0),
                entry_data.get('indicator_quality', 'UNKNOWN'),
                entry_data.get('squeeze_status', 'UNKNOWN'),
                entry_data.get('vol_regime', 'UNKNOWN'),
                entry_data.get('ai_confidence', 0),
                entry_data.get('ai_reasoning', ''),
                entry_data.get('l2_imbalance', 0),
                entry_data.get('l2_spread', 0),
                entry_data.get('stop_price', 0),
                entry_data.get('target_price', 0),
                win_loss,
                exit_data.get('notes', '')
            ])
        
        print(f"[LOGGER] Trade exit logged: {trade_id} | P&L: ${pnl_dollar:.2f} ({pnl_percent:.2f}%) | {win_loss}")
    
    def log_signal(self, signal_data: Dict[str, Any]):
        """
        Log an AI signal (whether traded or not).
        
        Args:
            signal_data: Signal information
        """
        with open(self.signals_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                signal_data.get('scenario', 'UNKNOWN'),
                signal_data.get('symbol', 'UNKNOWN'),
                signal_data.get('action', 'WAIT'),
                signal_data.get('current_price', 0),
                signal_data.get('indicator_prob', 0),
                signal_data.get('squeeze_status', 'UNKNOWN'),
                signal_data.get('ai_confidence', 0),
                signal_data.get('ai_action', 'WAIT'),
                signal_data.get('reasoning', '')
            ])
    
    def get_trade_history(self, scenario: Optional[str] = None) -> List[Dict]:
        """
        Get trade history from CSV.
        
        Args:
            scenario: Optional filter by scenario
            
        Returns:
            List of trade dicts
        """
        if not self.trades_file.exists():
            return []
        
        trades = []
        with open(self.trades_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if scenario is None or row['scenario'] == scenario:
                    trades.append(row)
        
        return trades
    
    def calculate_performance_stats(self, scenario: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate performance statistics.
        
        Args:
            scenario: Optional filter by scenario
            
        Returns:
            Performance stats dict
        """
        trades = self.get_trade_history(scenario)
        
        if not trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'avg_rr': 0,
                'avg_hold_minutes': 0
            }
        
        wins = [t for t in trades if t['win_loss'] == 'WIN']
        losses = [t for t in trades if t['win_loss'] == 'LOSS']
        
        total_pnl = sum(float(t['pnl_dollar']) for t in trades)
        avg_pnl = total_pnl / len(trades) if trades else 0
        
        avg_rr = sum(float(t['rr_achieved']) for t in trades) / len(trades) if trades else 0
        avg_hold = sum(float(t['hold_minutes']) for t in trades) / len(trades) if trades else 0
        
        return {
            'total_trades': len(trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(trades) * 100 if trades else 0,
            'total_pnl': round(total_pnl, 2),
            'avg_pnl': round(avg_pnl, 2),
            'avg_rr': round(avg_rr, 2),
            'avg_hold_minutes': round(avg_hold, 1),
            'best_trade': max(trades, key=lambda t: float(t['pnl_dollar']))['trade_id'] if trades else None,
            'worst_trade': min(trades, key=lambda t: float(t['pnl_dollar']))['trade_id'] if trades else None
        }
    
    def export_performance_report(self):
        """Export performance report to JSON."""
        report = {
            'date': self.date_str,
            'generated': datetime.now().isoformat(),
            'scenarios': {}
        }
        
        for scenario in ['aggressive', 'moderate', 'conservative']:
            report['scenarios'][scenario] = self.calculate_performance_stats(scenario)
        
        report['overall'] = self.calculate_performance_stats()
        
        with open(self.performance_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[LOGGER] Performance report saved: {self.performance_file}")
        return report


if __name__ == "__main__":
    # Quick test
    logger = TradeLogger()
    
    # Test trade entry
    trade_data = {
        'scenario': 'moderate',
        'symbol': 'AAPL',
        'entry_price': 150.30,
        'size': 100,
        'stop_price': 149.00,
        'target_price': 152.00,
        'indicator_prob': 68,
        'indicator_quality': 'MEDIUM',
        'squeeze_status': 'FIRING',
        'vol_regime': 'NORMAL',
        'ai_confidence': 72,
        'ai_reasoning': 'Strong setup with L2 confirmation',
        'l2_imbalance': 15.2,
        'l2_spread': 0.02
    }
    
    trade_id = logger.log_trade_entry(trade_data)
    
    # Simulate exit
    import time
    time.sleep(1)
    
    exit_data = {
        'exit_price': 151.50,
        'exit_reason': 'TARGET',
        'notes': 'Clean winner'
    }
    
    logger.log_trade_exit(trade_id, exit_data)
    
    # Get stats
    stats = logger.calculate_performance_stats()
    print(f"\nPerformance Stats:")
    print(json.dumps(stats, indent=2))
