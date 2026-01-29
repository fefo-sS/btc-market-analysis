from data.market_data import MarketData


def main():
    market = MarketData()

    btc_1d = market.get_ohlcv(
        symbol = "BTC/USDT",
        timeframe = "1d",
        limit = 200
    )

    btc_4h = market.get_ohlcv(
        symbol = "BTC/USDT",
        timeframe = "4h",
        limit = 200
    )

    print("===BTC 1D===")
    print(btc_1d.tail())
    print("===BTC 4H===")
    print(btc_4h.tail())


if __name__ == "__main__":
    main()