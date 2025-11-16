"""
Unified AI Trading Dashboard - FULLY INTEGRATED
Runs ALL 4 PHASES together:
  Phase 1: Indicator Engine (145-point scoring)
  Phase 2: AI Analyst (Multi-stage reasoning)
  Phase 3: Real-time Dashboard (This file)
  Phase 4: Paper Trading Engine (3 scenarios)
"""

import time
from datetime import datetime
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
from threading import Thread, Lock

# Import our components
from indicator_engine import IndicatorEngine
from ai_analyst import AIAnalyst
from ibkr_data_feed import IBKRDataFeed
from level2_handler import Level2Handler
from layout_components import *
import config_ai as config

# ========================================
# PHASE 4 INTEGRATION: Import Paper Trading
# ========================================
try:
    from paper_trading_engine import PaperTradingEngine
    PAPER_TRADING_AVAILABLE = True
    print("[DASHBOARD] ✅ Paper Trading Engine available")
except ImportError:
    PAPER_TRADING_AVAILABLE = False
    print("[DASHBOARD] ⚠️  Paper Trading Engine not found (optional)")


class UnifiedDashboard:
    """Main dashboard application - FULLY INTEGRATED."""
    
    def __init__(self, port: int = 8052, enable_paper_trading: bool = True):
        """
        Initialize dashboard.
        
        Args:
            port: Dashboard port
            enable_paper_trading: Enable background paper trading (Phase 4)
        """
        self.port = port
        self.enable_paper_trading = enable_paper_trading and PAPER_TRADING_AVAILABLE
        
        # Phase 1 & 2 Components
        self.data_feed = None
        self.indicator_engine = None
        self.ai_analyst = None
        self.l2_handler = None
        
        # Phase 4 Component
        self.paper_trading = None
        
        # State
        self.current_symbol = "SPY"
        self.current_data = {}
        self.last_update = 0
        self.data_lock = Lock()
        self.running = False
        
        # Create Dash app
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.app.title = "AI Trading Companion - FULL SYSTEM"
        
        # Build layout
        self._build_layout()
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _build_layout(self):
        """Build dashboard layout with paper trading stats."""
        
        self.app.layout = html.Div([
            # Header
            html.Div(id='header-div'),
            
            # Symbol input row
            html.Div([
                html.Div([
                    dcc.Input(
                        id='symbol-input',
                        type='text',
                        value=self.current_symbol,
                        placeholder='Enter symbol...',
                        style={'padding': '10px', 'fontSize': '1.1em', 'width': '200px', 'marginRight': '10px'}
                    ),
                    html.Button('Analyze', id='analyze-button', n_clicks=0, 
                               style={'padding': '10px 30px', 'fontSize': '1.1em', 'backgroundColor': '#3498db', 
                                     'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),
                    html.Span(id='status-message', style={'marginLeft': '20px', 'fontSize': '0.9em'})
                ], style={'textAlign': 'center', 'padding': '20px'})
            ]),
            
            # ========================================
            # PHASE 4 INTEGRATION: Paper Trading Stats
            # ========================================
            html.Div([
                html.Div([
                    html.H3("💰 PAPER TRADING (Live - 3 Scenarios)", 
                           style={'color': '#2c3e50', 'borderBottom': '2px solid #27ae60', 'paddingBottom': '10px'}),
                    html.Div(id='paper-trading-div')
                ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 
                         'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '10px'})
            ]) if self.enable_paper_trading else html.Div(),
            
            # Main content - 4 quadrants
            html.Div([
                # Top row
                html.Div([
                    # Top Left: Signal Strength
                    html.Div([
                        html.H3("📊 SIGNAL STRENGTH", style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
                        html.Div(id='signal-strength-div')
                    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    # Top Right: Order Book Intelligence
                    html.Div([
                        html.H3("📈 ORDER BOOK INTELLIGENCE", style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
                        html.Div(id='l2-intel-div')
                    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginLeft': '10px'})
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px', 'marginBottom': '10px'}),
                
                # Bottom row
                html.Div([
                    # Bottom Left: Risk Analysis
                    html.Div([
                        html.H3("⚖️ RISK ANALYSIS", style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
                        html.Div(id='risk-analysis-div')
                    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                    
                    # Bottom Right: AI Verdict
                    html.Div([
                        html.H3("🤖 AI VERDICT", style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
                        html.Div(id='ai-verdict-div')
                    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginLeft': '10px'})
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px', 'marginBottom': '10px'}),
                
                # Full width: Level 2 Order Book
                html.Div([
                    html.H3("📋 LEVEL 2 ORDER BOOK (Live)", style={'color': '#2c3e50', 'borderBottom': '2px solid #3498db', 'paddingBottom': '10px'}),
                    html.Div(id='l2-orderbook-div')
                ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginTop': '10px'})
            ], style={'padding': '20px', 'maxWidth': '1600px', 'margin': '0 auto'}),
            
            # Auto-update interval
            dcc.Interval(id='update-interval', interval=3000, n_intervals=0)  # 3 seconds
        ], style={'backgroundColor': '#f5f6fa', 'minHeight': '100vh'})
    
    def _setup_callbacks(self):
        """Setup Dash callbacks."""
        
        # Determine which outputs to include
        outputs = [
            Output('header-div', 'children'),
            Output('signal-strength-div', 'children'),
            Output('l2-intel-div', 'children'),
            Output('risk-analysis-div', 'children'),
            Output('ai-verdict-div', 'children'),
            Output('l2-orderbook-div', 'children'),
            Output('status-message', 'children')
        ]
        
        # Add paper trading output if enabled
        if self.enable_paper_trading:
            outputs.insert(1, Output('paper-trading-div', 'children'))
        
        @self.app.callback(
            outputs,
            [Input('update-interval', 'n_intervals'),
             Input('analyze-button', 'n_clicks')],
            [State('symbol-input', 'value')]
        )
        def update_dashboard(n_intervals, n_clicks, symbol):
            """Update all dashboard components."""
            
            # Update symbol if changed
            if symbol and symbol != self.current_symbol:
                self.current_symbol = symbol.upper()
                print(f"[DASHBOARD] Symbol changed to {self.current_symbol}")
            
            # Get latest data
            with self.data_lock:
                data = self.current_data.copy()
            
            if not data:
                # No data yet
                empty = create_empty_state("Waiting for data...")
                results = [
                    create_header(self.current_symbol, 0, 0),
                    empty, empty, empty, empty, empty,
                    create_status_indicator('info', 'Initializing...')
                ]
                
                # Add empty paper trading if enabled
                if self.enable_paper_trading:
                    results.insert(1, create_empty_state("Paper trading initializing..."))
                
                return tuple(results)
            
            # Build components
            try:
                header = self._build_header(data)
                signal_strength = self._build_signal_strength(data)
                l2_intel = self._build_l2_intelligence(data)
                risk_analysis = self._build_risk_analysis(data)
                ai_verdict = self._build_ai_verdict(data)
                l2_orderbook = self._build_l2_orderbook(data)
                
                # Status
                age = time.time() - self.last_update
                if age < 5:
                    status = create_status_indicator('success', f'✅ Live - Updated {age:.1f}s ago')
                elif age < 30:
                    status = create_status_indicator('warning', f'⚠️ Updating... ({age:.0f}s ago)')
                else:
                    status = create_status_indicator('error', f'❌ Data stale ({age:.0f}s ago)')
                
                results = [header, signal_strength, l2_intel, risk_analysis, ai_verdict, l2_orderbook, status]
                
                # ========================================
                # PHASE 4 INTEGRATION: Paper Trading Stats
                # ========================================
                if self.enable_paper_trading:
                    paper_trading_stats = self._build_paper_trading_stats()
                    results.insert(1, paper_trading_stats)
                
                return tuple(results)
                
            except Exception as e:
                print(f"[ERROR] Dashboard update failed: {e}")
                import traceback
                traceback.print_exc()
                
                error_msg = create_status_indicator('error', f'Error: {str(e)}')
                results = [create_header(self.current_symbol, 0, 0)] + [error_msg] * 6
                
                if self.enable_paper_trading:
                    results.insert(1, error_msg)
                
                return tuple(results)
    
    # ========================================
    # PHASE 4 INTEGRATION: Paper Trading Display
    # ========================================
    def _build_paper_trading_stats(self) -> html.Div:
        """Build paper trading statistics panel."""
        if not self.paper_trading:
            return create_empty_state("Paper trading not initialized")
        
        try:
            stats = self.paper_trading.get_stats()
            
            # Build scenario cards
            scenario_cards = []
            for scenario_name in ['aggressive', 'moderate', 'conservative']:
                scenario = stats['scenarios'].get(scenario_name, {})
                
                equity = scenario.get('equity', 15000)
                pnl = equity - 15000
                pnl_pct = (pnl / 15000) * 100
                trades = scenario.get('total_trades', 0)
                wins = scenario.get('winning_trades', 0)
                losses = scenario.get('losing_trades', 0)
                win_rate = scenario.get('win_rate', 0)
                position = scenario.get('current_position', {})
                
                # Color based on P&L
                pnl_color = '#27ae60' if pnl > 0 else '#e74c3c' if pnl < 0 else '#95a5a6'
                
                card = html.Div([
                    html.H4(scenario_name.upper(), style={'color': '#2c3e50', 'marginBottom': '10px'}),
                    
                    # Equity & P&L
                    html.Div([
                        html.Div([
                            html.Span("Equity: ", style={'color': '#7f8c8d'}),
                            html.Span(f"${equity:,.0f}", style={'fontWeight': 'bold', 'color': '#2c3e50'})
                        ]),
                        html.Div([
                            html.Span("P&L: ", style={'color': '#7f8c8d'}),
                            html.Span(f"${pnl:+,.0f} ({pnl_pct:+.2f}%)", 
                                     style={'fontWeight': 'bold', 'color': pnl_color})
                        ])
                    ], style={'marginBottom': '10px'}),
                    
                    # Trade Stats
                    html.Div([
                        html.Span(f"Trades: {trades} ({wins}W/{losses}L)", style={'fontSize': '0.9em', 'color': '#7f8c8d'}),
                        html.Br(),
                        html.Span(f"Win Rate: {win_rate:.1f}%", style={'fontSize': '0.9em', 'color': '#7f8c8d'})
                    ], style={'marginBottom': '10px'}),
                    
                    # Current Position
                    html.Div([
                        html.Strong("Position: "),
                        html.Span(position.get('status', 'FLAT'), 
                                 style={'color': '#27ae60' if position.get('status') != 'FLAT' else '#95a5a6'})
                    ], style={'fontSize': '0.9em'})
                    
                ], style={
                    'padding': '15px',
                    'backgroundColor': '#ecf0f1',
                    'borderRadius': '8px',
                    'border': '1px solid #bdc3c7'
                })
                
                scenario_cards.append(card)
            
            # Overall stats
            overall_equity = stats.get('total_equity', 45000)
            overall_pnl = overall_equity - 45000
            overall_pnl_pct = (overall_pnl / 45000) * 100
            total_trades = stats.get('total_trades', 0)
            
            overall_color = '#27ae60' if overall_pnl > 0 else '#e74c3c' if overall_pnl < 0 else '#95a5a6'
            
            return html.Div([
                # Overall Stats Bar
                html.Div([
                    html.Div([
                        html.Strong("OVERALL: "),
                        html.Span(f"${overall_equity:,.0f} total equity | ", style={'fontSize': '1.1em'}),
                        html.Span(f"{overall_pnl:+,.0f} ({overall_pnl_pct:+.2f}%) P&L | ", 
                                 style={'fontSize': '1.1em', 'fontWeight': 'bold', 'color': overall_color}),
                        html.Span(f"{total_trades} total trades", style={'fontSize': '1.0em', 'color': '#7f8c8d'})
                    ])
                ], style={'padding': '10px', 'backgroundColor': '#ecf0f1', 'borderRadius': '5px', 'marginBottom': '15px'}),
                
                # Scenario Cards
                html.Div(scenario_cards, style={
                    'display': 'grid',
                    'gridTemplateColumns': '1fr 1fr 1fr',
                    'gap': '10px'
                })
            ])
            
        except Exception as e:
            print(f"[ERROR] Failed to build paper trading stats: {e}")
            return create_empty_state(f"Error loading stats: {str(e)}")
    
    def _build_header(self, data: Dict) -> html.Div:
        """Build header component."""
        price = data.get('indicator', {}).get('current_price', 0)
        change_pct = 0.5  # Placeholder
        return create_header(self.current_symbol, price, change_pct)
    
    def _build_signal_strength(self, data: Dict) -> html.Div:
        """Build signal strength panel."""
        indicator = data.get('indicator', {})
        
        prob = indicator.get('probability', 0)
        quality = indicator.get('quality', 'UNKNOWN')
        squeeze = indicator.get('squeeze_status', 'UNKNOWN')
        regime = indicator.get('vol_regime', 'UNKNOWN')
        breakdown = indicator.get('score_breakdown', {})
        
        max_scores = {
            'vwap': 20, 'macd': 25, 'ema': 20, 'volume': 20,
            'extension': 15, 'squeeze': 20, 'momentum': 15, 'confluence': 10
        }
        
        return html.Div([
            create_probability_bar(prob, quality),
            html.Hr(),
            html.Div([
                create_metric_card("Squeeze", squeeze, "", '#3498db' if 'FIRING' in squeeze else '#95a5a6'),
                create_metric_card("Regime", regime, "", '#27ae60' if regime == 'NORMAL' else '#f39c12')
            ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px', 'marginTop': '15px'}),
            html.Hr(),
            html.H5("Score Breakdown:", style={'marginTop': '15px', 'color': '#7f8c8d'}),
            create_score_breakdown(breakdown, max_scores)
        ])
    
    def _build_l2_intelligence(self, data: Dict) -> html.Div:
        """Build L2 intelligence panel."""
        l2_stats = data.get('l2_stats', {})
        
        imbalance = l2_stats.get('imbalance', 0)
        spread = l2_stats.get('spread', 0)
        bid_levels = l2_stats.get('bid_levels', 0)
        ask_levels = l2_stats.get('ask_levels', 0)
        
        imbalance_color = '#27ae60' if imbalance > 5 else ('#e74c3c' if imbalance < -5 else '#95a5a6')
        
        return html.Div([
            html.Div([
                create_metric_card("Bid/Ask Imbalance", f"{imbalance:+.1f}%", 
                                  "Positive = Bullish", imbalance_color),
                create_metric_card("Spread", f"${spread:.2f}", 
                                  "Tighter = Better", '#3498db')
            ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px'}),
            html.Hr(),
            html.Div([
                html.Div([
                    html.Strong("Bid Levels: "),
                    html.Span(bid_levels, style={'color': '#27ae60'})
                ], style={'marginBottom': '5px'}),
                html.Div([
                    html.Strong("Ask Levels: "),
                    html.Span(ask_levels, style={'color': '#e74c3c'})
                ])
            ])
        ])
    
    def _build_risk_analysis(self, data: Dict) -> html.Div:
        """Build risk analysis panel."""
        indicator = data.get('indicator', {})
        
        vwap_zones = indicator.get('vwap_zones', {}).get('long', {})
        entry = vwap_zones.get('entry', 0)
        stop = vwap_zones.get('stop', 0)
        target = vwap_zones.get('target', 0)
        size = vwap_zones.get('position_size', 0)
        
        risk_per_share = entry - stop if entry and stop else 0
        reward_per_share = target - entry if target and entry else 0
        rr_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 0
        
        return html.Div([
            html.Div([
                create_metric_card("Entry", f"${entry:.2f}" if entry else "N/A", "VWAP Zone", '#3498db'),
                create_metric_card("Stop", f"${stop:.2f}" if stop else "N/A", "Risk Level", '#e74c3c'),
                create_metric_card("Target", f"${target:.2f}" if target else "N/A", "Profit Zone", '#27ae60')
            ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr 1fr', 'gap': '10px'}),
            html.Hr(),
            html.Div([
                html.Div([
                    html.Strong("Position Size: "),
                    html.Span(f"{size} shares", style={'color': '#3498db'})
                ], style={'marginBottom': '5px'}),
                html.Div([
                    html.Strong("R:R Ratio: "),
                    html.Span(f"{rr_ratio:.2f}:1", style={'color': '#27ae60' if rr_ratio >= 1.5 else '#f39c12'})
                ], style={'marginBottom': '5px'}),
                html.Div([
                    html.Strong("Max Risk: "),
                    html.Span(f"${risk_per_share * size:.2f}", style={'color': '#e74c3c'})
                ])
            ])
        ])
    
    def _build_ai_verdict(self, data: Dict) -> html.Div:
        """Build AI verdict panel."""
        ai_analysis = data.get('ai', {})
        
        if not ai_analysis or 'scenarios' not in ai_analysis:
            return create_empty_state("AI analysis in progress...")
        
        scenarios = ai_analysis.get('scenarios', {})
        recommended = ai_analysis.get('recommendation', 'moderate')
        
        cards = []
        for name in ['aggressive', 'moderate', 'conservative']:
            if name in scenarios:
                is_recommended = (name == recommended)
                cards.append(create_scenario_card(name, scenarios[name], is_recommended))
        
        return html.Div(cards)
    
    def _build_l2_orderbook(self, data: Dict) -> html.Div:
        """Build L2 order book visualization."""
        l2_depth = data.get('l2_depth', {})
        
        if not l2_depth:
            return create_empty_state("Level 2 data loading...")
        
        bids = l2_depth.get('bids', [])
        asks = l2_depth.get('asks', [])
        
        return create_l2_table(bids, asks)
    
    # ========================================
    # PHASE 1 & 2 & 4 INTEGRATION: Data Update Loop
    # ========================================
    def _data_update_loop(self):
        """
        Background thread for updating data.
        
        This is where ALL PHASES come together:
        - Phase 1: Indicator Engine
        - Phase 2: AI Analyst
        - Phase 3: Dashboard (UI updates)
        - Phase 4: Paper Trading (gets AI signals)
        """
        print("[DASHBOARD] Data update loop started")
        
        while self.running:
            try:
                # ========================================
                # PHASE 1: Run Indicator Engine
                # ========================================
                indicator_result = self.indicator_engine.analyze(self.current_symbol)
                
                # ========================================
                # PHASE 2: Run AI Analysis
                # ========================================
                ai_result = self.ai_analyst.analyze(indicator_result, symbol=self.current_symbol)
                
                # ========================================
                # PHASE 3: Get L2 Data
                # ========================================
                try:
                    self.l2_handler.subscribe_market_depth(self.current_symbol)
                    l2_depth = self.l2_handler.get_market_depth()
                    l2_stats = self.l2_handler.get_stats()
                except Exception as e:
                    l2_depth = {'bids': [], 'asks': []}
                    l2_stats = {'imbalance': 0, 'spread': 0, 'bid_levels': 0, 'ask_levels': 0}
                
                # ========================================
                # PHASE 4: Feed to Paper Trading Engine
                # ========================================
                if self.paper_trading:
                    try:
                        # Get current price for paper trading
                        current_price = indicator_result.get('current_price', 0)
                        
                        # Update paper trading with AI analysis
                        self.paper_trading.update(
                            symbol=self.current_symbol,
                            price=current_price,
                            indicator_data=indicator_result,
                            ai_analysis=ai_result,
                            timestamp=datetime.now()
                        )
                    except Exception as e:
                        print(f"[WARN] Paper trading update failed: {e}")
                
                # Update shared state (for dashboard display)
                with self.data_lock:
                    self.current_data = {
                        'indicator': indicator_result,
                        'ai': ai_result,
                        'l2_depth': l2_depth,
                        'l2_stats': l2_stats
                    }
                    self.last_update = time.time()
                
                print(f"[DASHBOARD] Updated {self.current_symbol} - Prob: {indicator_result.get('probability', 0):.0f}%")
                
                # Wait before next update
                time.sleep(3)
                
            except Exception as e:
                print(f"[ERROR] Data update failed: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)
    
    def start(self):
        """Start the dashboard."""
        print(f"[DASHBOARD] Starting AI Trading Companion (FULL SYSTEM) on port {self.port}...")
        
        # ========================================
        # Initialize ALL PHASES
        # ========================================
        
        # Phase 1 & 2: Data Feed + Indicator + AI
        try:
            print("[DASHBOARD] Phase 1: Connecting to IBKR...")
            self.data_feed = IBKRDataFeed(port=config.IBKR_PORT, client_id=4)
            self.data_feed.connect()
            
            print("[DASHBOARD] Phase 1: Initializing indicator engine...")
            self.indicator_engine = IndicatorEngine(self.data_feed)
            
            print("[DASHBOARD] Phase 2: Initializing AI analyst...")
            self.ai_analyst = AIAnalyst(model=config.AI_MODEL)
            
            print("[DASHBOARD] Phase 3: Initializing Level 2 handler...")
            self.l2_handler = Level2Handler(self.data_feed.ib)
            
            print("[DASHBOARD] ✅ Phases 1-3 initialized!")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize Phases 1-3: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # ========================================
        # PHASE 4: Initialize Paper Trading
        # ========================================
        if self.enable_paper_trading:
            try:
                print("[DASHBOARD] Phase 4: Initializing paper trading engine...")
                self.paper_trading = PaperTradingEngine()
                print("[DASHBOARD] ✅ Phase 4 initialized!")
                print(f"[DASHBOARD] 💰 Paper Trading: 3 scenarios, $45,000 total capital")
            except Exception as e:
                print(f"[WARN] Failed to initialize paper trading: {e}")
                self.enable_paper_trading = False
        
        # Start background data update loop
        self.running = True
        update_thread = Thread(target=self._data_update_loop, daemon=True)
        update_thread.start()
        
        # Run Dash app
        print(f"\n🚀 Dashboard running at: http://localhost:{self.port}")
        print(f"📊 Current symbol: {self.current_symbol}")
        print(f"🔄 Auto-update: Every 3 seconds")
        if self.enable_paper_trading:
            print(f"💰 Paper Trading: ACTIVE (3 scenarios)")
        print(f"\n✅ ALL 4 PHASES RUNNING!\n")
        
        self.app.run(debug=False, host='127.0.0.1', port=self.port)
    
    def stop(self):
        """Stop the dashboard."""
        print("[DASHBOARD] Stopping...")
        self.running = False
        
        if self.l2_handler:
            self.l2_handler.unsubscribe_market_depth()
        
        if self.paper_trading:
            # Save final state
            stats = self.paper_trading.get_stats()
            print(f"\n💰 FINAL PAPER TRADING STATS:")
            print(f"   Total Equity: ${stats.get('total_equity', 45000):,.0f}")
            print(f"   Total Trades: {stats.get('total_trades', 0)}")
        
        if self.data_feed:
            self.data_feed.disconnect()
        
        print("[DASHBOARD] Stopped")


if __name__ == "__main__":
    dashboard = UnifiedDashboard(port=8052, enable_paper_trading=True)
    try:
        dashboard.start()
    except KeyboardInterrupt:
        dashboard.stop()
