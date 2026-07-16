import pandas as pd


class Portfolio:
    def __init__(self, initial_capital=100000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}
        self.equity_curve = []
        self.trades = []

    @property
    def total_value(self, current_price=None):
        position_value = sum(
            qty * price for qty, price in self.positions.values()
        ) if isinstance(current_price, dict) else 0
        return self.cash + position_value

    def generate_order(self, signal, bar, quantity_pct=0.25):
        price = bar["close"]
        if signal.direction == "BUY":
            cost = self.cash * quantity_pct
            qty = int(cost / price)
            return {"symbol": "ASSET", "type": "BUY", "qty": qty, "price": price, "time": bar.name}
        elif signal.direction == "SELL":
            qty = self.positions.get("ASSET", (0, 0))[0]
            return {"symbol": "ASSET", "type": "SELL", "qty": qty, "price": price, "time": bar.name}
        return None

    def process_fill(self, fill):
        symbol = fill["symbol"]
        qty = fill["qty"]
        price = fill["price"]
        direction = fill["type"]
        timestamp = fill["time"]

        if qty == 0:
            return

        if direction == "BUY":
            self.cash -= qty * price
            current_qty, current_avg = self.positions.get(symbol, (0, 0))
            new_qty = current_qty + qty
            new_avg = ((current_qty * current_avg) + (qty * price)) / new_qty if new_qty > 0 else 0
            self.positions[symbol] = (new_qty, new_avg)
        elif direction == "SELL":
            self.cash += qty * price
            current_qty, _ = self.positions.get(symbol, (0, 0))
            new_qty = current_qty - qty
            if new_qty <= 0:
                self.positions.pop(symbol, None)
            else:
                self.positions[symbol] = (new_qty, price)

        self.trades.append({
            "time": timestamp,
            "symbol": symbol,
            "direction": direction,
            "qty": qty,
            "price": price,
            "value": qty * price,
            "cash_after": self.cash
        })

    def update(self, bar):
        symbol = "ASSET"
        current_price = bar["close"]
        current_qty, _ = self.positions.get(symbol, (0, 0))
        position_value = current_qty * current_price
        total_eq = self.cash + position_value
        self.equity_curve.append({
            "date": bar.name,
            "cash": self.cash,
            "holdings": position_value,
            "equity": total_eq,
            "returns": (total_eq / self.equity_curve[-1]["equity"] - 1) if self.equity_curve else 0
        })
