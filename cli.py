import calendar
import os
import time
from datetime import datetime, timedelta

import backtrader as bt
import fire
import pandas as pd
import pyupbit
from tqdm import tqdm


class PrintClose(bt.Strategy):
    """간단한 전략: 종가를 출력하는 전략"""

    def next(self):
        print(
            f"Date: {self.datas[0].datetime.datetime(0)}, Close: {self.datas[0].close[0]}"
        )


def fetch_minute_data(ticker, interval, start, end):
    """
    pyupbit를 사용하여 분봉 데이터를 가져오는 함수
    :param ticker: 거래 심볼 (예: "KRW-BTC")
    :param interval: 분봉 간격 (예: "minute1")
    :param start: 시작 날짜 (datetime 객체)
    :param end: 종료 날짜 (datetime 객체)
    :return: pandas DataFrame
    """
    all_data = []
    current = end
    total_minutes = int((end - start).total_seconds() / 60)
    processed_minutes = 0
    last_progress = -1

    while current > start:
        try:
            temp = pyupbit.get_ohlcv(
                ticker=ticker, interval=interval, to=current, count=2000
            )
            if temp is not None and not temp.empty:
                all_data.append(temp)
                processed_minutes += len(temp)
                progress = min(100, int((processed_minutes / total_minutes) * 100))

                if progress > last_progress:
                    print(f"\r데이터 수집 진행 중: {progress}%", end="", flush=True)
                    last_progress = progress

                current = temp.index[0] - timedelta(minutes=1)
                time.sleep(0.1)  # API 요청 사이에 잠깐 대기
            else:
                break
        except Exception as e:
            print(f"\n데이터 가져오기 중 오류 발생: {e}")
            break

    print("\n데이터 수집 완료")

    if all_data:
        df = pd.concat(all_data)
        df = df[~df.index.duplicated(keep="first")]
        df.sort_index(inplace=True)
        return df
    else:
        return pd.DataFrame()


def load_data(ticker: str, year: int, month: int, load: bool = False) -> pd.DataFrame:
    """
    데이터를 로드하는 공통 함수

    :param ticker: 거래 심볼 (예: "BTC")
    :param year: 백테스팅할 연도
    :param month: 백테스팅할 월 (1-12)
    :return: pandas DataFrame
    """
    symbol = "KRW-" + ticker
    interval = "minute1"
    start_date = datetime(year, month, 1)
    _, last_day = calendar.monthrange(year, month)
    end_date = datetime(year, month, last_day, 23, 59, 59)
    filename = f"krw-{ticker}_{year}{month:02d}.csv"

    if os.path.exists(filename):
        if load:
            df = pd.read_csv(filename, index_col=0, parse_dates=True)
    else:
        df = fetch_minute_data(symbol, interval, start_date, end_date)

        if df.empty:
            print("데이터가 비어 있습니다.")
        else:
            df.to_csv(filename)  # 데이터 저장
    if load:
        return df
    else:
        return None


class Backtest:
    def range_save(
        self,
        ticker: str,
        start_year: int = 2017,
        start_month: int = 1,
        end_year: int = 2024,
        end_month: int = 9,
    ):
        """
        데이터를 저장하는 함수

        :param year: 백테스팅할 연도
        :param month: 백테스팅할 월 (1-12)
        """
        rows = []
        for year in range(start_year, end_year + 1):
            for month in range(start_month, end_month + 1):
                rows.append((year, month))

        for row in tqdm(rows):
            load_data(ticker, row[0], row[1])

    def save(self, ticker: str, year: int, month: int):
        """
        데이터를 저장하는 함수

        :param year: 백테스팅할 연도
        :param month: 백테스팅할 월 (1-12)
        """
        load_data(ticker, year, month)

    def run(self, ticker: str, year: int, month: int):
        """
        백테스팅을 실행하는 함수

        :param year: 백테스팅할 연도
        :param month: 백테스팅할 월 (1-12)
        """
        df = load_data(ticker, year, month, load=True)

        # 백테스터 초기화
        cerebro = bt.Cerebro()

        # Backtrader용 데이터 피드 생성
        data = bt.feeds.PandasData(
            dataname=df,
            datetime=df.index.name,  # 수정된 부분
            open="open",
            high="high",
            low="low",
            close="close",
            volume="volume",
            openinterest=None,
            timeframe=bt.TimeFrame.Minutes,
            compression=1,
        )

        cerebro.adddata(data)
        cerebro.addstrategy(PrintClose)
        cerebro.run()

        # 차트 플로팅
        cerebro.plot(style="candlestick")


if __name__ == "__main__":
    fire.Fire(Backtest)
