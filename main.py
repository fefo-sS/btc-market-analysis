import pandas as pd

from backtest.engine import run_backtest_15m
from data.market_data import MarketData
from indicators.ema import EMAIndicator
from indicators.market_structure import MarketStructure
from indicators.price_action import PriceAction
from strategy.context import MarketContext
from strategy.entry import EntrySignal
from strategy.positioning import Positioning


def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", "{:,.2f}".format)

    market = MarketData()

    btc_1d = market.get_ohlcv(symbol="BTC/USDT", timeframe="1d", limit=200)
    btc_4h = market.get_ohlcv(symbol="BTC/USDT", timeframe="4h", limit=200)

    # --- 1D pipeline ---
    btc_1d = PriceAction(btc_1d).detect_swings()
    btc_1d = EMAIndicator(btc_1d).calculate()
    btc_1d = MarketStructure(btc_1d).add_structure()

    trend_1d = MarketStructure(btc_1d).get_trend(lookback=6)
    ctx_1d = MarketContext(btc_1d).summary()

    # --- 4H pipeline ---
    btc_4h = PriceAction(btc_4h).detect_swings()
    btc_4h = EMAIndicator(btc_4h).calculate()
    btc_4h = MarketStructure(btc_4h).add_structure()

    trend_4h = MarketStructure(btc_4h).get_trend(lookback=6)
    ctx_4h = MarketContext(btc_4h).summary()

    pos = Positioning(btc_1d, btc_4h).summary()

    print("===BTC 1D=== (COM SWINGS + EMA + STRUCTURE)")
    print(btc_1d[["close", "ema_9", "ema_21", "ema_50", "swing_high", "swing_low", "structure"]].tail(20).to_string())
    print("Trend 1D:", trend_1d)
    print("Contexto 1D:", ctx_1d)

    print("\n===BTC 4H=== (COM SWINGS + EMA + STRUCTURE)")
    print(btc_4h[["close", "ema_9", "ema_21", "ema_50", "swing_high", "swing_low", "structure"]].tail(20).to_string())
    print("Trend 4H:", trend_4h)
    print("Contexto 4H:", ctx_4h)

    print("\n=== POSICIONAMENTO FINAL (1D bias + 4H zona) ===")
    print(pos)

    # --- 15m para backtest base ---
    btc_15m = market.get_ohlcv(symbol="BTC/USDT", timeframe="15m", limit=1000)
    btc_15m = EMAIndicator(btc_15m).calculate()  # precisa de ema_21 no 15m

    side = pos["bias_final"]
    zone = pos["buy_zone_4h"] if side == "long" else pos["sell_zone_4h"]
    stop_level = pos["invalidation"]

    print("\n=== BACKTEST BASE (15m) ===")
    if side in ("long", "short") and zone is not None and stop_level is not None:
        stats = run_backtest_15m(
            df_15m=btc_15m,
            side=side,
            zone=zone,
            stop_level=stop_level,
            rr=2.0,
            trades_csv_path="logs/trades.csv",
            entry_signal_fn=EntrySignal.ema21_rejection
        )
        print("Stats:", stats)
        print("Trades salvos em:", stats["csv"])
    else:
        print("Sem setup para backtest agora (bias neutral ou zona/stop ausentes).")


if __name__ == "__main__":
    main()
