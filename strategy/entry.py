import pandas as pd


class EntrySignal:
    @staticmethod
    def ema21_rejection(df_15m: pd.DataFrame, side: str) -> bool:
        """
        Gatilho base (bem simples):
        - SHORT: o candle toca/ultrapassa EMA21 e fecha abaixo dela (rejeição)
        - LONG:  o candle toca/ultrapassa EMA21 e fecha acima dela (rejeição)
        Usa o ÚLTIMO candle fechado (df_15m.iloc[-1]).
        """
        last = df_15m.iloc[-1]
        ema21 = float(last["ema_21"])

        o = float(last["open"])
        h = float(last["high"])
        l = float(last["low"])
        c = float(last["close"])

        if side == "short":
            touched = h >= ema21
            rejected = c < ema21
            return touched and rejected

        if side == "long":
            touched = l <= ema21
            rejected = c > ema21
            return touched and rejected

        return False
