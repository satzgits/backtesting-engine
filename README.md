# Backtesting Engine

Event-driven backtesting framework in Python for quantitative trading strategies.

## Features

- Load historical price data (Yahoo Finance via `yfinance`)
- Event-driven architecture — market events → signal events → order events → fill events
- Built-in strategies: SMA Crossover, Mean Reversion
- Realistic simulation with slippage and commission
- Performance metrics: Sharpe ratio, max drawdown, win rate, profit factor
- Equity curve visualization

## Motivation

Quant trading is research → backtest → analyze → refine. This is the core loop. No quant resume is complete without one.

## Getting Started

```bash
pip install -r requirements.txt
python examples/sma_crossover.py
```

## Project Structure

```
├── backtester/
│   ├── engine.py        # Event loop
│   ├── data.py          # Data handler
│   ├── strategy.py      # Strategy base class
│   ├── portfolio.py     # Position & risk mgmt
│   ├── execution.py     # Simulated execution
│   └── metrics.py       # Performance stats
├── examples/
│   ├── sma_crossover.py
│   └── mean_reversion.py
├── tests/
├── requirements.txt
└── README.md
```

## Example Output

```
Sharpe Ratio:      1.42
Max Drawdown:     -12.3%
Win Rate:          58.7%
Profit Factor:     1.85
Total Return:      +34.2%
```
