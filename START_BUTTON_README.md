# 🚀 START BUTTON - QUICK INTEGRATION GUIDE

## Two Options to Get Started:

---

## ⚡ OPTION 1: ONE-CLICK START (RECOMMENDED)

Just double-click (Windows) or run:

```bash
START_TRADING_COMPANION.bat
```

Or:

```bash
python start_trading_companion.py
```

This will:
1. ✅ Check all dependencies
2. ✅ Verify IBKR connection
3. ✅ Check Ollama AI
4. ✅ Launch the dashboard
5. ✅ Start paper trading automatically

**Requirements:**
- TWS/IB Gateway running on port 7497
- Ollama running with qwen2.5:7b
- All Python packages installed

---

## 🔧 OPTION 2: MANUAL DASHBOARD INTEGRATION

If you want paper trading in your existing dashboard, make these 3 simple changes:

### Change 1: Add Import (Line ~18)
```python
from paper_trading_engine import PaperTradingEngine
```

### Change 2: Initialize in __init__ (Line ~32)
```python
self.paper_trading = None
```

### Change 3: Start Paper Trading in start() method (Line ~380)
```python
print("[DASHBOARD] Initializing paper trading engine...")
self.paper_trading = PaperTradingEngine()
```

### Change 4: Update Data Loop (Line ~310, in _data_update_loop)
After the AI analysis, add:
```python
# Update paper trading
if self.paper_trading:
    try:
        self.paper_trading.process_ai_analysis(
            ai_result,
            indicator_result,
            current_price=indicator_result.get('current_price', 0),
            current_high=indicator_result.get('current_price', 0),
            current_low=indicator_result.get('current_price', 0),
            l2_data=l2_stats
        )
    except Exception as e:
        print(f"[ERROR] Paper trading update failed: {e}")
```

That's it! Paper trading will run in the background and log all trades.

---

## 📊 What You'll See

### In Console:
```
[AGGRESSIVE] ENTRY: LONG 120 AAPL @ $150.30 | Stop: $149.00 | Target: $152.00
[MODERATE] Limit order filled @ $150.00
[AGGRESSIVE] EXIT: AAPL @ $152.00 | TARGET | P&L: $204.00 | Equity: $15204.00
```

### In Logs:
```
logs/ai_paper_trading/
├── trades_20251115.csv       # All completed trades
├── signals_20251115.csv      # All AI signals
└── performance_20251115.json # Daily stats
```

---

## 🎯 Quick Test

Want to verify it works before running live?

```bash
python test_paper_trading.py
```

Expected: **5/5 tests pass** ✅

---

## 📁 Files You Need

Make sure these are in your directory:

```
✅ start_trading_companion.py      # Main launcher
✅ START_TRADING_COMPANION.bat     # Windows launcher
✅ paper_trading_engine.py         # Trading engine
✅ trade_logger.py                 # Logging system
✅ dashboard_unified.py            # Your dashboard
✅ config_ai.py                    # Configuration
```

---

## ⚙️ Configuration

Want to change paper trading settings? Edit `config_ai.py`:

```python
# Starting capital per scenario
PAPER_EQUITY_PER_SCENARIO = 15000  # $15k each

# Probability thresholds
AGGRESSIVE_MIN_PROB = 45     # Aggressive enters at 45%+
MODERATE_MIN_PROB = 55       # Moderate enters at 55%+
CONSERVATIVE_MIN_PROB = 70   # Conservative enters at 70%+

# Risk per trade (% of equity)
AGGRESSIVE_RISK = 1.2
MODERATE_RISK = 1.0
CONSERVATIVE_RISK = 0.75
```

---

## 🆘 Troubleshooting

**"Module not found" error?**
```bash
pip install pandas numpy ib_insync dash ollama
```

**"Could not connect to IBKR"?**
- Start TWS or IB Gateway
- Check it's on port 7497
- Enable API in TWS settings

**"Ollama not running"?**
```bash
# Start Ollama, then:
ollama pull qwen2.5:7b
```

**Paper trading not logging?**
- Check `logs/ai_paper_trading/` directory exists
- Check file permissions
- Look for errors in console

---

## 🎉 You're Ready!

1. **Quick test:** `python test_paper_trading.py`
2. **Start dashboard:** `START_TRADING_COMPANION.bat`
3. **Watch it trade:** http://localhost:8052
4. **Check logs:** `logs/ai_paper_trading/trades_YYYYMMDD.csv`

The system will:
- Analyze every signal from your indicator
- Run 3 AI scenarios in parallel
- Log every trade with complete context
- Track performance in real-time
- Export ML-ready data to CSV

Let it run and collect data! 🚀
