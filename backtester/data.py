import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta


class DataHandler:
    def __init__(self, symbol, start_date, end_date=None):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date or datetime.now().strftime("%Y-%m-%d")
        self.data = None
        self.current_index = 0

    def load_from_yahoo(self):
        df = yf.download(self.symbol, start=self.start_date, end=self.end_date)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df = df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume"
        })
        df.index.name = "date"
        df = df[["open", "high", "low", "close", "volume"]]
        df = df.ffill().bfill()
        self.data = df
        return self

    def load_from_csv(self, filepath, date_column="date"):
        df = pd.read_csv(filepath, parse_dates=[date_column], index_col=date_column)
        required = {"open", "high", "low", "close", "volume"}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must have columns: {required}")
        df = df[list(required)].ffill().bfill()
        self.data = df
        return self

    def __len__(self):
        return len(self.data) if self.data is not None else 0

    def __iter__(self):
        self.current_index = 0
        return self

    def __next__(self):
        if self.current_index >= len(self.data):
            raise StopIteration
        bar = self.data.iloc[self.current_index]
        bar.name = self.data.index[self.current_index]
        self.current_index += 1
        return bar

    def reset(self):
        self.current_index = 0
