# -*- coding:utf-8 -*-
from datetime import datetime

import pandas as pd
import pyupbit
from tenacity import retry, stop_after_attempt
from tqdm import tqdm

now = datetime.now()

COIN_MAP = {
    "KRW-BTC": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-ETH": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-BCH": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-ETC": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-XRP": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-DOGE": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-SOL": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-AVAX": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-SHIB": ("2024-11-29", now.strftime("%Y-%m-%d")),
    "KRW-SUI": ("2024-11-29", now.strftime("%Y-%m-%d")),
}


@retry(stop=stop_after_attempt(3))
def get_data(coin, date):
    res = pyupbit.get_ohlcv(coin, interval="minute1", to=date, count=60 * 24)
    if res is None:
        raise Exception("Empty")
    return res


for coin, (start, end) in COIN_MAP.items():
    df = []
    for date in tqdm(pd.date_range(start=start, end=end), desc=coin):
        date = date.strftime("%Y%m%d")
        res = get_data(coin, date)
        df.append(res)
    df = pd.concat(df)
    df["Date"] = df.index.strftime("%Y-%m-%d %H:%M:%S")
    df = df[["Date", "open", "high", "low", "close", "volume", "value"]]
    df.to_parquet(f"{coin}_{start}_{end}.parquet", index=False, compression="brotli")
