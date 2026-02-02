import pandas as pd


class EMAIndicator:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def calculate(self) -> pd.DataFrame:
        """calcula as EMA"""

        df = self.df

        df["ema_9"] = df["close"].ewm(span=9, adjust=False).mean()
        df["ema_21"] = df["close"].ewm(span=21, adjust=False).mean()
        df["ema_50"] = df["close"].ewm(span=50, adjust=False).mean()

        return df
