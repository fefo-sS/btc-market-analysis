import pandas as pd


class MarketContext:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_levels(self) -> dict:
        """
        Pega níveis essenciais:
        - último swing low (suporte)
        - último swing high (resistência)
        """
        df = self.df

        last_low = df[df["swing_low"]].tail(1)
        last_high = df[df["swing_high"]].tail(1)

        support = float(last_low["low"].iloc[0]) if len(last_low) else None
        resistance = float(last_high["high"].iloc[0]) if len(last_high) else None

        return {"support": support, "resistance": resistance}

    def get_bias(self) -> str:
        """
        Bias simples (baseado em EMA):
        - long se close > ema_21 e ema_21 > ema_50
        - short se close < ema_21 e ema_21 < ema_50
        - senão neutral
        """
        df = self.df
        last = df.iloc[-1]

        close = float(last["close"])
        ema21 = float(last["ema_21"])
        ema50 = float(last["ema_50"])

        if close > ema21 and ema21 > ema50:
            return "long"
        if close < ema21 and ema21 < ema50:
            return "short"
        return "neutral"

    def get_zones(self) -> dict:
        """
        Define zonas didáticas:
        - Zona de compra: entre EMA21 e EMA50 (quando bias long)
        - Zona de venda: entre EMA50 e EMA21 (quando bias short)
        Ajuste fino virá depois com S/R e estrutura.
        """
        df = self.df
        last = df.iloc[-1]

        ema21 = float(last["ema_21"])
        ema50 = float(last["ema_50"])

        buy_zone = (min(ema21, ema50), max(ema21, ema50))
        sell_zone = (min(ema21, ema50), max(ema21, ema50))

        return {"buy_zone": buy_zone, "sell_zone": sell_zone}

    def summary(self) -> dict:
        levels = self.get_levels()
        bias = self.get_bias()
        zones = self.get_zones()

        # invalidação simples: abaixo do suporte para long, acima da resistência para short
        invalidation = None
        if bias == "long" and levels["support"] is not None:
            invalidation = levels["support"]
        if bias == "short" and levels["resistance"] is not None:
            invalidation = levels["resistance"]

        return {
            "bias": bias,
            "support": levels["support"],
            "resistance": levels["resistance"],
            "buy_zone": zones["buy_zone"] if bias == "long" else None,
            "sell_zone": zones["sell_zone"] if bias == "short" else None,
            "invalidation": invalidation,
        }
