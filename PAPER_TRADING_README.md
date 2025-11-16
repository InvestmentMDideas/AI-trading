# 📊 PAPER TRADING ENGINE - QUICK START

## 🎯 What Is This?

A background paper trading engine that runs **3 AI scenarios simultaneously**:

- **Aggressive:** Fast entries, higher risk (45% prob threshold)
- **Moderate:** Zone entries, balanced risk (55% prob threshold)  
- **Conservative:** High-quality only, lower risk (70% prob threshold)

All trades are logged to CSV for machine learning training.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Test the Engine
```bash
python test_paper_trading.py
```

**Expected:**
```
✅ PASS  Basic Trade Entry & Exit
✅ PASS  Stop Loss Execution
✅ PASS  Moderate Zone Entry
✅ PASS  Conservative Strict Thresholds
✅ PASS  Performance Logging

Total: 5/5 tests passed
🎉 ALL TESTS PASSED!
```

### Step 2: Integrate with Dashboard

Open `DASHBOARD_INTEGRATION_INSTRUCTIONS.txt` and follow the steps to add paper trading to your dashboard.

### Step 3: Run Dashboard

```bash
python dashboard_unified.py
```

Open: http://localhost:8052

You'll see live paper trading performance!

---

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `paper_trading_engine.py` | Main trading engine (3 scenarios) |
| `trade_logger.py` | Logging system (CSV exports) |
| `test_paper_trading.py` | Validation tests |
| `DASHBOARD_INTEGRATION_INSTRUCTIONS.txt` | Dashboard setup |
| `PHASE_4_COMPLETE.md` | Complete documentation |

---

## 📊 What Gets Logged?

### trades_YYYYMMDD.csv
Every trade with complete context:
- Entry/exit prices and times
- Indicator scores (probability, squeeze, regime)
- AI confidence and reasoning
- L2 data (imbalance, spread)
- Outcome (win/loss, P&L, R:R achieved)

### signals_YYYYMMDD.csv  
Every AI signal (whether traded or not):
- All three scenario recommendations
- Indicator data
- AI reasoning
- Current price action

### performance_YYYYMMDD.json
Daily performance stats:
- P&L per scenario
- Win rates
- Average R:R
- Best/worst trades

---

## 🎯 How It Works

```
1. Dashboard feeds AI analysis → Paper Trading Engine

2. Engine processes each scenario independently:
   
   AGGRESSIVE: "Signal? → Enter NOW"
   MODERATE:   "Signal? → Wait for zone"
   CONSERVATIVE: "High prob? → Wait for pullback"

3. Positions tracked with stops and targets

4. Automatic exits when stop/target hit

5. All trades logged to CSV

6. Dashboard shows live stats
```

---

## 📈 Example Dashboard Display

```
┌──────────────────┬──────────────────┬──────────────────┐
│ AGGRESSIVE       │ MODERATE         │ CONSERVATIVE     │
├──────────────────┼──────────────────┼──────────────────┤
│ Equity: $15,216  │ Equity: $15,100  │ Equity: $15,000  │
│ P&L: +$216(1.4%) │ P&L: +$100(0.7%) │ P&L: $0 (0.0%)   │
│ Trades: 3(2W/1L) │ Trades: 1(1W/0L) │ Trades: 0        │
│ Win Rate: 66.7%  │ Win Rate: 100%   │ Win Rate: N/A    │
│ Position: ✅ LONG │ Position: ⚪ FLAT │ Position: ⚪ FLAT │
└──────────────────┴──────────────────┴──────────────────┘

OVERALL: Total Equity: $45,316 | P&L: +$316 (+0.70%)
```

---

## ⚙️ Configuration

Edit `config_ai.py`:

```python
# Starting capital per scenario
PAPER_EQUITY_PER_SCENARIO = 15000

# Probability thresholds
AGGRESSIVE_MIN_PROB = 45
MODERATE_MIN_PROB = 55
CONSERVATIVE_MIN_PROB = 70

# Risk per trade
AGGRESSIVE_RISK = 1.2  # % of equity
MODERATE_RISK = 1.0
CONSERVATIVE_RISK = 0.75

# Stop loss sizing
AGGRESSIVE_STOP_ATR = 2.5  # ATR multiplier
MODERATE_STOP_ATR = 2.0
CONSERVATIVE_STOP_ATR = 1.5
```

---

## 🔍 Analyzing Results

### After 1 Day:
```bash
# View trade log
cat logs/ai_paper_trading/trades_20251115.csv

# See which scenario is winning
python -c "
from trade_logger import TradeLogger
logger = TradeLogger()
print(logger.calculate_performance_stats('aggressive'))
print(logger.calculate_performance_stats('moderate'))
print(logger.calculate_performance_stats('conservative'))
"
```

### After 1 Week:
```python
import pandas as pd

# Load all trades
df = pd.read_csv('logs/ai_paper_trading/trades_20251115.csv')

# Which scenario wins most?
print(df.groupby('scenario')['win_loss'].value_counts())

# Average R:R by scenario
print(df.groupby('scenario')['rr_achieved'].mean())

# Best setups
winners = df[df['win_loss'] == 'WIN']
print(winners.groupby('squeeze_status').size())
```

---

## 🎓 Learning from Data

The CSV logs are perfect for:

1. **Pattern Recognition**
   - Which indicators predict wins?
   - What squeeze status works best?
   - Does L2 imbalance matter?

2. **Strategy Optimization**
   - Should we adjust probability thresholds?
   - Is zone waiting worth it?
   - Do we exit too early/late?

3. **ML Training**
   - Predict trade outcomes
   - Optimize entry timing
   - Improve AI reasoning

---

## ⚠️ Important Notes

1. **Paper Trading Only**
   - No real money at risk
   - Uses simulated fills
   - For testing and learning

2. **Not Perfect Fills**
   - Assumes fills at limit/stop prices
   - Real trading has slippage
   - Use as directional guide only

3. **Data Collection Focus**
   - Goal: Gather ML training data
   - Prove strategies work
   - Optimize before going live

---

## 🎯 Success Metrics

After 1 month of paper trading, you should have:

✅ 100-300 trades logged  
✅ Clear winner between scenarios  
✅ Identified best setups  
✅ ML-ready dataset  
✅ Confidence in system  

Then consider live trading with **small size** to validate.

---

## 🆘 Troubleshooting

**Tests fail?**
- Check config_ai.py exists
- Verify imports work
- Check logs directory permissions

**No trades executing?**
- Check probability thresholds
- Verify AI analysis is running
- Check scenario logic

**Dashboard not showing paper trading?**
- Follow DASHBOARD_INTEGRATION_INSTRUCTIONS.txt
- Verify paper_trading_engine imported
- Check for error messages

---

## 📚 Documentation

- **PHASE_4_COMPLETE.md** - Full documentation
- **DASHBOARD_INTEGRATION_INSTRUCTIONS.txt** - Setup guide
- **test_paper_trading.py** - See examples of usage

---

## 🎉 You're Ready!

1. Run tests → `python test_paper_trading.py`
2. Integrate dashboard → Follow instructions
3. Start collecting data → Let it run 24/7
4. Analyze results → After 1 week
5. Optimize strategies → Based on data
6. Prove profitability → Before going live

Good luck! 🚀
