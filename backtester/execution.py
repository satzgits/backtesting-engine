import random


class ExecutionHandler:
    def __init__(self, slippage=0.001, commission=0.001):
        self.slippage = slippage
        self.commission = commission

    def execute(self, order, bar):
        if order is None:
            return None

        raw_price = order["price"]
        direction = order["type"]

        slippage_amount = raw_price * self.slippage * random.uniform(0.5, 1.5)
        if direction == "BUY":
            fill_price = raw_price + slippage_amount
        else:
            fill_price = raw_price - slippage_amount

        commission_cost = fill_price * order["qty"] * self.commission

        return {
            "symbol": order["symbol"],
            "type": direction,
            "qty": order["qty"],
            "price": round(fill_price, 2),
            "commission": round(commission_cost, 2),
            "time": order["time"]
        }
