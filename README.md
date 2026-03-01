# V4 Momentum Trading System

A production-grade algorithmic day trading system for US equities, built from the ground up after a failed V3 predecessor. Designed around mechanical stability, broker-native safety, and a data-first approach to machine learning.

**Status**: Paper trading (data collection phase) | **Version**: 4.5.0 | **Codebase**: ~23,000 lines across 16+ modules | **Tests**: 167+

---

## Overview

V4 is a fully automated gap-and-go momentum trading system that scans premarket for high-probability setups, scores entries against multiple technical conditions, executes bracket orders through Interactive Brokers, and manages positions with a dynamic exit system — all without human intervention during market hours.

The system was purpose-built after V3's failure in live trading (74% backtest accuracy collapsed to 24% live). Every architectural decision in V4 is a direct response to a V3 failure mode.

### What Makes This Different

- **Broker-native stops**: Stop-loss orders live on IB's servers, not in Python. If the process crashes, your positions are still protected.
- **Synchronous by design**: No async/await, no event spaghetti. One thread, one loop, fully debuggable. V3's async architecture was undebuggable in production.
- **ML can only veto, never initiate**: The rule-based system generates candidates. ML acts as a filter — it can reject bad setups but cannot create trades on its own. This prevents the feedback loops that killed V3.
- **Shared training/inference code**: One function builds features for both training and live prediction. No silent divergence.

---

## Architecture

```
                          ┌─────────────────────────────────┐
                          │         CONFIGURATION           │
                          │     TOML + Frozen Dataclass     │
                          └──────────────┬──────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
    ┌───────▼───────┐          ┌─────────▼─────────┐        ┌───────▼───────┐
    │   SCANNER     │          │   ORCHESTRATOR    │        │  PERSISTENCE  │
    │               │          │                   │        │               │
    │ • Premarket   │◄────────►│ • Phase Manager   │◄──────►│ • SQLite WAL  │
    │   gap detect  │          │ • Event Loop      │        │ • JSON state  │
    │ • Multi-layer │          │ • Reconciliation  │        │ • Trade log   │
    │   filtering   │          │ • Scheduling      │        │               │
    └───────┬───────┘          └────────┬──────────┘        └───────────────┘
            │                           │
            │                  ┌────────▼──────────┐
            │                  │     STRATEGY      │
            │                  │                   │
            └─────────────────►│ • Entry scoring   │
                               │ • Multi-condition │
                               │ • Quality gates   │
                               └────────┬──────────┘
                                        │
                               ┌────────▼──────────┐
                               │      BROKER       │
                               │                   │
                               │ • Bracket orders  │
                               │ • OCA groups      │
                               │ • Position mgmt   │
                               └────────┬──────────┘
                                        │
                               ┌────────▼──────────┐
                               │   RISK MANAGER    │
                               │                   │
                               │ • Multi-layer     │
                               │   safety stack    │
                               │ • Dynamic exits   │
                               │ • Circuit breakers│
                               │ • Reconciliation  │
                               └───────────────────┘
```

### Core Modules

| Module | Purpose |
|--------|---------|
| **Orchestrator** | Phase-based event loop (Premarket → Trading → Cleanup → Overnight) |
| **Scanner** | Multi-layer premarket gap detection with volume and price filters |
| **Strategy** | Multi-condition entry scoring system with quality gates |
| **Broker** | Interactive Brokers wrapper — bracket orders, OCA groups, contract qualification |
| **Risk Manager** | Multi-layer safety stack, dynamic exit management, position reconciliation |
| **Persistence** | SQLite (WAL mode) for trades, JSON for runtime state |
| **Config** | TOML-driven configuration with frozen Python dataclass |
| **ML Pipeline** | Feature engineering, LightGBM training, shadow candidate analysis |
| **Error Taxonomy** | Classified IB error handling (informational, connectivity, rejection, fatal) |

---

## Trading Phases

The system operates on a strict daily schedule (all times Eastern):

| Phase | Window | Activity |
|-------|--------|----------|
| **Premarket** | 6:00 – 9:30 | Scan for gap-up candidates, build watchlist, rescan every 5 min |
| **Trading** | 9:30 – 15:55 | Score entries, place bracket orders, manage dynamic exits, reconcile positions |
| **Cleanup** | 15:55 – 17:00 | Flatten all positions, log daily summary, save state |
| **Overnight** | 20:00 – 20:30 | Shadow candidate backfill, housekeeping |

---

## Risk Management

The system enforces a multi-layer safety stack. Every trade must pass all layers before execution — covering permanent blacklists, exchange filters, exposure limits, circuit breakers, spread quality gates, and more.

### Dynamic Exit System

Positions are actively managed through multiple exit strategies that activate based on price movement:

- **Breakeven protection** — moves stop to entry after a configurable gain threshold
- **Trailing stops** — locks in profits as price extends
- **Partial profit taking** — scales out at predefined levels
- **Pyramid adds** — scales into winners under strict conditions
- **Profit lock** — guarantees minimum profit on extended runners
- **Time-based exits** — removes stagnant positions
- **End-of-day flatten** — all positions closed before market close

### Backtest Validation

| Metric | Baseline (Static Exits) | Dynamic Exit System | Improvement |
|--------|------------------------|---------------------|-------------|
| **Net PnL** | $33,549 | $103,883 | **3.1x** |
| **Win Rate** | 29.5% | 32.1% | +2.6pp |
| **Avg Winner** | $487 | $623 | +28% |
| **Avg Loser** | $168 | $164 | -2% |
| **Profit Factor** | — | **2.49x** | — |

*Tested across 1,287 trades over 130 trading days.*

---

## Machine Learning Pipeline

The ML system follows a deliberate 4-sprint rollout designed to avoid the mistakes that killed V3:

| Sprint | Description | Status |
|--------|-------------|--------|
| **S1: Feature Infrastructure** | Multi-feature builder shared between training and inference | Deployed |
| **S1.5: Shadow Candidates** | Log what the system *would have* traded for counterfactual analysis | Deployed |
| **S2: Offline Trainer** | LightGBM with Optuna hyperparameter tuning, walk-forward temporal CV | Deployed |
| **S2.5: Triple Barrier** | Multiclass labeling (profit/neutral/loss) on shadow candidates | Deployed |
| **S3: Shadow Predictor** | Score candidates without affecting live trading | Blocked on S2 |
| **S4: Veto Integration** | ML filters out low-probability setups in real-time | Blocked on S3 |

### Design Principles

- **Profit factor over accuracy** — V3 optimized for accuracy (74% backtest → 24% live). V4 optimizes for profit factor: the ratio of gross profit to gross loss.
- **Walk-forward temporal CV** — Never random train/test splits. Always train on past, validate on future.
- **One code path** — The same function builds features for training and inference. No silent divergence.
- **Veto-only** — ML reduces bad trades. It never creates trades.

---

## User Interfaces

### Web Dashboard
Flask + Plotly web interface for monitoring trades, positions, daily P&L, and system health. Read-only access to the trading database with interactive charts.

### Desktop Application
Electron + React + TypeScript desktop app for real-time monitoring with native OS integration.

### Claude Code Integration (MCP Server)
A Model Context Protocol server exposes 12 tools for AI-assisted analysis — read-only system status, trade queries, and configuration inspection, plus write operations (config updates, blacklist management, emergency flatten) with confirmation gates.

### Telegram Notifications
Non-blocking alerts for trade entries, exits, daily summaries, errors, and circuit breaker events. Runs on daemon threads to never block the trading loop.

---

## Testing

167+ tests across 14 test suites covering all core modules:

- **Unit tests** — config parsing, persistence, broker wrapper, risk manager, strategy scoring
- **Integration tests** — full trade lifecycle (scan → score → enter → manage → exit)
- **Regression tests** — specific bugs (infinite flatten loops, stale position data, reconciliation edge cases)
- **Structural verification** — 63 checks across 11 categories for deployment safety
- **ML pipeline tests** — feature engineering, trainer, evaluation

All tests must pass at 100% before any deployment.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.11+ |
| **Broker** | Interactive Brokers via ib_async (synchronous) |
| **Market Data** | Polygon.io REST API (premarket scanning) |
| **Database** | SQLite with WAL mode (crash-safe writes) |
| **Configuration** | TOML files + frozen Python dataclasses |
| **ML Framework** | LightGBM + Optuna (hyperparameter optimization) |
| **Web Dashboard** | Flask + Plotly |
| **Desktop App** | Electron + React + TypeScript |
| **AI Integration** | MCP Server (Claude Code) |
| **Notifications** | Telegram Bot API |
| **Testing** | pytest + custom test framework |

### Minimal Dependencies

The system intentionally keeps external dependencies minimal to reduce supply chain risk:

```
ib_async>=0.9.86
requests>=2.31.0
pytz>=2024.1
python-dotenv>=1.0.0
```

---

## Project Structure

```
algotrader/
├── Core Trading Engine
│   ├── main.py                 # Orchestrator & event loop
│   ├── config.py               # Configuration dataclass
│   ├── config_loader.py        # TOML parser
│   ├── broker.py               # IB Gateway wrapper
│   ├── polygon_client.py       # Market data client
│   ├── strategy.py             # Entry scoring system
│   ├── risk.py                 # Risk management
│   ├── persistence.py          # SQLite/JSON storage
│   └── ib_errors.py            # Error taxonomy
│
├── ML Pipeline
│   ├── ml_features.py          # Feature engineering
│   ├── ml_trainer.py           # LightGBM training pipeline
│   ├── ml_evaluation.py        # Model evaluation & SHAP analysis
│   └── l2_collector.py         # L2 market depth collection
│
├── User Interfaces
│   ├── v4_dashboard.py         # Flask web dashboard
│   ├── v4_mcp_server.py        # Claude Code MCP server
│   ├── telegram_bot.py         # Telegram notifications
│   └── electron-app/           # Desktop app (Electron + React)
│
├── Testing
│   └── tests/                  # 167+ tests, 14 suites
│
├── Backtesting
│   └── backtest/               # Historical simulation engine
│
└── Configuration
    ├── v4_config.toml          # System configuration (TOML)
    └── .env                    # API keys (git-ignored)
```

---

## Version History

| Version | Highlights |
|---------|------------|
| **4.0** | Complete rewrite. Core trading loop, bracket orders, basic risk management. |
| **4.1** | Multi-layer scanner, entry scoring system, blacklist infrastructure. |
| **4.2** | IB error taxonomy (30+ codes classified), circuit breakers, order-entry-ratio limits. |
| **4.3** | Dynamic exit system — breakeven, trailing, partial, pyramid, profit lock. |
| **4.4** | ML feature infrastructure, shadow candidate logging, L2 market depth, MCP server. |
| **4.4.1** | Multi-model code review (15 fixes across 9 files), Electron desktop app. |
| **4.4.2** | SPY market context features, pre-market audit fixes. |
| **4.5.0** | ib_async migration (maintained fork of archived ib_insync), triple barrier labeling for ML. |

### Why V4 Exists: The V3 Post-Mortem

V3 was a 3,300-line monolith using async Python. It achieved 74% accuracy in backtesting but collapsed to 24% in live trading. Root causes:

1. **Async was undebuggable** — race conditions and dropped events in production
2. **Software stops** — stop-losses lived in Python; process crash = unprotected positions
3. **Code path divergence** — separate training/inference functions silently drifted apart
4. **Hardcoded constants** — tuning required code changes and redeployment
5. **Random CV splits** — gave false confidence; temporal ordering was ignored

V3 was declared dead on February 5, 2026. V4 development began the same day.

---

## Disclaimer

This software is for **educational and research purposes**. It is currently configured for paper trading only.

- Trading involves substantial risk of loss
- Past backtest performance does not guarantee future results
- This system is under active development
- The authors are not responsible for any financial losses
- Always do your own research

---

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright (c) 2025–2026 InvestmentMDideas

---

*V4.5.0 | Last updated March 2026*
