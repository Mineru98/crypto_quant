import re
import warnings

import koreanize_matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")


class Portfolio:
    def load_data(self, path, group, begin_date, end_date):
        # begin_date, end_date YYYY-MM-DD 형식 검증
        if begin_date:
            assert re.match(
                r"^\d{4}-\d{2}-\d{2}$", begin_date
            ), "begin_date must be YYYY-MM-DD format"
        if end_date:
            assert re.match(
                r"^\d{4}-\d{2}-\d{2}$", end_date
            ), "end_date must be YYYY-MM-DD format"

        # 세션 상태 키 생성
        session_key = f"{path}_{group}_{begin_date}_{end_date}"

        # 세션에서 데이터 확인
        if session_key in st.session_state:
            self.df = st.session_state[session_key]
        else:
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
            self.df["변동성"] = (
                (self.df["high"] - self.df["low"]) / self.df["open"] * 100
            )

            # 처리된 데이터를 세션 상태에 저장
            st.session_state[session_key] = self.df

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

    def run_streamlit(self):
        st.title("비트코인 가격 시각화")

        # 사이드바에 입력 옵션 추가
        path = st.sidebar.text_input(
            "데이터 파일 경로", "notebooks/krw-btc-201709-202409.csv"
        )
        group = st.sidebar.selectbox("그룹화", ["day", "minutes"])
        begin_date = st.sidebar.text_input("시작 날짜 (YYYY-MM-DD)", "2023-09-01")
        end_date = st.sidebar.text_input("종료 날짜 (YYYY-MM-DD)", "2024-08-31")

        options = [
            ("이동평균선(10일)", "SMA_10"),
            ("이동평균선(20일)", "SMA_20"),
            ("이동평균선(30일)", "SMA_30"),
            ("이동평균선(45일)", "SMA_45"),
            ("이동평균선(60일)", "SMA_60"),
            ("이동평균선(120일)", "SMA_120"),
            ("이동평균선(240일)", "SMA_240"),
            ("볼린저밴드 상단(Bollinger_Upper)", "Bollinger_Upper"),
            ("볼린저밴드 하단(Bollinger_Lower)", "Bollinger_Lower"),
            ("상대강도지수(RSI)", "RSI"),
            ("이동평균수렴확산지수(MACD)", "MACD"),
            ("평균 실제 범위(ATR)", "ATR"),
            ("거래량 가중 평균 가격(VWAP)", "VWAP"),
            ("평균 방향 지수(ADX)", "ADX"),
            ("피보나치 되돌림 23.6%", "Fib_23.6%"),
            ("피보나치 되돌림 38.2%", "Fib_38.2%"),
            ("피보나치 되돌림 50.0%", "Fib_50.0%"),
            ("피보나치 되돌림 61.8%", "Fib_61.8%"),
            ("피보나치 되돌림 100%", "Fib_100%"),
        ]
        # 지표 선택
        indicators = st.sidebar.multiselect(
            "기술적 지표 선택",
            options=[label for label, value in options],
            default=[
                "이동평균선(10일)",
                "이동평균선(60일)",
                "이동평균선(120일)",
                "볼린저밴드 상단(Bollinger_Upper)",
                "볼린저밴드 하단(Bollinger_Lower)",
                "상대강도지수(RSI)",
                "이동평균수렴확산지수(MACD)",
                "평균 방향 지수(ADX)",
            ],
        )

        if st.sidebar.button("분석 실행"):
            self.load_data(path, group, begin_date, end_date)

            # 선택된 지표 계산
            selected_values = [value for label, value in options if label in indicators]
            for indicator in selected_values:
                if indicator.startswith("SMA_"):
                    window = int(indicator.split("_")[1])
                    self._calculate_sma(window)
                elif indicator in ["Bollinger_Upper", "Bollinger_Lower"]:
                    self._calculate_bollinger_bands(window=20)
                elif indicator == "RSI":
                    self._calculate_rsi()
                elif indicator == "MACD":
                    self._calculate_macd()
                elif indicator == "ATR":
                    self._calculate_atr()
                elif indicator == "VWAP":
                    self._calculate_vwap()
                elif indicator.startswith("Fib_") and indicator.endswith("%"):
                    self._calculate_fibonacci()
                elif indicator == "ADX":
                    self._calculate_adx()

            # 차트 데이터 준비
            chart_data = pd.DataFrame(index=self.df.index)
            chart_data["종가"] = self.df["close"]

            for label, value in options:
                if label in indicators:
                    if value.startswith("SMA_"):
                        window = int(value.split("_")[1])
                        column_name = f"이동평균선({window}일)"
                    elif value == "Bollinger_Upper":
                        column_name = "볼린저밴드 상단(Bollinger_Upper)"
                    elif value == "Bollinger_Lower":
                        column_name = "볼린저밴드 하단(Bollinger_Lower)"
                    elif value == "RSI":
                        column_name = "상대강도지수(RSI)"
                    elif value == "MACD":
                        column_name = "이동평균수렴확산지수(MACD)"
                    elif value == "ADX":
                        column_name = "평균 방향 지수(ADX)"
                    else:
                        column_name = label

                    if value in self.df.columns:
                        chart_data[column_name] = self.df[value]

            # 파스텔 톤 색상 팔레트 정의
            pastel_colors = [
                "#1A5F7A",  # 깊은 청록색
                "#FFA07A",  # 연어색
                "#8E4585",  # 자주색
                "#2E8B57",  # 바다 녹색
                "#4682B4",  # 강철 파란색
                "#CD853F",  # 페루색
                "#708090",  # 슬레이트 회색
                "#B8860B",  # 어두운 황금색
                "#C71585",  # 중간 자주색
                "#556B2F",  # 어두운 올리브 녹색
                "#8B4513",  # 안장 갈색
                "#483D8B",  # 어두운 슬레이트 파란색
                "#6B8E23",  # 올리브 녹색
                "#9932CC",  # 진한 난초색
                "#8FBC8F",  # 어두운 바다 녹색
                "#DAA520",  # 황금빛
                "#5F9EA0",  # 카데트 파란색
                "#D2691E",  # 초콜릿색
                "#9370DB",  # 중간 보라색
                "#20B2AA",  # 밝은 바다 녹색
            ]

            # Streamlit line_chart로 그래프 그리기
            st.line_chart(
                chart_data,
                color=pastel_colors[: len(chart_data.columns)],
            )

            # 변동성 차트
            st.area_chart(self.df["변동성"], color="rgba(192, 192, 192, 0.4)")

            # 그래프 그리기
            fig, ax1 = plt.subplots(figsize=(20, 7))

            ax1.plot(
                self.df.index, self.df["close"], label="종가", color=pastel_colors[0]
            )  # 종가는 조금 더 진한 색상으로 설정

            for i, (label, value) in enumerate(options):
                if label in indicators:
                    color = pastel_colors[
                        i % len(pastel_colors)
                    ]  # 색상을 순환하여 사용
                    ax1.plot(self.df.index, self.df[value], label=label, color=color)

            ax1.set_xlabel("날짜")
            ax1.set_ylabel("가격 (KRW)")
            ax1.tick_params(axis="y")

            # Y축 값을 단축하지 않고 실제 수치로 표시하며 세 자리마다 쉼표 추가
            ax1.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda x, p: format(int(x), ","))
            )

            ax2 = ax1.twinx()
            ax2.fill_between(
                self.df.index,
                self.df["변동성"],
                alpha=0.3,
                color="#C0C0C0",
                label="변동성",
            )
            ax2.set_ylabel("변동성 (%)")
            ax2.tick_params(axis="y")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

            plt.title("비트코인 백테스팅")
            st.pyplot(fig)

            st.write("데이터 미리보기:")
            st.dataframe(self.df)


if __name__ == "__main__":
    portfolio = Portfolio()
    portfolio.run_streamlit()
