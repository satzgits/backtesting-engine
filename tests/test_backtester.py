import sys
import os
import pandas as pd
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backtester.data import DataHandler
from backtester.strategy import SMACrossoverStrategy, MeanReversionStrategy, Signal
from backtester.portfolio import Portfolio
from backtester.execution import ExecutionHandler


def make_sample_data(length=100):
    dates = pd.date_range("2020-01-01", periods=length, freq="D")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(length) * 0.5)
    data = pd.DataFrame({
        "open": prices * 0.99,
        "high": prices * 1.02,
        "low": prices * 0.98,
        "close": prices,
        "volume": np.random.randint(1000000, 5000000, size=length)
    }, index=dates)
    return data


def test_sma_crossover_generates_buy_signal():
    data = make_sample_data(200)
    strategy = SMACrossoverStrategy(fast_period=5, slow_period=20)
    strategy.reset()

    signals = []
    for i in range(len(data)):
        bar = data.iloc[i]
        history = data.iloc[:i + 1]
        signal = strategy.on_bar(bar, history)
        signals.append(signal.direction)

    assert Signal.BUY in signals, "SMA crossover should generate BUY signals"
    assert Signal.SELL in signals, "SMA crossover should generate SELL signals"


def test_mean_reversion_generates_buy_signal():
    data = make_sample_data(200)
    strategy = MeanReversionStrategy(window=10, entry_z=1.0, exit_z=0.3)
    strategy.reset()

    signals = []
    for i in range(len(data)):
        bar = data.iloc[i]
        history = data.iloc[:i + 1]
        signal = strategy.on_bar(bar, history)
        signals.append(signal.direction)

    assert Signal.BUY in signals, "Mean reversion should generate BUY signals"


def test_portfolio_tracks_equity():
    portfolio = Portfolio(initial_capital=100000)
    dates = pd.date_range("2020-01-01", periods=5, freq="D")
    for i in range(5):
        bar = pd.Series({"close": 100 + i, "name": dates[i]})
        bar.name = dates[i]
        portfolio.update(bar)
    assert len(portfolio.equity_curve) == 5


def test_execution_applies_slippage():
    exec_handler = ExecutionHandler(slippage=0.01, commission=0)
    order = {"symbol": "ASSET", "type": "BUY", "qty": 100, "price": 100.0, "time": "2020-01-01"}
    bar = pd.Series({"close": 100.0, "name": pd.Timestamp("2020-01-01")})
    fill = exec_handler.execute(order, bar)
    assert fill["price"] > 100.0, "Buy slippage should increase fill price"


def test_execution_commission():
    exec_handler = ExecutionHandler(slippage=0, commission=0.001)
    order = {"symbol": "ASSET", "type": "BUY", "qty": 100, "price": 100.0, "time": "2020-01-01"}
    bar = pd.Series({"close": 100.0, "name": pd.Timestamp("2020-01-01")})
    fill = exec_handler.execute(order, bar)
    assert fill["commission"] > 0, "Commission should be charged"


if __name__ == "__main__":
    test_sma_crossover_generates_buy_signal()
    test_mean_reversion_generates_buy_signal()
    test_portfolio_tracks_equity()
    test_execution_applies_slippage()
    test_execution_commission()
    print("All backtester tests passed!")
