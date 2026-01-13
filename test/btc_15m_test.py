from index import calculate_signals


def test_btc_15m_comprehensive():
    print("開始 BTC 15 分鐘測試")

    df = calculate_signals("BTCUSDT", "15m")

    print("數據形狀: {}".format(df.shape))
    print("欄位名稱: {}".format(list(df.columns)))

    return df
