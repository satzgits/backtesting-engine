from abc import ABC, abstractmethod


class Signal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

    def __init__(self, direction, strength=1.0):
        self.direction = direction
        self.strength = strength


class Strategy(ABC):
    def __init__(self):
        self.name = self.__class__.__name__

    @abstractmethod
    def on_bar(self, bar, history):
        pass

    def reset(self):
        pass


class SMACrossoverStrategy(Strategy):
    def __init__(self, fast_period=20, slow_period=50):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.name = f"SMA({fast_period}/{slow_period}) Crossover"
        self.prev_fast = None
        self.prev_slow = None

    def on_bar(self, bar, history):
        if len(history) < self.slow_period:
            return Signal(Signal.HOLD)

        closes = history["close"].values
        fast_sma = closes[-self.fast_period:].mean()
        slow_sma = closes[-self.slow_period:].mean()

        signal = Signal(Signal.HOLD)

        if self.prev_fast is not None and self.prev_slow is not None:
            if self.prev_fast <= self.prev_slow and fast_sma > slow_sma:
                signal = Signal(Signal.BUY)
            elif self.prev_fast >= self.prev_slow and fast_sma < slow_sma:
                signal = Signal(Signal.SELL)

        self.prev_fast = fast_sma
        self.prev_slow = slow_sma
        return signal

    def reset(self):
        self.prev_fast = None
        self.prev_slow = None


class MeanReversionStrategy(Strategy):
    def __init__(self, window=20, entry_z=2.0, exit_z=0.5):
        super().__init__()
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.name = f"Mean Reversion ({window}, z={entry_z})"
        self.position = 0

    def on_bar(self, bar, history):
        if len(history) < self.window:
            return Signal(Signal.HOLD)

        closes = history["close"].values[-self.window:]
        mean = closes.mean()
        std = closes.std()
        current_price = bar["close"]

        if std == 0:
            return Signal(Signal.HOLD)

        z_score = (current_price - mean) / std

        if self.position == 0 and z_score < -self.entry_z:
            self.position = 1
            return Signal(Signal.BUY)
        elif self.position == 1 and z_score > -self.exit_z:
            self.position = 0
            return Signal(Signal.SELL)
        elif self.position == 0 and z_score > self.entry_z:
            self.position = -1
            return Signal(Signal.SELL)
        elif self.position == -1 and z_score < self.exit_z:
            self.position = 0
            return Signal(Signal.BUY)

        return Signal(Signal.HOLD)

    def reset(self):
        self.position = 0
