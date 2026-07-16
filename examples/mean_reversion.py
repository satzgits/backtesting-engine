import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backtester import BacktestEngine, DataHandler, MeanReversionStrategy, Portfolio, ExecutionHandler

if __name__ == "__main__":
    data = DataHandler("MSFT", start_date="2020-01-01", end_date="2023-12-31").load_from_yahoo()
    strategy = MeanReversionStrategy(window=20, entry_z=2.0, exit_z=0.5)
    portfolio = Portfolio(initial_capital=100000)
    execution = ExecutionHandler(slippage=0.001, commission=0.001)

    engine = BacktestEngine(data, strategy, portfolio, execution)
    engine.run()

    metrics = engine.results()
    metrics.report()

    fig = metrics.plot_equity_curve("MSFT Mean Reversion (20d, z=2.0)")
    fig.savefig("mean_reversion_equity_curve.png", dpi=150)
    print("\nEquity curve saved to mean_reversion_equity_curve.png")
