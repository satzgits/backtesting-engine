import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backtester import BacktestEngine, DataHandler, SMACrossoverStrategy, Portfolio, ExecutionHandler

if __name__ == "__main__":
    data = DataHandler("AAPL", start_date="2020-01-01", end_date="2023-12-31").load_from_yahoo()
    strategy = SMACrossoverStrategy(fast_period=20, slow_period=50)
    portfolio = Portfolio(initial_capital=100000)
    execution = ExecutionHandler(slippage=0.001, commission=0.001)

    engine = BacktestEngine(data, strategy, portfolio, execution)
    engine.run()

    metrics = engine.results()
    metrics.report()

    fig = metrics.plot_equity_curve("AAPL SMA Crossover (20/50)")
    fig.savefig("sma_crossover_equity_curve.png", dpi=150)
    print("\nEquity curve saved to sma_crossover_equity_curve.png")
