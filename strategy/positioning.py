import pandas as pd


class Positioning:
    def __init__(self, df_1d: pd.DataFrame, df_4h: pd.DataFrame):
        self.df_1d = df_1d.copy()
        self.df_4h = df_4h.copy()

    @staticmethod
    def _bias_from_ema(df: pd.DataFrame) -> str:
        last = df.iloc[-1]
        close = float(last["close"])
        ema21 = float(last["ema_21"])
        ema50 = float(last["ema_50"])

        if close > ema21 and ema21 > ema50:
            return "long"
        if close < ema21 and ema21 < ema50:
            return "short"
        return "neutral"

    @staticmethod
    def _key_levels(df: pd.DataFrame) -> dict:
        last_low = df[df["swing_low"]].tail(1)
        last_high = df[df["swing_high"]].tail(1)

        support = float(last_low["low"].iloc[0]) if len(last_low) else None
        resistance = float(last_high["high"].iloc[0]) if len(last_high) else None
        return {"support": support, "resistance": resistance}

    @staticmethod
    def _interest_zone(df: pd.DataFrame, bias: str, levels: dict, padding: float = 0.015) -> dict:
        """
        Zona de interesse = confluência EMA (21-50) + proximidade de suporte/resistência.
        padding = tolerância (1.5%) em torno do suporte/resistência.
        """
        last = df.iloc[-1]
        ema21 = float(last["ema_21"])
        ema50 = float(last["ema_50"])

        ema_low, ema_high = (min(ema21, ema50), max(ema21, ema50))

        support = levels["support"]
        resistance = levels["resistance"]

        if bias == "long":
            return {"buy_zone": (ema_low, ema_high), "sell_zone": None}

        if bias == "short":
            return {"buy_zone": None, "sell_zone": (ema_low, ema_high)}

        return {"buy_zone": None, "sell_zone": None}

    def summary(self) -> dict:
        """
        Bias final vem do 1D.
        Zona e níveis vêm do 4H (setup).
        """
        bias_1d = self._bias_from_ema(self.df_1d)

        levels_4h = self._key_levels(self.df_4h)
        zones_4h = self._interest_zone(self.df_4h, bias_1d, levels_4h)

        invalidation = None

        if bias_1d == "long":
            # invalidação long: o menor entre suporte e o limite inferior da zona
            if levels_4h["support"] is not None and zones_4h["buy_zone"] is not None:
                invalidation = min(levels_4h["support"], zones_4h["buy_zone"][0])
            else:
                invalidation = levels_4h["support"]

        if bias_1d == "short":
            # invalidação short: o maior entre resistência e o limite superior da zona
            if levels_4h["resistance"] is not None and zones_4h["sell_zone"] is not None:
                invalidation = max(levels_4h["resistance"], zones_4h["sell_zone"][1])
            else:
                invalidation = levels_4h["resistance"]

        return {
            "bias_final": bias_1d,
            "support_4h": levels_4h["support"],
            "resistance_4h": levels_4h["resistance"],
            "buy_zone_4h": zones_4h["buy_zone"],
            "sell_zone_4h": zones_4h["sell_zone"],
            "invalidation": invalidation,
        }
