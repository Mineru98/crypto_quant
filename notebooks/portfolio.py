import re
import warnings
from typing import List, Optional

import fire
import koreanize_matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")


class Portfolio:
    # 단순 이동평균선(SMA) 계산
    def _calculate_sma(self, window: int):
        self.df[f"SMA_{window}"] = self.df["close"].rolling(window=window).mean()

    # 볼린저 밴드(Bollinger Bands) 계산
    def _calculate_bollinger_bands(self, window: int, num_std: int = 2):
        self.df["SMA"] = self.df["close"].rolling(window).mean()
        self.df["Bollinger_Upper"] = (
            self.df["SMA"] + num_std * self.df["close"].rolling(window).std()
        )
        self.df["Bollinger_Lower"] = (
            self.df["SMA"] - num_std * self.df["close"].rolling(window).std()
        )

    # 상대강도지수(RSI) 계산
    def _calculate_rsi(self, window: int = 14):
        delta = self.df["close"].diff(1)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)

        avg_gain = pd.Series(gain).rolling(window=window).mean()
        avg_loss = pd.Series(loss).rolling(window=window).mean()

        rs = avg_gain / avg_loss
        self.df["RSI"] = 100 - (100 / (1 + rs))

    # MACD 계산
    def _calculate_macd(
        self,
        short_window: int = 12,
        long_window: int = 26,
        signal_window: int = 9,
    ):
        self.df["EMA_12"] = self.df["close"].ewm(span=short_window, adjust=False).mean()
        self.df["EMA_26"] = self.df["close"].ewm(span=long_window, adjust=False).mean()
        self.df["MACD"] = self.df["EMA_12"] - self.df["EMA_26"]
        self.df["MACD_Signal"] = (
            self.df["MACD"].ewm(span=signal_window, adjust=False).mean()
        )
        self.df["MACD_Hist"] = self.df["MACD"] - self.df["MACD_Signal"]

    # 스토캐스틱 계산
    def _calculate_stochastic(self, k_window: int = 14, d_window: int = 3):
        self.df["Lowest_Low"] = self.df["low"].rolling(window=k_window).min()
        self.df["Highest_High"] = self.df["high"].rolling(window=k_window).max()
        self.df["%K"] = 100 * (
            (self.df["close"] - self.df["Lowest_Low"])
            / (self.df["Highest_High"] - self.df["Lowest_Low"])
        )
        self.df["%D"] = self.df["%K"].rolling(window=d_window).mean()

    # VWAP 계산
    def _calculate_vwap(self):
        self.df["Cumulative_Price_Volume"] = (
            self.df["close"] * self.df["volume"]
        ).cumsum()
        self.df["Cumulative_Volume"] = self.df["volume"].cumsum()
        self.df["VWAP"] = (
            self.df["Cumulative_Price_Volume"] / self.df["Cumulative_Volume"]
        )

    # 피보나치 되돌림/확장 (Fibonacci Retracement/Extension)
    def _calculate_fibonacci(self):
        max_price = self.df["high"].max()
        min_price = self.df["low"].min()

        levels = {
            "Fib_23.6%": max_price - (max_price - min_price) * 0.236,
            "Fib_38.2%": max_price - (max_price - min_price) * 0.382,
            "Fib_50.0%": max_price - (max_price - min_price) * 0.5,
            "Fib_61.8%": max_price - (max_price - min_price) * 0.618,
            "Fib_100%": min_price,
        }

        for level in levels:
            self.df[level] = levels[level]

    # ADX 계산
    def _calculate_adx(self, window: int = 14):
        self.df["TR"] = np.maximum(
            (self.df["high"] - self.df["low"]),
            np.maximum(
                abs(self.df["high"] - self.df["close"].shift(1)),
                abs(self.df["low"] - self.df["close"].shift(1)),
            ),
        )

        self.df["+DM"] = np.where(
            (self.df["high"] - self.df["high"].shift(1))
            > (self.df["low"].shift(1) - self.df["low"]),
            np.maximum((self.df["high"] - self.df["high"].shift(1)), 0),
            0,
        )
        self.df["-DM"] = np.where(
            (self.df["low"].shift(1) - self.df["low"])
            > (self.df["high"] - self.df["high"].shift(1)),
            np.maximum((self.df["low"].shift(1) - self.df["low"]), 0),
            0,
        )

        self.df["+DI"] = 100 * (
            self.df["+DM"].rolling(window=window).mean()
            / self.df["TR"].rolling(window=window).mean()
        )
        self.df["-DI"] = 100 * (
            self.df["-DM"].rolling(window=window).mean()
            / self.df["TR"].rolling(window=window).mean()
        )

        self.df["DX"] = (
            100
            * abs(self.df["+DI"] - self.df["-DI"])
            / (self.df["+DI"] + self.df["-DI"])
        )
        self.df["ADX"] = self.df["DX"].rolling(window=window).mean()

    # ATR(Average True Range) 계산
    def _calculate_atr(self, window: int = 14):
        self.df["TR"] = np.maximum(
            (self.df["high"] - self.df["low"]),
            np.maximum(
                abs(self.df["high"] - self.df["close"].shift(1)),
                abs(self.df["low"] - self.df["close"].shift(1)),
            ),
        )

        self.df["ATR"] = self.df["TR"].rolling(window=window).mean()

    # 데이터 로드
    def load_data(
        self,
        path: str = "notebooks/krw-btc-201709-202409.csv",
        group: str = "day",
        begin_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        # begin_date, end_date YYYY-MM-DD 형식 검증
        if begin_date:
            assert re.match(
                r"^\d{4}-\d{2}-\d{2}$", begin_date
            ), "begin_date must be YYYY-MM-DD format"
        if end_date:
            assert re.match(
                r"^\d{4}-\d{2}-\d{2}$", end_date
            ), "end_date must be YYYY-MM-DD format"
        self.df = pd.read_csv(path, index_col=0, parse_dates=True)
        if begin_date:
            self.df = self.df.loc[begin_date:]
        if end_date:
            self.df = self.df.loc[:end_date]
        if group == "day":
            self.df = self.df.resample("D").agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                    "value": "sum",
                }
            )
        self.df["Volume_Indicator"] = self.df["volume"]
        self.df["변동성"] = (self.df["high"] - self.df["low"]) / self.df["open"] * 100

    def _plot_technical_indicators(self, indicators: List[str]):
        import concurrent.futures

        def calculate_indicator(indicator):
            if indicator.startswith("SMA_"):
                if indicator.endswith("_20"):
                    self._calculate_sma(window=20)
                elif indicator.endswith("_60"):
                    self._calculate_sma(window=60)
                elif indicator.endswith("_120"):
                    self._calculate_sma(window=120)
                else:
                    raise ValueError(f"유효하지 않은 SMA 윈도우: {indicator}")
            elif indicator in ["Bollinger_Upper", "Bollinger_Lower"]:
                self._calculate_bollinger_bands(window=20)
            elif indicator == "RSI":
                self._calculate_rsi(window=14)
            elif indicator == "MACD":
                self._calculate_macd()
            elif indicator == "ATR":
                self._calculate_atr()
            elif indicator == "VWAP":
                self._calculate_vwap()
            elif indicator.startswith("Fib_"):
                if indicator.endswith("_23.6%"):
                    self._calculate_fibonacci(level="23.6%")
                elif indicator.endswith("_38.2%"):
                    self._calculate_fibonacci(level="38.2%")
                elif indicator.endswith("_50.0%"):
                    self._calculate_fibonacci(level="50.0%")
                elif indicator.endswith("_61.8%"):
                    self._calculate_fibonacci(level="61.8%")
                elif indicator.endswith("_100%"):
                    self._calculate_fibonacci(level="100%")
            elif indicator == "ADX":
                self._calculate_adx()
            else:
                raise ValueError(f"유효하지 않은 지표: {indicator}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(calculate_indicator, indicator)
                for indicator in indicators
            ]
            concurrent.futures.wait(futures)
        # 그래프 그리기
        _, ax1 = plt.subplots(figsize=(20, 7))

        ax1.plot(self.df.index, self.df["close"], label="종가")
        for indicator in indicators:
            if indicator in self.df.columns:
                ax1.plot(self.df.index, self.df[indicator], label=indicator)

        ax1.set_xlabel("날짜")
        ax1.set_ylabel("가격 (KRW)")
        ax1.tick_params(axis="y")

        # Y축 값을 단축하지 않고 실제 수치로 표시하며 세 자리마다 쉼표 추가
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: format(int(x), ","))
        )

        ax2 = ax1.twinx()
        ax2.fill_between(
            self.df.index, self.df["변동성"], alpha=0.3, color="blue", label="변동성"
        )
        ax2.set_ylabel("변동성 (%)")
        ax2.tick_params(axis="y")

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        plt.title("비트코인 백테스팅")
        plt.show()

    def run(
        self,
        path: str = "notebooks/krw-btc-201709-202409.csv",
        group: str = "day",
        begin_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ):
        self.load_data(path, group, begin_date, end_date)
        self._plot_technical_indicators(
            indicators=[
                "SMA_20",
                "Bollinger_Upper",
                "Bollinger_Lower",
                "RSI",
                "MACD",
                "ATR",
            ],
        )


if __name__ == "__main__":
    fire.Fire(Portfolio)
