import ccxt
import pandas as pd


class MarketData:
    def __init__(self, exchange_name: str = "binance"):
        if exchange_name == "binance":
            self.exchange = ccxt.binance()
        else:
            raise ValueError("Exchange não suportada")

    def get_ohlcv(
        self,
        symbol: str = "BTC/USDT",
        timeframe: str = "1d",
        limit: int = 200
    ) -> pd.DataFrame:
        """
        Coleta dados OHLCV da exchange e retorna DataFrame limpo
        """

        # Coleta dos dados brutos
        ohlcv = self.exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )

        #  Criação do DataFrame
        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        #  Conversão do timestamp para datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        #  Definição do timestamp como índice
        df.set_index("timestamp", inplace=True)

        #  Limpeza dos dados (Fase 1.5)
        df = self._clean_ohlcv(df)

        return df

    def _clean_ohlcv(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica limpeza e padronização dos dados OHLCV
        """
        df = df.copy()

        #  Ordenação temporal explícita
        df.sort_index(inplace=True)

        #  Remoção de timestamps duplicados (segurança)
        df = df[~df.index.duplicated(keep="last")]

        # Garantia de tipos numéricos corretos
        df = df.astype({
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "float64"
        })

        # 9️⃣ Remoção do candle em formação
        df = df.iloc[:-1]

        return df





