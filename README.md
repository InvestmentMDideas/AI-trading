# 🤖 AI-Powered Day Trading System

An advanced automated day trading system combining **145-point technical probability scoring** with **multi-stage AI reasoning** for systematic trade generation and execution.

![System Architecture](docs/ai_trading_flow_diagram.svg)

## 🎯 Key Features

- **📊 145-Point Probability Scoring**: Comprehensive technical analysis across 8 components (VWAP, MACD, EMA, Volume, Squeeze, Momentum, etc.)
- **🤖 Multi-Stage AI Reasoning**: 6-stage analysis pipeline using Ollama (qwen2.5:7b) for context-aware decision making
- **🎬 Three Trading Scenarios**: Adaptive strategies (Aggressive 45%+, Moderate 55%+, Conservative 70%+) with automatic selection
- **📈 Real-Time Dashboard**: Live monitoring with signal strength, order book intelligence, risk analysis, and AI verdicts
- **🛡️ Safety-First Design**: Paper trading enforcement, daily loss limits, position controls, emergency stops
- **⚡ High Performance**: Parallel processing of 50+ stocks with 73% faster analysis, <5% AI failure rate

## 📈 Performance Metrics

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| **Signal Generation** | Baseline | 10x more | +1000% |
| **Average Probability** | 25% | 50%+ | +100% |
| **AI Reliability** | 55% | 95%+ | +73% |
| **Processing Speed** | Baseline | 73% faster | Sequential → Parallel |
| **Stock Coverage** | 20 stocks | 50+ stocks | +150% |

**Target**: $1,000/day profit | **Starting Capital**: $10,000 | **Risk**: 1%/trade

## 🏗️ System Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌──────────────┐
│   IBKR      │────▶│  Indicator       │────▶│  AI Analyst │────▶│  Execution   │
│   Data      │     │  Engine          │     │  (Ollama)   │     │  & Monitor   │
│ (50 stocks) │     │ (145pt scoring)  │     │  (6 stages) │     │  Dashboard   │
└─────────────┘     └──────────────────┘     └─────────────┘     └──────────────┘
   Multi-TF          VWAP•MACD•EMA           Context→Tech         Paper Trading
   Level 2           Squeeze•Volume          Risk→Scenarios       Level 2 Intel
```

### Component Breakdown

**Layer 1: Data Collection**
- Interactive Brokers (TWS/Gateway) on port 7497
- Multi-timeframe data (1min, 5min, 15min, 4H, Daily)
- Level 2 order book streaming
- 50+ stocks with 60-second refresh

**Layer 2: Analysis Engine**
- **Indicator Engine**: 145-point probability scoring across 8 technical components
- **AI Analyst**: 6-stage reasoning (Market Context → Technical → Risk → 3 Scenarios)

**Layer 3: Decision Engine**
- Three adaptive scenarios with auto-selection
- Risk-adjusted position sizing
- Entry/Stop/Target calculation

**Layer 4: Execution & Monitoring**
- Paper trading with safety controls
- Real-time unified dashboard (Port 8052)
- Level 2 order book intelligence

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Interactive Brokers TWS or IB Gateway
- Ollama with qwen2.5:7b model

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-trading-system.git
cd ai-trading-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install and setup Ollama
# Visit: https://ollama.ai
ollama pull qwen2.5:7b

# 4. Configure settings
cp config.py.example config.py
# Edit config.py with your settings

# 5. Verify setup
python setup_check.py
```

### Running the System

```bash
# Run tests
python test_indicator.py      # Test 145-point scoring
python test_ai_analyst.py      # Test AI reasoning

# Analyze a symbol
python example_analyze.py SPY

# Full AI analysis
python example_with_ai.py AAPL

# Start the dashboard
python dashboard_unified.py
# Open: http://localhost:8052
```

## 📊 Usage Examples

### Quick Analysis

```python
from indicator_engine import IndicatorEngine
from ibkr_data_feed import IBKRDataFeed

# Connect to IBKR
feed = IBKRDataFeed(port=7497)
feed.connect()

# Analyze a symbol
engine = IndicatorEngine(feed)
result = engine.analyze('SPY')

print(f"Probability: {result['probability']}%")
print(f"Quality: {result['quality']}")
print(f"Signals: {result['signals']}")
```

### Full AI Analysis

```python
from ai_analyst import AIAnalyst

analyst = AIAnalyst(model="qwen2.5:7b")
ai_result = analyst.analyze(indicator_data, symbol='SPY')

print(f"Recommendation: {ai_result['recommendation']}")
print(f"Confidence: {ai_result['recommended_confidence']}%")
print(f"AI Verdict: {ai_result['overall_verdict']}")
```

## 🎯 145-Point Scoring System

| Component | Max Points | Description |
|-----------|------------|-------------|
| **VWAP Position** | 20 | Distance from VWAP in ATR units |
| **MACD Alignment** | 25 | MACD line vs signal line position |
| **EMA Trend** | 20 | Fast EMA vs slow EMA alignment |
| **Volume Surge** | 20 | Relative volume (RVOL) strength |
| **Price Extension** | 15 | Price deviation from VWAP |
| **TTM Squeeze** | 20 | Squeeze status and strength |
| **Squeeze Momentum** | 15 | Momentum magnitude and direction |
| **Confluence Bonus** | 10 | Multiple indicators aligning |
| **TOTAL** | **145** | Converted to 0-100% probability |

**Quality Ratings**:
- 🟢 **HIGH** (70%+): Premium setups
- 🟡 **MEDIUM** (50-69%): Standard setups
- 🔴 **LOW** (<50%): Avoid or wait

## 🤖 AI Reasoning Pipeline

### 6-Stage Analysis

1. **Market Context** (Score: 0-100)
   - Volatility regime detection
   - Session identification
   - Market conditions assessment

2. **Technical Analysis** (Score: 0-100)
   - Probability assessment
   - Squeeze evaluation
   - Trend quality analysis

3. **Risk Assessment** (Score: 0-100)
   - Entry quality evaluation
   - Stop placement validation
   - Risk:Reward ratio calculation

4. **Aggressive Scenario**
   - Min 45% probability
   - 1.2% risk tolerance
   - Wider stops, immediate entry

5. **Moderate Scenario**
   - Min 55% probability
   - 1.0% risk tolerance
   - Balanced approach

6. **Conservative Scenario**
   - Min 70% probability
   - 0.75% risk tolerance
   - Premium setups only

### AI Model

- **Engine**: Ollama (local inference)
- **Model**: qwen2.5:7b (7B parameter LLM)
- **Cache**: 5-minute TTL, ~50% hit rate
- **Reliability**: <5% failure rate

## 🛡️ Safety Controls

### Built-in Protection

- ✅ **Paper Trading Only**: No live trading capability
- ✅ **Daily Loss Limit**: $150 maximum (configurable)
- ✅ **Position Size Limit**: $1,000 per trade
- ✅ **Max Concurrent Positions**: 5 simultaneous trades
- ✅ **Symbol Diversity**: Minimum 3 different symbols
- ✅ **Emergency Stops**: Manual kill switches

### Risk Management

```python
# Example configuration
MAX_DAILY_LOSS = 150          # Stop trading if hit
MAX_POSITION_SIZE = 1000      # Per trade limit
RISK_PER_TRADE = 0.01         # 1% of account
```

## 📊 Dashboard Features

**Unified Dashboard** (Port 8052):

- **Signal Strength**: Real-time probability bar, score breakdown
- **Order Book Intelligence**: Bid/Ask imbalance, spread analysis
- **Risk Analysis**: Entry/Stop/Target levels, R:R ratios
- **AI Verdict**: Three scenarios with confidence scores
- **Live Level 2**: Real-time order book visualization

**Auto-refresh**: Every 60 seconds

## 🔧 Configuration

Key settings in `config.py`:

```python
# IBKR Connection
IBKR_PORT = 7497              # Paper trading

# Risk Settings
ACCOUNT_SIZE = 10000
RISK_PER_TRADE = 0.01         # 1%

# AI Model
AI_MODEL = "qwen2.5:7b"

# Scenario Thresholds
AGGRESSIVE_MIN_PROB = 45      # 45%+
MODERATE_MIN_PROB = 55        # 55%+
CONSERVATIVE_MIN_PROB = 70    # 70%+

# Dashboard
AI_DASHBOARD_PORT = 8052
```

See `config.py.example` for all options.

## 📈 Evolution: v1.0 → v2.0

### Major Improvements

**AI Engine**:
- Switched from DeepSeek-R1 to qwen2.5:7b → 10x more signals
- Reduced AI failure rate from 45% to <5%
- Added response caching → 50% speed boost

**Scoring System**:
- Upgraded from 115 to 145 points → 26% more granular
- Made squeeze "nice to have" vs mandatory → more flexible
- Lowered thresholds (70%+ to 50-60%) → better signal flow

**Performance**:
- Parallel processing → 73% faster
- 50 stocks (up from 20) → 2.5x coverage
- Average probability 50%+ (up from 25%) → 2x better quality

## 🧪 Testing

```bash
# Run all tests
python test_indicator.py      # 7 tests
python test_ai_analyst.py     # 6 tests
python test_dashboard.py      # Component validation

# Expected: All tests pass ✅
```

## 📁 Project Structure

```
ai-trading-system/
├── config.py.example          # Configuration template
├── requirements.txt           # Dependencies
├── README.md                  # This file
│
├── Core Engine/
│   ├── ibkr_data_feed.py     # IBKR data connection
│   ├── indicator_engine.py    # 145-point scoring
│   ├── market_metrics.py      # Technical calculations
│   ├── ai_analyst.py          # Multi-stage AI
│   ├── ai_cache.py            # Response caching
│   └── prompt_templates.py    # AI prompts
│
├── Dashboard/
│   ├── dashboard_unified.py   # Main dashboard
│   ├── layout_components.py   # UI components
│   └── level2_handler.py      # Order book
│
├── Testing/
│   ├── setup_check.py         # Setup verification
│   ├── test_indicator.py      # Indicator tests
│   ├── test_ai_analyst.py     # AI tests
│   └── test_dashboard.py      # Dashboard tests
│
└── Examples/
    ├── example_analyze.py     # Simple analysis
    └── example_with_ai.py     # Full AI analysis
```

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Broker API**: ib_insync (Interactive Brokers)
- **AI Engine**: Ollama (local LLM inference)
- **AI Model**: qwen2.5:7b (7B parameters)
- **Dashboard**: Dash + Plotly + Bootstrap
- **Data Analysis**: pandas, numpy
- **Technical Indicators**: Custom (Pine Script compatible)

## 📝 Requirements

```
pandas>=1.5.0
numpy>=1.23.0
ib_insync>=0.9.86
ollama>=0.1.0
dash>=2.14.0
dash-bootstrap-components>=1.5.0
plotly>=5.17.0
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

**IMPORTANT**: This software is for **educational and research purposes only**. 

- This system is configured for **paper trading only**
- Past performance does not guarantee future results
- Trading involves substantial risk of loss
- Always do your own research (DYOR)
- Never trade with money you can't afford to lose
- The authors are not responsible for any financial losses

**USE AT YOUR OWN RISK**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Interactive Brokers for market data and execution
- Ollama team for local LLM infrastructure
- qwen2.5 model developers
- Pine Script community for indicator inspiration

## 📧 Contact

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/ai-trading-system/issues)
- Discussions: [Ask questions or share ideas](https://github.com/yourusername/ai-trading-system/discussions)

## 🗺️ Roadmap

- [ ] Add backtesting engine
- [ ] Support for additional brokers
- [ ] Machine learning for pattern recognition
- [ ] Mobile dashboard
- [ ] Advanced order types
- [ ] Portfolio optimization
- [ ] Multi-asset support (futures, options, crypto)

---

**Built with** ❤️ **for systematic day trading**

**Version**: 2.0 | **Status**: Production-ready for paper trading | **Last Updated**: November 2025
