import csv
import os
from dataclasses import dataclass
from typing import Optional, List, Dict

import pandas as pd


@dataclass
class Trade:
    side: str
    entry_time: str
    entry: float
    stop: float
    tp: float
    exit_time: str = ""
    exit: float = 0.0
    result: str = ""  # "win" / "loss"
    r: float = 0.0  # resultado em R


def _append_trade_csv(path: str, trade: Trade) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_exists = os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["side", "entry_time", "entry", "stop", "tp", "exit_time", "exit", "result", "r"]
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "side": trade.side,
            "entry_time": trade.entry_time,
            "entry": trade.entry,
            "stop": trade.stop,
            "tp": trade.tp,
            "exit_time": trade.exit_time,
            "exit": trade.exit,
            "result": trade.result,
            "r": trade.r,
        })


def run_backtest_15m(
        df_15m: pd.DataFrame,
        side: str,
        zone: tuple[float, float],
        stop_level: float,
        rr: float = 2.0,
        trades_csv_path: str = "logs/trades.csv",
        entry_signal_fn=None
) -> Dict:
    """
    Backtest base:
    - Apenas 1 trade aberto por vez
    - Entrada: quando entry_signal_fn dá True E preço está dentro da zona
    - Entrada é no OPEN do próximo candle (pra evitar lookahead)
    - Stop/TP intrabar usando high/low (conservador)
    """
    if entry_signal_fn is None:
        raise ValueError("Passe entry_signal_fn (ex.: EntrySignal.ema21_rejection).")

    zlow, zhigh = zone
    trades: List[Trade] = []
    position: Optional[Trade] = None

    # equity em R
    equity_r = 0.0
    peak_r = 0.0
    max_dd_r = 0.0

    # começamos em 1 pra poder entrar no candle i (usando sinal em i-1)
    for i in range(1, len(df_15m)):
        prev = df_15m.iloc[i - 1]
        cur = df_15m.iloc[i]

        cur_time = str(df_15m.index[i])
        prev_close = float(prev["close"])

        # 1) Se não tem posição, avaliar entrada (sinal no candle anterior, entrada no open atual)
        if position is None:
            in_zone = (zlow <= prev_close <= zhigh)

            if in_zone and entry_signal_fn(df_15m.iloc[:i], side):
                entry = float(cur["open"])
                stop = float(stop_level)

                # valida stop do lado certo
                if side == "long" and stop >= entry:
                    continue
                if side == "short" and stop <= entry:
                    continue

                risk = abs(entry - stop)
                if risk <= 0:
                    continue

                if side == "long":
                    tp = entry + rr * risk
                else:
                    tp = entry - rr * risk

                position = Trade(
                    side=side,
                    entry_time=cur_time,
                    entry=entry,
                    stop=stop,
                    tp=tp
                )
            continue

        # 2) Se tem posição, checar stop/tp no candle atual (intrabar)
        high = float(cur["high"])
        low = float(cur["low"])

        hit_stop = False
        hit_tp = False

        if position.side == "long":
            hit_stop = low <= position.stop
            hit_tp = high >= position.tp
            # conservador: se bater ambos, assume STOP primeiro
            if hit_stop:
                exit_price = position.stop
                position.result = "loss"
                position.r = -1.0
            elif hit_tp:
                exit_price = position.tp
                position.result = "win"
                position.r = rr
            else:
                continue

        else:  # short
            hit_stop = high >= position.stop
            hit_tp = low <= position.tp
            # conservador: se bater ambos, assume STOP primeiro
            if hit_stop:
                exit_price = position.stop
                position.result = "loss"
                position.r = -1.0
            elif hit_tp:
                exit_price = position.tp
                position.result = "win"
                position.r = rr
            else:
                continue

        position.exit_time = cur_time
        position.exit = exit_price

        trades.append(position)
        _append_trade_csv(trades_csv_path, position)

        equity_r += position.r
        peak_r = max(peak_r, equity_r)
        max_dd_r = min(max_dd_r, equity_r - peak_r)

        position = None

    # métricas básicas
    n = len(trades)
    wins = sum(1 for t in trades if t.result == "win")
    losses = sum(1 for t in trades if t.result == "loss")
    win_rate = (wins / n) if n else 0.0
    avg_r = (sum(t.r for t in trades) / n) if n else 0.0

    return {
        "trades": n,
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "avg_r": avg_r,
        "equity_r": equity_r,
        "max_drawdown_r": abs(max_dd_r),
        "csv": trades_csv_path
    }
