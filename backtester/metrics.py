import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class PerformanceMetrics:
    def __init__(self, equity_curve, trades, risk_free_rate=0.05):
        self.equity_curve = equity_curve
        self.trades = trades
        self.risk_free_rate = risk_free_rate
        self.df = pd.DataFrame(equity_curve).set_index("date") if equity_curve else pd.DataFrame()

    @property
    def returns(self):
        return self.df["equity"].pct_change().dropna()

    @property
    def total_return(self):
        if self.df.empty:
            return 0
        return (self.df["equity"].iloc[-1] / self.df["equity"].iloc[0]) - 1

    @property
    def cagr(self):
        if self.df.empty or len(self.df) < 2:
            return 0
        days = (self.df.index[-1] - self.df.index[0]).days
        if days <= 0:
            return 0
        return (self.df["equity"].iloc[-1] / self.df["equity"].iloc[0]) ** (365 / days) - 1

    @property
    def annualized_volatility(self):
        r = self.returns
        return float(r.std() * np.sqrt(252)) if len(r) > 0 else 0

    @property
    def sharpe_ratio(self):
        r = self.returns
        if len(r) == 0 or r.std() == 0:
            return 0
        excess = r.mean() * 252 - self.risk_free_rate
        return excess / (r.std() * np.sqrt(252))

    @property
    def max_drawdown(self):
        if self.df.empty:
            return 0
        eq = self.df["equity"]
        rolling_max = eq.expanding().max()
        drawdown = (eq - rolling_max) / rolling_max
        return float(drawdown.min())

    @property
    def win_rate(self):
        if not self.trades:
            return 0
        buys_and_sells = [
            t for t in self.trades if t["direction"] == "SELL"
        ]
        if not buys_and_sells:
            return 0
        wins = sum(1 for t in buys_and_sells if self._is_profitable(t))
        return wins / len(buys_and_sells)

    def _is_profitable(self, sell_trade):
        buy_trades = [
            t for t in self.trades
            if t["direction"] == "BUY" and t["time"] < sell_trade["time"]
        ]
        if not buy_trades:
            return False
        avg_buy = sum(t["price"] for t in buy_trades) / len(buy_trades)
        return sell_trade["price"] > avg_buy

    @property
    def profit_factor(self):
        if not self.trades:
            return 0
        gross_profit = sum(
            t["value"] for t in self.trades
            if t["direction"] == "SELL" and self._is_profitable(t)
        )
        gross_loss = sum(
            t["value"] for t in self.trades
            if t["direction"] == "SELL" and not self._is_profitable(t)
        )
        return gross_profit / gross_loss if gross_loss != 0 else float("inf")

    @property
    def num_trades(self):
        return len([t for t in self.trades if t["direction"] == "SELL"])

    @property
    def avg_trade_return(self):
        if self.num_trades == 0:
            return 0
        pnl = 0
        count = 0
        for t in self.trades:
            if t["direction"] == "SELL":
                buy_trades = [
                    bt for bt in self.trades
                    if bt["direction"] == "BUY" and bt["time"] < t["time"]
                ]
                if buy_trades:
                    avg_cost = sum(bt["price"] for bt in buy_trades) / len(buy_trades)
                    pnl += (t["price"] - avg_cost) / avg_cost
                    count += 1
        return pnl / count if count > 0 else 0

    def report(self):
        print("\n" + "=" * 40)
        print("      PERFORMANCE REPORT")
        print("=" * 40)
        print(f"  Total Return:      {self.total_return:>+8.2%}")
        print(f"  CAGR:              {self.cagr:>+8.2%}")
        print(f"  Sharpe Ratio:      {self.sharpe_ratio:>8.2f}")
        print(f"  Volatility (ann):  {self.annualized_volatility:>8.2%}")
        print(f"  Max Drawdown:      {self.max_drawdown:>8.2%}")
        print(f"  Win Rate:          {self.win_rate:>8.2%}")
        print(f"  Profit Factor:     {self.profit_factor:>8.2f}")
        print(f"  Total Trades:      {self.num_trades:>8d}")
        print(f"  Avg Trade Return:  {self.avg_trade_return:>+8.2%}")
        print("=" * 40)

    def plot_equity_curve(self, title=None):
        if self.df.empty:
            print("No data to plot.")
            return
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [3, 1]})

        ax1.plot(self.df.index, self.df["equity"], label="Equity", color="navy", linewidth=2)
        ax1.set_ylabel("Portfolio Value ($)")
        ax1.set_title(title or "Equity Curve")
        ax1.legend()
        ax1.grid(alpha=0.3)

        eq = self.df["equity"]
        rolling_max = eq.expanding().max()
        drawdown = (eq - rolling_max) / rolling_max
        ax2.fill_between(self.df.index, 0, drawdown, color="red", alpha=0.3)
        ax2.set_ylabel("Drawdown")
        ax2.set_xlabel("Date")
        ax2.grid(alpha=0.3)

        plt.tight_layout()
        return fig
