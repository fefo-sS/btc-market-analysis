import pandas as pd


class PriceAction:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def detect_swings(self) -> pd.DataFrame:
        """
        Detecta Swing Highs (topos) e Swing Lows (fundos)
        """
        df = self.df

        df["swing_high"] = False
        df["swing_low"] = False

        for i in range(1, len(df) - 1):

            # Swing High
            if (
                    df["high"].iloc[i] > df["high"].iloc[i - 1]
                    and df["high"].iloc[i] > df["high"].iloc[i + 1]
            ):
                df.iloc[i, df.columns.get_loc("swing_high")] = True

            # Swing Low
            if (
                    df["low"].iloc[i] < df["low"].iloc[i - 1]
                    and df["low"].iloc[i] < df["low"].iloc[i + 1]
            ):
                df.iloc[i, df.columns.get_loc("swing_low")] = True

        return df
