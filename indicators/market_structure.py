import pandas as pd


class MarketStructure:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def classify(self) -> pd.DataFrame:
        """
        Classifica swings como:
        - HH (higher high), LH (lower high)
        - HL (higher low),  LL (lower low)
        e adiciona uma coluna de tendência (uptrend/downtrend/range).
        """
        df = self.df

        # Colunas novas
        df["structure"] = None  # HH, HL, LH, LL (apenas nos pontos de swing)
        df["trend"] = None  # uptrend, downtrend, range (vamos preencher no final)

        last_high = None
        last_low = None

        # Guardar sequência das últimas classificações pra decidir tendência
        highs_seq = []  # HH/LH
        lows_seq = []  # HL/LL

        for i in range(len(df)):
            if df["swing_high"].iloc[i]:
                price = df["high"].iloc[i]
                if last_high is None:
                    label = "LH"  # primeiro high não tem comparação (convencional)
                else:
                    label = "HH" if price > last_high else "LH"

                df.iloc[i, df.columns.get_loc("structure")] = label
                highs_seq.append(label)
                last_high = price

            if df["swing_low"].iloc[i]:
                price = df["low"].iloc[i]
                if last_low is None:
                    label = "LL"  # primeiro low não tem comparação (convencional)
                else:
                    label = "HL" if price > last_low else "LL"

                df.iloc[i, df.columns.get_loc("structure")] = label
                lows_seq.append(label)
                last_low = price

        # Determinar tendência com base nas últimas marcações
        trend = self._detect_trend(highs_seq, lows_seq)
        df["trend"] = trend

        return df

    @staticmethod
    def _detect_trend(highs_seq: list[str], lows_seq: list[str]) -> str:
        """
        Regra simples e didática:
        - uptrend: últimos highs têm HH e últimos lows têm HL
        - downtrend: últimos highs têm LH e últimos lows têm LL
        - senão: range
        """
        last_highs = highs_seq[-2:] if len(highs_seq) >= 2 else highs_seq
        last_lows = lows_seq[-2:] if len(lows_seq) >= 2 else lows_seq

        if ("HH" in last_highs) and ("HL" in last_lows):
            return "uptrend"
        if ("LH" in last_highs) and ("LL" in last_lows):
            return "downtrend"
        return "range"

    def add_structure(self) -> pd.DataFrame:
        """
        Fase 2.2:
        Adiciona estrutura HH/HL/LH/LL com base em swing_high/swing_low.

        Cria colunas:
          - structure_high: SH/HH/LH (apenas onde swing_high=True)
          - structure_low:  SL/HL/LL (apenas onde swing_low=True)
          - structure:      coluna combinada (preenche apenas em candles de swing)
        """
        df = self.df

        # Validação mínima: swings precisam existir
        if "swing_high" not in df.columns or "swing_low" not in df.columns:
            raise ValueError("DataFrame precisa ter colunas 'swing_high' e 'swing_low' (rode PriceAction antes).")

        # Garante que high/low existam
        if "high" not in df.columns or "low" not in df.columns:
            raise ValueError("DataFrame precisa ter colunas 'high' e 'low'.")

        df["structure_high"] = None
        df["structure_low"] = None
        df["structure"] = None

        last_high = None
        last_low = None

        for i in range(len(df)):
            # Swing High -> SH / HH / LH
            if bool(df["swing_high"].iloc[i]):
                curr_high = float(df["high"].iloc[i])

                if last_high is None:
                    label = "SH"
                else:
                    label = "HH" if curr_high > last_high else "LH"

                df.iloc[i, df.columns.get_loc("structure_high")] = label
                df.iloc[i, df.columns.get_loc("structure")] = label
                last_high = curr_high

            # Swing Low -> SL / HL / LL
            if bool(df["swing_low"].iloc[i]):
                curr_low = float(df["low"].iloc[i])

                if last_low is None:
                    label = "SL"
                else:
                    label = "HL" if curr_low > last_low else "LL"

                df.iloc[i, df.columns.get_loc("structure_low")] = label
                df.iloc[i, df.columns.get_loc("structure")] = label
                last_low = curr_low

        return df

    def get_trend(self, lookback: int = 6) -> str:
        """
        Retorna a tendência atual baseada nos últimos labels de estrutura.

        Regras (didáticas):
        - uptrend: últimos highs têm HH e últimos lows têm HL (no lookback)
        - downtrend: últimos highs têm LH e últimos lows têm LL (no lookback)
        - caso contrário: range
        """
        df = self.df

        if "structure_high" not in df.columns or "structure_low" not in df.columns:
            raise ValueError("Rode add_structure() antes de get_trend().")

        last_highs = df["structure_high"].dropna().tail(lookback).tolist()
        last_lows = df["structure_low"].dropna().tail(lookback).tolist()

        # remove SH/SL (não ajudam na direção)
        last_highs = [x for x in last_highs if x in ("HH", "LH")]
        last_lows = [x for x in last_lows if x in ("HL", "LL")]

        # Se não tem dados suficientes
        if len(last_highs) < 2 or len(last_lows) < 2:
            return "range"

            # critério simples: maioria dos últimos swings
        up_score = last_highs.count("HH") + last_lows.count("HL")
        down_score = last_highs.count("LH") + last_lows.count("LL")

        if up_score >= down_score + 2:
            return "uptrend"
        if down_score >= up_score + 2:
            return "downtrend"
        return "range"
