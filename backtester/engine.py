import pandas as pd


class BacktestEngine:
    def __init__(self, data_handler, strategy, portfolio, execution):
        self.data = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.execution = execution
        self.history = pd.DataFrame()

    def run(self):
        self.strategy.reset()
        self.data.reset()

        for bar in self.data:
            bar_series = bar.copy()
            self._update_history(bar_series)

            signal = self.strategy.on_bar(bar_series, self.history)
            order = self.portfolio.generate_order(signal, bar_series)
            fill = self.execution.execute(order, bar_series)
            if fill:
                self.portfolio.process_fill(fill)

            self.portfolio.update(bar_series)

    def _update_history(self, bar):
        bar_df = bar.to_frame().T
        self.history = pd.concat([self.history, bar_df], ignore_index=False)

    def results(self):
        from .metrics import PerformanceMetrics
        return PerformanceMetrics(self.portfolio.equity_curve, self.portfolio.trades)
