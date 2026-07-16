# Backtesting Engine

Event-driven backtesting framework in Python for quantitative trading strategies.

## Overview

This project implements a complete event-driven backtesting system that simulates the full trade lifecycle: receiving market data → generating signals → submitting orders → executing fills → updating portfolio. The architecture mirrors how real quant trading systems work.

### The Event-Driven Architecture

Unlike simple vectorized backtests (which calculate everything at once with pandas), this event-driven approach processes one bar at a time — just like a live trading system. This makes it more realistic and extensible:

```
Market Data → Data Handler → Strategy → Signal → Portfolio → Order → Execution → Fill → Portfolio Update
```

**Why event-driven?** Real trading systems process data sequentially. Vectorized backtests cheat by looking at all data at once, which can hide issues like look-ahead bias and slippage. Event-driven forces you to think in terms of event loops and state machines — the same architecture used by production systems at quant firms.

## Features

- **Event-driven loop** — processes market, signal, order, and fill events sequentially (like real trading)
- **Data handler** — loads and iterates over historical price data (Yahoo Finance via `yfinance`)
- **Strategy base class** — extend to implement your own strategies; receives bars, emits signals
- **Portfolio manager** — tracks positions, P&L, capital, and risk limits in real-time
- **Execution handler** — simulates fills with configurable slippage and commission
- **Strategy library**:
  - SMA crossover (trend following)
  - Mean reversion (pairs / single asset)
- **Performance metrics**:
  - Sharpe ratio (annualized)
  - Maximum drawdown (absolute & percentage)
  - Win rate & profit factor
  - Total return & CAGR
  - Daily volatility
- **Visualization** — equity curve, drawdown chart, trade markers

## Project Structure

```
backtesting-engine/
├── backtester/
│   ├── __init__.py
│   ├── engine.py          # Main event loop (drives the simulation)
│   ├── data.py            # Data handler (loads bars from CSV/API)
│   ├── strategy.py        # Abstract strategy + built-in implementations
│   ├── portfolio.py       # Position tracking, P&L, cash management
│   ├── execution.py       # Fill simulation with slippage/commission
│   └── metrics.py         # Performance statistics & plots
├── examples/
│   ├── sma_crossover.py   # Trend-following strategy demo
│   └── mean_reversion.py  # Mean reversion strategy demo
├── tests/
│   └── test_backtester.py # Unit tests
├── requirements.txt
└── README.md
```

## How It Works (Step by Step)

### 1. Data Handler (`backtester/data.py`)
Loads historical OHLCV data and yields one bar at a time to the engine. Handles:
- CSV loading with date parsing and column mapping
- Forward-filling missing values
- Iteration protocol (one row per `next()` call)

### 2. Strategy (`backtester/strategies.py`)
Abstract base class with `on_bar()` method. You override this to implement your logic. Built-in strategies:
- **SMA Crossover**: Buy when fast SMA crosses above slow SMA, sell when it crosses below
- **Mean Reversion**: Buy when price dips below N-day rolling mean by K standard deviations, sell when it reverts

### 3. Portfolio (`backtester/portfolio.py`)
Tracks everything in real-time:
- Current cash and holdings
- Unrealized and realized P&L
- Open positions with entry price and size
- Transaction log (every trade recorded)

### 4. Execution (`backtester/execution.py`)
Simulates the market impact of your orders:
- Configurable slippage (fixed % per trade)
- Configurable commission (fixed per share or % of value)
- Partial fills (optional)
- Market orders only (no limit order simulation — that's for the C++ order book project)

### 5. Engine (`backtester/engine.py`)
The main event loop that ties everything together:
```
for each bar in data:
    strategy.on_bar(bar)             # generate signals
    portfolio.update(bar)            # mark-to-market
    for each signal:
        order = portfolio.generate_order(signal)
        fill = execution.execute(order, bar)
        portfolio.process_fill(fill)
    metrics.track(portfolio)
metrics.report()
```

### 6. Metrics (`backtester/metrics.py`)
After the backtest completes, computes and displays:
- **Sharpe Ratio**: `(mean(returns) - risk_free_rate) / std(returns) * sqrt(252)` — the standard risk-adjusted return metric
- **Max Drawdown**: Largest peak-to-trough decline in the equity curve
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit / gross loss (>1.0 means profitable)
- **CAGR**: Compound annual growth rate

## Example Output

```
=== Performance Report ===
Total Return:        +34.2%
CAGR:                +12.8%
Sharpe Ratio:         1.42
Max Drawdown:        -12.3%
Win Rate:             58.7%
Profit Factor:        1.85
Total Trades:         124
Avg Trade:           +0.28%
```

## Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Run SMA crossover example
python examples/sma_crossover.py

# Run mean reversion example
python examples/mean_reversion.py
```

## Why This Matters for Quant Trading

Backtesting is the foundation of quantitative research. Every strategy starts as an idea, gets coded into a backtest, and is validated by:
1. **Historical performance** — would this strategy have made money?
2. **Risk metrics** — is the return worth the drawdown?
3. **Statistical significance** — is this alpha or just overfitting?

This project proves you understand the entire research → backtest → analyze → refine loop that defines quant trading.

```

